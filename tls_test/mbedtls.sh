#!/bin/bash
for file in stacks/mbedtls-git/tags/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags1/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags1/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags2/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags2/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags3/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags3/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git4/tags/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git4/tags/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f