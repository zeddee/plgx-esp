{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "polylogyx.fullname" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Kubernetes standard labels
*/}}
{{- define "polylogyx.labels.standard" -}}
app.kubernetes.io/name: {{ include "common.names.name" . }}
helm.sh/chart: {{ include "common.names.chart" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Labels to use on deploy.spec.selector.matchLabels and svc.spec.selector
*/}}
{{- define "polylogyx.labels.matchLabels" -}}
app.kubernetes.io/name: {{ include "common.names.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Return the rsyslogf pvc name.
*/}}
{{- define "polylogyx.rsyslogf.pvcName" -}}
{{- .Values.plgx.rsyslogf.persistence.existingClaim | default (printf "%s-rsyslogf-pvc" (include "polylogyx.fullname" .)) -}}
{{- end -}}


{{/*
Return the yara pvc name
*/}}
{{- define "polylogyx.yara.pvcName" -}}
{{- .Values.plgx.persistence.yara.existingClaim | default (printf "%s-yara-pvc" (include "polylogyx.fullname" .)) -}}
{{- end -}}

{{/*
Return the yara pvc storageClass
*/}}
{{- define "polylogyx.yara.storageClass" -}}
{{- $storageClass := .Values.plgx.persistence.yara.storageClass -}}

{{- if $storageClass -}}
  {{- if (eq "-" $storageClass) -}}
      {{- printf "storageClassName: \"\"" -}}
  {{- else }}
      {{- printf "storageClassName: %s" $storageClass -}}
  {{- end -}}
{{- end -}}
{{- end -}}

{{/*
Return the carves pvc storageClass
*/}}
{{- define "polylogyx.carves.storageClass" -}}
{{- $storageClass := .Values.plgx.persistence.carves.storageClass -}}

{{- if $storageClass -}}
  {{- if (eq "-" $storageClass) -}}
      {{- printf "storageClassName: \"\"" -}}
  {{- else }}
      {{- printf "storageClassName: %s" $storageClass -}}
  {{- end -}}
{{- end -}}
{{- end -}}

{{/*
Return the carves pvc name
*/}}
{{- define "polylogyx.carves.pvcName" -}}
{{- .Values.plgx.persistence.carves.existingClaim | default (printf "%s-carves-pvc" (include "polylogyx.fullname" .)) -}}
{{- end -}}

{{- define "polylogyx.pvcs.storageClass" -}}

{{- $storageClass := .Values.plgx.persistence.storageClass -}}

{{- if $storageClass -}}
  {{- if (eq "-" $storageClass) -}}
      {{- printf "storageClassName: \"\"" -}}
  {{- else }}
      {{- printf "storageClassName: %s" $storageClass -}}
  {{- end -}}
{{- end -}}

{{- end -}}

{{- define "polylogyx.rsyslogf.storageClass" -}}

{{- $storageClass := default .Values.plgx.persistence.storageClass .Values.plgx.rsyslogf.persistence.storageClass -}}

{{- if $storageClass -}}
  {{- if (eq "-" $storageClass) -}}
      {{- printf "storageClassName: \"\"" -}}
  {{- else }}
      {{- printf "storageClassName: %s" $storageClass -}}
  {{- end -}}
{{- end -}}

{{- end -}}

{{/*
Return the image name as a string
{{ include "polylogyx.images.image" ( dict "imageRoot" .Values.path.to.the.image "global" $) }}
*/}}
{{- define "polylogyx.images.image" -}}
{{- $registryName := .imageRoot.registry -}}
{{- $repositoryName := .imageRoot.repository -}}
{{- $tag := .imageRoot.tag | toString -}}
{{- if .global }}
    {{- if .global.imageRegistry }}
     {{- $registryName = .global.imageRegistry -}}
    {{- end -}}
{{- end -}}
{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- end -}}

{{/*
Return the polylogyx-esp esp image name
*/}}
{{- define "polylogyx.images.esp" -}}
{{- $root := dict "imageRoot" .Values.plgx.esp.image "global" .Values.global -}}
{{- include "polylogyx.images.image" $root -}}
{{- end -}}

{{/*
Return the polylogyx-esp ui image name
*/}}
{{- define "polylogyx.images.ui" -}}
{{- include "polylogyx.images.image" ( dict "imageRoot" .Values.plgx.ui.image "global" $) -}}
{{- end -}}

{{/*
Return the polylogyx-esp fileserver image name
*/}}
{{- define "polylogyx.images.fileserver" -}}
{{- include "polylogyx.images.image" ( dict "imageRoot" .Values.plgx.fileserver.image "global" $)}}
{{- end -}}

{{/*
Return the polylogyx-esp rsyslogf image name
*/}}
{{- define "polylogyx.images.rsyslogf" -}}
{{- $id := .Values.plgx.rsyslogf.image.registry -}}
{{- $root := dict "imageRoot" .Values.plgx.rsyslogf.image "global" .Values.global -}}
{{- include "polylogyx.images.image" ($root) -}}
{{- end -}}