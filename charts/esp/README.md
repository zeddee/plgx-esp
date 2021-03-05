# polylogyx-esp

![Version: 0.0.11](https://img.shields.io/badge/Version-0.0.11-informational?style=flat-square) ![AppVersion: 2.1.0](https://img.shields.io/badge/AppVersion-2.1.0-informational?style=flat-square)

A Helm Chart for deploying the polylogyx endpoint security platform

PolyLogyx ESP leverages the [Osquery](https://osquery.io/) tool, with [PolyLogx Extension](https://github.com/polylogyx/osq-ext-bin) to provide endpoint visibility and monitoring at scale. To get the details of the architecture of the full platform, please read the [platform docs](https://github.com/polylogyx/platform-docs). This repository provides the community release of the platform which focuses on the Osquery based agent management to provide visbility into endpoint activities, query configuration management, a live query interface and alerting capabilities based on security critical events.

## TLDR;

```console
$ helm repo add polylogyx https://polylogyx.github.io/plgx-esp
$ helm install my-release polylogyx/polylogyx-esp
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://charts.bitnami.com/bitnami | postgresql | 10.2.0 |
| https://charts.bitnami.com/bitnami | rabbitmq | 8.5.4 |

## Introduction

This chart bootstraps a [PolyLogyx ESP](https://github.com/polylogyx/plgx-esp) deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| plgx.api_keys.IBMxForceKey | string | `""` | IBMxForceKey API Key |
| plgx.api_keys.IBMxForcePass | string | `""` | IBMxForcePass Password |
| plgx.api_keys.alienvault | string | `""` | AlienVault API Key |
| plgx.api_keys.vt | string | `""` | VirusTotal API Key |
| plgx.auth.enroll_secret | string | `nil` | ESP application secret for agent enrollment |
| plgx.auth.password | string | `nil` | ESP application password |
| plgx.auth.user | string | `nil` | ESP application username |
| plgx.databaseUrl | string | `""` | The connection url for the postgresql database |
| plgx.esp.enabled | bool | `true` | Set to true to enable the esp component |
| plgx.esp.image | object | `{"registry":"ghcr.io","repository":"polylogyx/esp","tag":"latest"}` | ESP image |
| plgx.esp.pullPolicy | string | `"Always"` | Specify an imagePullPolicy. It is suggested to use 'Always' if image tag is 'latest', else set to 'IfNotPresent' ref: http://kubernetes.io/docs/user-guide/images/#pre-pulling-images |
| plgx.esp.pullSecrets | list | `[]` | Specify docker-registry secret names |
| plgx.esp.replicas | int | `1` | Number of replicas to deploy |
| plgx.esp.resources | object | `{}` |  |
| plgx.esp.service | object | `{"port":80,"type":"ClusterIP"}` | ESP service parameters |
| plgx.fileserver.enabled | bool | `true` | Set to true to enable the fileserver component |
| plgx.fileserver.image | object | `{"registry":"ghcr.io","repository":"polylogyx/esp-fileserver","tag":"latest"}` | ESP Fileserver image |
| plgx.fileserver.pullPolicy | string | `"Always"` | Specify an imagePullPolicy. It is suggested to use 'Always' if image tag is 'latest', else set to 'IfNotPresent' ref: http://kubernetes.io/docs/user-guide/images/#pre-pulling-images |
| plgx.fileserver.pullSecrets | list | `[]` | Specify docker-registry secret names |
| plgx.fileserver.replicas | int | `1` | Number of replicas to deploy |
| plgx.fileserver.service | object | `{"port":80,"type":"ClusterIP"}` | ESP Fileserver service parameters |
| plgx.ingress.annotations | object | `{}` | Ingress annotations |
| plgx.ingress.enabled | bool | `true` | Set to true to enable the ingress |
| plgx.ingress.hostname | string | `nil` | Default host for the ingress  |
| plgx.ingress.tls | object | `{"enabled":true}` | Create ingress TLS section |
| plgx.persistence.carves.accessMode | string | `"ReadWriteMany"` | PVC Access Mode for Carves files |
| plgx.persistence.carves.enabled | bool | `true` | Enable persistence for Carves files |
| plgx.persistence.carves.existingClaim | string | `nil` | Provide an existing `PersistentVolumeClaim` for Carves files |
| plgx.persistence.carves.size | string | `"100Mi"` | PVC Storage Request for Carves files |
| plgx.persistence.carves.storageClass | string | `nil` | PVC Storage Class for Carves files |
| plgx.persistence.yara.accessMode | string | `"ReadWriteMany"` | PVC Access Mode for Yara files |
| plgx.persistence.yara.enabled | bool | `true` | Enable persistence for Yara files |
| plgx.persistence.yara.existingClaim | string | `nil` | Provide an existing `PersistentVolumeClaim` for Yara files |
| plgx.persistence.yara.size | string | `"100Mi"` | PVC Storage Request for Yara files |
| plgx.persistence.yara.storageClass | string | `nil` | PVC Storage Class for Yara files |
| plgx.purge_duration | string | `"7"` | Specifies the duration after which data should be purged |
| plgx.rabbitmqPassword | string | `""` |  |
| plgx.rabbitmqUser | string | `""` | The rabbitMQ instance username |
| plgx.rsyslogf.enabled | bool | `true` | Set to true to enable the rsyslogf component |
| plgx.rsyslogf.image | object | `{"registry":"ghcr.io","repository":"polylogyx/esp-rsyslogf","tag":"latest"}` | ESP Rsyslogf image |
| plgx.rsyslogf.persistence | object | `{"accessMode":"ReadWriteMany","enabled":true,"existingClaim":null,"size":"500Mi","storageClass":null}` | ESP Rsyslogf persistence parameters |
| plgx.rsyslogf.persistence.accessMode | string | `"ReadWriteMany"` | PVC Access Mode for rsyslogf data |
| plgx.rsyslogf.persistence.enabled | bool | `true` | Enable persistence for rsyslogf data |
| plgx.rsyslogf.persistence.existingClaim | string | `nil` | Provide an existing `PersistentVolumeClaim` for rsyslogf data |
| plgx.rsyslogf.persistence.size | string | `"500Mi"` | PVC Storage Request for rsyslogf data |
| plgx.rsyslogf.persistence.storageClass | string | `nil` | PVC Storage Class for rsyslogf data |
| plgx.rsyslogf.pullPolicy | string | `"Always"` | Specify an imagePullPolicy. Defaults to 'Always' if image tag is 'latest', else set to 'IfNotPresent' ref: http://kubernetes.io/docs/user-guide/images/#pre-pulling-images |
| plgx.rsyslogf.pullSecrets | list | `[]` | Specify docker-registry secret names |
| plgx.rsyslogf.replicas | int | `1` | Number of replicas to deploy |
| plgx.rsyslogf.service | object | `{"port":80,"type":"ClusterIP"}` | ESP Rsyslogf service parameters |
| plgx.threatIntel.alertFrequency | string | `"30"` |  |
| plgx.ui.enabled | bool | `true` | Set to true to enable the ui component |
| plgx.ui.image | object | `{"registry":"ghcr.io","repository":"polylogyx/esp-ui","tag":"latest"}` | ESP UI image |
| plgx.ui.pullPolicy | string | `"Always"` | Specify an imagePullPolicy. It is suggested to use 'Always' if image tag is 'latest', else set to 'IfNotPresent' ref: http://kubernetes.io/docs/user-guide/images/#pre-pulling-images |
| plgx.ui.pullSecrets | list | `[]` | Specify docker-registry secret names |
| plgx.ui.replicas | int | `1` | Number of replicas to deploy |
| plgx.ui.service | object | `{"port":80,"type":"ClusterIP"}` | ESP UI service parameters |
| postgresql | object | You can find all of the configuration options for [the postgresql chart here](https://github.com/bitnami/charts/tree/master/bitnami/postgresql) | PostgreSQL configuration. |
| rabbitmq | object | You can find all of the configuration options for [the rabbitmq chart here](https://github.com/bitnami/charts/tree/master/bitnami/rabbitmq) | RabbitMQ configuration. |

## Installing on Minikube for local development

### 1. [Install minikube](https://minikube.sigs.k8s.io/docs/start/)

### 2. Enable Ingress for Minikube. ([Details](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/))

```
$ # Start minikube
$ minikube start
$ # enable the NGINX Ingress controller
$ minikube addons enable ingress
$ # Verify the installation
$ kubectl get pods -n kube-system | grep ingress
```

### 3. Enabling TLS for your Ingress

You can [create your own certificate](https://kubernetes.github.io/ingress-nginx/user-guide/tls/) or

for a more realistic development environment you can follow the guide on how to use cert-manager in the _/charts/examples/cert-manager_ folder.
