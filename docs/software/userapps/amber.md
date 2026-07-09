[](){#ref-software-amber}
# Amber

!!! warning ""
    Amber is [user software][ref-support-user-apps] on Alps.
    This guide is provided based on our experiences helping users --- however we can't provide the same level of support as we do for [supported software][ref-support-apps].
    See the [main applications page][ref-software] for more information.

    Amber provides many options and tools.
    The process shown here builds a representative CUDA + MPI configuration for Grace-Hopper --- you may have to modify the CMake options to build the exact set of tools you need.

[Amber](https://ambermd.org) is a suite of programs for molecular dynamics simulation of biomolecular systems such as proteins, nucleic acids, and small molecules.
It is widely used in computational chemistry and structural biology, with strong GPU acceleration support through its PMEMD engine.

!!! note
    This page documents how to download and install **Amber26**, which can be freely downloaded and used for non-commercial academic use cases.
    Older versions had different license terms that stop CSCS from accessing the source.

The instructions provided here are for building Amber on [daint][ref-cluster-daint] with Grace-Hopper (GH200) support.

## Overview

Because CSCS cannot redistribute Amber (see [Licensing](#getting-amber) below), we provide a **uenv** that contains everything needed to *build* Amber, and you build it yourself.
The workflow has three steps:

1. **Pull the `amber/26.6` uenv** --- provides the compiler, CUDA, Python and libraries.
2. **Download and extract the Amber source** --- you agree to the license and download it yourself.
3. **Build Amber** with the provided script, then test it.

The whole build takes roughly 1 to 2 hours on a single Grace-Hopper node.

## The Amber uenv

!!! under-construction
    CSCS currently provides release candidate `rcN` versions of the amber uenv --- this will be a properly tagged and released version once it has been validated.

The `amber/26.6` [uenv][ref-uenv] provides the compilers and libraries needed to build both CPU-only and CUDA-enabled installations on the [gh200][ref-alps-gh200-node] nodes of [daint][ref-cluster-daint].
It provides, in a single view called `amber`:

* **CUDA 12.8** --- the most recent version of CUDA supported by Amber26.
* **GCC 12.5** --- the most recent non-deprecated GCC compatible with CUDA 12.8.
* **Python 3.12** with `tkinter` --- compatible with all of the Python packages used by Amber, plus every Python package Amber checks for at build time (numpy, scipy, matplotlib, pandas, numba, gemmi, biopython, rich, scikit-learn, sympy, pydantic, psutil, networkx, mpi4py, freesasa, f90nml, ...).
* **cray-mpich** (CUDA-aware) and optimised **FFTW, netCDF, HDF5, OpenBLAS, GSL**.

You do **not** need to install any Python packages by hand --- everything Amber's build looks for is already in the view.

!!! example "Downloading the `amber/26.6` uenv"

    ```console
    $ uenv image find amber
    uenv          arch   system  id                size(MB)  date
    amber/26.6:rc2  gh200  daint   ...                ...       ...
    $ uenv image pull amber/26.6:rc2
    ```

!!! example "Starting the `amber/26.6` uenv"
    The `amber/26.6` uenv must be loaded with the **`amber` view** both when building and when running Amber.

    ```console
    $ uenv start --view=amber amber/26.6:rc2
    $ uenv status
    amber:/user-environment
      An environment for building Amber26. Does not include Amber.
      views:
        spack: configure spack upstream
        amber (loaded):
    ```

    If you frequently use the tools interactively, consider creating an alias for a [custom environment][ref-uenv-customenv] that loads the uenv and also sets `AMBERHOME`.

## Getting Amber

!!! info "Licensing"
    Amber is distributed under a dual license, with free access for non-profit academic users, and paid licenses for commercial use.
    CSCS is not permitted to redistribute Amber binaries or source code.
    Instead, users must independently agree to the license terms, then download the source and compile Amber themselves.

    Users are responsible for following the terms of the license that they agree to when applying for access on the Amber web site.

A full Amber installation consists of **AmberTools** and **Amber (PMEMD)**, which are downloaded as two separate archives from the [Amber website](https://ambermd.org/GetAmber.php) --- see the "How to obtain AmberTools26" and "How to obtain Amber26" sections.
You have to enter your name and institution; if you agree to the non-commercial terms the download starts immediately.

After downloading you will have two files:

| file                  | description                 |
| --------------------- | --------------------------- |
| `ambertools26.tar.bz2`| source code for AmberTools  |
| `pmemd26.tar.bz2`     | source code for Amber/PMEMD |

??? example "Copying the Amber sources to Daint"
    We assume you have SSH set up as described in [Using SSH][ref-ssh].

    ```console
    $ ssh daint 'mkdir -p ~/ambersources'
    $ scp ambertools26.tar.bz2 pmemd26.tar.bz2 daint:~/ambersources
    ```

## Extracting the source

!!! tip "Where to build"
    Building generates a large number of files.
    Build on a fast file system with plenty of space --- your [Scratch][ref-storage-scratch] is a good choice.
    Install the result into your [Store][ref-storage-store] path (e.g. `export AMBERHOME=$STORE/amber26`) if you want everyone in your group to be able to use it.

Choose a directory to unpack the sources into, and set `AMBER_ROOT` to point at it:

```bash title="extract the source archives"
# choose a build location on scratch
export AMBER_ROOT=$SCRATCH/amber
mkdir -p $AMBER_ROOT
cd $AMBER_ROOT

# copy and extract the two archives (extraction takes a few minutes)
cp $HOME/ambersources/*.tar.bz2 .
tar -xjf ambertools26.tar.bz2
tar -xjf pmemd26.tar.bz2
```

After extraction `$AMBER_ROOT` contains the two source trees:

```
$AMBER_ROOT/ambertools26_src/     # AmberTools
$AMBER_ROOT/pmemd26_src/          # Amber / PMEMD
```

!!! note "Checking for updates (optional)"
    Amber periodically releases patches.
    You can check for and apply them before building.
    Review what the updater will do before applying it --- applied updates change your source tree.

    ```bash
    uenv start --view=amber amber/26.6:rc2
    cd $AMBER_ROOT/ambertools26_src && ./update_amber --check-updates
    cd $AMBER_ROOT/pmemd26_src      && ./update_pmemd --check-updates
    # apply with: ./update_amber --update   and   ./update_pmemd --update
    ```

## Building Amber

Download the build script [`build-amber.sh`](scripts/build-amber.sh) (also reproduced below), make it executable, and run it inside the uenv.
It builds **AmberTools** first and then **Amber/PMEMD**, installing both into a single `$AMBERHOME`.

```bash title="build Amber (MPI + CUDA, for GH200)"
# 1. start the uenv with the amber view
uenv start --view=amber amber/26.6:rc2

# 2. point at your extracted sources (from the previous step)
export AMBER_ROOT=$SCRATCH/amber

# 3. build. 'gpu' = MPI + CUDA (default); 'cpu' = serial/OpenMP, no CUDA.
#    Installs into $AMBER_ROOT/amber26 by default (override with AMBERHOME).
./build-amber.sh gpu
```

!!! tip "Build CPU-only first if you are debugging"
    The CPU-only build (`./build-amber.sh cpu`) is faster and is a good way to check that the
    basic toolchain works before committing to the longer MPI+CUDA build.
    Both configurations install into the same `$AMBERHOME`, so you can run the script twice.

The script sets the following important options for you:

* `-DCMAKE_Fortran_FLAGS=-fPIC` --- **required** on Grace-Hopper (works around a `COMMON` block size limit).
* `-DDOWNLOAD_MINICONDA=false` --- never let Amber install its own conda; the Amber conda environment contains ~115,000 files and will hammer a shared file system, so the uenv provides Python and all packages instead.
* `-DBUILD_PYTHON=on` --- use the uenv's Python and packages.
* `-DBUILD_QUICK=off` --- the Quick QM engine's GPU build takes hours, so remove this from the script only if you need Quick.
* `-DCHECK_UPDATES=false` --- don't contact the network during configure (apply updates explicitly, as above).

When it finishes, the install directory `$AMBERHOME/bin` contains the PMEMD executables, including:

| executable            | description                                  |
| --------------------- | -------------------------------------------- |
| `pmemd`               | serial CPU engine                            |
| `pmemd.MPI`           | MPI CPU engine                               |
| `pmemd.cuda`          | single-GPU engine (SPFP precision)           |
| `pmemd.cuda.MPI`      | multi-GPU / multi-node engine                |
| `sander`, `sander.MPI`| the AmberTools MD engine                     |

??? example "Contents of `build-amber.sh`"
    ```bash
    --8<-- "docs/software/userapps/scripts/build-amber.sh"
    ```

## Testing the build

Activate the installation and run a short simulation on a GPU to confirm everything works.
`amber.sh` sets `AMBERHOME` and puts the Amber tools on your `PATH`.

```bash title="single-GPU smoke test"
uenv start --view=amber amber/26.6:rc2
source $AMBER_ROOT/amber26/amber.sh      # sets AMBERHOME + PATH

# use the small GB test case shipped with the sources
cd $(mktemp -d)
cp $AMBER_ROOT/pmemd26_src/test/cuda/gb_ala3/{prmtop,inpcrd} .
cat > mdin <<'EOF'
GB smoke test
 &cntrl
  imin=0, irest=1, ntx=5, nstlim=20, dt=0.002, ntb=0,
  ntf=2, ntc=2, ntpr=5, cut=9999.0, rgbmax=9999.0,
  igb=1, ntt=0, ig=71277,
 /
EOF
pmemd.cuda -O -i mdin -p prmtop -c inpcrd -o out
grep "GPU IN USE" out            # -> "NVIDIA GPU IN USE"
grep -A2 "CUDA Device Name" out  # -> "NVIDIA GH200 120GB"
```

A successful run prints `Final Performance Info` at the end of `out`.

The [`test-amber.sh`](scripts/test-amber.sh) script automates this check.
It runs the single-GPU test above and, if `srun` and more than one GPU are available, a short multi-GPU run as well.

```bash title="run the smoke test"
export AMBERHOME=$AMBER_ROOT/amber26
export PMEMD_SRC=$AMBER_ROOT/pmemd26_src
./test-amber.sh
```

??? example "Contents of `test-amber.sh`"
    ```bash
    --8<-- "docs/software/userapps/scripts/test-amber.sh"
    ```

!!! note "IEEE floating-point notes are harmless"
    PMEMD often prints `Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG`.
    This is expected and does not indicate a failed run.

## Running simulations

Load the uenv with the `amber` view in your batch script and launch the GPU engine with `srun`.
Each MPI rank uses one GPU; the [gh200][ref-alps-gh200-node] nodes have 4 GPUs.

```bash title="submit.sh — 1 node, 4 GPUs"
#!/bin/bash
#SBATCH --job-name=amber
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --time=01:00:00
#SBATCH --uenv=amber/26.6:rc2
#SBATCH --view=amber

source $SCRATCH/amber/amber26/amber.sh

srun pmemd.cuda.MPI -O -i mdin -p prmtop -c inpcrd -o mdout -r restrt -x mdcrd
```

!!! tip "One GPU is often fastest"
    For many systems a single GPU (`pmemd.cuda`, `--ntasks-per-node=1 --gpus-per-node=1`) is faster than multi-GPU, because PMEMD is highly optimised for one GPU.
    Multi-GPU (`pmemd.cuda.MPI`) helps for large systems; it uses direct GPU peer-to-peer communication, which is enabled on the GH200 nodes.

    `pmemd.cuda.MPI` requires the system to have at least **32× more atoms than MPI ranks** --- very small test systems will abort with `Must have 32x more atoms than processors!` when run on multiple ranks.

## Advanced notes

!!! note
    These notes are for CSCS staff and adventurous users who want to update or modify the `amber` uenv.
    See the recipe's `README.md` and `lessons.md` for the full build history.

Installing *only* Amber against externally provided dependencies is awkward because Amber:

* vendors dependencies such as boost (and, with MPI, fftw) into its source tree and builds its own copies if it does not find suitable ones;
* by default installs a conda environment, which it then uses to install Python packages (~115k files).

The `amber/26.6` uenv was configured to avoid this:

* CUDA 12.8 is the most recent CUDA supported by Amber26, which forces GCC ≤ 12 (GCC 12.5 is the newest non-deprecated GCC compatible with it in Spack).
* Python is pinned to 3.12 --- the most recent Python compatible with every package Amber uses, and it is built `+tkinter` (required by Amber, not the default in the `prgenv` uenv).
* Every Python package that Amber's `cmake/PythonBuildConfig.cmake` checks for is included in the view.
    Two packages that are not in Spack --- `freesasa` and `f90nml` --- are `pip`-installed into the view by the recipe's `post-install` script.
    `f90nml` in particular is `pip install`-ed unconditionally by `AmberTools/src/PyPE_RESP/setup.py` at build time, so providing it in the uenv prevents a read-only-filesystem failure.

Remaining opportunities for a future version:

* Amber rebuilds its own boost, and its own fftw when building with MPI, instead of using the optimised copies in the uenv --- each dependency taken from the uenv would speed up the build and reduce warning noise.
* Amber tracks a few years behind current package versions; pinning older CMake/Python could reduce warnings further.
