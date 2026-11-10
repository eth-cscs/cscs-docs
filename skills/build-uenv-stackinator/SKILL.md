---
name: build-uenv-stackinator
description: Build a uenv (SquashFS software-stack image) on Alps HPC systems using Stackinator and Spack. Use when the task involves creating, configuring, building, debugging, or iterating on a uenv — writing or editing a Stackinator recipe (config.yaml, compilers.yaml, environments.yaml, packages.yaml), running stack-config, building store.squashfs, resolving Spack concretization/build failures inside the bubblewrap sandbox, fixing runtime issues in views, or testing an image with `uenv run`.
---

# Building a uenv with Stackinator

A uenv is a SquashFS image containing a Spack-built software stack, mounted on Alps HPC nodes. Stackinator turns a *recipe* plus a *cluster config* into a build directory, then orchestrates the Spack build inside a bubblewrap sandbox.

## A uenv image is just a SquashFS file

`store.squashfs` is an ordinary SquashFS archive whose filesystem root becomes the mount point. Nothing about it is uenv-specific except one metadata file, and nothing requires its contents to have come from Spack.

```bash
unsquashfs -l store.squashfs             # list contents, no mount needed
unsquashfs -d out store.squashfs meta    # extract a single path
mksquashfs <dir> image.squashfs          # build one by hand
```

At the root of the image — i.e. at the mount point:

| Path | What it is |
|---|---|
| `meta/env.json` | the only file `uenv` itself reads: `name`, `description`, `mount`, `views`, `modules` |
| `meta/recipe/` | a copy of the recipe that built the image |
| `env/<view>/` | the views: `bin`, `lib`, … symlink farms that land on the user's `PATH` |
| `linux-<uarch>/` | the Spack install prefixes |
| `.spack-db/` | the Spack database describing them |

Three consequences worth knowing:

- **The mount point is baked into the contents.** Spack writes absolute prefixes and RPATHs, so the build-time `store:` must equal the runtime mount point. `store:` is a real decision, not a label — and with `mount_specific: true` it also selects which build cache is warm.
- **Mounting is separate from uenv.** `uenv start` / `uenv run` are conveniences over `squashfs-mount`, a setuid helper that mounts images at arbitrary paths in a new mount namespace:
  ```bash
  squashfs-mount -s store.squashfs:/user-tools -- bash
  ```
  (In squashfs-mount 10, images go in `-s`; positional arguments are the command to run.)
- **The contents do not have to come from Spack.** A `post-install` hook can put anything into the store — unpacked RPMs, extracted tarballs, wrapper scripts — provided it works when mounted at `store:`. Spack is the usual way to fill a uenv, not a property of the format. This is the route for software Spack does not package.

**A uenv session is a one-way door.** `squashfs-mount` sets `PR_SET_NO_NEW_PRIVS` before handing control back (symbol `return_to_user_and_no_new_privs`), which permanently disables setuid for that process tree. So inside a uenv session nothing can mount another image — `uenv start`/`uenv run` refuse outright (*"a uenv session is already running"*), and `squashfs-mount`, `squashfuse` and rootless `podman` all fail with permission errors. Two images have to be requested together at session start, at different mount points:

```bash
uenv start prgenv-gnu/24.7:v3,editors/24.7:v1     # /user-environment + /user-tools
```

This matters when designing an image whose software launches other software: an application started from inside a uenv session cannot itself start a uenv. If users must be able to load a uenv *from* the tool, the tool's image has to be mounted outside a session — at boot, like `/mch-environment` — rather than started with `uenv start`.

## Prerequisites

- **Stackinator** — provides `stack-config`. No install step: run `stackinator/bin/stack-config` directly; it bootstraps its own dependencies with `uv` on first use.
- **Cluster config** — per-vCluster system externals and network config, passed with `-s`.
- **Recipe** — the directory of YAML described below, passed with `-r`.
- **`mirrors.yaml`** — source and build caches, passed with `--mirror`. Optional, but a cold build cache means building everything from source.
- **Build directory** — must NOT be under `/tmp`, `$HOME`, or `/` (sandbox bind-mount restriction). `/dev/shm/$USER/build` is fast and works.

## Setting up a build from scratch

When nothing is set up yet, put the three repos, the recipe and the mirror config in one working directory:

```bash
mkdir -p ~/work/<project> && cd ~/work/<project>
git clone https://github.com/eth-cscs/stackinator.git            # stack-config
git clone https://github.com/eth-cscs/alps-cluster-config.git    # -s argument
git clone https://github.com/eth-cscs/alps-uenv.git              # recipes to crib from
```

**Pick the cluster config**: `alps-cluster-config/<cluster>`, where `<cluster>` is `$CLUSTER_NAME` — also the `system` column of `uenv image ls`.

