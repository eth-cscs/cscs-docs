# GPU Saturation Scorer Report

## Overview

GSSR records how your GPUs are used during a job and generates a PDF report suitable for project proposals.

You run your application once with GSSR enabled, then generate the report.
The PDF helps reviewers better understand the GPU usage of your application.

## Downloading GSSR

Clone the GSSR repository onto a GH200 Alps login node and build

```bash
git clone https://github.com/jpcoles-cscs/gssr.git
cd gssr
make
```

Include the git repository in your `PATH` (put this in `$HOME/.bashrc` too)
```bash
export PATH=<path-to-gssr>:$PATH
```

Optionally install `uv` if you don't already have it installed
```bash
make install-uv
```

## The two-command workflow

Using GSSR always follows the same two steps:

1. Run your job while recording GPU metrics  
2. Generate the PDF report

## Quick start -- fastest path to a PDF

This example uses a dummy job so you can verify everything works in under one minute.

### Step 1 -- record a run

Run any command using `gssr-record`:

```bash
gssr-record -o gr-test sleep 30
```

What happens:

- Your command runs normally (e.g., `sleep 30`) 
- GPU metrics are recorded in the directory `gr-test/`

### Step 2 -- generate the report

```bash
gssr-analyze.py gr-test -o gssr-report.pdf
```

You now have a GPU utilization report.  
Open the PDF to verify it was created successfully.

## Real usage with your application

Replace the test command with your real workload. Example:

```bash
srun gssr-record -o gr-training python train.py
```

After the job finishes:

```bash
gssr-analyze.py gr-training -o gpu-report.pdf
```

Upload the generated PDF with your project proposal.

## Slurm job script example

```bash
#!/bin/bash
#SBATCH --job-name=gssr-test
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --time=00:30:00

srun gssr-record -o gr-run python train.py
```

After the job completes:

```bash
gssr-analyze.py gr-run -o gpu-report.pdf
```

## Using GSSR inside containers

GSSR uses the NVIDIA DCGM library to read GPU metrics. This is available on the Alps host system.

When running inside a container, you must enable the DCGM hook in your EDF file:

```ini
[annotations]
com.hooks.dcgm.enabled = "true"
```

Without this setting, GPU metrics cannot be collected.

!!! warning
    The output directory should be under a path that has been bind-mounted in the
    `.toml` file.  If the output directory is inside the container, the data will
    be lost when the container ends. GSSR attempts to detect this scenario and warn
    the user.

## Important behaviour to know

### Only one task per node records metrics

You do not need to modify your MPI job.  
GSSR automatically records metrics for all GPUs on the node.

### Overlapping jobs share GPU data

If multiple jobs run on the same GPUs at the same time, they will record the same GPU metrics.  
This behaviour is normal.

## Choosing the right run for your proposal

Your profiling run should demonstrate how a typical simulations from your proposal performs.

A good profiling run:

- Captures GPU usage for a few minutes after any initial data loading and setup.
- Represents real training or simulation behaviour.
- Shows steady GPU usage.

## Output files

After recording, the output directory contains raw GPU metrics, e.g.:

```
gr-training/
```

Most users do not need to inspect these files directly.  
They are used to generate the report.

## Troubleshooting

### The report is empty

Your job likely did not see GPUs.  
Verify that GPUs are visible inside your job or container.

### I forgot to run gssr-record

You must rerun the job.  
GPU metrics cannot be recreated after a job finishes.

### The run was very short

Runs shorter than approximately one minute may not produce useful plots.

## Command reference

### gssr-record

Run a command while recording GPU metrics.

```bash
gssr-record -o <directory> <command>
```

Options:

```
-o <directory>   Output directory for recorded metrics
-h, --help       Show help
--version        Show version
```

### gssr-analyze.py

Generate a PDF report from recorded metrics.

```bash
gssr-analyze.py <directory> -o <pdf>
```

Options:

```
-o <file>    Output PDF (default: gssr-report.pdf)
```

## Support

If you encounter problems, contact support and include:

- Job script  
- GSSR output directory  
- Error messages

