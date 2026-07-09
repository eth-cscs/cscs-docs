#!/bin/bash
#
# test-amber.sh — quick smoke test of an Amber26 installation built with the amber uenv.
#
# Runs a short GB simulation on one GPU with pmemd.cuda, and (if srun is available and you
# have >=2 GPUs) a short PME simulation across 2 GPUs with pmemd.cuda.MPI.
#
# Usage (inside the amber uenv, with the build already installed):
#   uenv start --view=amber amber/26.6:rc2
#   export AMBERHOME=/path/to/amber26        # or: source /path/to/amber26/amber.sh
#   ./test-amber.sh
#
set -euo pipefail

: "${AMBERHOME:?Set AMBERHOME to your Amber install (e.g. \$AMBER_ROOT/amber26)}"
work="$(mktemp -d "${SCRATCH:-/tmp}/amber-smoketest.XXXXXX")"
cd "$work"
echo "smoke-test working dir: $work"

# Locate a small GB test case (ACE-ALA3-NME) from the extracted pmemd sources.
# Set PMEMD_SRC to the pmemd26_src directory so the script can find it.
gb="${PMEMD_SRC:-}/test/cuda/gb_ala3"
if [[ -n "${PMEMD_SRC:-}" && -f "$gb/prmtop" ]]; then
  cp "$gb/prmtop" "$gb/inpcrd" .
else
  echo "NOTE: set PMEMD_SRC=\$AMBER_ROOT/pmemd26_src to auto-locate a test case." >&2
  echo "      Skipping — provide prmtop + inpcrd in $work to run this test." >&2
  exit 0
fi

cat > mdin <<'EOF'
GB smoke test
 &cntrl
  imin=0, irest=1, ntx=5, nstlim=20, dt=0.002, ntb=0,
  ntf=2, ntc=2, ntpr=5, ntwx=0, ntwr=0,
  cut=9999.0, rgbmax=9999.0, igb=1, ntt=0, ig=71277,
 /
EOF

echo "=== [1] pmemd.cuda : single-GPU GB run ==="
"$AMBERHOME/bin/pmemd.cuda" -O -i mdin -p prmtop -c inpcrd -o out.serial -r rst.serial
grep -iE "GPU IN USE|Device Name" out.serial | head -2
grep -q "Final Performance" out.serial && echo "  -> single-GPU run OK"

if command -v srun >/dev/null 2>&1 && [[ -x "$AMBERHOME/bin/pmemd.cuda.MPI" ]]; then
  echo "=== [2] pmemd.cuda.MPI : 2-GPU run (needs a real system; using JAC if present) ==="
  jac="${PMEMD_SRC}/test/cuda/jac"
  if [[ -f "$jac/prmtop" && -f "$jac/inpcrd.equil" ]]; then
    cp "$jac/prmtop" jac.prmtop; cp "$jac/inpcrd.equil" jac.inpcrd
    cat > mdin.jac <<'EOF'
JAC PME smoke test
 &cntrl
  ntx=5, irest=1, ntb=2, nstlim=50, dt=0.002, cut=8.0,
  ntt=1, ntc=2, ntf=2, ntp=1, taup=1.0, temp0=300.0,
  ntpr=10, ntwx=0, ntwr=0, ig=71277,
 /
EOF
    srun -n2 "$AMBERHOME/bin/pmemd.cuda.MPI" -O -i mdin.jac -p jac.prmtop -c jac.inpcrd -o out.jacmpi -r rst.jacmpi
    grep -iE "Peer to Peer support" out.jacmpi | head -1
    grep -q "A V E R A G E" out.jacmpi && echo "  -> 2-GPU MPI run OK"
  else
    echo "  (JAC test case not found — skipping multi-GPU test)"
  fi
fi

echo "=== smoke test complete ==="
