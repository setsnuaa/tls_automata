FROM debian:buster AS builder
# 添加国内源
RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update -y
# 安装编译工具以及依赖包
RUN apt-get install -y --no-install-recommends git perl gcc make libc6-dev ca-certificates && apt-get clean

WORKDIR /openssl
ARG COMMIT
# 下载源码
RUN git clone --branch ${COMMIT} --depth 1 https://gitclone.com/github.com/openssl/openssl.git .

# 编译客户端源码
RUN ./config
RUN make -j
RUN make install_sw DESTDIR=/tmp/destdir


FROM debian:buster

RUN sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean && apt-get update -y
# 安装重置客户端所需的软件包
RUN apt-get install -y --no-install-recommends ncat && apt-get clean

COPY --from=builder /tmp/destdir /
RUN ldconfig
RUN ldconfig /usr/local/lib64/

# 复制运行脚本至镜像
COPY run_client_new.sh /run_client.sh
# 添加执行权限
RUN chmod +x /run_client.sh
RUN sed -i 's/\r$//' /run_client.sh
