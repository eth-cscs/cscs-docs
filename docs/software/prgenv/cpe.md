[](){#ref-cpe}
# Cray Programming Environment (CPE)

The Cray Programming Environment (CPE) is a suite of software: programming environments, compilers, libraries and tools.

The CPE is provided to users on Alps as containers.

!!! info "CPE is the cray modules"
    The familiar modules that provide the `Prgenv-gnu` and `Prgenv-cray`  programming environments, and packages like `cray-python` and `cray-fftw`, that will be familiar from the old Piz Daint system.

!!! warning "CPE is not supported on Alps"
    The Cray modules were provided on the old Daint system, and CSCS supported their use and provided software built on top of them.

    **Alps is a big change - the CPE modules are not provide as officially supported software.**
    They are provided _as is_ to users who still need to use them, however CSCS will not be able to provide detailed support for issues that arise when using them.

    The recommended method for building and running software is to use [uenv][ref-uenv] or [containers][ref-container-engine].

## CPE in a container

[](){#ref-cpe-versions}
### Available versions

The `PrgEnv-gnu` and `PrgEnv-cray` programming environments are provided as separate containers, instead of having both in one container, named `gnu-$version` and `cray-$version` respectively.
The `version` is the CPE version in the container.

Deployed versions can be found at `/capstor/store/cscs/cscs/public/containers/edf/<microarchitecture>`.

!!! example "Listing all available CPE containers"
    ```console
    $ find /capstor/store/cscs/cscs/public/containers/edf -type f -printf '%P\n'
    zen2/cpe-cray-24.07.toml
    zen2/cpe-cray-25.03.toml
    zen2/cpe-gnu-25.03.toml
    zen2/cpe-gnu-24.07.toml
    zen2/.cpe-base.toml
    gh200/cpe-cray-24.07.toml
    gh200/cpe-cray-25.03.toml
    gh200/cpe-gnu-25.03.toml
    gh200/cpe-gnu-24.07.toml
    gh200/.cpe-base.toml
    ```

|                 | `zen2`   | `gh200` |
|-----------------|----------|---------|
| `cpe-gnu-24.7`  | ✅       | ✅      |
| `cpe-cray-24.7` | ✅       | ✅      |
| `cpe-gnu-25.3`  | ✅       | ✅      |
| `cpe-cray-25.3` | ✅       | ✅      |

### How to use

To start a session with the CPE (see [available-versions][ref-cpe-versions] above):
```console
$ srun --environment=cpe-cray-24.07 --pty bash
```
Once the container starts up you can directly use the programming environment, because there will be modules loaded by default at startup.

```console
$ srun -p debug --environment=cpe-cray-24.07 --pty bash
$ module list

Currently Loaded Modules:
  1) craype-arm-grace     4) cce/18.0.0          7) cray-mpich/8.1.30
  2) craype-network-ofi   5) craype/2.7.32       8) cuda/12.6
  3) xpmem/2.9.6          6) PrgEnv-cray/8.5.0   9) craype-accel-nvidia90


$ module avail

---- /opt/cray/pe/lmod/modulefiles/mpi/crayclang/17.0/ofi/1.0/cray-mpich/8.0 ----
   cray-hdf5-parallel/1.14.3.1    cray-parallel-netcdf/1.12.3.13

---------- /opt/cray/pe/lmod/modulefiles/comnet/crayclang/17.0/ofi/1.0 ----------
   cray-mpich-abi/8.1.30    cray-mpich/8.1.30 (L)

------------- /opt/cray/pe/lmod/modulefiles/compiler/crayclang/17.0 -------------
   cray-hdf5/1.14.3.1    cray-libsci/24.07.0

------------------ /opt/cray/pe/lmod/modulefiles/mix_compilers ------------------
   cce-mixed/18.0.0

---------------- /opt/cray/pe/lmod/modulefiles/cpu/arm-grace/1.0 ----------------
   cray-fftw/3.3.10.8

------------- /opt/cray/pe/lmod/modulefiles/craype-targets/default --------------
   craype-accel-amd-gfx908        craype-hugepages16M     craype-network-none
   craype-accel-amd-gfx90a        craype-hugepages1G      craype-network-ofi  (L)
   craype-accel-amd-gfx940        craype-hugepages256M    craype-network-ucx
   craype-accel-amd-gfx942        craype-hugepages2G      craype-x86-genoa
   craype-accel-host              craype-hugepages2M      craype-x86-milan-x
   craype-accel-nvidia70          craype-hugepages32M     craype-x86-milan
   craype-accel-nvidia80          craype-hugepages4M      craype-x86-rome
   craype-accel-nvidia90   (L)    craype-hugepages512M    craype-x86-spr-hbm
   craype-arm-grace        (L)    craype-hugepages64M     craype-x86-spr
   craype-hugepages128M           craype-hugepages8M      craype-x86-trento

---------------------- /opt/cray/pe/lmod/modulefiles/core -----------------------
   PrgEnv-cray/8.5.0 (L)    cray-libsci_acc/24.07.0    cray-python/3.11.7
   cce/18.0.0        (L)    cray-pmi/6.1.15.19         craype/2.7.32      (L)

----------------------------- /opt/cray/modulefiles -----------------------------
   xpmem/2.9.6 (L)

----------------------------- /opt/cscs/modulefiles -----------------------------
   cuda/12.6 (L)

$ CC --version
Cray clang version 18.0.0  (0e4696aa65fa9549bd5e19c216678cc98185b0f7)
Target: aarch64-unknown-linux-gnu
Thread model: posix
InstalledDir: /opt/cray/pe/cce/18.0.0/cce-clang/aarch64/share/../bin
```

The recommended way of using CPE in a container is to start the container, and use `$SCRATCH` and `$STORE` to interact with persistent data. Please remember that any data that is written to a directory that is not mounted from the host system will be lost, after the container stops.

!!! note
    By default, the paths `/capstor`, `/iopsstor` are mounted to the same paths inside the container.

!!! note
    `/users` will not be mounted by default.
    If you need your home directory, you need to override the `mounts` directive.
    The recommended way is to derive from existing EDF file using the key `base_environment`, further details at [EDF file reference][ref-ce-edf-reference].
