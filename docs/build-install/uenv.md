[](){#ref-build-uenv}
# Building with uenv

Uenv are user environments that provide scientific applications, libraries and tools on [Alps][ref-alps]. 
This article explains how to use them to build software.

For more documentation on how to find, download and use uenv in your workflow,
see the [uenv documentation][ref-uenv].

[](){#ref-build-uenv-spack}
## Building software using Spack

Each uenv is tightly coupled with [Spack] and can be used as an upstream [Spack] instance, because
the software in uenv is built with [Spack] using the [Stackinator] tool.

CSCS provides `uenv-spack` - a tool that can be used to quickly install software using the software and configuration provided inside a uenv, similarly to how `module load` loads software packages.

### Installing `uenv-spack`

```bash
git clone https://github.com/eth-cscs/uenv-spack.git # (1)!
export PATH=$PWD/uenv-spack:$PATH  # (2)!
```

1. Download the `uenv-spack` tool from GitHub.

2. Make the `uenv-spack` executable available.

!!! note "Requires uv"
    `uenv-spack` requires [uv](https://docs.astral.sh/uv/).
    See our guide to setting up [installation locations][ref-guides-terminal-arch], before [installing uv](https://docs.astral.sh/uv/getting-started/installation).

### Select the uenv

The next step is to choose which uenv to use.
The uenv will provide the compilers, Cray MPICH, and other libraries and tools.

```mermaid
graph TD
  A[/is there a uenv for the application?\] -->|yes| B[use that image, e.g. **gromacs**]
  A --> |no| C[/do I need OpenACC or CUDA Fortran?\]
  C --> |no| D[use **prgenv-gnu**]
  C --> |yes| E[/are you _really_ sure?\]
  E --> |yes| F[use **prgenv-nvfortran**]
  E --> |no| D
```

!!! tip "Use `prgenv-gnu` when in doubt"
    If you don't know where to start, use the latest release of the `prgenv-gnu` on the system that you are targeting.
    It provides the latest versions of `gcc`, `cray-mpich`, `python` and commonly used libraries like `fftw` and `boost`.

    On systems that have NVIDIA GPUs (`gh200` and `a100` uarch), it also provides the latest version of `cuda` and `nccl`, and it is configured for GPU-aware MPI communication.

To use a uenv as an [upstream Spack instance](https://spack.readthedocs.io/en/latest/chain.html),
the uenv has to be started with the `spack` view:

```bash
uenv start prgenv-gnu/24.11:v1 --view=spack
```

!!! note "What does the `spack` view do?"
    The `spack` view sets environment variables that provide information about the version of Spack that was used to build the uenv, and where the uenv Spack configuration is stored.

    | <div style="width:12em">variable</div> | <div style="width:18em">example</div> | description |
    | -------- | ------- | ----------- |
    | `UENV_SPACK_CONFIG_PATH` | `user-environment/config` | the path of the upstream [spack configuration files]. |
    | `UENV_SPACK_REF`         | `releases/v0.23` | the branch or tag used - this might be empty if a specific commit of Spack was used. |
    | `UENV_SPACK_URL`         | `https://github.com/spack/spack.git` | The git repository for Spack - nearly always the main spack/spack repository. |
    | `UENV_SPACK_COMMIT`      | `c6d4037758140fe...0cd1547f388ae51` | The commit of Spack that was used |

    Spack version 1 moved the Spack packages from inside the Spack repository to a standalone [repository on GitHub](https://github.com/spack/spack-packages).
    Uenvs that were built using Spack 1.0 and later will also set the following environment variables that provide information about the package versioning:

    | <div style="width:14em">variable</div> | <div style="width:16em">example</div> | description |
    | -------- | ------- | ----------- |
    | `UENV_SPACK_PACKAGES_REF`         | `releases/v2025.07` | the branch or tag used - this might be empty if a specific commit of Spack was used. |
    | `UENV_SPACK_PACKAGES_URL`         | `https://github.com/spack/spack-packages.git` | The git repository - nearly always the main spack/spack-packages repository. |
    | `UENV_SPACK_PACKAGES_COMMIT`      | `c6d4037758140fe...0cd1547f388ae51` | The git commit of Spack-packages that was used |

    !!! note

        The environment variables set by the `spack` view are scoped by `UENV_`.
        Therefore, they don't change Spack-related environment variables.
        You can use them to consistently set Spack-related environment variables.

??? warning "Upstream Spack version"

    It is strongly recommended that your version of Spack and the version of Spack in the uenv match when building software on top of an uenv.

!!! note "Advanced Spack users"
    The `uenv-spack` tool creates an empty Spack environment, configuration files and a build script that automates concretizing and installing the environment.
    It is recommended that you take the time to review the environment and configuration, and modify it as needed for your project.

    It is also possible to integrate uenv into your own Spack workflow.
    For this, it is recommended to load the `spack` view, and use the `UENV_SPACK_*` environment variables.

    !!! example "Setting Spack configuration path"
        ```bash
        export SPACK_SYSTEM_CONFIG_PATH=$UENV_SPACK_CONFIG_PATH
        ```

### Describing what to build

The next step is to describe what software to build.
This is done using a [Spack environment file] and a [Spack package repository].

The `uenv-spack` tool can be used to create a build directory with a template [Spack environment file] (`spack.yaml`) and a [Spack package repository] (`repo/` directory).

!!! example "Create a build directory with a Spack environment file and a Spack package repository"

    ```bash
    uenv-spack <build-path> --uarch=<uarch> --name=<env-name>
    cd <build-path>
    vim ./env/spack.yaml    # (1)!
    ./build
    ```

    1. Edit the [`spack.yaml`][Spack environment file] file to add package specs, set preferences, etc.

    All of the arguments are required:

    * `<build-path>` is the path in which the environment will be built:
        * typically in `$SCRATCH`, e.g. `$SCRATCH/builds/gromacs-24.11`.
    * `<uarch>`: is the microarchitecture:
        * one of `zen2, zen3, gh200, a100`;
        * used to set default variants in the Spack recipe.
    * `<env-name>`: is the name of the environment:
        * must start with a letter, and may only contain letters, numbers, underscores `_` and dashes `-`.



`uenv-spack` creates a directory tree with the following contents:

```bash
<build-path>
├─ build # (1)!
├─ spack # (2)!
├─ config # (3)!
│   ├─ meta.json # (4)!
│   ├─ user
│   │  ├─ config.yaml
│   │  ├─ modules.yaml
│   │  └─ repos.yaml
│   └─ system
│      ├─ compilers.yaml
│      ├─ packages.yaml
│      ├─ repos.yaml
│      └─ upstreams.yaml
└─ env # (5)!
    ├─ spack.yaml # (6)!
    └─ repo # (7)!
       ├─ repo.yaml
       └─ packages
```

1. Script to build the software stack.
2. `git` clone of the required version of Spack.
3. Spack configuration files for the software stack.
4. Information about the uenv that was used to run `uenv-spack`.
5. Description of the software to build.
6. Template [Spack environment file].
7. Empty [Spack package repository].

The `env` path contains a template `spack.yaml` file, and an empty [Spack package repository]:

```
env
├─ spack.yaml
└─ repo
   ├─ repo.yaml
   └─ packages
```

where the `spack.yaml` file contains an empty list of specs:

```yaml
    specs: []
```

Edit this file to add the specs that you wish to build, for example:

```yaml
    specs: [tree, screen, emacs +treesitter]
```

The step of adding a list of specs to the `spack.yaml` template can be skipped by providing them using the `--specs` argument to `uenv-spack`.

!!! example "Create a build path and populate the `spack.yaml` file with some Spack [specs]"

    ```bash
    uenv-spack $SCRATCH/install/tools --uarch=gh200 \
               --specs="tree, screen, emacs +treesitter"
    cd $SCRATCH/install/tools
    ./build
    ```

If you already have a directory with a complete `spack.yaml` file and custom repo,
you can provide it as an argument to `uenv-spack`:

!!! example "Create a build path and use a pre-configured `spack.yaml` and `repo`"

    ```bash
    uenv-spack $SCRATCH/install/arbor --uarch=gh200 \
               --recipe=<path-to-recipe>
    cd $SCRATCH/install/tools
    ./build
    ```

??? example "Create a build path and use your own `spack.yaml`"

    !!! warning "NOT YET IMPLEMENTED"

        ```bash
        uenv-spack $SCRATCH/install/arbor --uarch=gh200 \
                   --recipe=<path-to-spack.yaml>
        cd $SCRATCH/install/tools
        ./build
        ```

### Build the software

Once specs have been added to `spack.yaml`, you can build the image using the `build` script that was generated in `<build-path>`:

```bash
./build
```

This process will take a while, because the version of Spack that was downloaded needs to:

* bootstrap Spack;
* then concretise the environment;
* then build all of the packages.

The duration of the build depends on the specs: some specs may require a long time to build, or require installing many dependencies.

The build step generates multiple outputs, described below.

### Installed packages

The packages built by Spack are installed in `<build-path>/store`.

### Spack view

A Spack view is generated in `<build-path>/view` with an activation script `<build-path>/view/activate.sh`.
When the view is activated, all of the installed packages are available for use in the environment.

!!! example "Activating the view"
    For an environment with `build-path=$SCRATCH/software/tool` that was built using `prgenv-gnu/25.6:v2`:

    ```bash
    uenv start prgenv-gnu/25.6:v2                   # (1)!
    source $SCRATCH/software/tool/view/activate.sh  # (2)!
    ```

    1. Start the uenv: to use the software the `spack` view does not need to be loaded.
    2. The `activate.sh` script sets environment variables that load the software.


### Modules

Module files are generated in the `module` sub-directory of the `<build-path>`

To use them, add them to the module environment:

!!! example "Use the modules"
    For an environment with `build-path=$SCRATCH/software/tool` that was built using `prgenv-gnu/25.6:v2`:

    ```bash
    uenv start prgenv-gnu/25.6:v2             # (1)!
    module use $SCRATCH/software/tool/modules # (2)!
    module avail                              # (3)!
    ```

    1. Start the uenv: to use the software the `spack` view does not need to be loaded.
    2. Make modules available.
    3. Check that the modules are available.

!!! note
    The generation of modules can be customised by editing the `<build-path>/config/user/modules.yaml` file _before_ running `build`.
    See the [Spack modules] documentation.

[Chaining Spack Installations]: https://spack.readthedocs.io/en/latest/chain.html
[Spack]: https://spack.readthedocs.io/en/latest/
[Spack Basic Usage]: https://spack.readthedocs.io/en/latest/basic_usage.html
[Spack modules]: https://spack.readthedocs.io/en/latest/module_file_support.html
[Spack package repository]: https://spack.readthedocs.io/en/latest/repositories.html
[Stackinator]: https://eth-cscs.github.io/stackinator/
[Spack configuration files]: https://spack.readthedocs.io/en/latest/configuration.html
[spec]: https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs
[specs]: https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs
[Spack environment file]: https://spack.readthedocs.io/en/latest/environments.html
