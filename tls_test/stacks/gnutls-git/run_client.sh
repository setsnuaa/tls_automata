#!/bin/bash

set -e

PORT=4433
KEYFILE=
CERTFILE=
CAFILE=--insecure
VERSION=VERS-TLS1.2
BEHAVIOUR=http
VERBOSE=

usage () {
    echo "Error: $1"
    echo "$0 [-C cert_file|-K key_file|-A ca_file|-p port|-V version|-v|-B behaviour]" >&2
    exit 1
}

while getopts "C:KA::p:vV:B:c:" option; do
    case "$option" in
	c)
            echo "Ignoring \"$OPTION\" for now"
            ;;
        C)
            CERTFILE="$OPTARG"
            usage "unsupported option for now (-C)"
            ;;
        K)
            KEYFILE="$OPTARG"
            usage "unsupported option for now (-K)"
            ;;
        A)
            CAFILE="--x509cafile=$OPTARG"
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
                    VERSION=VERS-TLS1.0
                    ;;
                "1.1"|"TLS 1.1"|"TLS_1.1"|"tls11")
                    VERSION=VERS-TLS1.1
                    ;;
                "1.2"|"TLS 1.2"|"TLS_1.2"|"tls12")
                    VERSION=VERS-TLS1.2
                    ;;
                "1.3"|"TLS 1.3"|"TLS_1.3"|"tls13")
                    VERSION=VERS-TLS1.3
                    ;;
                *)
                    usage "invalid version \"$OPTARG\" (expected: 1.0 to 1.3)"
                    ;;
            esac
            ;;
        B)
            case "$OPTARG" in
                "http")
                    BEHAVIOUR="$OPTARG"
                    usage "unsupported behaviour \"$OPTARG\""
                    ;;
                "echo")
                    usage "unsupported behaviour \"$OPTARG\""
                    ;;
                *)
                    usage "invalid behaviour \"$OPTARG\" (expected: http or echo)"
                    ;;
            esac
            ;;
        *)
            usage "invalid option \"$OPTION\""
            ;;
    esac
done

[ "$PORT" -ge 1 -a "$PORT" -le 65535 ] || usage "$PORT is not a valid port value"

ncat -c "while read server port; do gnutls-cli $CAFILE --priority NORMAL:-VERS-TLS-ALL:+$VERSION -p \$port \$server < /dev/null > /dev/null 2> /dev/null; done" -l -p "$PORT" -k
