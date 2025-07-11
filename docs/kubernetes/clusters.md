
# CSCS Kubernetes Clusters

This document provides an overview of the Kubernetes clusters maintained by CSCS and offers step-by-step instructions for accessing and interacting with them.

---

## Architecture

All Kubernetes clusters at CSCS are:

- Managed using **[Rancher](https://www.rancher.com)**
- Running **[RKE2 (Rancher Kubernetes Engine 2)](https://github.com/rancher/rke2)**

---

## Cluster Environments

Clusters are grouped into two main environments:

- **TDS** – Test and Development Systems  
- **PROD** – Production

TDS clusters receive updates first. If no issues arise, the same updates are then applied to PROD clusters.

---

## Kubernetes API Access

You can access the Kubernetes API in two main ways:

### Direct Internet Access

- A Virtual IP is exposed for the API server.  
- Access can be restricted by source IP addresses.

### Access via CSCS Jump Host

- Connect through a bastion host (e.g., `ela.cscs.ch`).
- API calls are securely proxied through Rancher.

To check which method you are using, examine the `current-context` in your `kubeconfig` file.

---

## Cluster Access

To interact with the cluster, you need the `kubectl` CLI:  
🔗 [Install kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)  
> `kubectl` is pre-installed on the CSCS jump host.

### Step-by-Step Access Guide

#### Retrieve your kubeconfig file
   - If you have a CSCS account and can access [Rancher](https://rancher.cscs.ch), download the kubeconfig for your cluster.
   
   - If you have a CSCS account but can't access [Rancher](https://rancher.cscs.ch), request a local Rancher user and use the **kcscs** tool installed on **ela.cscs.ch** to obtain the kubeconfig:
    - Download your SSH keys from [SSH Service](https://sshservice.cscs.ch)
    - SSH to `ela.cscs.ch` using the downloaded SSH keys
    - Run `kcscs login` and insert your Rancher local user credentials (Supplied by CSCS)
    - Run `kcscs list` to list the clusters you have access to
    - Run `kcscs get` to get the kubeconfig file for a specific cluster

   - If you don't have a CSCS account, open a Service Desk ticket to ask support.

#### Store the kubeconfig file
   ```bash
   mv mykubeconfig.yaml ~/.kube/config
   # or
   export KUBECONFIG=/home/user/kubeconfig.yaml
   ```

#### Test connectivity
   ```bash
   kubectl get nodes
   ```

> ⚠️ The kubeconfig file contains credentials. Keep it secure.

---

## Pre-installed Applications

All CSCS-provided clusters include a set of pre-installed tools and components, described below:

---

### 📦 `ceph-csi`

Provides **dynamic persistent volume provisioning** via the Ceph Container Storage Interface.

#### Storage Classes

- `cephfs` – ReadWriteMany (RWX), backed by HDD (large data volumes)
- `rbd-hdd` – ReadWriteOnce (RWO), backed by HDD
- `rbd-nvme` – RWO, backed by NVMe (high-performance workloads like databases)
- `*-retain` – Same classes, but retain the volume after PVC deletion

---

### 🌐 `external-dns`

Automatically manages DNS entries for:

- Ingress resources
- Services of type `LoadBalancer` (when annotated)

#### Example
```bash
kubectl annotate service nginx "external-dns.alpha.kubernetes.io/hostname=nginx.mycluster.tds.cscs.ch."
```

> ✅ Use a valid name under the configured subdomain.  
📄 [external-dns documentation](https://github.com/kubernetes-sigs/external-dns)

---

### 🔐 `cert-manager`

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

You can also issue certs automatically via Ingress annotations (see `ingress-nginx` section).

📄 [cert-manager documentation](https://cert-manager.io)

---

### 📡 `metallb`

Enables `LoadBalancer` service types by assigning public IPs.

> ⚠️ The public IP pool is limited.  
Prefer using `Ingress` unless you specifically need a `LoadBalancer`.  
📄 [metallb documentation](https://metallb.universe.tf)

---

### 🌍 `ingress-nginx`

Default Ingress controller with class `nginx`.  
Supports automatic TLS via cert-manager annotations.

#### Example\
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

📄 [NGINX Ingress Docs](https://docs.nginx.com/nginx-ingress-controller)  
📄 [cert-manager Ingress Usage](https://cert-manager.io/docs/usage/ingress/)

---

### 🔑 `external-secrets`

Integrates with secret management tools like **HashiCorp Vault**.

📄 [external-secrets documentation](https://external-secrets.io/)

---

### 🔁 `kured`

Responsible for automatic node reboots (e.g., after kernel updates).

📄 [kured documentation](https://kured.dev/)

---

### 📊 Observability

Includes:

- **ECK Operator**  
- **Beats agents** – Export logs and metrics to CSCS’s central log system
- **Prometheus** – Scrapes metrics and exports them to CSCS's central monitoring cluster
