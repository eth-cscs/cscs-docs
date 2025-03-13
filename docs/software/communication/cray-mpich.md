[](){#ref-communication-cray-mpich}
# Cray MPICH

Cray MPICH is the recommended MPI implementation on Alps.
It is available through uenvs like [prgenv-gnu][ref-uenv-prgenv-gnu] and [the application-specific uenvs][ref-software-sciapps].

The [Cray MPICH documentation](https://cpe.ext.hpe.com/docs/latest/mpt/mpich/index.html) contains detailed information about Cray MPICH.
On this page we outline the most common workflows and issues that you may encounter on Alps.

## GPU-aware MPI

We recommend using GPU-aware MPI whenever possible, as it almost always provides a significant performance improvement compared to communication through CPU memory.
To use GPU-aware MPI with Cray MPICH

1. the application must be linked to the GTL library, and
2. the `MPICH_GPU_SUPPORT_ENABLED=1` environment variable must be set.

If either of these are missing, the application will fail to communicate GPU buffers.

In supported uenvs, Cray MPICH is built with GPU support (on clusters that have GPUs).
This means that Cray MPICH will automatically be linked to the GTL library, which implements the the GPU support for Cray MPICH.

??? info "Checking that the application links to the GTL library"

    To check if your application is linked against the required GTL library, running `ldd` on your executable `myexecutable` should print something similar to:
    ```bash
    $ ldd myexecutable | grep gtl
            libmpi_gtl_cuda.so => /user-environment/linux-sles15-neoverse_v2/gcc-13.2.0/cray-gtl-8.1.30-fptqzc5u6t4nals5mivl75nws2fb5vcq/lib/libmpi_gtl_cuda.so (0x0000ffff82aa0000)
    ```
    
    The path may be different, but the `libmpi_gtl_cuda.so` library should be printed when using CUDA.
    In ROCm environments the `libmpi_gtl_hsa.so` library should be linked.
    If the GTL library is not linked, nothing will be printed.

In addition to linking to the GTL library, Cray MPICH must be configured to be GPU-aware at runtime by setting the `MPICH_GPU_SUPPORT_ENABLED=1` environment variable.
On some CSCS systems this option is set by default.
See [this page][ref-slurm-gh200] for more information on configuring SLURM to use GPUs.

!!! warning "Segmentation faults when trying to communicate GPU buffers without `MPICH_GPU_SUPPORT_ENABLED=1`"
    If you attempt to communicate GPU buffers through MPI without setting `MPICH_GPU_SUPPORT_ENABLED=1`, it will lead to segmentation faults, usually without any specific indication that it is the communication that fails.
    Make sure that the option is set if you are communicating GPU buffers through MPI.
    
!!! warning "Error: "`GPU_SUPPORT_ENABLED` is requested, but GTL library is not linked""
    If `MPICH_GPU_SUPPORT_ENABLED` is set to `1` and your application does not link against one of the GTL libraries you will get an error similar to the following during MPI initialization:
    ```bash
    MPICH ERROR [Rank 0] [job id 410301.1] [Thu Feb 13 12:42:18 2025] [nid005414] - Abort(-1) (rank 0 in comm 0): MPIDI_CRAY_init: GPU_SUPPORT_ENABLED is requested, but GTL library is not linked
     (Other MPI error)

    aborting job:
    MPIDI_CRAY_init: GPU_SUPPORT_ENABLED is requested, but GTL library is not linked
    ```

    This means that the required GTL library was not linked to the application.
    In supported uenvs, GPU support is enabled by default.
    If you believe a uenv should have GPU support but you are getting the above error, feel free to [get in touch with us][ref-get-in-touch] to understand whether there is an issue with the uenv or something else in your environment. 
    If you are using Cray modules you must load the corresponding accelerator module, e.g. `craype-accel-nvidia90`, before compiling your application.

    Alternatively, if you wish to not use GPU-aware MPI, either unset `MPICH_GPU_SUPPORT_ENABLED` or explicitly set it to `0` in your launch scripts.

## Known issues

This section documents known issues related to Cray MPICH on Alps. Resolved issues are also listed for reference.

### Existing Issues

#### Cray MPICH hangs

Cray MPICH may sometimes hang on larger runs.

!!! info "Workaround"

    There are many possible reasons why an application would hang, many unrelated to Cray MPICH. However, if you are experiencing hangs the issue may be worked around by setting:
    ```bash
    export FI_MR_CACHE_MONITOR=disabled
    ```

Performance may be negatively affected by this option.

### Resolved issues

#### `"cxil_map: write error"` when doing inter-node GPU-aware MPI communication

??? info "The issue has been resolved on the 7th of October 2024 with a system update"
    The issue was caused by a system misconfiguration.

When doing inter-node GPU-aware communication with Cray MPICH after the update on the 30th of September 2024 on Alps, applications will fail with:
```bash
cxil_map: write error
```

??? info "Workaround"
    The only workaround is to not use inter-node GPU-aware MPI.

    ??? tip "Workaround for CP2K"
        For users of CP2K encountering this issue, one can disable the use of COSMA, which uses GPU-aware MPI, by placing the following in the `&GLOBAL` section of your input file: 
        ```bash
        &FM
        TYPE_OF_MATRIX_MULTIPLICATION SCALAPACK
        &END FM
        ```

        Unless you run RPA calculations, this should have limited impact on performance.

#### `MPI_THREAD_MULTIPLE` does not work

!!! info "The issue has been resolved in Cray MPICH version 8.1.30"

When using `MPI_THREAD_MULTIPLE` on GH200 systems Cray MPICH may fail with an assertion that looks similar to:
```bash
Assertion failed [...]: (&MPIR_THREAD_GLOBAL_ALLFUNC_MUTEX)->count == 0
```

or

```bash
Assertion failed [...]: MPIR_THREAD_GLOBAL_ALLFUNC_MUTEX.count == 0
```

??? info "Workaround"
    The issue can be worked around by falling back to a less optimized implementation of `MPICH_THREAD_MULTIPLE` by setting `MPICH_OPT_THREAD_SYNC=0`.
