# Helm Chart for Polylogyx ESP

PolyLogyx ESP leverages the [Osquery](https://osquery.io/) tool, with [PolyLogx Extension](https://github.com/polylogyx/osq-ext-bin) to provide endpoint visibility and monitoring at scale. To get the details of the architecture of the full platform, please read the [platform docs](https://github.com/polylogyx/platform-docs). This repository provides the community release of the platform which focuses on the Osquery based agent management to provide visbility into endpoint activities, query configuration management, a live query interface and alerting capabilities based on security critical events.

## 👋 Hey

> This chart is under heavy development at the moment. We welcome contributions of any kind so feel free to drop us a message at #xdr or create an issue/merge request in the repo.

## TLDR;

```sh
$ helm repo add polylogyx https://polylogyx.github.io/plgx-esp
$ helm install polylogyx/polylogyx-esp
```

## Introduction

This chart bootstraps a [PolyLogyx ESP](https://github.com/polylogyx/plgx-esp) deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Installing for local development using Minikube

To install the chart:

Install [cert-manager](https://cert-manager.io/) and create secrets

```console
$ kubectl create namespace plgx
$ ./examples/cert-manager/make_cert.sh plgx polylogyx-ca-tls-secret
$ kubectl apply -f ./examples/cert-manager/cert-manager-issuer.yaml -n plgx
$ kubectl apply -f ./examples/cert-manager/certificate.yaml -n plgx
```

## Prerequisites

- Kubernetes 1.12+
- Helm 3.0-beta3+
- PV provisioner support in the underlying infrastructure
- ReadWriteMany volumes for deployment scaling

## Resources

Configure [rabbitmq](https://github.com/bitnami/charts/tree/master/bitnami/rabbitmq)

Configure [postgress](https://github.com/bitnami/charts/tree/master/bitnami/postgresql)

## Docs:

Enrolling an endpoint:

If you use the default ingress configs run

```sh
sudo ./plgx_cpt.sh -p -i <HOST> -port 443
```

Notice that it needs to be TLS encrypted traffic.

## Parameters:

The following table lists the configurable parameters of the Polylogyx ESP chart and their default values.

> **Tip**: You can lint the values you provide to the chart by using the `helm lint @TODO[repo_name/esp] -f your_values_file.yaml` command.

| Parameter                 | Description                                     | Default Value                                           |
| ------------------------- | ----------------------------------------------- | ------------------------------------------------------- |
| `global.imageRegistry`    | Global Docker image registry                    | `nil`                                                   |
| `global.imagePullSecrets` | Global Docker registry secret names as an array | `[]` (does not add image pull secrets to deployed pods) |
| `global.storageClass`     | Global storage class for dynamic provisioning   | `nil`                                                   |

## Internal TODO:

<input type="checkbox" disabled>Testing. How do we make changes to this chart with confidence that all features work as expected? Do we need a new test suite or can we use an existing one?

## Troubleshooting
