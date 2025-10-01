#!/usr/bin/env bash
set -euo pipefail

FRAMEWORK=$1
VERSION="${2:-}"  # opcional
NAME="$FRAMEWORK${VERSION:+-$VERSION}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RESULTS_DIR=$ROOT_DIR"/results"
RESULTS_DIR_LOGS=$RESULTS_DIR"/logs"
RESULTS_DIR_CARBON=$RESULTS_DIR"/carbon"

RESULTS_FILE_LOG=$RESULTS_DIR_LOGS"/"$NAME".txt"


APP_NAME="app_${FRAMEWORK}"
APP_IMAGE="${FRAMEWORK}_app"
APP_DIR="$ROOT_DIR/frameworks/$FRAMEWORK"
SCRIPTS_DIR="$ROOT_DIR/wrk"

echo $SCRIPTS_DIR


mkdir -p $RESULTS_DIR
mkdir -p $RESULTS_DIR_LOGS
mkdir -p $RESULTS_DIR_CARBON

# Remove container antigo, se existir
docker rm -f $APP_NAME

# Build da imagem
docker build \
  -f "$ROOT_DIR/frameworks/Dockerfile" \
  -t $APP_IMAGE $APP_DIR

# Sobe o container da aplicação
echo "docker run -d \
  -p 8080:8080 \
  --name $APP_NAME \
  -v $RESULTS_DIR_CARBON:/results \
  $APP_IMAGE"

docker run -d \
  -p 8080:8080 \
  --name $APP_NAME \
  -v $RESULTS_DIR_CARBON:/results \
  $APP_IMAGE

echo "Rodando"

# Aguarda a aplicação estar pronta
sleep 2

# Função de benchmark
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

run_benchmark_hey() {
  local endpoint="$1"
  local label="$2"
  local max_requests="${3:-}"  # opcional: total de requisições (ex.: 10000)
  local duration="${4:-}"      # opcional: duração (ex.: 30s, 2m)
  
  local hey_base=("docker" "run" "--rm"
                    "-v" "$SCRIPTS_DIR:/scripts"
                    "-v" "$RESULTS_DIR_LOGS:/results"
                    "vinixnan/hey:0.1.4"
                    "-c" "64"          # conexões (ajuste se quiser)
                    "-o" "csv")       # saída em JSON (stdout)

  tipo=""
  if [[ -n "$max_requests" ]]; then
      hey_base+=("-n" "$max_requests")
      tipo="max_requests"
  elif [[ -n "$duration" ]]; then
      hey_base+=("-z" "$duration")
      tipo="duration"
  else
      echo "Erro: informe MAX_REQUESTS ou DURATION" >&2
      return 1
  fi
  local outfile="$RESULTS_DIR_LOGS/${label}_${tipo}.csv"
  hey_base+=("http://localhost:8080/$endpoint")

  hey_cmd="${hey_base[*]}"
  echo $hey_cmd

  eval $hey_cmd > "$outfile"
  echo "Benchmark '$label' concluído. Resultado em $outfile"
  
}

finish_benchmark() {
  local endpoint="save"
  local label="save"
  docker run --rm \
  --network host \
  -v $SCRIPTS_DIR:/scripts \
  -v $RESULTS_DIR_LOGS:/results \
  wrk \
  -t1 -c1 -d15s \
  http://localhost:8080/$endpoint
  sleep 3
  docker stop -t 5 $APP_NAME
}

run_benchmark "html" "html"
run_benchmark "upload" "upload"
run_benchmark "api/users/1/records/1?query=test" "api"

#run_benchmark_hey "html" "html" 500000
#run_benchmark_hey "upload" "upload" 500000
#run_benchmark_hey "api/users/1/records/1?query=test" "api" 500000

#run_benchmark_hey "html" "html" "" "30s"
#run_benchmark_hey "upload" "upload" "" "30s"
#run_benchmark_hey "api/users/1/records/1?query=test" "api" "" "30s"



finish_benchmark

echo "=== Benchmark concluído. Resultados salvos em $RESULTS_DIR_LOGS ==="
sleep 3

