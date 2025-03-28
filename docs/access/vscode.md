[](){#ref-access-vscode}
# Connecting with VSCode

[Visual Studio Code](https://code.visualstudio.com/) provides flexible support for remote development.
VSCode's [remote tunnel feature](https://code.visualstudio.com/docs/remote/tunnels) starts a server on a remote system, and connects the editor to this server.
There are two ways to set up the connection:

* using the code CLI: the most flexible method if using containers or uenv.
* using the VSCode interface: VSCode will connect onto the system, download and start the server

The main challenge with using VSCode is that the most convenient method for starting a remote session is to start a remote tunnel from the VS Code GUI.
This approach starts a session in the standard login environment on that node, however this won't work if you want to be developing in a container, in a uenv, or on a compute node.

## Flexible method: remote server

The most flexible method for connecting VSCode is to log in to the Alps system, set up your environment (start a container or uenv, start a session on a compute node), and start the remote server in that environment pre-configured.

!!! note
    This approach requires that you have a GitHub account, and that the GitHub account is configured with your VS Code editor.

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

!!! note
    See the guide on how to manage [architecture-specific binaries][ref-guides-terminal-arch] if you plan to use VScode on both x86 and ARM clusters.

Alternatively, download the CLI tool from the [VS Code site](https://code.visualstudio.com/Download) -- take care to select either x86 or Arm64 version that matches the target system.

After downloading, copy the `code` executable to a location in your PATH, so that it is available for future sessions.

??? note "guidance on where to put architecture-specific executables"
    The home directory can be shared by multiple clusters that might have different micro-architectures, so it is important to separate executables for x86 and aarch64 (ARM) targets.

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

To set up a remote server on the target system,
run the `code` executable that you downloaded the `tunnel` argument.
You will be asked to choose whether to log in to Microsoft or GitHub (we have tested with GitHub):

```
> code tunnel --name=$CLUSTER_NAME-tunnel
...
? How would you like to log in to Visual Studio Code? ›
  Microsoft Account
❯ GitHub Account
```

!!! tip
    Give the tunnel a unique name using the `--name` flag, which will later be listed on the VSCode UI.

You will be requested to go to [github.com/login/device](https://github.com/login/device) and enter an 8-digit code.
Once you have finished registering the service with GitHub, in VSCode on your PC/laptop open the "remote explorer" pane on the left hand side of the main window, and the connection will be visible under REMOTES (TUNNELS/SSH) -> Tunnels.

!!! note "first time setting up a remote service"
    If this is the first time you have followed this procedure, you may have to sign in to GitHub in VSCode.
    Click on the Remote Explorer button on the left hand side, and then find the following option:

    ```
    REMOTES(TUNNELS/SSH)
     Tunnels
        Sign in to tunnels registered with GitHub
    ```

    If you have not signed in to GitHub with VS Code editor, you will be redirected to the browser to sign in.

    After signing in and authorizing VSCode, the open tunnel should be visible under REMOTES (TUNNELS/SSH) -> Tunnels.

### Using with uenv

To use a uenv with VSCode, the uenv must be started before calling `code tunnel`.
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

Once the tunnel is configured, you can access it from VSCode.

!!! warning
    If you plan to do any intensive work: repeated compilation of large projects or running python code in Jupyter, please see the guide to running on a compute node below.
    Running intensive workloads on login nodes, which are shared resources between all users, is against CSCS [fair usage][ref-policies-fair-use] of Shared Resources policy.

### Using with containers

!!! todo
    write a guide

### Running on a compute node

If you plan to do computation using your VSCode, then you should first allocate resources on a compute node and set up your environment there.

!!! example "directly create the tunnel using srun"
    You can directly execute the `code tunnel` command using srun:
    ```
    ssh daint
    srun --uenv=prgenv-gnu/24.11:v1 --view=default -t120 -n1 --pty code tunnel --name=$CLUSTER_NAME-tunnel
    ```

    * `--uenv` and `--view` set up the uenv
    * `-t120` requests a 2 hour (120 minute) reservation
    * `-n1` requests a single rank - only one rank/process is required for VSCode
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
    * `-n1` requests a single rank - only one rank/process is required for VSCode
    * `--pty` allows forwarding of terminal I/O, for bash to work interactively

## Connecting via VSCode UI

!!! warning
    This approach is not recommended, because while it may be easier to connect via the VS Code UI, it is much more difficult to configure the connection so that you can use uenv, containers or compute nodes.

!!! todo
    Write the guide
