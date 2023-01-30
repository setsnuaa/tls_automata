FROM debian:buster

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update -y
RUN apt install -y git cmake make build-essential pkg-config libunwind-dev
RUN apt install -y golang ncat

ARG REPO=boringssl
RUN git clone https://boringssl.googlesource.com/${REPO}

ARG COMMIT=chromium-stable
WORKDIR boringssl/

RUN git checkout -b current ${COMMIT}
RUN mkdir build && cd build && cmake .. 
RUN cd build && make

COPY run_client.sh /run_client.sh
RUN chmod +x /run_client.sh
