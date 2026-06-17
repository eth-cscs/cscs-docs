[](){#ref-kubernetes-clusters-upgrades}
# Kubernetes Cluster Upgrade Policy

To maintain a secure, stable, and supported platform, we regularly upgrade our Kubernetes clusters. We use **[RKE2](https://docs.rke2.io/)** as our Kubernetes distribution.

## Upgrade Flow

**Phased Rollout**

  - Upgrades are first applied to **TDS clusters** (Test and Development Systems).
  - After a **minimum of 2 weeks**, if no critical issues are observed, the same upgrade will be applied to **PROD clusters**.

**No Fixed Schedule**

  - Upgrades are not done on a strict calendar basis.
  - Timing may depend on compatibility with **other infrastructure components** (e.g., storage, CNI plugins, monitoring tools).
  - However, all clusters will be upgraded **before the current Kubernetes version reaches End of Life (EOL)**.

## Upgrade Impact

The **impact of a Kubernetes upgrade can vary**, depending on the nature of the changes involved:

**Minimal Impact**

  - For example, upgrades that affect only the `kubelet` may be **transparent to workloads**.
  - Rolling restarts may occur, but no downtime is expected for well-configured applications.

**Potentially Disruptive**

  - Upgrades involving components such as the **CNI (Container Network Interface)** may cause **temporary network interruptions**.
  - Other control plane or critical component updates might cause short-lived disruption to scheduling or connectivity.

??? Note "Applications that follow cloud-native best practices (e.g., readiness probes, multiple replicas, graceful shutdown handling) are **less likely to be impacted** by upgrades."

## What You Can Expect

- Upgrades are performed using safe, tested procedures with minimal risk to production workloads.
- TDS clusters serve as a **canary environment**, allowing us to identify issues early.
- All clusters are kept **aligned with supported Kubernetes versions**.

