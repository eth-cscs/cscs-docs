[](){#ref-guides-terminal}
# Terminal usage on Alps

This documentation is a collection of guides, hints, and tips for setting up your terminal environment on Alps.

[](){#ref-guides-terminal-shells}
## Shells

Every user has a shell that will be used when they log in, with [bash](https://www.gnu.org/software/bash/) as the default shell for new users at CSCS.

!!! example "Which shell am I using?"

    Run the following command after logging in:

    ```console
    $ echo $SHELL
    /usr/local/bin/bash
    ```

!!! tip
    If you would like to change your shell, for example to [zsh](https://www.zsh.org), you have to open a [service desk](https://jira.cscs.ch/plugins/servlet/desk) ticket to request the change. You can't make the change yourself.


!!! warning
    If you are comfortable with another shell (like Zsh or Fish), you are welcome to switch.
    Just keep in mind that some tools and instructions might not work the same way outside of `bash`.
    Since our support and documentation are based on the default setup, using a different shell might make it harder to follow along or get help.
    
    We strongly recommend against using cshell - tools like uenv are not tested against it.

[](){#ref-guides-terminal-arch}
## Managing x86 and ARM

Alps has nodes with different CPU architectures, for example [Santis][ref-cluster-santis] has ARM (Grace `aarch64`) processors, and [Eiger][ref-cluster-eiger] uses x86 (AMD Rome `x86_64`) processors.
Binary applications are generally not portable, for example if you compile or install a tool compiled for `x86_64` on Eiger, you will get an error when you run it on an `aarch64` node.

??? warning "cannot execute binary file: Exec format error"
    You will see this error message if you try to execute an executable built for a different architecture.

    In this case, the `rg` executable built for `aarch64` (Grace-Hopper nodes) is run on an `x86_64` node on [Eiger][ref-cluster-eiger]:
    ```
    $ ~/.local/aarch64/bin/rg
    -bash: ./rg: cannot execute binary file: Exec format error
    ```

A common pattern for installing local software, for example some useful command line utilities like [ripgrep](https://github.com/BurntSushi/ripgrep), is to install them in `$HOME/.local/bin`.
This approach won't work if the same home directory is mounted on two different clusters with different architectures: the version of ripgrep in our example would crash with `Exec format error` on one of the clusters.

Care needs to be taken to store executables, configuration and data for different architectures in separate locations, and automatically configure the login environment to use the correct location when you log into different systems.

The following example:

* sets architecture-specific `bin` path for installing programs
* sets architecture-specific paths for installing application data and configuration
* selects the correct path by running `uname -m` when you log in to a cluster

```bash title=".bashrc"
# Set the "base" directory in which all architecture specific will be installed.
# The $(uname -m) command will generate either x86_64 or aarch64 to match the
# node type, when run during login.
xdgbase=$HOME/.local/$(uname -m)

# The XDG variables define where applications look for configurations
export XDG_DATA_HOME=$xdgbase/share
export XDG_CONFIG_HOME=$xdgbase/config
export XDG_STATE_HOME=$xdgbase/state

# set PATH to look for in architecture specific path:
# - on x86: $HOME/.local/x86_64/bin
# - on ARM: $HOME/.local/aarch64/bin
export PATH=$xdgbase/bin:$PATH
```

!!! note "XDG what?"
    The [XDG base directory specification](https://specifications.freedesktop.org/basedir-spec/latest/) is used by most applications to determine where to look for configurations, and where to store data and temporary files.

[](){#ref-guides-terminal-bashrc}
## Modifying bashrc

The `~/.bashrc` in your home directory is executed __every time__ you log in, and there is no way to log in without executing it.

It is strongly recommended that customization in `~/.bashrc` should be kept to the bare minimum:

1. It sets a fixed set of environment options every time you log in, and all downstream scripts and Slurm batch jobs might assume that these commands have run, so that later modifications to `~/.bashrc` can break workflows in ways that are difficult to debug.
    * If a script or batch job requires environment modifications, implement them there.
    * In other words, move the definition of environment used by a workflow to the workflow definition.
1. It makes it difficult for CSCS to provide support, because it is difficult for support staff to reproduce your environment, and it can take a lot of back and forth before we determine that the root cause of an issue is a command in `~/.bashrc`.


!!! warning "Do not call `module` in bashrc"
    Calls to `module use` and `module load` in `~/.bashrc` is possible, however avoid it for the reasons above.
    If there are module commands in your `~/.bashrc`, remember to provide a full copy of `~/.bashrc` with support tickets.

!!! danger "Do not call `uenv` in bashrc"
    The `uenv` command is designed for creating isolated environments, and calling it in `~/.bashrc` will not work as expected.
    See the [uenv docs][ref-uenv-customenv] for more information about how to create bespoke uenv environments that can be started with a single command.

??? note "Help, I broke bashrc!"
    It is possible to add commands to bashrc that will stop you from being able to log in.
    The author of these docs has done it more than once, after ignoring their own advice.

    For example, if the command `exit` is added to `~/.bashrc` you will be logged out every time you log in.

    The first thing to try is to execute a command that will back up `~/.bashrc`, and remove `~/.bashrc`:
    ```bash
    ssh eiger.cscs.ch 'bash --norc --noprofile -c "mv ~/.bashrc ~/.bashrc.back"'
    ```
    If this works, you can then log in normally, and edit the backup and copy it back to `~/.bashrc`.

    If there is a critical error, like calling `exit`, the approach above won't work.
    In such cases, the only solution that doesn't require root permissions is to log in and hit `<ctrl-c>` during the log in.
    With luck, this will cancel the login process before `~/.bashrc` is executed, and you will be able to edit and fix `~/.bashrc`.
    Note that you might have to try a few times to get the timing right.

    If this does not work, create a [service desk ticket][ref-get-in-touch] with the following message:

    !!! example "Help request"
        My bashrc has been modified, and I can't log in any longer to `insert-system-name`.
        My username is `insert-cscs-username`.
        Can you please make a backup copy of my bashrc, i.e. `mv ~/.bashrc ~/.bashrc.back`,
        so that I can log in and fix the issue.

