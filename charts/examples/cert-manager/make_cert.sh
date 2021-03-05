#!/usr/bin/env bash
set -e

echo "Creating self-signed CA certificates for TLS and installing them in the local trust stores"

NAMESPACE=$1
SECRET_NAME=$2

CA_CERTS_FOLDER=$(pwd)/.certs
# This requires mkcert to be installed/available
echo "${CA_CERTS_FOLDER}"
rm -rf "${CA_CERTS_FOLDER}"
mkdir -p "${CA_CERTS_FOLDER}"
mkdir -p "${CA_CERTS_FOLDER}"/"${ENVIRONMENT_DEV}"
# The CAROOT env variable is used by mkcert to determine where to read/write files
# Reference: https://github.com/FiloSottile/mkcert
CAROOT=${CA_CERTS_FOLDER}/${ENVIRONMENT_DEV} mkcert -install

echo "Creating K8S secrets with the CA private keys (will be used by the cert-manager CA Issuer)"

kubectl -n "$NAMESPACE" create secret tls "$SECRET_NAME" --key="${CA_CERTS_FOLDER}"/"${ENVIRONMENT_DEV}"/rootCA-key.pem --cert="${CA_CERTS_FOLDER}"/"${ENVIRONMENT_DEV}"/rootCA.pem
