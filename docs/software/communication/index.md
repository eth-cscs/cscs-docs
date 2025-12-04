[](){#ref-software-communication}
# Communication Libraries

Communication libraries, like MPI and NCCL, are one of the building blocks for high performance scientific and ML workloads.
Broadly speaking, there are two levels of communication:

* **intra-node** communication between two processes on the same node.
* **inter-node** communication between different nodes, over the [Slingshot 11 network][ref-alps-hsn] that connects nodes on Alps..

To get the best inter-node performance on Alps, they need to be configured to use the [libfabric][ref-communication-libfabric] library that has an optimised back end for the Slingshot 11 network on Alps.

As such, communication libraries are part of the "base layer" of libraries and tools used by all workloads to fully utilize the hardware on Alps.
They comprise the *Network* layer in the following stack:

* **CPU**: compilers with support for building applications optimized for the CPU architecture on the node.
* **GPU**: CUDA and ROCM provide compilers and runtime libraries for NVIDIA and AMD GPUs respectively.
* **Network**: libfabric, MPI, NCCL/RCCL, NVSHMEM, need to be configured for the Slingshot network.

CSCS provides communication libraries optimised for libfabric and Slingshot in uenv, and guidance on how to create container images that use them.
This section of the documentation provides advice on how to build and install software to use these libraries, and how to deploy them.

For most scientific applications relying on MPI, [Cray MPICH][ref-communication-cray-mpich] is recommended.
[MPICH][ref-communication-mpich] and [OpenMPI][ref-communication-openmpi] may also be used, with limitations.
Cray MPICH, MPICH, and OpenMPI make use of [libfabric][ref-communication-libfabric] to interact with the underlying network.

Most machine learning applications rely on [NCCL][ref-communication-nccl] or [RCCL][ref-communication-rccl] for high-performance implementations of collectives.
NCCL and RCCL have to be configured with a plugin using [libfabric][ref-communication-libfabric] to make full use of the Slingshot network.

See the individual pages for each library for information on how to use and best configure the libraries.

<div class="grid cards" markdown>

-   __Low Level__

    Learn about the base installation libfabric and its dependencies

    [:octicons-arrow-right-24: libfabric][ref-alps]

</div>
<div class="grid cards" markdown>

-   __MPI__

    Cray MPICH is the most optimized and best tested MPI implementation on Alps, and is used by uenv.

    [:octicons-arrow-right-24: Cray MPICH][ref-communication-cray-mpich]

    For compatibility in containers:

    [:octicons-arrow-right-24: MPICH][ref-communication-mpich]

    Also OpenMPI can be built in containers or in uenv

    [:octicons-arrow-right-24: OpenMPI][ref-communication-openmpi]

</div>
<div class="grid cards" markdown>

-   __Machine Learning__

    Communication libraries used by ML tools like Torch, and some simulation codes.

    [:octicons-arrow-right-24: NCCL][ref-communication-nccl]

    [:octicons-arrow-right-24: RCCL][ref-communication-rccl]

    [:octicons-arrow-right-24: NVSHMEM][ref-communication-nvshmem]

</div>
