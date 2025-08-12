[](){#ref-known-issues}
# Known Issues

## Out of Memory on GH200 nodes
There is a known issue with Nvidia GPU driver version R550.54.15, currently installed on all GH200 nodes, that can reduce the amount of available GPU memory.

Under normal conditions, Linux in-memory file caches may migrate from CPU to GPU memory. Allocating GPU memory should trigger the eviction of these caches, freeing up GPU memory. However, due to this bug, eviction does not occur, leading to out-of-memory errors.

Applications with heavy I/O workloads are especially affected, as increased I/O generates more cached data. While we currently ensure that at least 90% of GPU memory is available when a node is allocated to a job, available memory may still decrease during the job’s execution.

This issue is fixed in driver version R570, which will be deployed during a future system maintenance.

