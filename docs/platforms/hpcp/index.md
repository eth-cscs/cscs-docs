[](){#ref-platform-hpcp}
# HPC Platform

The HPC Platform (HPCP) provides compute, storage, and related services for the HPC community in Switzerland and abroad. The majority of compute cycles are provided to the [User Lab](https://www.cscs.ch/user-lab/overview) via peer-reviewed allocation schemes.  

## Getting Started

<div class="grid cards" markdown>
-   :fontawesome-solid-mountain: [__Policies__][ref-policies]

    New users are invited to read carefully the [CSCS User Policies][ref-policies].
</div>

### Getting access

Principal Investigators (PIs) and Deputy PIs can invite users to join their projects using the [account and resource management tool][ref-account-ump].

Once invited to a project you will receive an email with information on how to create an account and configure [multi-factor authentication][ref-mfa] (MFA).

## Systems

<div class="grid cards" markdown>
-   :fontawesome-solid-mountain: [__Daint__][ref-cluster-daint]

    Daint is a large [Grace-Hopper][ref-alps-gh200-node] cluster for GPU-enabled workloads.
</div>

<div class="grid cards" markdown>
-   :fontawesome-solid-mountain: [__Eiger__][ref-cluster-eiger]

    Eiger is an [AMD Epyc][ref-alps-zen2-node] cluster for CPU-only workloads.
</div>

[](){#ref-hpcp-storage}
## File systems and storage

There are three main file systems mounted on the HPCP clusters.

| type |mount | file system |
| -- | -- | -- |
| [Home][ref-storage-home]       | /users/$USER | [VAST][ref-alps-vast] |
| [Scratch][ref-storage-scratch] | `/capstor/scratch/cscs/$USER` | [Capstor][ref-alps-capstor] |
| [Store][ref-storage-store]     | `/capstor/store/cscs/<customer>/<project>` | [Capstor][ref-alps-capstor] |

### Home

Every user has a [home][ref-storage-home] path (`$HOME`) mounted at `/users/$USER` on the [VAST][ref-alps-vast] file system.
Home directories have 50 GB of capacity and are intended for keeping configuration files, small software packages, and scripts.

### Scratch

The Scratch file system is a large, temporary storage system designed for high-performance I/O. It is not backed up. 

See the [Scratch][ref-storage-scratch] documentation for more information.

The environment variable `$SCRATCH` points to `/capstor/scratch/cscs/$USER`, and can be used as a shortcut to access your scratch folder.

!!! warning "scratch cleanup policy"
    Files that have not been accessed in 30 days are automatically deleted.

    **Scratch is not intended for permanent storage**: transfer files back to the [Store][ref-storage-store] after batch job completion.

### Store

The Store (or Project) file system is provided as a space to store datasets, code, or configuration scripts that can be accessed from different clusters. The file system is backed up and there is no automated deletion policy.

The environment variable `$STORE` can be used as a shortcut to access the Store folder of your primary project.

Hard limits on the amount of data and number of files (inodes) will prevent you from writing to [Store][ref-storage-store] if your quotas are exceeded.
You can check how much data and inodes you are consuming -- and their respective quotas -- by running the [`quota`][ref-storage-quota] command on a login node.

!!! warning
    It is not recommended to write directly to the `$STORE` path from batch jobs. 

