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


mkdir -p $RESULTS_DIR
mkdir -p $RESULTS_DIR_LOGS
mkdir -p $RESULTS_DIR_CARBON

# Remove container antigo, se existir
docker rm -f $APP_NAME

# Build da imagem
docker build --no-cache \
  -f "$ROOT_DIR/frameworks/Dockerfile" \
  -t $APP_IMAGE $APP_DIR

# Sobe o container da aplicação
echo "docker run --rm -d \
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
  docker run --rm \
  -v $SCRIPTS_DIR:/scripts \
  -v $RESULTS_DIR_LOGS:/results \
  wrk \
  -t4 -c64 -d15s \
  http://host.docker.internal:8080/$endpoint >> $RESULTS_FILE_LOG

  echo -e "\n" >> $RESULTS_FILE_LOG
}

run_benchmark "html" "html"
run_benchmark "upload" "upload"
run_benchmark "api/users/1/records/1?query=test" "api"
run_benchmark "save" "save"

sleep 3

echo "=== Benchmark concluído. Resultados salvos em $RESULTS_FILE_LOG ==="
echo "docker stop --timeout 5 $APP_NAME"
docker stop --timeout 5 $APP_NAME

sleep 10

