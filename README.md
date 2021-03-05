# Helm Chart for Polylogyx ESP

PolyLogyx ESP leverages the [Osquery](https://osquery.io/) tool, with [PolyLogx Extension](https://github.com/polylogyx/osq-ext-bin) to provide endpoint visibility and monitoring at scale. To get the details of the architecture of the full platform, please read the [platform docs](https://github.com/polylogyx/platform-docs). This repository provides the community release of the platform which focuses on the Osquery based agent management to provide visbility into endpoint activities, query configuration management, a live query interface and alerting capabilities based on security critical events.

## 👋 Hey

> This chart is under heavy development at the moment. We welcome contributions of any kind so feel free to drop us a message at #xdr or create an issue/merge request in the repo.

## TLDR;

```sh
$ helm repo add @TODO https://@TODO
$ helm install release-name @TODO
```

## Installing the Chart (DEV)

To install the chart:

1. Publish the images to a registry. For minikube you can push to minikube's local registry.

2. Install cert-manager and create secrets

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

## Development:

You can use [minikube](https://github.com/kubernetes/minikube) to develop and test the chart locally.

The easiest way to put local images to minikube is to run

```sh
make build_images
```

to build the images inside minikube's local registry.

This command builds all the images for polylogyx inside the cluster's image registry cache, which means they will be available for local deployments.
To use the cached images in your containers you will need to provide the
`imagePullPolicy: Never`
configuration option in the values file.

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

<input type="checkbox" disabled>Deploy an example chart in our cluster

<input type="checkbox" disabled>How/Where do we provide the helm chart? Do we need a private registry for customers on enterprise edition? What registry are we going to use for the community edition? [Artifact Hub](https://artifacthub.io/) looks like the preferred place to release charts by the community.

<input type="checkbox" disabled> Minimum requirements. kubernetes/helm versions and cluster requirements.

<input type="checkbox" disabled> Configuration options. Should we expose more options through the values.yaml file?

<input type="checkbox" disabled>Testing. How do we make changes to this chart with confidence that all features work as expected? Do we need a new test suite or can we use an existing one?

<input type="checkbox" disabled>Automation: Once we know the IP address generate the osquery.flags file with the correct ip/host

<input type="checkbox" disabled> Versioning and support for the chart. How do we make sure this chart stays relevant? Will we offer upgrade paths, support etc?

<input type="checkbox" disabled> Monitoring. Should we provide prometheus or similar monitoring in the chart?

<input type="checkbox" disabled> Using TLS certificates

- <input type="checkbox" disabled> Existing certificates
- <input type="checkbox" disabled> Using cert-manager
- <input type="checkbox" disabled> Issuing your own
- <input type="checkbox" disabled> Using lets-encrypt
- <input type="checkbox" disabled> Persistent Volumes example with a cloud service provider

## Troubleshooting
