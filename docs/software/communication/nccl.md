[](){#ref-communication-nccl}
# NCCL

[NCCL](https://developer.nvidia.com/nccl) is an optimized inter-GPU communication library for NVIDIA GPUs.
It is commonly used in machine learning frameworks, but traditional scientific applications can also benefit from NCCL.

[](){#ref-communication-nccl-using}
## Using NCCL

!!! info "Further reading"
    [_Demystifying NCCL: An In-depth Analysis of GPU Communication Protocols and Algorithms_](https://arxiv.org/abs/2507.04786v2) contains detailed information about NCCL algorithms and protocols, which can be helpful for deciding if your application could benefit from an alternative configuration.

[](){#ref-communication-nccl-uenv}
### uenv

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

[](){#ref-communication-nccl-ce}
### Containers

To use NCCL in a container, we suggest using a container provided by NVIDIA that already contains CUDA and NCCL, and using the [AWS OFI hook][ref-ce-aws-ofi-hook] to configure NCCL to use [libfabric][ref-communication-libfabric] optimised for the Alps network.

The example container files provided in the [libfabric][ref-communication-libfabric-ce] documentation, and as a base for the [OpenMPI][ref-communication-openmpi-ce] and [NVSHMEM][ref-communication-nvshmem-ce] containers is based on an NVIDIA image like ``docker.io/nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04`.

!!! example "Installing the NCCL benchmarks in a container for NVIDIA nodes"
    To test whether NCCL inside a container has been set up correctly for optimal performance, add the NCCL test suite to the container.
    Use the following as the starting point for installing the tests:

    ```Dockerfile
    --8<-- "docs/software/communication/dockerfiles/nccl-tests"
    ```

    Expand the box below for an example of a full Containerfile that installs libfabric and the NCCL tests on a base container provided by NVIDIA with CUDA and NCCL:

    ??? note "The full Containerfile"
        ```Dockerfile
        --8<-- "docs/software/communication/dockerfiles/base"
        --8<-- "docs/software/communication/dockerfiles/libfabric"
        --8<-- "docs/software/communication/dockerfiles/ucx"
        --8<-- "docs/software/communication/dockerfiles/nccl-tests"
        ```

[](){#ref-communication-nccl-issues}
## Known issues

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

[](){#ref-communication-nccl-performance}
## NCCL Performance

!!! warning "no version information available"
    The following warning message was generated by each rank running the benchmarks below, and can safely be ignored.
    ```
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    ```

!!! note "impact of disabling the CXI hook"
    On many Alps vClusters, the Container Engine is configured with the [CXI hook][ref-ce-cxi-hook] enabled by default, enabling transparent access to the Slingshot interconnect.

    The inter node tests marked with `(*)` were run with the CXI container hook disabled, to demonstrate the effect of not using an optimised network configuration.
    If you see similar performance degradation in your tests, the first thing to investigate is whether your setup is using the libfabric optimised back end.

Below are the results of of running the collective all reduce latency test on 2 nodes with 8 GPUs total (the `all_reduce_perf` test).

=== "All-reduce latency"
    ```console
    $ srun -N2 -t5 --mpi=pmix --ntasks-per-node=4 --environment=nccl-test-ompi /nccl-tests-2.17.1/build/all_reduce_perf -b 8 -e 128M -f 2
    # Collective test starting: all_reduce_perf
    # nThread 1 nGpus 1 minBytes 8 maxBytes 134217728 step: 2(factor) warmup iters: 1 iters: 20 agg iters: 1 validation: 1 graph: 0
    #
    # Using devices
    #  Rank  0 Group  0 Pid 204199 on  nid005471 device  0 [0009:01:00] NVIDIA GH200 120GB
    #  Rank  1 Group  0 Pid 204200 on  nid005471 device  1 [0019:01:00] NVIDIA GH200 120GB
    #  Rank  2 Group  0 Pid 204201 on  nid005471 device  2 [0029:01:00] NVIDIA GH200 120GB
    #  Rank  3 Group  0 Pid 204202 on  nid005471 device  3 [0039:01:00] NVIDIA GH200 120GB
    #  Rank  4 Group  0 Pid 155254 on  nid005487 device  0 [0009:01:00] NVIDIA GH200 120GB
    #  Rank  5 Group  0 Pid 155255 on  nid005487 device  1 [0019:01:00] NVIDIA GH200 120GB
    #  Rank  6 Group  0 Pid 155256 on  nid005487 device  2 [0029:01:00] NVIDIA GH200 120GB
    #  Rank  7 Group  0 Pid 155257 on  nid005487 device  3 [0039:01:00] NVIDIA GH200 120GB
    #
    #                                                              out-of-place                       in-place          
    #       size         count      type   redop    root     time   algbw   busbw #wrong     time   algbw   busbw #wrong
    #        (B)    (elements)                               (us)  (GB/s)  (GB/s)            (us)  (GB/s)  (GB/s)       
               8             2     float     sum      -1    17.93    0.00    0.00      0    17.72    0.00    0.00      0
              16             4     float     sum      -1    17.65    0.00    0.00      0    17.63    0.00    0.00      0
              32             8     float     sum      -1    17.54    0.00    0.00      0    17.43    0.00    0.00      0
              64            16     float     sum      -1    19.27    0.00    0.01      0    19.21    0.00    0.01      0
             128            32     float     sum      -1    18.86    0.01    0.01      0    18.67    0.01    0.01      0
             256            64     float     sum      -1    18.83    0.01    0.02      0    19.02    0.01    0.02      0
             512           128     float     sum      -1    19.72    0.03    0.05      0    19.40    0.03    0.05      0
            1024           256     float     sum      -1    20.35    0.05    0.09      0    20.32    0.05    0.09      0
            2048           512     float     sum      -1    22.07    0.09    0.16      0    21.72    0.09    0.17      0
            4096          1024     float     sum      -1    31.97    0.13    0.22      0    31.58    0.13    0.23      0
            8192          2048     float     sum      -1    37.21    0.22    0.39      0    35.84    0.23    0.40      0
           16384          4096     float     sum      -1    37.29    0.44    0.77      0    36.53    0.45    0.78      0
           32768          8192     float     sum      -1    39.61    0.83    1.45      0    37.09    0.88    1.55      0
           65536         16384     float     sum      -1    61.03    1.07    1.88      0    68.45    0.96    1.68      0
          131072         32768     float     sum      -1    81.41    1.61    2.82      0    72.94    1.80    3.14      0
          262144         65536     float     sum      -1    127.0    2.06    3.61      0    108.9    2.41    4.21      0
          524288        131072     float     sum      -1    170.3    3.08    5.39      0    349.6    1.50    2.62      0
         1048576        262144     float     sum      -1    164.3    6.38   11.17      0    187.7    5.59    9.77      0
         2097152        524288     float     sum      -1    182.1   11.51   20.15      0    180.6   11.61   20.32      0
         4194304       1048576     float     sum      -1    292.7   14.33   25.08      0    295.4   14.20   24.85      0
         8388608       2097152     float     sum      -1    344.5   24.35   42.61      0    345.7   24.27   42.47      0
        16777216       4194304     float     sum      -1    461.7   36.34   63.59      0    454.0   36.95   64.67      0
        33554432       8388608     float     sum      -1    686.5   48.88   85.54      0    686.6   48.87   85.52      0
        67108864      16777216     float     sum      -1   1090.5   61.54  107.69      0   1083.5   61.94  108.39      0
       134217728      33554432     float     sum      -1   1916.4   70.04  122.57      0   1907.8   70.35  123.11      0
    # Out of bounds values : 0 OK
    # Avg bus bandwidth    : 19.7866 
    #
    # Collective test concluded: all_reduce_perf
    ```

=== "All-reduce latency (*)"
    ```console
    $ srun -N2 -t5 --mpi=pmix --ntasks-per-node=4 --environment=nccl-test-ompi /nccl-tests-2.17.1/build/all_reduce_perf -b 8 -e 128M -f 2
    # Collective test starting: all_reduce_perf
    # nThread 1 nGpus 1 minBytes 8 maxBytes 134217728 step: 2(factor) warmup iters: 1 iters: 20 agg iters: 1 validation: 1 graph: 0
    #
    # Using devices
    #  Rank  0 Group  0 Pid 202829 on  nid005471 device  0 [0009:01:00] NVIDIA GH200 120GB
    #  Rank  1 Group  0 Pid 202830 on  nid005471 device  1 [0019:01:00] NVIDIA GH200 120GB
    #  Rank  2 Group  0 Pid 202831 on  nid005471 device  2 [0029:01:00] NVIDIA GH200 120GB
    #  Rank  3 Group  0 Pid 202832 on  nid005471 device  3 [0039:01:00] NVIDIA GH200 120GB
    #  Rank  4 Group  0 Pid 154517 on  nid005487 device  0 [0009:01:00] NVIDIA GH200 120GB
    #  Rank  5 Group  0 Pid 154518 on  nid005487 device  1 [0019:01:00] NVIDIA GH200 120GB
    #  Rank  6 Group  0 Pid 154519 on  nid005487 device  2 [0029:01:00] NVIDIA GH200 120GB
    #  Rank  7 Group  0 Pid 154520 on  nid005487 device  3 [0039:01:00] NVIDIA GH200 120GB
    #
    #                                                              out-of-place                       in-place          
    #       size         count      type   redop    root     time   algbw   busbw #wrong     time   algbw   busbw #wrong
    #        (B)    (elements)                               (us)  (GB/s)  (GB/s)            (us)  (GB/s)  (GB/s)       
               8             2     float     sum      -1    85.47    0.00    0.00      0    53.44    0.00    0.00      0
              16             4     float     sum      -1    52.41    0.00    0.00      0    51.11    0.00    0.00      0
              32             8     float     sum      -1    50.45    0.00    0.00      0    50.40    0.00    0.00      0
              64            16     float     sum      -1    62.58    0.00    0.00      0    50.70    0.00    0.00      0
             128            32     float     sum      -1    50.94    0.00    0.00      0    50.77    0.00    0.00      0
             256            64     float     sum      -1    50.76    0.01    0.01      0    51.77    0.00    0.01      0
             512           128     float     sum      -1    163.2    0.00    0.01      0    357.5    0.00    0.00      0
            1024           256     float     sum      -1    373.0    0.00    0.00      0    59.31    0.02    0.03      0
            2048           512     float     sum      -1    53.22    0.04    0.07      0    52.58    0.04    0.07      0
            4096          1024     float     sum      -1    55.95    0.07    0.13      0    56.63    0.07    0.13      0
            8192          2048     float     sum      -1    58.52    0.14    0.24      0    58.62    0.14    0.24      0
           16384          4096     float     sum      -1    108.7    0.15    0.26      0    107.8    0.15    0.27      0
           32768          8192     float     sum      -1    184.1    0.18    0.31      0    183.5    0.18    0.31      0
           65536         16384     float     sum      -1    325.0    0.20    0.35      0    325.4    0.20    0.35      0
          131072         32768     float     sum      -1    592.7    0.22    0.39      0    591.5    0.22    0.39      0
          262144         65536     float     sum      -1    942.0    0.28    0.49      0    941.4    0.28    0.49      0
          524288        131072     float     sum      -1   1143.1    0.46    0.80      0   1138.0    0.46    0.81      0
         1048576        262144     float     sum      -1   1502.2    0.70    1.22      0   1478.9    0.71    1.24      0
         2097152        524288     float     sum      -1    921.8    2.28    3.98      0    899.8    2.33    4.08      0
         4194304       1048576     float     sum      -1   1443.1    2.91    5.09      0   1432.7    2.93    5.12      0
         8388608       2097152     float     sum      -1   2437.7    3.44    6.02      0   2417.0    3.47    6.07      0
        16777216       4194304     float     sum      -1   5036.9    3.33    5.83      0   5003.6    3.35    5.87      0
        33554432       8388608     float     sum      -1    17388    1.93    3.38      0    17275    1.94    3.40      0
        67108864      16777216     float     sum      -1    21253    3.16    5.53      0    21180    3.17    5.54      0
       134217728      33554432     float     sum      -1    43293    3.10    5.43      0    43396    3.09    5.41      0
    # Out of bounds values : 0 OK
    # Avg bus bandwidth    : 1.58767 
    #
    # Collective test concluded: all_reduce_perf
    ```

