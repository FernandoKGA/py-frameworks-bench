#!/usr/bin/env bash
set -euo pipefail

FRAMEWORK=$1
VERSION="${2:-}"  # optional
NAME="$FRAMEWORK${VERSION:+-$VERSION}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RESULTS_DIR=$ROOT_DIR"/results"
RESULTS_DIR_LOGS=$RESULTS_DIR"/logs"
RESULTS_DIR_CARBON=$RESULTS_DIR"/carbon"

RESULTS_FILE_LOG=$RESULTS_DIR_LOGS"/"$NAME".txt"


APP_NAME="app_${FRAMEWORK}"
if [[ -n "$VERSION" ]]; then
  APP_IMAGE="${FRAMEWORK}_app:${VERSION}"
else
  APP_IMAGE="${FRAMEWORK}_app:latest"
fi

APP_DIR="$ROOT_DIR/frameworks/$FRAMEWORK"
SCRIPTS_DIR="$ROOT_DIR/wrk"

echo "Using Docker image: $APP_IMAGE"
echo $SCRIPTS_DIR

mkdir -p $RESULTS_DIR
mkdir -p $RESULTS_DIR_LOGS
mkdir -p $RESULTS_DIR_CARBON

# Remove old container, if it exists
docker rm -f $APP_NAME

# Check if the image already exists
if docker image inspect $APP_IMAGE &> /dev/null; then
  echo "Image $APP_IMAGE already exists, skipping build..."
else
  echo "Building image $APP_IMAGE..."
  # Build the image with versioned TAG
  docker build \
    -f "$ROOT_DIR/frameworks/Dockerfile" \
    -t $APP_IMAGE $APP_DIR
  echo "Build complete!"
fi

# Start the application container

echo ">>> Starting container $APP_NAME..."

echo "docker run -d \
  -p 8080:8080 \
  --name $APP_NAME \
  -v $RESULTS_DIR_CARBON:/results \
  --env-file .env \
  $APP_IMAGE"

docker run -d -p 8080:8080 --name $APP_NAME -v $RESULTS_DIR_CARBON:/results --env-file .env $APP_IMAGE

echo "Running"

# Wait for the application to be ready
sleep 2

# Benchmark function
run_benchmark() {
  local endpoint="$1"
  local label="$2"
  echo "=== Benchmark: $label ($endpoint) ===" >> $RESULTS_FILE_LOG
  cmd="docker run --rm \
  --network host \
  -v $SCRIPTS_DIR:/scripts \
  -v $RESULTS_DIR_LOGS:/results \
  -e FRAMEWORK=${FRAMEWORK} -e FILENAME=/results/${label}.csv
  wrk \
  -t4 -c64 -d30s \
  -s /scripts/${label}.lua
  http://localhost:8080/$endpoint >> $RESULTS_FILE_LOG"

  echo $cmd
  eval $cmd

  echo -e "\n" >> $RESULTS_FILE_LOG
}

