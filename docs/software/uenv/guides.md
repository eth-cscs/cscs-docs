[](){#ref-uenv-guides}
# uenv guides

[](){#ref-uenv-labels}
## uenv labels

Uenv are referred to using **labels**, which are used to refer to specific uenv, or groups of uenv, with the uenv command line tool.
Each label has the following form:

```
name/version:tag@system%uarch
```

The different fields are described in the following table:

| label | meaning |
|-------|---------|
| `name`    | name of the uenv, e.g. `gromacs`, `prgenv-gnu`  |
| `version` | version of the uenv: e.g. `v8.7`, `2025.01` |
| `tag`     | a tag applied by CSCS     |
| `system`  | name of the system/cluster, e.g. `daint`, `clariden`, `eiger` or `santis` |
| `uarch`   | node microarchitecture: one of `gh200`, `a100`, `zen2`, `mi200`, `mi300a`, `zen3`    |

!!! example "Example labels"
    ??? note "`prgenv-gnu/24.11:v2@daint%gh200`"
        The `prgenv-gnu` programming environment, built on [Daint][ref-cluster-daint] for the Grace-Hopper GH200 (`gh200`) architecture.

        * the _version_ is `24.11`, referring to the December 2024 version.
        * the _tag_ `v2` refers to a minor update to the uenv (e.g. a bug fix or addition of a new package).

    ??? note "`cp2k/2025.1:v3@eiger%zen2`"
        The uenv provides version 2025.1 of the CP2K simulation code, built for the AMD Rome (`zen2`) architecture of [Eiger][ref-cluster-eiger].

        * the _version_ `2025.1` refers to the CP2K version [v2025.1](https://github.com/cp2k/cp2k/releases/tag/v2025.1)
        * the _tag_ `v2` refers to a minor update by CSCS to the original `v1` version of the uenv that had a bug.

For more information about the labeling scheme, see the [uenv deployment][ref-uenv-deploy-versions] docs.

[](){#ref-uenv-labels-examples}
### Using labels

The uenv command line interface (CLI) has a flexible interface for filtering uenv by providing only part of the full label.
Below are some examples of using labels with the CLI (see documentation for the individual commands for more information):

```bash
# search for all uenv on the current system that have the name prgenv-gnu
uenv image find prgenv-gnu

# search for all uenv with version 24.11
uenv image find /24.11

# search for all uenv with tag v1
uenv image find :v1

# search for a specific version
uenv image find prgenv-gnu/24.11:v1
```

By default, `uenv` filters results to uenv that were built for the current cluster to match the `system` field in the label.
The name of the current cluster is always available via the `CLUSTER_NAME` environment variable.

```console
# log into eiger
$ ssh eiger

# this command will search for all prgenv-gnu uenv on eiger
$ uenv image find prgenv-gnu

# use @ to search on a specific system, e.g. on daint:
$ uenv image find prgenv-gnu@daint

# this can be used to search for all uenv on daint:
$ uenv image find @daint

# use '*' as a wildcard used meaning "all systems"
# this will show all images on all systems
uenv image find @*

# search for all images on Alps that were built for gh200 nodes.
uenv image find @*%gh200
```

[](){#ref-uenv-customenv}
## Custom environments

!!! warning "[Keep bashrc clean][ref-guides-terminal-bashrc]"

It is common practice to add `module` commands to `~.bashrc`, for example
```bash title="~/.bashrc"
# make my custom modules available
module use $STORE/myenv/modules
# load the modules that I always want in the environment
module load ncview
```

This will make custom modules available, and load `ncview`, every time you log in.
It is not possible to do the equivalent with `uenv start`, for example:
```bash title="~/.bashrc"
# start the uenv that I always use
uenv start prgenv-gnu/24.11:v2 --view=default
# ERROR: the following lines will not be executed
module use $STORE/myenv/modules
module load ncview
```

!!! question "Why can't I use `uenv start` in `~/.bashrc`?"
    The `module` command uses some "clever" tricks to modify the environment variables in your current shell.
    For example, `module load ncview` will modify the value of environment variables like `PATH`, `LD_LIBRARY_PATH`, and `PKG_CONFIG_PATH`.

    The `uenv start` command loads a uenv, and __starts a new shell__, ready for you to enter commands.
    This means that lines in the `.bashrc` that follow the command are never executed.

    Things are further complicated because if `uenv start` is executed inside `~/.bashrc`, the shell is not a tty shell.

It is possible to create a custom command that will start a new shell with a uenv loaded, with additional customizations to the environment (e.g. loading modules and setting environment variables).

The first step is to create a script that performs the the customization steps to perform once the uenv has been loaded.
Here is an example for an environment called `myenv`:

```bash title="~/.myenvrc"
# always add this line
source ~/.bashrc

# then add customization commands here
module use $STORE/myenv/modules
module load ncview
export DATAPATH=$STORE/2025/data
```

Then create an alias in `~/.bashrc` for the `myenv` environment:

```bash title="~/.bashrc"
alias myenv='uenv run prgenv-gnu/24.11:v2 --view=default -- bash --rcfile ~/.myenvrc'
```

This alias uses `uenv run` to start a new bash shell that will apply the customizations in `~/.myenvrc` once the uenv has been loaded.
Then, the environment can be started with a single command once logged in.

```console
$ ssh eiger.cscs.ch
$ myenv
```

The benefit of this approach is that you can create multiple environments, whereas modifying `.bashrc` would lock you into using the same environment every time you log in.

[](){#ref-uenv-uninstall}
## Uninstalling the uenv tool

It is strongly recommended to use the version of uenv installed on the system, instead of installing your own version from source.
This guide walks through the process of detecting if you have an old version installed, and removing it.

!!! note
    In the past CSCS has recommended installing a more recent version of uenv to help fix issues for some users.
    Some users still have old self-installed versions installed in `HOME`, so they are missing out on new uenv features, and possibly seeing errors on systems with the most recent `v9.0.0` uenv installed.

!!! warning "error caused by incompatible uenv version"
    If trying to use `uenv run` or `uenv start`, and you see an error message like the following:

    ```
    error: unable to exec '/capstor/scratch/cscs/wombat/.uenv-images/images/61d1f21881a6....squashfs:/user-environment':
    No such file or directory (errno=2)
    ```

    Then you are probably using an old version of uenv that is not compatible with the version of `squashfs-mount` installed on the system.

First, log into the target cluster, and enter `type uenv` and inspect the output.

The system version of `uenv` is installed in `/usr/bin`, so if you see the following you do not need to make any changes:

```console
$ type uenv
uenv is /usr/bin/uenv
```

Version 5 of uenv used a bash function called `uenv`, which will give output that looks like this:

```console
$ type uenv
uenv is a function
uenv ()
{
    local _last_exitcode=$?;
    function uenv_usage ()
    {
...
```

If you have installed version 6, 7, 8 or 9, it will be in a different location, for example:

```console
$ type uenv
uenv is /users/voldemort/.local/bin/uenv
```

??? question "why not use `which uenv`?"
    The `which uenv` command searches the directories listed in the `PATH` environment variable for the `uenv` executable, and ignores bash functions.
    If there is a `uenv` bash function is set, then it will be take precedence over the `uenv` executable found using `which uenv`.

To remove uenv version 6, 7, 8 or 9, delete the executable, then force bash to forget the old command.

```console
# remove your self-installed executable
$ rm $(which uenv)

# forget the old uenv command
$ hash -r

# type and which should point to the same executable in /usr/bin
$ type uenv
uenv is /usr/bin/uenv
$ which uenv
/usr/bin/uenv
```

To remove version 5, look in your `.bashrc` file for a line like the following and remove or comment it out:

```bash
# configure the user-environment (uenv) utility
source /users/voldemort/.local/bin/activate-uenv
```

Log out and back in again, then issue the following command to force bash to forget the old uenv command:
```console
# forget the old uenv command
$ hash -r

# type and which should point to the same executable in /usr/bin
$ type uenv
uenv is /usr/bin/uenv
$ which uenv
/usr/bin/uenv
```

