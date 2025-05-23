[](){#ref-jobreport}
# Job report

A batch job summary report is often requested in project proposals at CSCS to demonstrate the effective use of GPUs.
[jobreport](https://github.com/eth-cscs/alps-jobreport/releases) is used in two stages.
The first stage monitors an application and records the GPU usage statistics.
The monitoring stage must be executed within a `slurm` environment.
The information is recorded as `.csv` data within a directory  `jobreport_${SLURM_JOB_ID}` or a directory supplied on the command line.
The second stage prints this information in a tabular form that can be inserted into a project proposal.

## Downloading the job summary report tool

A precompiled binary for the `jobreport` utility can be obtained directly from the [repository](https://github.com/eth-cscs/alps-jobreport/releases) or via the command line:

```console
$ wget https://github.com/eth-cscs/alps-jobreport/releases/download/v0.1/jobreport
$ chmod +x ./jobreport
```
## Command line options

A full list of command line options with explanations can be obtained by running the command with the `--help` option:

```console
$ ./jobreport --help
Usage: jobreport [-v -h] [subcommand] -- COMMAND

Options:
  -h, --help                        Show this help message
  -v, --version                     Show version information

Subcommands:
  monitor                           Monitor the performance metrics for a job. (Default)
    -h, --help                      Shows help message
    -o, --output <path>             Specify output directory (default: ./jobreport_<SLURM_JOB_ID>)
    -u, --sampling_time <seconds>   Set the time between samples (default: automatically determined)
    -t, --max_time <time>           Set the maximum monitoring time (format: DD-HH:MM:SS, default: 24:00:00)
  print                             Print a job report
    -h, --help                      Shows help message
    -o, --output <path>             Output path for the report file
  container-hook                    Write enroot hook for jobreport
    -h, --help                      Shows help message
    -o, --output <path>             Output path for the enroot hook file
                                    (default: $HOME/.config/enroot/hooks.d/cscs_jobreport_dcgm_hook.sh)

Arguments:
  COMMAND                           The command to run as the workload
```

## Reported information

The final output from `jobreport` is a table summarizing the most important details of how your application used the compute resources during its execution.
The report is divided into two parts: a general summary and GPU specific values.

### Job statistics

| Field | Description |
| ----- | ----------- |
| Job Id | The Slurm job id |
| Step Id | The slurm step id. A job step in SLURM is a subdivision of a job started with srun |
| User | The user account that submitted the job |
| SLURM Account | The project account that will be billed |
| Start Time, End Time, Elapsed Time | The time the job started and ended, and how long it ran |
| Number of Nodes | The number of nodes allocated to the job |
| Number of GPUs | The number of GPUs allocated to the job |
| Total Energy Consumed | The total energy consumed based on the average power usage (below) over the elapsed time |
| Average Power Usage | The average power draw over the elapsed time in Watts (W), summed over all GPUs |
| Average SM Utilization | The percentage of the process's lifetime during which Streaming Multiprocessors (SM) were executing a kernel, averaged over all GPUs |
| Average Memory Utilization | The percentage of a process's lifetime during which global (device) memory was being read or written, averaged over all GPUs |

### GPU specific values

| Field | Description |
| ----- | ----------- |
| Host | The compute node executing a job step |
| GPU | The GPU id on a node |
| Elapsed | The elapsed time |
| SM Utilization % | The percentage of the process's lifetime during which Streaming Multiprocessors (SM) were executing a kernel |
| Memory Utilization % | The percentage of process's lifetime during which global (device) memory was being read or written |

## Example with slurm: srun

The simplest example to test `jobreport` is to run it with the sleep command.
It is important to separate `jobreport` (and its options) and your command  with `--`.

```console
$ srun -A my_account -t 5:00 --nodes=1 ./jobreport -- sleep 5
$ ls
jobreport_16133
$ ./jobreport print jobreport_16133
Summary of Job Statistics
+-----------------------------------------+-----------------------------------------+
| Job Id                                  | 16133                                   |
+-----------------------------------------+-----------------------------------------+
| Step Id                                 | 0                                       |
+-----------------------------------------+-----------------------------------------+
| User                                    | jpcoles                                 |
+-----------------------------------------+-----------------------------------------+
| SLURM Account                           | unknown_account                         |
+-----------------------------------------+-----------------------------------------+
| Start Time                              | 03-07-2024 15:32:24                     |
+-----------------------------------------+-----------------------------------------+
| End Time                                | 03-07-2024 15:32:29                     |
+-----------------------------------------+-----------------------------------------+
| Elapsed Time                            | 5s                                      |
+-----------------------------------------+-----------------------------------------+
| Number of Nodes                         | 1                                       |
+-----------------------------------------+-----------------------------------------+
| Number of GPUs                          | 4                                       |
+-----------------------------------------+-----------------------------------------+
| Total Energy Consumed                   | 0.5 Wh                                  |
+-----------------------------------------+-----------------------------------------+
| Average Power Usage                     | 348.8 W                                 |
+-----------------------------------------+-----------------------------------------+
| Average SM Utilization                  | 0%                                      |
+-----------------------------------------+-----------------------------------------+
| Average Memory Utilization              | 0%                                      |
+-----------------------------------------+-----------------------------------------+

GPU Specific Values
+---------------+------+------------------+------------------+----------------------+
| Host          | GPU  | Elapsed          | SM Utilization % | Memory Utilization % |
|               |      |                  | (avg/min/max)    | (avg/min/max)        |
+---------------+------+------------------+------------------+----------------------+
| nid006212     | 0    | 5s               |   0 /   0 /   0  |   0 /   0 /   0      |
| nid006212     | 1    | 5s               |   0 /   0 /   0  |   0 /   0 /   0      |
| nid006212     | 2    | 5s               |   0 /   0 /   0  |   0 /   0 /   0      |
| nid006212     | 3    | 5s               |   0 /   0 /   0  |   0 /   0 /   0      |
+---------------+------+------------------+------------------+----------------------+
```

!!! warning "`jobreport` requires successful completion of the application"

    The `jobreport` tool requires the application to complete successfully.
    If the application crashes or the job is killed by `slurm` prematurely, `jobreport` will not be able to write any output.

!!! warning "Too many GPUs reported by `jobreport`"
    If the job reporting utility reports more GPUs than you expect from the number of nodes requested by SLURM, you may be missing options to set the visible devices correctly for your job.
    See the [GH200 SLURM documentation][ref-slurm-gh200] for examples on how to expose GPUs correctly in your job.
    When oversubscribing ranks to GPUs, the utility will always report too many GPUs.
    The utility does not combine data for the same GPU from different ranks.

!!! warning "workaround known issue on macOS"
    Currently, there is an issue when generating the report file via `jobreport print` on the macOS terminal:
    
    ```console
    what(): locale::facet::_S_create_c_locale name not valid
    /var/spool/slurmd/job32394/slurm_script: line 21: 199992 Aborted         (core dumped) ./jobreport print report
    ```

    To fix this follow these steps:

    1. Open the terminal application
    2. In the top-left corner menu select Terminal -> Settings
    3. Select your default profile
    4. Uncheck "Set locale environment variables on startup"
    5. Quit and reopen the terminal and try again. This should fix the issue.

## Example with slurm: batch script

The `jobreport` command can be used in a batch script
The report printing, too, can be included in the script and does not need the `srun` command.

```bash title="submit script with jobreport"
#!/bin/bash
#SBATCH -t 5:00
#SBATCH --nodes=2

srun ./jobreport -o report -- my_command
./jobreport print report
```


When used within an job script, `jobreport` will work across multiple calls to `srun`.
Each time `srun` is called, `slurm` creates a new job step and `jobreport` records data for each one.
Multiple job steps running simultaneously are also allowed.
The job report generated contains sections for each `slurm` job step.

```bash title="submit script with multiple steps"
#!/bin/bash
#SBATCH -t 5:00
#SBATCH --nodes=2

srun ./jobreport -o report -- my_command_1
srun ./jobreport -o report -- my_command_2

srun --nodes=1 ./jobreport -o report -- my_command_3 &
srun --nodes=1 ./jobreport -o report -- my_command_4 &

wait
```


## Example with uenv

The following example runs a program called `burn` that computes repeated matrix multiplications to stress the GPUs.
It was built with, and requires to run the [prgenv-gnu][ref-uenv-prgenv-gnu].

```console
$ srun --uenv=prgenv-gnu/24.2:v1 -t 5:00 --nodes=1 --ntasks-per-node=4 --gpus-per-task=1 ${JOBREPORT} -o report -- ./burn --gpu=gemm -d 30

$ ./jobreport print report
Summary of Job Statistics
+-----------------------------------------+-----------------------------------------+
| Job Id                                  | 15923                                   |
+-----------------------------------------+-----------------------------------------+
| Step Id                                 | 0                                       |
+-----------------------------------------+-----------------------------------------+
| User                                    | jpcoles                                 |
+-----------------------------------------+-----------------------------------------+
| SLURM Account                           | unknown_account                         |
+-----------------------------------------+-----------------------------------------+
| Start Time                              | 03-07-2024 14:54:48                     |
+-----------------------------------------+-----------------------------------------+
| End Time                                | 03-07-2024 14:55:25                     |
+-----------------------------------------+-----------------------------------------+
| Elapsed Time                            | 36s                                     |
+-----------------------------------------+-----------------------------------------+
| Number of Nodes                         | 1                                       |
+-----------------------------------------+-----------------------------------------+
| Number of GPUs                          | 4                                       |
+-----------------------------------------+-----------------------------------------+
| Total Energy Consumed                   | 18.7 Wh                                 |
+-----------------------------------------+-----------------------------------------+
| Average Power Usage                     | 1.8 kW                                  |
+-----------------------------------------+-----------------------------------------+
| Average SM Utilization                  | 88%                                     |
+-----------------------------------------+-----------------------------------------+
| Average Memory Utilization              | 43%                                     |
+-----------------------------------------+-----------------------------------------+

GPU Specific Values
+---------------+------+------------------+------------------+----------------------+
| Host          | GPU  | Elapsed          | SM Utilization % | Memory Utilization % |
|               |      |                  | (avg/min/max)    | (avg/min/max)        |
+---------------+------+------------------+------------------+----------------------+
| nid007044     | 0    | 36s              |  83 /   0 / 100  |  39 /   0 /  50      |
| nid007044     | 0    | 36s              |  90 /   0 / 100  |  43 /   0 /  50      |
| nid007044     | 0    | 36s              |  90 /   0 / 100  |  43 /   0 /  48      |
| nid007044     | 0    | 36s              |  90 /   0 / 100  |  47 /   0 /  54      |
+---------------+------+------------------+------------------+----------------------+
```

!!! note "Using `jobreport` with other uenvs"

    `jobreport` works with any uenv, not just `prgenv-gnu`.

## Example with container-engine (CE)

Running `jobreport` with the [container-engine (CE)][ref-container-engine] requires a little more setup to allow the CE to mount the required GPU library paths inside the container.

A script to set up the mount points needs to be placed in `${HOME}/.config/enroot/hooks.d/`.
This can be generated with the `jobreport` tool, and by default, the script will be placed in `${HOME}/.config/enroot/hooks.d/cscs_jobreport.sh`.

```console title="Generate DCGM hook"
$ ./jobreport container-hook
Writing enroot hook to "/users/myuser/.config/enroot/hooks.d/cscs_jobreport_dcgm_hook.sh"
Add the following to your container .toml file:

[annotations]
com.hooks.dcgm.enabled = "true"
```

As indicated by the output, the hook must be added to the container `.toml` file.

```toml title="Example .toml file"
[annotations]
com.hooks.dcgm.enabled = "true"
```

Once the CE is configured, only the EDF file (here `my-edf.toml`) needs to be specified along with a call to `jobreport`:

```console title="Run jobreport in a container"
$ srun --environment=my-edf.toml ./jobreport -- sleep 5
```

!!! note "Using `jobreport` with other container images"

    `jobreport` works with any container image, as long as the hook is set up and the EDF file has the correct annotation.
