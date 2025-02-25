[](){#ref-cluster-clariden}
# Clariden

!!! todo
    Introduction

    This page is a cut and paste of some of Todi's old documentation, which we can turn into a template.

## Cluster Specification
### Hardware
Clariden consists of ~1200 [Grace-Hopper nodes][ref-alps-gh200-node]. Most nodes are in the [`normal` slurm partition][ref-slurm-partition-normal], while a few nodes are in the [`debug` partition][ref-slurm-partition-debug].



!!! todo
    a standardised table with information about

    * number and type of nodes

    and any special notes

## Logging into Clariden

!!! todo
    how to log in, i.e. `ssh clariden.cscs.ch` via `ela.cscs.ch`

    provide the snippet to add to your `~/.ssh/config`, and link to where we document this (docs not currently available)

## Software and services

!!! todo
    information about CSCS services/tools available

    * container engine
    * uenv
    * CPE
    * ... etc

## Running Jobs on Clariden

Clariden uses [SLURM][slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

See detailed instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

## Storage

!!! todo
    describe the file systems that are attached, and where.

    This is where `$SCRATCH`, `$PROJECT` etc are defined for this cluster.

    Refer to the specific file systems that these map onto (capstor, iopstor, waldur), and link to the storage docs for these.

    Also discuss any specific storage policies. You might want to discuss storage policies for MLp one level up, in the [MLp docs][ref-platform-mlp].

* attached storage and policies

## Calendar and key events

The system is updated every Tuesday, between 9 am and 12 pm.
...

!!!todo
    notifications
    
    a calendar widget would be useful, particularly if we can have a central calendar, and a way to filter events for specific instances

## Change log

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

## Known issues

__TODO__ list of know issues - include links to known issues page

[CSCS Service Desk]: https://jira.cscs.ch/plugins/servlet/desk
