# Communication Libraries

Communication libraries, like MPI and NCCL, are one of the building blocks for high performance scientific and ML workloads. Broadly speaking, there are two levels of communication:

- **Intra-node** communication between two processes on the same node.
- **Inter-node** communication between different nodes, over the [Slingshot 11 network](<https://docs.cscs.ch/alps/hardware/index.md#alps-high-speed-network> "Alps High Speed Network") that connects nodes on Alps.

To get the best inter-node performance on Alps, they need to be configured to use the [libfabric](<https://docs.cscs.ch/software/communication/libfabric/index.md#libfabric> "Libfabric") library that has an optimised back end for the Slingshot 11 network on Alps.

As such, communication libraries are part of the “base layer” of libraries and tools used by all workloads to fully utilize the hardware on Alps. They comprise the *network* layer in the following stack:

- **CPU**: compilers with support for building applications optimized for the CPU architecture on the node.
- **GPU**: CUDA and ROCM provide compilers and runtime libraries for NVIDIA and AMD GPUs respectively.
- **Network**: libfabric, MPI, NCCL, NVSHMEM, need to be configured for the Slingshot network.

CSCS provides communication libraries optimised for libfabric and Slingshot in uenv, and guidance on how to create container images that use them. This section of the documentation provides advice on how to build and install software to use these libraries, and how to deploy them.

For most scientific applications relying on MPI, [Cray MPICH](<https://docs.cscs.ch/software/communication/cray-mpich/index.md#cray-mpich>) is recommended. [MPICH](<https://docs.cscs.ch/software/communication/mpich/index.md#mpich>) and [OpenMPI](<https://docs.cscs.ch/software/communication/openmpi/index.md#openmpi>) may also be used, with limitations. Cray MPICH, MPICH, and OpenMPI make use of [libfabric](<https://docs.cscs.ch/software/communication/libfabric/index.md#libfabric> "Libfabric") to interact with the underlying network.

Most machine learning applications rely on [NCCL](<https://docs.cscs.ch/software/communication/nccl/index.md#nccl>) for high-performance implementations of collectives. NCCL have to be configured with a plugin using [libfabric](<https://docs.cscs.ch/software/communication/libfabric/index.md#libfabric> "Libfabric") to make full use of the Slingshot network.

See the individual pages for each library for information on how to use and best configure the libraries.

- **Low Level**

  Learn about the low-level networking library libfabric, and how to use it in uenv and containers

  [libfabric](<https://docs.cscs.ch/software/communication/libfabric/index.md#libfabric> "Libfabric")

- **MPI**

  Cray MPICH is the most optimized and best tested MPI implementation on Alps, and is used by uenv.

  [Cray MPICH](<https://docs.cscs.ch/software/communication/cray-mpich/index.md#cray-mpich>)

  For compatibility in containers:

  [MPICH](<https://docs.cscs.ch/software/communication/mpich/index.md#mpich>)

  Also OpenMPI can be built in containers or in uenv

  [OpenMPI](<https://docs.cscs.ch/software/communication/openmpi/index.md#openmpi>)

- **Machine Learning**

  Communication libraries used by ML tools like Torch, and some simulation codes.

  [NCCL](<https://docs.cscs.ch/software/communication/nccl/index.md#nccl>)

  [NVSHMEM](<https://docs.cscs.ch/software/communication/nvshmem/index.md#nvshmem>)
