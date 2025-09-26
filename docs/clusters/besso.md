[](){#ref-cluster-besso}
# Besso

Besso is an Alps cluster that provides development resources for porting software for selected customers.

!!! note
    Besso is a small system for development work for selected customers.

### Storage and file systems

Besso uses the [HPCP filesystems and storage policies][ref-hpcp-storage].

## Getting started

### Logging into Besso

To connect to Besso via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to besso using `ssh besso`.
    ```
    Host besso
        HostName besso.vc.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

[](){#ref-cluster-besso-uenv}
#### uenv

Besso is a development and testing system, for which CSCS does not provide supported applications.

Instead, the [prgenv-gnu][ref-uenv-prgenv-gnu] programming environment is provided for the both the [a100][ref-alps-a100-node] and [mi200][ref-alps-mi200-node] node types.

[](){#ref-cluster-besso-containers}
#### Containers

Besso supports container workloads using the [Container Engine][ref-container-engine].

To build images, see the [guide to building container images on Alps][ref-build-containers].

#### Cray Modules

!!! warning
    The Cray Programming Environment (CPE), loaded using `module load cray`, is no longer supported by CSCS.

    CSCS will continue to support and update uenv and the Container Engine, and users are encouraged to update their workflows to use these methods at the first opportunity.

    The CPE is still installed on Besso, however it will receive no support or updates, and will be [replaced with a container][ref-cpe] in a future update.

## Running jobs on Besso

### Slurm

Besso uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor workloads on compute nodes.

There are multiple [Slurm partitions][ref-slurm-partitions] on the system:

* the `a100` partition contains [NVIDIA A100 GPU][ref-alps-a100-node] nodes
* the `mi200` partition contains [AMD Mi250x GPU][ref-alps-mi200-node] nodes
* the `normal` partition contains all of the nodes in the system.

| name | max nodes per job | time limit |
| --   |  -- | -- |
| `a100`   | 2    | 24 hours |
| `mi200`  | 2    | 24 hours |
| `normal` | 4    | 24 hours |

See the Slurm documentation for instructions on how to [run jobs][ref-slurm].

### FirecREST

!!! todo
    add the correct API endpoint

Besso can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/hpc/firecrest/v2` API endpoint.

## Maintenance and status

There is no regular scheduled maintenance for this system.
