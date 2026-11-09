# Bristen

Bristen is an Alps cluster that provides GPU accelerators and filesystems designed to meet the needs of machine learning workloads in the MLP. It is classified as a test and development system, provided on a best effort basis for benchmarking and testing a100 nodes, data preparation and similar tasks that require x86 nodes. It is *not* a cluster where to do the bulk of your computation, nodes can be removed from it for higher priority tasks. Clariden is where production runs should take place.

## Cluster Specification

### Compute Nodes

Bristen consists of NVIDIA A100 nodes. The number of nodes can change when nodes are added or removed from other clusters on Alps.

| Node type | Memory | Nodes | CPU sockets | GPUs |
| --- | --- | --- | --- | --- |
| zen2 | 512 GB | 2 | 4 | none |
| a100 | 512 GB | 30 | 30 | 120 |

Nodes are in the `normal` Slurm partition.

### Storage and file systems

Bristen uses the MLP filesystems and storage policies.

## Getting started

### Logging into Bristen

To connect to Bristen via SSH, first refer to the ssh guide.

> [!NOTE]
>
> **`~/.ssh/config`**
>
> Add the following to your SSH configuration to enable you to directly connect to bristen using `ssh bristen`.
>
> ```text
> Host bristen
>     HostName bristen.alps.cscs.ch
>     ProxyJump ela
>     User cscsusername
>     IdentityFile ~/.ssh/cscs-key
>     IdentitiesOnly yes
> ```

### Software

Users are encouraged to use containers on Bristen.

- Jobs using containers can be easily set up and submitted using the container engine.
- To build images, see the guide to building container images on Alps.

## Running Jobs on Bristen

### Slurm

Bristen uses Slurm as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

There is currently a single Slurm partition on the system:

- the `normal` partition is for all production workloads.

  - nodes in this partition are not shared.

| name | nodes | max nodes per job | time limit |
| --- | --- | --- | --- |
| `normal` | 32 | \- | 24 hours |

### FirecREST

Bristen can also be accessed using FirecREST at the `https://api.cscs.ch/ml/firecrest/v2` API endpoint.

### Scheduled Maintenance

A monthly maintenance on a Wednesday morning 8-12 CET is is typically performed when clariden monthly maintenance takes place, but being a test cluster other update might happen with short notice.

Exceptional and non-disruptive updates may happen outside this time frame and will be announced on the [CSCS status page](<https://status.cscs.ch>).

### Change log

> [!NOTE]
>
> **2026-08-26**
>
> > **New file system**
> >
> > - The Lustre file system `/iopsstor/datacache/cscs` is now mounted on the compute nodes.
> > - The Ritom VAST file system `/ritom/scratch` is now mounted on the compute nodes.

**2025-03-05 container engine updated**

now supports better containers that go faster. Users do not to change their workflow to take advantage of these updates.

### Known issues
