# Vetnode

Vetnode validates your job's allocated nodes at runtime. You can check allocated nodes against a predefined set of performance and configuration evaluations to ensure your environment is properly set up and your allocation does not contain "bad" nodes.


!!! note "Experimental"

    This is an experimental tool currently being developed primerely for the ML community.

---

## Quick Start

The simplest way to run Vetnode is to include the following `srun` snippet at the beginning of your `sbatch` script. Set the `ENV_FILE` environment variable to the path of your EDF TOML file.

```bash
srun -N ${SLURM_JOB_NUM_NODES} --tasks-per-node=4 --environment=${ENV_FILE} \
     --network=disable_rdzv_get --container-writable bash -c '

    if [ "${SLURM_LOCALID}" = "0" ]; then
        mkdir -p /tmp/vetnode-$(hostname)-${SLURM_JOB_ID}
        cd /tmp/vetnode-$(hostname)-${SLURM_JOB_ID}
        wget -q -O config.yaml https://raw.githubusercontent.com/eth-cscs/vetnode/refs/heads/main/examples/alps-ml-vetting/config.yaml
        python -m venv --system-site-packages .venv
        source .venv/bin/activate
        pip install -q --no-cache-dir --index-url "https://jfrog.svc.cscs.ch/artifactory/api/pypi/pypi-remote/simple" vetnode
        touch /tmp/vetnode-$(hostname)-${SLURM_JOB_ID}/.setup_done
    else
        while [ ! -f /tmp/vetnode-$(hostname)-${SLURM_JOB_ID}/.setup_done ]; do
            sleep 2
        done
        cd /tmp/vetnode-$(hostname)-${SLURM_JOB_ID}
        source .venv/bin/activate
    fi

    vetnode diagnose config.yaml

    if [ "${SLURM_LOCALID}" = "0" ]; then
        sleep 5
        rm -rf /tmp/vetnode-$(hostname)-${SLURM_JOB_ID}
    fi
'
```

This snippet installs Vetnode on the fly on each allocated node and runs a series of predefined evaluations specifically designed to test Alps for ML workloads.

---

## Installation

Vetnode is distributed as a Python package and can be installed via pip:

```bash
pip install vetnode
```

---

## CLI Reference

Vetnode is a CLI designed to run in distributed HPC environments. It has two main commands: `diagnose` and `setup`. Both commands require a configuration file listing all evaluations to be performed.

### `diagnose`

Sequentially executes all evaluations listed in the config file and produces a summary of the results and node state.

By default, `diagnose` also installs any required dependencies before running. You can skip this step with the `--skip-install` flag if you have already set up the environment via the `setup` command.

```bash
vetnode diagnose config.yaml
vetnode diagnose config.yaml --skip-install   # skip dependency installation
vetnode diagnose config.yaml --verbose        # include all output metrics
```

| Flag | Description |
|------|-------------|
| `--skip-install` | Skip dependency installation (use if `setup` was already run) |
| `--verbose` | Print all output metrics produced by each evaluation |
| `--help` | Print help |

### `setup`

Installs all requirements needed to execute the evaluations listed in the configuration file. This step is usually not necessary since `diagnose` performs it automatically.

```bash
vetnode setup config.yaml
```

---

## Configuration

The evaluations configuration file is a YAML file that lists all evaluations to be performed and provides context information for Vetnode to properly distribute the workload.

```yaml
name: Image Vetting
scheduler: slurm
pip:
  index_url: "https://jfrog.svc.cscs.ch/artifactory/api/pypi/pypi-remote/simple"
evals:
  - name: Environment Variables
    type: vetnode.evaluations.env_var_eval.EnvVarEval
    expected: # (1)!
      CUDA_CACHE_DISABLE: "1"
      NCCL_NET: "AWS Libfabric"
      NCCL_CROSS_NIC: "1"
      NCCL_NET_GDR_LEVEL: "PHB"
      NCCL_PROTO: "^LL128"
      FI_PROVIDER: "cxi"
      FI_CXI_DEFAULT_CQ_SIZE: "131072"
      FI_CXI_DEFAULT_TX_SIZE: "16384"
      FI_CXI_DISABLE_HOST_REGISTER: "1"
      FI_CXI_RDZV_PROTO: "alt_read"
      FI_CXI_RDZV_EAGER_SIZE: "0"
      FI_CXI_RDZV_GET_MIN: "0"
      FI_CXI_RDZV_THRESHOLD: "0"
      FI_CXI_RX_MATCH_MODE: "hybrid"
      FI_MR_CACHE_MONITOR: "userfaultfd"

  - name: Check GPU
    type: vetnode.evaluations.gpu_eval.GPUEval
    max_temp: 30  # (2)!
    max_used_memory: 0.2   # (3)!

  - name: CudaKernel
    type: vetnode.evaluations.cuda_eval.CUDAEval
    cuda_home: /usr/local/cuda   # (4)!
    requirements:
      - cuda-python==13.*
      - numpy
```

1. A dictionary of required environment variables and their expected values.
The evaluation fails if any variable is missing or does not match the specified value.

2. The maximum allowed GPU temperature (in degrees Celsius) when the system is idle.
If the measured temperature exceeds this threshold, the evaluation fails.

3. The maximum allowed fraction of GPU memory in use when the system is idle.
The value is expressed as a ratio (e.g., 0.2 corresponds to 20% of total GPU memory).
The evaluation fails if memory usage exceeds this limit.

4. The filesystem path to the CUDA installation directory.
This path is used to locate CUDA libraries and binaries required for the CUDA kernel validation.

The example above configures three evaluations. For the full list of available evaluation types, see the [evaluations folder](https://github.com/eth-cscs/vetnode/tree/main/src/vetnode/evaluations) in the Vetnode GitHub repository.

### Top-level fields

| Field | Description |
|-------|-------------|
| `name` | Human-readable name for this vetting configuration |
| `scheduler` | Job scheduler in use (e.g. `slurm`, `standalone`) |
| `pip.index_url` | PyPI index URL used to install evaluation dependencies |
| `evals` | List of evaluation definitions |

### Evaluation fields

Each entry in `evals` must have a `name` and a `type`. Additional fields depend on the specific evaluation type.

| Field | Description |
|-------|-------------|
| `name` | Human-readable label for the evaluation |
| `type` | Fully qualified Python class name for the evaluation |
| *(type-specific)* | Additional parameters vary by evaluation type |