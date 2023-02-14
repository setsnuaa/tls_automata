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

for file in stacks/mbedtls-git/tags4/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags4/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags5/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags5/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags6/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags6/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags7/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags7/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags8/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags8/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f

for file in stacks/mbedtls-git/tags9/*
do
  make containers/mbedtls/"$(basename $file)".docker
done
for file in stacks/mbedtls-git/tags9/*
do
  ./infer-client.sh tls-test/mbedtls:"$(basename $file)" 1.2 tls12
done
docker rmi `docker images | grep mbedtls | awk '{print $3}'`
docker image prune -f