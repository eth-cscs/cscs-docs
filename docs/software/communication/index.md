[](){#ref-software-communication}
# Communication Libraries

CSCS provides common communication libraries optimized for the [Slingshot 11 network on Alps][ref-alps-hsn].

For most scientific applications relying on MPI, [Cray MPICH][ref-communication-cray-mpich] is recommended.
[OpenMPI][ref-communication-openmpi] may also be used, with limitations.
Both Cray MPICH and OpenMPI make use of [libfabric][ref-communication-libfabric] to interact with the underlying network.

Most machine learning applications rely on [NCCL][ref-communication-nccl] or [RCCL][ref-communication-rccl] for high-performance implementations of collectives.
NCCL and RCCL have to be configured with a plugin using [libfabric][ref-communication-libfabric] to make full use of the Slingshot network.

See the individual pages for each library for information on how to use and best configure the libraries.

* [Cray MPICH][ref-communication-cray-mpich]
* [OpenMPI][ref-communication-openmpi]
* [NCCL][ref-communication-nccl]
* [RCCL][ref-communication-rccl]
* [libfabric][ref-communication-libfabric]
