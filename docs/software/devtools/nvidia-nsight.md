[](){#ref-devtools-nsight}
# NVIDIA Nsight

## NVIDIA Nsight Systems

[NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems) is a system-wide performance analysis tool that enables developers to gain a deep understanding of how their applications utilize computing resources, such as CPUs, GPUs, memory, and I/O.
The tool provides a unified view of application performance across the entire system, capturing detailed trace information that allows users to analyze how different components interact and where performance issues might arise.

A key advantage of Nsight Systems is its ability to provide detailed traces of GPU activity, offering deeper insights into GPU utilization.
It features a timeline-based visualization, enabling developers to inspect the execution flow, pinpoint latencies, and correlate events across different system components.
As a sampling profiler, it can be easily used to profile applications written in C, C++, Python, Fortran, or Julia by wrapping the application with the Nsight Systems profiler executable.

!!! note
    NVIDIA Nsight Systems is available with any [uenv][ref-uenv] that comes with a CUDA compiler, for instance [`prgenv-gnu`][ref-uenv-prgenv-gnu].

## NVIDIA Nsight Compute

[NVIDIA Nsight Compute](https://developer.nvidia.com/nsight-compute) is a performance analysis tool specifically designed for optimizing GPU-accelerated applications.
It focuses on providing detailed metrics and insights into the performance of CUDA kernels, helping developers identify performance bottlenecks and improve the efficiency of their GPU code.
Nsight Compute offers a kernel-level profiler with customizable reports, enabling in-depth analysis of memory usage, compute utilization, and instruction throughput.
As a sampling profiler, it can be easily used to profile applications written in C, C++, Python, Fortran, or Julia by wrapping the application with the Nsight Compute profiler executable.

!!! note
    NVIDIA Nsight Systems is available with any [uenv][ref-uenv] that comes with a CUDA compiler, for instance [`prgenv-gnu`][ref-uenv-prgenv-gnu].

### Known Issues and Common Problems

??? warning "CrashReporter: Qt initialization failed, Failed to load Qt platform plugin: xcb"
    While we recommend using `ncu` instead of `ncu-ui`, it is possible to use X11 to launch ncu-ui.
    However, this will fail with the following error message: `Failed to load Qt platform plugin: "xcb"`.

    To workaround this issue, you can follow these instructions:

    ```bash
    ssh -Y -J <user>@ela.cscs.ch <user>@daint.alps.cscs.ch
    # the -Y ssh flag enables trusted X11 forwarding.
    wget https://jfrog.svc.cscs.ch/artifactory/cscs-reframe-tests/nvidia/ncu_deps.tar.gz
    tar xf ncu_deps.tar.gz
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD/usr/lib64
    ncu-ui &
    ```

