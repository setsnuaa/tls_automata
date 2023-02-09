#!/bin/bash
# gnutls
for file in stacks/gnutls-git/tags/*
do
  make containers/gnutls/"$(basename $file)".docker
done