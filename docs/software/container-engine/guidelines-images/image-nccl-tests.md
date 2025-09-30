[](){#ref-ce-guidelines-images-nccl-tests}
# NCCL Tests image

This page describes a container image featuring the [NCCL Tests](https://github.com/NVIDIA/nccl-tests) to demonstrate how to efficiently execute NCCL-based containerized software on Alps.

This image is based on the [OpenMPI image][ref-ce-guidelines-images-ompi], and thus it is suited for hosts with NVIDIA GPUs, like Alps GH200 nodes.

A build of this image is currently hosted on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/nccl-tests:2.17.1-ompi5.0.8-ofi1.22-cuda12.8`.

## Contents

- Ubuntu 24.04
- CUDA 12.8.1 (includes NCCL)
- GDRCopy 2.5.1
- Libfabric 1.22.0
- UCX 1.19.0
- OpenMPI 5.0.8
- NCCL Tests 2.17.1

## Containerfile
```Dockerfile
FROM quay.io/ethcscs/ompi:5.0.8-ofi1.22-cuda12.8

ARG nccl_tests_version=2.17.1
RUN wget -O nccl-tests-${nccl_tests_version}.tar.gz https://github.com/NVIDIA/nccl-tests/archive/refs/tags/v${nccl_tests_version}.tar.gz \
    && tar xf nccl-tests-${nccl_tests_version}.tar.gz \
    && cd nccl-tests-${nccl_tests_version} \
    && MPI=1 make -j$(nproc) \
    && cd .. \
    && rm -rf nccl-tests-${nccl_tests_version}.tar.gz
```

!!! note
    This image builds NCCL tests with MPI support enabled.

## Performance examples

### Environment Definition File
```toml
image = "quay.io#ethcscs/nccl-tests:2.17.1-ompi5.0.8-ofi1.22-cuda12.8"

[env]
PMIX_MCA_psec="native"

[annotations]
com.hooks.aws_ofi_nccl.enabled = "true"
com.hooks.aws_ofi_nccl.variant = "cuda12"
```

### Notes

- Since OpenMPI uses PMIx for wire-up and communication between ranks, when using this image the `srun` option `--mpi=pmix` must be used to run successful multi-rank jobs.
- NCCL requires the presence of the [AWS OFI NCCL plugin](https://github.com/aws/aws-ofi-nccl) in order to correctly interface with Libfabric and (through the latter) the Slingshot interconnect. Therefore, for optimal performance the [related CE hook][ref-ce-aws-ofi-hook] must be enabled and set to match the CUDA version in the container.
- Libfabric itself is usually injected by the [CXI hook][ref-ce-cxi-hook], which is enabled by default on several Alps vClusters.

### Results

=== "All-reduce latency test on 2 nodes, 8 GPUs"
    ```console
    $ srun -N2 -t5 --mpi=pmix --ntasks-per-node=4 --environment=nccl-test-ompi /nccl-tests-2.17.1/build/all_reduce_perf -b 8 -e 128M -f 2
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
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

### Results without the AWS OFI NCCL hook
This section demonstrates the performance benefit of the AWS OFI NCCL hook by not enabling it through the EDF:
```console
$ cat ~/.edf/nccl-test-ompi-no-awsofinccl.toml
image = "quay.io#ethcscs/nccl-tests:2.17.1-ompi5.0.8-ofi1.22-cuda12.8"

[env]
PMIX_MCA_psec="native"
```

=== "All-reduce latency test on 2 nodes, 8 GPUs"
    ```console
    $ srun -N2 -t5 --mpi=pmix --ntasks-per-node=4 --environment=nccl-test-ompi /nccl-tests-2.17.1/build/all_reduce_perf -b 8 -e 128M -f 2
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /nccl-tests-2.17.1/build/all_reduce_perf: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
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
