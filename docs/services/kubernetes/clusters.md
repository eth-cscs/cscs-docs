[](){#ref-kubernetes-clusters}
# CSCS Kubernetes clusters

This document provides an overview of the Kubernetes clusters maintained by CSCS and offers step-by-step instructions for accessing and interacting with them.

## Architecture

All Kubernetes clusters at CSCS are:

- Managed using **[Rancher](https://www.rancher.com)**
- Running **[RKE2 (Rancher Kubernetes Engine 2)](https://github.com/rancher/rke2)**

CSCS offers two types of Kubernetes clusters for partners:

- **Harvester-only clusters**: These clusters run exclusively on virtual machines provisioned by Harvester (SUSE Virtualization), providing a flexible and isolated environment suitable for most workloads.
- **Alpernetes clusters**: These clusters combine Harvester VMs with compute nodes from the Alps supercomputer. This hybrid setup, called *Alpernetes*, enables workloads to leverage both virtualized infrastructure and high-performance computing resources within the same Kubernetes environment.

## Cluster Environments

Clusters are grouped into two main environments:

- **TDS** – Test and Development Systems  
- **PROD** – Production

See [Kubernetes upgrades][ref-kubernetes-clusters-upgrades] for detailed upgrade policy.

## Kubernetes API Access

You can access the Kubernetes API in two main ways:

### Direct Internet Access

- A Virtual IP is exposed for the API server.  
- Access is restricted by source IP addresses of the partner.

### Access via CSCS Jump Host

- Connect through a jump host (e.g., `ela.cscs.ch`).
- API calls are securely proxied through Rancher.

To check which method you are using, examine the `current-context` in your `kubeconfig` file.

## Cluster Access

To interact with the cluster, you need the `kubectl` CLI:  
🔗 [Install kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)  
??? Note "`kubectl` is pre-installed on the CSCS jump host."


### Retrieve your kubeconfig file

#### Internal CSCS Users
Access [Rancher](https://rancher.cscs.ch) and download the kubeconfig for your cluster. 
   
#### External Users
A specific Rancher user and password should have been provided to the partner.

Use the `kcscs` tool installed on `ela.cscs.ch` to obtain the kubeconfig by following the next steps.

Download your SSH keys from [SSH Service](https://sshservice.cscs.ch) (and add them to the SSH agent).

SSH to the jump host using the downloaded SSH keys
```bash
ssh ela.cscs.ch
```

Login with `kcscs` with the provided Rancher credentials
```bash
kcscs login
```

List the accessible clusters
```bash
kcscs list
```

Retrieve the kubeconfig file for a specific cluster
```bash
kcscs get
```


### Store the kubeconfig file

```bash
mv mykubeconfig.yaml ~/.kube/config
```
or
```bash
export KUBECONFIG=/home/user/kubeconfig.yaml
```

### Test connectivity
   ```bash
   kubectl get nodes
   ```

!!! warning
    The kubeconfig file contains credentials. Keep it secure.

## Pre-installed Applications

All CSCS-provided clusters include a set of pre-installed tools and components, described below:

### `ceph-csi`

Provides dynamic persistent volume provisioning via the Ceph Container Storage Interface (CEPH CSI).

#### Storage Classes

- `cephfs` – ReadWriteMany (RWX), backed by HDD (large data volumes)
- `rbd-hdd` – ReadWriteOnce (RWO), backed by HDD
- `rbd-nvme` – RWO, backed by NVMe (high-performance workloads like databases)
- `*-retain` – Same classes, but retain the volume after PVC deletion

### `external-dns`

Automatically manages DNS entries for:

- Ingress resources
- Services of type `LoadBalancer` (when annotated)

#### Example
```bash
kubectl annotate service nginx "external-dns.alpha.kubernetes.io/hostname=nginx.mycluster.tds.cscs.ch."
```

!!! Note "Use a valid name under the configured subdomain"
    
🔗 [external-dns documentation](https://github.com/kubernetes-sigs/external-dns)

### `cert-manager`

Handles automatic issuance of TLS certificates from Let's Encrypt.

#### Example
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: echo
spec:
  secretName: echo
  commonName: echo.mycluster.tds.cscs.ch
  dnsNames:
    - echo.mycluster.tds.cscs.ch
  issuerRef:
    kind: ClusterIssuer
    name: letsencrypt
```

You can also issue certificates automatically via Ingress annotations (see `ingress-nginx` section).

🔗 [cert-manager documentation](https://cert-manager.io)

### `metallb`

Enables `LoadBalancer` service types by assigning public IPs.

!!! Warning "The public IP pool is limited. Prefer using `Ingress` unless you specifically need a `LoadBalancer` Service for TCP traffic."

🔗 [metallb documentation](https://metallb.universe.tf)

###  `ingress-nginx`

Default Ingress controller with class `nginx`.  
Supports automatic TLS via cert-manager annotations.

Example:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myIngress
  namespace: myIngress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  rules:
    - host: example.tds.cscs.ch
      http:
        paths:
          - pathType: Prefix
            path: /
            backend:
              service:
                name: myservice
                port:
                  number: 80
  tls:
    - hosts:
        - example.tds.cscs.ch
      secretName: myingress-cert
```

🔗 [NGINX Ingress Docs](https://docs.nginx.com/nginx-ingress-controller)  
🔗 [cert-manager Ingress Usage](https://cert-manager.io/docs/usage/ingress/)

### `external-secrets`

Integrates with secret management tools like **HashiCorp Vault**.

Enables the usage of `ExternalSecret` resources to fetch secrets from `SecreStore` or `ClusterSecretStore` resources to fetch secrets and store them into `Secrets` inside the cluster.

It helps to avoid storing secrets in the deployment manifests, especially in GitOps environments.

🔗 [external-secrets documentation](https://external-secrets.io/)

### `kured`

Responsible for automatic node reboots (e.g., after kernel updates).

🔗 [kured documentation](https://kured.dev/)

### Observability

Includes:

- **Beats agents** – Export logs and metrics to CSCS’s central log system
- **Prometheus** – Scrapes metrics and exports them to CSCS's central monitoring cluster
