[](){#ref-mlp-llm-nanotron-tutorial}

# LLM Nanotron Training Tutorial

In this tutorial, we will build a container image to run nanotron training jobs. We will train a 109M parameter model with ~100M wikitext tokens as a proof of concept.

### Prequisites 

It is also recommended to follow the previous tutorials: [LLM Inference][ref-mlp-llm-inference-tutorial] and [LLM Finetuning][ref-mlp-llm-finetuning-tutorial], as this will build up from it.

### Set up Podman

Edit your `$HOME/.config/containers/storage.conf` according to the following minimal template:

```title="$HOME/.config/containers/storage.conf"
[storage]
  driver = "overlay"
  runroot = "/dev/shm/$USER/runroot"
  graphroot = "/dev/shm/$USER/root"

[storage.options.overlay]
  mount_program = "/usr/bin/fuse-overlayfs-1.13"
```

## Modify the NGC Container

See previous tutorial for context. Here, we assume we are already in a compute node (run `srun -A <ACCOUNT> --pty bash` to get an interactive session). In this case, we will be creating the dockerfile in `$SCRATCH/container-image/nanotron/Dockerfile`. These are the contents of the dockerfile:

```title="$SCRATCH/container-image/nanotron/Dockerfile"
FROM nvcr.io/nvidia/pytorch:24.04-py3

# Update flash-attn.
RUN pip install --upgrade --no-build-isolation flash-attn==2.5.8

# Install the rest of dependencies.
RUN pip install \
	datasets \
	transformers \
	wandb \
	dacite \
	pyyaml \
	numpy \
	packaging \
	safetensors \
	tqdm
```

Then build and import the container.

```bash
cd $SCRATCH/container-image/nanotron
podman build -t nanotron:v1.0 .
enroot import -x mount -o nanotron-v1.0.sqsh podman://nanotron:v1.0
```

Now exit the interactive session by running `exit`.

### Set up an EDF

See the previous tutorial for context. In this case, the edf will be at `$HOME/.edf/nanotron.toml` and will have the following contents:

```title="$HOME/.edf/nanotron.toml"
image = "/capstor/scratch/cscs/<USER>/container-image/nanotron/nanotron-v1.0.sqsh"
mounts = ["/capstor", "/users"]
workdir = "/users/<username>/" 
writable = true
 
[annotations]
com.hooks.aws_ofi_nccl.enabled = "true"
com.hooks.aws_ofi_nccl.variant = "cuda12"
 
[env]
FI_CXI_DISABLE_HOST_REGISTER = "1"
FI_MR_CACHE_MONITOR = "userfaultfd"
NCCL_DEBUG = "INFO"
```

Note that, if you built your own container image, you will need to modify the image path.

### Preparing a Training Job

Now let's download nanotron. In the login node run:

```bash
git clone https://github.com/huggingface/nanotron.git
cd nanotron
```

And with your favorite text editor, create the following nanotron configuration file in `$HOME/nanotron/examples/config_tiny_llama_wikitext.yaml`:

```title="$HOME/nanotron/examples/config_tiny_llama_wikitext.yaml"
general:
  benchmark_csv_path: null
  consumed_train_samples: null
  ignore_sanity_checks: true
  project: debug
  run: tiny_llama_%date_%jobid
  seed: 42
  step: null
model:
  ddp_bucket_cap_mb: 25
  dtype: bfloat16
  init_method:
    std: 0.025
  make_vocab_size_divisible_by: 1
  model_config:
    bos_token_id: 1
    eos_token_id: 2
    hidden_act: silu
    hidden_size: 768
    initializer_range: 0.02
    intermediate_size: 1536
    is_llama_config: true
    max_position_embeddings: 512
    num_attention_heads: 12
    num_hidden_layers: 12
    num_key_value_heads: 12
    pad_token_id: null
    pretraining_tp: 1
    rms_norm_eps: 1.0e-05
    rope_scaling: null
    tie_word_embeddings: true
    use_cache: true
    vocab_size: 50257
optimizer:
  accumulate_grad_in_fp32: true
  clip_grad: 1.0
  learning_rate_scheduler:
    learning_rate: 0.001
    lr_decay_starting_step: null
    lr_decay_steps: null
    lr_decay_style: cosine
    lr_warmup_steps: 150 # 10% of the total steps
    lr_warmup_style: linear
    min_decay_lr: 0.00001
  optimizer_factory:
    adam_beta1: 0.9
    adam_beta2: 0.95
    adam_eps: 1.0e-08
    name: adamW
    torch_adam_is_fused: true
  weight_decay: 0.01
  zero_stage: 1
parallelism:
  dp: 2
  expert_parallel_size: 1
  pp: 1
  pp_engine: 1f1b
  tp: 4
  tp_linear_async_communication: true
  tp_mode: reduce_scatter
data_stages:
  - name: stable training stage
    start_training_step: 1
    data:
      dataset:
        dataset_overwrite_cache: false
        dataset_processing_num_proc_per_process: 32
        hf_dataset_config_name: null
        hf_dataset_or_datasets: wikitext
        hf_dataset_splits: train
        text_column_name: text
        hf_dataset_config_name: wikitext-103-v1
      num_loading_workers: 1
      seed: 42
lighteval: null
tokenizer:
  tokenizer_max_length: null
  tokenizer_name_or_path: gpt2
  tokenizer_revision: null
tokens:
  batch_accumulation_per_replica: 1
  limit_test_batches: 0
  limit_val_batches: 0
  micro_batch_size: 64
  sequence_length: 512
  train_steps: 1500
  val_check_interval: -1
checkpoints:
  checkpoint_interval: 1500
  checkpoints_path: checkpoints
  checkpoints_path_is_shared_file_system: false
  resume_checkpoint_path: checkpoints
  save_initial_state: false
profiler: null
logging:
  iteration_step_info_interval: 1
  log_level: info
  log_level_replica: info
```

This configuration file will train, as a proof of concept, a gpt-2-like (109M parameters) llama model with approximately 100M tokens of wikitext with settings `tp=4, dp=2, pp=1` (which means that it requires two nodes to train). This training job will require approximately 10 minutes to run. Now, create a batchfile in `$HOME/nanotron/run_tiny_llama.sh` with the contents:

```bash title="$HOME/nanotron/run_tiny_llama.sh"
#!/bin/bash
#SBATCH --job-name=nanotron      # create a short name for your job
#SBATCH --nodes=2                # total number of nodes
#SBATCH --ntasks-per-node=1      # total number of tasks per node
#SBATCH --gpus-per-task=4
#SBATCH --time=1:00:00
#SBATCH --account=<ACCOUNT>
#SBATCH --output=logs/%x_%j.log  # control where the stdout will be
#SBATCH --error=logs/%x_%j.err   # control where the error messages will be#

mkdir -p logs

# Initialization.
set -x
cat $0
export MASTER_PORT=25678
export MASTER_ADDR=$(hostname)
export HF_HOME=$SCRATCH/huggingface_home
export CUDA_DEVICE_MAX_CONNECTIONS=1         # required by nanotron
# export either WANDB_API_KEY=<api key> or WANDB_MODE=offline

# Run main script.
srun -ul --environment=nanotron bash -c "
  # Change cwd and run the main training script.
  cd nanotron/
  pip install -e .   # Only required the first time.

  TORCHRUN_ARGS=\"
   --node-rank=\${SLURM_PROCID} \
   --master-addr=\${MASTER_ADDR} \
   --master-port=\${MASTER_PORT} \
   --nnodes=\${SLURM_NNODES} \
   --nproc-per-node=\${SLURM_GPUS_PER_TASK} \
  \"

  torchrun \${TORCHRUN_ARGS} run_train.py --config-file examples/config_tiny_llama_wikitext.yaml
"
```

A few comments:
- The parts outside the srun command will be run on the first node of the Slurm allocation for this job. srun commands without further specifiers execute with the settings of the sbatch script (i.e. using all nodes allocated to the job). 
- If you have a [wandb](https://wandb.ai/) API key and want to synchronize the training run, be sure to set the `WANDB_API_KEY` variable. Otherwise, set `WANDB_MODE=of​f​line` instead.
- Note that we are setting `HF_HOME` in a directory in scratch. This is done to place the downloaded dataset in scratch, instead of your home directory.
- The pip install command is only run once in every container (compute node). Note that this will only link the nanotron python package to be able to import it in any script irrespective of the current working directory. Because all dependencies of nanotron are already installed in the Dockerfile, no extra libraries will be installed at this point. If the installation of the package under development creates artefacts on the shared filesystem (such as binaries from compiled C++/CUDA source code), this results in a race condition when run from multiple nodes. Therefore, in this case and also when additional external libraries are to be installed, you should either use venv as shown in previous tutorials, or directly build everything in the Dockerfile.

### Launch a Training Job with the new Image

Run:

```bash
sbatch run_tiny_llama.sh
```

You can inspect if your job has been submitted successfully by running `squeue --me` and looking for your username. Once the run starts, there will be a new file under `logs/`. You can inspect the status of your run using:

```
tail -f logs/<logfile>
```

In the end, the checkpoints of the model will be saved in `checkpoints/`.