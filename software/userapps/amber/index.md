# Amber

> [!WARNING]
>
> Amber is [user software](<https://docs.cscs.ch/policies/support/index.md#user-applications> "User Applications") on Alps. This guide is provided based on our experiences helping users — however we can’t provide the same level of support as we do for [supported software](<https://docs.cscs.ch/policies/support/index.md#officially-supported-applications> "Officially Supported Applications"). See the [main applications page](<https://docs.cscs.ch/software/index.md#applications-and-frameworks> "Applications and frameworks") for more information.
>
> Amber provides many options and tools. The process shown here builds a representative CUDA + MPI configuration for Grace-Hopper — you may have to modify the CMake options to build the exact set of tools you need.

[Amber](<https://ambermd.org>) is a suite of programs for molecular dynamics simulation of biomolecular systems such as proteins, nucleic acids, and small molecules. It is widely used in computational chemistry and structural biology, with GPU acceleration support through its PMEMD engine.

The instructions provided here are for building Amber on [daint](<https://docs.cscs.ch/clusters/daint/index.md#daint> "Daint") with Grace-Hopper (GH200) support.

## Licensing

Amber is distributed under a dual license, with free access for non-profit academic users, and paid licenses for commercial use. CSCS is not permitted to redistribute Amber binaries or source code. Instead, users must independently agree to the license terms, then download the source and compile Amber themselves.

Users are responsible for following the terms of the license that they agree to when applying for access on the Amber web site.

> [!NOTE]
>
> This page documents how to download and install **Amber26**, which can be freely downloaded and used for non-commercial academic use cases. Older versions had different license terms that stop CSCS from accessing the source.

## Overview

Because CSCS cannot redistribute Amber (see [Licensing](<https://docs.cscs.ch/software/userapps/amber/index.md#licensing>)), we provide a uenv that contains everything needed to build Amber, for users to build their own Amber. The workflow has three steps:

1. [Pull the `amber/26` uenv](<https://docs.cscs.ch/software/userapps/amber/index.md#the-amber-uenv> "The Amber uenv"): provides the compiler, CUDA, Python and libraries.
2. [Download and extract the Amber source](<https://docs.cscs.ch/software/userapps/amber/index.md#getting-amber> "Getting Amber"): you agree to the license and download it yourself.
3. [Build Amber](<https://docs.cscs.ch/software/userapps/amber/index.md#getting-amber> "Getting Amber"): with the provided script, then test it.
4. Optionally, [package the build as its own uenv](<https://docs.cscs.ch/software/userapps/amber/index.md#making-a-uenv> "Making a Uenv") so it survives scratch cleanup.

The whole build takes roughly 1 to 2 hours on a single Grace-Hopper node.

## The Amber uenv

The `amber/26` [uenv](<https://docs.cscs.ch/software/uenv/index.md#uenv>) provides the compilers and libraries needed to build both CPU-only and CUDA-enabled installations on the [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") nodes of [daint](<https://docs.cscs.ch/clusters/daint/index.md#daint> "Daint"). It provides, in a single view called `amber`:

- **CUDA 12.8**: the most recent version of CUDA supported by Amber26.
- **GCC 12.5**: the most recent non-deprecated GCC compatible with CUDA 12.8.
- **Python 3.12** with `tkinter`: compatible with all of the Python packages used by Amber, plus every Python package Amber checks for at build time (numpy, scipy, matplotlib, pandas, numba, gemmi, biopython, rich, scikit-learn, sympy, pydantic, psutil, networkx, mpi4py, freesasa, f90nml, …).
- **cray-mpich** (CUDA-aware) and optimised FFTW, netCDF, HDF5, OpenBLAS, GSL.

You do not need to install any Python packages by hand—everything required to build Amber is already in the view.

> [!NOTE]
>
> **Downloading the `amber/26` uenv**
>
> ```console
> $ uenv image find amber
> uenv          arch   system  id                size(MB)  date
> amber/26:v1   gh200  daint   60fe8c184669d520   8,327    2026-07-09
> $ uenv image pull amber/26:v1
> ```

> [!NOTE]
>
> **Starting the `amber/26` uenv**
>
> The `amber/26` uenv must be loaded with the **`amber` view** both when building and when running Amber.
>
> ```console
> $ uenv start --view=amber amber/26:v1
> $ uenv status
> uenv  amber
>   image  amber/26:v1@daint%gh200
>   mount  /user-environment
>   views  [amber]
> ```
>
> If you frequently use the tools interactively, consider creating an alias for a [custom environment](<https://docs.cscs.ch/software/uenv/guides/index.md#custom-environments> "Custom environments") that loads the uenv and also sets `AMBERHOME`.

## Getting Amber

A full Amber installation consists of AmberTools and Amber (PMEMD), which are downloaded as two separate archives from the [Amber website](<https://ambermd.org/GetAmber.php>) (see the “How to obtain AmberTools26” and “How to obtain Amber26” sections). You have to enter your name and institution; if you agree to the non-commercial terms the download starts immediately.

After downloading you will have two files:

| file | description |
| --- | --- |
| `ambertools26.tar.bz2` | source code for AmberTools |
| `pmemd26.tar.bz2` | source code for Amber/PMEMD |

> [!NOTE]
>
> **Copying the Amber sources to Daint**
>
> We assume you have SSH set up as described in [Using SSH](<https://docs.cscs.ch/access/ssh/index.md#using-ssh>).
>
> ```console
> $ ssh daint 'mkdir -p ~/ambersources'
> $ scp ambertools26.tar.bz2 pmemd26.tar.bz2 daint:~/ambersources
> ```

### Extracting the source

> [!TIP]
>
> **Where to build**
>
> Building generates a large number of files. Build on a fast file system with plenty of space — your [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) is a good choice. Install the result into your [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) path (e.g. `export AMBERHOME=$STORE/amber26`) if you want everyone in your group to be able to use it.

Choose a directory to unpack the sources into, and set `AMBER_ROOT` to point at it:

extract the source archives

```bash
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

```text
$AMBER_ROOT/ambertools26_src/     # AmberTools
$AMBER_ROOT/pmemd26_src/          # Amber / PMEMD
```

> [!NOTE]
>
> **Checking for updates (optional)**
>
> Amber periodically releases patches. You can check for and apply them before building. Review what the updater will do before applying it — applied updates change your source tree.
>
> ```bash
> uenv start --view=amber amber/26:v1
> cd $AMBER_ROOT/ambertools26_src && ./update_amber --check-updates
> cd $AMBER_ROOT/pmemd26_src      && ./update_pmemd --check-updates
> # apply with: ./update_amber --update   and   ./update_pmemd --update
> ```

## Building Amber

Download the build script [`build-amber.sh`](<https://docs.cscs.ch/software/userapps/scripts/build-amber.sh>) (also reproduced below), make it executable, and run it inside the uenv. It builds **AmberTools** first and then **Amber/PMEMD**, installing both into a single `$AMBERHOME`.

build Amber (MPI + CUDA, for GH200)

```bash
# 1. start the uenv with the amber view
uenv start --view=amber amber/26:v1

# 2. point at your extracted sources (from the previous step)
export AMBER_ROOT=$SCRATCH/amber

# 3. build. 'gpu' = MPI + CUDA (default); 'cpu' = serial/OpenMP, no CUDA.
#    Installs into $AMBER_ROOT/amber26 by default (override with AMBERHOME).
./build-amber.sh gpu
```

> [!TIP]
>
> **Build CPU-only first if you are debugging**
>
> The CPU-only build (`./build-amber.sh cpu`) is faster and is a good way to check that the basic toolchain works before committing to the longer MPI+CUDA build. Both configurations install into the same `$AMBERHOME`, so you can run the script twice.

The script sets the following important options for you:

- `-DCMAKE_Fortran_FLAGS=-fPIC` — **required** on Grace-Hopper (works around a `COMMON` block size limit).
- `-DDOWNLOAD_MINICONDA=false` — never let Amber install its own conda; the Amber conda environment contains \~115,000 files and will hammer a shared file system, so the uenv provides Python and all packages instead.
- `-DBUILD_PYTHON=on` — use the uenv’s Python and packages.
- `-DBUILD_QUICK=off` — the Quick QM engine’s GPU build takes hours, so remove this from the script only if you need Quick.
- `-DCHECK_UPDATES=false` — don’t contact the network during configure (apply updates explicitly, as above).

When it finishes, the install directory `$AMBERHOME/bin` contains the PMEMD executables, including:

| executable | description |
| --- | --- |
| `pmemd` | serial CPU engine |
| `pmemd.MPI` | MPI CPU engine |
| `pmemd.cuda` | single-GPU engine (SPFP precision) |
| `pmemd.cuda.MPI` | multi-GPU / multi-node engine |
| `sander`, `sander.MPI` | the AmberTools MD engine |

> [!NOTE]
>
> **Contents of `build-amber.sh`**
>
> ```bash
> #!/bin/bash
> #
> # build-amber.sh — build Amber26 + AmberTools26 on Alps Grace-Hopper (daint gh200)
> # inside the `amber/26.6` uenv.
> #
> # Prerequisites (see the Amber user guide):
> #   * the amber uenv is loaded WITH the amber view, e.g.
> #       uenv start --view=amber amber/26.6:rc3
> #   * the Amber source archives have been extracted and AMBER_ROOT points at the
> #     directory that contains ambertools26_src/ and pmemd26_src/.
> #
> # Usage:
> #   export AMBER_ROOT=/path/to/amber      # dir containing ambertools26_src & pmemd26_src
> #   ./build-amber.sh [cpu|gpu]            # default: gpu (MPI+CUDA build for GH200)
> #
> # The install goes into $AMBERHOME (default $AMBER_ROOT/amber26). Serial, MPI, CPU and
> # CUDA executables all install side-by-side into the same $AMBERHOME/bin.
> #
> # On success, this script also packages $AMBERHOME as its own "amber-build" uenv by calling
> # squash-amber.sh (must be in the same directory) — see that script and the Amber user guide.
>
> set -euo pipefail
>
> # ---------------------------------------------------------------------------
> # 0. configuration
> # ---------------------------------------------------------------------------
> config="${1:-gpu}"
>
> : "${AMBER_ROOT:?Set AMBER_ROOT to the directory containing ambertools26_src and pmemd26_src}"
> : "${AMBERHOME:=$AMBER_ROOT/amber26}"
> : "${NJOBS:=64}"
>
> AMBERTOOLS_SRC="$AMBER_ROOT/ambertools26_src"
> AMBER_SRC="$AMBER_ROOT/pmemd26_src"
>
> case "$config" in
>   cpu) amber_mpi=off; amber_cuda=off; amber_openmp=on ;;
>   gpu) amber_mpi=on;  amber_cuda=on;  amber_openmp=off ;;
>   *)   echo "usage: $0 [cpu|gpu]" >&2; exit 1 ;;
> esac
>
> # sanity: make sure we are inside the amber uenv view
> if [[ "$(command -v cmake || true)" != /user-environment/* ]]; then
>   echo "ERROR: this does not look like the amber uenv view." >&2
>   echo "       start it first with:  uenv start --view=amber amber/26.6:rc3" >&2
>   exit 1
> fi
> for d in "$AMBERTOOLS_SRC" "$AMBER_SRC"; do
>   [[ -d "$d" ]] || { echo "ERROR: missing source directory $d" >&2; exit 1; }
> done
>
> AMBERTOOLS_BUILD="$AMBER_ROOT/build-ambertools-$config"
> AMBER_BUILD="$AMBER_ROOT/build-amber-$config"
>
> echo "=================================================================="
> echo " Amber26 build"
> echo "   config     : $config  (MPI=$amber_mpi CUDA=$amber_cuda OPENMP=$amber_openmp)"
> echo "   AMBER_ROOT : $AMBER_ROOT"
> echo "   AMBERHOME  : $AMBERHOME"
> echo "   jobs       : $NJOBS"
> echo "=================================================================="
>
> # ---------------------------------------------------------------------------
> # common CMake options
> #   -DCMAKE_Fortran_FLAGS=-fPIC : required on Grace-Hopper (COMMON block size)
> #   -DDOWNLOAD_MINICONDA=false  : never let Amber install its own conda (~115k inodes)
> #   -DBUILD_PYTHON=on           : use the Python + packages provided by the uenv
> #   -DBUILD_QUICK=off           : Quick's GPU build takes hours; enable only if you need it
> #   -DCHECK_UPDATES=false       : don't phone home during configure
> # ---------------------------------------------------------------------------
> common_cmake=(
>   -DCMAKE_INSTALL_PREFIX="$AMBERHOME"
>   -DCOMPILER=GNU
>   -DMPI="$amber_mpi" -DCUDA="$amber_cuda" -DOPENMP="$amber_openmp"
>   -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=on
>   -DCMAKE_Fortran_FLAGS="-fPIC"
>   -DBUILD_QUICK=off
>   -DCHECK_UPDATES=false
> )
>
> # ---------------------------------------------------------------------------
> # 1. AmberTools
> # ---------------------------------------------------------------------------
> echo; echo "### [1/2] AmberTools : configure"
> rm -rf "$AMBERTOOLS_BUILD"; mkdir -p "$AMBERTOOLS_BUILD"; cd "$AMBERTOOLS_BUILD"
> cmake "${common_cmake[@]}" "$AMBERTOOLS_SRC"
>
> echo; echo "### [1/2] AmberTools : build (warnings -> at-error.log)"
> make -j"$NJOBS" 2> at-error.log
>
> echo; echo "### [1/2] AmberTools : install"
> make install 2>> at-error.log
>
> # ---------------------------------------------------------------------------
> # 2. Amber / PMEMD
> # ---------------------------------------------------------------------------
> echo; echo "### [2/2] Amber/PMEMD : configure"
> rm -rf "$AMBER_BUILD"; mkdir -p "$AMBER_BUILD"; cd "$AMBER_BUILD"
> cmake "${common_cmake[@]}" -DPMEMD_ONLY=true "$AMBER_SRC"
>
> echo; echo "### [2/2] Amber/PMEMD : build (warnings -> amber-error.log)"
> make -j"$NJOBS" 2> amber-error.log
>
> echo; echo "### [2/2] Amber/PMEMD : install"
> make install 2>> amber-error.log
>
> echo
> echo "=================================================================="
> echo " DONE. Installed into $AMBERHOME"
> echo " pmemd executables:"
> ls "$AMBERHOME"/bin/ | grep -iE 'pmemd|sander' | sed 's/^/   /'
> echo
> echo " Activate this installation in a new shell with:"
> echo "   uenv start --view=amber amber/26.6:rc3"
> echo "   source $AMBERHOME/amber.sh"
> echo "=================================================================="
>
> # ---------------------------------------------------------------------------
> # 3. package $AMBERHOME as its own uenv, so it survives SCRATCH cleanup and stops
> #    consuming inodes there (see squash-amber.sh).
> # ---------------------------------------------------------------------------
> script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
> AMBERHOME="$AMBERHOME" "$script_dir/squash-amber.sh"
> ```

## Testing the build

Activate the installation and run a short simulation on a GPU to confirm everything works. `amber.sh` sets `AMBERHOME` and puts the Amber tools on your `PATH`.

single-GPU smoke test

```bash
uenv start --view=amber amber/26:v1
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

The [`test-amber.sh`](<https://docs.cscs.ch/software/userapps/scripts/test-amber.sh>) script automates this check. It runs the single-GPU test above and, if `srun` and more than one GPU are available, a short multi-GPU run as well.

run the smoke test

```bash
export AMBERHOME=$AMBER_ROOT/amber26
export PMEMD_SRC=$AMBER_ROOT/pmemd26_src
./test-amber.sh
```

> [!NOTE]
>
> **Contents of `test-amber.sh`**
>
> ```bash
> #!/bin/bash
> #
> # test-amber.sh — quick smoke test of an Amber26 installation built with the amber uenv.
> #
> # Runs a short GB simulation on one GPU with pmemd.cuda, and (if srun is available and you
> # have >=2 GPUs) a short PME simulation across 2 GPUs with pmemd.cuda.MPI.
> #
> # Usage (inside the amber uenv, with the build already installed):
> #   uenv start --view=amber amber/26.6:rc3
> #   export AMBERHOME=/path/to/amber26        # or: source /path/to/amber26/amber.sh
> #   ./test-amber.sh
> #
> set -euo pipefail
>
> : "${AMBERHOME:?Set AMBERHOME to your Amber install (e.g. \$AMBER_ROOT/amber26)}"
> work="$(mktemp -d "${SCRATCH:-/tmp}/amber-smoketest.XXXXXX")"
> cd "$work"
> echo "smoke-test working dir: $work"
>
> # Locate a small GB test case (ACE-ALA3-NME) from the extracted pmemd sources.
> # Set PMEMD_SRC to the pmemd26_src directory so the script can find it.
> gb="${PMEMD_SRC:-}/test/cuda/gb_ala3"
> if [[ -n "${PMEMD_SRC:-}" && -f "$gb/prmtop" ]]; then
>   cp "$gb/prmtop" "$gb/inpcrd" .
> else
>   echo "NOTE: set PMEMD_SRC=\$AMBER_ROOT/pmemd26_src to auto-locate a test case." >&2
>   echo "      Skipping — provide prmtop + inpcrd in $work to run this test." >&2
>   exit 0
> fi
>
> cat > mdin <<'EOF'
> GB smoke test
>  &cntrl
>   imin=0, irest=1, ntx=5, nstlim=20, dt=0.002, ntb=0,
>   ntf=2, ntc=2, ntpr=5, ntwx=0, ntwr=0,
>   cut=9999.0, rgbmax=9999.0, igb=1, ntt=0, ig=71277,
>  /
> EOF
>
> echo "=== [1] pmemd.cuda : single-GPU GB run ==="
> "$AMBERHOME/bin/pmemd.cuda" -O -i mdin -p prmtop -c inpcrd -o out.serial -r rst.serial
> grep -iE "GPU IN USE|Device Name" out.serial | head -2
> grep -q "Final Performance" out.serial && echo "  -> single-GPU run OK"
>
> if command -v srun >/dev/null 2>&1 && [[ -x "$AMBERHOME/bin/pmemd.cuda.MPI" ]]; then
>   echo "=== [2] pmemd.cuda.MPI : 2-GPU run (needs a real system; using JAC if present) ==="
>   jac="${PMEMD_SRC}/test/cuda/jac"
>   if [[ -f "$jac/prmtop" && -f "$jac/inpcrd.equil" ]]; then
>     cp "$jac/prmtop" jac.prmtop; cp "$jac/inpcrd.equil" jac.inpcrd
>     cat > mdin.jac <<'EOF'
> JAC PME smoke test
>  &cntrl
>   ntx=5, irest=1, ntb=2, nstlim=50, dt=0.002, cut=8.0,
>   ntt=1, ntc=2, ntf=2, ntp=1, taup=1.0, temp0=300.0,
>   ntpr=10, ntwx=0, ntwr=0, ig=71277,
>  /
> EOF
>     # --overlap: without it, srun can hang ("step creation temporarily disabled") when run
>     # inside an interactive allocation that already has a step running (e.g. the login bash).
>     srun --overlap -n2 "$AMBERHOME/bin/pmemd.cuda.MPI" -O -i mdin.jac -p jac.prmtop -c jac.inpcrd -o out.jacmpi -r rst.jacmpi
>     grep -iE "Peer to Peer support" out.jacmpi | head -1
>     grep -q "A V E R A G E" out.jacmpi && echo "  -> 2-GPU MPI run OK"
>   else
>     echo "  (JAC test case not found — skipping multi-GPU test)"
>   fi
> fi
>
> echo "=== smoke test complete ==="
> ```

> [!NOTE]
>
> **IEEE floating-point notes are harmless**
>
> PMEMD often prints `Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG`. This is expected and does not indicate a failed run.

## Making a Uenv

A full Amber install contains a very large number of files, which can push you over your inode quota if it is stored on [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>). [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) is also subject to [cleanup policies](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies").

The fix is to package the installed `$AMBERHOME` directory itself as a uenv that mounts at the `$AMBERHOME` path, and is designed to be loaded **alongside** the `amber` uenv rather than on its own.

`build-amber.sh` runs this packaging step automatically after a successful install, by calling [`squash-amber.sh`](<https://docs.cscs.ch/software/userapps/scripts/squash-amber.sh>) (also reproduced below). It:

- writes a `meta/env.json` into `$AMBERHOME` that describes a uenv named `amber-build`, mounted at `$AMBERHOME`, with a single `amber-build` view that adds `$AMBERHOME/bin` to `PATH` and sets `AMBERHOME`;
- packages `$AMBERHOME` into a squashfs image with `mksquashfs` — using the copy bundled inside the `amber` uenv’s own store, since it is not on `PATH` by default;
- prints, but does not run, the commands needed to register and use the image.

> [!NOTE]
>
> **Contents of `squash-amber.sh`**
>
> ```bash
> #!/bin/bash
> #
> # squash-amber.sh — package a built Amber26 installation ($AMBERHOME) as its own
> # "amber-build" uenv, so it survives SCRATCH cleanup and stops consuming inodes there.
> #
> # The resulting image mounts at the exact $AMBERHOME path it was built at, and provides a
> # single "amber-build" view that puts $AMBERHOME/bin on PATH and sets AMBERHOME. It is
> # designed to be loaded ALONGSIDE the amber uenv (for CUDA/MPI/Python/...), not standalone:
> #
> #   uenv start amber/26.6:rc3,amber-build/2026:v1 --view=amber,amber-build
> #
> # Called automatically by build-amber.sh after a successful install. Can also be run by hand:
> #
> #   export AMBERHOME=/path/to/amber26   # an existing Amber install (built with build-amber.sh)
> #   ./squash-amber.sh
> #
> set -euo pipefail
>
> : "${AMBERHOME:?Set AMBERHOME to an existing Amber install (e.g. \$AMBER_ROOT/amber26)}"
> : "${OUTPUT:=$(dirname "$AMBERHOME")/store.squashfs}"
>
> # sanity: make sure this looks like a real Amber install
> shopt -s nullglob
> pmemd_bins=("$AMBERHOME"/bin/pmemd*)
> shopt -u nullglob
> [[ ${#pmemd_bins[@]} -gt 0 ]] || { echo "ERROR: no pmemd* executables found in $AMBERHOME/bin -- is AMBERHOME correct?" >&2; exit 1; }
>
> echo "=================================================================="
> echo " squash-amber: packaging \$AMBERHOME as the 'amber-build' uenv"
> echo "   AMBERHOME : $AMBERHOME"
> echo "   image     : $OUTPUT"
> echo "=================================================================="
>
> # ---------------------------------------------------------------------------
> # 1. meta/env.json — a single view ("amber-build") that only adds $AMBERHOME/bin to PATH
> #    (+ AMBERHOME, + LD_LIBRARY_PATH if $AMBERHOME/lib exists). It deliberately does NOT set
> #    CC/CUDA_HOME/MPICC/etc: those come from the "amber" view, loaded alongside this one.
> # ---------------------------------------------------------------------------
> echo; echo "### [1/2] writing meta/env.json"
> mkdir -p "$AMBERHOME/meta"
> python3 - "$AMBERHOME" <<'PYEOF'
> import json, os, sys
>
> amberhome = sys.argv[1]
>
> view = {
>     "description": "Amber26 tools built with build-amber.sh. Load alongside the amber view for CUDA/MPI/Python.",
>     "recipe_variables": {"list": {}, "scalar": {}},
>     "root": amberhome,
>     "env": {
>         "version": 1,
>         "values": {
>             "list": {
>                 "PATH": [{"op": "prepend", "value": [f"{amberhome}/bin"]}],
>             },
>             "scalar": {
>                 "AMBERHOME": amberhome,
>             },
>         },
>     },
> }
>
> libdir = os.path.join(amberhome, "lib")
> if os.path.isdir(libdir):
>     view["env"]["values"]["list"]["LD_LIBRARY_PATH"] = [{"op": "prepend", "value": [libdir]}]
>
> env_json = {
>     "name": "amber-build",
>     "description": "Amber26 built with the amber uenv, must be loaded alongside amber.",
>     "mount": amberhome,
>     "default-view": "amber-build",
>     "modules": None,
>     "views": {"amber-build": view},
> }
>
> out = os.path.join(amberhome, "meta", "env.json")
> with open(out, "w") as f:
>     json.dump(env_json, f, indent=2)
>     f.write("\n")
> print(f"  -> wrote {out}")
> PYEOF
>
> # ---------------------------------------------------------------------------
> # 2. mksquashfs — use the copy bundled in the amber uenv's store (a build-time-only
> #    dependency, not linked into the "amber" view), falling back to PATH.
> # ---------------------------------------------------------------------------
> echo; echo "### [2/2] building $OUTPUT"
> mksquashfs_bin="$(find /user-environment -maxdepth 4 -iname mksquashfs -type f 2>/dev/null | head -n1)"
> if [[ -z "$mksquashfs_bin" ]]; then
>   mksquashfs_bin="$(command -v mksquashfs || true)"
> fi
> [[ -n "$mksquashfs_bin" && -x "$mksquashfs_bin" ]] || {
>   echo "ERROR: mksquashfs not found (expected inside the amber uenv store, e.g." >&2
>   echo "       /user-environment/linux-*/squashfs-*/bin/mksquashfs). Is the amber uenv loaded?" >&2
>   exit 1
> }
> echo "  using $mksquashfs_bin"
> rm -f "$OUTPUT"
> "$mksquashfs_bin" "$AMBERHOME" "$OUTPUT" -noappend
>
> uenv_cfg="$(uenv config 2>/dev/null | awk '$1=="user:"{print $2}')"
>
> echo
> echo "=================================================================="
> echo " DONE. Packaged $(du -h "$OUTPUT" | cut -f1) image: $OUTPUT"
> echo
> echo " The default uenv repository (\$SCRATCH/.uenv-images) lives on the same file system"
> echo " this is meant to escape -- register the image in a repository on \$STORE instead:"
> echo
> echo "   uenv image add amber-build/2026:v1@daint%gh200 $OUTPUT"
> echo
> echo " Then use it alongside the amber uenv (the 'amber-build' view relies on 'amber' for"
> echo " CUDA/MPI/Python):"
> echo
> echo "   uenv start amber/26.6:v1,amber-build/2026:v1 --view=amber,amber-build"
> echo
> echo " Once registered, empty out $AMBERHOME's *contents* to reclaim its inodes:"
> echo "   rm -rf $AMBERHOME && mkdir -p $AMBERHOME"
> echo " Leave the directory itself in place -- uenv mounts onto it but does not create it,"
> echo " so it must still exist (empty) at this exact path for the amber-build uenv to start."
> echo "=================================================================="
> ```

Once it is registered in a uenv repository that lives outside Scratch, the *contents* of `$AMBERHOME` can be removed — freeing the inodes they were using — while Amber keeps working, mounted read-only from the packaged image, indefinitely.

### Registering the image

The `squash-amber.sh` script leaves the image next to `$AMBERHOME`.

register the amber-build image

```console
$ uenv image add amber-build/2026:v1@daint%gh200 $AMBER_ROOT/store.squashfs
```

Once the image is registered, empty out `$AMBERHOME` to reclaim its inodes:

reclaim the inodes

```console
$ rm -rf $AMBERHOME && mkdir -p $AMBERHOME
```

> [!WARNING]
>
> Leave the directory itself in place. `uenv` mounts the image onto `$AMBERHOME` but does not create the mount point — it must still exist (empty) at this exact path for the `amber-build` uenv to start.

### Using the packaged build

Load the `amber-build` uenv alongside `amber`, with both views active. The `amber-build` view only adds `$AMBERHOME/bin` to `PATH` and sets `AMBERHOME` — it relies on the `amber` view, loaded at the same time, for CUDA, MPI and Python.

start both uenvs together

```console
$ uenv start amber/26:v1,amber-build/2026:v1 --view=amber,amber-build
$ pmemd.cuda -O -i mdin -p prmtop -c inpcrd -o out
```

> [!TIP]
>
> You no longer need to `source $AMBERHOME/amber.sh` — the `amber-build` view already sets `AMBERHOME` and puts the Amber tools on `PATH`.

## Running simulations

Load the uenv with the `amber` view in your batch script and launch the GPU engine with `srun`. Each MPI rank uses one GPU; the [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") nodes have 4 GPUs.

If you [packaged your build as the `amber-build` uenv](<https://docs.cscs.ch/software/userapps/amber/index.md#making-a-uenv> "Making a Uenv"), load it alongside `amber` and drop the `source amber.sh` step — `pmemd.cuda.MPI` is already on `PATH`:

submit.sh — 1 node, 4 GPUs, using the packaged amber-build uenv

```bash
#!/bin/bash
#SBATCH --job-name=amber
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --time=01:00:00
#SBATCH --uenv=amber/26:v1,amber-build/2026:v1
#SBATCH --view=amber,amber-build

srun pmemd.cuda.MPI -O -i mdin -p prmtop -c inpcrd -o mdout -r restrt -x mdcrd
```

Otherwise, running straight from the `$AMBERHOME` you just built also works, by sourcing `amber.sh` to set `AMBERHOME` and `PATH`:

submit.sh — 1 node, 4 GPUs, running directly from \\$AMBERHOME

```bash
#!/bin/bash
#SBATCH --job-name=amber
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --time=01:00:00
#SBATCH --uenv=amber/26:v1
#SBATCH --view=amber

source $SCRATCH/amber/amber26/amber.sh

srun pmemd.cuda.MPI -O -i mdin -p prmtop -c inpcrd -o mdout -r restrt -x mdcrd
```

> [!TIP]
>
> **One GPU is often fastest**
>
> For many systems a single GPU (`pmemd.cuda`, `--ntasks-per-node=1 --gpus-per-node=1`) is faster than multi-GPU, because PMEMD is highly optimised for one GPU. Multi-GPU (`pmemd.cuda.MPI`) helps for large systems; it uses direct GPU peer-to-peer communication, which is enabled on the GH200 nodes.
>
> `pmemd.cuda.MPI` requires the system to have at least **32× more atoms than MPI ranks** — very small test systems will abort with `Must have 32x more atoms than processors!` when run on multiple ranks.

## Advanced notes

> [!NOTE]
>
> These notes are for CSCS staff and adventurous users who want to update or modify the `amber` uenv. See the recipe’s `README.md` and `lessons.md` for the full build history.

Installing *only* Amber against externally provided dependencies is awkward because Amber:

- vendors dependencies such as boost (and, with MPI, fftw) into its source tree and builds its own copies if it does not find suitable ones;
- by default installs a conda environment, which it then uses to install Python packages (\~115k files).

The `amber/26` uenv was configured to avoid this:

- CUDA 12.8 is the most recent CUDA supported by Amber26, which forces GCC ≤ 12 (GCC 12.5 is the newest non-deprecated GCC compatible with it in Spack).
- Python is pinned to 3.12 — the most recent Python compatible with every package Amber uses, and it is built `+tkinter` (required by Amber, not the default in the `prgenv` uenv).
- Every Python package that Amber’s `cmake/PythonBuildConfig.cmake` checks for is included in the view. Two packages that are not in Spack — `freesasa` and `f90nml` — are `pip`-installed into the view by the recipe’s `post-install` script. `f90nml` in particular is `pip install`-ed unconditionally by `AmberTools/src/PyPE_RESP/setup.py` at build time, so providing it in the uenv prevents a read-only-filesystem failure.

Remaining opportunities for a future version:

- Amber rebuilds its own boost, and its own fftw when building with MPI, instead of using the optimised copies in the uenv — each dependency taken from the uenv would speed up the build and reduce warning noise.
- Amber tracks a few years behind current package versions; pinning older CMake/Python could reduce warnings further.
