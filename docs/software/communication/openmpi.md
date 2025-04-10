[](){#ref-communication-openmpi}
# OpenMPI

[Cray MPICH][ref-communication-cray-mpich] is the recommended MPI implementation on Alps.
However, [OpenMPI](https://www.open-mpi.org/) can be used as an alternative in some cases, with limited support from CSCS.

To use OpenMPI on Alps, it must be built against [libfabric][ref-communication-libfabric] with support for the [Slingshot 11 network][ref-alps-hsn].

## Using OpenMPI

!!! warning
    Building and using OpenMPI on Alps is still [work in progress](https://eth-cscs.github.io/cray-network-stack/).
    The instructions found on this page may be inaccurate, but are a good starting point to using OpenMPI on Alps.

!!! todo
    Deploy experimental uenv.

!!! todo
    Document OpenMPI uenv next to prgenv-gnu, prgenv-nvfortran, and linalg?

OpenMPI is provided through a [uenv][ref-uenv] similar to [`prgenv-gnu`][ref-uenv-prgenv-gnu].
Once the uenv is loaded, compiling and linking with OpenMPI and libfabric is transparent.
At runtime, some additional options must be set to correctly use the Slingshot network.

First, when launching applications through slurm, [PMIx](https://pmix.github.com) must be used for application launching.
This is done with the `--mpi` flag of `srun`:
```bash
srun --mpi=pmix ...
```

Additionally, the following environment variables should be set:
```bash
export PMIX_MCA_psec="native" # (1)!
export FI_PROVIDER="cxi" # (2)!
export OMPI_MCA_pml="^ucx" # (3)!
export OMPI_MCA_mtl="ofi" # (4)!

1. Ensures PMIx uses the same security domain as Slurm. Otherwise PMIx will print warnings at startup.
2. Use the CXI (Slingshot) provider.
3. Use anything except [UCX](https://openucx.org/documentation/) for [point-to-point communication](https://docs.open-mpi.org/en/v5.0.x/mca.html#selecting-which-open-mpi-components-are-used-at-run-time). The `^` signals that OpenMPI should exclude all listed components.
4. Use libfabric for the [Matching Transport Layer](https://docs.open-mpi.org/en/v5.0.x/mca.html#frameworks).

!!! info "CXI provider does all communication through the network interface cards (NICs)"
    When using the libfabric CXI provider, all communication goes through NICs, including intra-node communication.
    This means that intra-node communication can not make use of shared memory optimizations and the maximum bandwidth will not be severely limited.

    Libfabric has a new [LINKx](https://ofiwg.github.io/libfabric/v2.1.0/man/fi_lnx.7.html) provider, which allows using different libfabric providers for inter- and intra-node communication.
    This provider is not as well tested, but can in theory perform better for intra-node communication, because it can use shared memory.
    To use the LINKx provider, set the following, instead of `FI_PROVIDER=cxi`:

    ```bash
    export FI_PROVIDER="lnx" # (1)!
    export FI_LNX_PROV_LINKS="shm+cxi" # (2)!
    ```

    1. Use the libfabric LINKx provider, to allow using different libfabric providers for inter- and intra-node communication.
    2. Use the shared memory provider for intra-node communication and the CXI (Slingshot) provider for inter-node communication.
