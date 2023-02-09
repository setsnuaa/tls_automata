FROM debian:buster

RUN sed -i s@/deb.debian.org/@/mirrors.163.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update && apt-get install -y --no-install-recommends git perl gcc make libc6-dev ca-certificates ncat && apt-get clean
RUN apt-get update && apt-get install -y --no-install-recommends dh-autoreconf && apt-get clean
ARG REPO=wolfSSL
RUN git clone https://gitclone.com/github.com/${REPO}/wolfssl.git
ARG COMMIT=v5.1.1-stable
WORKDIR /wolfssl
RUN git checkout -b current ${COMMIT}
RUN ./autogen.sh
RUN ./configure --enable-tlsv10 --enable-sni --enable-tls13 C_EXTRA_FLAGS="-DWOLFSSL_STATIC_RSA"
RUN sed -i 's/-Werror /-DUSE_ANY_ADDR=1 /' Makefile
RUN make
RUN make install
RUN ldconfig

COPY run_server.sh /run_server.sh
COPY run_client.sh /run_client.sh
RUN chmod +x /run_client.sh
