[](){#ref-guides-terminal}
# Terminal usage on Alps

This documentation is a collection of guides, hints, and tips for setting up your terminal environment on Alps.

[](){#ref-guides-terminal-shells}
## Shells

Every user has a shell that will be used when they log in, with [bash](https://www.gnu.org/software/bash/) as the default shell for new users at CSCS.

At CSCS the vast majority of users stick with the default `bash`: at the time of writing, of over 1000 users on Daint, over 99% were using bash.

!!! example "Which shell am I using?"

    Run the following command after logging in:

    ```console
    $ getent passwd | grep $USER
    bcumming:*:22008:1000:Benjamin Cumming, CSCS:/users/bcumming:/usr/local/bin/bash
    ```

    The last entry in the output points to the shell of the user, in this case `/usr/local/bin/bash`.

!!! tip
    If you would like to change your shell, for example to [zsh](https://www.zsh.org), you have to open a [service desk](https://jira.cscs.ch/plugins/servlet/desk) ticket to request the change. You can't make the change yourself.


!!! warning
    Because `bash` is used by all CSCS staff and the overwhelming majority of users, it is the best tested, and safest default.

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

Care needs to be taken to store executables, configuration and data for different architecures in separate locations, and automatically configure the login environment to use the correct location when you log into different systems.

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

