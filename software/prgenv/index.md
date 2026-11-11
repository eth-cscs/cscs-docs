# Programming Environments

CSCS provides “programming environments” on Alps clusters. Programming environments provide pre-installed software, libraries and tools that can be used to build or install applications and workflows. For example:

- The `prgenv` uenv provide provide compilers, MPI, and commonly-used libraries and packages for building applications from source.
- Container images for ML/AI with optimised communication and GPU libraries and popular frameworks like PyTorch, on top of which workflow-specific tools can be installed.

## Uenv

- [**prgenv-gnu**](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) uenv

  Provides compilers, MPI, tools and libraries built around the GNU compiler toolchain. It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.
- [**prgenv-gnu-openmpi**](<https://docs.cscs.ch/software/prgenv/prgenv-gnu-openmpi/index.md#prgenv-gnu-openmpi>) uenv

  Same as [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) but with OpenMPI instead of Cray MPICH.
- [**prgenv-nvfortran**](<https://docs.cscs.ch/software/prgenv/prgenv-nvfortran/index.md#prgenv-nvfortran>) uenv

  Provides a set of tools and libraries for building applications that need the NVIDIA Fortran compiler, commonly required for OpenACC and CUDA-Fortran applications.
- [**linalg**](<https://docs.cscs.ch/software/prgenv/linalg/index.md#linalg>) uenv

  Provides compilers, MPI and Python, along with linear algebra and mesh partitioning libraries for a broad range of use cases.
- [**julia**](<https://docs.cscs.ch/software/prgenv/julia/index.md#julia>) uenv

  Provides a complete HPC setup for running Julia efficiently at scale, using the supercomputer hardware optimally.
- [**prgenv-intel**](<https://docs.cscs.ch/software/prgenv/prgenv-intel/index.md#prgenv-intel>) uenv

  Provides a set of tools and libraries for building applications with the intel OneAPI compilers on [Eiger](<https://docs.cscs.ch/clusters/eiger/index.md#eiger>).
- [**prgenv-dpcpp**](<https://docs.cscs.ch/software/prgenv/prgenv-dpcpp/index.md#prgenv-dpcpp>) uenv

  Extends [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) with the Intel DPC++ (SYCL) compiler for [GH200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") GPUs.

## Containers

- [**Alps Extended Images**](<https://docs.cscs.ch/software/alps-extended-images/index.md#alps-extended-images>) containers

  Container images based on [NGC](<https://catalog.ngc.nvidia.com/>) that have been fine-tuned for Alps. Recommended as the starting point for ML/AI workflows.
- [**Cray Programming Environment**](<https://docs.cscs.ch/software/prgenv/cpe/index.md#cray-programming-environment-cpe> "Cray Programming Environment (CPE)") containers

  The Cray Programming Environment (CPE) is a suite of compilers, libraries and tools provided by HPE.

  These are the “Cray Modules”, familiar to users of old Piz Daint and other HPE/Cray clusters.
