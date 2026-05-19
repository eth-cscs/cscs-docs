[](){#ref-support-tickets}
# Submitting a support ticket

Requests for support must be submitted to our Service Desk.
[:octicons-arrow-right-24: Service Desk](https://support.cscs.ch)

If you're experiencing a service interruption, it may already be a known issue.
Please check the [status page](https://status.cscs.ch) first for the latest updates and ongoing incidents.

To help us diagnose and resolve issues as quickly as possible, please include as much relevant information as you can when submitting a support ticket.
Incomplete tickets often require additional back-and-forth before troubleshooting can begin.

A good support request should provide enough detail for our staff to understand:

* What you were trying to do
* What happened instead
* How the issue can be reproduced
* What software environment and resources were involved
* Whether the problem is new or ongoing

## Information to include

### Clear description of the problem

Please provide a clear and concise explanation of the issue.

Examples:

* "My Slurm job exits immediately with an out-of-memory error."
* "MPI jobs hang during startup on more than two nodes."
* "My application compiled successfully but crashes at runtime."

Please avoid reports such as:

* "My job failed."
* "The cluster is broken."

### Slurm job information

If the issue involves a batch or interactive Slurm job, include:

* Slurm Job ID(s)
* Submission script
* Number of nodes, tasks, and other resources requested
* Whether the issue occurs consistently or intermittently

### Standard output and standard error locations

Always provide the locations of the standard output and standard error and ensure these are readable.

Include, where possible:

* Relevant error messages
* Stack traces
* The last few lines of output before the job failure

Please make use of the available markdown features such as "Code snippet" and "Quote" when pasting code or logs.

### Steps to reproduce the problem

Support staff must be able to reproduce the issue wherever possible.

Please include:

* The commands you executed
* Required software environment (uenv, container description, etc.)
* Location of input data or configuration files as needed
* Exact sequence of actions leading to the failure

### Has this worked before?

This information is important in helping us track down the cause.

Please include:

* Whether this workflow has ever run successfully
* When it last worked
* What changed since then (if anything)

Examples:

* "This job ran successfully last Friday but started failing after I updated my virtual environment with X, Y."
* "This workflow has never run successfully on Clariden, but worked on Daint."
* "This issue began after the maintenance last Wednesday."

### Scope and impact

Please tell us:

* Does this issue affect one job or all jobs?
* Is the issue reproducible for other users?
* Is there an urgent deadline associated with the problem?

## Example of a good support ticket

```text
My MPI application hangs during initialization when running on 2 or more nodes on Daint.

Job ID: 123456

The issue occurs consistently when using 2 or more nodes but works correctly on a single node.

Stdout:
/capstor/scratch/cscs/alice/run_123456.out

Stderr:
/capstor/scratch/cscs/alice/run_123456.err

Batch file:
/capstor/scratch/cscs/alice/mpi_gpu.slurm

Steps to reproduce:

1. uenv start --view=default prgenv-gnu/25.6:v1
2. sbatch mpi_gpu.slurm

This workflow ran fine last month and no changes were made to the application code. The issue started this week.
```

## Before submitting a ticket

Please check:

* The job script for syntax errors
* Available disk quotas using the `quota` command
* Whether scheduled maintenance is in progress
* Whether the issue is already listed on the [status page](https://status.cscs.ch)

## Summary

Including detailed technical information in your support request significantly reduces turnaround time and helps staff diagnose issues efficiently.
In particular, always include:

* Slurm Job IDs
* Output and error log locations
* Exact steps to reproduce
* Software environment details
* Whether the issue is new or previously working
