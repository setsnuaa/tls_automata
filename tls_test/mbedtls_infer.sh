#!/bin/bash
for file in containers/mbedtls/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done