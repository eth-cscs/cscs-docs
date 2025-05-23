[](){#ref-uenv-lammps}
# LAMMPS

[LAMMPS] is a classical molecular dynamics code that models an ensemble of particles in a liquid, solid, or gaseous state.
It can model atomic, polymeric, biological, metallic, granular, and coarse-grained systems using a variety of force fields and boundary conditions. 
The current version of LAMMPS is written in C++.

!!! note "uenvs"
    [LAMMPS](https://www.lammps.org/) is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.


??? note "Licensing terms and conditions"
    [LAMMPS] is a freely-available open-source code, distributed under the terms of the [GNU Public License](http://www.gnu.org/copyleft/gpl.html).

## Running LAMMPS

### Loading LAMMPS Interactively

On Alps, LAMMPS is precompiled and available in a [uenv][ref-uenv]. 
LAMMPS has been built with the [Kokkos](https://docs.lammps.org/Speed_kokkos.html) and GPU packages separately.

To find which LAMMPS uenv is provided, you can use the following command:

```
uenv image find lammps
```

which will list several available LAMMPS uenv images.
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

You can load the `kokkos` or `gpu` view from the uenv to make the `lmp` executable available.
The executable in both these views support GPUs:

=== "Kokkos"
    ```bash
    #lammps +kokkos package
    uenv start --view kokkos lammps/2024:v2
    ```
=== "GPU"
    ```bash
    #lammps +gpu package
    uenv start --view gpu lammps/2024:v2
    ```

A development view is also provided, which contains all libraries and command-line tools necessary to build LAMMPS from source, without including the LAMMPS executable:

=== "Kokkos"
    ```bash
    # build environment for lammps +kokkos package, without providing lmp executable
    uenv start --view develop-kokkos lammps/2024:v2
    ```
=== "GPU"
    ```bash
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
#SBATCH --gpus-per-node=4
#SBATCH --gpus-per-task=1
#SBATCH --gpu-bind=per_task:1
#SBATCH --account=<ACCOUNT> (3)
#SBATCH --uenv=<LAMMPS_UENV>:/user-environment (4)
#SBATCH --view=kokkos (5)

export MPICH_GPU_SUPPORT_ENABLED=1
 
ulimit -s unlimited
 
srun lmp -in lj_kokkos.in -k on g 1 -sf kk -pk kokkos gpu/aware on
```

1. Time format: `HH:MM:SS`.
2. For LAMMPS + Kokkos its typical to only use 1 MPI-rank per GPU.
3. Change `<ACCOUNT>` to your project account name.
4. Change `<LAMMPS_UENV>` to the name (or path) of the LAMMPS uenv you want to use.
5. Load the `kokkos` uenv view.

!!! Note
    Using `-k on g 1` specifies that we want 1 GPU per MPI-rank. 
    This is contrary to what is mentioned in the official LAMMPS documentation, however this is required to achieve the propper configuration on Alps.

With the above script, you can launch a LAMMPS + Kokkos calculation on 2 nodes, using 4 MPI ranks and 1 GPU per MPI rank with:

```bash
sbatch run_lammps_kokkos.sh
```

??? example "LAMMPS + Kokkos input file, defining a 3d Lennard-Jones melt."

    The following input file for LAMMPS + Kokkos defines a 3D Lennard-Jones system
    melt.
    
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

### Running LAMMPS + GPU on the HPC Platform

To start a job, two bash scripts are required: a [Slurm][ref-slurm] submission script, and a wrapper for [CUDA MPS][ref-slurm-gh200-multi-rank-per-gpu].

```bash title="run_lammps_gpu.sh"
#!/bin/bash -l
#SBATCH --job-name=<JOB_NAME>
#SBATCH --time=01:00:00 (1)
#SBATCH --nodes=2 (2)                                                                        
#SBATCH --ntasks-per-node=32
#SBATCH --gpus-per-node=4
#SBATCH --account=<ACCOUNT> (3)                                                       
#SBATCH --uenv=<LAMMPS_UENV>:/user-environment (4)
#SBATCH --view=gpu (5)

export MPICH_GPU_SUPPORT_ENABLED=1
 
ulimit -s unlimited

srun ./mps-wrapper.sh lmp -sf gpu -pk gpu 4 -in lj.in
```

1. Time format: `HH:MM:SS`.
2. For LAMMPS + GPU it is often beneficial to use more than 1 MPI rank per GPU. To enable oversubscription of MPI ranks per GPU, you'll need to use the `mps-wrapper.sh` script provided in the following section: [multiple ranks per GPU][ref-slurm-gh200-multi-rank-per-gpu].
3. Change `<ACCOUNT>` to your project account name.
4. Change `<LAMMPS_UENV>` to the name (or path) of the LAMMPS uenv you want to use.
5. Enable the `gpu` uenv view.

To enable oversubscription of MPI ranks per GPU, you'll need to use the `mps-wrapper.sh` script provided at the following page: [NVIDIA GH200 GPU nodes: multiple ranks per GPU][ref-slurm-gh200-multi-rank-per-gpu].
??? example "LAMMPS+GPU input file"

    The following input file for LAMMPS + GPU defines a 3D Lennard-Jones system
    melt.
    
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

On Eiger, the following sbatch script can be used:

```bash title="run_lammps_eiger.sh"
#!/bin/bash -l
#SBATCH --job-name=<JOB_NAME>
#SBATCH --time=01:00:00 (1)
#SBATCH --nodes=2                   
#SBATCH --ntasks-per-core=1                                                    
#SBATCH --ntasks-per-node=32 (2)
#SBATCH --cpus-per-task=4 (3) 
#SBATCH --account=<ACCOUNT> (4)
#SBATCH --hint=nomultithread
#SBATCH --hint=exclusive
#SBATCH --constraint=mc                                                  
#SBATCH --uenv=<LAMMPS_UENV>:/user-environment (5)
#SBATCH --view=kokkos (6)

ulimit -s unlimited

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PROC_BIND=spread
export OMP_PLACES=threads

srun --cpu-bind=cores lmp -k on t $OMP_NUM_THREADS -sf kk -in lj_kokkos.in
```

1. Time format: `HH:MM:SS`.
2. Number of MPI ranks per node.
3. Number of threads per MPI rank.
4. Change `<ACCOUNT>` to your project account name.
5. Change `<LAMMPS_UENV>` to the name (or path) of the LAMMPS uenv you want to use.
6. Enable the `kokkos` uenv view.

Note that the same input file `lj_kokkos.in` can be used as with running LAMMPS with Kokkos on the HPC Platform.

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

=== "Kokkos"
    ```bash
    #build environment for lammps +kokkos package, without providing lmp executable
    uenv start --view develop-kokkos lammps/2024:v2
    ```
=== "GPU"
    ```bash
    #build environment for lammps +gpu package, without providing lmp executable
    uenv start --view develop-gpu lammps/2024:v2
    ```

and now you can build your local copy of LAMMPS. 
For example to build with Kokkos and the `MOLECULE` package enabled:

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

!!! warning

    If you are downloading LAMMPS from GitHub or their website and intend to use Kokkos for acceleration, there is an issue with Cray MPICH and `Kokkos <= 4.3`. 
    For LAMMPS to work correctly on our system, you need a LAMMPS version which provides `Kokkos >= 4.4`. 
    Alternatively, the CMake variable `-DEXTERNAL_KOKKOS=yes` should force CMake to use the Kokkos version provided by the uenv, rather than the one contained within the lammps distribution.

#### Using LAMMPS uenv as an upstream Spack Instance

If you'd like to extend the existing uenv with additional packages (or your own), you can use the LAMMPS uenv to provide all dependencies needed to build your customization. See [here](https://eth-cscs.github.io/alps-uenv/tutorial-spack) for more information.

[LAMMPS]: https://www.lammps.org
[GNU Public License]: http://www.gnu.org/copyleft/gpl.html
[uenv]: https://eth-cscs.github.io/cscs-docs/software/uenv
[SLURM]: https://eth-cscs.github.io/cscs-docs/running/slurm