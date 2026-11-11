# NAMD

> [!NOTE]
>
> NAMD is [supported software](<https://docs.cscs.ch/policies/support/index.md#officially-supported-applications> "Officially Supported Applications") on Alps. See the [main applications page](<https://docs.cscs.ch/software/index.md#applications-and-frameworks> "Applications and frameworks") for more information.

[NAMD](<http://www.ks.uiuc.edu/Research/namd/>) is a parallel molecular dynamics code based on [Charm++](<https://charm.cs.uiuc.edu/>), designed for high-performance simulations of large biomolecular systems.

> [!CAUTION]
>
> **Licensing Terms and Conditions**
>
> [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) is distributed free of charge for research purposes only and not for commercial use: users must agree to the [NAMD license](<http://www.ks.uiuc.edu/Research/namd/license.html>) in order to use it at [CSCS](<https://www.cscs.ch>). Users agree to acknowledge use of [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) in any reports or publications of results obtained with the Software (see [NAMD Homepage](<http://www.ks.uiuc.edu/Research/namd/>) for details).

> [!NOTE]
>
> **User Environments**
>
> [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) is provided on [ALPS](<https://docs.cscs.ch/alps/platforms/index.md#platforms-on-alps> "Platforms on Alps") as a uenv. Please have a look at the [uenv documentation](<https://docs.cscs.ch/software/uenv/index.md#uenv>) for more information about UENVs and how to use them.

[NAMD](<http://www.ks.uiuc.edu/Research/namd/>) is provided in two flavours on [CSCS](<https://www.cscs.ch>) systems:

- Single-node build
- Multi-node build

The single-node build works on a single node and benefits from the new GPU-resident mode (see [NAMD 3.0b6 GPU-Resident benchmarking results](<https://www.ks.uiuc.edu/Research/namd/benchmarks/>) for more details). The multi-node build works on multiple nodes and is based on [Charm++](<https://charm.cs.uiuc.edu/>)’s MPI backend.

> [!NOTE]
>
> **Prefer the single-node build and exploit GPU-resident mode**
>
> Unless you have good reasons to use the multi-node build, we recommend using the single-node build with the GPU-resident mode.

> [!WARNING]
>
> **Eiger**
>
> The multi-node version is the only version of NAMD available on [Eiger](<https://docs.cscs.ch/clusters/eiger/index.md#eiger>) - single-node is not provided.

> [!NOTE]
>
> **Changelog**
>
> > **3.0.2:v1**
> >
> > - Updated CUDA from 12.4 to 12.9
> > - Disabled Adaptive MPI (AMPI) in Charm++

## Single-node build

The single-node build provides the following views:

- `namd-single-node` (standard view, with NAMD)
- `develop-single-node` (development view, without NAMD)

### Running NAMD on a single node

The following sbatch script shows how to run NAMD on a single node with 4 GPUs:

```bash
#!/bin/bash
#SBATCH --job-name="namd-example"
#SBATCH --time=00:10:00
#SBATCH --account=<ACCOUNT>          (6)
#SBATCH --nodes=1                    (1)
#SBATCH --ntasks-per-node=1          (2)
#SBATCH --cpus-per-task=288
#SBATCH --gres=gpu:4                 (3)
#SBATCH --uenv=<NAMD_UENV>           (4)
#SBATCH --view=namd-single-node      (5)


srun namd3 +p 29 +pmeps 5 +setcpuaffinity +devices 0,1,2,3 <NAMD_CONFIG_FILE> # (7)! 
```

1. You can only use one node with the `single-node` build
2. You can only use one task per node with the `single-node` build
3. Make all GPUs visible to NAMD (by automatically setting `CUDA_VISIBLE_DEVICES=0,1,2,3`)
4. Load the NAMD UENV (UENV name or path to the UENV). Change `<NAMD_UENV>` to the name (or path) of the actual NAMD UENV you want to use
5. Load the `namd-single-node` view
6. Change `<ACCOUNT>` to your project account
7. Make sure you set `+p`, `+pmeps`, and other NAMD options optimally for your calculation. Change `<NAMD_CONFIG_FILE>` to the name (or path) of the NAMD configuration file for your simulation

> [!NOTE]
>
> **Scaling of STMV benchmark with GPU-resident mode from 1 to 4 GPUs**
>
> Scaling of the tobacco mosaic virus (STMV) benchmark with GPU-resident mode on our system is the following:
>
> | GPUs | ns/day | Speedup | Parallel efficiency |
> | :---: | :---: | :---: | :---: |
> | 1 | 31.1 | \- | \- |
> | 2 | 53.7 | 1.9 | 86% |
> | 4 | 92.7 | 3.5 | 74% |
>
> ```bash
> srun namd3 +p 8 +setcpuaffinity +devices 0 <NAMD_CONFIG_FILE>
> ```
>
> ```bash
> srun namd3 +p 15 +pmeps 7 +setcpuaffinity +devices 0,1 <NAMD_CONFIG_FILE>
> ```
>
> ```bash
> srun namd3 +p 29 +pmeps 5 +setcpuaffinity +devices 0,1,2,3 <NAMD_CONFIG_FILE>
> ```

### Building NAMD from source with Charm++’s multicore backend

> [!WARNING]
>
> **Action required**
>
> According to the NAMD 3.0 release notes, TCL `8.6` is required. However, the source code for the `3.0` release still contains hard-coded flags for TCL `8.5`. The UENV provides `tcl@8.6`, therefore you need to manually modify NAMD 3.0’s `arch/Linux-ARM64.tcl` file as follows: change `-ltcl8.5` to `-ltcl8.6` in the definition of the `TCLLIB` variable.

The [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) `uenv` provides all the dependencies required to build [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) from source.

Build NAMD:

```bash
export DEV_VIEW_NAME="develop-single-node"
export PATH_TO_NAMD_SOURCE=<PATH_TO_NAMD_SOURCE>

# Start uenv and load develop view
uenv start --view=${DEV_VIEW_NAME} <NAMD_UENV>

# Set variable VIEW_PATH to the view
export DEV_VIEW_PATH=/user-environment/env/${DEV_VIEW_NAME}

cd ${PATH_TO_NAMD_SOURCE}
```

> [!NOTE]
>
> **Action required**
>
> Modify the `<PATH_TO_NAMD_SOURCE>/arch/Linux-ARM64.tcl` file now. Change `-ltcl8.5` with `-ltcl8.6` in the definition of the `TCLLIB` variable.

```bash
# Build bundled Charm++
tar -xvf charm-8.0.0.tar && cd charm-8.0.0
./build charm++ multicore-linux-arm8 gcc --with-production --enable-tracing -j 32

# Configure NAMD build for GPU
cd .. 
./config Linux-ARM64-g++.cuda \
    --charm-arch multicore-linux-arm8-gcc --charm-base $PWD/charm-8.0.0 \
    --with-tcl --tcl-prefix ${DEV_VIEW_PATH} \
    --with-fftw --with-fftw3 --fftw-prefix ${DEV_VIEW_PATH} \
    --cuda-gencode arch=compute_90,code=sm_90 --with-single-node-cuda --with-cuda --cuda-prefix ${DEV_VIEW_PATH}
cd Linux-ARM64-g++.cuda && make -j 32

# The namd3 executable (GPU-accelerated) will be built in the Linux-ARM64-g++.cuda directory
```

- Change `<PATH_TO_NAMD_SOURCE>` to the path where you have the NAMD source code
- Change `<NAMD_UENV>` to the name (or path) of the actual NAMD UENV you want to use

To run NAMD, make sure you load the same UENV and view you used to build NAMD, and set the following variable:

```bash
export LD_LIBRARY_PATH="${DEV_VIEW_PATH}/lib/"
```

Some workflows, such as constant pH MD simulations, might require a CPU-only NAMD build which is used to drive the simulation.

> [!WARNING]
>
> **Use the CPU-only build only if needed**
>
> The CPU-only build is optional and should be used only if needed. You should use it in conjunction with the GPU build to drive the simulation. Do not use the CPU-only build for actual simulations as it will be slower than the GPU build.

You can build a CPU-only version of NAMD as follows:

```bash
export DEV_VIEW_NAME="develop-single-node"
export PATH_TO_NAMD_SOURCE=<PATH_TO_NAMD_SOURCE>

# Start uenv and load develop view
uenv start --view=${DEV_VIEW_NAME} <NAMD_UENV>

# Set variable VIEW_PATH to the view
export DEV_VIEW_PATH=/user-environment/env/${DEV_VIEW_NAME}

cd ${PATH_TO_NAMD_SOURCE}
```

> [!NOTE]
>
> **Action required**
>
> Modify the `<PATH_TO_NAMD_SOURCE>/arch/Linux-ARM64.tcl` file now. Change `-ltcl8.5` with `-ltcl8.6` in the definition of the `TCLLIB` variable.

```bash
# Build bundled Charm++
tar -xvf charm-8.0.0.tar && cd charm-8.0.0
./build charm++ multicore-linux-arm8 gcc --with-production --enable-tracing -j 32

# Configure NAMD build for GPU
cd ..
./config Linux-ARM64-g++ \
    --charm-arch multicore-linux-arm8-gcc --charm-base $PWD/charm-8.0.0 \
    --with-tcl --tcl-prefix ${DEV_VIEW_PATH} \
    --with-fftw --with-fftw3 --fftw-prefix ${DEV_VIEW_PATH}
cd Linux-ARM64-g++ && make -j 32

# The namd3 executable (CPU-only) will be built in the Linux-ARM64-g++ directory
```

- Change `<PATH_TO_NAMD_SOURCE>` to the path where you have the NAMD source code

To run NAMD, make sure you load the same UENV and view you used to build NAMD, and set the following variable:

```bash
export LD_LIBRARY_PATH="${DEV_VIEW_PATH}/lib/"
```

## Multi-node build

The multi-node build provides the following views:

- `namd` (standard view, with NAMD)
- `develop` (development view, without NAMD)

> [!NOTE]
>
> **GPU-resident mode**
>
> The multi-node build based on [Charm++](<https://charm.cs.uiuc.edu/>)’s MPI backend can’t take advantage of the new GPU-resident mode. Unless you require the multi-node build or you can prove it is faster for your use case, we recommend using the single-node build with the GPU-resident mode.

### Running NAMD on Eiger

The following sbatch script shows how to run NAMD on Eiger:

```bash
#!/bin/bash -l
#SBATCH --job-name=namd-test
#SBATCH --time=00:30:00
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=8
#SBATCH --account=<ACCOUNT> (1)
#SBATCH --hint=nomultithread
#SBATCH --uenv=namd/3.0:v1 (2)
#SBATCH --view=namd (3)

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export PPN=$(($SLURM_CPUS_PER_TASK-1))

srun --cpu-bind=cores namd3 +setcpuaffinity +ppn ${PPN} <NAMD_CONFIG_FILE> # (4)!
```

1. Change `<ACCOUNT>` to your project account
2. Load the NAMD uenv (uenv label or path to the uenv)
3. Load the `namd` view
4. Each rank runs `+ppn` worker threads and one communication thread, so `+ppn` is `--cpus-per-task` minus 1. Make sure you set `+ppn`, and other NAMD options optimally for your calculation. Change `<NAMD_CONFIG_FILE>` to the name (or path) of the NAMD configuration file for your simulation

### Building NAMD from source with Charm++’s MPI backend

> [!WARNING]
>
> **TCL Version**
>
> According to the NAMD 3.0 release notes, TCL `8.6` is required. However, the source code for some (beta) releases still contains hard-coded flags for TCL `8.5`. The UENV provides `tcl@8.6`, therefore you need to manually modify NAMD’s `arch/Linux-<ARCH>.tcl` file: change `-ltcl8.5` to `-ltcl8.6` in the definition of the `TCLLIB` variable, if needed.

The [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) `uenv` provides all the dependencies required to build [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) from source. You can follow these steps to build [NAMD](<http://www.ks.uiuc.edu/Research/namd/>) from source:

```bash
export DEV_VIEW_NAME="develop"
export PATH_TO_NAMD_SOURCE=<PATH_TO_NAMD_SOURCE> # (1)!

# Start uenv and load develop view
uenv start --view=${DEV_VIEW_NAME} <NAMD_UENV> # (2)!

# Set variable VIEW_PATH to the view
export DEV_VIEW_PATH=/user-environment/env/${DEV_VIEW_NAME}

cd ${PATH_TO_NAMD_SOURCE}
```

1. Substitute `<PATH_TO_NAMD_SOURCE>` with the actual path to the NAMD source code
2. Substitute `<NAMD_UENV>` with the actual name (or path) of the NAMD UENV you want to use.

> [!NOTE]
>
> **Action required**
>
> Modify the `${PATH_TO_NAMD_SOURCE}/arch/Linux-ARM64.tcl` file now. Change `-ltcl8.5` with `-ltcl8.6` in the definition of the `TCLLIB` variable, if needed.

Build [Charm++](<https://charm.cs.uiuc.edu/>) bundled with NAMD:

```bash
tar -xvf charm-8.0.0.tar && cd charm-8.0.0
env MPICXX=mpicxx ./build charm++ mpi-linux-arm8 smp --with-production -j 32
```

Finally, you can configure and build NAMD (with GPU acceleration):

```bash
cd .. 
./config Linux-ARM64-g++.cuda \
    --charm-arch mpi-linux-arm8-smp --charm-base $PWD/charm-8.0.0 \
    --with-tcl --tcl-prefix ${DEV_VIEW_PATH} \
    --with-fftw --with-fftw3 --fftw-prefix ${DEV_VIEW_PATH} \
    --cuda-gencode arch=compute_90,code=sm_90 --with-single-node-cuda --with-cuda --cuda-prefix ${DEV_VIEW_PATH}
cd Linux-ARM64-g++.cuda && make -j 32
```

The `namd3` executable (GPU-accelerated) will be built in the `Linux-ARM64-g++.cuda` directory.

```bash
export DEV_VIEW_NAME="develop"
export PATH_TO_NAMD_SOURCE=<PATH_TO_NAMD_SOURCE> # (1)!

# Start uenv and load develop view
uenv start --view=${DEV_VIEW_NAME} <NAMD_UENV> # (2)!

# Set variable VIEW_PATH to the view
export DEV_VIEW_PATH=/user-environment/env/${DEV_VIEW_NAME}

cd ${PATH_TO_NAMD_SOURCE}
```

1. Substitute `<PATH_TO_NAMD_SOURCE>` with the actual path to the NAMD source code
2. Substitute `<NAMD_UENV>` with the actual name (or path) of the NAMD UENV you want to use.

> [!NOTE]
>
> **Action required**
>
> Modify the `${PATH_TO_NAMD_SOURCE}/arch/Linux-x86_64.tcl` file now. Change `-ltcl8.5` with `-ltcl8.6` in the definition of the `TCLLIB` variable, if needed.

Build [Charm++](<https://charm.cs.uiuc.edu/>) bundled with NAMD:

```bash
tar -xvf charm-8.0.0.tar && cd charm-8.0.0
env MPICXX=mpicxx ./build charm++ mpi-linux-x86_64 smp --with-production -j 32
```

Finally, you can configure and build NAMD:

```bash
cd .. 
./config Linux-x86_64-g++ \
    --charm-arch mpi-linux-x86_64-smp --charm-base $PWD/charm-8.0.0 \
    --with-tcl --tcl-prefix ${DEV_VIEW_PATH} \
    --with-fftw --with-fftw3 --fftw-prefix ${DEV_VIEW_PATH}
cd Linux-x86_64-g++ && make -j 32
```

The `namd3` executable will be built in the `Linux-x86_64-g++` directory.

To run NAMD, make sure you load the same UENV and view you used to build NAMD, and set the following variable:

```bash
export LD_LIBRARY_PATH="${DEV_VIEW_PATH}/lib/"
```

## Useful Links

- [NAMD Homepage](<http://www.ks.uiuc.edu/Research/namd/>)
- [NAMD Tutorials](<http://www.ks.uiuc.edu/Training/Tutorials/index.html#namd>)
- [Running Charm++ Programs](<https://charm.readthedocs.io/en/latest/charm++/manual.html#running-charm-programs>)
- [What you should know about NAMD and Charm++ but were hoping to ignore](<https://dl.acm.org/doi/pdf/10.1145/3219104.3219134>) by J. C. Phillips
- [NAMD Spack package](<https://packages.spack.io/package.html?name=namd>)
- [Charm++ Spack package](<https://packages.spack.io/package.html?name=charmpp>)
