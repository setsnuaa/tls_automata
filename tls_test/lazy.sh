#!/bin/bash
#make crypto-material
## tool
#make containers/tool/tls-inferer.docker
# openssl
for file in stacks/openssl-git--1_1--3_0/tags/*
do
  make containers/openssl/"$(basename $file)".docker
done
for file in stacks/openssl-git--1_0/tags/*
do
  make containers/openssl/"$(basename $file)".docker
done
for file in stacks/openssl-git--0_9_8/tags/*
do
  make containers/openssl/"$(basename $file)".docker
done
# gnutls
for file in stacks/gnutls-git/tags/*
do
  make containers/gnutls/"$(basename $file)".docker
done
# boringssl
for file in stacks/boringssl-git/tags/*
do
  make containers/boringssl/"$(basename $file)".docker
done