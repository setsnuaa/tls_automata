FROM debian:buster

RUN sed -i s@/deb.debian.org/@/mirrors.163.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update -y
RUN apt-get install -y --no-install-recommends git perl gcc make libc6-dev ca-certificates ncat && apt-get clean
RUN apt-get update && apt-get install -y --no-install-recommends python2 python3 && apt-get clean
RUN git clone https://gitclone.com/github.com/ARMmbed/mbedtls.git
ARG COMMIT=mbedtls-2.16.2
RUN cd mbedtls && git checkout -b current ${COMMIT} && git submodule init && git submodule update
RUN cd mbedtls && make -j

COPY run_client.sh /run_client.sh
RUN chmod +x /run_client.sh
RUN sed -i 's/\r$//' /run_client.sh
