[](){#ref-software-amber}
# Amber

!!! warning ""
    Amber is [user software][ref-support-user-apps] on Alps.
    This guide is provided based on our experiences helping users -- however we can't provide the same level of support as we do for [supported software][ref-support-apps].
    See the [main applications page][ref-software] for more information.

[Amber](https://ambermd.org) is a suite of programs for molecular dynamics simulation of biomolecular systems such as proteins, nucleic acids, and small molecules.
It is widely used in computational chemistry and structural biology, with strong GPU acceleration support through its PMEMD engine.

## License

Amber is commercial software distributed under a paid academic or commercial license.
CSCS is not permitted to redistribute Amber binaries or source code, so users must obtain a license independently and compile Amber themselves.

AmberTools, the companion package that includes many analysis and preparation utilities, is free and open source, and is required to build Amber.
Both packages are distributed from the [Amber website](https://ambermd.org/GetAmber.php), where you can register and purchase a license.

## Building Amber

Amber is built from source using CMake.
The [`prgenv-gnu`][ref-uenv-prgenv-gnu] uenv provides the compilers and libraries needed to build both a CPU-only and a CUDA-enabled installation.

After downloading the Amber source archive `pmemd26.tar.bzw`, extract both into the same directory and set the `AMBERHOME` environment variable:

```console title="extract the source archives"
$ mkdir amber
$ cd amber
$ tar -xjvf pmemd26.tar.bz2
$ export AMBERHOME=$PWD
$ export AMBERSRC=$AMBERHOME/pmemd26_src
```

### Set up Python

```
+ numpy
+ scipy
+ matplotlib
+ setuptools
+ pandas
+ numba
+ gemmi
- Bio
+ rich
- freesasa
+ scikit-learn
+ sympy
+ pydantic
+ psutil
+ networkx
```

https://packages.spack.io/package.html?name=freesasa

- this needs to be installed using Spack

```
export AMBERENV=$AMBERHOME/amberenv
uv venv $AMBERENV --python=$(which python)
source $AMBERENV/bin/activate
uv pip install -r requirements.txt
export PYTHONPATH=$AMBERENV/lib/python3.14/site-packages:$PATHONPATH
```

This fails during CMake configuration, because the tkinter Python is missing.
This package is part of Python, optionally configured with `python +tkinter` in Spack, which is missing in the version provided by the uenv.


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
