[](){#software-ml-llm-nanotron-tutorial}

# LLM Nanotron Pre-training Tutorial

In this tutorial, we will build a container image to run multi-node training jobs with [nanotron](https://github.com/huggingface/nanotron).
We will train a 109M parameter model with ~100M wikitext tokens as a proof of concept.

!!! info
    Note that while the concepts taught here for multi-node training with PyTorch are generally portable across frameworks, the current (August 2025) recommendation for users with a need for large-scale model-parallel training is to use `Megatron-LM` instead of `nanotron` due to significant performance advantages at scale. 

### Prerequisites 

It is recommended to follow the previous two tutorials on [LLM Inference][software-ml-llm-inference-tutorial] and [LLM Fine-tuning][software-ml-llm-fine-tuning-tutorial] first, as this will build upon them.

### Set up Podman

If not already done as part of the [LLM Inference tutorial][software-ml-llm-inference-tutorial], edit your podman configuration in `$HOME/.config/containers/storage.conf` as follows:

```toml title="$HOME/.config/containers/storage.conf"
[storage]
  driver = "overlay"
  runroot = "/dev/shm/$USER/runroot"
  graphroot = "/dev/shm/$USER/root"

[storage.options.overlay]
  mount_program = "/usr/bin/fuse-overlayfs-1.13"
```

Create a directory to store container images used with CE and configure it with [recommended LUSTRE settings][ref-guides-storage-lustre]:

```console title="Container image directory with recommended LUSTRE settings"
[clariden-lnXXX]$ mkdir -p $SCRATCH/ce-images
[clariden-lnXXX]$ lfs setstripe -E 4M -c 1 -E 64M -c 4 -E -1 -c -1 -S 4M $SCRATCH/ce-images # (1)!
```

1. This makes sure that files stored subsequently end up on the same storage node (up to 4 MB), on 4 storage nodes (between 4 and 64 MB) or are striped across all storage nodes (above 64 MB)

## Build a modified NGC Container

In this tutorial, we build a virtual environment on top of a customized NGC container image. This represents a typical task during development, where stable dependencies are captured in a static container image, whereas frequently changing packages are installed in a virtual environment on top. In contrast to the previous tutorials, the container in this case will be mostly self-contained.

Here, we assume we are already in a compute node (run `srun -A <ACCOUNT> --pty bash` to get an interactive session).
In this case, we create a Dockerfile with the following contents:

```dockerfile title="$SCRATCH/tutorials/nanotron-pretrain/Dockerfile"
FROM nvcr.io/nvidia/pytorch:24.04-py3

RUN apt-get update && \
    apt-get install -y python3.10-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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

!!! note "More recent NGC releases"
    As discussed in the [LLM Inference tutorial][software-ml-llm-inference-tutorial], starting with the 24.11 release, NGC PyTorch no longer requires the installation of the Python venv module. Furthermore, FlashAttention and several other packages were integrated into the hosted image. However, as `nanotron` as of June 2025 still requires Python 3.10 (cf. this [issue](https://github.com/huggingface/nanotron/issues/217)), this example is restricted to NGC releases up to `24.10`.

    ```dockerfile title="$SCRATCH/tutorials/nanotron-pretrain/Dockerfile"
    FROM nvcr.io/nvidia/pytorch:24.10-py3

    RUN apt-get update && \
        apt-get install -y python3.10-venv && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

    # Update flash-attn.
    RUN pip install --upgrade --no-build-isolation flash-attn==2.5.8

    # Install the rest of dependencies.
    RUN pip install \
        datasets \
        transformers \
        wandb \
        dacite \
        pyyaml
    ```

    The remaining steps can then be performed equivalently, replacing the version number `24.04` by the one chosen in the Dockerfile (e.g. `24.10`).
    
    It is generally recommended to stick to one of the most recent versions of NGC, unless there is a strong reason from your application to stick to an old version for compatibility.

Then build and import the container.

```console
[nidYYYYYY]$ cd $SCRATCH/tutorials/nanotron-pretrain
[nidYYYYYY]$ podman build -f Dockerfile -t ngc-nanotron:24.04 .
[nidYYYYYY]$ enroot import -x mount \
  -o $SCRATCH/ce-images/ngc-nanotron+24.04.sqsh podman://ngc-nanotron:24.04  # (1)!
```

1. We import container images into a canonical location under $SCRATCH.


!!! info "Debugging the container build"
    If the container build fails, you can run an interactive shell using the image from the last successfully built layer with

    ```bash
    podman run -it --rm -e NVIDIA_VISIBLE_DEVICES=void <last-layer-hash> bash # (1)!
    ```

    1. Setting `NVIDIA_VISIBLE_DEVICES` in the environment is required specifically to run NGC containers with podman

    replacing `<last-layer-hash>` by the actual hash output in the build job and interactively test the failing command.  

Now exit the interactive session by running `exit`.

### Set up an environment description file (EDF)

See the previous tutorial for context. In this case, the EDF will be co-located with the Dockerfile under `$SCRATCH/tutorials/nanotron-pretrain` and will have the following contents:

```toml title="$SCRATCH/tutorials/nanotron-pretrain/ngc-nanotron-24.04.toml"
image = "${SCRATCH}/ce-images/ngc-nanotron+24.04.sqsh" # (1)!

mounts = [
    "/capstor",
    "/iopsstor"
] # (2)!

workdir = "${SCRATCH}/tutorials/nanotron-pretrain/" # (3)!

[annotations]
com.hooks.aws_ofi_nccl.enabled = "true" # (4)!
com.hooks.aws_ofi_nccl.variant = "cuda12"

[env]
NCCL_DEBUG = "INFO" # (5)!
CUDA_CACHE_DISABLE = "1" # (6)!
TORCH_NCCL_ASYNC_ERROR_HANDLING = "1" # (7)!
MPICH_GPU_SUPPORT_ENABLED = "0" # (8)!
```

1. It is important to use curly braces for environment variables used in the EDF
2. The path `/users` is not mounted since it often contains user-specific initialization scripts for the host environment and many frameworks leave temporary data behind that can lead to non-trivial runtime errors when swapping container images. Thus, it is recommended to selectively mount specific subfolders under `${HOME}` if needed.
3. You can use `${PWD}` as an alternative to use the path submitted from when the container is started
4. This enables NCCL installed in the container to make effective use of the Slingshot interconnect on Alps by interfacing with the [AWS OFI NCCL plugin][ref-ce-aws-ofi-hook] with libfabric. While not strictly needed for single node workloads, it is good practice to keep it always on.
5. This makes NCCL output debug info during initialization, which can be useful to spot communication-related issues in a distributed scenario (see later tutorials). Subsystems with debug log can be configured with `NCCL_DEBUG_SUBSYS`.
6. Disable CUDA JIT cache
7. Async error handling when an exception is observed in NCCL watchdog: aborting NCCL communicator and tearing down process upon error
8. Disable GPU support in MPICH, as it can lead to deadlocks when using together with NCCL

Note that, if you built your container image elsewhere, you will need to modify the image path.

## Installing nanotron in a virtual environment

Now let's download nanotron.
In the login node run:

```console
[clariden-lnXXX]$ cd $SCRATCH/tutorials/nanotron-pretrain
[clariden-lnXXX]$ git clone https://github.com/huggingface/nanotron.git
[clariden-lnXXX]$ cd nanotron
[clariden-lnXXX]$ git checkout 5f8a52b08b702e206f31f2660e4b6f22ac328c95  # (1)!
```

1. This ensures the compatibility of nanotron with the following example. For general usage, there is no reason to stick to an outdated version of nanotron, though.

We will install nanotron in a thin virtual environment on top of the container image built above. This proceeds as in the [LLM Inference][software-ml-llm-inference-tutorial].

```console
[clariden-lnXXX]$ srun  -A <ACCOUNT> --environment=./ngc-nanotron-24.04.toml --pty bash
user@nidYYYYYY$ python -m venv --system-site-packages venv-24.04
user@nidYYYYYY$ source venv-24.04/bin/activate
(venv-24.04) user@nidYYYYYY$ cd nanotron/ && pip install -e .
```

This creates a virtual environment on top of this container image (`--system-site-packages` ensuring access to system-installed site-packages) and installs nanotron in editable mode inside it. Because all dependencies of nanotron are already installed in the Dockerfile, no extra libraries will be installed at this point.

!!! note
    Jobs making use of this virtual environment will always need to activate it first (_inside_ the `srun` command). 


## Preparing a Training Job

Now, with your favorite text editor, create the following nanotron configuration file:

```yaml title="$SCRATCH/tutorials/nanotron-pretrain/nanotron/examples/config_tiny_llama_wikitext.yaml"
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

This configuration file will train, as a proof of concept, a GPT-2-like (109M parameters) Llama model with approximately 100M tokens of wikitext with 4-way tensor parallelism (`tp`), 2-way data-parallelism (`dp`) and no pipeline-parallelism (`pp`). As a consequence, two GH200 nodes are required to train the model.
The training job will require approximately 10 minutes to run.

Now, create a submission script in `$SCRATCH/tutorials/nanotron-pretrain/nanotron/run_tiny_llama.sh` with the following content:

```bash title="$SCRATCH/tutorials/nanotron-pretrain/run_tiny_llama.sh"
#!/bin/bash
#SBATCH --account=<ACCOUNT>
#SBATCH --job-name=pretrain-nanotron      # create a short name for your job
#SBATCH --time=00:45:00
#SBATCH --nodes=2                # total number of nodes
#SBATCH --ntasks-per-node=1      # total number of tasks per node
#SBATCH --gpus-per-task=4
#SBATCH --output=logs/slurm-%x-%j.log  # if #SBATCH --error=... is not specified,
                                 # this will also contain stderr (error messages)

# Initialization.
set -x
cat $0
export HF_HOME=$SCRATCH/huggingface # (1)!
export CUDA_DEVICE_MAX_CONNECTIONS=1 #(2)!

export WANDB_API_KEY=<api key> # alternatively: export WANDB_MODE=offline

# Run main script.
srun -ul --environment=./ngc-nanotron-24.04.toml bash -c "
  # activate virtual environment
  source venv-24.04/bin/activate

  # change cwd and run the training script
  cd nanotron/

  TORCHRUN_ARGS=\"
   --master-addr=\$(scontrol show hostnames \$SLURM_JOB_NODELIST | head -n 1) \
   --master-port=29500 \
   --node-rank=\${SLURM_PROCID} \
   --nnodes=\${SLURM_NNODES} \
   --nproc-per-node=\${SLURM_GPUS_ON_NODE} \
  \"

  python -m torch.distributed.run \${TORCHRUN_ARGS} \
    run_train.py --config-file examples/config_tiny_llama_wikitext.yaml
" # (3)!
```

1. Location for locally stored data (incl. token and cache for models/datasets/spaces if `HF_HUB_CACHE` is not set) from `huggingface_hub` (cf. [HuggingFace docs](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables#hfhome).
2. This setting is specifically required by nanotron. Note that this setting can lead to faulty Nsight Systems (`nsys`) profiles that do not show overlap of compute and communication when there actually is (e.g. observed in [this issue](https://github.com/NVIDIA/Megatron-LM/issues/1468)). The solution is to use a more recent version of `nsys`.
3. Use `python -m torch.distributed.run` instead of `torchrun` with virtual environments.

!!! note "A few comments"
    - The parts outside the srun command will be run on the first node of the Slurm allocation for this job. srun commands without further specifiers execute with the settings of the sbatch script (i.e. using all nodes allocated to the job). 
    - Note that we are setting `HF_HOME` to a directory in scratch. This is done to place the dataset downloaded from `huggingface_hub` in your scratch, instead of your home directory. The same applies to your HuggingFace token as well as any models/spaces unless `HF_HUB_CACHE` is set (cf. [HuggingFace docs](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables#hfhome)). As discussed in the tutorial on [LLM Inference][software-ml-llm-inference-tutorial], it is good practice to apply the [recommended LUSTRE settings][ref-guides-storage-lustre] there.
    - If instead of downloading a dataset from HuggingFace you want to re-use one managed by a colleague, please refer to the [storage guide][ref-guides-storage-sharing] for instructions on dataset sharing.
    - If you have a [wandb API key](https://docs.wandb.ai/guides/track/environment-variables/) and want to synchronize the training run, be sure to set the `WANDB_API_KEY` variable. Alternatively, `wandb` can write log data to the distributed filesystem with `WANDB_MODE=of​f​line` so that it can be uploaded with `wandb sync` (cf. [Weights & Biases docs](https://docs.wandb.ai/support/run_wandb_offline/)) after the training run has finished.

!!! warning "`torchrun` with virtual environments"
    When using a virtual environment on top of a base image with PyTorch, always replace `torchrun` with `python -m torch.distributed.run` to pick up the correct Python environment. Otherwise, the system Python environment will be used and virtual environment packages not available. If not using virtual environments such as with a self-contained PyTorch container, `torchrun` is equivalent to `python -m torch.distributed.run`.

!!! note "Using srun instead of `torchrun`"
    In many cases, workloads launched with `torchrun` can equivalently be launched purely with SLURM by setting some extra environment variables for `torch.distributed`. This simplifies the overall setup. That is, the `srun` statement in the above `sbatch` script can be rewritten as

    ```bash title="$SCRATCH/tutorials/nanotron-pretrain/run_tiny_llama.sh"
    #!/bin/bash
    #SBATCH --account=<ACCOUNT>
    #SBATCH --job-name=pretrain-nanotron      # create a short name for your job
    #SBATCH --time=00:45:00
    #SBATCH --nodes=2                # total number of nodes
    #SBATCH --ntasks-per-node=4      # total number of tasks per node
    #SBATCH --output=logs/slurm-%x-%j.log  # if #SBATCH --error=... is not specified,
                                    # this will also contain stderr (error messages)

    # Initialization.
    set -x
    cat $0
    export HF_HOME=$SCRATCH/huggingface
    export CUDA_DEVICE_MAX_CONNECTIONS=1

    export WANDB_API_KEY=<api key> # alternatively: export WANDB_MODE=offline

    # Run main script.
    srun -ul --environment=./ngc-nanotron-24.04.toml bash -c "
      # activate virtual environment
      source venv-24.04/bin/activate

      # change cwd and run the training script
      cd nanotron/

      MASTER_ADDR=\$(scontrol show hostnames \$SLURM_JOB_NODELIST | head -n 1) \
      MASTER_PORT=29500 \
      RANK=\${SLURM_PROCID} \
      LOCAL_RANK=\${SLURM_LOCALID} \
      WORLD_SIZE=\${SLURM_NTASKS} \
      python run_train.py --config-file examples/config_tiny_llama_wikitext.yaml
    "
    ```

    Note that, the quoted block inside the `srun` command gets executed by each task separately, i.e. 4 times per node, but all tasks on a node share the _same_ container. This is different to the setup with `torchrun` where only one task executes the lines above the final `python` command. This is important to be aware of in order to avoid any accidental race condition (e.g. by writing to the container filesystem in one of these lines).


## Launch a Training Job

Run:

```console
[clariden-lnXXX]$ sbatch run_tiny_llama.sh
```

You can inspect if your job has been submitted successfully by running `squeue --me` and looking for your username. Once the run starts, there will be a new file under `logs/`. You can inspect the status of your run using:

```console
[clariden-lnXXX]$ tail -f logs/<logfile>
```

In the end, the checkpoints of the model will be saved in `checkpoints/`.

!!! note "Core dump files"
    In case the application crashes, it may leave behind large core dump files that contain an image of the process memory at the time of the crash. While these can be useful for debugging the reason of a specific crash (by e.g. loading them with `cuda-gdb` and looking at the stack trace with `bt`), they may accumulate over time and occupy a large space on the filesystem. For this reason, it can be useful to disable their creation by adding the line

    ```bash
    ulimit -c 0
    ```

    to the sbatch script.
