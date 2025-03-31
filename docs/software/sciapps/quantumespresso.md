[](){#ref-uenv-quantumespresso}
# Quantum ESPRESSO

Quantum ESPRESSO is an integrated suite of Open-Source computer codes for electronic-structure calculations and materials modeling at the nanoscale. It is based on density-functional theory, plane waves, and pseudopotentials:

PWscf (Plane-Wave Self-Consistent Field)
FPMD (First Principles Molecular Dynamics)
CP (Car-Parrinello)

## ALPS (GH200)
### Setup
Download the uenv image for QuantumESPRESSO:


### List available images

```bash
uenv image find quantumespresso
```

### Pull the image of interest

```
uenv image pull quantumespresso/v7.4:v2
```


QuantumESPRESSO can be compiled from source using the above uenv. The procedure is described in https://eth-cscs.github.io/alps-uenv/uenv-qe/#building-a-custom-version.

### How to run

=== "GH200"
Either run uenv start quantumespresso/v7.4  and then submit the job or set --uenv  sbatch option accordingly. The following sbatch script can be used as a template.

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

=== "Eiger"
Either run uenv start quantumespresso/v7.4  and then submit the job or set --uenv  sbatch option accordingly. The following sbatch script can be used as a template.

```bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH -A <account>
#SBATCH --uenv=quantumespresso/v7.4:v2
#SBATCH --view=default
#SBATCH --hint=nomultithread

export OMP_NUM_THREADS=1

srun -u /user-environment/env/default/bin/pw.x < pw.in
```

