[](){#ref-communication-openmpi}
# OpenMPI

[Cray MPICH][ref-communication-cray-mpich] is the recommended MPI implementation on Alps.
However, [OpenMPI](https://www.open-mpi.org/) can be used as an alternative in some cases, with limited support from CSCS.

Support for the [Slingshot 11 network][ref-alps-hsn] is provided by the [libfabric][ref-communication-libfabric] library.

## Using OpenMPI

OpenMPI is provided in the [`prgenv-gnu-openmpi`][ref-uenv-prgenv-gnu-openmpi] uenv.
Once the uenv is loaded, compiling and linking with OpenMPI and libfabric is transparent.
At runtime, some additional options must be set to correctly use the Slingshot network.

First, when launching applications through Slurm, [PMIx](https://pmix.github.com) must be used for application launching.
This is done with the `--mpi` flag of `srun`:
```bash
srun --mpi=pmix ...
```

There are two primary ways to configure OpenMPI and libfabric to use the Slingshot network:

1. [Only using the CXI provider][ref-communication-openmpi-cxi].
   This method has been found to work in more applications but uses NICs for intra-node communication which can limit performance.
2. [Using the LINKx provider][ref-communication-openmpi-lnx] which combines the CXI provider for inter-node communication with the shared memory provider for intra-node communication.
   This provider is newer, may not support all features, and more likely to contain bugs, but makes full use of intra-node bandwidth.

We recommend trying the LINKx provider first as it provides better performance in the situations that it's supported.
If you encounter failures using the LINKx provider we ask you to [get in touch with us][ref-get-in-touch] so that we can evaluate whether upstream libfabric or OpenMPI need fixing.

[](){#ref-communication-openmpi-cxi}
### Using the CXI provider

To use the CXI provider the following environment variables should be set:

```bash
export PMIX_MCA_psec="native" # (1)!
export FI_PROVIDER="cxi" # (2)!
export OMPI_MCA_pml="cm" # (3)!
export OMPI_MCA_mtl="ofi" # (4)!
```

1. Ensures PMIx uses the same security domain as Slurm. Otherwise PMIx will print warnings at startup.
2. Use the CXI (Slingshot) provider.
3. Use CM for [point-to-point communication](https://docs.open-mpi.org/en/v5.0.x/mca.html#selecting-which-open-mpi-components-are-used-at-run-time).
4. Use libfabric for the [Matching Transport Layer](https://docs.open-mpi.org/en/v5.0.x/mca.html#frameworks).

!!! info "CXI provider does all communication through the network interface cards (NICs)"
    When using the libfabric CXI provider, all communication goes through NICs, including intra-node communication.
    This means that intra-node communication can not make use of shared memory optimizations and the maximum bandwidth will be severely limited.
    Use the [LINKx][ref-communication-openmpi-lnx] provider to make full use of the available intra-node bandwidth.

[](){#ref-communication-openmpi-lnx}
### Using the LINKx provider

The default configuration routes all communication through the NICs.
While performance may sometimes be acceptable, this mode does not make full use of the much higher intra-node bandwidth available on Grace-Hopper nodes.
In particular, GPU-GPU communication is significantly faster when using the appropriate intra-node links.

The experimental [LINKx](https://ofiwg.github.io/libfabric/v2.3.1/man/fi_lnx.7.html) libfabric provider allows composing multiple libfabric providers for inter- and intra-node communication.
The CXI provider can be used for inter-node communication while the shared memory (`shm`) provider can be used to take advantage of xpmem for CPU-CPU communication and GDRCopy for GPU-GPU communication.

!!! danger "The LINKx provider is experimental"

    While many basic tests work correctly using the LINKx provider we have had reports of applications failing to run with the LINKx provider.
    Always validate your results to ensure MPI is working correctly.

To use the LINKx provider set the following environment variables:

```bash
export PMIX_MCA_psec="native"
export FI_PROVIDER="lnx" # (1)!
export FI_LNX_PROV_LINKS="shm+cxi:cxi0|shm+cxi:cxi1|shm+cxi:cxi2|shm+cxi:cxi3" # (2)!
export FI_SHM_USE_XPMEM=1 # (3)!
export OMPI_MCA_pml="cm"
export OMPI_MCA_mtl="ofi"
export OMPI_MCA_mtl_ofi_av=table # (4)!
```

1. Use the libfabric LINKx provider, to allow using different libfabric providers for inter- and intra-node communication.
2. Specify which providers LINKx should use.
   Use the shared memory provider for intra-node communication and the CXI (Slingshot) provider for inter-node communication.
   Choose one of the four available NICs on a node in a round-robin fashion.
3. Explicitly use xpmem for CPU-CPU communication.
   The default is to use CMA.
4. The LINKx provider requires this option to be set. TODO: Better explanation?

## Known issues

TODO: async collectives don't work.
