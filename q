[93mdiff --git a/docs/software/sciapps/lammps.md b/docs/software/sciapps/lammps.md[m
[93mindex 7bbc73c..9636643 100644[m
[93m--- a/docs/software/sciapps/lammps.md[m
[93m+++ b/docs/software/sciapps/lammps.md[m
[1;35m@@ -329,7 +329,114 @@[m [m[1;38;5;146mCC=mpicc CXX=mpic++ cmake \[m
 [m
 If you'd like to extend the existing uenv with additional packages (or your own), you can use the LAMMPS uenv to provide all dependencies needed to build your customization. See [here](https://eth-cscs.github.io/alps-uenv/tutorial-spack) for more information.[m
 [m
[1;32m+[m[1;32m### LAMMPS ML-IAP: using LAMMPS with machine learning interatomic potentials[m
[1;32m+[m
[1;32m+[m[1;32mFrom `lammps/20251210:v1` onwards, LAMMPS has been built with the [ML-IAP package] enabled.[m
[1;32m+[m[1;32mThis package allows LAMMPS to interface with machine learning interatomic potentials (MLIPs) for molecular dynamics simulations.[m
[1;32m+[m
[1;32m+[m[1;32mDue to the complex dependencies of different MLIPs, users need to install the necessary Python packages themselves.[m
[1;32m+[m[1;32mThis can be best done in a Python virtual environment.[m
[1;32m+[m
[1;32m+[m[1;32m```bash[m
[1;32m+[m[1;32muenv image pull lammps/20251210:v1[m
[1;32m+[m[1;32muenv start --view kokkos lammps/20251210:v1[m
[1;32m+[m
[1;32m+[m[1;32mpython -m venv --system-site-packages venv-lammps-mace[m
[1;32m+[m[1;32msource venv-lammps-mace/bin/activate[m
[1;32m+[m
[1;32m+[m[1;32mpip install --upgrade pip[m
[1;32m+[m
[1;32m+[m[1;32m# TODO: Install the necessary MLIP packages[m
[1;32m+[m[1;32m```[m
[1;32m+[m
[1;32m+[m[1;32mTo run LAMMPS, you need to ensure that the virtual environment is activated (for each process).[m
[1;32m+[m[1;32mYou can use something like the following in your Slurm submission script:[m
[1;32m+[m
[1;32m+[m[1;32m```bash[m
[1;32m+[m[1;32msrun bash -c "[m
[1;32m+[m[1;32msource /PATH/TO/VENV/bin/activate[m
[1;32m+[m[1;32mlmp ...[m
[1;32m+[m[1;32m"[m
[1;32m+[m[1;32m```[m
[1;32m+[m
[1;32m+[m[1;32m??? example "LAMMPS with MACE"[m
[1;32m+[m
[1;32m+[m[1;32m    Install MACE and its dependencies in the virtual environment as follows:[m
[1;32m+[m
[1;32m+[m[1;32m    ```bash[m
[1;32m+[m[1;32m    uenv image pull lammps/20251210:v1[m
[1;32m+[m[1;32m    uenv start --view kokkos lammps/20251210:v1[m
[1;32m+[m[1;32m    python -m venv --system-site-packages venv-lammps-mace[m
[1;32m+[m[1;32m    source venv-lammps-mace/bin/activate[m
[1;32m+[m[1;32m    pip install --upgrade pip[m
[1;32m+[m[1;32m    pip install torch --index-url https://download.pytorch.org/whl/cu129[m
[1;32m+[m[1;32m    pip install mace-torch cuequivariance-torch cuequivariance cuequivariance-ops-torch-cu12 cupy-cuda12x[m
[1;32m+[m[1;32m    ```[m
[1;32m+[m
[1;32m+[m[1;32m    Convert your MACE model to LAMMPS format using the provided conversion script:[m
[1;32m+[m
[1;32m+[m[1;32m    ```bash[m
[1;32m+[m[1;32m    python -m mace.cli.create_lammps_model mace.model --format=mliap[m
[1;32m+[m[1;32m    ```[m
[1;32m+[m
[1;32m+[m[1;32m    This last command generates a file named `mace.model-mliap_lammps.pt` that can be used in LAMMPS.[m
[1;32m+[m
[1;32m+[m[1;32m    A simple LAMMPS input file using MACE looks as follows:[m
[1;32m+[m
[1;32m+[m[1;32m    ```[m
[1;32m+[m[1;32m    units         metal[m
[1;32m+[m[1;32m    atom_style    atomic[m
[1;32m+[m[1;32m    newton        on[m
[1;32m+[m
[1;32m+[m[1;32m    boundary p p p[m
[1;32m+[m
[1;32m+[m[1;32m    atom_style atomic/kk[m
[1;32m+[m[1;32m    lattice fcc 3.6[m
[1;32m+[m[1;32m    region box block 0 4 0 4 0 4[m
[1;32m+[m[1;32m    create_box 1 box[m
[1;32m+[m[1;32m    create_atoms 1 box[m
[1;32m+[m
[1;32m+[m[1;32m    mass 1 58.693[m
[1;32m+[m
[1;32m+[m
[1;32m+[m[1;32m    pair_style    mliap unified mace.model-mliap_lammps.pt 0[m
[1;32m+[m[1;32m    pair_coeff    * * C H O N[m
[1;32m+[m
[1;32m+[m[1;32m    timestep      0.0001[m
[1;32m+[m[1;32m    thermo        100[m
[1;32m+[m
[1;32m+[m[1;32m    fix           1 all nvt temp 300 300 100[m
[1;32m+[m[1;32m    run           1000[m
[1;32m+[m[1;32m    ```[m
[1;32m+[m
[1;32m+[m[1;32m    Run LAMMPS with the following submissions script (adapt to your needs):[m
[1;32m+[m[7;31m    [m
[1;32m+[m[1;32m    ```bash[m
[1;32m+[m[1;32m    #!/bin/bash -l[m
[1;32m+[m[1;32m    #SBATCH --nodes=1[m
[1;32m+[m[1;32m    #SBATCH --ntasks=1[m
[1;32m+[m[1;32m    #SBATCH --cpus-per-task=64[m
[1;32m+[m[1;32m    #SBATCH --gpus-per-task=1[m
[1;32m+[m[1;32m    #SBATCH --account=csstaff[m
[1;32m+[m[1;32m    #SBATCH --time=00:10:00[m
[1;32m+[m[1;32m    #SBATCH --uenv=lammps/20251210:v1[m
[1;32m+[m[1;32m    #SBATCH --view=kokkos[m
[1;32m+[m[1;32m    #SBATCH --partition=debug[m
[1;32m+[m
[1;32m+[m[1;32m    export MPICH_GPU_SUPPORT_ENABLED=1[m
[1;32m+[m[1;32m    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK[m
[1;32m+[m[1;32m    ulimit -s unlimited[m
[1;32m+[m
[1;32m+[m[1;32m    srun bash -c "[m
[1;32m+[m[1;32m    source ./venv-lammps-mace/bin/activate[m
[1;32m+[m[1;32m    lmp -k on g 1 -sf kk -pk kokkos gpu/aware on newton on neigh half -in lmp.inp[m[7;31m [m
[1;32m+[m[1;32m    "[m
[1;32m+[m[1;32m    ```[m
[1;32m+[m
[1;32m+[m
[1;32m+[m
 [LAMMPS]: https://www.lammps.org[m
 [GNU Public License]: http://www.gnu.org/copyleft/gpl.html[m
 [uenv]: https://eth-cscs.github.io/cscs-docs/software/uenv[m
 [Slurm ]: https://eth-cscs.github.io/cscs-docs/running/slurm[m
[1;32m+[m[1;32m[ML-IAP package]: https://docs.lammps.org/Packages_details.html#pkg-ml-iap[m
