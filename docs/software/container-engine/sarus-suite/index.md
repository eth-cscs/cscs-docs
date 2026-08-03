# Sarus Suite & Podman on Alps — Early Access

This section provides starting documentation for using [Sarus Suite](https://github.com/sarus-suite) on Alps. Sarus Suite is a collection of components that enable the use of [Podman](https://podman.io/) for running containers at scale in HPC workloads.

Sarus Suite and Podman are planned to become the core machinery behind the next generation of the [Container Engine (CE)][ref-container-engine] service. The tools described here are **currently intended for early access testing and evaluation only**, with the goal of collecting feedback to guide further development and eventual production rollout.

Familiarity with the current [Container Engine (CE)][ref-container-engine] toolset is assumed.

!!! under-construction

    Sarus Suite is under active development and will be continuously updated over the coming months as progress is made towards supporting more features and production readiness.

    Accordingly, the contents of this page are not final and should be expected to change.

## Similarities with the current Container Engine

One of the main goals of the transition from **Enroot & Pyxis** to **Sarus Suite & Podman** is to minimize changes to the end-user experience.

Sarus Suite:

*   supports the **EDF format** and the **EDF search path rules** already implemented in the current Container Engine;
*   integrates with **Slurm** in a similar way to launch containerized jobs on compute nodes.

!!! Danger "Current differences and limitations"

    * Due to the way Podman's image storage works, with Sarus Suite it's no longer possible to use direct filesystem paths to define images in EDFs. Images must be entered in the form of registry references.
    * [HPC features][ref-sarus-suite-hpc-features] are enabled primarily through [CDI specs](https://github.com/cncf-tags/container-device-interface) and the [device array][ref-sarus-suite-edf-device-array], not annotations. Work is ongoing to enable the CE vService to handle configuration of OCI hooks for Podman and align them with annotations.
    * CXI libfabric replacement is not enabled by default.
    * The CXI CDI relies on an old Sarus 1.7.0 hook for libfabric replacement. When activated, the hook requires a libfabric to be present inside the container. Enabling the CXI CDI with a container that does not have libfabric results in an error.
    * CXI and AWS OFI NCCL CDI specs cannot handle replacement of multiple libfabric or plugin libraries inside containers. This complicates the effective use of images with multiple NCCL plugins already installed, like NGC images. Work in preparing OCI hooks to handle these cases is ongoing. In the meantime, customized CDI specs are a possible workaround.
    * Mount destinations in EDFs must be explicit (e.g. `mounts=["${SCRATCH}"]` will result in an error).
    * SquashFS mounts from EDFs are not supported yet.
    * PMIx propagation is achieved by bind-mounting `/tmp` into containers, until a hook for proper PMIx support is rolled out.
    * No support yet for netstack artifacts, CUDA MPS, or direct SSH into containers.
    * Error propagation and reporting still need improvements.


## Quickstart with Alps Extended Images

[Alps Extended Images][ref-software-extended-images] offer a convenient way of starting to experiment with Sarus Suite, due to their self-sufficient nature that does not require modifications from hooks or device definitions.

Consider an EDF like the following:

```toml
image = "jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.02-py3-alps6"

mounts = ["${SCRATCH}:${SCRATCH}"]

[env]
PMIX_MCA_psec = "native"
```

The key user-visible difference of using Sarus Suite from the production Container Engine is the use of the `--edf` option in Slurm commands instead of `--environment`.

For example, using the EDF presented above, the NCCL Tests all-reduce bandwidth benchmark can be run as follows:

```console
$ srun -N2 --gpus-per-node=4 --mpi=pmix --edf=aei-alps6 --network=disable_rdzv_get all_reduce_perf -b 1M -e 128M -f2
# nccl-tests version 2.18.2 nccl-headers=23007 nccl-library=23007
# Collective test starting: all_reduce_perf
# nThread 1 nGpus 1 minBytes 1048576 maxBytes 134217728 step: 2(factor) warmup iters: 1 iters: 20 agg iters: 1 validation: 1 graph: 0 unalign: 0
#
# Using devices
#  Rank  0 Group  0 Pid  15784 on  nid007106 device  0 [0009:01:00] NVIDIA GH200 120GB
#  Rank  1 Group  0 Pid  24926 on  nid007109 device  0 [0009:01:00] NVIDIA GH200 120GB
#
#                                                              out-of-place                       in-place          
#       size         count      type   redop    root     time   algbw   busbw  #wrong     time   algbw   busbw  #wrong 
#        (B)    (elements)                               (us)  (GB/s)  (GB/s)             (us)  (GB/s)  (GB/s)         
     1048576        262144     float     sum      -1   339.61    3.09    3.09       0   335.85    3.12    3.12       0
     2097152        524288     float     sum      -1   355.53    5.90    5.90       0   361.77    5.80    5.80       0
     4194304       1048576     float     sum      -1   476.28    8.81    8.81       0   471.14    8.90    8.90       0
     8388608       2097152     float     sum      -1   556.83   15.06   15.06       0   559.35   15.00   15.00       0
    16777216       4194304     float     sum      -1   840.36   19.96   19.96       0   841.25   19.94   19.94       0
    33554432       8388608     float     sum      -1  1537.62   21.82   21.82       0  1538.74   21.81   21.81       0
    67108864      16777216     float     sum      -1  2982.38   22.50   22.50       0  2983.25   22.50   22.50       0
   134217728      33554432     float     sum      -1  5871.07   22.86   22.86       0  5867.43   22.88   22.88       0
# Out of bounds values : 0 OK
# Avg bus bandwidth    : 14.9966 
#
# Collective test concluded: all_reduce_perf
#
```

## Further reading

More details about using Sarus Suite and its features on Alps are provided in the [Early Access User Guide][ref-sarus-suite-user-guide].