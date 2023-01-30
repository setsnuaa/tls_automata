FROM debian:buster AS builder

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update -y
RUN apt-get install -y --no-install-recommends git perl gcc make libc6-dev ca-certificates && apt-get clean

WORKDIR /openssl
ARG COMMIT
RUN git clone --branch ${COMMIT} --depth 1 https://github.com/openssl/openssl.git .

RUN ./config
RUN make
RUN make -j install_sw INSTALL_PREFIX=/tmp/destdir


FROM debian:buster

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update -y
RUN apt-get install -y --no-install-recommends ncat && apt-get clean

ENV PATH="/usr/local/ssl/bin:$PATH"
COPY --from=builder /tmp/destdir /
RUN ldconfig
RUN ldconfig /usr/local/lib64/

COPY run_client.sh /run_client.sh
RUN chmod +x /run_client.sh
RUN sed -i 's/\r$//' /run_client.sh
