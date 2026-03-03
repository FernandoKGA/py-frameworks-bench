FROM python:3.12.3-slim-bookworm AS benchbase

RUN apt-get update -q && apt install -q curl pkg-config patchelf rename linux-perf python3-dev build-essential -y

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN /usr/local/bin/pip install --no-cache-dir \
    wheel \
    gunicorn \
    orjson \
    ujson \
    uvicorn[standard]

RUN pip install --no-cache-dir codecarbon==3.0.7 pyinstrument setuptools wheel

ONBUILD COPY requirements.txt /app/requirements.txt
ONBUILD RUN /usr/local/bin/pip install --no-cache-dir -r requirements.txt
ONBUILD COPY . /app

EXPOSE 8080
WORKDIR /app