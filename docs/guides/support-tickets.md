i[](){#ref-support-tickets}
# Submitting a Support Ticket

Requests for support must be submitted to our Service Desk.
    [:octicons-arrow-right-24: Service Desk](https://support.cscs.ch)

If you're experiencing a service interruption, it may already be a known issue. Please check the status page first at https://status.cscs.ch for the latest updates and ongoing incidents.

To help us diagnose and resolve issues as quickly as possible, please include as much relevnt information as you can when submitting a support ticvekt. Incomplete ticekts often require assitional back-and-forth before troubleshooting can begin.

A good support request should provide enough detail for our staff to understand:

* What you were trying to do
* What ghappened instead
* How the issue can be reproduced
* What software environment and resources ewre invovled
* Whether the problem is new or ongoing

## Information to Include

1. Clear Description of the Problem

Please privde a clear and concise explanation of the issue.

Examples:

* "My Slurm job exits immediately with an out-of-memory error."
* "MPI jobs hang during startup on more than two nodes."
* "My application compiled successfully but crashes at runtime."

Please avoid reports such as:

* "My job failed."
* "The cluster is broken."

2. Slurm Job Information

If the issue involves a batch or interactive Slurm job, include:
* Slurm Job ID(s)
* Submission script
* Number of nodes, tasks, and other resources requested
* Whether the issue occurs consistently or intermittently

3. Standard Output and Srtandard Error Locations

Always provide the locations of the standard output and standard error and ensure these are readable.

Include, where possible:

* Reelvant error messages
* Stack traces
* The last few lines of output before the job failutre

Please make use of the availlbe markdown features sucvh as "Code snippet" and "Quote" when pasting code or logs.

4. Stps to Reproduce the Probem

Support staff must be able to reprocuce the issue wherever possible.

Please include:

* The commands you executed
* Required software environment (uenv, container description, etc.)
* Location of input data or configuration files as needed
* Exact sequesnce of actions leading to the failure

5. Has this worked before?

This information is important in helping us track down the cause.

Please include:

* Whether this workflow has ever run successfully
* When it last worked
* What changed since then (if anyhting)

iExamples:

* "This job ran successfully last Friday but started failing after I updated my virtual environemnt with X, Y."
* "Tis workflow has never run successfully on Clariden, but worked on Dainti."
* "This issue began after the maintenance last Wednesday."


7. Scope and Impact

Please tell us:

* Does this issue affect one job or all jobs?
* Is the issue reproducible for other users?
* Is there an irgent deadline assocaited with the problem?

## Example of a Good Support Ticekt

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

/caps

Steps to reproduce:

1. uenv start --view=default prgenv-gnu/25.6:v1
2. sbatch mpi_gpu.slurm

This workflow ran fine last month and no changes were made to the application code. The issue started this week.
```

## Before submitting a ticekt

Please check:

* Teh job script for syntax errors
* Avaialble disk quotas using the `quota` command
* Whether scheduled maintenance is in progress
* Whether the issue is already listed on our status page at https://status.cscs.ch.

## Summary

Inclduing degtailed techncial information in your support request significantly reduces turnoround time and helps staff diagnose issues efficiently. In particular, always include:
* Slurm Job IDs
* Output andd error log locations
* Exact steps to reprodyce
* Software environemnt details
* Whether the issue is new or previously working





