#!/bin/bash

set -e

PORT=4433
CAFILE=
VERSION=tls1_2
VERBOSE=

usage () {
    echo "$0 [-C cert_file|-K key_file|-A ca_file|-p port|-V version|-v|-B behaviour]" >&2
    exit 1
}

while getopts "A:p:vV:" option; do
    case "$option" in
        A)
            CAFILE="$OPTARG"
            ;;

        p)
            PORT="$OPTARG"
            ;;
        v)
            VERBOSE=1
            ;;
	V)
            case "$OPTARG" in
                "1.0"|"TLS 1.0"|"TLS_1.0"|"tls10"|"tls1")
                    VERSION=tls1
                    ;;
                "1.1"|"TLS 1.1"|"TLS_1.1"|"tls11")
                    VERSION=tls1_1
                    ;;
                "1.2"|"TLS 1.2"|"TLS_1.2"|"tls12")
                    VERSION=tls1_2
                    ;;
                "1.3"|"TLS 1.3"|"TLS_1.3"|"tls13")
                    VERSION=tls1_3
                    ;;
                *)
                    usage "invalid version \"$OPTARG\" (expected: 1.0 to 1.3)"
                    ;;
            esac
            ;;
        *)
            usage "invalid option \"$OPTION\""
            ;;
    esac
done

[ "$PORT" -ge 1 -a "$PORT" -le 65535 ] || usage "$PORT is not a valid port value"

ncat -c "while read server port; do /mbedtls/programs/ssl/ssl_client2 server_name=\$server server_port=\$port min_version=$VERSION max_version=$VERSION auth_mode=none < /dev/null > /dev/null 2> /dev/null; done" -l -p "$PORT" -k
