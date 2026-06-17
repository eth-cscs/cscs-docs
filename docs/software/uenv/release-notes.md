[](){#ref-uenv-release-notes}
# uenv release notes

The latest version of uenv deployed on [Alps clusters][ref-alps-clusters] is **v10.0.1**.
You can check the version available on a specific system with the `uenv --version` command.

[](){#ref-uenv-release-notes-v10.0}
## v10.0

### Features

- [TOML configuration format][ref-uenv-configure] and [improved repository management][ref-uenv-repo-multiple]: multiple named repositories can be configured and selected by name.
- [Default views][ref-uenv-views]: uenv images can declare a view to load automatically when no `--view` flag is given.
- Advanced Slurm workflows: the [`--uenv-passthrough`][ref-uenv-slurm-passthrough] flag controls whether a loaded uenv is forwarded to nested `srun`, `sbatch`, or `salloc` calls.
- New global `--system` flag to override the cluster name on the CLI (e.g. `uenv --system='*' image find`).
- Improved bash completion for uenv labels and file paths.

### Fixes

- Changed a hard error to a warning when image metadata is not attached in the registry.
- Fixed a latent bug parsing date strings in image metadata.

### Known issues

[](){#ref-uenv-release-notes-v10-passthrough}
!!! warning "calling `sbatch` from inside a uenv session is now an error"
    Starting with uenv v10, submitting a job with `sbatch` or `salloc` from inside an active `uenv start` session fails by default.
    See the [passthrough documentation][ref-uenv-slurm-passthrough] for how to handle this.

### Minor and patch releases

[](){#ref-uenv-release-notes-v10.0.1}
??? info "v10.0.1 feature release"
    - `uenv status`: fix bug when no view was loaded, or when the name in the uenv meta data did not match that in the database.

[](){#ref-uenv-release-notes-v9.0.0}
## v9.0.0

This [version](https://github.com/eth-cscs/uenv2/releases/tag/v9.0.0) will replace v8.1.0 on Alps clusters.

### Features

- elastic logging.
- Add `--json` option to `image ls` and `image find`.
- add `--format` flag to uenv status.

### Improvements

- force unsquashfs to use a single thread when unpacking meta data.
- reimplement squashfs-mount in the main repository.
- improve file name completion in bash.

### Fixes

- Turn some CLI flags into options, so that they can be set with or without `=`. e.g. `uenv --repo=$HOME/uenv` or `uenv --repo $HOME/uenv`.
- Only use the meta data path adjacent to a uenv image if it contains an env.json file.
- `image push` was not pushing the correct meta data path.
- a bug where the `--only-meta` flag was ignored on `image pull`.
- add hints to error message when uenv is not found.

[](){#ref-uenv-release-notes-v9.0.0-issues}
### Known issues

!!! warning "user-installed uenv stopped working"
    This version introduced changes to the `squashfs-mount` tool used by `uenv start` and `uenv -run` that are incompatible with older versions of uenv.
    If you see errors that contain `error: unable to exec '...': No such file or directory (errno=2)`, follow the guide for [uninstalling user-installed uenv][ref-uenv-uninstall].

??? warning "bash: module: command not found"
    This is a known issue with version 9.0.0 that was fixed in 9.0.1, and should no longer be an issue on Alps.
    See the [uenv modules][ref-uenv-error-v9modules] docs for a workaround.

### Minor and patch releases

[](){#ref-uenv-release-notes-v9.2.0}
??? info "v9.2.0 feature release"
    - [feature] `uenv image inspect` — inspect views, mount point, and other metadata without mounting the uenv.
    - [feature] `--format` flag on `image find` and `image ls` (replaces the removed `--list` flag).
    - [feature] `uenv image find` and `uenv image ls` now accept partial uenv names.

[](){#ref-uenv-release-notes-v9.1.2}
??? info "v9.1.2 bug fix release"
    - [fix] on non-production systems fall back to `SCRATCH` as the default repository location (required for systems like Balfrin)
    - [fix] `uenv image add` works when the image provided is already inside the repo (i.e. retagging is properly supported)

[](){#ref-uenv-release-notes-v9.1.1}
??? info "v9.1.1 bug fix release"
    - [fix] rename cluster field in elastic logs to avoid name conflict
    - [fix] clean up `uenv status --format=views` output
    - [fix] restrict lustre striping to max 32 OST

[](){#ref-uenv-release-notes-v9.1.0}
??? info "v9.1.0 feature release"
    A feature release that focussed on managing repositories

    - [feature] add support for lustre striping and cleaning up missing images from repos
    - [feature] add `uenv repo migrate` feature

[](){#ref-uenv-release-notes-v9.0.1}
??? info "v9.0.1 bug fix release"
    - [fix] fix bash function forwarding bug that broke the module command


[](){#ref-uenv-release-notes-v8.1.0}
## v8.1.0

This version replaced v7.1.0 on Alps clusters.

### Features

* improved uenv view management
* automatic generation of default uenv repository the first time uenv is called
    * this fixes the error message
* bash completion
* support for configuration files
    * currently only support setting `color` and default uenv repo
* support for `SLURM_UENV` and `SLURM_UENV_VIEW` environment variables for use inside CI/CD pipelines.

### Small fixes

* better error messages and small bug fixes
* relative paths can be used for referring to squashfs images

