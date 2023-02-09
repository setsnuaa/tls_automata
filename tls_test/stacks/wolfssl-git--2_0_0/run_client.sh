#!/bin/bash

set -e

PORT=4433
KEYFILE=
CERTFILE=
CAFILE=-d
VERSION=-tls1_2
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
            CIPHERS="-l AES128-SHA"
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
            CAFILE="-A $OPTARG"
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
                    VERSION="-v 1"
                    ;;
                "1.1"|"TLS 1.1"|"TLS_1.1"|"tls11")
                    VERSION="-v 2"
                    ;;
                "1.2"|"TLS 1.2"|"TLS_1.2"|"tls12")
                    VERSION="-v 3"
                    ;;
                "1.3"|"TLS 1.3"|"TLS_1.3"|"tls13")
                    VERSION="-v 4"
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

#[ -f "$CERTFILE" ] || usage "$CERTFILE is not a certificate file"
#[ -f "$KEYFILE" ] || usage "$KEYFILE is not a key file"
[ "$PORT" -ge 1 -a "$PORT" -le 65535 ] || usage "$PORT is not a valid port value"

ncat -c "while read server port; do ./examples/client/client $VERSION $CIPHERS -p \$port $CAFILE -Y -g -h \$server < /dev/null; done" -l -p "$PORT" -k
