[](){#ref-hyperqueue}
# HyperQueue
!!! info "GREASY"
    GREASY is not supported at CSCS anymore.
    We recommend using HyperQueue instead.

[HyperQueue](https://it4innovations.github.io/hyperqueue/stable/) is a meta-scheduler designed for high-throughput computing on high-performance computing (HPC) clusters.
It addresses the inefficiency of using traditional schedulers like Slurm for a large number of small, short-lived tasks by allowing you to bundle them into a single, larger Slurm job.
This approach minimizes scheduling overhead and improves resource utilization.

By using a meta-scheduler like HyperQueue, you get fine-grained control over your tasks within the allocated resources of a single batch job.
It's especially useful for workflows that involve numerous tasks, each requiring minimal resources (e.g., a single CPU core or GPU) or a short runtime.

[](){#ref-hyperqueue-setup}
## Setup
Before you can use HyperQueue, you'll need to download it.
No installation is needed as it is a statically linked binary with no external dependencies.
You can download the latest version from the [official site](https://it4innovations.github.io/hyperqueue/stable/installation/).
Because there are different architectures on Alps (ARM and x86_64), we recommend unpacking the binary in `$HOME/.local/<arch>/bin`, as described [here][ref-guides-terminal-arch].

[](){#ref-hyperqueue-example}
## Example workflow
This example demonstrates a basic HyperQueue workflow by running a large number of "hello world" tasks, some on a CPU and others on a GPU.

[](){#ref-hyperqueue-example-script-task}
### The task script
First, create a simple script that represents the individual tasks you want to run.
This script will be executed by HyperQueue workers.

```bash title="task.sh"
#!/usr/local/bin/bash

# This script is a single task that will be run by HyperQueue.
# HQ_TASK_ID is an environment variable set by HyperQueue for each task.
# See HyperQueue documentation for other variables set by HyperQueue

echo "$(date): start task ${HQ_TASK_ID}: $(hostname) CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"

# Simulate some work
sleep 30

echo "$(date): end task ${HQ_TASK_ID}: $(hostname) CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
```

[](){#ref-hyperqueue-example-script-simple}
### Simple Slurm batch job script
Next, create a Slurm batch script that will launch the HyperQueue server and workers, submit your tasks, wait for the tasks to finish, and then shut everything down.

```bash title="job.sh"
#!/usr/local/bin/bash

#SBATCH --nodes 2
#SBATCH --ntasks-per-node 1
#SBATCH --time 00:10:00
#SBATCH --partition normal
#SBATCH --account <account>

# Start HyperQueue server and workers
hq server start &

# Wait for the server to be ready
hq server wait

# Start HyperQueue workers
srun hq worker start &

# Submit tasks (300 CPU tasks and 16 GPU tasks)
hq submit --resource "cpus=1" --array 1-300 ./task.sh;
hq submit --resource "gpus/nvidia=1" --array 1-16 ./task.sh;

# Wait for all jobs to finish
hq job wait all

# Stop HyperQueue server and workers
hq server stop

echo
echo "Everything done!"
```

To submit this job, use `sbatch`:
```bash
$ sbatch job.sh
```

[](){#ref-hyperqueue-example-script-advanced}
### More robust Slurm batch job script
A powerful feature of HyperQueue is the ability to resume a job that was interrupted, for example, by reaching a time limit or a node failure.
You can achieve this by using a journal file to save the state of your tasks.
By adding a journal file, HyperQueue can track which tasks were completed and which are still pending.
When you restart the job, it will only run the unfinished tasks.

Another useful feature is running multiple servers simultaneously.
This can be achieved by starting each server with unique directory set in the variable `HQ_SERVER_DIR`.

Here's an improved version of the batch script that incorporates these features:

```bash title="job.sh"
#!/usr/local/bin/bash

#SBATCH --nodes 2
#SBATCH --ntasks-per-node 1
#SBATCH --time 00:10:00
#SBATCH --partition normal
#SBATCH --account <account>

# Set up the journal file for state tracking
# If an argument is provided, use it to restore a previous job
# Otherwise, create a new journal file for the current job
RESTORE_JOB=$1
if [ -n "$RESTORE_JOB" ]; then
    export JOURNAL=~/.hq-journal-${RESTORE_JOB}
else
    export JOURNAL=~/.hq-journal-${SLURM_JOBID}
fi

# Ensure each Slurm job has its own HyperQueue server directory
export HQ_SERVER_DIR=~/.hq-server-${SLURM_JOBID}

# Start the HyperQueue server with the journal file
hq server start --journal=${JOURNAL} &

# Wait for the server to be ready
hq server wait --timeout=120
if [ "$?" -ne 0 ]; then
    echo "Server did not start, exiting ..."
    exit 1
fi

# Start HyperQueue workers
srun hq worker start &

# Submit tasks only if we are not restoring a previous job
# (300 CPU tasks and 16 GPU tasks)
if [ -z "$RESTORE_JOB" ]; then
    hq submit --resource "cpus=1" --array 1-300 ./task.sh;
    hq submit --resource "gpus/nvidia=1" --array 1-16 ./task.sh;
fi

# Wait for all jobs to finish
hq job wait all

# Stop HyperQueue server and workers
hq server stop

# Clean up server directory and journal file
rm -rf ${HQ_SERVER_DIR}
rm -rf ${JOURNAL}

echo
echo "Everything done!"
```

To submit a new job, use `sbatch`:
```bash
$ sbatch job.sh
```

If the job fails for any reason, you can resubmit it and tell HyperQueue to pick up where it left off by passing the original Slurm job ID as an argument:

```bash
$ sbatch job.sh <job-id>
```

The script will detect the argument, load the journal file from the previous run, and only execute the tasks that haven't been completed.

!!! info "External references"
    You can find other features and examples in the HyperQueue [documentation](https://it4innovations.github.io/hyperqueue/stable/).
