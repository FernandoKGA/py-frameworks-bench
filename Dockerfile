FROM debian:12-slim AS python_dynamic_version

ARG VERSION=3.12.3
ARG SMALL_VERSION=3.12

RUN apt-get update -q && apt install -q graphviz gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config python3-dev ninja-build patchelf rename linux-perf nano build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev wget curl build-essential cmake libboost-context-dev libboost-program-options-dev libboost-filesystem-dev doxygen graphviz-dev libgraphviz-dev libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev -y

ENV PATH="$HOME/.cargo/bin:$PATH"

ADD https://www.python.org/ftp/python/${VERSION}/Python-${VERSION}.tgz Python-${VERSION}.tgz
RUN tar xzf Python-${VERSION}.tgz
RUN cd Python-${VERSION} && ./configure --enable-optimizations 
RUN cd Python-${VERSION} && make altinstall
RUN ln -s /usr/local/bin/python${SMALL_VERSION} /usr/local/bin/python
RUN ln -s /usr/local/bin/python${SMALL_VERSION} /usr/local/bin/python3
RUN ln -s /usr/local/bin/pip${SMALL_VERSION} /usr/local/bin/pip
RUN ln -s /usr/local/bin/pip${SMALL_VERSION} /usr/local/bin/pip3
RUN python -V
RUN rm -rf /var/lib/apt/lists/*


FROM python_dynamic_version AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN /usr/local/bin/pip install --no-cache-dir \
    wheel \
    gunicorn \
    orjson \
    ujson \
    codecarbon \
    pycallgraph \
    uvicorn[standard]

ONBUILD COPY requirements.txt /app/requirements.txt
ONBUILD RUN /usr/local/bin/pip install --no-cache-dir -r requirements.txt
ONBUILD COPY . /app

EXPOSE 8080
WORKDIR /app
