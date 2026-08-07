[](){#software-ml-llm-inference-multi-node-tutorial}

# LLM Inference (multi-node and AMD) Tutorial

This is somehow a multi-node version of [LLM Inference Tutorial][software-ml-llm-inference-tutorial].

This tutorial will guide you through the steps required to setup a vLLM container and do ML inference.
This means that we load an existing machine learning model, prompt it with some custom data, and run the model to see what output it will generate with our data.

In this specific tutorial we are going to show how:

- run an LLM model with vLLM
- on AMD GPUs
- in a multi-node setup

TODO what is not: how to configure at best vllm

## TODO name a model

### Prerequisites

### Pull the image

From early 2026 the [AMD's Docker images `rocm/vllm` (and others) have been deprecated](https://docs.vllm.ai/en/v0.19.1/getting_started/installation/gpu/#use-amds-docker-images-deprecated) in favour of [vllm/vllm-openai-rocm](https://hub.docker.com/r/vllm/vllm-openai-rocm)

```console
enroot import \
    -o ce-images/vllm-opeani-rocm.sqfs \
    docker://vllm/vllm-openai-rocm:latest
```

See also

- [Container Engine][ref-container-engine]
- [Lustre Tuning][ref-guides-storage-lustre]

### Setup EDF

See:
- [netstack][ref-ce-netstack-source]
- [AWS OFI NCCL hook][ref-ce-aws-ofi-hook]
- for available netstack have a look at `/capstor/store/cscs/cscs/public/containers/netstack`


```toml
image = "<absolute-path-to>/ce-images/vllm-openai-rocm.sqfs"
writable = true
entrypoint = false

[annotations]
com.hooks.netstack.source = "artifact"
com.hooks.netstack.version = "26.07.1"
com.hooks.netstack.name = "gpu:rocm7,cxi:13.1.0,ofi:2.6.0,aws:1.20.0"

com.hooks.cxi.enabled = "true"
com.hooks.aws_ofi_nccl.enabled = "true"
```

At this point you would be ready to launch a single rank instance with something similar to

```console
srun --environment ./vllm-new.toml -pmi300 --pty bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct
```

Once you get that the node is serving, you can start using it with

```console
curl -s http://nid002710:8000/v1/models | jq .
```

or

```console
curl -s http://nid002672:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "prompt": "San Francisco is a",
        "max_tokens": 7,
        "temperature": 0
    }' | jq .
```

### Single Rank - Multi-GPU

```
srun --environment ./vllm-new.toml -pmi300 -N1 --tasks-per-node=1 --gpus-per-task 2 --pty bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct --tensor-parallel-size 2
```

### Multi Rank (with Slurm)

```sbatch
WIP
```

### Test it
