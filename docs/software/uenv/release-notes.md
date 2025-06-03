[](){#ref-uenv-release-notes}
# uenv releases notes

The latest version of uenv deployed on [Alps clusters][ref-alps-clusters] is **v8.1.0**.
You can check the version available on a specific system with the `uenv --version` command.

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

