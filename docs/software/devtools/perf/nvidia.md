[](){#ref-software-devtools-perf-nvidia}
## NVIDIA Nsight Systems

[NVIDIA Nsight Systems](https://developer.nvidia.com/nsight-systems) 
is a system-wide performance analysis tool that enables developers to gain a
deep understanding of how their applications utilize computing resources, such
as CPUs, GPUs, memory, and I/O. The tool provides a unified view of an
application\'s performance across the entire system, capturing detailed trace
information that allows users to analyze how different components interact and
where performance issues might arise. A key advantage of Nsight Systems is its
ability to provide detailed traces of GPU activity, offering deeper insights
into GPU utilization. It features a timeline-based visualization, enabling
developers to inspect the execution flow, pinpoint latencies, and correlate
events across different system components. As a sampling profiler, it can be
easily used to profile applications written in C, C++, Python, Fortran, or
Julia by wrapping the application with the Nsight Systems profiler executable.
`NVIDIA Nsight Systems` is available with any UENV that comes with a CUDA
compiler.

## NVIDIA Nsight Compute

[NVIDIA Nsight Compute](https://developer.nvidia.com/nsight-compute) is a
performance analysis tool specifically designed for optimizing GPU-accelerated
applications. It focuses on providing detailed metrics and insights into the
performance of CUDA kernels, helping developers identify performance
bottlenecks and improve the efficiency of their GPU code. Nsight Compute offers
a kernel-level profiler with customizable reports, enabling in-depth analysis
of memory usage, compute utilization, and instruction throughput. As a sampling
profiler, it can be easily used to profile applications written in C, C++,
Python, Fortran, or Julia by wrapping the application with the Nsight Compute
profiler executable. `NVIDIA Nsight Compute` is available with any
[UENV][ref-uenv] that comes with a CUDA compiler.
