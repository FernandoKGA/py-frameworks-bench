FROM vinixnan/python:3.12 AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN /usr/local/bin/pip install --no-cache-dir \
    wheel \
    gunicorn \
    orjson \
    ujson \
    uvicorn[standard]

RUN pip install codecarbon pyinstrument

ONBUILD COPY requirements.txt /app/requirements.txt
ONBUILD RUN /usr/local/bin/pip install --no-cache-dir -r requirements.txt
ONBUILD COPY . /app

EXPOSE 8080
WORKDIR /app