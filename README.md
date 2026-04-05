# Python Web Frameworks Benchmark for Emissions

Based on https://github.com/klen/py-frameworks-bench

---

This is a benchmark for asynchronous Python web frameworks. Most of the frameworks are ASGI-compatible (aiohttp is an exception).

The goal of the benchmark is not to evaluate deployment strategies (e.g., uvicorn vs hypercorn) or database layers (ORM, drivers), but the frameworks themselves and their emissions. The benchmark exercises request parsing (body, headers, formdata, query strings), routing, and response generation. The emissions are measured using [CodeCarbon](https://docs.codecarbon.io/latest/).

## Table of Contents

- [Methodology](#methodology)
- [Frameworks Under Test](#frameworks-under-test)
- [Test Types](#test-types)
- [Infrastructure and Automation](#infrastructure-and-automation)
- [How to Run](#how-to-run)

---

## Methodology

Results are collected using a Dockerized version of [hey v0.1.4](https://hub.docker.com/layers/vinixnan/hey/0.1.4/images/) with the following parameters:

```
hey -c 64 -o "csv" -m $method -n $max_requests [URL]
```

Each version of each framework is executed across multiple rounds to ensure statistical validity. The collected metrics include, but are not limited to:

- **Throughput** (req/s)
- **Percentile latencies** (P95, P99)
- **Energy consumed** (via [CodeCarbon](https://docs.codecarbon.io/latest/))
- **CPU power draw**
- **Estimated CO₂ emissions**

---

## Frameworks Under Test

The following asynchronous Python web frameworks are evaluated across multiple released versions:

- [FastAPI](https://github.com/tiangolo/fastapi)
- [Starlette](https://github.com/encode/starlette)
- [Django](https://www.djangoproject.com/)
- [Sanic](https://sanic.dev/)
- [Baize](https://github.com/abersheeran/baize)
- [Muffin](https://github.com/klen/muffin)
- [aiohttp](https://docs.aiohttp.org/)
- [Quart](https://github.com/pallets/quart)
- [Emmett](https://emmett.sh/)
- [BlackSheep](https://github.com/Neoteroi/BlackSheep)
- [Tornado](https://www.tornadoweb.org/)

> **Note:** Not all frameworks have fully functional benchmark results across all tested versions. Version-specific incompatibilities are treated as benchmark findings and are documented accordingly.

---

## Test Types

The benchmark covers three endpoint types:

1. **HTML** (`/api/html`): Accepts a request and returns a simple HTML response with a custom dynamic header. Simulates a plain HTML response.

2. **API** (`/api/`): Checks headers, parses path parameters, query string, and JSON body, then returns a JSON response. Simulates a JSON REST API.

3. **Upload** (`/api/upload`): Accepts a file uploaded via multipart formdata and processes it. Simulates multipart file upload handling.

The application source code for each framework can be found in the [`frameworks/`](./frameworks) directory.

---

## Infrastructure and Automation

### Docker

Each framework version runs inside an isolated Docker container, ensuring reproducibility and preventing cross-environment interference. The `hey` load generator itself is also containerized, using the [`vinixnan/hey:0.1.4`](https://hub.docker.com/layers/vinixnan/hey/0.1.4/images/) image.

```sh
# Build the base image
docker build . -t benchbase:latest
```

### Automated Pipeline

The project includes an automated pipeline that:

- **Discovers and filters** available versions of each framework from PyPI
- **Builds** a dedicated Docker image for each version on demand
- **Validates** each image with a quick functional test before committing it to the benchmark
- **Caches** previously built and validated images to avoid redundant rebuilds across runs
- **Executes** the benchmark for a configurable number of rounds per version
- **Collects** both HTTP performance metrics and energy consumption data (via [CodeCarbon](https://docs.codecarbon.io/latest/))

---

## How to Run

### Recommended Workflow

It is strongly recommended to validate and build all framework versions before running the full benchmark. This ensures that only images known to work correctly are benchmarked, and that subsequent runs benefit from the build cache.

**Step 1 — Validate and build all versions:**

```sh
./run.py --validate-only
```

This builds Docker images for all framework versions and runs a quick functional test on each. Validated versions are saved to `good_versions.json`.

**Step 2 — Run the full benchmark on validated versions:**

```sh
./run.py --use-good-versions --rounds N
```

This runs the benchmark for `N` rounds using only the versions that passed validation, pulling from the cache built in the previous step.

---

### All Execution Modes

| Command | Description |
|---|---|
| `./run.py` | Full benchmark across all versions |
| `./run.py --validate-only` | Build images and run quick validation only |
| `./run.py --use-good-versions` | Benchmark only validated versions |
| `./run.py --use-good-versions --rounds N` | Benchmark validated versions for N rounds |
| `./run.py --force-rebuild` | Force rebuild of all images, even if cached |

### Flags

| Flag | Description |
|---|---|
| `--validate-only`, `--build-only` | Build images and validate with a quick test |
| `--use-good-versions` | Use versions from `good_versions.json` |
| `--force-rebuild` | Rebuild all images regardless of cache |
| `--rounds N` | Number of benchmark rounds to execute |
| `--help`, `-h` | Show help message |

---

## License

Licensed under the MIT License (see the LICENSE file).