[](){#ref-communication-libfabric}
# Libfabric

[Libfabric](https://ofiwg.github.io/libfabric/), or Open Fabrics Interfaces (OFI), is a low level networking library that abstracts away various networking backends.
It is used by Cray MPICH, and can be used together with OpenMPI, NCCL, and RCCL to make use of the [Slingshot network on Alps][ref-alps-hsn].

## Using libfabric

If you are using a uenv provided by CSCS, such as [prgenv-gnu][ref-uenv-prgenv-gnu], [Cray MPICH][ref-communication-cray-mpich] is linked to libfabric and the high speed network will be used.
No changes are required in applications.

If you are using containers, the system libfabric can be loaded into your container using the [CXI hook provided by the container engine][ref-ce-cxi-hook].
Using the hook is essential to make full use of the Alps network.

## Tuning libfabric

Tuning libfabric (particularly together with [Cray MPICH][ref-communication-cray-mpich], [OpenMPI][ref-communication-openmpi], [NCCL][ref-communication-nccl], and [RCCL][ref-communication-rccl]) depends on many factors, including the application, workload, and system.
For a comprehensive overview libfabric options for the CXI provider (the provider for the Slingshot network), see the [`fi_cxi` man pages](https://ofiwg.github.io/libfabric/v2.1.0/man/fi_cxi.7.html).
Note that the exact version deployed on Alps may differ, and not all options may be applicable on Alps.

See the [Cray MPICH known issues page][ref-communication-cray-mpich-known-issues] for issues when using Cray MPICH together with libfabric.

!!! todo
    More options?
