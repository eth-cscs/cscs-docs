[](){#ref-uenv-cp2k}
# CP2K

[CP2K] is a quantum chemistry and solid state physics software package that can perform atomistic simulations of solid
state, liquid, molecular, periodic, material, crystal, and biological systems.

CP2K provides a general framework for different modeling methods such as DFT using the mixed Gaussian and plane waves
approaches GPW and GAPW. Supported theory levels include DFTB, LDA, GGA, MP2, RPA, semi-empirical methods (AM1, PM3,
PM6, RM1, MNDO, …), and classical force fields (AMBER, CHARMM, …). CP2K can do simulations of molecular dynamics,
metadynamics, Monte Carlo, Ehrenfest dynamics, vibrational analysis, core level spectroscopy, energy minimization, and
transition state optimization using NEB or dimer method. See [CP2K Features] for a detailed overview.

!!! note "uenvs"

    [CP2K] is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

## Dependencies

On our systems, CP2K is built with the following dependencies:

* [COSMA]
* [Cray MPICH]
* [DBCSR]
* [DLA-Future]
* [dftd4] (from `cp2k@2025.1` onwards)
* [ELPA]
* [FFTW]
* [Libxc]
* [libint]
* [OpenBLAS]
* [PLUMED] (from `cp2k@2024.1` onwards)
* [ScaLAPACK]
* [SIRIUS]
* [Spglib]
* [spla]

!!! note "GPU-aware MPI"
    [COSMA] and [DLA-Future] are built with GPU-aware MPI. On the HPC platform, `MPICH_GPU_SUPPORT_ENABLED=1` is set by
    default, therefore there is no need to set it manually.

!!! warning "BLAS/LAPACK on Eiger"
    
    On Eiger, the default BLAS/LAPACK library is Intel oneAPI MKL (oneMKL) until `cp2k@2024.3`. 
    From `cp2k@2025.1` the default BLAS/LAPACK library is [OpenBLAS].

## Running CP2K

### Running on the HPC platform

To start a job, two bash scripts are potentially required: a [slurm] submission script, and a wrapper to start the [CUDA
MPS] daemon so that multiple MPI ranks can use the same GPU.

```bash title="run_cp2k.sh"
#!/bin/bash -l

#SBATCH --job-name=cp2k-job
#SBATCH --time=00:30:00           # (1)
#SBATCH --nodes=4
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=32      # (2)
#SBATCH --cpus-per-task=8         # (3)
#SBATCH --account=<ACCOUNT>
#SBATCH --hint=nomultithread
#SBATCH --hint=exclusive
#SBATCH --no-requeue
#SBATCH --uenv=<CP2K_UENV>
#SBATCH --view=cp2k

export CUDA_CACHE_PATH="/dev/shm/$RANDOM"           # (5)
export MPICH_MALLOC_FALLBACK=1
export OMP_NUM_THREADS=$((SLURM_CPUS_PER_TASK - 1)) # (4)

ulimit -s unlimited
srun --cpu-bind=socket ./mps-wrapper.sh cp2k.psmp -i <CP2K_INPUT> -o <CP2K_OUTPUT>
```

1. Time format: `HH:MM:SS`

2. Number of MPI ranks per node
 
3. Number of CPUs per MPI ranks

4. [OpenBLAS] spawns an extra thread, therefore it is necessary to set `OMP_NUM_THREADS` to `SLURM_CPUS_PER_TASK - 1`
   for good performance. With [Intel MKL], this is not necessary and one can set `OMP_NUM_THREADS` to
   `SLURM_CPUS_PER_TASK`.

5. [DBCSR] relies on extensive JIT compilation and we store the cache in memory to avoid I/O overhead


* Change <ACCOUNT> to your project account name
* Change `<CP2K_UENV>` to the name (or path) of the actual CP2K uenv you want to use
* Change `<PATH_TO_CP2K_DATA_DIR>` to the actual path to the CP2K data directory
* Change `<CP2K_INPUT>` and `<CP2K_OUTPUT>` to the actual input and output files


With the above scripts, you can launch a [CP2K] calculation on 4 nodes, with 32 MPI ranks per node and 8 OpenMP threads
per rank with


```bash 
sbatch run_cp2k.sh
```

!!! note
    
    The `mps-wrapper.sh` script, required to properly over-subscribe the GPU, is provided at the following page: 
    [NVIDIA GH200 GPU nodes: multiple ranks per GPU][ref-slurm-gh200-multi-rank-per-gpu].

!!! warning

    The `--cpu-bind=socket` option is necessary to get good performance.


!!! warning

    Each GH200 node has 4 modules, each of them composed of a ARM Grace CPU with 72 cores and a H200 GPU directly
    attached to it. Please see [Alps hardware][ref-alps-hardware] for more information.
    It is important that the number of MPI ranks passed to [slurm] with `--ntasks-per-node` is a multiple of 4.

    ??? note

         In the example above, we use 32 MPI ranks with 8 OpenMP threads, for a total of 64 cores per GPU and 256 cores
         per node. Experiments have shown that CP2K performs and scales better when the number of MPI ranks is a power
         of 2, even if some cores are left idling. 


??? info "Running regression tests"

    If you want to run CP2K regression tests with the CP2K executable provided by the uenv, make sure to use the version
    of the regression tests corresponding to the version of CP2K provided by the uenv. The regression test data is
    sometimes adjusted, and using the wrong version of the regression tests can lead to test failures.


??? example "Scaling of `QS/H2O-1024` benchmark"

    The [`QS/H2O-1024` benchmark](https://github.com/cp2k/cp2k/blob/master/benchmarks/QS/H2O-1024.inp) is a DFT
    molecular dynamics simulation of liquid water. It relies on [DBCSR] for block sparse matrix-matrix multiplication.

    All calculations were run with 32 MPI ranks per node, and 8 OpenMP threads per rank (best configuration for this
    benchmark). 

    !!! note 
        `H2O-102.inp` is the largest example of DFT molecular dynamics simulation of liquid water that fits on a single
        GH200 node.

    | Number of nodes | Wall time (s) | Speecup | Efficiency |
    |:---------------:|:-------------:|:-------:|:----------:|
    | 1               |  793.1        | 1.00    | 1.00       |
    | 2               |  535.2        | 1.48    | 0.74       |
    | 4               |  543.9        | 1.45    | 0.36       |
    | 8               |  487.3        | 1.64    | 0.20       |
    | 16              |  616.7        | 1.28    | 0.08       |

    Scaling is not ideal on more than two nodes.

??? example "Scaling of `QS_mp2_rpa/128-H2O/H2O-128-RI-MP2-TZ` benchmark"

    The `QS_mp2_rpa/128-H2O/H2O-128-RI-MP2-TZ` benchmark is a straighfoward modification of the
    [`QS_mp2_rpa/64-H2O/H2O-64-RI-MP2-TZ` benchmark](https://github.com/cp2k/cp2k/blob/master/benchmarks/QS_mp2_rpa/64-H2O/H2O-64-RI-MP2-TZ.inp).
    
    It is a RI-MP2 calculation of a water cluster with 128 atoms.

    ??? info "Input file"
        
        ```Fortran
        &GLOBAL
          PRINT_LEVEL MEDIUM
          PROJECT H2O-128-RI-MP2-TZ
          RUN_TYPE ENERGY
        &END GLOBAL

        &FORCE_EVAL
          METHOD Quickstep
          &DFT
            BASIS_SET_FILE_NAME ./BASIS_H2O
            POTENTIAL_FILE_NAME ./POTENTIAL_H2O
            WFN_RESTART_FILE_NAME ./H2O-128-PBE-TZ-RESTART.wfn
            &MGRID
              CUTOFF 800
              REL_CUTOFF 50
            &END MGRID
            &QS
              EPS_DEFAULT 1.0E-12
            &END QS
            &SCF
              EPS_SCF 1.0E-6
              MAX_SCF 30
              SCF_GUESS RESTART
              &OT
                MINIMIZER CG
                PRECONDITIONER FULL_ALL
              &END OT
              &OUTER_SCF
                EPS_SCF 1.0E-6
                MAX_SCF 20
              &END OUTER_SCF
              &PRINT
                &RESTART OFF
                &END RESTART
              &END PRINT
            &END SCF
            &XC
              &HF
                FRACTION 1.0
                &INTERACTION_POTENTIAL
                  CUTOFF_RADIUS 6.0
                  POTENTIAL_TYPE TRUNCATED
                  T_C_G_DATA ./t_c_g.dat
                &END INTERACTION_POTENTIAL
                &MEMORY
                  MAX_MEMORY 16384
                &END MEMORY
                &SCREENING
                  EPS_SCHWARZ 1.0E-8
                  SCREEN_ON_INITIAL_P TRUE
                &END SCREENING
              &END HF
              &WF_CORRELATION
                MEMORY 1200
                NUMBER_PROC 1
                &INTEGRALS
                  &WFC_GPW
                    CUTOFF 300
                    EPS_FILTER 1.0E-12
                    EPS_GRID 1.0E-8
                    REL_CUTOFF 50
                  &END WFC_GPW
                &END INTEGRALS
                &RI_MP2
                &END RI_MP2
              &END WF_CORRELATION
              &XC_FUNCTIONAL NONE
              &END XC_FUNCTIONAL
            &END XC
          &END DFT
          &SUBSYS
            &CELL
              ABC 15.6404 15.6404 15.6404
            &END CELL
            &KIND H
              BASIS_SET cc-TZ
              BASIS_SET RI_AUX RI-cc-TZ
              POTENTIAL GTH-HF-q1
            &END KIND
            &KIND O
              BASIS_SET cc-TZ
              BASIS_SET RI_AUX RI-cc-TZ
              POTENTIAL GTH-HF-q6
            &END KIND
            &TOPOLOGY
              COORD_FILE_FORMAT XYZ
              COORD_FILE_NAME ./H2O-128.xyz
            &END TOPOLOGY
          &END SUBSYS
        &END FORCE_EVAL
        ```

    All calculations run for this scaling tests were using 32 MPI ranks per node and 8 OpenMP threads per rank. 
    The smallest amount of nodes necessary to run this calculation is 8.


    | Number of nodes | Wall time (s) | Speecup | Efficiency |
    |:---------------:|:-------------:|:-------:|:----------:|
    | 8               |  2037.0       | 1.00    | 1.00       |
    | 16              |  1096.2       | 1.85    | 0.92       |
    | 32              |  611.5        | 3.33    | 0.83       |
    | 64              |  410.5        | 4.96    | 0.62       |
    | 128             |  290.9        | 7.00    | 0.43       |

    MP2 calculations scale well on GH200, up to a large number of nodes ($> 50\%$ efficiency with 64 nodes).

??? example "Scaling of `QS_mp2_rpa/128-H2O/H2O-128-RI-dRPA-TZ` benchmark"

    The [`QS_mp2_rpa/128-H2O/H2O-128-RI-dRPA-T` benchmark](https://github.com/cp2k/cp2k/blob/master/benchmarks/QS_mp2_rpa/128-H2O/H2O-128-RI-dRPA-TZ.inp)
    is a RPA energy calculation, traditionally used to benchmark the performance of the [COSMA] library. 
    It a very large calculation, which requires at least 8 GH200 nodes to run. 
    The calculations were run with 16 MPI ranks per node and 16 OpenMP threads per rank.
    For RPA workloads, a higher ratio of threads per rank were beneficial.

    | Number of nodes | Wall time (s) | Speecup | Efficiency |
    |:---------------:|:-------------:|:-------:|:----------:|
    | 8               |  575.4        | 1.00    | 1.00       |
    | 16              |  465.8        | 1.23    | 0.61       |
    | 32              |  281.1        | 2.04    | 0.51       |
    | 64              |  205.3        | 2.80    | 0.35       |
    | 128             |  185.8        | 3.09    | 0.19       |

    This RPA input scales well until 32 GH200 nodes.

### Running on Eiger

On Eiger, a similar sbatch script can be used:

```bash title="run_cp2k.sh"
#!/bin/bash -l
#SBATCH --job-name=cp2k-job
#SBATCH --time=00:30:00           # (1)
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=32      # (2)
#SBATCH --cpus-per-task=4         # (3)
#SBATCH --account=<ACCOUNT>
#SBATCH --hint=nomultithread
#SBATCH --hint=exclusive
#SBATCH --constraint=mc
#SBATCH --uenv=<CP2K_UENV>
#SBATCH --view=cp2k

export OMP_NUM_THREADS=$((SLURM_CPUS_PER_TASK - 1)) # (4)

ulimit -s unlimited
srun --cpu-bind=socket cp2k.psmp -i <CP2K_INPUT> -o <CP2K_OUTPUT>
```

1. Time format: `HH:MM:SS`

2. Number of MPI ranks per node
 
3. Number of CPUs per MPI ranks

4. [OpenBLAS] spawns an extra thread, therefore it is necessary to set `OMP_NUM_THREADS` to `SLURM_CPUS_PER_TASK - 1`
   for good performance. With [Intel MKL], this is not necessary and one can set `OMP_NUM_THREADS` to
   `SLURM_CPUS_PER_TASK`.

5. [DBCSR] relies on extensive JIT compilation and we store the cache in memory to avoid I/O overhead

* Change <ACCOUNT> to your project account name
* Change `<CP2K_UENV>` to the name (or path) of the actual CP2K uenv you want to use
* Change `<PATH_TO_CP2K_DATA_DIR>` to the actual path to the CP2K data directory
* Change `<CP2K_INPUT>` and `<CP2K_OUTPUT>` to the actual input and output files

!!! warning

    The `--cpu-bind=socket` option is necessary to get good performance.

??? info "Running regression tests"

    If you want to run CP2K regression tests with the CP2K executable provided by the uenv, make sure to use the version
    of the regression tests corresponding to the version of CP2K provided by the uenv. The regression test data is
    sometimes adjusted, and using the wrong version of the regression tests can lead to test failures.

## Building CP2K from Source


The [CP2K] uenv provides all the dependencies required to build [CP2K] from source, with several optional features
enabled. You can follow these steps to build [CP2K] from source:

```bash
uenv start --view=develop <CP2K_UENV>               # (1)

cd <PATH_TO_CP2K_SOURCE>                            # (2)

mkdir build && cd build
CC=mpicc CXX=mpic++ FC=mpifort cmake \
    -GNinja \
    -DCMAKE_CUDA_HOST_COMPILER=mpicc \              # (3)
    -DCP2K_USE_LIBXC=ON \
    -DCP2K_USE_LIBINT2=ON \
    -DCP2K_USE_SPGLIB=ON \
    -DCP2K_USE_ELPA=ON \
    -DCP2K_USE_SPLA=ON \
    -DCP2K_USE_SIRIUS=ON \
    -DCP2K_USE_COSMA=ON \
    -DCP2K_USE_PLUMED=ON \
    -DCP2K_USE_DFTD4=ON \
    -DCP2K_USE_DLAF=ON \
    -DCP2K_USE_ACCEL=CUDA -DCP2K_WITH_GPU=H100 \    # (4)
    ..

ninja -j 32
```

1. Start the CP2K uenv and load the `develop` view (which provides all the necessary dependencies)

2. Go to the CP2K source directory

3. The `H100` option enables the `sm_90` architecture for the CUDA backend

!!! note "Eiger: `libxsmm`"

    On `x86` we deploy with `libxmm`. Add `-DCP2K_USE_LIBXSMM=ON` to the CMake invocation to use `libxsmm`.

??? note "Eiger: Intel MKL (before `cp2k@2025.1`)"

    On `x86` we deployed with `intel-oneapi-mkl` before `cp2k@2025.1`. 
    If you are using a pre-`cp2k@2025.1` uenv, add `-DCP2K_SCALAPACK_VENDOR=MKL` to the CMake invocation to find MKL.

??? note "CUDA architecture for `cp2k@2024.1` and earlier"

    `cp2k@2024.1` (and earlier) does not support compiling for `cuda_arch=90`. Use `-DCP2K_WITH_GPU=A100` instead, 
    which enables the `sm_80` architecture.

See [manual.cp2k.org/CMake] for more details.

### Known issues


#### DBCSR GPU scaling

On the GH200 architecture, it has been observed that the GPU accelerated version of [DBCSR] does not perform optimally in some cases.
For example, in the `QS/H2O-1024` benchmark above, CP2K does not scale well beyond 2 nodes. 
The CPU implementation of DBCSR does not suffer from this. A workaround was implemented in DBCSR, in order to switch 
GPU acceleration on/off with an environment variable:

```bash
export DBCSR_RUN_ON_GPU=0
```

While GPU acceleration is very good on a small number of nodes, the CPU implementation scales better. 
Therefore, for CP2K jobs running on a large number of nodes, it is worth investigating the use of the `DBCSR_RUN_ON_GPU`
environment variable.

Ssome niche application cases such as the `QS_low_scaling_postHF` benchmarks only run efficiently with the CPU version
of DBCSR. Generally, if the function `dbcsr_multiply_generic` takes a significant portion of the timing report
(at the end of the CP2K output file), it is worth investigating the effect of the `DBCSR_RUN_ON_GPU` environment variable.


#### CUDA grid backend with high angular momenta basis sets

The CP2K grid CUDA backend is currently buggy on Alps. Using basis sets with high angular momenta ($l \ge 3$)
result in slow calculations, especially for force calculations with meta-GGA functionals. 

As a workaround, you can you can disable CUDA acceleration fo the grid backend:

```bash
&GLOBAL
    &GRID
        BACKEND CPU
    &END GRID
&END GLOBAL
```

??? info "Fix available upon request"

    A fix for this issue for the HIP backend is currently being tested by CSCS engineers. If you would like to test it,
    please contact us and we will be able to provide the source code. The fix will eventually land on the upstream
    [CP2K] repository.

[CP2K]: https://www.cp2k.org/
[CP2K Features]: https://www.cp2k.org/features
[COSMA]: https://github.com/eth-cscs/COSMA
[DLA-Future]: https://github.com/eth-cscs/DLA-Future
[manual.cp2k.org/CMake]: https://manual.cp2k.org/trunk/getting-started/CMake.html
[DBCSR]: https://cp2k.github.io/dbcsr/develop/
[SIRIUS]: https://github.com/electronic-structure/SIRIUS
[COSMA]: https://github.com/eth-cscs/COSMA
[dftd4]: https://dftd4.readthedocs.io/en/latest/ 
[libint]: https://github.com/evaleev/libint
[PLUMED]: https://www.plumed.org
[ELPA]: https://elpa.mpcdf.mpg.de
[spla]: https://github.com/eth-cscs/spla
[Spglib]: https://spglib.readthedocs.io/en/stable/
[Libxc]: https://libxc.gitlab.io
[FFTW]: https://www.fftw.org
[ScaLAPACK]: https://www.netlib.org/scalapack/
[OpenBLAS]: http://www.openmathlib.org/OpenBLAS/
[Intel MKL]: https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html
[Cray MPICH]: https://docs.nersc.gov/development/programming-models/mpi/cray-mpich/
[slurm]: https://slurm.schedmd.com/
[CUDA MPS]: https://docs.nvidia.com/deploy/mps/index.html
