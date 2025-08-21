[](){#ref-gssr-quickstart}
# gssr - Quickstart Guide

## Installation

### From Pypi 

`gssr` can be easily installed as follows.:

    pip install gssr

### From GitHub Source

To install directly from the source:

    pip install git+https://github.com/eth-cscs/GPU-saturation-scorer.git

To install from a specific branch, e.g. the development branch, from the source:

    pip install git+https://github.com/eth-cscs/GPU-saturation-scorer.git@dev

To install a specific release tag, e.g. gssr-v0.3, from the source:

    pip install git+https://github.com/eth-cscs/GPU-saturation-scorer.git@gssr-v0.3

## Profile

### Example

If you are submitting a batch job and the command you are executing is:

    srun python test.py

The corresponding srun command should be modified as follows.:

    srun gssr profile -wrap="python abc.py"

* The `gssr` option to run is `profile`
* The `"--wrap"` flag will wrap the command that you would like to run
* The default output directory is `profile_out_{slurm_job_id}`
* A label to the output data can be set with the `-l` flag

## Analyze

### Metric Output
The profiled output can be analysed as follows.:

    gssr analyze -i ./profile_out

### PDF File Output with Plots

    gssr analyze -i ./profile_out --report

A/Multiple PDF report(s) will be generated.