**Start from an existing recipe, not a blank one.** Copy a `prgenv-gnu` recipe and delete everything the new image does not need; it inherits choices already known to work on Alps:

```bash
mkdir -p recipes/<name>
cp alps-uenv/recipes/prgenv-gnu/<version>/<uarch>/{config,compilers,environments}.yaml recipes/<name>/
```

Match `<uarch>` to the target system (`gh200`, `a100`, `mc`, `amdgpu`). Then strip hard — for a stack that needs neither MPI nor GPU:

- `config.yaml` — set `name`, `store` (the mount point), `description`, `version: 3`. Set `default-view` only when one view is obviously the one to load.
- `compilers.yaml` — `gcc: version: "system"` unless the image must build another compiler. This skips a full gcc bootstrap and is a large saving.
- `environments.yaml` — delete the whole `network:` block (it defaults to no MPI), delete `variants:` (`+mpi`, `+cuda`, `cuda_arch=`), and cut `specs:` to what the image is actually for.
- Delete `modules.yaml` unless users will `module load`, and delete `extra/`.

**Write `mirrors.yaml`.** Find the existing cache in `$SCRATCH` — it is the directory containing a `push-key.gpg`:

```bash
find $SCRATCH -maxdepth 3 -name 'push-key.gpg' 2>/dev/null
```

```yaml
buildcache:
  url: /scratch/<...>/uenv-cache          # a `file://` URL is also accepted
  private_key: /scratch/<...>/uenv-cache/push-key.gpg
  mount_specific: true
sourcecache:
  path: /scratch/<...>/uenv-cache
```

`mount_specific: true` partitions the build cache **by mount point** (`<cache>/user-tools` vs `<cache>/user-environment`). Choosing a `store:` that the cache has never been built for gives a cold cache and a full from-source build — expect it, or reuse the mount point the cache was filled for.

Confirm the caches were actually wired up before starting a long build: `config/mirrors.yaml` and `config/config.yaml` in the build directory should name them.

## Build workflow

### Phase 0 — Check where the build will run

A stack build is CPU- and memory-heavy and runs for minutes (warm cache) to hours (cold cache, torch/LLVM/gcc from source). Before configuring, check the host:

```bash
echo "job=${SLURM_JOB_ID:-none} nodelist=${SLURM_JOB_NODELIST:-none} host=$(hostname)"
[ -n "$SLURM_JOB_ID" ] && scontrol show hostnames "$SLURM_JOB_NODELIST" | grep -qx "$(hostname)" && echo "on a node of the job"
nproc                                              # cores this shell may use (respects the job's cpuset)
free -g | awk 'NR==2{print "memory available (GiB):", $7}'
df -h /dev/shm | tail -1                           # the build directory lives here, and it is RAM
[ -n "$SLURM_JOB_ID" ] && squeue -j "$SLURM_JOB_ID" -h -o 'time_left=%L nodes=%D cpus=%C'
```

Then decide:

- **On a compute node of a Slurm job** (`SLURM_JOB_ID` is set and `hostname` is in the job's node list): build here, with this node's resources. Do not send the build to other nodes with `sbatch`/`srun`: the allocation (often a reservation of one node) is for this work.
- **Not in a Slurm job, or not on one of its nodes** (a login node, or a shell that inherited `SLURM_JOB_ID`): stop and ask the user to consider moving to a compute node before building. Login nodes are shared, have fewer cores and memory limits, and a cold build there takes hours and slows other users. Suggest `salloc -N1 --time=04:00:00` (plus `--reservation=...` / `--account=...` as appropriate) and restarting the session on that node. Continue on the login node only if the user confirms (e.g. a small stack or a fully warm build cache).

Check the resources, and **warn the user** when they are insufficient:

- **Cores**: if `nproc` is below about 32, warn that a cold build of a large stack will take many hours, and suggest a full node (`--exclusive`, or `--cpus-per-task` set to the node's core count). `nproc` can be lower than the node's core count when the job did not request all CPUs: check it, not the hardware.
- **Memory**: `/dev/shm` counts against node memory, and CUDA-heavy packages need several GB per compiler process (torch's flash-attention units: 6-7 GB per `cicc`; TE and flash-attn templates: 4-12 GB). Warn if less than about 4 GiB is available per build job.
- **Time**: compare the time left with the expected build time. If the job may end first, warn, and schedule `make cache-force` (push installed packages to the build cache) shortly before the end so a later build can resume.

Choose `NJOBS` from what is available, not a fixed number: `NJOBS = min(nproc, available memory GiB / 8)`, rounded down. For example, a GH200 node (288 cores, ~850 GiB) builds a torch stack safely with `NJOBS=64` (measured peak 489 GiB); `NJOBS=128` risks running out of memory while torch and other CUDA packages compile at the same time. Use smaller values on shared or partial nodes.

### Phase 0b — Check for prior build notes

When given an existing recipe as a starting point, **read `README.md` in the root of the recipe directory first** (if present). It records findings from the last build of this recipe — custom Spack packages that were created, concretization workarounds, external-package overrides, runtime fixes, and other gotchas. Use these notes as hints before configuring or building.

### Phase 1 — Configure

```bash
stack-config \
  -r /path/to/recipe/ \
  -s /path/to/cluster-config/ \
  -b /dev/shm/$USER/build \
  --mirror=/path/to/mirrors.yaml
