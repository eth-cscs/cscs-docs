# prgenv-dpcpp

> [!NOTE]
>
> **experimental and not officially supported**
>
> `prgenv-dpcpp` is experimental and not officially supported. It is provided as-is and may break or be removed on system upgrades. It is currently deployed only on [Daint](<https://docs.cscs.ch/clusters/daint/index.md#daint>).
>
> Try [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) first, because it is better tested and better supported. Use `prgenv-dpcpp` only if you specifically need the DPC++ (SYCL) compiler; it provides the same package set as `prgenv-gnu/25.11`, plus DPC++.

Provides the [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) toolchain together with the Intel DPC++ (SYCL) compiler with a CUDA backend. It is for building SYCL applications that target the [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") nodes on Alps.

## Versioning

The naming scheme is `prgenv-dpcpp/<version>`, where `<version>` tracks the [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) version it extends, in the `YY.M[M]` format (for example `25.11` for November 2025).

The release schedule is not fixed. New versions will be released to match an underlying `prgenv-gnu` based on user requests: contact the CSCS [service desk](<https://jira.cscs.ch/plugins/servlet/desk>) for an updated version.

| version | node types | system |
| --- | --- | --- |
| 25.11 | gh200 | daint |

### Deprecation policy

There is no fixed deprecation policy for this experimental uenv. Versions are provided for as long as practical, and system upgrades may force an update that requires you to recompile.

### Versions

Extends [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) `25.11` with the Intel DPC++ (SYCL) compiler. The Intel oneAPI binary distribution is x86\_64 only, so the compiler is built from source (the [intel/llvm](<https://github.com/intel/llvm>) `sycl` branch) with a custom Spack package.

The notable differences from `prgenv-gnu/25.11` are:

- the DPC++ compiler (`llvmdpcpp`), with the CUDA backend targeting `sm_90`
- `cray-mpich@9 +cuda`, which is GPU-aware and compatible with SYCL device pointers
- `cuda@12`

> [!NOTE]
>
> **packages**
>
> The package set is the same as [`prgenv-gnu`](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) `25.11` (Boost, HDF5, NetCDF, Kokkos, FFTW, OpenBLAS, ScaLAPACK, NCCL, Python and so on; see its page for the full list with versions), with the DPC++ compiler ([llvmdpcpp](<https://github.com/intel/llvm>)) added.

## How to use

There are three ways to access the software provided by `prgenv-dpcpp`, once it has been started.

The simplest way to get started is to use the `default` file system view, which automatically loads all of the packages when the uenv is started.

> [!NOTE]
>
> **test the DPC++ compiler provided by prgenv-dpcpp/25.11**
>
> start the uenv and check the compiler
>
> ```console
> # start using the default view
> $ uenv start --view=default prgenv-dpcpp/25.11:v1
>
> # the DPC++ (SYCL) compiler is available
> $ which clang++
> /user-environment/env/default/bin/clang++
> ```

To compile SYCL code for the GH200 GPU, target the CUDA backend and point the compiler at the CUDA installation in the uenv with `--cuda-path`.

compile a SYCL source file for the GH200 GPU

```bash
export CUDA_PATH=$(ls -d /user-environment/linux-neoverse_v2/cuda-*)
clang++ -fsycl -fsycl-targets=nvptx64-nvidia-cuda \
    -Xsycl-target-backend --cuda-gpu-arch=sm_90 --cuda-path=$CUDA_PATH \
    source.cpp -o binary
```

To build MPI code, compile with the `mpicxx` wrapper and set `MPICH_CXX=clang++`, otherwise `mpicxx` falls back to `g++`, which does not understand `-fsycl`.

> [!NOTE]
>
> **oneAPI libraries not included**
>
> Only the DPC++ compiler is provided. oneAPI libraries such as oneDPL, oneMKL and oneTBB are not part of this uenv and must be provided separately, for example by cloning oneDPL and adding `-I<path>/oneDPL/include` to the compile command.

The uenv provides modules for all of the software packages, which can be made available by using the `modules` view. No modules are loaded when a uenv starts, and have to be loaded individually using `module load`.

> [!NOTE]
>
> **start prgenv-dpcpp and list the provided modules**
>
> list the modules provided by the uenv
>
> ```console
> $ uenv start prgenv-dpcpp/25.11:v1 --view=modules
> $ module avail
> ```

The uenv provides compilers, MPI, Python and common libraries, and can be used as a base for building further software with Spack.

[Check out the guide for using Spack with uenv](<https://docs.cscs.ch/build-install/uenv/index.md#building-software-using-spack> "Building software using Spack").
