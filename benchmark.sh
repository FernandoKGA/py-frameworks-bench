#!/usr/bin/env bash
set -euo pipefail

FRAMEWORK=$1
VERSION="${2:-}"  # opcional
NAME="$FRAMEWORK${VERSION:+-$VERSION}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_FILE="$ROOT_DIR/results/${NAME}.txt"


APP_NAME="app_${FRAMEWORK}"
APP_IMAGE="${FRAMEWORK}_app"
APP_DIR="$ROOT_DIR/frameworks/$FRAMEWORK"
SCRIPTS_DIR="$ROOT_DIR/wrk"
RESULTS_DIR="$ROOT_DIR/results"

mkdir -p "$RESULTS_DIR"

# Remove container antigo, se existir
docker rm -f "$APP_NAME" >/dev/null 2>&1 || true

# Build da imagem
docker build \
  -f "$ROOT_DIR/frameworks/Dockerfile" \
  -t "$APP_IMAGE" "$APP_DIR"

# Sobe o container da aplicação
docker run --rm -d \
  -p 8080:8080 \
  --name "$APP_NAME" \
  "$APP_IMAGE"


# Aguarda a aplicação estar pronta
sleep 2

# Função de benchmark
run_benchmark() {
  local endpoint="$1"
  local label="$2"
  echo "=== Benchmark: $label ($endpoint) ===" >> "$RESULTS_FILE"
  docker run --rm \
  -v "$SCRIPTS_DIR":/scripts \
  -v "$RESULTS_DIR":/results \
  wrk \
  -t4 -c64 -d15s \
  http://host.docker.internal:8080/$endpoint >> "$RESULTS_FILE"

  echo -e "\n" >> "$RESULTS_FILE"
}

run_benchmark "html" "html"
run_benchmark "upload" "upload"
run_benchmark "api/users/1/records/1?query=test" "api"

# O container será removido automaticamente com --rm
