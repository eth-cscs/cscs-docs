[](){#ref-uenv-vasp}
# VASP

The Vienna Ab initio Simulation Package ([VASP]) is a computer program for atomic scale materials modelling, e.g. electronic structure calculations and quantum-mechanical molecular dynamics, from first principles.

VASP computes an approximate solution to the many-body Schrödinger equation, either within density functional theory (DFT), solving the Kohn-Sham equations, or within the Hartree-Fock (HF) approximation, solving the Roothaan equations.
Hybrid functionals that mix the Hartree-Fock approach with density functional theory are implemented as well.
Furthermore, Green's functions methods (GW quasiparticles, and ACFDT-RPA) and many-body perturbation theory (2nd-order Møller-Plesset) are available in VASP.

In VASP, central quantities, like the one-electron orbitals, the electronic charge density, and the local potential are expressed in plane wave basis sets.
The interactions between the electrons and ions are described using norm-conserving or ultrasoft pseudopotentials, or the projector-augmented-wave method.
To determine the electronic groundstate, VASP makes use of efficient iterative matrix diagonalisation techniques, like the residual minimisation method with direct inversion of the iterative subspace (RMM-DIIS) or blocked Davidson algorithms.
These are coupled to highly efficient Broyden and Pulay density mixing schemes to speed up the self-consistency cycle.


!!! note "Licensing Terms and Conditions"
    Access to VASP is restricted to users who have purchased a license from VASP Software GmbH.
    CSCS cannot provide free access to the code and needs to inform VASP Software GmbH with an updated list of users.
    Once you have a license, submit a request on the [CSCS service desk](https://jira.cscs.ch/plugins/servlet/desk) (with a copy of your license) to be added to the `vasp6` unix group, which will grant access to the `vasp` uenv.
    Please refer to the VASP web site for more information about licensing.
    Therefore, access to precompiled `VASP.6` executables and library files will be available only to users who have already purchased a `VASP.6` license and upon request will become members of the CSCS unix group `vasp6`.
    
    To access VASP follow the [`Accessing Restricted Software`][ref-uenv-restricted-software] guide.
    Please refer to the [VASP web site](https://www.vasp.at) for more information.


## Running VASP

### Running on the HPC platform
A precompiled uenv containing VASP with MPI, OpenMP, OpenACC, HDF5 and Wannier90 support is available.
Due to license restrictions, the VASP images are not directly accessible in the same way as other applications.

For accessing VASP uenv images, please see the guide to [accessing restricted software][ref-uenv-restricted-software].

To load the VASP uenv:
```bash
uenv start vasp/v6.5.0:v1 --view=vasp
```
The `vasp_std` , `vasp_ncl`  and `vasp_gam`  executables are now available for use.
Loading the uenv can also be directly done inside of a SLURM script.

```bash title="SLURM script for running VASP on a single node"
#!/bin/bash -l

#SBATCH --job-name=vasp
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=16
#SBATCH --gpus-per-task=1
#SBATCH --uenv=vasp/v6.5.0:v1
#SBATCH --view=vasp
#SBATCH --account=<ACCOUNT>
#SBATCH --partition=normal

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MPICH_GPU_SUPPORT_ENABLED=1

srun vasp_std
```

!!! note
    It's recommended to use the SLURM option `--gpus-per-task=1`, since VASP may fail to properly assign ranks to GPUs when running on more than one node.
    This is not required when using the CUDA MPS wrapper for oversubscription of GPUs.

!!! note
    VASP relies on CUDA-aware MPI, which requires `MPICH_GPU_SUPPORT_ENABLED=1` to be set when using Cray MPICH. On the HPC platform including `daint`, this is set by default and does not have to be included in SLURM scripts.



### Multiple Tasks per GPU
Using more than one task per GPU is possible with VASP and may lead to better GPU utilization.
However, VASP relies on [NCCL] for efficient communication, but falls back to MPI when using multiple tasks per GPU.
In many cases, this drawback is the greater factor and it's best to use one task per GPU.

To run with multiple tasks per GPU, a wrapper script is required to start a CUDA MPS service.
This script can be found at [NVIDIA GH200 GPU nodes: multiple ranks per GPU][ref-slurm-gh200-multi-rank-per-gpu].

```bash title="SLURM script for running VASP on a single node with two tasks per GPU"
#!/bin/bash -l

#SBATCH --job-name=vasp
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=16
#SBATCH --uenv=vasp/v6.5.0:v1
#SBATCH --view=vasp
#SBATCH --account=<ACCOUNT>
#SBATCH --partition=normal

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MPICH_GPU_SUPPORT_ENABLED=1

srun ./mps-wrapper.sh vasp_std
```

## Building VASP from source

To build VASP from source, the `develop` view must first be loaded:
```
uenv start vasp/v6.5.0:v1 --view=develop
```

All required dependencies can now be found in `/user-environment/env/develop`.
Note that shared libraries might not be found when executing VASP, if the makefile does not include additional rpath linking options or `LD_LIBRARY_PATH` has not been extended.

!!! warning
    The detection of MPI CUDA support does not work properly with Cray MPICH.
    After compiling from source, it's also required to set `export PMPI_GPU_AWARE=1` at runtime to disable the CUDA support check within VASP.
    Alternatively, since version 6.5.0, the build option `-DCRAY_MPICH` can be added to disable the check at compile time.
    The provided precompiled binaries of VASP are patched and do not require special settings.


Examples for makefiles that set the necessary rpath and link options on GH200:


??? note "Makefile for v6.5.0"
    ```make
    # Default precompiler options
    CPP_OPTIONS = -DHOST=\"LinuxNV\" \
                 -DMPI -DMPI_INPLACE -DMPI_BLOCK=8000 -Duse_collective \
                 -DscaLAPACK \
                 -DCACHE_SIZE=4000 \
                 -Davoidalloc \
                 -Dvasp6 \
                 -Dtbdyn \
                 -Dqd_emulate \
                 -Dfock_dblbuf \
                 -D_OPENMP \
                 -DACC_OFFLOAD \
                 -DNVCUDA \
                 -DUSENCCL \
                 -DCRAY_MPICH

    CPP         = nvfortran -Mpreprocess -Mfree -Mextend -E $(CPP_OPTIONS) $*$(FUFFIX)  > $*$(SUFFIX)
    CPP         = nvfortran -Mpreprocess -Mfree -Mextend -E $(CPP_OPTIONS) $*$(FUFFIX)  > $*$(SUFFIX)

    CUDA_VERSION = $(shell nvcc -V | grep -E -o -m 1 "[0-9][0-9]\.[0-9]," | rev | cut -c 2- | rev)

    CC          = mpicc -acc -gpu=cc90,cuda${CUDA_VERSION} -mp
    FC          = mpif90 -acc -gpu=cc90,cuda${CUDA_VERSION} -mp
    FCL         = mpif90 -acc -gpu=cc90,cuda${CUDA_VERSION} -mp -c++libs

    FREE        = -Mfree

    FFLAGS      = -Mbackslash -Mlarge_arrays

    OFLAG       = -fast

    DEBUG       = -Mfree -O0 -traceback

    LLIBS       = -cudalib=cublas,cusolver,cufft,nccl -cuda

    # Redefine the standard list of O1 and O2 objects
    SOURCE_O1  := pade_fit.o minimax_dependence.o
    SOURCE_O2  := pead.o

    # For what used to be vasp.5.lib
    CPP_LIB     = $(CPP)
    FC_LIB      = $(FC)
    CC_LIB      = $(CC)
    CFLAGS_LIB  = -O -w
    FFLAGS_LIB  = -O1 -Mfixed
    FREE_LIB    = $(FREE)

    OBJECTS_LIB = linpack_double.o

    # For the parser library
    CXX_PARS    = nvc++ --no_warnings

    ##
    ## Customize as of this point! Of course you may change the preceding
    ## part of this file as well if you like, but it should rarely be
    ## necessary ...
    ##
    # When compiling on the target machine itself , change this to the
    # relevant target when cross-compiling for another architecture
    #
    # NOTE: Using "-tp neoverse-v2" causes some tests to fail. On GH200 architecture, "-tp host"
    # is recommended.
    VASP_TARGET_CPU ?= -tp host
    FFLAGS     += $(VASP_TARGET_CPU)

    # Specify your NV HPC-SDK installation (mandatory)
    #... first try to set it automatically
    NVROOT      =$(shell which nvfortran | awk -F /compilers/bin/nvfortran '{ print $$1 }')

    # If the above fails, then NVROOT needs to be set manually
    #NVHPC      ?= /opt/nvidia/hpc_sdk
    #NVVERSION   = 21.11
    #NVROOT      = $(NVHPC)/Linux_x86_64/$(NVVERSION)

    ## Improves performance when using NV HPC-SDK >=21.11 and CUDA >11.2
    #OFLAG_IN   = -fast -Mwarperf
    #SOURCE_IN  := nonlr.o

    # Software emulation of quadruple precision (mandatory)
    QD         ?= $(NVROOT)/compilers/extras/qd
    LLIBS      += -L$(QD)/lib -lqdmod -lqd -Wl,-rpath,$(QD)/lib
    INCS       += -I$(QD)/include/qd

    # BLAS (mandatory)
    BLAS        = -lnvpl_blas_lp64_gomp -lnvpl_blas_core

    # LAPACK (mandatory)
    LAPACK      = -lnvpl_lapack_lp64_gomp -lnvpl_lapack_core

    # scaLAPACK (mandatory)
    SCALAPACK   = -lscalapack

    LLIBS      += $(SCALAPACK) $(LAPACK) $(BLAS) -Wl,-rpath,/user-environment/env/develop/lib -Wl,-rpath,/user-environment/env/develop/lib64 -Wl,--disable-new-dtags

    # FFTW (mandatory)
    FFTW_ROOT  ?= /user-environment/env/develop
    LLIBS      += -L$(FFTW_ROOT)/lib -lfftw3 -lfftw3_omp
    INCS       += -I$(FFTW_ROOT)/include

    # Use cusolvermp (optional)
    # supported as of NVHPC-SDK 24.1 (and needs CUDA-11.8)
    #CPP_OPTIONS+= -DCUSOLVERMP -DCUBLASMP
    #LLIBS      += -cudalib=cusolvermp,cublasmp -lnvhpcwrapcal

    # HDF5-support (optional but strongly recommended)
    CPP_OPTIONS+= -DVASP_HDF5
    HDF5_ROOT  ?= /user-environment/env/develop
    LLIBS      += -L$(HDF5_ROOT)/lib -lhdf5_fortran
    INCS       += -I$(HDF5_ROOT)/include

    # For the VASP-2-Wannier90 interface (optional)
    CPP_OPTIONS    += -DVASP2WANNIER90
    WANNIER90_ROOT ?= /user-environment/env/develop
    LLIBS          += -L$(WANNIER90_ROOT)/lib -lwannier

    # For the fftlib library (recommended)
    #CPP_OPTIONS+= -Dsysv
    #FCL        += fftlib.o
    #CXX_FFTLIB  = nvc++ -mp --no_warnings -std=c++11 -DFFTLIB_THREADSAFE
    #INCS_FFTLIB = -I./include -I$(FFTW_ROOT)/include
    #LIBS       += fftlib
    #LLIBS      += -ldl
    ```


??? note "Makefile for v6.4.3"
    ```make
    # Default precompiler options
    CPP_OPTIONS = -DHOST=\"LinuxNV\" \
                 -DMPI -DMPI_INPLACE -DMPI_BLOCK=8000 -Duse_collective \
                 -DscaLAPACK \
                 -DCACHE_SIZE=4000 \
                 -Davoidalloc \
                 -Dvasp6 \
                 -Duse_bse_te \
                 -Dtbdyn \
                 -Dqd_emulate \
                 -Dfock_dblbuf \
                 -D_OPENMP \
                 -D_OPENACC \
                 -DUSENCCL -DUSENCCLP2P

    CPP         = nvfortran -Mpreprocess -Mfree -Mextend -E $(CPP_OPTIONS) $*$(FUFFIX)  > $*$(SUFFIX)

    CUDA_VERSION = $(shell nvcc -V | grep -E -o -m 1 "[0-9][0-9]\.[0-9]," | rev | cut -c 2- | rev)

    CC          = mpicc -acc -gpu=cc90,cuda${CUDA_VERSION} -mp
    FC          = mpif90 -acc -gpu=cc90,cuda${CUDA_VERSION} -mp
    FCL         = mpif90 -acc -gpu=cc90,cuda${CUDA_VERSION} -mp -c++libs

    FREE        = -Mfree

    FFLAGS      = -Mbackslash -Mlarge_arrays

    OFLAG       = -fast

    DEBUG       = -Mfree -O0 -traceback

    OBJECTS     = fftmpiw.o fftmpi_map.o fftw3d.o fft3dlib.o

    LLIBS       = -cudalib=cublas,cusolver,cufft,nccl -cuda

    # Redefine the standard list of O1 and O2 objects
    SOURCE_O1  := pade_fit.o minimax_dependence.o
    SOURCE_O2  := pead.o

    # For what used to be vasp.5.lib
    CPP_LIB     = $(CPP)
    FC_LIB      = $(FC)
    CC_LIB      = $(CC)
    CFLAGS_LIB  = -O -w
    FFLAGS_LIB  = -O1 -Mfixed
    FREE_LIB    = $(FREE)

    OBJECTS_LIB = linpack_double.o

    # For the parser library
    CXX_PARS    = nvc++ --no_warnings

    ##
    ## Customize as of this point! Of course you may change the preceding
    ## part of this file as well if you like, but it should rarely be
    ## necessary ...
    ##
    # When compiling on the target machine itself , change this to the
    # relevant target when cross-compiling for another architecture
    #
    # NOTE: Using "-tp neoverse-v2" causes some tests to fail. On GH200 architecture, "-tp host"
    # is recommended.
    VASP_TARGET_CPU ?= -tp host
    FFLAGS     += $(VASP_TARGET_CPU)

    # Specify your NV HPC-SDK installation (mandatory)
    #... first try to set it automatically
    NVROOT      =$(shell which nvfortran | awk -F /compilers/bin/nvfortran '{ print $$1 }')

    # If the above fails, then NVROOT needs to be set manually
    #NVHPC      ?= /opt/nvidia/hpc_sdk
    #NVVERSION   = 21.11
    #NVROOT      = $(NVHPC)/Linux_x86_64/$(NVVERSION)

    ## Improves performance when using NV HPC-SDK >=21.11 and CUDA >11.2
    #OFLAG_IN   = -fast -Mwarperf
    #SOURCE_IN  := nonlr.o

    # Software emulation of quadruple precision (mandatory)
    QD         ?= $(NVROOT)/compilers/extras/qd
    LLIBS      += -L$(QD)/lib -lqdmod -lqd -Wl,-rpath,$(QD)/lib
    INCS       += -I$(QD)/include/qd

    # BLAS (mandatory)
    BLAS        = -lnvpl_blas_lp64_gomp -lnvpl_blas_core

    # LAPACK (mandatory)
    LAPACK      = -lnvpl_lapack_lp64_gomp -lnvpl_lapack_core

    # scaLAPACK (mandatory)
    SCALAPACK   = -lscalapack

    LLIBS      += $(SCALAPACK) $(LAPACK) $(BLAS) -Wl,-rpath,/user-environment/env/develop/lib -Wl,-rpath,/user-environment/env/develop/lib64 -Wl,--disable-new-dtags

    # FFTW (mandatory)
    FFTW_ROOT  ?= /user-environment/env/develop
    LLIBS      += -L$(FFTW_ROOT)/lib -lfftw3 -lfftw3_omp
    INCS       += -I$(FFTW_ROOT)/include

    # Use cusolvermp (optional)
    # supported as of NVHPC-SDK 24.1 (and needs CUDA-11.8)
    #CPP_OPTIONS+= -DCUSOLVERMP -DCUBLASMP
    #LLIBS      += -cudalib=cusolvermp,cublasmp -lnvhpcwrapcal

    # HDF5-support (optional but strongly recommended)
    CPP_OPTIONS+= -DVASP_HDF5
    HDF5_ROOT  ?= /user-environment/env/develop
    LLIBS      += -L$(HDF5_ROOT)/lib -lhdf5_fortran
    INCS       += -I$(HDF5_ROOT)/include

    # For the VASP-2-Wannier90 interface (optional)
    CPP_OPTIONS    += -DVASP2WANNIER90
    WANNIER90_ROOT ?= /user-environment/env/develop
    LLIBS          += -L$(WANNIER90_ROOT)/lib -lwannier

    # For the fftlib library (recommended)
    #CPP_OPTIONS+= -Dsysv
    #FCL        += fftlib.o
    #CXX_FFTLIB  = nvc++ -mp --no_warnings -std=c++11 -DFFTLIB_THREADSAFE
    #INCS_FFTLIB = -I./include -I$(FFTW_ROOT)/include
    #LIBS       += fftlib
    #LLIBS      += -ldl
    ```



[VASP]: https://vasp.at/
[NCCL]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html

