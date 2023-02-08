#!/bin/bash
#make crypto-material
## tool
#make containers/tool/tls-inferer.docker
# openssl
for file in stacks/openssl-git--1_1--3_0/tags/*
do
  echo $file
done