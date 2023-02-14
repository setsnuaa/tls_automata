#!/bin/bash
for file in stacks/mbedtls-git/tags/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done