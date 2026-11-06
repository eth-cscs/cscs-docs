# Recipe files reference

A recipe is a directory containing the following YAML files (plus optional scripts and a custom repo).

## `config.yaml` (required)

```yaml
name: vnc                           # name of the uenv
store: /user-tools                  # mount point on the target system
spack:
  repo: 'https://github.com/spack/spack.git'
  commit: 'releases/v1.2'           # spack version (branch, tag, or SHA)
  packages:
    repo: https://github.com/spack/spack-packages.git
    commit: releases/v2026.06       # spack-packages version
description: tools and libraries for remote visualization connection
default-view: vnc                   # view loaded when uenv is started
cleanup: runtime                    # optional: remove build-only files
version: 3                          # must be 3 for stackinator v7
```

Key decisions:
- `store` sets the mount point. `/user-tools` is typical for tool uenvs; `/user-environment` for dev environments.
- `default-view` must match a view name defined in `environments.yaml`.
    - it does not have to be set: set when a uenv provides an obvious view that should be loaded (e.g. a debugging uenv that provides one view that exposes the debugging tool)
- `cleanup: runtime` strips build artifacts to reduce image size.
- `version: 3` is required for stackinator v7.

## `compilers.yaml` (required)

```yaml
gcc:
  version: "system"    # use "system" to skip building gcc and use the system compiler
```

- `version: "system"` uses the system gcc (avoids building gcc from source).
- A specific version like `"13"` builds gcc from source — needed when building other compilers (nvhpc/llvm).

## `environments.yaml` (required)

```yaml
vnc-tools:
  compiler: [gcc]              # which compiler(s) to use
  unify: when_possible         # concretizer strategy
  network:
    mpi: null                  # no MPI needed for this stack
  specs:
  - turbovnc
  - virtualgl
  - mesa~llvm
  - squashfs                   # see note below: required despite being added internally
  views:
    vnc:
      link: run                # only link runtime files (not build deps)
      uenv:
        add_compilers: false   # don't add compiler symlinks to view
```

Key decisions:
- `unify: when_possible` is more permissive than `true` — use it when packages have conflicting dependency requirements but only after making effort to make `true` work.
- `link: run` creates a lighter view with only runtime files (no headers, static libs, build tools).
- To ensure a package's binaries appear in the view, add it as a root spec in `specs`. Packages pulled in only as transitive dependencies may not have their binaries linked into the view.
    - determining the required root specs requires some iteration on stack-config -> make workflow.
- `network:` can be omitted entirely when MPI is not needed; it defaults to `{mpi: null, specs: null}`.
- **List `squashfs` in `specs` anyway**, even though Stackinator adds it to its own internal `uenv_tools` spec group. That internal copy is `explicit: false`, so the `cleanup` make target's `spack gc` uninstalls it again, and the image step then falls back to a bare `/bin/mksquashfs` that does not exist (`env: '/bin/mksquashfs': No such file or directory`). Listing it makes it an explicit root that survives gc. Add `exclude: [squashfs]` to the view so it does not reach users.
- `specs` may not be empty. An empty list passes Stackinator's schema but renders as `specs: null` in `env/spack.yaml`, which Spack rejects with `is not valid under any of the given schemas`. An image whose content comes from `post-install` still needs at least one spec.
- Avoid including MPI or compilers in `specs` — they are handled separately (inspect the generated `env/spack.yaml` file in the build directory.
    - it may be neccessary in some corner cases

## `packages.yaml` (optional)

Override external package definitions beyond what the cluster config provides:

```yaml
packages:
  bash:
    buildable: false
    externals:
    - prefix: /usr
      spec: bash@4.4.23
  perl:
    buildable: false
    externals:
    - prefix: /usr
      spec: perl@5.26.1
```

Use to:
- Mark system packages `buildable: false` to force system versions.
- Add externals not in the cluster config.
- Override default package preferences.

ONLY USE when strictly neccesary.
AVOID when the uenv provides libraries, tools and compilers that downstream users will want to use in Spack, because it makes the downstream Spack less likely to reuse packages in the uenv.

## `modules.yaml` (optional)

Enable module file generation. Only needed if users will load packages via `module load`.

## `repo/` (optional)

Custom Spack package definitions. Use when upstream Spack lacks a package or one needs patching.

**Prefer working with upstream definitions.** Understand the root cause of a build failure first and try to work around it (variants, added specs, `packages.yaml` externals) before resorting to a custom package. Custom packages are a maintenance burden: they must be kept in sync with upstream and can mask issues better reported upstream.

## `post-install` / `pre-install` (optional)

Executable shell scripts placed in the recipe directory, run inside the build sandbox after/before the main Spack build.

Uses:
- Install software not available as Spack packages.
- Install helper/wrapper scripts or module files.
- Modify installed packages (delete files causing runtime issues, patch configs).
- Edit `meta/env.json` to modify/add views or environment variable definitions.

Best practices:
- Comment every action: explain *what* and *why*. Future maintainers need the motivation.
- If a script **modifies files inside an installed Spack package prefix**, incremental rebuilds may not pick up the change (Spack considers the package already installed). Do a clean rebuild (`rm -rf $BUILD` and start fresh).
- If a script only **adds new files** (e.g. a helper script into a view's `bin/`) without modifying installed packages, an incremental rebuild is sufficient.
- Keep modifications minimal and well-documented — they are invisible to Spack and cause confusing behaviour if forgotten.
