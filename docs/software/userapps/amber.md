[](){#ref-software-amber}
# Amber

!!! warning ""
    Amber is [user software][ref-support-user-apps] on Alps.
    This guide is provided based on our experiences helping users -- however we can't provide the same level of support as we do for [supported software][ref-support-apps].
    See the [main applications page][ref-software] for more information.

[Amber](https://ambermd.org) is a suite of programs for molecular dynamics simulation of biomolecular systems such as proteins, nucleic acids, and small molecules.
It is widely used in computational chemistry and structural biology, with strong GPU acceleration support through its PMEMD engine.

!!! note
    This page documents how to download and install Amber26, which can be freely downloaded and used for non-commercial academic use cases.
    Older versions had different license terms, that stop CSCS from accessing the source.

## Getting Amber

!!! info "Licensing"
    Amber is distributed under a dual license, with free access for non-profit academic users, and paid licenses for commercial use.
    CSCS is not permitted to redistribute Amber binaries or source code, instead users have to independently agree to the license term, then download the source and compile Amber themselves.

    Users are responsible for following the terms of the licensing terms that they agree to when applying for access on the Amber web site.

A full Amber installation will include both AmberTools and Amber, which are downloaded as separate tar balls.
Both packages are distributed from the [Amber website](https://ambermd.org/GetAmber.php) (see the "How to obtain AmberTools26" and "How to obtain Amber26" sections respectively), where you have to enter your name and institution for each 
If you agree to the non-commercial terms, the download will start immediately.

After downloading, the following two files will have been downloaded:

| file                  | description                 |
| ----                  | -----------                 |
| `ambertools26.tar.bz2`| source code for AmberTools  |
| `pmemd26.tar.bz2`     | source code for Amber/PMEMD |

Which need to be copied to Alps.

!!! example "copying Amber sources to Daint"
    Use ssh to create a remoted directory, and scp to copy the Amber source files to the directory.
    ```console
    $ ssh daint 'mkdir -p ~/ambersource'
    $ scp *.tar.bz2 daint:~/ambersource
    ```

## Building Amber

The `amber/26` uenv provides the compilers and libraries needed to build both a CPU-only and a CUDA-enabled installation.

!!! example "Downloading the amber/26 uenv"

    **these docs are draft, and we currently use a `build::` version of the amber uenv - this will be a properly tagged and released version once it has been validated**

    ```console
    $ uenv image find build::amber
    uenv                 arch   system  id                size(MB)  date
    amber/26:2567560372  gh200  daint   c32e5cda1c6a961e   9,125    2026-06-01
    $ uenv image pull build::amber/26:2567560372
    pulling c32e5cda1c6a961e 100.00% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9126/9126 (742.62 MB/s)
    updating amber/26:2567560372@daint%gh200
    ```

After downloading the Amber source archive `pmemd26.tar.bzw`, extract both into the same directory and set the `AMBER_ROOT` environment variable:

```bash title="extract the source archives"
# create a directory where we will unpack and compile the sources
mkdir amber
cd amber
export AMBER_ROOT=$(pwd)

# copy the source code tar balls to this directory and extract them
# extracting the tar balls takes minutes
cp $HOME/ambersources/*.tar.bz2 .
tar -xjf ambertools26.tar.bz2
tar -xjf pmemd26.tar.bz2
export AMBERTOOLS_SRC=$AMBER_ROOT/ambertools26_src
export AMBER_SRC=$AMBER_ROOT/pmemd26_src
```

```bash
#
# configure the build (set to on and off as need be)
#
amber_mpi=on
amber_cuda=on
amber_openmp=off
export AMBERHOME=$AMBER_ROOT/amber

#
# create build paths
#

AMBERTOOLS_BUILD=$AMBER_ROOT/build-ambertools
AMBER_BUILD=$AMBER_ROOT/build-amber
rm -rf $AMBERTOOLS_BUILD $AMBER_BUILD
mkdir $AMBERTOOLS_BUILD $AMBER_BUILD

#
# build ambertools
#

cd $AMBERTOOLS_BUILD
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME -DCOMPILER=GNU \
      -DMPI=$amber_mpi -DCUDA=$amber_cuda -DOPENMP=$amber_openmp \
      -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=true \
      $AMBERTOOLS_SRC
make -j64
make install

cd $AMBERS_BUILD
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME -DCOMPILER=GNU \
      -DMPI=$amber_mpi -DCUDA=$amber_cuda -DOPENMP=$amber_openmp \
      -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=false \
      -DPMEMD_ONLY=true \
      $AMBER_SRC
make -j64
make install

#
# build amber
#

```


```
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME/cpu -DCOMPILER=GNU -DMPI=true -DCUDA=false -DOPENMP=true -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=true -DPMEMD_ONLY=true $AMBERSRC
```

## Advanced Notes

!!! note
    These notes are for CSCS staff and adventurous users who want to update or modify the `amber` uenv.

Installing Amber is challenging if you want to build only Amber, and have it use dependencies provided via a uenv/container/Spack environment, because Amber:

* vendors dependencies like boost into its source tree, and builds them if they are not found in the calling env
* installs conda which is, in turn, used to install Python packages.

We want to avoid this, because it will greatly increas the build time of Amber, and lead to the creation of many small files.

!!! warning
    The Conda environment installed by the Amber CMake workflow contains 115,000 inodes, which will murder a distributed filesystem.

A specific uenv was configured because of the following requirements:

* CUDA 12.8 is the most recent version of CUDA supported by Ambewr26.
* GCC 12.5 is the most recent non-deprecated version of GCC that is compatible with CUDA 12.8.
* Python with [tkinter](https://docs.python.org/3/library/tkinter.html) support is required by Amber (i.e. `python +tkinter`), which is not the default configuration installed in the `prgenv` uenv.

The Amber CMake configuration will use versions of required Python packages that are installed on the system, if it can find them during configuration.
We add all required Python packages to the uenv environment.

One of the dependencies, [`freesasa`](https://pypi.org/project/freesasa/) is not available in Spack, so we install it separately in a `post-install` script.

### CPU build

A CPU-only build is suitable for serial pre-processing and post-processing tasks, and for MPI-parallel runs on [Eiger][ref-cluster-eiger].
Start the `prgenv-gnu` uenv and configure the build:

First build with MINICONDA download

```bash title="configure and build (CPU + MPI)"
uenv start --view=default prgenv-gnu/25.11:v1

cd $AMBERHOME
mkdir build && cd build
# build with no python
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME/cpu
    -DCOMPILER=GNU
    -DMPI=TRUE -DCUDA=FALSE -DOPENMP=TRUE
    -DBUILD_PYTHON=FALSE
    -DDOWNLOAD_MINICONDA=FALSE
    -DPMEMD_ONLY=FALSE
    $AMBERSRC
# build with conda python
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME/cpu
    -DCOMPILER=GNU
    -DMPI=TRUE -DCUDA=FALSE -DOPENMP=TRUE
    -DBUILD_PYTHON=TRUE
    -DDOWNLOAD_MINICONDA=TRUE
    -DPMEMD_ONLY=FALSE
    $AMBERSRC
# build with uv python
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME/cpu
    -DCOMPILER=GNU
    -DMPI=TRUE -DCUDA=FALSE -DOPENMP=TRUE
    -DBUILD_PYTHON=TRUE
    -DDOWNLOAD_MINICONDA=TRUE
    -DPMEMD_ONLY=FALSE
    $AMBERSRC
make -j32
make install
```

!!! note
    The `-DPMEMD_ONLY=false` flag is required to build without Amber Tools.


To run
```
export PMEMDHOME=$AMBERHOME/cpu
export PATH=$PMEMDHOME/bin:$PATH
export LD_LIBRARY_PATH=$PMEMDHOME/lib:$LD_LIBRARY_PATH
```

### GPU build

A CUDA-enabled build is required to run PMEMD on GPU nodes such as those on [Daint][ref-cluster-daint].
Use the same `prgenv-gnu` uenv and pass `-DCUDA=TRUE`:

```bash title="configure and build (CUDA + MPI)"
uenv start prgenv-gnu/24.11:v2 --view=default

cd $AMBERHOME
mkdir build-cuda && cd build-cuda
cmake .. \
    -DCMAKE_INSTALL_PREFIX=$AMBERHOME \
    -DCOMPILER=GNU \
    -DMPI=TRUE \
    -DCUDA=TRUE \
    -DOPENMP=TRUE
make -j$(nproc) install
```

!!! info "Check the Amber build documentation"
    The exact CMake flags required may vary between Amber releases.
    Consult `$AMBERHOME/doc/` or the [Amber reference manual](https://ambermd.org/Manuals.php) if you encounter build errors.

## Running Amber

### GPU job on Daint

PMEMD with CUDA is the recommended engine for production runs.
Below is a single-node GPU job script for [Daint][ref-cluster-daint]:

```bash title="single-node GPU job"
#!/bin/bash -l
#SBATCH --job-name=amber_gpu
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --account=<ACCOUNT>
#SBATCH --uenv=prgenv-gnu/24.11:v2
#SBATCH --view=default

export AMBERHOME=/path/to/amber25_src  # modify this accordingly
export PATH="$AMBERHOME/bin:$PATH"

mpirun -np 4 pmemd.cuda.MPI \
    -O \
    -i mdin \
    -o mdout \
    -p prmtop \
    -c inpcrd \
    -r restrt \
    -x mdcrd
```

### CPU job on Eiger

```bash title="MPI job on Eiger"
#!/bin/bash -l
#SBATCH --job-name=amber_cpu
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --account=<ACCOUNT>
#SBATCH --constraint=mc
#SBATCH --uenv=prgenv-gnu/24.11:v2
#SBATCH --view=default

export AMBERHOME=/path/to/amber25_src  # modify this accordingly
export PATH="$AMBERHOME/bin:$PATH"

srun pmemd.MPI \
    -O \
    -i mdin \
    -o mdout \
    -p prmtop \
    -c inpcrd \
    -r restrt \
    -x mdcrd
```
