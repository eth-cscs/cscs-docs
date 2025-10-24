[](){#ref-software-communication}
# Communication Libraries

Communication libraries are used by scientific and AI workloads to communicate between processes.
The communication libraries used by workloads need to be built and configured correctly to get the best performance.
Broadly speaking, there are two levels of communication:

* **intra-node** communication between two processes on the same node.
* **inter-node** communication between different nodes, which requires 

Inter-node communication requires sending and receiving data over the [Slingshot 11 network][ref-alps-hsn] that connects nodes on Alps.
Communication libraries, like MPI and NCCL, need to be configured to use the [libfabric][ref-communication-libfabric] library that has an optimised back end for Slingshot 11.

CSCS provides communication libraries optimised for libfabric and slingshot in uenv, and guidance on how to configure container images similarly.
This section of the documentation provides advice on how to build and install software to use these libraries, and how to deploy them.

For most scientific applications relying on MPI, [Cray MPICH][ref-communication-cray-mpich] is recommended.
[MPICH][ref-communication-mpich] and [OpenMPI][ref-communication-openmpi] may also be used, with limitations.
Cray MPICH, MPICH, and OpenMPI make use of [libfabric][ref-communication-libfabric] to interact with the underlying network.

Most machine learning applications rely on [NCCL][ref-communication-nccl] or [RCCL][ref-communication-rccl] for high-performance implementations of collectives.
NCCL and RCCL have to be configured with a plugin using [libfabric][ref-communication-libfabric] to make full use of the Slingshot network.

See the individual pages for each library for information on how to use and best configure the libraries.

* [libfabric][ref-communication-libfabric]
* [Cray MPICH][ref-communication-cray-mpich]
* [MPICH][ref-communication-mpich]
* [OpenMPI][ref-communication-openmpi]
* [NCCL][ref-communication-nccl]
* [RCCL][ref-communication-rccl]
