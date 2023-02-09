.PRECIOUS: containers/openssl/%.docker \
           containers/wolfssl/%.docker \
           containers/mbedtls/%.docker \
           containers/matrixssl/%.docker \
           containers/gnutls/%.docker \
           containers/boringssl/%.docker \
           containers/fizz/%.docker \
           containers/picotls/%.docker \
	   containers/erlang/%.docker \
	   containers/nss/%.docker \
	   containers/curl-openssl/%.docker \
	   containers/curl-gnutls/%.docker \
	   containers/curl-wolfssl/%.docker \
           containers/tools/%.docker


########
# TOOL #
########

containers/tool/tls-inferer.docker: tool/Dockerfile tool/probe_client.sh
	docker build -t tls-test/tls-inferer tool
	mkdir -p containers/tool
	docker image ls -q tls-test/tls-inferer > $@



##############
# TLS STACKS #
##############


# OpenSSL

containers/openssl/%.docker: stacks/openssl-git--1_1--3_0/tags/% stacks/openssl-git--1_1--3_0/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/openssl:$$(basename $(@:.docker=)) stacks/openssl-git--1_1--3_0
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/openssl:$$(basename $(@:.docker=)) > $@

containers/openssl/%.docker: stacks/openssl-git--1_0/tags/% stacks/openssl-git--1_0/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/openssl:$$(basename $(@:.docker=)) stacks/openssl-git--1_0
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/openssl:$$(basename $(@:.docker=)) > $@

containers/openssl/%.docker: stacks/openssl-git--0_9_8/tags/% stacks/openssl-git--0_9_8/Dockerfile stacks/openssl-git--0_9_8/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/openssl:$$(basename $(@:.docker=)) stacks/openssl-git--0_9_8
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/openssl:$$(basename $(@:.docker=)) > $@

# all: $(foreach tag, $(wildcard openssl-git/tags/*), $(subst openssl-git/tags/,.build/openssl/,$(tag)))



# wolfSSL

containers/wolfssl/%.docker: stacks/wolfssl-git/tags/% stacks/wolfssl-git/Dockerfile stacks/wolfssl-git/run_server.sh stacks/wolfssl-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test-bed/wolfssl:$$(basename $(@:.docker=)) stacks/wolfssl-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test-bed/wolfssl:$$(basename $(@:.docker=)) > $@

containers/wolfssl/patch-CVE-2021-3336.docker: stacks/wolfssl-git/Dockerfile stacks/wolfssl-git/run_server.sh stacks/wolfssl-git/run_client.sh
	docker build --build-arg REPO=SparkiDev --build-arg COMMIT=fad1e67677bf7797b6bd6e1f21a513c289d963a7 -t tls-test-bed/wolfssl:$$(basename $(@:.docker=)) stacks/wolfssl-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test-bed/wolfssl:$$(basename $(@:.docker=)) > $@

# all: $(foreach tag, $(wildcard wolfssl-git/tags/*), $(subst wolfssl-git/tags/,.build/wolfssl/,$(tag)))



# mbedtls 

containers/mbedtls/%.docker: stacks/mbedtls-git/tags/% stacks/mbedtls-git/Dockerfile stacks/mbedtls-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/mbedtls:$$(basename $(@:.docker=)) stacks/mbedtls-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/mbedtls:$$(basename $(@:.docker=)) > $@

containers/mbedtls/vulnerable.docker: stacks/mbedtls-vulnerable/Dockerfile stacks/mbedtls-vulnerable/explicit.patch
	docker build -t tls-test/mbedtls:$$(basename $(@:.docker=)) stacks/mbedtls-vulnerable
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/mbedtls:$$(basename $(@:.docker=)) > $@

# all: $(foreach tag, $(wildcard mbedtls-git/tags/*), $(subst mbedtls-git/tags/,.build/mbedtls/,$(tag)))
# all: .build/mbedtls/vulnerable



# GnuTLS

containers/gnutls/%.docker: stacks/gnutls-git/tags/% stacks/gnutls-git/Dockerfile stacks/gnutls-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/gnutls:$$(basename $(@:.docker=)) stacks/gnutls-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/gnutls:$$(basename $(@:.docker=)) > $@

