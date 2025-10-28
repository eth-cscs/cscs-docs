[](){#ref-uenv-release-notes}
# uenv releases notes

The latest version of uenv deployed on [Alps clusters][ref-alps-clusters] is **v8.1.0**.
You can check the version available on a specific system with the `uenv --version` command.

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

!!! warning "bash: module: command not found"
    This is a known issue with version 9.0.0 that will be fixed in 9.0.1.
    See the [uenv modules][ref-uenv-error-v9modules] docs for a workaround.

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

