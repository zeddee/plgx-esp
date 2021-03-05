#!/usr/bin/env bash
set -e

HOST=$1
PORT=$2
OUT_PATH=$3

openssl s_client -showcerts -connect "$HOST:$PORT" < /dev/null | openssl x509 -outform PEM > "$OUT_PATH"