[](){#ref-cluster-beverin}
# Beverin

Beverin is an AMD-based GPU cluster for the purpose of testing and porting applications.

## Cluster Specification

### Login node

Beverin has one [MI250X][ref-alps-mi200-node] login node.

### Compute Nodes

Beverin consists of 13 [MI250X][ref-alps-mi200-node] and 128 [MI300A][ref-alps-mi300-node] compute nodes.

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|--------| ----------------- | ---------- |
| [mi200][ref-alps-mi200-node] | 13 | 13 | 104 |
| [mi300][ref-alps-mi300-node] | 128 | 512 | 512 |

### Storage and file systems

Beverin uses the [HPCP filesystems and storage policies][ref-hpcp-storage].

## Getting started

### Logging into Beverin

To connect to Beverin via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to Beverin using `ssh beverin`.
    ```
    Host beverin
        HostName beverin.vc.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

[](){#ref-cluster-beverin-uenv}

Beverin provides uenv to deliver programming environments and application software. Please refer to the [uenv documentation][ref-uenv] for detailed information on how to use the uenv tools on the system.

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Climate and Weather Applications__

    Provide software stacks for climate and weather workflows on Beverin.

     * [ICON][ref-software-icon]

</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Scientific Applications__

    Provide scientific applications.

     * [Quantumespresso][ref-uenv-quantumespresso]

</div>

<div class="grid cards" markdown>

-    :fontawesome-solid-layer-group: __Programming Environments__

    Provide compilers, MPI, Python, common libraries and tools used to build your own applications.

    * [prgenv-gnu][ref-uenv-prgenv-gnu]
    * [linalg][ref-uenv-linalg]
    
</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Tools__

    Provide tools like 

    * [Linaro Forge][ref-uenv-linaro]
</div>

[](){#ref-cluster-beverin-containers}
#### Containers

Beverin supports container workloads using the [Container Engine][ref-container-engine].

To build images, see the [guide to building container images on Alps][ref-build-containers].

## Running Jobs on Beverin

### Slurm

Beverin uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor distributed workloads.

There are two Slurm partitions on the system, corresponding to the two node types:

* `mi200` (default)
* `mi300`

| name | nodes  | max nodes per job | time limit |
| --   | --     | --                | -- |
| `mi200` | 13 | 13 | 24 hours |
| `mi300` | 128 | 128 | 24 hours |

### FirecREST

Beverin can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v2` API endpoint.
