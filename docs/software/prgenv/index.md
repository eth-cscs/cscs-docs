[](){#ref-software-prgenvs}
# Programming Environments

CSCS provides "programming environments" on Alps vClusters that provide compilers, MPI, and commonly used libraries and packages, that can be used to build applications from source.

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: [__prgenv-gnu__][ref-uenv-prgenv-gnu]

    Provides compilers, MPI, tools and libraries built around the GNU compiler toolchain.
    It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.

-   :fontawesome-solid-layer-group: [__prgenv-nvfortran__][ref-uenv-prgenv-nvfortran]

    Provides a set of tools and libraries for building applications that need the NVIDIA Fortran compiler, commonly required for OpenACC and CUDA-Fortran applications.

-   :fontawesome-solid-layer-group: [__linalg__][ref-uenv-linalg]

    Provides compilers, MPI and Python, along with linear algebra and mesh partitioning libraries for a broad range of use cases.

-   :fontawesome-solid-layer-group: [__Cray Programming Environment__][ref-cpe]

    The Cray Programming Environment (CPE) is a suite of compilers, libraries and tools provided by HPE.

    These are the "Cray Modules", familiar to users of old Piz Daint and other HPE/Cray clusters.

</div>

