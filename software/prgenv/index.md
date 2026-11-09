# Programming Environments

CSCS provides “programming environments” on Alps clusters. Programming environments provide pre-installed software, libraries and tools that can be used to build or install applications and workflows. For example:

- The `prgenv` uenv provide provide compilers, MPI, and commonly-used libraries and packages for building applications from source.
- Container images for ML/AI with optimised communication and GPU libraries and popular frameworks like PyTorch, on top of which workflow-specific tools can be installed.

## Uenv

- **prgenv-gnu** uenv

  Provides compilers, MPI, tools and libraries built around the GNU compiler toolchain. It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.
- **prgenv-gnu-openmpi** uenv

  Same as `prgenv-gnu` but with OpenMPI instead of Cray MPICH.
- **prgenv-nvfortran** uenv

  Provides a set of tools and libraries for building applications that need the NVIDIA Fortran compiler, commonly required for OpenACC and CUDA-Fortran applications.
- **linalg** uenv

  Provides compilers, MPI and Python, along with linear algebra and mesh partitioning libraries for a broad range of use cases.
- **julia** uenv

  Provides a complete HPC setup for running Julia efficiently at scale, using the supercomputer hardware optimally.
- **prgenv-intel** uenv

  Provides a set of tools and libraries for building applications with the intel OneAPI compilers on Eiger.
- **prgenv-dpcpp** uenv

  Extends `prgenv-gnu` with the Intel DPC++ (SYCL) compiler for GH200 GPUs.

## Containers

- **Alps Extended Images** containers

  Container images based on [NGC](<https://catalog.ngc.nvidia.com/>) that have been fine-tuned for Alps. Recommended as the starting point for ML/AI workflows.
- **Cray Programming Environment** containers

  The Cray Programming Environment (CPE) is a suite of compilers, libraries and tools provided by HPE.

  These are the “Cray Modules”, familiar to users of old Piz Daint and other HPE/Cray clusters.
