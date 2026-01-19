[](){#ref-software-orca}
# ORCA

!!! warning ""
    ORCA is [user software][ref-support-user-apps] on Alps.
    This guide is provided based on our experiences helping users -- however we can't provide the same level of support as we do for [supported software][ref-support-apps].
    See the [main applications page][ref-software] for more information.

[ORCA](https://www.faccts.de/orca/) is a quantum chemistry software package implementing a wide range of methods (DFT,
HF, wave-function methods, etc) with Gaussian basis sets.

It is used for CPU-only simulations on [Eiger][ref-cluster-eiger], for which this guide applies. Please do not 
use it on GPU platforms such as [Daint][ref-cluster-daint].

## Installation
You need to download the compiled executable yourself [here](https://www.faccts.de/customer). You first need to create a
user account, and make sure you fulfill the license requirements. Select the archive for the linux x86_64 architecture.
For ORCA v6.1.1, it is called `orca_6_1_1_linux_x86-64_shared_openmpi418_nodmrg.tar.xz`

Move the archive into your `$HOME` or `$PROJECT`, and unpack it in its own subfolder.

## Running ORCA calculations
ORCA is shipped as a pre-compiled executable linked against OpenMPI. To be able to run, the [`prgenv-gnu-openmpi`][ref-uenv-prgenv-gnu-openmpi]
uenv is required. Here is a sample Slurm batch script:

```bash
#!/bin/bash -l
#SBATCH --job-name=orca_job
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --account=<ACCOUNT>
#SBATCH --hint=nomultithread
#SBATCH --constraint=mc
#SBATCH --uenv=prgenv-gnu-openmpi/25.12:v1
#SBATCH --view=default

ORCA_PATH="absolute_path_to_orca_unpacked_directory" # modify this accordingly
export PATH="$PATH:$ORCA_PATH"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$ORCA_PATH"

ORCA_EXEC="$ORCA_PATH/orca"

$ORCA_EXEC water.inp > water.out
```

The number of MPI processes must be specified in the ORCA input file, and it should match the specifications of the
Slurm submission script. The example input file below (non-physical stack of water molecules with RI-MP2) matches 
the above sample script:

```bash
!RI-MP2 DEF2-QZVPP  DEF2-QZVPP/C
%PAL NPROCS 64  END
* xyz 0 1
O   0.0000   0.0000   0.0626
H  -0.7920   0.0000  -0.4973
H   0.7920   0.0000  -0.4973
O   0.0000   2.0000   0.0626
H  -0.7920   2.0000  -0.4973
H   0.7920   2.0000  -0.4973
O   0.0000   4.0000   0.0626
H  -0.7920   4.0000  -0.4973
H   0.7920   4.0000  -0.4973
O   0.0000   6.0000   0.0626
H  -0.7920   6.0000  -0.4973
H   0.7920   6.0000  -0.4973
O   0.0000   8.0000   0.0626
H  -0.7920   8.0000  -0.4973
H   0.7920   8.0000  -0.4973
O   0.0000  10.0000   0.0626
H  -0.7920  10.0000  -0.4973
H   0.7920  10.0000  -0.4973
O   0.0000  12.0000   0.0626
H  -0.7920  12.0000  -0.4973
H   0.7920  12.0000  -0.4973
*
```

!!! warning
    The ORCA executable is built with version 4 of OpenMPI, but the `prgenv-gnu-openmpi` uenv provides version 5. In
    principle, OpenMPI is backward compatible and everything should work. It is however possible that unforeseen issues
    arise when using methods that go beyond the simple testing we have done.
