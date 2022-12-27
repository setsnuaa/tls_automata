#!/bin/bash

set -e

PORT=4433
KEYFILE=
CERTFILE=
CAFILE=
VERSION=-tls1_2
BEHAVIOUR=http
VERBOSE=
CIPHERS=

usage () {
    echo "Error: $1"
    echo "$0 [-C cert_file|-K key_file|-A ca_file|-p port|-V version|-v|-B behaviour]" >&2
    exit 1
}

while getopts "C:KA::p:vV:B:c:" option; do
    case "$option" in
        c)
            CIPHERS="-cipher $OPTARG"
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
                    VERSION=-tls1
                    ;;
                "1.1"|"TLS 1.1"|"TLS_1.1"|"tls11")
                    VERSION=-tls1_1
                    ;;
                "1.2"|"TLS 1.2"|"TLS_1.2"|"tls12")
                    VERSION=-tls1_2
                    ;;
                "1.3"|"TLS 1.3"|"TLS_1.3"|"tls13")
                    VERSION="-tls1_3 -no_middlebox"
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

PATH="/usr/local/ssl/bin:$PATH"
ncat -c "while read server port; do openssl s_client $VERSION $CIPHERS -connect \$server:\$port < /dev/null > /dev/null 2> /dev/null; done" -l -p "$PORT" -k
