#!/bin/bash
# openssl
for file in stacks/openssl-git--1_1--3_0/tags/*
do
  ./infer-client.sh tls-test/openssl:"$(basename $file)" 1.3 tls13
done

# gnutls
for file in stacks/gnutls-git/tags/*
do
  ./infer-client.sh tls-test/gnutls:"$(basename $file)" 1.3 tls13
done
## boringssl
#for file in stacks/boringssl-git/tags/*
#do
#  ./infer-client.sh tls-test/boringssl:"$(basename $file)" 1.2 tls12
#done
# wolfssl
for file in stacks/wolfssl-git--3_15_5/tags/*
do
  ./infer-client.sh tls-test/wolfssl:"$(basename $file)" 1.3 tls13
done