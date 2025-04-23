# Cray Programming Environment (CPE)

!!! warning
    you don't want to use this

!!! mlp
    The CPE is not provided on the machine learning platform.

!!! cwp
    The CPE is not provided on the climage and weather platform

## CPE in a container
!!! info
    Currently it is mandatory to export the EDF path manually
    ```
    export EDF_PATH=/capstor/scratch/cscs/anfink/shared/cpe/edf:$EDF_PATH
    ```

To start a container with the cray programming environment, there are pre-defined EDF toml files. Currently they are stored in `/capstor/scratch/cscs/anfink/shared/cpe/edf`, but this will change in the future to a different location.
Every toml file in this edf path is a programming environment that can be started
```
[daint][anfink@daint-ln001 ~]$ ls -lh /capstor/scratch/cscs/anfink/shared/cpe/edf
total 8.0K
-rw-r--r--+ 1 anfink csstaff 175 Apr 23 11:48 cpe-cray-24.07.toml
-rw-r--r--+ 1 anfink csstaff 174 Apr 23 11:32 cpe-gnu-24.07.toml
```
Following the naming scheme from the output, you can spawn a container with
```
srun --environment=cpe-cray-24.07 --pty bash
```
Once the container starts up you can directly use the programming environment, because there will be modules loaded by default at startup.
```
[daint][anfink@daint-ln001 ~]$ srun -p debug --environment=cpe-gnu-24.07 --pty bash
[daint][anfink@nid005417 /]$ module list

Currently Loaded Modules:
  1) craype-arm-grace   2) craype-network-ofi   3) xpmem/2.9.6   4) gcc-native/13.2   5) craype/2.7.32   6) PrgEnv-gnu/8.5.0   7) cray-mpich/8.1.30   8) cuda/12.6   9) craype-accel-nvidia90



[daint][anfink@nid005417 /]$ module avail

----------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/mpi/gnu/12.0/ofi/1.0/cray-mpich/8.0 -----------------------------------------------------------------------------------------------------------------------------------------------------
   cray-hdf5-parallel/1.14.3.1    cray-parallel-netcdf/1.12.3.13

----------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/comnet/gnu/12.0/ofi/1.0 -----------------------------------------------------------------------------------------------------------------------------------------------------------
   cray-mpich-abi/8.1.30    cray-mpich/8.1.30 (L)

---------------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/mix_compilers ----------------------------------------------------------------------------------------------------------------------------------------------------------------
   gcc-native-mixed/13.2

-------------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/compiler/gnu/12.0 --------------------------------------------------------------------------------------------------------------------------------------------------------------
   cray-hdf5/1.14.3.1    cray-libsci/24.07.0

-------------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/cpu/arm-grace/1.0 --------------------------------------------------------------------------------------------------------------------------------------------------------------
   cray-fftw/3.3.10.8

----------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/craype-targets/default ------------------------------------------------------------------------------------------------------------------------------------------------------------
   craype-accel-amd-gfx908    craype-accel-amd-gfx942    craype-accel-nvidia80        craype-hugepages128M    craype-hugepages256M    craype-hugepages32M     craype-hugepages64M    craype-network-ofi (L)    craype-x86-milan-x    craype-x86-spr-hbm
   craype-accel-amd-gfx90a    craype-accel-host          craype-accel-nvidia90 (L)    craype-hugepages16M     craype-hugepages2G      craype-hugepages4M      craype-hugepages8M     craype-network-ucx        craype-x86-milan      craype-x86-spr
   craype-accel-amd-gfx940    craype-accel-nvidia70      craype-arm-grace      (L)    craype-hugepages1G      craype-hugepages2M      craype-hugepages512M    craype-network-none    craype-x86-genoa          craype-x86-rome       craype-x86-trento

-------------------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/pe/lmod/modulefiles/core ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   PrgEnv-gnu/8.5.0 (L)    cray-libsci_acc/24.07.0    cray-pmi/6.1.15.19    cray-python/3.11.7    craype/2.7.32 (L)    gcc-native/13.2 (L)

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cray/modulefiles ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   xpmem/2.9.6 (L)

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- /opt/cscs/modulefiles ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   cuda/12.6 (L)

  Where:
   L:  Module is loaded

If the avail list is too long consider trying:

"module --default avail" or "ml -d av" to just list the default modules.
"module overview" or "ml ov" to display the number of modules for each name.

Use "module spider" to find all possible modules and extensions.
Use "module keyword key1 key2 ..." to search for all possible modules matching any of the "keys".


[daint][anfink@nid005417 /]$ CC --version
g++-13 (SUSE Linux) 13.3.0
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

[daint][anfink@nid005417 /]$
```

The recommended way of using CPE in a container is to start the container, and use `$SCRATCH` and `$STORE` to interact with persistent data. Please remember that any data that is written to a directory that is not mounted from the host system will be lost, after the container stops.

By default, the paths `/capstor`, `/iopsstor` are mounted to the same paths inside the container.

Additionally `/users` will be mounted at `/users.host`, so you can access data in your home folder, but with a slightly different path. This is on purpose, and you can override this behaviour by writing your own [EDF file][ref-ce-edf-reference], especially using the key `base_environment`, referencing the predefined CPE environment files and override what you would like to change.
