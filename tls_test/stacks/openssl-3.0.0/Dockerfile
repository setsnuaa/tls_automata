FROM debian:buster AS builder

RUN apt-get update && apt-get install -y --no-install-recommends git perl gcc make libc6-dev ca-certificates && apt-get clean

WORKDIR /openssl
RUN git clone --branch openssl-3.0.0 --depth 1 https://github.com/openssl/openssl.git .

RUN ./config
RUN make -j
RUN make install_sw DESTDIR=/tmp/destdir


FROM debian:buster

RUN apt-get update && apt-get install -y --no-install-recommends ncat ncurses-base && apt-get clean

COPY --from=builder /tmp/destdir /
RUN ldconfig
RUN ldconfig /usr/local/lib64/

COPY run_client.sh /run_client.sh
RUN sed -i 's/\r$//' /run_client.sh
