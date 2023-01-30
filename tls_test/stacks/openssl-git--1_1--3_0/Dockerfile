FROM debian:buster AS builder
# 添加国内源
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends git perl gcc make libc6-dev ca-certificates && apt-get clean

WORKDIR /openssl
ARG COMMIT
RUN git clone --branch ${COMMIT} --depth 1 https://github.com/openssl/openssl.git .

RUN ./config
RUN make -j
RUN make install_sw DESTDIR=/tmp/destdir


FROM debian:buster

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends ncat && apt-get clean

COPY --from=builder /tmp/destdir /
RUN ldconfig
RUN ldconfig /usr/local/lib64/

COPY run_client_new.sh /run_client.sh
RUN sed -i 's/\r$//' /run_client.sh
