#!/bin/bash
#
# squash-amber.sh — package a built Amber26 installation ($AMBERHOME) as its own
# "amber-build" uenv, so it survives SCRATCH cleanup and stops consuming inodes there.
#
# The resulting image mounts at the exact $AMBERHOME path it was built at, and provides a
# single "amber-build" view that puts $AMBERHOME/bin on PATH and sets AMBERHOME. It is
# designed to be loaded ALONGSIDE the amber uenv (for CUDA/MPI/Python/...), not standalone:
#
#   uenv start amber/26.6:rc3,amber-build/2026:v1 --view=amber,amber-build
#
# Called automatically by build-amber.sh after a successful install. Can also be run by hand:
#
#   export AMBERHOME=/path/to/amber26   # an existing Amber install (built with build-amber.sh)
#   ./squash-amber.sh
#
set -euo pipefail

: "${AMBERHOME:?Set AMBERHOME to an existing Amber install (e.g. \$AMBER_ROOT/amber26)}"
: "${OUTPUT:=$(dirname "$AMBERHOME")/amber-build.squashfs}"

# sanity: make sure this looks like a real Amber install
shopt -s nullglob
pmemd_bins=("$AMBERHOME"/bin/pmemd*)
shopt -u nullglob
[[ ${#pmemd_bins[@]} -gt 0 ]] || { echo "ERROR: no pmemd* executables found in $AMBERHOME/bin -- is AMBERHOME correct?" >&2; exit 1; }

echo "=================================================================="
echo " squash-amber: packaging \$AMBERHOME as the 'amber-build' uenv"
echo "   AMBERHOME : $AMBERHOME"
echo "   image     : $OUTPUT"
echo "=================================================================="

# ---------------------------------------------------------------------------
# 1. meta/env.json — a single view ("amber-build") that only adds $AMBERHOME/bin to PATH
#    (+ AMBERHOME, + LD_LIBRARY_PATH if $AMBERHOME/lib exists). It deliberately does NOT set
#    CC/CUDA_HOME/MPICC/etc: those come from the "amber" view, loaded alongside this one.
# ---------------------------------------------------------------------------
echo; echo "### [1/2] writing meta/env.json"
mkdir -p "$AMBERHOME/meta"
python3 - "$AMBERHOME" <<'PYEOF'
import json, os, sys

amberhome = sys.argv[1]

view = {
    "description": "Amber26 tools built with build-amber.sh. Load alongside the amber view for CUDA/MPI/Python.",
    "recipe_variables": {"list": {}, "scalar": {}},
    "root": amberhome,
    "env": {
        "version": 1,
        "values": {
            "list": {
                "PATH": [{"op": "prepend", "value": [f"{amberhome}/bin"]}],
            },
            "scalar": {
                "AMBERHOME": amberhome,
            },
        },
    },
}

libdir = os.path.join(amberhome, "lib")
if os.path.isdir(libdir):
    view["env"]["values"]["list"]["LD_LIBRARY_PATH"] = [{"op": "prepend", "value": [libdir]}]

env_json = {
    "name": "amber-build",
    "description": "Amber26 built with the amber uenv (does not include CUDA/MPI/Python -- load alongside amber).",
    "mount": amberhome,
    "default-view": "amber-build",
    "modules": None,
    "views": {"amber-build": view},
}

out = os.path.join(amberhome, "meta", "env.json")
with open(out, "w") as f:
    json.dump(env_json, f, indent=2)
    f.write("\n")
print(f"  -> wrote {out}")
PYEOF

# ---------------------------------------------------------------------------
# 2. mksquashfs — use the copy bundled in the amber uenv's store (a build-time-only
#    dependency, not linked into the "amber" view), falling back to PATH.
# ---------------------------------------------------------------------------
echo; echo "### [2/2] building $OUTPUT"
mksquashfs_bin="$(find /user-environment -maxdepth 4 -iname mksquashfs -type f 2>/dev/null | head -n1)"
if [[ -z "$mksquashfs_bin" ]]; then
  mksquashfs_bin="$(command -v mksquashfs || true)"
fi
[[ -n "$mksquashfs_bin" && -x "$mksquashfs_bin" ]] || {
  echo "ERROR: mksquashfs not found (expected inside the amber uenv store, e.g." >&2
  echo "       /user-environment/linux-*/squashfs-*/bin/mksquashfs). Is the amber uenv loaded?" >&2
  exit 1
}
echo "  using $mksquashfs_bin"
rm -f "$OUTPUT"
"$mksquashfs_bin" "$AMBERHOME" "$OUTPUT" -noappend

uenv_cfg="$(uenv config 2>/dev/null | awk '$1=="user:"{print $2}')"

echo
echo "=================================================================="
echo " DONE. Packaged $(du -h "$OUTPUT" | cut -f1) image: $OUTPUT"
echo
echo " The default uenv repository (\$SCRATCH/.uenv-images) lives on the same file system"
echo " this is meant to escape -- register the image in a repository on \$STORE instead:"
echo
echo "   uenv repo create \$STORE/\$USER/uenv-images    # once, if it doesn't exist"
echo "   uenv --repo=\$STORE/\$USER/uenv-images image add amber-build/2026:v1@daint%gh200 $OUTPUT"
echo
echo " So that repository is also searched (alongside the default one) without passing"
echo " --repo every time, add it to your uenv config file once (found at: ${uenv_cfg:-run 'uenv config' to find it}):"
echo
echo "   cat >> $uenv_cfg <<CFG"
echo "   [[repositories]]"
echo "   name = 'store'"
echo "   path = '\$STORE/\$USER/uenv-images'"
echo "   CFG"
echo
echo " Then use it alongside the amber uenv (the 'amber-build' view relies on 'amber' for"
echo " CUDA/MPI/Python):"
echo
echo "   uenv start amber/26.6:rc3,amber-build/2026:v1 --view=amber,amber-build"
echo
echo " Once registered, empty out $AMBERHOME's *contents* to reclaim its inodes:"
echo "   rm -rf $AMBERHOME && mkdir -p $AMBERHOME"
echo " Leave the directory itself in place -- uenv mounts onto it but does not create it,"
echo " so it must still exist (empty) at this exact path for the amber-build uenv to start."
echo "=================================================================="
