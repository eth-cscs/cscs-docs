# Eiger

Eiger is an Alps cluster that provides compute nodes and file systems designed to meet the needs of CPU-only workloads for the HPC Platform.

## Cluster specification

### Compute nodes

Eiger consists of multicore AMD Epyc Rome compute nodes: please note that the total number of available compute nodes on the system might vary over time. See the Slurm documentation for information on how to check the number of nodes.

Additionally, there are four login nodes with host names `eiger-ln00[1-4]`.

| Node type | Memory | Nodes | CPU sockets | GPUs |
| --- | --- | --- | --- | --- |
| zen2 | 256 GB | 240 | 480 | none |
| zen2 | 512 GB | 286 | 572 | none |

In addition, two zen2 nodes are reserved for data transfer in the `xfer` partition, and cannot run compute jobs.

### Storage and file systems

Eiger uses the HPCP filesystems and storage policies.

## Getting started

### Logging into Eiger

To connect to Eiger via SSH, first refer to the ssh guide.

> [!NOTE]
>
> **`~/.ssh/config`**
>
> Add the following to your SSH configuration to enable you to directly connect to eiger using `ssh eiger.alps`.
>
> ```text
> Host eiger.alps
>     HostName eiger.alps.cscs.ch
>     ProxyJump ela
>     User cscsusername
>     IdentityFile ~/.ssh/cscs-key
>     IdentitiesOnly yes
> ```

### Software

#### uenv

CSCS and the user community provide uenv software environments on Eiger.

- **Scientific Applications**

  Provide the latest versions of scientific applications, tuned for Eiger, and the tools required to build your own version of the applications.

  - CP2K
  - GROMACS
  - LAMMPS
  - NAMD
  - Quantumespresso
  - VASP

- **Programming Environments**

  Provide compilers, MPI, Python, common libraries and tools used to build your own applications.

  - prgenv-gnu
  - linalg
  - julia

- **Tools**

  Provide tools like

  - Linaro Forge

#### User applications

For help with user applications, see the following guides:

- ORCA
- WRF

#### Containers

Eiger supports container workloads using the Container Engine.

To build images, see the guide to building container images on Alps.

The CPE has been uninstalled from Eiger, however it can still be accessed as a container.

## Running jobs on Eiger

### Slurm

Eiger uses Slurm as the workload manager, which is used to launch and monitor workloads on compute nodes.

There are multiple Slurm partitions on the system:

- the `debug` partition can be used to access a small allocation for up to 30 minutes for debugging and testing purposes
- the `prepost` partition is meant for small high priority allocations up to 30 minutes, for pre- and post-processing jobs.
- the `normal` partition is for all production workloads.
- the `xfer` partition is for internal data transfer.
- the `low` partition is a low-priority partition, which may be enabled for specific projects at specific times.

| Partition | Nodes | Max nodes/job | Default time | Max time |
| --- | --- | --- | --- | --- |
| `normal` (default) | 514 | 480 | 01:00:00 | 1-00:00:00 |
| `low` | 514 | 124 | 01:00:00 | 1-00:00:00 |
| `prepost` | 514 | 1 | 00:30:00 | 00:30:00 |
| `debug` | 12 | 10 | 00:30:00 | 00:30:00 |
| `xfer` | 2 | 1 | 06:00:00 | 1-00:00:00 |

The `normal`, `prepost` and `low` partitions draw on the same pool of nodes, so the node counts above overlap and do not sum to the size of the cluster.

- nodes in the `normal` and `debug` partitions are not shared
- jobs in `debug`: at most 1 running and 2 submitted per user
- nodes in the `xfer` partition can be shared

The hardware available in each partition, including the Slurm features that can be selected with `--constraint`:

| Partition | Nodes | Node type | Features |
| --- | --- | --- | --- |
| `normal` | 274 | zen2 512 GB | none |
| `normal` | 240 | zen2 256 GB | none |
| `low` | 274 | zen2 512 GB | none |
| `low` | 240 | zen2 256 GB | none |
| `prepost` | 274 | zen2 512 GB | none |
| `prepost` | 240 | zen2 256 GB | none |
| `debug` | 12 | zen2 512 GB | none |
| `xfer` | 2 | zen2 256 GB | none |

> [!NOTE]
>
> **Default MPI plugin**
>
> The default MPI plugin on Eiger is `cray_shasta`. This plugin is correct for applications that use Cray MPICH, for example applications in uenv and the CPE. Applications that use OpenMPI or MPICH must set `--mpi=pmix` or `--mpi=pmi2`.

See the Slurm documentation for instructions on how to run jobs on the AMD CPU nodes.

### JupyterHub