# ------------------------------------------------------------------------------
# run_benchmark_hey
#
# Usage:
#   run_benchmark_hey <endpoint> <label> [max_requests] [duration] \
#                     [method] [content_type] [body] [body_file] [extra_headers...]
#
# Parameters:
#   endpoint      - URL path (e.g.: "html", "api/users/1/records/1?query=test")
#   label         - test name, used in the output file name
#   max_requests  - total number of requests (use "" to ignore)
#   duration      - duration (e.g.: "30s", "2m") (use "" to ignore)
#   method        - HTTP method: GET, POST, PUT, DELETE etc. (default: GET)
#   content_type  - Content-Type value (use "" to leave unset)
#   body          - inline body as string (use "" to leave unset)
#   body_file     - path to body file on HOST (mounted at /body in the container)
#                   (use "" to leave unset; takes priority over inline body)
#   extra_headers - any additional "-H 'Header: value'" arguments (optional, multiple)
#
# Examples:
#   run_benchmark_hey "html" "html" 10000 "" "GET"
#   run_benchmark_hey "api/..." "api" 10000 "" "PUT" "application/json" '{"foo":"bar"}' "" \
#                     "-H" "authorization: user"
#   run_benchmark_hey "upload" "upload" 10000 "" "POST" "" "" "/tmp/multipart.bin" \
#                     "-H" "content-type: multipart/form-data; boundary=----Boundary"
# ------------------------------------------------------------------------------
run_benchmark_hey() {
  local endpoint="$1"
  local label="$2"
  local max_requests="${3:-}"
  local duration="${4:-}"
  local method="${5:-GET}"
  local content_type="${6:-}"
  local body="${7:-}"
  local body_file="${8:-}"
  # All extra arguments from the 9th onward are treated as additional hey flags
  local extra_args=("${@:9}")

  local hey_base=("docker" "run" "--rm"
    "--network" "host"
    "-v" "$RESULTS_DIR_LOGS:/results"
  )

  # If a body_file is provided, mount its parent directory inside the container
  if [[ -n "$body_file" ]]; then
    local body_file_dir
    body_file_dir="$(dirname "$body_file")"
    local body_file_name
    body_file_name="$(basename "$body_file")"
    hey_base+=("-v" "${body_file_dir}:/bodydir:ro")
  fi

  hey_base+=(
    "vinixnan/hey:0.1.4"
    "-c" "64"
    "-o" "csv"
    "-m" "$method"
  )

  # Limit: number of requests or duration
  local tipo=""
  if [[ -n "$max_requests" ]]; then
    hey_base+=("-n" "$max_requests")
    tipo="max_requests"
  elif [[ -n "$duration" ]]; then
    hey_base+=("-z" "$duration")
    tipo="duration"
  else
    echo "Error: provide max_requests or duration" >&2
    return 1
  fi

  # Content-Type via -T (hey's dedicated parameter)
  if [[ -n "$content_type" ]]; then
    hey_base+=("-T" "$content_type")
  fi

  # Inline body via -d
  if [[ -n "$body" && -z "$body_file" ]]; then
    hey_base+=("-d" "$body")
  fi

  # File body via -D (points to the path inside the container)
  if [[ -n "$body_file" ]]; then
    hey_base+=("-D" "/bodydir/${body_file_name}")
  fi

  # Extra headers (e.g.: "-H" "authorization: user")
  if [[ ${#extra_args[@]} -gt 0 ]]; then
    hey_base+=("${extra_args[@]}")
  fi

  hey_base+=("http://localhost:8080/$endpoint")

  local outfile="$RESULTS_DIR_LOGS/${label}_${tipo}.csv"

  echo ">>> Running hey: ${hey_base[*]}"
  "${hey_base[@]}" > "$outfile"

  echo "Benchmark '$label' complete. Results saved to $outfile"

  sleep 1
}

finish_benchmark() {
  curl http://localhost:8080/save
  
  sleep 1
  docker stop -t 5 $APP_NAME
}

# run_benchmark "html" "html"
# run_benchmark "upload" "upload"
# run_benchmark "api/users/1/records/1?query=test" "api"

# ------------------------------------------------------------------------------
# Prepare the multipart body for the "upload" endpoint
# Mirrors exactly what upload.lua does manually
# ------------------------------------------------------------------------------
MULTIPART_BOUNDARY="----WebKitFormBoundaryePkpFF7tjBAqx29L"
MULTIPART_BODY_FILE="/tmp/hey_upload_body_${FRAMEWORK}.txt"

printf -- "--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"test.txt\"\r\n\r\n" \
  "$MULTIPART_BOUNDARY" > "$MULTIPART_BODY_FILE"
cat "$SCRIPTS_DIR/1kb.txt" >> "$MULTIPART_BODY_FILE"
printf "\r\n--%s--" "$MULTIPART_BOUNDARY" >> "$MULTIPART_BODY_FILE"

# html -> simple GET
run_benchmark_hey \
  "html" "html" \
  10000 "" \
  "GET" "" "" ""

# upload -> multipart POST (mirrors upload.lua)
run_benchmark_hey \
  "upload" "upload" \
  10000 "" \
  "POST" "multipart/form-data; boundary=${MULTIPART_BOUNDARY}" "" "$MULTIPART_BODY_FILE"

# api -> PUT with JSON and authorization header (mirrors api.lua)
run_benchmark_hey \
  "api/users/1/records/1?query=test" "api" \
  10000 "" \
  "PUT" "application/json" '{"foo": "bar"}' "" \
  "-H" "authorization: user"


finish_benchmark

# Clean up temporary multipart file
rm -f "$MULTIPART_BODY_FILE"

echo "=== Benchmark complete. Results saved to $RESULTS_DIR_LOGS ==="
sleep 1
