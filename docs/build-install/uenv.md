Uenv are user environments that provide scientific applications, libraries and tools on Alps. This article use them to build software.

For more documentation on how to find, download and use uenv in your workflow, see the [env tool documentation][ref-uenv].

[](){#ref-building-uenv-spack}
## Building software using Spack

Each uenv is tightly coupled with [Spack] and can be used as an upstream [Spack] instance, because
the sofware in uenv is built with [Spack] using the [Stackinator] tool.

CSCS provides `uenv-spack` - a tool that can be used to quickly install software using the software and configuration provided inside a uenv, similarly to how `module load` loads software packages.

### Installing `uenv-spack`

```bash
# download the uenv-spack tool
git clone https://github.com/eth-cscs/uenv-spack.git

# initialise the tool
(cd uenv-spack && ./bootstrap)

export PATH=$PWD/uenv-spack:$PATH
```

### Select The uenv

The next step is to choose which uenv to use.
The uenv will provide the compilers, cray-mpich, and other libraries and tools.

``` mermaid
graph TD
  A[/is there a uenv for the application?\] -->|yes| B[use that image, e.g. **gromacs**]
  A --> |no| C[/do I need OpenACC or CUDA Fortran?\]
  C --> |no| D[use **prgenv-gnu**]
  C --> |yes| E[/are you _really_ sure?\]
  E --> |yes| F[use **prgenv-nvfortran**]
  E --> |no| D
```

!!! tip "use `prgenv-gnu` when in doubt"
    If you don't know where to start, use the latest release of the `prgenv-gnu` on the system that you are targeting.
    It provides the latest versions of `gcc`, `cray-mpich`, `python` and commonly used libraries like `fftw` and `boost`.

    On systems that have NVIDIA GPUs (`gh200` and `a100` uarch), it also provides the latest version of `cuda` and `nccl`, and is configured for GPU-aware MPI communication.

To use Spack as an upstream, the uenv has to be started with the `spack` view:

```bash
uenv start prgenv-gnu/24.11:v1 --view=spack
```

??? note "what does the `spack` view do?"
    The `spack` view sets environment variables that provide information about the version of Spack that was used to build the uenv, and where the uenv Spack configuration is stored.

    This information is useful because it is strongly recomended that you use the same version of Spack to build software on top of the uenv.

    | <div style="width:12em">variable</div> | <div style="width:18em">example</div> | description |
    | -------- | ------- | ----------- |
    | `UENV_SPACK_CONFIG_PATH` | `user-environment/config` | the path of the upstream [spack configuration files]. |
    | `UENV_SPACK_REF`         | `releases/v0.23` | the branch or tag used - this might be empty if a specific commit of Spack was used. |
    | `UENV_SPACK_URL`         | `https://github.com/spack/spack.git` | The git repository for Spack - nearly always the main spack/spack repository. |
    | `UENV_SPACK_COMMIT`      | `c6d4037758140fe...0cd1547f388ae51` | The commit of Spack that was used |

### Describing what to build

!!! example "Create a build path with a template `spack.yaml` and `repo`:"
    ```
    uenv-spack <build-path> --uarch=gh200
    cd <build-path>
    ./build
    ```
    Where `<build-path>` is a path (typically in `$SCRATCH`, e.g. `$SCRATCH/builds/gromacs-24.11`).


`uenv-spack` creates a directory tree with the following contents:

```
<build-path>
├─ build        # build the software stack (script)
├─ spack        # a git clone of the required version of Spack
├─ config       # spack configurations for the software stack
│   ├─ meta.json # information about the uenv that was used
│   ├─ user
│   │  ├─ config.yaml
│   │  ├─ modules.yaml
│   │  └─ repos.yaml
│   └─ system
│      ├─ compilers.yaml
│      ├─ packages.yaml
│      ├─ repos.yaml
│      └─ upstreams.yaml
└─ env          # description of the software to build
    ├─ spack.yaml
    └─ repo
       ├─ repo.yaml
       └─ packages
```

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

!!! example "Create a build path and populate the `spack.yaml` file with some [specs]"

    ```bash
    uenv-spack $SCRATCH/install/tools --uarch=gh200 \
               --specs="tree, screen, emacs +treesitter"
    cd $SCRATCH/install/tools
    ./build
    ```

If you already have a directory with a complete `spack.yaml` file and custom repo, you can provide it as an argument to `uenv-spack`:

!!! example "Create a build path and use a pre-configured `spack.yaml` and `repo`"
    ```
    uenv-spack $SCRATCH/install/arbor --uarch=gh200 \
               --recipe=<path-to-recipe>
    cd $SCRATCH/install/tools
    ./build
    ```

!!! example "Create a build path and use your own `spack.yaml`"
    **TODO** this feature has not been implemented yet
    ```
    uenv-spack $SCRATCH/install/arbor --uarch=gh200 \
               --recipe=<path-to-spack.yaml>
    cd $SCRATCH/install/tools
    ./build
    ```

### Build the software

Once specs have been added to `spack.yaml`, you can build the image using the `build` script that was generated in `<build-dir>`:

```bash
./build
```

This process will take a few minutes at least, because the version of Spack that was downloaded needs to

* bootstrap;
* concretise the environment;
* build all of the packages.

The duration of the build depends on the specs: some specs may require a long time to build, or require installing many dependencies.

The build step generates multiple outputs:

### installed packages

The packages built by Spack are installed in `<build-dir>/store`.

### Spack view

A Spack view is generated in `<build-dir>/view`.

### modules

Module files are generated in the `module` sub-directory of the `<build-path>`

To use them, add them to the module environment

```bash
# make the modules available
module use <build-dir>/modules

# they should no be visible, check them:
module avail
```

!!! note
    The generation of modules can be customised by editing the `<build-dir>/config/user/modules.yaml` file _before_ running `build`.
    See the [Spack modules] documentation.

### Use the software

!!! warning
    This step is not fully covered by the tool/workflow yet

!!! warning
    The uenv that was used to configure and build must always be loaded when using the software stack.

* [option] load modules
* [option] activate the view
* [option] `source <build-dir>/spack/share/spack/setup-env.sh` then `spack find`, `spack load`, `spack -e env ...` etc.


[Chaining Spack Installations]: https://spack.readthedocs.io/en/latest/chain.html
[Spack]: https://spack.readthedocs.io/en/latest/
[Spack Basic Usage]: https://spack.readthedocs.io/en/latest/basic_usage.html
[Spack modules]: https://spack.readthedocs.io/en/latest/module_file_support.html
[Spack package repository]: https://spack.readthedocs.io/en/latest/repositories.html
[Stackinator]: https://eth-cscs.github.io/stackinator/
[Spack configuration files]: https://spack.readthedocs.io/en/latest/configuration.html
[spec]: https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs
[specs]: https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs
