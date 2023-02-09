#!/bin/bash

set -e

PORT=4433
KEYFILE=/tmp/key.pem
CERTFILE=/tmp/cert.pem
CAFILE=-d

usage () {
    echo "Error: $1"
    echo "$0 [-C cert_file|-K key_file|-p port|-V version|-v|-A ca_file]" >&2
    exit 1
}

while getopts "C:K:p:A:V:v" option; do
    case "$option" in
        A)
            CAFILE="-A $OPTARG -F"
            ;;
        v)
            echo "Ignoring $option for now..."
            ;;
        C)
            CERTFILE="$OPTARG"
            ;;
        K)
            KEYFILE="$OPTARG"
            ;;
        p)
            PORT="$OPTARG"
            ;;
        V)
            case "$OPTARG" in
                "1.0"|"TLS 1.0"|"TLS_1.0")
                    VERSION="-v 1"
                    ;;
                "1.1"|"TLS 1.1"|"TLS_1.1")
                    VERSION="-v 2"
                    ;;
                "1.2"|"TLS 1.2"|"TLS_1.2")
                    VERSION="-v 3"
                    ;;
                "1.3"|"TLS 1.3"|"TLS_1.3")
                    VERSION="-v 4"
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

[ -f "$CERTFILE" ] || usage "$CERTFILE is not a certificate file"
[ -f "$KEYFILE" ] || usage "$KEYFILE is not a key file"
[ "$PORT" -ge 1 -a "$PORT" -le 65535 ] || usage "$PORT is not a valid port value"

./examples/server/server $VERSION -p "$PORT" -k "$KEYFILE" -c "$CERTFILE" $CAFILE -x -i -b -g