A JupyterHub service for Eiger is available at [https://jupyter-eiger.cscs.ch](<https://jupyter-eiger.cscs.ch>).

### FirecREST

Eiger can also be accessed using FirecREST at the `https://api.cscs.ch/hpc/firecrest/v2` API endpoint.

> [!WARNING]
>
> **The FirecREST v1 API is still available, but deprecated**

## Maintenance and status

### Scheduled maintenance

One Wednesday per month is reserved for planned maintenance (usually around the middle of the month). If the batch queues must be drained (for redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window.

Exceptional and non-disruptive updates may happen outside this time frame and will be announced via the [CSCS status page](<https://status.cscs.ch>) and the [\#eiger channel](<https://cscs-users.slack.com/archives/C08FBP55CG1>) of the CSCS User Slack.

### Change log

> [!NOTE]
>
> **2026-09-16**
>
> > **New $SCRATCH directory**
> >
> > - `$SCRATCH` now points to `/ritom/scratch/cscs/<username>`
> > - `$SCRATCH_OLD` points to `/capstor/scratch/cscs/<username>`
> > - `$SCRATCH_NEW` is unchanged and points to `/ritom/scratch/cscs/<username>`
>
> > **Slurm updated to 25.05.9**
> >
> > - Slurm was updated from 25.05.8 to 25.05.9
>
> > **Uenv updated to 10.1.0**
> >
> > - `uenv` has been updated from 10.0.1 to 10.1.0
> > - This fixes an issue downloading images that need a token authentication
>
> > **Slurm batch policies plugin**
> >
> > - Fixes a bug with library dependencies

**2026-08-26**

> [!NOTE]
>
> **Major system upgrade**
>
> `Eiger` received a major system upgrade; note in particular the following changes:
>
> - Updated operating system from SLES-15.5 to SLES-15.6
> - Updated HPE Cray Supercomputing User Services Software (USS) from 1.1.0 to version 1.4.0
> - Updated Slingshot Host Software (SHS) from version 11.1.0 to version 13.1.0.
> - Updated Slurm from version 24.05 to 25.05.

> [!NOTE]
>
> **Removal of cray modules**
>
> The cray modules have been removed from `eiger`. As a replacement, we recommend to use uenv.

> [!NOTE]
>
> **Login node limits**
>
> To enforce our fair usage of shared resources policies, we have enabled limits on the login nodes. Please note that some limits apply to individual processes, while other limits apply to the sum of your running processes. Agentic tools and VSCode might be affected by these limits. Compute intensive tasks will also be affected by the limits. Any compute intensive task that is beyond the limits should be submitted to a compute node.

> [!NOTE]
>
> **Enforce performance cpufreq governor**
>
> Due to a bug the cpu frequency governor has not always been set to `performance`. This bug has been fixed and the frequency governor will always be set to `performance` (instead of the default `ondemand`)

> [!NOTE]
>
> **/capstor/archive**
>
> The filesystem `/capstor/archive` is only mounted on the nodes of the `xfer` partition. The mount was removed from the login nodes.

> [!NOTE]
>
> **uenv default repository**
>
> Using `uenv` with a repository stored on `capstor` will issue a migration warning. It is safe to follow the migration guide, and move your repository to `ritom`. Please take note of potential access permission problems and the fix, as described in the migration guide.

**2026-06-17**

> [!NOTE]
>
> **Uenv**
>
> - Upgraded Uenv from version 9.2.0 to 10.0.1.
> - Features:
>
>   - TOML configuration format and improved repository management: multiple named repositories can be configured and selected by name.
>   - Default views: Uenv images can declare a view to load automatically when no `--view` flag is given.
>   - Advanced Slurm workflows: the `--uenv-passthrough` flag controls whether a loaded uenv is forwarded to nested srun, sbatch, or salloc calls.
>   - New global `--system` flag to override the cluster name on the CLI (e.g., `uenv --system='*' image find`).
>   - Improved bash completion for uenv labels and file paths.
> - Fixes:
>
>   - Changed a hard error to a warning when image metadata is not attached in the registry.
>   - Fixed a latent bug parsing date strings in image metadata.
> - uenv changelog

> [!NOTE]
>
> **Container Engine**
>
> - Updated Container Engine to v26.06.1
> - Slingshot-related hooks now use Network Stack Artifacts (also called “netstacks”) as default resources for the components, libraries and dependencies mounted inside containers (e.g. libfabric, AWS OFI NCCL, Slingshot dependencies). Previously, the host stack was the default: see our docs
>
>   - To enable the previous behaviour, you should use `com.hooks.netstack.source = "host"`
> - Fixed an issue with importing images using multi-line LABEL, e.g., ubuntu-26.04 based images.

**2025-06-05 Early access phase**

Early access phase is open

**2025-05-23 Creation of Eiger on Alps**

Eiger is deployed as a vServices-enabled cluster

### Known issues
