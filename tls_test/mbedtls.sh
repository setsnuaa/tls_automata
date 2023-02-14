#!/bin/bash
for file in stacks/mbedtls-git/tags/*
do
  make containers/mbedtls/"$(basename $file)".docker
done