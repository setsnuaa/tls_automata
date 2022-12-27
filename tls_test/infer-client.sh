#!/bin/bash

set -e

SCRIPTDIR="$(dirname "$0")"
cd "$SCRIPTDIR"

CLIENT_IMAGE=$1
INFERER_IMAGE=tls-test/tls-inferer
VERSION=$2
VOCABULARY=$3


shift 3

PID=$$

# 虚拟网卡
if [ -z "$( docker network ls -f name=tls-test -q )" ]; then
    docker network create tls-test
fi

# 启动客户端镜像
docker run -d --rm \
           --name "tls-client-$PID" \
           --network tls-test \
           -v "$PWD"/crypto/material/trusted-ca/ca.pem:/tmp/ca.pem \
           "$CLIENT_IMAGE" /run_client.sh \
                           -p 4444 \
                           -V "$VERSION" \
                           $CIPHERS \
                           -A /tmp/ca.pem

# 结果保存在这个路径
RESULTS_DIR="$PWD"/results/"${CLIENT_IMAGE#*:}"/${VOCABULARY^^}
mkdir -p "$RESULTS_DIR"

# 生成服务端证书
make -C crypto certs/"tls-inferer-$PID".crt

# 启动推理机
docker run -i --rm \
           --name tls-inferer-$PID \
           -v "$RESULTS_DIR":/results \
           -v "$PWD"/crypto/material:/tmp/material \
           -v "$PWD"/crypto/certs:/tmp/certs \
           --network tls-test \
           "$INFERER_IMAGE" /probe_client.sh \
                            -T "tls-client-$PID":4444 \
                            -S "$VOCABULARY" \
                            -L "tls-inferer-$PID":4433 \
                            -C valid:/tmp/certs/"tls-inferer-$PID".crt:/tmp/certs/"tls-inferer-$PID".key:DEFAULT \
                            -C invalid:/tmp/material/servers/invalid/cert.pem:/tmp/material/servers/invalid/key.pem \
                            -C untrusted:/tmp/material/servers/untrusted/cert.pem:/tmp/material/servers/untrusted/key.pem \
                            -o /results \
                            "$@"

# 客户端会在后台一直监听4444端口，手动关一下
docker kill "tls-client-$PID"

echo Results are in "$RESULTS_DIR"
