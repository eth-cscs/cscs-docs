[](){#ref-uenv-gromacs}
# GROMACS

[GROMACS] (GROningen Machine for Chemical Simulations) is a versatile and widely-used open source package to perform molecular dynamics, i.e. simulate the Newtonian equations of motion for systems with hundreds to millions of particles.

It is primarily designed for biochemical molecules like proteins, lipids and nucleic acids that have a lot of complicated bonded interactions, but since GROMACS is extremely fast at calculating the nonbonded interactions (that usually dominate simulations) many groups are also using it for research on non-biological systems, e.g. polymers.

!!! note "uenvs"

    [GROMACS] is provided on [Alps][ref-alps-platforms] via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

## Licensing terms & conditions

GROMACS is a joint effort, with contributions from developers around the world: users agree to acknowledge use of GROMACS in any reports or publications of results obtained with the Software (see [GROMACS Homepage](https://www.gromacs.org/about.html) for details).

## Key features

1. **Molecular Dynamics Simulations**: GROMACS performs classical MD simulations, which compute the trajectories of atoms based on Newton's laws of motion. It integrates the equations of motion to simulate the behavior of molecular systems, capturing their dynamic properties and conformational changes.

2. **Force Fields**: GROMACS supports a wide range of force fields, including CHARMM, AMBER, OPLS-AA, and GROMOS, which describe the potential energy function and force interactions between atoms. These force fields provide accurate descriptions of the molecular interactions, allowing researchers to study various biological processes and molecular systems.

3. **Parallelization and Performance**: GROMACS is designed for high-performance computing (HPC) and can efficiently utilize parallel architectures, such as multi-core CPUs and GPUs. It employs domain decomposition methods and advanced parallelization techniques to distribute the computational workload across multiple computing resources, enabling fast and efficient simulations.

4. **Analysis and Visualization**: GROMACS offers a suite of analysis tools to extract and analyze data from MD simulations. It provides functionalities for computing properties such as energy, temperature, pressure, radial distribution functions, and free energy landscapes. GROMACS also supports visualization tools, allowing users to visualize and analyze the trajectories of molecular systems.

5. **User-Friendly Interface**: GROMACS provides a command-line interface (CLI) and a set of well-documented input and control files, making it accessible to both novice and expert users. It offers flexibility in defining system parameters, simulation conditions, and analysis options through easily modifiable input files.

6. **Integration with Other Software**: GROMACS can be integrated with other software packages and tools to perform advanced analysis and extend its capabilities. It supports interoperability with visualization tools like VMD and PyMOL, analysis packages like GROMACS Analysis Tools (GROMACS Tools) and MDAnalysis, and scripting languages such as Python, allowing users to leverage a wide range of complementary tools.

## Daint on Alps (GH200)

### Setup

On Alps, we provide pre-built user environments containing GROMACS alongside all the required dependencies for the GH200 hardware setup. To access the `gmx_mpi` executable, we do the following:

```bash
uenv image find 							  # list available images

uenv image pull gromacs/VERSION:TAG.          # copy version:tag from the list above
uenv start gromacs/VERSION:TAG --view=gromacs # load the gromacs view

gmx_mpi --version                             # check GROMACS version
```

The images also provide two alternative views, namely `plumed` and `develop`.

```console
$ uenv status
/user-environment:gromacs-gh200
  GPU-optimised GROMACS with and without PLUMED, and the toolchain to build your own GROMACS.
  modules: no modules available
  views:
    develop
    gromacs
    plumed
```

The `develop` view has all the required dependencies or GROMACS without the program itself. This is meant for those users who want to use a customized variant of GROMACS for their simulation which they build from source. This view makes it convenient for users as it provides the required compilers (GCC) along with the dependencies such as CMake, CUDA, hwloc, Cray MPICH, among many others which their GROMACS can use during build and installation. Users must enable this view each time they want to use their **custom GROMACS installation**.

The `plumed` view contains GROMACS patched with PLUMED. The version of GROMACS in this view may be different from the one in the `gromacs` view due to the compatibility requirements of PLUMED. CSCS will periodically update these user environment images to feature newer versions as they are made available.

The `gromacs` view contains GROMACS 2024.1 that has been configured and tested for the highest performance on the Grace-Hopper nodes.

Use `exit` to leave the user environment and return to the original shell.

### How to run

To start a job, 2 bash scripts are required: a standard SLURM submission script, and a [wrapper to start the CUDA MPS daemon][ref-slurm-gh200-single-rank-per-gpu] (in order to have multiple MPI ranks per GPU).

The wrapper script above needs to be made executable with `chmod +x mps-wrapper.sh`.
 
The SLURM submission script can be adapted from the template below to use the application and the `mps-wrapper.sh` in conjunction.

```bash title="launch.sbatch"
#!/bin/bash

#SBATCH --job-name="JOB NAME"
#SBATCH --nodes=1             # number of GH200 nodes with each node having 4 CPU+GPU
#SBATCH --ntasks-per-node=8   # 8 MPI ranks per node
#SBATCH --cpus-per-task 32    # 32 OMP threads per MPI rank
#SBATCH --account=ACCOUNT
#SBATCH --hint=nomultithread  
#SBATCH --uenv=<GROMACS_UENV>
#SBATCH --view=gromacs

export MPICH_GPU_SUPPORT_ENABLED=1
export FI_CXI_RX_MATCH_MODE=software

export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true
export GMX_FORCE_UPDATE_DEFAULT_GPU=true
export GMX_ENABLE_DIRECT_GPU_COMM=1
export GMX_FORCE_GPU_AWARE_MPI=1

srun ./mps-wrapper.sh gmx_mpi mdrun -s input.tpr -ntomp 32 -bonded gpu -nb gpu -pme gpu -pin on -v -noconfout -dlb yes -nstlist 300 -gpu_id 0123 -npme 1 -nsteps 10000 -update gpu
```

This can be run using `sbatch launch.sbatch` on the login node with the user environment loaded.

This submission script is only representative. Users must run their input files with a range of parameters to find an optimal set for the production runs. Some hints for this exploration below:

!!! note "Configuration hints"

	- Each Grace CPU has 72 cores, but a small number of them are used for the underlying processes such as runtime daemons. So all 72 cores are not available for compute. To be safe, do not exceed more than 64 OpenMP threads on a single CPU even if it leads to a handful of cores idling.
	- Each node has 4 Grace CPUs and 4 Hopper GPUs. When running 8 MPI ranks (meaning two per CPU), keep in mind to not ask for more than 32 OpenMP threads per rank. That way no more than 64 threads will be running on a single CPU.
	- Try running both 64 OMP threads x 1 MPI rank and 32 OMP threads x 2 MPI ranks configurations for the test problems and pick the one giving better performance. While using multiple GPUs, the latter can be faster by 5-10%.
	- `-update gpu` may not be possible for problems that require constraints on all atoms. In such cases, the update (integration) step will be performed on the CPU. This can lead to performance loss of at least 10% on a single GPU. Due to the overheads of additional data transfers on each step, this will also lead to lower scaling performance on multiple GPUs.
	- When running on a single GPU, one can either configure the simulation with 1-2 MPI ranks with `-gpu_id` as `0`, or try running the simulation with a small number of parameters and let GROMACS run with defaults/inferred parameters with a command like the following in the SLURM script:
	`srun ./mps-wrapper.sh -- gmx_mpi mdrun -s input.tpr -ntomp 64`
	- Given the compute throughput of each Grace-Hopper module (single CPU+GPU), **for smaller-sized problems, it is possible that a single-GPU run is the fastest**. This may happen when the overheads of domain decomposition, communication and orchestration exceed the benefits of parallelism across multiple GPUs. In our test cases, a single Grace-Hopper module (1 CPU+GPU) has consistently shown a 6-8x performance speedup over a single node on Piz Daint (Intel Xeon Broadwell + P100).
	- Try runs with and without specifying the GPU IDs explicitly with `-gpu_id 0123`. For the multi-node case, removing it might yield the best performance.

## Scaling

Benchmarking is done with large MD simulations of systems of 1.4 million and 3 million atoms, in order to fully saturate the GPUs, from the [HECBioSim Benchmark Suite](https://www.hecbiosim.ac.uk/access-hpc/benchmarks).

In addition, the STMV (~1 million atom) benchmark that NVIDIA publishes on its [website](https://developer.nvidia.com/hpc-application-performance) was also tested for comparison. 

The STMV test case is a fairly large problem size, with constraints operating only on a smaller set of atoms (h-bonds) which allows the update step to also take place on GPUs. This makes the simulation almost **fully GPU resident** with the key performance intensive bits namely the long-range forces (PME), short-range non-bonded forces (NB) and bonded forces all running on the GPU. On a single node, this leads to the following scaling on GROMACS 2024.1.

#### STMV - Multiple ranks - Single node up to 4 GPUs

| #GPUs  | ns/day  | Speedup |
| ------ | ------- | ------- |
| 1      |  42.855 | 1x      |
| 2      |  61.583 | 1.44x   |
| 4      | 115.316 | 2.69x   |
| 8      | 138.896 | 3.24x   |

The other benchmark cases from HECBioSim simulates a pair of proteins (hEGFR Dimers/Tetramers of [1IVO](https://www.rcsb.org/structure/1IVO) and [1NQL](https://www.rcsb.org/structure/1NQL)) with a large lipid membrane. This also involves a fairly large number of charged ions which increases the proportion of PME in the total compute workload. For these simulations, constraints are applicable on all atoms, which effectively **prevents the update from happening in the GPU**, thus negatively impacting scaling due large host-to-device data transfers and key computations happening on the CPU. These show the following scaling characteristics on GROMACS 2024.1:

#### 1.4m Atom System - Multiple ranks - Single node

Total number of atoms = 1,403,182

Protein atoms = 43,498  Lipid atoms = 235,304  Water atoms = 1,123,392  Ions = 986

| #GPUs  | ns/day  | Speedup |
| ------ | ------- | ------- |
| 1      |  31.243 | 1x      |
| 4      |  55.936 | 1.79x   |

#### 3m Atom System - Single node - Multiple ranks

Total number of atoms = 2,997,924

Protein atoms = 86,996  Lipid atoms = 867,784  Water atoms = 2,041,230  Ions = 1,914

| #GPUs  | ns/day  | Speedup |
| ------ | ------- | ------- |
| 1      |  14.355 | 1x      |
| 4      |  30.289 | 2.11x   |

!!! warning "Known Performance/Scaling Issues"

	- The currently provided build of GROMACS allows **only one MPI rank to be dedicated for PME** with `-nmpe 1`. This becomes a serious performance limitation for larger systems where the non-PME ranks finish their work before the PME rank leading to unwanted load imbalances across ranks. This limitation is targeted to be fixed in the subsequent releases of our builds of user environments.
	- The above problem is especially critical for large problem sizes (1+ million atom systems) but is far less apparent in small and medium sized runs.
	- If the problem allows the integration step to take place on the GPU with `-update gpu`, that can lead to significant performance and scaling gains as it allows an even greater part of the computations to take place on the GPU.
	- A single node of the GH200 cluster offers 4x CPU+GPU. For problems that can benefit from scaling beyond a single node, use the flag `export FI_CXI_RX_MATCH_MODE=software` in the SBATCH script. The best use of resources in terms of node-hours might be achieved on a single node for most simulations.

### Building GROMACS from Source

The [GROMACS] uenv provides all the dependencies required to build GROMACS from source, with several optional features enabled. This approach is particularly useful for deploying customized variants of GROMACS. You can follow these steps to build GROMACS from source:

```bash
uenv start --view=develop <GROMACS_UENV> # (1)!

cd <PATH_TO_GROMACS_SOURCE> # (2)!

mkdir build && cd build
cmake \
	-DCMAKE_C_COMPILER=gcc \
	-DCMAKE_CXX_COMPILER=g++ \
	-DGMX_MPI=on \
	-DGMX_GPU=CUDA \
	-GMX_CUDA_TARGET_SM="90" \ # for the Hopper GPUs
	-DGMX_SIMD=ARM_NEON_ASIMD \ # for the Grace CPUs
	-DGMX_DOUBLE=off \ # turn on double precision only if useful
	-DCMAKE_INSTALL_PREFIX=/custom/gromacs/install/path
	..

make
make check
make install
source /custom/gromacs/install/path/bin/GMXRC
```

1. Start the GROMACS uenv and load the `develop` view (which provides all the necessary dependencies)

2. Go to the GROMACS source directory

See [GROMACS Installation Guide] for more details, especially on special configurations.

## Further documentation 

* [GROMACS Homepage][GROMACS]
* [GROMACS Manual](https://manual.gromacs.org/2024.1/index.html)

[GROMACS]: https://www.gromacs.org
[GROMACS Installation Guide]: https://manual.gromacs.org/current/install-guide/index.html
