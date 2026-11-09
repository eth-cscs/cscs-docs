# Climate and Weather Platform

The Climate and Weather Platform (CWP) provides compute, storage, and related services for the climate and weather modeling community in Switzerland.

## Getting Started

- **Policies**

  New users are invited to read carefully the CSCS User Policies.

### Getting access

Principal Investigators (PIs) and Deputy PIs can invite users to join their projects using the project management tool.

Once invited to a project you will receive an email with information on how to create an account and configure multi-factor authentication (MFA).

## Systems

- **Santis**

  Santis is a large Grace-Hopper cluster for GPU-enabled climate and weather workloads.

## File systems and storage

The file systems provided on the CWP cluster Santis, the environment variables that point to them, and the Alps storage system that hosts each one:

| Variable | File system | Path | Storage | Type |
| --- | --- | --- | --- | --- |
| `$HOME` | Home | `/users/$USER` | Vadret | VAST |
| `$SCRATCH` | Scratch | `/capstor/scratch/cscs/$USER` | Capstor | Lustre |
| `$STORE`, `$PROJECT` | Store | `/capstor/store/cscs/<customer>/<group_id>` | Capstor | Lustre |

### Home

Every user has a home path (`$HOME`) mounted at `/users/$USER` on the Vadret file system. Home directories have 50 GB of capacity and are intended for keeping configuration files, small software packages, and scripts.

### Scratch

The Scratch file system is a large, temporary storage system designed for high-performance I/O. It is not backed up.

See the Scratch documentation for more information.

The environment variable `$SCRATCH` points to `/capstor/scratch/cscs/$USER`, and can be used as a shortcut to access your scratch folder.

> [!WARNING]
>
> **scratch cleanup policy**
>
> Files that have not been accessed in **30 days** are automatically deleted.
>
> **Scratch is not intended for permanent storage**: transfer files back to the Store after batch job completion.

### Store

The Store (or Project) file system is provided as a space to store datasets, code, or configuration scripts that can be accessed from different clusters. The file system is backed up and there is no automated deletion policy.

The environment variable `$PROJECT` can be used as a shortcut to access the Store folder of your primary project.

Hard limits on the amount of data and number of files (inodes) will prevent you from writing to Store if your quotas are exceeded.

> [!WARNING]
>
> It is not recommended to write directly to the `$PROJECT` path from batch jobs.

### Checking quota

You can check how much capacity and how many files (inodes) you are consuming, and the corresponding quotas, by running the `quota` command on a login node.

The `quota` command prints a table with one row per file system path that you have access to. The most important columns are:

- `Directory`: the file system path (for example your `$HOME`, `$SCRATCH`, and each `$PROJECT` Store path you are a member of).
- `Used`: the amount currently used (capacity or number of files).
- `%`: the percentage of the quota used.
- `Grace`: the remaining grace period once a soft quota has been exceeded.
- `Limit`: the quota limit (capacity or maximum number of files).

The same set of columns is reported twice for each path: once for the capacity *quota* and once for the *files* (inode) quota.

> [!NOTE]
>
> **path names in the quota output**
>
> The paths shown by `quota` are taken from the internal storage service, not from the vCluster where the command is executed. This means the directory names may differ from the mount points you see on Santis. For example, `$HOME` is reported as `/vast/users/cscs/$USER` instead of `/users/$USER`.

See the quota documentation for a detailed example and a description of the different quota types.