containers/curl-gnutls/%.docker: containers/gnutls/%.docker stacks/curl-gnutls-git/Dockerfile stacks/curl-gnutls-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/curl-gnutls:$$(basename $(@:.docker=)) stacks/curl-gnutls-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/curl-gnutls:$$(basename $(@:.docker=)) > $@

# all: $(foreach tag, $(wildcard gnutls-git/tags/*), $(subst gnutls-git/tags/,.build/gnutls/,$(tag)))



# Fizz

containers/fizz/%.docker: stacks/fizz-git/tags/% stacks/fizz-git/Dockerfile stacks/fizz-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/fizz:$$(basename $(@:.docker=)) stacks/fizz-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/fizz:$$(basename $(@:.docker=)) > $@


# BoringSSL

containers/boringssl/%.docker: stacks/boringssl-git/tags/% stacks/boringssl-git/Dockerfile stacks/boringssl-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/boringssl:$$(basename $(@:.docker=)) stacks/boringssl-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/boringssl:$$(basename $(@:.docker=)) > $@


# PicoTLS

containers/picotls/%.docker: stacks/picotls-git/tags/% stacks/picotls-git/Dockerfile stacks/picotls-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/picotls:$$(basename $(@:.docker=)) stacks/picotls-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/picotls:$$(basename $(@:.docker=)) > $@


# Erlang

containers/erlang/%.docker: stacks/erlang-20-git/tags/% stacks/erlang-20-git/Dockerfile stacks/erlang-20-git/server.erl stacks/erlang-20-git/run_server.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/erlang:$$(basename $(@:.docker=)) stacks/erlang-20-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/erlang:$$(basename $(@:.docker=)) > $@

containers/erlang/%.docker: stacks/erlang-24-git/tags/% stacks/erlang-24-git/Dockerfile stacks/erlang-24-git/server.erl stacks/erlang-24-git/run_server.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/erlang:$$(basename $(@:.docker=)) stacks/erlang-24-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/erlang:$$(basename $(@:.docker=)) > $@


# NSS

containers/nss/%.docker: stacks/nss-git--3_15/tags/% stacks/nss-git--3_15/Dockerfile stacks/nss-git--3_15/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/nss:$$(basename $(@:.docker=)) stacks/nss-git--3_15
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/nss:$$(basename $(@:.docker=)) > $@

containers/nss/%.docker: stacks/nss-git--3_16_17/tags/% stacks/nss-git--3_16_17/Dockerfile stacks/nss-git--3_16_17/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/nss:$$(basename $(@:.docker=)) stacks/nss-git--3_16_17
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/nss:$$(basename $(@:.docker=)) > $@

containers/nss/%.docker: stacks/nss-git--3_18_20/tags/% stacks/nss-git--3_18_20/Dockerfile stacks/nss-git--3_18_20/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/nss:$$(basename $(@:.docker=)) stacks/nss-git--3_18_20
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/nss:$$(basename $(@:.docker=)) > $@

containers/nss/%.docker: stacks/nss-git--3_21_36/tags/% stacks/nss-git--3_21_36/Dockerfile stacks/nss-git--3_21_36/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/nss:$$(basename $(@:.docker=)) stacks/nss-git--3_21_36
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/nss:$$(basename $(@:.docker=)) > $@

containers/nss/%.docker: stacks/nss-git/tags/% stacks/nss-git/Dockerfile stacks/nss-git/run_client.sh
	docker build --build-arg COMMIT=$$(basename $(@:.docker=)) -t tls-test/nss:$$(basename $(@:.docker=)) stacks/nss-git
	mkdir -p $$(dirname $@)
	docker image ls -q tls-test/nss:$$(basename $(@:.docker=)) > $@





###################
# CRYPTO MATERIAL #
###################

crypto-material: crypto/generate.sh crypto/tls-server.conf crypto/tls-client.conf crypto/trusted-root-ca.conf crypto/untrusted-root-ca.conf crypto/Makefile
	make -C crypto material

clean:
	make -C crypto clean
	rm -f .build/*.docker
