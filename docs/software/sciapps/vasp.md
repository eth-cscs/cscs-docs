[](){#ref-uenv-vasp}
# VASP

!!! info ""
    VASP is [supported software][ref-support-apps] on Alps.
    See the [main applications page][ref-software] for more information.

The Vienna Ab initio Simulation Package ([VASP]) is a computer program for atomic scale materials modelling, e.g. electronic structure calculations and quantum-mechanical molecular dynamics, from first principles.

!!! note "uenvs"
    [VASP] is provided on [Alps][platforms-on-alps] via [uenv][ref-uenv], with two views:

    * `vasp`: includes the precompiled `vasp_std`, `vasp_ncl` and `vasp_gam` executables.
    * `develop`: includes only the dependencies required to build VASP from source.

    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

!!! note "Licensing terms and conditions"
    Access to VASP is restricted to users who have purchased a license from VASP Software GmbH.
    CSCS cannot provide free access to the code, and has to provide VASP Software GmbH with an updated list of users.

    Once you have a license, submit a request on the [CSCS service desk](https://jira.cscs.ch/plugins/servlet/desk), with a copy of your license, to be added to the `vasp6` unix group.
    Membership of the `vasp6` group grants access to the precompiled VASP executables and library files in the `vasp` uenv.

    Because of these restrictions, the VASP images cannot be pulled in the same way as other uenv: follow the guide to [accessing restricted software][ref-uenv-restricted-software].

    Please refer to the [VASP web site](https://www.vasp.at) for more information about licensing.

[](){#ref-uenv-vasp-daint}
## VASP on Daint

### Running VASP

To load the VASP uenv on [Daint][ref-cluster-daint]:

```bash title="load the vasp view"
uenv start vasp/v6.6.1:v1 --view=vasp
```

The `vasp_std`, `vasp_ncl` and `vasp_gam` executables are now available for use.
Loading the uenv can also be directly done inside of a Slurm script.

```bash title="Slurm script for running VASP on a single node"
#!/bin/bash -l

#SBATCH --job-name=vasp
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=16
#SBATCH --gpus-per-task=1
#SBATCH --uenv=vasp/v6.6.1:v1
#SBATCH --view=vasp
#SBATCH --account=<ACCOUNT>
#SBATCH --partition=normal

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun vasp_std
```

!!! note
    It's recommended to use the Slurm option `--gpus-per-task=1`, since VASP may fail to properly assign ranks to GPUs when running on more than one node.
    This is not required when using the CUDA MPS wrapper for oversubscription of GPUs.

!!! note
    Since v6.6.0, the VASP uenv views on Daint enable the AWS NCCL plugin, which should provide better multi-node performance.
    See the [NCCL documentation][ref-communication-nccl] for more information.

[](){#ref-uenv-vasp-daint-mps}
### Multiple tasks per GPU

Using more than one task per GPU is possible with VASP and may lead to better GPU utilization.
However, VASP relies on [NCCL] for efficient communication, but falls back to MPI when using multiple tasks per GPU.
In many cases, this drawback is the greater factor and it's best to use one task per GPU.

To run with multiple tasks per GPU, a wrapper script is required to start a CUDA MPS service.
This script can be found at [NVIDIA GH200 GPU nodes: multiple ranks per GPU][ref-slurm-gh200-multi-rank-per-gpu].

```bash title="Slurm script for running VASP on a single node with two tasks per GPU"
#!/bin/bash -l

#SBATCH --job-name=vasp
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=16
#SBATCH --uenv=vasp/v6.6.1:v1
#SBATCH --view=vasp
#SBATCH --account=<ACCOUNT>
#SBATCH --partition=normal

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

srun ./mps-wrapper.sh vasp_std
```

[](){#ref-uenv-vasp-daint-build}
### Building VASP from source

To build VASP from source, the `develop` view must first be loaded:

```bash title="load the develop view"
uenv start vasp/v6.6.1:v1 --view=develop
```

All required dependencies can now be found in `/user-environment/env/develop`.
Note that shared libraries might not be found when executing VASP, if the makefile does not include additional rpath linking options or `LD_LIBRARY_PATH` has not been extended.

!!! warning
    The detection of MPI CUDA support does not work properly with Cray MPICH.
    After compiling from source, it's also required to set `export PMPI_GPU_AWARE=1` at runtime to disable the CUDA support check within VASP.
    Alternatively, since version 6.5.0, the build option `-DCRAY_MPICH` can be added to disable the check at compile time.
    The provided precompiled binaries of VASP are patched and do not require special settings.

Examples for makefiles that set the necessary rpath and link options on GH200, to be copied to `makefile.include` in the VASP source directory:

??? note "Makefile for v6.6.0 / v6.6.1"
    ```make
    --8<-- "docs/software/sciapps/vasp_makefiles/v6.6.0"
    ```

??? note "Makefile for v6.5.1"
    ```make
    --8<-- "docs/software/sciapps/vasp_makefiles/v6.5.1"
    ```

??? note "Makefile for v6.5.0"
    ```make
    --8<-- "docs/software/sciapps/vasp_makefiles/v6.5.0"
    ```

??? note "Makefile for v6.4.3"
    ```make
    --8<-- "docs/software/sciapps/vasp_makefiles/v6.4.3"
    ```

[](){#ref-uenv-vasp-eiger}
## VASP on Eiger

### Running VASP

The optimal setting for running VASP on CPU depends on the workload, but usually involves setting OpenMP related environment variables and using a mixture of MPI and multi-threading.
An example to run on [Eiger][ref-cluster-eiger] on two nodes:

```bash title="Slurm script for running VASP on Eiger"
#!/bin/bash -l
#SBATCH --job-name=vasp
#SBATCH --time=24:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-core=1
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=8
#SBATCH --account=<ACCOUNT>
#SBATCH --hint=nomultithread
#SBATCH --hint=exclusive
#SBATCH --constraint=mc
#SBATCH --uenv=vasp/v6.6.1:v1
#SBATCH --view=vasp

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

ulimit -s unlimited
srun --cpu-bind=cores vasp_std
```

!!! note
    OpenBLAS may spawn an extra thread, therefore it can be beneficial in some cases to set `OMP_NUM_THREADS` to `$((SLURM_CPUS_PER_TASK - 1))` for improved performance.

[](){#ref-uenv-vasp-eiger-build}
### Building VASP from source

On Eiger, the `makefile.include.gnu_omp` file provided with the VASP source can be used directly if `FFTW_ROOT` is set to point to the develop view location at `/user-environment/env/develop`.
You may also want to add optional dependencies like HDF5.

```bash title="load the develop view and set FFTW_ROOT"
uenv start vasp/v6.6.1:v1 --view=develop
export FFTW_ROOT=/user-environment/env/develop
```

[VASP]: https://vasp.at/
[NCCL]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html
