[](){#ref-software-prgenvs}
# Programming Environments

CSCS provides "programming environments" on Alps clusters.
Programming environments provide pre-installed software, libraries and tools that can be used to build or install applications and workflows.
For example:

- The `prgenv` uenv provide provide compilers, MPI, and commonly-used libraries and packages for building applications from source.
- Container images for ML/AI with optimised communication and GPU libraries and popular frameworks like PyTorch, on top of which workflow-specific tools can be installed.

## Uenv

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: [__prgenv-gnu__][ref-uenv-prgenv-gnu] uenv

    Provides compilers, MPI, tools and libraries built around the GNU compiler toolchain.
    It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.

-   :fontawesome-solid-layer-group: [__prgenv-gnu-openmpi__][ref-uenv-prgenv-gnu-openmpi] uenv

    Same as [`prgenv-gnu`][ref-uenv-prgenv-gnu] but with OpenMPI instead of Cray MPICH.

-   :fontawesome-solid-layer-group: [__prgenv-nvfortran__][ref-uenv-prgenv-nvfortran] uenv

    Provides a set of tools and libraries for building applications that need the NVIDIA Fortran compiler, commonly required for OpenACC and CUDA-Fortran applications.

-   :fontawesome-solid-layer-group: [__linalg__][ref-uenv-linalg] uenv

    Provides compilers, MPI and Python, along with linear algebra and mesh partitioning libraries for a broad range of use cases.

-   :fontawesome-solid-layer-group: [__julia__][ref-uenv-julia] uenv

    Provides a complete HPC setup for running Julia efficiently at scale, using the supercomputer hardware optimally.

</div>

## Containers

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: [__Alps Extended Images__][ref-software-extended-images] containers

    Container images based on [NGC]() images that have been fine-tuned for Alps.
    Recommended as the starting point for ML/AI workflows.

-   :fontawesome-solid-layer-group: [__Cray Programming Environment__][ref-cpe] containers

    The Cray Programming Environment (CPE) is a suite of compilers, libraries and tools provided by HPE.

    These are the "Cray Modules", familiar to users of old Piz Daint and other HPE/Cray clusters.

</div>
