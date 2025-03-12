[](){#ref-communication-openmpi}
# OpenMPI

[Cray MPICH][ref-communication-cray-mpich] is the recommended MPI implementation on Alps.
However, [OpenMPI](https://www.open-mpi.org/) can be used as an alternative in some cases, with limited support from CSCS.

To use OpenMPI on Alps, it must be built against [libfabric][ref-communication-libfabric] with support for the [Slingshot 11 network][ref-alps-hsn].

!!! todo
    Building OpenMPI for Alps is still work in progress: https://eth-cscs.github.io/cray-network-stack/.
