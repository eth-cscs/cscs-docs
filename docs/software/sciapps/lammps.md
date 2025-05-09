[](){#ref-uenv-lammps}
# LAMMPS

[LAMMPS] is a classical molecular dynamics code that models an ensemble of particles in a liquid, solid, or gaseous state.
It can model atomic, polymeric, biological, metallic, granular, and coarse-grained systems using a variety of force fields and boundary conditions. 
The current version of LAMMPS is written in C++.

!!! note "uenvs"
    [LAMMPS](https://www.lammps.org/) is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

## Licensing Terms and Conditions

??? note "Licensing terms and conditions"
    [LAMMPS] is a freely-available open-source code, distributed under the terms of the [GNU Public License](http://www.gnu.org/copyleft/gpl.html).

## Running  LAMMPS

### Loading LAMMPS Interactively

On Alps, LAMMPS is precompiled and available in a user environment [uenv]. 
LAMMPS has been built with kokkos, and the GPU package separately.

To find which LAMMPS uenv is provided, you can use the following command:

```
uenv image find lammps
```

which will list several uenv lammps uenv images. 
We recommend that you regularly check for the latest version.
Please see the documentation here for further details: https://eth-cscs.github.io/cscs-docs/software/uenv/#finding-uenv.

To obtain this image, please run:

```bash
uenv image pull lammps/2024:v2
```

To start the uenv for this specific version of LAMMPS, you can use:

```bash
uenv start --view kokkos lammps/2024:v2
```

You can load the `view` from the uenv which contains the `lmp` executable. The executable in both these views support GPUs:

```bash
#lammps +kokkos packae
uenv start --view kokkos lammps/2024:v2
#lammps +gpu package, kokkos disabled
uenv start --view gpu lammps/2024:v2
```

A development view is also provided, which contains all libraries and command-line tools necessary to build LAMMPS from source, without including the LAMMPS executable:

```bash
# build environment for lammps +kokkos package, without providing lmp executable
uenv start --view develop-kokkos lammps/2024:v2
# build environment for lammps +gpu package, without providing lmp executable
uenv start --view develop-gpu lammps/2024:v2
```

### Running LAMMPS with Kokkos on the HPC Platform

To start  a job, two bash scripts are potentially required: a [SLURM] submission script, and a wrapper for `numactl` which sets up CPU and memory binding.

The submission script is the following:

```bash title="run_lammps_kokkos.sh"
#!/bin/bash -l
#SBATCH --job-name=<JOB_NAME>
#SBATCH --time=01:00:00 (1)
#SBATCH --nodes=2                                                                        
#SBATCH --ntasks-per-node=4  (2)
#SBATCH --gres=gpu:4
#SBATCH --account=<ACCOUNT> (3)
#SBATCH --uenv=<LAMMPS_UENV>:/user-environment (4)
#SBATCH --view=kokkos (5)

export MPICH_GPU_SUPPORT_ENABLED=1
 
ulimit -s unlimited
 
srun ./wrapper.sh lmp -in lj_kokkos.in -k on g 1 -sf kk -pk kokkos gpu/aware on
```

1. Time format: `HH:MM:SS`.
2. For LAMMPS+kokkos its typical to only use 1 MPI-rank per GPU.
3. Change `<ACCOUNT>` to your project account name.
4. Change `<LAMMPS_UENV>` to the name (or path) of the LAMMPS uenv you want to use.
5. Load the `kokkos` uenv view.

the `numactl` wrapper is the following:

```bash title="wrapper.sh"
#!/bin/bash

export LOCAL_RANK=$SLURM_LOCALID
export GLOBAL_RANK=$SLURM_PROCID
export GPUS=(0 1 2 3)
export NUMA_NODE=$(echo "$LOCAL_RANK % 4" | bc)
export CUDA_VISIBLE_DEVICES=${GPUS[$NUMA_NODE]}

export MPICH_GPU_SUPPORT_ENABLED=1
 
numactl --cpunodebind=$NUMA_NODE --membind=$NUMA_NODE "$@"
```

With the above scripts, you can launch a LAMMPS+kokkos calculation on 2 nodes, using 4 MPI ranks per node and 4 GPUs per node with:

```bash
sbatch run_lammps_kokkos.sh
```

You may need to make the `wrapper.sh` script executable (`chmod +x wrapper.sh`).

#### LAMMPS + kokkos input file
??? example "LAMMPS+kokkos input file, defining a 3d Lennard-Jones melt."
    ```
    variable        x index 200
    variable        y index 200
    variable        z index 200
    variable        t index 1000

    variable        xx equal 1*$x
    variable        yy equal 1*$y
    variable        zz equal 1*$z

    variable        interval equal $t/2

    units           lj
    atom_style      atomic/kk

    lattice         fcc 0.8442
    region          box block 0 ${xx} 0 ${yy} 0 ${zz}
    create_box      1 box
    create_atoms    1 box
    mass            1 1.0

    velocity        all create 1.44 87287 loop geom

    pair_style      lj/cut/kk 2.5
    pair_coeff      1 1 1.0 1.0 2.5

    neighbor        0.3 bin
    neigh_modify    delay 0 every 20 check no

    fix             1 all nve

    thermo          ${interval}
    thermo_style custom step time  temp press pe ke etotal density
    run_style       verlet/kk
    run             $t
    ```

### Running LAMMPS+GPU on the HPC Platform

To start a job, two bash scripts are required: a [Slurm][ref-slurm] submission script, and a wrapper for `numactl` which sets up CPU and memory binding.

```bash title="run_lammps_gpu.sh"
#!/bin/bash -l
#SBATCH --job-name=<JOB_NAME>
#SBATCH --time=01:00:00 (1)
#SBATCH --nodes=2                                                                        
#SBATCH --ntasks-per-node=32 (2)
#SBATCH --gres=gpu:4
#SBATCH --account=<ACCOUNT> (3)                                                                  
#SBATCH --uenv=<LAMMPS_UENV>:/user-environment (4)
#SBATCH --view=gpu (5)

export MPICH_GPU_SUPPORT_ENABLED=1
 
ulimit -s unlimited

srun ./mps-wrapper.sh lmp -sf gpu -pk gpu 4 -in lj.in
```

To enable oversubscription of MPI ranks per GPU, you'll need to use the `mps-wrapper.sh` script provided at the following page: [NVIDIA GH200 GPU nodes: multiple ranks per GPU][ref-slurm-gh200-multi-rank-per-gpu]

1. Time format: `HH:MM:SS`.
2. For LAMMPS+gpu its often beneficial to use more than 1 MPI rank per GPU.
3. Change `<ACCOUNT>` to your project account name.
4. Change `<LAMMPS_UENV>` to the name (or path) of the LAMMPS uenv you want to use.
5. Load the `gpu` uenv view.

#### LAMMPS + kokkos input file

Below is the input file used in the above script, defining a 3d Lennard-Jones melt.

```
# 3d Lennard-Jones melt
variable        x index 200
variable        y index 200
variable        z index 200
variable        t index 1000

variable        xx equal 1*$x
variable        yy equal 1*$y
variable        zz equal 1*$z

variable        interval equal $t/2

units           lj
atom_style      atomic

lattice         fcc 0.8442
region          box block 0 ${xx} 0 ${yy} 0 ${zz}
create_box      1 box
create_atoms    1 box
mass            1 1.0

velocity        all create 1.44 87287 loop geom

pair_style      lj/cut 2.5
pair_coeff      1 1 1.0 1.0 2.5

neighbor        0.3 bin
neigh_modify    delay 0 every 20 check no

fix             1 all nve

thermo          ${interval}
thermo_style custom step time  temp press pe ke etotal density
run_style       verlet
run             $t
```

### Running on Eiger

!!! TODO !!!

### Building LAMMPS from source

#### Using CMake

If you'd like to rebuild LAMMPS from source to add additional packages or to use your own customized code, you can use the develop views contained within the uenv image to provide you with all the necessary libraries and command-line tools you'll need.
For the following, we'd recommend obtaining an interactive node and building inside the tmpfs directory.

```bash
salloc -N1 -t 60 -A <account>
srun --pty bash
mkdir /dev/shm/lammps_build; cd /dev/shm/lammps_build
```

After you've obtained a version of LAMMPS you'd like to build, extract it in the above temporary folder and create a build directory. 
Load one of the two following views:

```
#build environment for lammps +kokkos package, without providing lmp executeable
uenv start --view develop-kokkos lammps/2024:v2-rc1
#build environment for lammps +gpu package, without providing lmp executeable
uenv start --view develop-gpu lammps/2024:v2-rc1
```

and now you can build your local copy of LAMMPS. 
For example to build with kokkos and the `MOLECULE` package enabled:

```
CC=mpicc CXX=mpic++ cmake \
-DCMAKE_CXX_FLAGS=-DCUDA_PROXY \
-DBUILD_MPI=yes\
-DBUILD_OMP=no \
-DPKG_MOLECULE=yes \
-DPKG_KOKKOS=yes \
-DEXTERNAL_KOKKOS=yes \
-DKokkos_ARCH_NATIVE=yes \
-DKokkos_ARCH_HOPPER90=yes \
-DKokkos_ARCH_PASCAL60=no \
-DKokkos_ENABLE_CUDA=yes \
-DKokkos_ENABLE_OPENMP=yes \
-DCUDPP_OPT=no \
-DCUDA_MPS_SUPPORT=yes \
-DCUDA_ENABLE_MULTIARCH=no \
../cmake  
```

!!! `Warning` !!!

If you are downloading LAMMPS from GitHub or their website and intend to use kokkos for acceleration, there is an issue with Cray MPICH and `kokkos <= 4.3`. 
For LAMMPS to work correctly on our system, you need a LAMMPS version which provides `kokkos >= 4.4`. 
Alternatively, the CMake variable `-DEXTERNAL_KOKKOS=yes` should force CMake to use the kokkos version provided by the uenv, rather than the one contained within the lammps distribution.

#### Using LAMMPS uenv as an upstream Spack Instance

If you'd like to extend the existing uenv with additional packages (or your own), you can use the provide LAMMPS uenv to provide all dependencies needed to build your customization. See https://eth-cscs.github.io/alps-uenv/uenv-compilation-spack/ for more information.

First, set up an environment:

```
uenv start --view develop-gpu lammps/2024:v2

git clone -b v0.23.0 https://github.com/spack/spack.git
source spack/share/spack/setup-env.sh
export SPACK_SYSTEM_CONFIG_PATH=/user-environment/config/
```

Then create the path and file `$SCRATCH/custom_env/spack.yaml`. We'll disable the KOKKOS package (and enable the GPU package via +cuda spec), and add the CG-SPICA package (via the +cg-spica spec) as an example. You can get the full list of options on [the LAMMPS spack package overview](https://packages.spack.io/package.html?name=lammps).

```
spack:
  specs:
  - lammps@20240417 ~kokkos +cuda cuda_arch=90 +python +extra-dump +cuda_mps +cg-spica
  packages:
    all:
      prefer:
        - +cuda cuda_arch=90
    mpi:
      require: cray-mpich +cuda
  view: true
  concretizer:
    unify: true
```

Then concretize and build (note, you will of course be using a different path):

```
spack -e $SCRATCH/custom_env/ concretize -f
spack -e $SCRATCH/custom_env/ install
```

During concretization, you'll notice a hash being printed alongside the LAMMPS package name. Take note of this hash. If you now try to load LAMMPS:

```
# naively try to load  LAMMPS 
# it shows two versions installed (the one in the uenv, and the one we just built)
spack load lammps
==> Error: lammps matches multiple packages.
  Matching packages:
    rd2koe3 lammps@20240207.1%gcc@12.3.0 arch=linux-sles15-neoverse_v2
    zoo2p63 lammps@20240207.1%gcc@12.3.0 arch=linux-sles15-neoverse_v2
  Use a more specific spec (e.g., prepend '/' to the hash).
# use the hash thats listed in the output of the build
# and load using the hash
spack load /zoo2p63
# check the lmp executable:
which lmp
/capstor/scratch/cscs/browning/SD-61924/spack/opt/spack/linux-sles15-neoverse_v2/gcc-12.3.0/lammps-20240417-zoo2p63rzyuleogzn4a2h6yj7u3vhyy2/bin/lmp
```

You should now see that the CG-SPICA package in the list of installed packages:

```
> lmp -h
...
Installed packages:

CG-SPICA GPU KSPACE MANYBODY MOLECULE PYTHON RIGID
```

## Scaling

!!! TODO !!!

[LAMMPS]: https://www.lammps.org
[GNU Public License]: http://www.gnu.org/copyleft/gpl.html
[uenv]: https://eth-cscs.github.io/cscs-docs/software/uenv
[SLURM]: https://eth-cscs.github.io/cscs-docs/running/slurm