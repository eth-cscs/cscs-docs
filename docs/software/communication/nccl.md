[](){#ref-communication-nccl}
# NCCL

[NCCL](https://developer.nvidia.com/nccl) is an optimized inter-GPU communication library for NVIDIA GPUs.
It is commonly used in machine learning frameworks, but traditional scientific applications can also benefit from NCCL.

## Using NCCL

To use the Slingshot network on Alps, the [`aws-ofi-nccl`](https://github.com/aws/aws-ofi-nccl) plugin must be used.
With the container engine, the [AWS OFI NCCL hook][ref-ce-aws-ofi-hook] can be used to load the plugin into the container and configure NCCL to use it.

Most uenvs, like [`prgenv-gnu`][ref-uenv-prgenv-gnu], also contain the NCCL plugin.
When using e.g. the `default` view of `prgenv-gnu` the `aws-ofi-nccl` plugin will be available in the environment.
Alternatively, loading the `aws-ofi-nccl` module with the `modules` view also makes the plugin available in the environment.
The environment variables described below must be set to ensure that NCCL uses the plugin.

While the container engine sets these automatically when using the NCCL hook, the following environment variables should always be set for correctness and optimal performance when using NCCL with uenv:

```bash
--8<-- "docs/software/communication/nccl_env_vars"
```

[_Demystifying NCCL: An In-depth Analysis of GPU Communication Protocols and Algorithms_](https://arxiv.org/abs/2507.04786v2) contains detailed information about NCCL algorithms and protocols, which can be helpful for deciding if your application could benefit from an alternative configuration.

In addition to the above variables, setting `NCCL_NCHANNELS_PER_NET_PEER` can improve point-to-point performance (operations based directly on send/recv):

```bash
export NCCL_NCHANNELS_PER_NET_PEER=4
```

A value of 4 is generally a good compromise to improve point-to-point performance without affecting collectives performance.
Setting it to a higher value such as 16 or 32 can still further improve send/recv performance, but may degrade collectives performance, so the optimal value depends on the mix of operations used in an application.
The option is undocumented, but [this issue](https://github.com/NVIDIA/nccl/issues/1272) and the paper linked above contain additional details.

!!! warning "NCCL watchdog timeout or hanging process"
    In some cases, still under investigation, NCCL may hang resulting in a stuck process or a watchdog timeout error.
    In this scenario, we recommend disabling Slingshot eager messages with the following workaround:
    ```bash
    # Disable eager messages to avoid NCCL timeouts
    export FI_CXI_RDZV_GET_MIN=0
    export FI_CXI_RDZV_THRESHOLD=0
    export FI_CXI_RDZV_EAGER_SIZE=0
    ```

!!! warning "Using NCCL with uenvs"
    The environment variables listed above are not set automatically when using uenvs.

!!! warning "GPU-aware MPI with NCCL"
    Using GPU-aware MPI together with NCCL [can easily lead to deadlocks](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/mpi.html#inter-gpu-communication-with-cuda-aware-mpi).
    Unless care is taken to ensure that the two methods of communication are not used concurrently, we recommend not using GPU-aware MPI with NCCL.
    To explicitly disable GPU-aware MPI with Cray MPICH, explicitly set `MPICH_GPU_SUPPORT_ENABLED=0`.
    Note that this option may be set to `1` by default on some Alps clusters.
    See [the Cray MPICH documentation][ref-communication-cray-mpich] for more details on GPU-aware MPI with Cray MPICH.

!!! warning "`invalid usage` error with `NCCL_NET="AWS Libfabric"`"
    If you are getting error messages such as:
    ```console
    nid006352: Test NCCL failure common.cu:958 'invalid usage (run with NCCL_DEBUG=WARN for details)
    ```
    this may be due to the plugin not being found by NCCL.
    If this is the case, running the application with the recommended `NCCL_DEBUG=WARN` should print something similar to the following:
    ```console
    nid006352:34157:34217 [1] net.cc:626 NCCL WARN Error: network AWS Libfabric not found.
    ```
    When using uenvs like `prgenv-gnu`, make sure you are either using the `default` view which loads `aws-ofi-nccl` automatically, or, if using the `modules` view, load the `aws-ofi-nccl` module with `module load aws-ofi-nccl`.
    If the plugin is found correctly, running the application with `NCCL_DEBUG=INFO` should print:
    ```console
    nid006352:34610:34631 [0] NCCL INFO Using network AWS Libfabric
    ```

!!! warning "Do not use `NCCL_NET_PLUGIN="ofi"` with uenvs"
    NCCL has an alternative way of specifying what plugin to use: `NCCL_NET_PLUGIN`.
    When using uenvs, do not set `NCCL_NET_PLUGIN="ofi"` instead of, or in addition to, `NCCL_NET="AWS Libfabric"`.
    If you do, your application will fail to start since NCCL will:

    1. fail to find the plugin because of the name of the shared library in the uenv, and
    2. prefer `NCCL_NET_PLUGIN` over `NCCL_NET`, so it will fail to find the plugin even if `NCCL_NET="AWS Libfabric"` is correctly set.
    
    When both environment variables are set the error message, with `NCCL_DEBUG=WARN`, will look similar to when the plugin isn't available:
    ```console
    nid006365:179857:179897 [1] net.cc:626 NCCL WARN Error: network AWS Libfabric not found.
    ```
    
    With `NCCL_DEBUG=INFO`, NCCL will print:
    ```console
    nid006365:180142:180163 [0] NCCL INFO NET/Plugin: Could not find: ofi libnccl-net-ofi.so. Using internal network plugin.
    ...
    nid006365:180142:180163 [0] net.cc:626 NCCL WARN Error: network AWS Libfabric not found.
    ```
    
    If you only set `NCCL_NET="ofi"`, NCCL may silently fail to load the plugin but fall back to the default implementation.

## Expected performance

This section covers the expected performance behavior of the [NCCL Tests benchmark](https://github.com/NVIDIA/nccl-tests) suite on Alps.
This information can be used as a reference for comparing with application behavior.
The [NCCL Stack Constellation Benchmarks](https://github.com/jpcoles-cscs/nccl-stack-constellation-benchmarks) can be used to reproduce this information and also build and run the tests within a user's own environment.

=== "NCCL v2.26"
    === "Plots"
        [Download PDF](nccl-assets/nccl-plots-226.pdf)
        ![NCCL v2.26 benchmark performance](nccl-assets/nccl-plots-226.png)
    === "Environment Settings"
        [Download settings](nccl-assets/config_v226.sh)
        ```bash
        --8<-- "docs/software/communication/nccl-assets/config_v226.sh"
        ```
    === "Tuner parameters"
        [Download parameters](nccl-assets/nccl_tuner_v226.conf)
        ```
        --8<-- "docs/software/communication/nccl-assets/nccl_tuner_v226.conf"
        ```

=== "NCCL v2.27"
=== "NCCL v2.28"

## NCCL Tuner Plugin

NCCL has internal logic to choose the most performant communication algorithm given collective, message size, number of ranks, and other system characteristics.
This logic has been optimized for the infiniband network and can perform suboptimally on the Slinghshot network of Alps.

To achieve best results, it is necessary to use the NCCL Tuner Plugin along side a tuner configuration file.
A modified tuner plugin for Alps is included in a [forked version of NCCL](https://github.com/jpcoles-cscs/nccl).
The forked repository is only needed for building the tuner and is compatible with versions of NCCL >= 2.24 that support the `ncclTunerPlugin_v4` data structure.
CSCS has prepared example configuration files for use in these benchmarks and can be used as a reference point for application-specific tuning.

To use the CSCS tuner, first download, build, and copy the library to a preferred location:
```console
git clone --branch 2.27.7-1-cscs-tuner git@github.com:jpcoles-cscs/nccl.git nccl-tuner-cscs/nccl
cd nccl-tuner-cscs/nccl/ext-tuner/example
make
cp libnccl-tuner-example.so $INSTALL_DIR/libnccl-tuner-cscs.so
```
Then point NCCL to the tuner library:
```bash
export NCCL_TUNER_PLUGIN=$INSTALL_DIR/libnccl-tuner-cscs.so
```


