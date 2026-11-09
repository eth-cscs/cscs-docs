# HPC Platform

The HPC Platform (HPCP) provides compute, storage, and related services for the HPC community in Switzerland and abroad. The majority of compute cycles are provided to the [User Lab](<https://www.cscs.ch/user-lab/overview>) via peer-reviewed allocation schemes.

## Getting Started

- **Policies**

  New users are invited to read carefully the CSCS User Policies.

### Getting access

Principal Investigators (PIs) and Deputy PIs can invite users to join their projects using the project management tool.

Once invited to a project you will receive an email with information on how to create an account and configure multi-factor authentication (MFA).

## Systems

- **Daint**

  Daint is a large Grace-Hopper cluster for GPU-enabled workloads.

- **Eiger**

  Eiger is an AMD Epyc cluster for CPU-only workloads.

## File systems and storage

The file systems provided on the HPCP clusters Daint and Eiger, the environment variables that point to them, and the Alps storage system that hosts each one:

| Variable | File system | Path | Storage | Type |
| --- | --- | --- | --- | --- |
| `$HOME` | Home | `/users/$USER` | Vadret | VAST |
| `$SCRATCH` | Scratch | `/ritom/scratch/cscs/$USER` | Ritom | VAST |
| `$SCRATCH_OLD` | Scratch (previous location) | `/capstor/scratch/cscs/$USER` | Capstor | Lustre |
| `$STORE`, `$PROJECT` | Store | `/capstor/store/cscs/<customer>/<group_id>` | Capstor | Lustre |

### Home

Every user has a home path (`$HOME`) mounted at `/users/$USER` on the Vadret file system. Home directories have 50 GB of capacity and are intended for keeping configuration files, small software packages, and scripts.

### Scratch

The Scratch file system is a large, temporary storage system designed for high-performance I/O. It is not backed up.

See the Scratch documentation for more information.

The environment variable `$SCRATCH` points to `/ritom/scratch/cscs/$USER`, and can be used as a shortcut to access your scratch folder. Ritom is using the VAST Data filesystem accessed over NFS. Since this is not a native parallel filesystem it requires some tuning for applications using parallel IO. See the VAST tuning guide for Ritom.

> [!WARNING]
>
> **scratch cleanup policy**
>
> Files that have not been accessed in **30 days** are automatically deleted.
>
> **Scratch is not intended for permanent storage**: transfer files back to the Store after batch job completion.

### Store

The Store (or Project) file system is provided as a space to store datasets, code, or configuration scripts that can be accessed from different clusters. The file system is backed up and there is no automated deletion policy.

The environment variable `$STORE` can be used as a shortcut to access the Store folder of your primary project.

Hard limits on the amount of data and number of files (inodes) will prevent you from writing to Store if your quotas are exceeded. You can check how much data and inodes you are consuming—and their respective quotas—by running the `quota` command on a login node.

> [!WARNING]
>
> It is not recommended to write directly to the `$STORE` path from batch jobs.
