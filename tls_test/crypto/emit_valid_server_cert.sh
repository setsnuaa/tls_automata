#!/bin/bash

DIRNAME="$(dirname $0)"
cd "$DIRNAME"

NAME=$1

# Create TLS server request
SAN=DNS:"$NAME" \
openssl req -new -config tls-server.conf \
                 -out certs/$NAME.csr \
                 -keyout certs/$NAME.key \
                 -subj "/DC=fr/O=TLS-inferer GASP Inc/CN=$NAME"  &> /dev/null

# Create TLS server certificate (have to define DN, O, OUN and CM)
printf "y\ny" | openssl ca -config trusted-root-ca.conf \
                           -in "certs/$NAME.csr" \
                           -out "certs/$NAME.crt" \
                           -extensions server_ext  &> /dev/null
