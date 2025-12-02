[](){#ref-communication-libfabric}
# Libfabric

[Libfabric](https://ofiwg.github.io/libfabric/), or Open Fabrics Interfaces (OFI), is a low-level networking library that provides an abstract interface for networks.
Libfabric has backends for different network types, and is the interface chosen by HPE for the [Slingshot network on Alps][ref-alps-hsn], and by AWS for their [EFA network interface](https://aws.amazon.com/hpc/efa/).

To fully take advantage of the network on Alps:

* libfabric and its dependencies must be available in your environment (uenv or container);
* and, communication libraries like Cray MPICH, OpenMPI, NCCL, and RCCL have to be built or configured to use libfabric.

??? question "What about UCX?"
    [Unified Communication X (UCX)](https://openucx.org/) is a low level library that targets the same layer as libfabric.
    Specifically, it provides an open, standards-based, networking API.

    By targeting UCX and libfabric, MPI and NCCL do not need to implement low-level support for each network hardware.

    A downside of having two standards instead of one, is that pre-built software (for example Conda packages and Containers) have versions of MPI built for UCX, which does not provide a back end for Slingshot 11.
    Trying to run these images will lead to errors, or very poor performance.

## Using libfabric

### uenv

If you are using a uenv provided by CSCS, such as [prgenv-gnu][ref-uenv-prgenv-gnu], [Cray MPICH][ref-communication-cray-mpich] is linked to libfabric and the high speed network will be used.
No changes are required in applications.

### Container Engine

If you are using [containers][ref-container-engine], the simplest approach is to load libfabric into your container using the [CXI hook provided by the container engine][ref-ce-cxi-hook].

Alternatively, it is possible to build libfabric and its dependencies into your container.

!!! example "Installing libfabric in a container for NVIDIA nodes"
    The following lines demonstrate how to configure and install libfabric in a Dockerfile.

    Note that it is assumed that CUDA has already been installed on the system.
    ```Dockerfile
    --8<-- "docs/software/communication/dockerfiles/libfabric"
    ```

??? note "The full Containerfile for GH200"

    The Containerfile below is based on the NVIDIA CUDA image, which provides a complete CUDA installation.

    - Communication frameworks are built with explicit support for CUDA and GDRCopy.

    Some additional features are enabled to increase the portability of the container to non-Alps systems:

    - The libfabric [EFA](https://aws.amazon.com/hpc/efa/) provider is configured using the `--enable-efa` compatibility for derived images on AWS infrastructure.
    - this image also packages the UCX communication framework to allow building a broader set of software (e.g. some OpenSHMEM implementations) and supporting optimized Infiniband communication as well.

    ```
    --8<-- "docs/software/communication/dockerfiles/base"
    --8<-- "docs/software/communication/dockerfiles/libfabric"
    --8<-- "docs/software/communication/dockerfiles/ucx"
    ```

## Tuning libfabric

Tuning libfabric (particularly together with [Cray MPICH][ref-communication-cray-mpich], [OpenMPI][ref-communication-openmpi], [NCCL][ref-communication-nccl], and [RCCL][ref-communication-rccl]) depends on many factors, including the application, workload, and system.
For a comprehensive overview libfabric options for the CXI provider (the provider for the Slingshot network), see the [`fi_cxi` man pages](https://ofiwg.github.io/libfabric/v2.1.0/man/fi_cxi.7.html).
Note that the exact version deployed on Alps may differ, and not all options may be applicable on Alps.

See the [Cray MPICH known issues page][ref-communication-cray-mpich-known-issues] for issues when using Cray MPICH together with libfabric.

!!! todo
    - add environment variable tuning guide
