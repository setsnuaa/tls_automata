#!/bin/bash

DIRNAME="$(dirname $0)"
cd "$DIRNAME"


#                        ---------------------
#                        -  Trusted Root CA  -
#                        ---------------------
#                             *      *
#                           *          *
#                         *              *
#  www.tls-inferer.gasp.ebfe.fr       invalid.tls-inferer.gasp.ebfe.fr


# CREATE TRUSTED CA (PKI)

#------------------------------------------------------#
#                CREATE TRUSTED ROOT CA                #
#------------------------------------------------------#

# Create directories
mkdir -p ca/trusted-root-ca/private ca/trusted-root-ca/db crl certs
chmod 700 ca/trusted-root-ca/private

# Create database
cp /dev/null ca/trusted-root-ca/db/trusted-root-ca.db
cp /dev/null ca/trusted-root-ca/db/trusted-root-ca.db.attr
echo 01 > ca/trusted-root-ca/db/trusted-root-ca.crt.srl
echo 01 > ca/trusted-root-ca/db/trusted-root-ca.crl.srl

# Create CA request
openssl req -new -config trusted-root-ca.conf \
                 -out ca/trusted-root-ca.csr \
                 -keyout ca/trusted-root-ca/private/trusted-root-ca.key \
                 -nodes

# Create CA certificate (enter "y" 2 times)
printf "y\ny" | openssl ca -selfsign -config trusted-root-ca.conf \
                           -in ca/trusted-root-ca.csr \
                           -out ca/trusted-root-ca.crt \
                           -extensions root_ca_ext


# CREATE UNTRUSTED CA (PKI)

#------------------------------------------------------#
#               CREATE UNTRUSTED ROOT CA               #
#------------------------------------------------------#

# Create directories
mkdir -p ca/untrusted-root-ca/private ca/untrusted-root-ca/db crl certs
chmod 700 ca/untrusted-root-ca/private

# Create database
cp /dev/null ca/untrusted-root-ca/db/untrusted-root-ca.db
cp /dev/null ca/trusted-root-ca/db/untrusted-root-ca.db.attr
echo 01 > ca/untrusted-root-ca/db/untrusted-root-ca.crt.srl
echo 01 > ca/untrusted-root-ca/db/untrusted-root-ca.crl.srl

# Create CA request
openssl req -new -config untrusted-root-ca.conf \
                 -out ca/untrusted-root-ca.csr \
                 -keyout ca/untrusted-root-ca/private/untrusted-root-ca.key \
                 -nodes

# Create CA certificate (enter "y" 2 times)
printf "y\ny" | openssl ca -selfsign -config untrusted-root-ca.conf \
                           -in ca/untrusted-root-ca.csr \
                           -out ca/untrusted-root-ca.crt \
                           -extensions root_ca_ext



#*************************       TLS SERVER CERTIFICATE       *************************#

#------------------------------------------------------#
#               FOR VALID TLS Certificate              #
#             www.tls-inferer.gasp.ebfe.fr             #
#------------------------------------------------------#

# Create TLS server request
SAN=DNS:www.tls-inferer.gasp.ebfe.fr \
openssl req -new -config tls-server.conf \
                 -out certs/tls-inferer-gasp.csr \
                 -keyout certs/tls-inferer-gasp.key \
                 -subj "/DC=fr/O=TLS-inferer GASP Inc/CN=wwww.tls-inferer.gasp.ebfe.fr"

# Create TLS server certificate (have to define DN, O, OUN and CM)
printf "y\ny" | openssl ca -config trusted-root-ca.conf \
                           -in certs/tls-inferer-gasp.csr \
                           -out certs/tls-inferer-gasp.crt \
                           -extensions server_ext



#--------------------------------------------------------#
#             FOR **INVALID** TLS Certificate            #
#            invalid.tls-inferer.gasp.ebfe.fr            #
#--------------------------------------------------------#

# Create TLS server request
SAN=DNS:invalid.tls-inferer.gasp.ebfe.fr \
openssl req -new -config tls-server.conf \
                 -out certs/invalid-tls-inferer-gasp.csr \
                 -keyout certs/invalid-tls-inferer-gasp.key \
                 -subj "/DC=fr/O=TLS-inferer GASP Inc/CN=invalid.tls-inferer.gasp.ebfe.fr"

# Create TLS server certificate
printf "y\ny" | openssl ca -config trusted-root-ca.conf \
                           -in certs/invalid-tls-inferer-gasp.csr \
                           -out certs/invalid-tls-inferer-gasp.crt \
                           -extensions server_ext

#--------------------------------------------------------#
#             FOR **INVALID** TLS Certificate            #
#           untrusted.tls-inferer.gasp.ebfe.fr           #
#--------------------------------------------------------#

# Create TLS server request
SAN=DNS:untrusted.tls-inferer.gasp.ebfe.fr \
openssl req -new -config tls-server.conf \
                 -out certs/untrusted-tls-inferer-gasp.csr \
                 -keyout certs/untrusted-tls-inferer-gasp.key \
                 -subj "/DC=fr/O=Untrusted TLS-inferer GASP Inc/CN=untrusted.tls-inferer.gasp.ebfe.fr"

# Create TLS server certificate
printf "y\ny" | openssl ca -config untrusted-root-ca.conf \
                           -in certs/untrusted-tls-inferer-gasp.csr \
                           -out certs/untrusted-tls-inferer-gasp.crt \
                           -extensions server_ext

