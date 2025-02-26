[](){#ref-cluster-clariden}
# Clariden

!!! todo
    Introduction

    This page is a cut and paste of some of Todi's old documentation, which we can turn into a template.

## Cluster Specification
### Hardware
Clariden consists of ~1200 [Grace-Hopper nodes][ref-alps-gh200-node]. Most nodes are in the [`normal` slurm partition][ref-slurm-partition-normal], while a few nodes are in the [`debug` partition][ref-slurm-partition-debug].
The nodes are interconnected with the [slingshot high speed network][ref-alps-slingshot-network].

As usual the login nodes have direct internet connections, while the compute nodes use a [proxy server][ref-alps-slingshot-network] to access the internet.
!!! todo
    Document proxy and the implications (normally transparent, but git needs modifications
    Fix the ref

### File systems and storage
The scratch filesystem is hosted on [IOPStore][ref-storage-iopstor], but also the capacity storage [Capstor][ref-storage-capstor] is mounted at `/capstor/scratch/cscs`.
The variables `STORE` and `PROJECT` are not set on Clariden.
The home directory is hosted on [VAST][ref-storage-vast].

As usual, an overview of your quota on the different filesystems, can be obtained by the `quota` command.

## Getting started
The project and resources are managed by [this tool][ref-account-waldur].

### Connect to Clariden
You can connect to Clariden via [ssh][ref-ssh-config], ensuring that the file `~/.ssh/config` has these settings (replace `cscsusername` with your username).

```title="$HOME/.ssh/config"
Host ela
    HostName ela.cscs.ch
    User cscsusername
    IdentityFile ~/.ssh/cscs-key

Host clariden
    HostName clariden.alps.cscs.ch
    ProxyJump ela
    User cscsusername
    IdentityFile ~/.ssh/cscs-key
    IdentitiesOnly yes
```
You can then use `ssh clariden` to login to Clariden.

### Available programming environments

#### Container engine
The recommended way for working on Clariden are containerized workflows leveraging the [container engine][ref-container-engine].

#### UENV
Besides running containerized workflows, it is possible to run your jobs with a [UENV][ref-tool-uenv].

#### CPE
Unlike on other platforms the Cray programming environment is not supported on Clariden.

### Running Jobs on Clariden

Clariden uses [SLURM][slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

See detailed instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

The flag `--account=<account>` / `-A <account>` is mandatory for submitting jobs to SLURM, and nodehour accounting will be on the account that is specified with this flag.

## Maintenance
### Calendar and key events

- The system is updated every Wednesday, between 08:00-12:00 Zurich local time.
- Access to the system might be closed during the maintenance window.
- There is a maintenance reservation for SLURM, which prohibits jobs to start, if their `StartTime+TimeLimit` is beyond the maintenance start.

!!!todo
    notifications
    
    a calendar widget would be useful, particularly if we can have a central calendar, and a way to filter events for specific instances

### Change log

!!! change "special text boxes for updates"
    they can be opened and closed.

!!! change "2024-10-15 reservation `daint` available again"
    The reservation daint  is available again exclusively for Daint users that need to run their benchmarks for submitting their proposals, additionally to the debug  partition and free nodes.
    Please add the Slurm option --reservation=daint to your batch script if you want to use it

??? change "2024-10-07 New compute node image deployed"
    New compute node image deployed to fix the issue with GPU-aware MPI.

    Max job time limit is decreased from 12 hours to 6 hours

??? change "2024-09-18 Daint users"
    In order to complete the preparatory work necessary to deliver Alps in production, as of September 18 2024 the vCluster Daint on Alps will no longer be accessible until further notice: the early access will still be granted on Tödi using the Slurm reservation option `--reservation=daint`

### Known issues

__TODO__ list of know issues - include links to known issues page

[CSCS Service Desk]: https://jira.cscs.ch/plugins/servlet/desk
