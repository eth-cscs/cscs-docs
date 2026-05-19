[](){#ref-uenv-configure}
# Configuring uenvs

The uenv tools are designed to work out of the box, with zero configuration for most users.
There is support for per-user configuration via a [TOML](https://toml.io/en/) configuration file, which can be used to set preferences and configure multiple repositories.

## User configuration

[](){#ref-uenv-configure-file}
### Configuration file

The location of the configuration file follows the [XDG base directory specification](https://specifications.freedesktop.org/basedir-spec/latest/):

* If the `XDG_CONFIG_HOME` environment variable is set, use `$XDG_CONFIG_HOME/uenv/config.toml`.
* Otherwise use the default location `$HOME/.config/uenv/config.toml`.

A system-wide configuration file may also be present at `/etc/uenv/config.toml`.
This file is managed by CSCS and sets system defaults such as the registry endpoint and elastic logging.
User settings take precedence over system settings, and CLI flags take precedence over both.

Use the [`uenv config`][ref-uenv-configure-cmd] command to inspect the active configuration.

[](){#ref-uenv-configure-syntax}
### Syntax

The configuration file uses [TOML v1.0](https://toml.io/en/) syntax.
Comments start with `#`.

!!! example "example configuration file"
    ```toml
    # enable color output
    color = true

    # override the system name (use "*" to match all clusters)
    system_name = "daint"

    # define one or more repositories
    [[repositories]]
    name = "main"
    path = "/capstor/scratch/cscs/username/.uenv-images"

    [[repositories]]
    name = "team"
    path = "/store/g123/shared/uenv-images"
    ```

[](){#ref-uenv-configure-options}
### Options

| key | description | default | values |
| --- | ----------- | ------- | ------ |
| [`color`][ref-uenv-configure-options-color] | Use color output | automatically chosen | `true`, `false` |
| [`system_name`][ref-uenv-configure-options-system] | Override the cluster name | auto-detected from `$CLUSTER_NAME` | cluster name or `"*"` |
| [`[[repositories]]`][ref-uenv-configure-options-repos] | One or more local image repositories | `$SCRATCH/.uenv-images` | array of `name`/`path` pairs |
| [`[elastic].url`][ref-uenv-configure-options-elastic] | Elastic logging endpoint | — | set by CSCS in system config |

[](){#ref-uenv-configure-options-color}
#### `color`

By default, uenv will generate color output according to the following priority:

* if `--no-color` is passed on the CLI, color output is disabled;
* else if `color` is set in the config file, use that setting;
* else if the `NO_COLOR` environment variable is defined, color output is disabled;
* else if the terminal is not a TTY, disable color;
* else enable color output.

[](){#ref-uenv-configure-options-system}
#### `system_name`

Overrides the automatic cluster detection used to filter uenv search results and labels.
By default, uenv reads the `$CLUSTER_NAME` environment variable set on each Alps cluster.

Setting `system_name = "*"` disables system filtering, showing images for all clusters.
This is equivalent to the `@*` label syntax and the `--system=*` CLI flag:

```bash title="equivalent ways to search across all systems"
# in config.toml
system_name = "*"

# via the global --system flag (overrides the config file)
uenv --system='*' image find prgenv-gnu

# via the label syntax
uenv image find prgenv-gnu@'*'
```

[](){#ref-uenv-configure-options-repos}
#### `[[repositories]]`

A repository is a directory on the file system where downloaded uenv images are stored.
Multiple repositories can be defined using the TOML array-of-tables syntax (`[[repositories]]`).
Each entry requires a `name` (used to refer to the repository) and a `path` (absolute path on disk).

```toml title="defining multiple repositories"
[[repositories]]
name = "main"
path = "/capstor/scratch/cscs/username/.uenv-images"

[[repositories]]
name = "team"
path = "/store/g123/shared/uenv-images"
```

The first repository in the list is the default — it will be used when no `--repo` flag is given.
The `--repo` CLI flag can reference a repository by name or by path, and takes precedence over the config file.

[](){#ref-uenv-configure-options-elastic}
#### `[elastic]`

!!! warning "do not modify"
    This section is set in the system configuration file at `/etc/uenv/config.toml`.
    It can only be modified by CSCS system engineers.

The elastic logging configuration used to log uenv usage in Slurm jobs.
CSCS uses this to understand uenv usage and improve the quality of the uenv service.

```toml title="elastic logging (system config only)"
[elastic]
url = "http://log.cscs.ch:31311/logs"
```

[](){#ref-uenv-configure-cmd}
## The `uenv config` command

The `uenv config` command prints the active configuration and the paths of the configuration files that were loaded.
It is useful for diagnosing configuration issues.

!!! example "inspecting the active configuration"
    ```console
    $ uenv config
    configuration-files:
      system:      /etc/uenv/config.toml
      user:        /home/username/.config/uenv/config.toml
    uenv-configuration:
      system:      daint
      repos:       main:/capstor/scratch/cscs/username/.uenv-images
      registry:    registry.cscs.ch/cscs
      color:       on
      elastic:     http://log.cscs.ch:31311/logs
    ```