```

Generates the build directory (Makefile + spack.yaml) and clones Spack.

### Phase 2 — Build

```bash
cd /dev/shm/$USER/build
env --ignore-environment PATH=/usr/bin:/bin:`pwd -P`/spack/bin HOME=$HOME make store.squashfs NJOBS=$NJOBS
```

- `env --ignore-environment` guarantees a clean build environment.
- `NJOBS` controls parallelism (choose it in Phase 0 from the cores and memory available); the build runs inside a bubblewrap sandbox.
- Output is `store.squashfs` — the final uenv image.

### Phase 3 — Record build notes

On a successful build, **create (or update) `README.md` in the root of the recipe directory** with notes about the build. This is the counterpart to Phase 0b — write down what a future build of this recipe would want to know. In particular:
- **Custom Spack packages** created in `repo/` — what they are, why they were needed, and what they change (patches, variants, versions). Call these out explicitly; they are the most valuable notes.
- Concretization workarounds (unify strategy, pinned versions, variant flags).
- External-package overrides added to `packages.yaml` and why.
- Post-install / pre-install hooks and what they fix.
- Runtime fixes applied and any host dependencies the image relies on.
- Anything surprising or hard-won during the build.

Keep it concise and factual — it is a build log for the next person (or the next build), not user-facing documentation. If a `README.md` already exists, update the relevant sections rather than overwriting wholesale.

### Iterating

Edit recipe YAML → re-run `stack-config` → re-run `make store.squashfs`. Re-running `stack-config` over an existing build directory is safe: it regenerates the config and updates the cloned Spack repos in place.

Individual targets speed up iteration:
- `make env/spack.lock` — concretize only; the fast check that the specs resolve. **There is no `make concretize` target.**
- `make install` — build the packages.
- `make store.squashfs` — package the image (the default target).

For rapid prototyping (e.g. testing a script change), edit files directly in the store path (`$BUILD/store/`) and re-run `make store.squashfs` — repackaging takes seconds. Once validated, implement the change properly in the recipe (post-install hook, custom package, etc.).

## Recipe structure

A recipe is a directory of YAML files. See `references/recipe-files.md` for the full field-by-field breakdown, examples, and key decisions for each of:
- `config.yaml` (required) — name, store/mount point, spack version, default-view, cleanup, version.
- `compilers.yaml` (required) — compiler versions; `"system"` skips building gcc.
- `environments.yaml` (required) — specs, compiler, unify strategy, network/mpi, and views.
- `packages.yaml` (optional) — external package overrides.
- `modules.yaml` (optional) — module file generation.
- `repo/` (optional) — custom Spack packages (last resort — prefer fixing upstream via variants/specs/externals).
- `post-install` / `pre-install` (optional) — shell scripts run inside the sandbox before/after the Spack build.

Read `references/recipe-files.md` before writing or editing any recipe file.

## Cluster config

Provided via `-s`; not authored per-recipe but must be understood:
- `packages.yaml` — system external packages. **Must include `gcc`** (with `extra_attributes.compilers` paths).
- `network.yaml` — MPI/network libraries. Irrelevant for non-MPI stacks.

## Debugging

- **Failed package logs**: the sandbox mounts `$BUILD/tmp` at `/tmp`. Spack prints log paths as `/tmp/...` but the real file is at `$BUILD/tmp/...`. E.g. a reported `/tmp/$USER/spack-stage/.../foo.log` lives at `/dev/shm/$USER/build/tmp/$USER/spack-stage/.../foo.log`. Check the tail for the real compile/link error.
- **Stackinator configure log**: `/tmp/$USER/log_stackinator_*`.
- **Debug shell inside the sandbox**: run `./stack-debug.sh` in the build directory.
- **Run commands non-interactively in the sandbox**: `stack-debug.sh` opens an *interactive* shell. To script the exact build environment — query the store DB, run `jq`, patch files, compile a test — copy the `env … bwrap-mutable-root.sh …` line from `stack-debug.sh` and replace the trailing `bash -noprofile -l` with `bash -noprofile -lc "<commands>"`. This is the reliable way to inspect or edit the store before repackaging: the store only exists at its mount point (`/user-environment`) *inside* the sandbox. Resolve a package's concrete prefix from the store DB with `spack find --format "{prefix}" "<spec>"`.
- **Spack directly**: `cd $BUILD && spack -e . find` or `spack -e . spec <package>`.

## Common issues

- **Concretization failures**: conflicting package requirements. Try `unify: when_possible` or adjust variant flags.
- **Missing externals**: if Spack builds something that should come from the system, add it to the recipe `packages.yaml` with `buildable: false`.
- **Build path restrictions**: cannot use `/tmp`, `$HOME`, or `/`.
- **`Error: cannot concretize 'X', since 'X' does not exist`**: the pinned `spack.packages.commit` in `config.yaml` predates the package. Check the package exists at that commit (`ls repos/builtin/repos/spack_repo/builtin/packages/<X>` in the build directory) and bump the commit if not.
- **Everything rebuilds from source**: the build cache is keyed by mount point when `mount_specific: true`. A new `store:` value has no cache behind it. `no binary available` for packages you know are cached is the tell.
- **`env: '/bin/mksquashfs': No such file or directory`** at the image step: `spack gc` in the `cleanup` target has uninstalled the `squashfs` package that Stackinator added internally, because it is not an explicit root (look for `Successfully uninstalled squashfs` earlier in the log). The path in the recipe collapses to `/bin/mksquashfs`, which does not exist. Add `squashfs` to the environment's `specs` and `exclude` it from the view.
- **`specs: null ... is not valid under any of the given schemas`**: the environment has an empty `specs` list. Stackinator accepts it; Spack does not. Give the environment at least one spec.
- **Large images**: use `cleanup: runtime` (config.yaml), `link: run` in views, and avoid heavy deps (e.g. `mesa~llvm` to skip LLVM).
- **Custom-package post-install steps must be idempotent**: Stackinator builds a package, pushes it to the build cache, then reinstalls it from the cache — so a custom package's `@run_after("install")` file mutation (and other install-time file edits) can run *more than once* on the same prefix. A non-idempotent in-place edit (appending a block, injecting an rpath line) corrupts the file on the second pass, and the failure surfaces far downstream. Regenerate from a preserved pristine copy, or guard so re-application is a no-op.

## Fixing runtime issues

When a uenv builds but packages fail at runtime, escalate through these approaches (see `references/runtime-fixes.md` for detail):
1. **Missing files in the view** — only explicit specs (and their runtime deps) get linked. Add the needed package as an explicit spec (e.g. a transitive dep whose files must appear in `XDG_DATA_DIRS`).
2. **Environment variables** — set them in the view definition (`env.set` / `env.prepend_path`) in `environments.yaml`.
3. **Post-install hook** — arbitrary modifications: edit `meta/env.json`, patch installed prefixes, add wrapper scripts. May require a clean rebuild.
4. **Custom package** — last resort, only when the fault is in the Spack package's build logic.

## Testing images

**Verify the headline feature actually works — not just that the build finished.** A build can complete successfully while its main capability is broken (e.g. a compiler that builds but can't link or run its target, a plugin that isn't on the view's search path). Exercise the real workflow end-to-end: compile *and run* a representative program, load the library, drive the tool — don't stop at "the binary is on `PATH`". If the image's purpose is offload/GPU, run something that forces the GPU (e.g. `OMP_TARGET_OFFLOAD=MANDATORY`) so a silent host fallback fails loudly.

Use `uenv run` (NOT `uenv start`) to test a built image:

```bash
# Run a command inside the uenv (default-view applies automatically if set in config.yaml)
uenv run /dev/shm/$USER/build/store.squashfs -- which Xvnc

# Specify a view name explicitly when there is no default-view
uenv run /dev/shm/$USER/build/store.squashfs vnc -- which Xvnc

# Inspect available views
uenv inspect /dev/shm/$USER/build/store.squashfs
```

If running from `/dev/shm` fails with `error: unable to exec 'bash': Input/output error (errno=5)` although the image is complete (`unsquashfs -s` reads its header), copy it to a regular filesystem (e.g. `$SCRATCH`) and run it from there. This was seen on daint GH200 nodes (2026-11-05): the same image mounted from `$SCRATCH` worked. Copying the image off `/dev/shm` is worthwhile anyway: `/dev/shm` disappears when the job ends.

## Reference material

- `references/recipe-files.md` — full recipe file reference with annotated examples and per-field decisions.
- `references/runtime-fixes.md` — detailed runtime-issue remediation.
- `references/vnc-example.md` — worked example: design decisions for a VNC/remote-visualization uenv on GH200 (what to bundle, what to rely on from the host, GPU/EGL notes).

## Updates

This skill is published by CSCS at <https://docs.cscs.ch/agents/>.
When the user asks to install or update the CSCS agent skills, follow the instructions on that page.
