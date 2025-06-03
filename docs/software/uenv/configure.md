[](){#ref-uenv-configure}
# Configuring uenv

Uenv is designed to work out of the box, with zero configuration for most users.
There is support for limited per-user configuration via a configuration file, which will be expanded as we add features that make it easier for groups and communities to manage their own environments.

## User configuration

Uenv is configured using a text configuration file.

The location of the configuration file follows the [XDG base directory specification](https://specifications.freedesktop.org/basedir-spec/latest/), with the location defined as follows:

* If the `XDG_CONFIG_HOME` environment variable is set, use `$XDG_CONFIG_HOME/uenv/config`.
* Otherwise use the default location `$HOME/.config/uenv/config`.

### Syntax

The configuration file uses a simple `key = value` syntax, with comments starting with `#`:

```ini
# this is a comment

# the following are equivalent
color = true
color=true
```

Notes on the syntax:

* keys are case-sensitive: `color` and `Color` are not equivalent.
* all keys are lower case
* white space is trimmed from keys and values, e.g.: `color = true` will be parsed as `key='color'` and `value='true'`.

### Options

| key       | description | default     | values  |
| ---       | ----------- | --------    | ------  |
| [`color`][ref-uenv-configure-options-color]   | Use color output  | automatically chosen according to environment | `true`, `false` |
| [`repo`][ref-uenv-configure-options-repo]    | The default repo location for downloaded uenv images  | `$SCRATCH/.uenv-images`  | An absolute path |

[](){#ref-uenv-configure-options-color}
#### `color`

By default, uenv will generate color output according to the following:

* if `--no-color` is passed, color output is disabled
* else if `color` is set in the config file, use that setting
* else if the `NO_COLOR` environment variable is defined color output is disabled
* else if the terminal is not TTY disable color
* else enable color output

[](){#ref-uenv-configure-options-repo}
#### `repo`

The default repo location for downloaded uenv images.
The repo is selected according to the following process:

* if the `--repo` CLI arguement overrides 
* else if `color` is set in the config file, use that setting
* else use the default value of `$SCRATCH/.uenv-images`
