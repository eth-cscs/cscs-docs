# HPC Platform

The HPC Platform (HPCP) provides compute, storage, and related services for the HPC community in Switzerland and abroad. The majority of compute cycles are provided to the [User Lab](<https://www.cscs.ch/user-lab/overview>) via peer-reviewed allocation schemes.

## Getting Started

- [**Policies**](<https://docs.cscs.ch/policies/index.md#cscs-user-policies> "CSCS User Policies")

  New users are invited to read carefully the [CSCS User Policies](<https://docs.cscs.ch/policies/index.md#cscs-user-policies>).

### Getting access

Principal Investigators (PIs) and Deputy PIs can invite users to join their projects using the [project management tool](<https://docs.cscs.ch/accounts/waldur/index.md#the-project-and-resources-management-tool> "The Project and Resources Management Tool").

Once invited to a project you will receive an email with information on how to create an account and configure [multi-factor authentication](<https://docs.cscs.ch/access/mfa/index.md#multi-factor-authentication> "Multi Factor Authentication") (MFA).

## Systems

- [**Daint**](<https://docs.cscs.ch/clusters/daint/index.md#daint>)

  Daint is a large [Grace-Hopper](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") cluster for GPU-enabled workloads.

- [**Eiger**](<https://docs.cscs.ch/clusters/eiger/index.md#eiger>)

  Eiger is an [AMD Epyc](<https://docs.cscs.ch/alps/hardware/index.md#amd-rome-cpu-nodes> "AMD Rome CPU Nodes") cluster for CPU-only workloads.

## File systems and storage

The file systems provided on the HPCP clusters [Daint](<https://docs.cscs.ch/clusters/daint/index.md#daint>) and [Eiger](<https://docs.cscs.ch/clusters/eiger/index.md#eiger>), the environment variables that point to them, and the [Alps storage system](<https://docs.cscs.ch/alps/storage/index.md#alps-storage> "Alps Storage") that hosts each one:

| Variable | File system | Path | Storage | Type |
| --- | --- | --- | --- | --- |
| `$HOME` | [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>) | `/users/$USER` | [Vadret](<https://docs.cscs.ch/alps/storage/index.md#vadret>) | VAST |
| `$SCRATCH` | [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) | `/ritom/scratch/cscs/$USER` | [Ritom](<https://docs.cscs.ch/alps/storage/index.md#ritom>) | [VAST](<https://docs.cscs.ch/guides/storage/index.md#vast-tuning-on-ritom> "VAST tuning on Ritom") |
| `$SCRATCH_OLD` | [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) (previous location) | `/capstor/scratch/cscs/$USER` | [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) | [Lustre](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") |
| `$STORE`, `$PROJECT` | [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) | `/capstor/store/cscs/<customer>/<group_id>` | [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) | [Lustre](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") |

### Home

Every user has a [home](<https://docs.cscs.ch/storage/filesystems/index.md#home> "Home") path (`$HOME`) mounted at `/users/$USER` on the [Vadret](<https://docs.cscs.ch/alps/storage/index.md#vadret>) file system. Home directories have 50 GB of capacity and are intended for keeping configuration files, small software packages, and scripts.

### Scratch

The Scratch file system is a large, temporary storage system designed for high-performance I/O. It is not backed up.

See the [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) documentation for more information.

The environment variable `$SCRATCH` points to `/ritom/scratch/cscs/$USER`, and can be used as a shortcut to access your scratch folder. [Ritom](<https://docs.cscs.ch/alps/storage/index.md#ritom>) is using the VAST Data filesystem accessed over NFS. Since this is not a native parallel filesystem it requires some tuning for applications using parallel IO. See the [VAST tuning guide for Ritom](<https://docs.cscs.ch/guides/storage/index.md#vast-tuning-on-ritom> "VAST tuning on Ritom").

> [!WARNING]
>
> **scratch cleanup policy**
>
> Files that have not been accessed in **30 days** are automatically deleted.
>
> **Scratch is not intended for permanent storage**: transfer files back to the [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) after batch job completion.

### Store

The Store (or Project) file system is provided as a space to store datasets, code, or configuration scripts that can be accessed from different clusters. The file system is backed up and there is no automated deletion policy.

The environment variable `$STORE` can be used as a shortcut to access the Store folder of your primary project.

Hard limits on the amount of data and number of files (inodes) will prevent you from writing to [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) if your quotas are exceeded. You can check how much data and inodes you are consuming—and their respective quotas—by running the [`quota`](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota") command on a login node.

> [!WARNING]
>
> It is not recommended to write directly to the `$STORE` path from batch jobs.
