# Linaro Forge

[Linaro Forge](<https://docs.linaroforge.com/latest/html/forge/index.html>) is a suite of profiling and debugging tools, that includes the DDT debugger and the MAP performance analysis tool.

> [!NOTE]
>
> **Linaro DDT debugger and Linaro MAP performance analysis tool**
>
> We have separate user guides for the tools provided by the `linaro-forge` uenv. The documentation here shows how to download the uenv, and how to set up your environment.
>
> Once you are set up, follow the specific guides:
>
> - DDT debugger,
> - MAP performance analysis tool.

## Quickstart guide

The Linaro uenv is named `linaro-forge`, and the available versions can be determined using the `uenv image find` command, as explained in the uenv documentation.

> [!NOTE]
>
> **Finding available `linaro-forge` versions**
>
> Search for `linaro-forge`, in this case there are two versions available, and download the latest.
>
> ```console
> $ uenv image find linaro-forge
> uenv                  arch  system  id                size(MB)  date
> linaro-forge/25.1:v2  zen2  eiger   89a25464e0b3d4f4     385    2026-05-21
> linaro-forge/26.0:v1  zen2  eiger   dedc658162f5fc28     194    2026-07-03
>
> $ uenv image pull linaro-forge/26.0:v1
> ```

This uenv is configured to be mounted in the `/user-tools` path so that they can be used alongside application and development uenv mounted at `/user-environment`.

When using alongside another uenv, start a uenv session with both uenv. In the following example, the `prgenv-gnu` and `linaro-forge` uenv will be mounted at `/user-environment` and `/user-tools` respectively:

```console
$ uenv start prgenv-gnu/26.3:v1,linaro-forge/26.0:v1 \
    --view=prgenv-gnu:default,forge # (1)!

$ uenv status # (2)!

$ ddt --version # (3)!
Linaro DDT Part of Linaro Forge.
Copyright (c) 2023-2026 Linaro Limited. All rights reserved.
Version: 26.0
```

1. The `forge` view provided by the `linaro-forge` uenv makes `ddt` and `map` executables available.
2. Test that everything has been mounted correctly by looking at `uenv status`. There will be warnings if there are problems.
3. Check that the DDT debugger is in the path.

> [!NOTE]
>
> The `linaro-forge` uenv is always mounted at the `/user-tools` mount point.

### Install and configure the Linaro client on your local machine

We recommend installing the [Linaro desktop client](<https://www.linaroforge.com/downloadForge>) on your local workstation or laptop. It can be downloaded for a selection of operating systems.

> [!WARNING]
>
> Make sure you download the [Linaro desktop client](<https://www.linaroforge.com/downloadForge>) matching the version of the `linaro-forge` uenv you are planning to use.
>
> > **Mismatched desktop client and uenv versions**
> >
> > Mismatches between the client and the uenv version will lead to the following error when trying to establish a remote connection:
> >
> > ```text
> > The local version of Linaro DDT (24.0.6) is not compatible with the remote version (24.1.2).
> > ```

The client can be configured to connect with the debug jobs running on Alps, offering a better user experience compared to running with X11 forwarding. Once installed, the client needs to be configured to connect to the vCluster on which you are working.

First, start the client on your laptop:

> [!WARNING]
>
> The path will change if you have installed a different version, or if it has been installed in a non-standard installation location.

```bash
$HOME/linaro/forge/26.0/bin/ddt
```

> [!WARNING]
>
> The path will change if you have installed a different version, or if it has been installed in a non-standard installation location. Please use the appropriate path and version for your installation.

```bash
open /Applications/Linaro\ Forge\ Client\ 26.0.app/
```

Next, configure a connection to the target system. Open the `Remote Launch` menu and click on `Configure...` then `Add`. Examples of the settings are below.

> [!WARNING]
>
> The `Remote Installation Directory` will change if you are using a different version of the `linaro-forge` uenv. Please use the appropriate version for your setup.

| Field | Value |
| --- | --- |
| Connection | `daint` |
| Host Name | `cscsusername@ela.cscs.ch cscsusername@daint.cscs.ch` |
| Remote Installation Directory | `uenv run linaro-forge/26.0:v1:/user-tools -- /user-tools/env/forge/` |
| Private Key | `~/.ssh/cscs-key` |

> [!WARNING]
>
> The `Remote Installation Directory` will change if you are using a different version of the `linaro-forge` uenv. Please use the appropriate version for your setup.

| Field | Value |
| --- | --- |
| Connection | `santis` |
| Host Name | `cscsusername@ela.cscs.ch cscsusername@santis.cscs.ch` |
| Remote Installation Directory | `uenv run linaro-forge/26.0:v1:/user-tools -- /user-tools/env/forge/` |
| Private Key | `~/.ssh/cscs-key` |

> [!WARNING]
>
> The `Remote Installation Directory` will change if you are using a different version of the `linaro-forge` uenv. Please use the appropriate version for your setup.

| Field | Value |
| --- | --- |
| Connection | `clariden` |
| Host Name | `cscsusername@ela.cscs.ch cscsusername@clariden.cscs.ch` |
| Remote Installation Directory | `uenv run linaro-forge/26.0:v1:/user-tools -- /user-tools/env/forge/` |
| Private Key | `~/.ssh/cscs-key` |

> [!WARNING]
>
> The `Remote Installation Directory` will change if you are using a different version of the `linaro-forge` uenv. Please use the appropriate version for your setup.

| Field | Value |
| --- | --- |
| Connection | `eiger` |
| Host Name | `cscsusername@ela.cscs.ch cscsusername@eiger.cscs.ch` |
| Remote Installation Directory | `uenv run linaro-forge/26.0:v1:/user-tools -- /user-tools/env/forge/` |
| Private Key | `~/.ssh/cscs-key` |

> [!TIP]
>
> It is recommended to log into Alps using `ela.cscs.ch` as a ssh Jump host, as explained here. In that case, you can remove `cscsusername@ela.cscs.ch` from the Linaro client configuration above.

Some notes on the examples above:

- SSH forwarding via `ela.cscs.ch` is used to access the cluster;
- replace the username `cscsusername` with your CSCS user name that you would normally use to open an SSH connection to CSCS;
- `Remote Installation Directory` is pointing to the install directory of DDT inside the uenv image;
- private keys should be the ones generated for CSCS MFA, and this field does not need to be set if you have added the key to your SSH agent.

Once configured, test and save the configuration:

1. check whether the configuration is correct by clicking `Test Remote Launch` (and then `OK` when the test is successful),
2. click on `OK` and then `Close` to save the configuration.
3. You can now connect by going to `Remote Launch` and choose the entry (`Connection` name) you added. If the client fails to connect, look at the error message, check your SSH configuration and make sure you can SSH without the client.

## Troubleshooting

Notes about known issues.

> [!WARNING]
>
> **The proxy type is invalid for this operation**
>
> If the tool fails to launch with the following error message:
>
> ```text
> Error communicating with Licence Server velan.cscs.ch:
> The proxy type is invalid for this operation
> Attempting again while ignoring proxies.
> ```
>
> Proxy environment variables need to be set to let the tool connect to the license server, as explained in Compute node proxy configuration.

> [!NOTE]
>
> **AMD GPU support**
>
> Linaro Forge is supported on both NVIDIA and AMD GPUs at CSCS.
