# Usage with [cert-manager](https://cert-manager.io/)

## Enabling TLS for local development

### 1. Install [cert-manager](https://cert-manager.io/docs/installation/kubernetes/#installing-with-helm).

```console
$ # Create the namespace for the esp:
$ kubectl create namespace plgx
$ # Create the namespace for cert-manager:
$ kubectl create namespace cert-manager
$ # Add the jestack helm repo
$ helm repo add jetstack https://charts.jetstack.io
$ # Update your local Helm chart repository cache:
$ helm repo update
```

### 2. Create an issuer

You can create your own secret and CA issuer [by following these instructions](https://cert-manager.io/docs/configuration/ca/)

An automated way to do it if you are planning to enroll your host machine to the esp is to install [mkcert](https://github.com/FiloSottile/mkcert#installation). mkcert will add the generated certificates to your machine's trusted stores.

After installing it you can run the following script to generate a CA certificate and upload a secret named _polylogyx-ca-tls-secret_ to the _plgx_ namespace.

```console
$ ./examples/cert-manager/make_cert.sh plgx polylogyx-ca-tls-secret
```

Finally create the ca issuer in the same namespace as the application, using the same secret that we just created.

```console
$ kubectl apply -f ./examples/cert-manager/cert-manager-issuer.yaml -n plgx
```

You can verify that the issuer can sign certificates by running:

```console
$ kubectl -n plgx describe issuers.cert-manager.io ca-issuer | grep Message                
$ # Message:               Signing CA verified
```

### 3. Add annotations to the Ingress

Add these to your values.yaml file.

```yaml
plgx:
  ingress:
    hostname: polylogyx.dev
    annotations:
      kubernetes.io/ingress.class: "nginx"
      cert-manager.io/issuer: ca-issuer
    tls:
      enabled: true
```

As a final piece of the puzzle you can now add minikube's IP in your hosts file:

```console
$ # Get the minikube's <IP>
$ minikube ip
```

And add this to your hosts file
```txt
<IP> polylogyx.dev
```

### 4. Install plgx-esp

```console
$ helm repo add polylogyx https://polylogyx.github.io/plgx-esp
$ helm install esp polylogyx/polylogyx-esp -n plgx
```

👏 That's it. You should now be able to navigate to https://polylogyx.dev in your browser!!!