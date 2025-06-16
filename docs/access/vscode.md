[](){#ref-access-vscode}
# Connecting with VS Code

[Visual Studio Code](https://code.visualstudio.com/) provides flexible support for remote development.
VS Code's [remote tunnel feature](https://code.visualstudio.com/docs/remote/tunnels) starts a server on a remote system, and connects the editor to this server.
There are two ways to set up the connection:

* using the code CLI: the most flexible method if using containers or uenv.
* using the VS Code interface: VS Code will connect onto the system, download and start the server

The main challenge with using VS Code is that the most convenient method for starting a remote session is to start a remote tunnel from the VS Code GUI.
This approach starts a session in the standard login environment on that node, however this won't work if you want to be developing in a container, in a uenv, or on a compute node.

This process is also demonstrated in a webinar on [Interactive computing on "Alps"](https://www.cscs.ch/publications/tutorials/2025/video-of-the-webinar-interactive-computing-on-alps):

<iframe width="100%"
        height="315"
        src="https://www.youtube.com/embed/cLVpJO_fE6I?si=bTmmsS_9QvTHpUqK&amp;start=2257"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
</iframe>

## Flexible method: remote server

The most flexible method for connecting VS Code is to log in to the Alps system, set up your environment (start a container or uenv, start a session on a compute node), and start the remote server in that environment pre-configured.

[](){#ref-vscode-install}
### Installing the server

The first step is to download the VS Code CLI tool `code`, which CSCS provides for easy download.
There are two executables, one for using on systems with x86 or ARM CPUs respectively.

=== "`aarch64` nodes (daint, clariden, santis)"
    ```
    wget https://jfrog.svc.cscs.ch/artifactory/uenv-sources/vscode/vscode_cli_alpine_arm64_cli.tar.gz
    tar -xf vscode_cli_alpine_arm64_cli.tar.gz
    ```

=== "`x86_64` nodes (eiger, bristen)"
    ```
    wget https://jfrog.svc.cscs.ch/artifactory/uenv-sources/vscode/vscode_cli_alpine_x64_cli.tar.gz
    tar -xf vscode_cli_alpine_x64_cli.tar.gz
    ```

After downloading, copy the `code` executable to a location in your PATH, so that it is available for future sessions.

Clusters on Alps share a common [home][ref-storage-home] path `HOME=/users/$USER` that is mounted on all clusters.

If you want to use VS Code on multiple clusters, possibly with different CPU architectures (Daint, Clariden and Santis use `aarch64` CPUs, and [Eiger][ref-cluster-eiger] uses `x86_64` CPUs), you need to take some additional steps to ensure that VS Code installation and configuration is separated.

First, install the `code` executable in an [architecture-specific path][ref-guides-terminal-arch].

!!! example "Installing VS Code for `x86_64` and `aarch64`"
    In `~/.bashrc`, add the following line (you will need to log in again for this to take effect):
    ```
    export PATH=$HOME/.local/$(uname -m)/bin:$PATH
    ```
    The `uname -m` command will print `aarch64` or `x86_64`, according to the microarchitecture of the node it is run on.

    Then create the path, and copy the `code` executable to the architecture-specific path:
    ```
    mkdir -p $HOME/.local/$(uname -m)/bin
    cp ./code $HOME/.local/$(uname -m)/bin
    ```
    Repeat this for both `x86_64` and `aarch64` binaries.

By default VS Code will store configuration, data and executables in `$HOME/.vscode-server`.
To use VS Code on multiple clusters, it is strongly recommended that you create separate `vscode-server` path for each cluster
by adding the following environment variable definitions to your `~/.bashrc`:

```bash
export VSCODE_AGENT_FOLDER="$HOME/.vscode-server/$CLUSTER_NAME-tunnel/.vscode-server"
export VSCODE_CLI_DATA_DIR="$VSCODE_AGENT_FOLDER/cli"
```

!!! warning
    You will need to log out and back in after updating `$HOME/.bashrc`, before trying to start the VS Code server for the first time.

[](){#ref-vscode-update}
### Updating VS Code server

VS Code is continuously being updated, and the version of VS Code on your laptop will most likely be more recent than the version provided by CSCS.

Once you have installed the server, you can easily update it to the latest version:

```console title="Updating VS Code server"
$ code --version
code 1.97.2 (commit e54c774e0add60467559eb0d1e229c6452cf8447)
$ code update
Successfully updated to 1.101.0 (commit dfaf44141ea9deb3b4096f7cd6d24e00c147a4b1)
$ code --version
code 1.101.0 (commit dfaf44141ea9deb3b4096f7cd6d24e00c147a4b1)
```

It is good practice to periodically update code to keep it in sync with the version on your laptop.

[](){#ref-vscode-starting}
### Starting and configuring the server

!!! note
    You need to have a GitHub account to connect a remote tunnel to VS Code.

To set up a remote server on the target system,
run the `code` executable that you downloaded with the `tunnel` argument.
You will be asked to choose whether to log in to Microsoft or GitHub (we have tested with GitHub):

```console
$ code tunnel --name=$CLUSTER_NAME-tunnel
...
? How would you like to log in to Visual Studio Code? ›
  Microsoft Account
❯ GitHub Account
```

!!! tip
    Give the tunnel a unique name using the `--name` flag, which will later be listed on the VS Code UI.

You will be requested to go to [github.com/login/device](https://github.com/login/device) and enter an 8-digit code.
Once you have finished registering the service with GitHub, in VS Code on your PC/laptop open the "remote explorer" pane on the left hand side of the main window, and the connection will be visible under REMOTES (TUNNELS/SSH) -> Tunnels.

!!! note "First time setting up a remote service"
    If this is the first time you have followed this procedure, you may have to sign in to GitHub in VS Code.

    Click on the Remote Explorer button on the left hand side, and then find the following option:

    ```
    REMOTES(TUNNELS/SSH)
     Tunnels
        Sign in to tunnels registered with GitHub
    ```

    If you have not signed in to GitHub with VS Code editor, you will be redirected to the browser to sign in.

    After signing in and authorizing VS Code, the open tunnel should be visible under REMOTES (TUNNELS/SSH) -> Tunnels.

[](){#ref-vscode-uenv}
### Using with uenv

To use a uenv with VS Code, the uenv must be started before calling `code tunnel`.
Log into the target system and start the uenv, then start the remote server, for example:
```
# log into daint (this could be any other Alps cluster)
ssh daint
# start a uenv session on the login node
uenv start --view=default prgenv-gnu/24.11:v1
# then start the tunnel
code tunnel --name=$CLUSTER_NAME-tunnel
```

Alternatively, you can execute `code tunnel` directly in the environment:
```
ssh daint
uenv run --view=default prgenv-gnu/24.11:v1 -- code tunnel --name=$CLUSTER_NAME-tunnel
```

Once the tunnel is configured, you can access it from VS Code.

!!! warning
    If you plan to do any intensive work: repeated compilation of large projects or running python code in Jupyter, please see the guide to running on a compute node below.
    Running intensive workloads on login nodes, which are shared resources between all users, is against CSCS [fair usage][ref-policies-fair-use] of Shared Resources policy.

[](){#ref-vscode-compute-nodes}
### Running on a compute node

If you plan to do computation using your VS Code, then you should first allocate resources on a compute node and set up your environment there.

!!! example "directly create the tunnel using srun"
    You can directly execute the `code tunnel` command using srun:
    ```
    ssh daint
    srun --uenv=prgenv-gnu/24.11:v1 --view=default -t120 -n1 --pty code tunnel --name=$CLUSTER_NAME-tunnel
    ```

    * `--uenv` and `--view` set up the uenv
    * `-t120` requests a 2 hour (120 minute) reservation
    * `-n1` requests a single rank - only one rank/process is required for VS Code
    * `--pty` allows forwarding of terminal I/O, required to sign in to Github

    Once the job allocation is granted, you will be prompted to log into GitHub, the same as starting a session on the login node.
    If you don't want to use a uenv, the command is even simpler:
    ```
    ssh daint
    srun -t120 -n1 --pty code tunnel --name=$CLUSTER_NAME-tunnel
    ```

!!! example "log into a node before starting"
    It is also possible to log into a compute node before executing the `code tunnel` command, if that suits your workflow:
    ```
    # log into daint
    ssh daint

    # start an interactive shell session
    srun -t120 -n1 --pty bash

    # set up the environment before starting the tunnel
    uenv start prgenv-gnu/24.11:v1 --view=default
    code tunnel --name=$CLUSTER_NAME-tunnel
    ```

    * `-t120` requests a 2 hour (120 minute) reservation
    * `-n1` requests a single rank - only one rank/process is required for VS Code
    * `--pty` allows forwarding of terminal I/O, for bash to work interactively

[](){#ref-vscode-containers}
### Using with containers

This will use CSCS's [Container Engine][ref-container-engine], to launch the container on a compute node and start the VS Code server.

```toml title="EDF file with image and mount paths"
image = "nvcr.io#nvidia/pytorch:24.01-py3" # example of PyTorch NGC image
writable = true
mounts = ["/paths/on/scratch/or/home:path/on/the/container",
          "/path/if/same/on/both"
          "/path/of/code/executable:/path/for/code/executable/in/container"]
workdir = "default/working/dir/path"
```

!!! note
    Ensure that the `code` executable is accessible in the container.
    It can either be contained in the image, or you can [install][ref-vscode-install] and [update][ref-vscode-update] the server in a path that you [mount][ref-ce-edf-reference-mounts] inside the container in the `mounts` field of the EDF file.

Log into the target system, and launch an interactive session with the container image:
```console
# launch container on compute node
$ srun -N 1 --environment=/absolute/path/to/tomlfile.toml --pty bash
```

Then on the compute node, you can start the tunnel manually, following the prompts to log in via GitHub:
```console
$ cd path/for/code/executable/in/container
$ ./code tunnel --name=$CLUSTER_NAME-tunnel
```

## Connecting via VS Code UI

!!! warning
    This approach is not recommended, and is not supported by CSCS.

    It is relatively easy to connect to a log in node using the "Connect to Host... (Remote-SSH)" option in the VS Code GUI on your laptop.
    However, it is complicated and difficult to configure the connection so that the environment used by the VS Code session is in a uenv/container or on a compute node.
