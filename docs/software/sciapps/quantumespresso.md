[](){#ref-uenv-quantumespresso}
# Quantum ESPRESSO

[Quantum ESPRESSO](https://www.quantum-espresso.org/) is an integrated suite of Open-Source computer codes for electronic-structure calculations and materials modeling at the nanoscale. It is based on density-functional theory, plane waves, and pseudopotentials:

* `pw.x`: Plane-Wave Self-Consistent Field (PWscf)
* `pw.x` First Principles Molecular Dynamics (FPMD)
* `cp.x` Car-Parrinello (CP)


!!! note "uenvs"

    [Quantum ESPRESSO](https://www.quantum-espresso.org/) is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.


## How to run

The following sbatch script can be used as a template.

=== "GH200"

    ```bash
    #SBATCH -N 1
    #SBATCH --ntasks-per-node=4
    #SBATCH --cpus-per-task=71
    #SBATCH --gpus-per-task=1
    #SBATCH -A <account>
    #SBATCH --uenv=quantumespresso/v7.4:v2
    #SBATCH --view=default

    export OMP_NUM_THREADS=20
    export MPICH_GPU_SUPPORT_ENABLED=1
    export OMP_PLACES=cores

    srun -u --cpu-bind=socket /user-environment/env/default/bin/pw.x < pw.in
    ```
    Current observation is that best perfomance is achieved using [one MPI rank per GPU][ref-slurm-gh200-single-rank-per-gpu]. How to run multiple ranks per GPU is described [here][ref-slurm-gh200-multi-rank-per-gpu].

=== "Eiger"

    ```bash
    #SBATCH -N 1
    #SBATCH --ntasks-per-node=128
    #SBATCH -A <account>
    #SBATCH --uenv=quantumespresso/v7.3.1
    #SBATCH --view=default
    #SBATCH --hint=nomultithread

    export OMP_NUM_THREADS=1

    srun -u /user-environment/env/default/bin/pw.x < pw.in
    ```


## Building QE from Source

### Using modules

=== "GH200"

    ```bash
    uenv start --view=modules quantumespresso/v7.4:v2
    module load cmake \
        fftw \
        nvhpc \
        nvpl-lapack \
        nvpl-blas \
        cray-mpich \
        netlib-scalapack \
        libxc

    mkdir build && cd build
    FC=mpif90 CXX=mpic++ CC=mpicc cmake .. \
        -DQE_ENABLE_MPI=ON \
        -DQE_ENABLE_OPENMP=ON \
        -DQE_ENABLE_SCALAPACK:BOOL=OFF \
        -DQE_ENABLE_LIBXC=ON \
        -DQE_ENABLE_CUDA=ON \
        -DQE_ENABLE_PROFILE_NVTX=ON \
        -DQE_CLOCK_SECONDS:BOOL=OFF \
        -DQE_ENABLE_MPI_GPU_AWARE:BOOL=OFF \
        -DQE_ENABLE_OPENACC=ON
    make -j20
    ```

=== "A100"

    ```bash
    uenv start --view=modules quantumespresso/v7.3.1:v2
    module load cmake \
        cray-mpich
        cuda \
        fftw \
        gcc \
        libxc \
        nvhpc \
        openblas
    mkdir build && cd build
    FC=mpif90 CXX=mpic++ CC=mpicc cmake .. \
        -DQE_ENABLE_MPI=ON \
        -DQE_ENABLE_OPENMP=ON \
        -DQE_ENABLE_SCALAPACK:BOOL=OFF \
        -DQE_ENABLE_LIBXC=ON \
        -DQE_ENABLE_CUDA=ON \
        -DQE_CLOCK_SECONDS:BOOL=OFF \
        -DQE_ENABLE_MPI_GPU_AWARE:BOOL=OFF \
        -DQE_ENABLE_OPENACC=ON
    make -j20
    ```

### Using spack

1. Clone spack using the same version that has been used to build the uenv.
```bash
uenv start quantumespresso/v7.3.1
# clone the same spack version as has been used to build the uenv
git clone -b $(jq -r .spack.commit /user-environment/meta/configure.json) $(jq -r .spack.repo /user-environment/meta/configure.json) $SCRATCH/spack
```

2. Activate spack with the uenv configured as upstream
```bash
# ensure spack is using the uenv as upstream repository (always required)
export SPACK_SYSTEM_CONFIG_PATH=/user-environment/config
# active spack (always required)
. $SCRATCH/spack/share/spack/setup-env.sh
```

3. Create an anonymous environment for QE
```bash
spack env create -d $SCRATCH/qe-env
spack -e $SCRATCH/qe-env add quantum-espresso%nvhpc +cuda
spack -e $SCRATCH/qe-env config add packages:all:prefer:cuda_arch=90
spack -e $SCRATCH/qe-env develop -p /path/to/your/QE-src quantum-espresso@=develop
spack -e $SCRATCH/qe-env concretize -f
```
Check the output of `spack concretize -f`. All dependencies should have been picked up from spack upstream, marked eiter by a green `[^]` or `[e]`.
Next we create a local filesystem view, this instructs spack to create symlinks for binaries and libraries in a local directory `view`.
```bash
spack -e $SCRATCH/qe-env env view enable view
spack -e $SCRATCH/qe-env install
```
To recompile QE after editing the source code re-run `spack -e $SCRATCH/qe-env install`.

4. Run `pw.x` using the filesystem view generated in 3.
```bash
uenv start quantumespresso/v7.3.1
MPICH_GPU_SUPPORT_ENABLED=1 srun [...] $SCRATCH/qe-env/view/bin/pw.x < pw.in
```

!!! warning
    The `pw.x` is linked to the uenv, it won't work without activating the uenv, also it will only work with the exact same version of the uenv. 

!!! warning
    The physical installation path is in `$SCRATCH/spack`, deleting this directory will leave the anonymous spack environment created in 3. with dangling symlinks.




