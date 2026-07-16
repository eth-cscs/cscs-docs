#!/bin/bash
#
# build-amber.sh — build Amber26 + AmberTools26 on Alps Grace-Hopper (daint gh200)
# inside the `amber/26.6` uenv.
#
# Prerequisites (see the Amber user guide):
#   * the amber uenv is loaded WITH the amber view, e.g.
#       uenv start --view=amber amber/26.6:rc2
#   * the Amber source archives have been extracted and AMBER_ROOT points at the
#     directory that contains ambertools26_src/ and pmemd26_src/.
#
# Usage:
#   export AMBER_ROOT=/path/to/amber      # dir containing ambertools26_src & pmemd26_src
#   ./build-amber.sh [cpu|gpu]            # default: gpu (MPI+CUDA build for GH200)
#
# The install goes into $AMBERHOME (default $AMBER_ROOT/amber26). Serial, MPI, CPU and
# CUDA executables all install side-by-side into the same $AMBERHOME/bin.

set -euo pipefail

# ---------------------------------------------------------------------------
# 0. configuration
# ---------------------------------------------------------------------------
config="${1:-gpu}"

: "${AMBER_ROOT:?Set AMBER_ROOT to the directory containing ambertools26_src and pmemd26_src}"
: "${AMBERHOME:=$AMBER_ROOT/amber26}"
: "${NJOBS:=64}"

AMBERTOOLS_SRC="$AMBER_ROOT/ambertools26_src"
AMBER_SRC="$AMBER_ROOT/pmemd26_src"

case "$config" in
  cpu) amber_mpi=off; amber_cuda=off; amber_openmp=on ;;
  gpu) amber_mpi=on;  amber_cuda=on;  amber_openmp=off ;;
  *)   echo "usage: $0 [cpu|gpu]" >&2; exit 1 ;;
esac

# sanity: make sure we are inside the amber uenv view
if [[ "$(command -v cmake || true)" != /user-environment/* ]]; then
  echo "ERROR: this does not look like the amber uenv view." >&2
  echo "       start it first with:  uenv start --view=amber amber/26.6:rc2" >&2
  exit 1
fi
for d in "$AMBERTOOLS_SRC" "$AMBER_SRC"; do
  [[ -d "$d" ]] || { echo "ERROR: missing source directory $d" >&2; exit 1; }
done

AMBERTOOLS_BUILD="$AMBER_ROOT/build-ambertools-$config"
AMBER_BUILD="$AMBER_ROOT/build-amber-$config"

echo "=================================================================="
echo " Amber26 build"
echo "   config     : $config  (MPI=$amber_mpi CUDA=$amber_cuda OPENMP=$amber_openmp)"
echo "   AMBER_ROOT : $AMBER_ROOT"
echo "   AMBERHOME  : $AMBERHOME"
echo "   jobs       : $NJOBS"
echo "=================================================================="

# ---------------------------------------------------------------------------
# common CMake options
#   -DCMAKE_Fortran_FLAGS=-fPIC : required on Grace-Hopper (COMMON block size)
#   -DDOWNLOAD_MINICONDA=false  : never let Amber install its own conda (~115k inodes)
#   -DBUILD_PYTHON=on           : use the Python + packages provided by the uenv
#   -DBUILD_QUICK=off           : Quick's GPU build takes hours; enable only if you need it
#   -DCHECK_UPDATES=false       : don't phone home during configure
# ---------------------------------------------------------------------------
common_cmake=(
  -DCMAKE_INSTALL_PREFIX="$AMBERHOME"
  -DCOMPILER=GNU
  -DMPI="$amber_mpi" -DCUDA="$amber_cuda" -DOPENMP="$amber_openmp"
  -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=on
  -DCMAKE_Fortran_FLAGS="-fPIC"
  -DBUILD_QUICK=off
  -DCHECK_UPDATES=false
)

# ---------------------------------------------------------------------------
# 1. AmberTools
# ---------------------------------------------------------------------------
echo; echo "### [1/2] AmberTools : configure"
rm -rf "$AMBERTOOLS_BUILD"; mkdir -p "$AMBERTOOLS_BUILD"; cd "$AMBERTOOLS_BUILD"
cmake "${common_cmake[@]}" "$AMBERTOOLS_SRC"

echo; echo "### [1/2] AmberTools : build (warnings -> at-error.log)"
make -j"$NJOBS" 2> at-error.log

echo; echo "### [1/2] AmberTools : install"
make install 2>> at-error.log

# ---------------------------------------------------------------------------
# 2. Amber / PMEMD
# ---------------------------------------------------------------------------
echo; echo "### [2/2] Amber/PMEMD : configure"
rm -rf "$AMBER_BUILD"; mkdir -p "$AMBER_BUILD"; cd "$AMBER_BUILD"
cmake "${common_cmake[@]}" -DPMEMD_ONLY=true "$AMBER_SRC"

echo; echo "### [2/2] Amber/PMEMD : build (warnings -> amber-error.log)"
make -j"$NJOBS" 2> amber-error.log

echo; echo "### [2/2] Amber/PMEMD : install"
make install 2>> amber-error.log

echo
echo "=================================================================="
echo " DONE. Installed into $AMBERHOME"
echo " pmemd executables:"
ls "$AMBERHOME"/bin/ | grep -iE 'pmemd|sander' | sed 's/^/   /'
echo
echo " Activate this installation in a new shell with:"
echo "   uenv start --view=amber amber/26.6:rc2"
echo "   source $AMBERHOME/amber.sh"
echo "=================================================================="
