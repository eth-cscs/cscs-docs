[](){#software-ml-vllm-sglang-amdgpus}

# vLLM/SGLang on AMD GPUs Tutorial

This tutorial will guide you through the steps required to setup a vLLM or SGLang container on AMD GPUs to serve a LLM.

In this specific tutorial we are going to show how:

- setup a vLLM/SGLang container
- to run a LLM
- with Slurm
- on AMD GPUs
- in a single or multi-node setup
- and test it

!!! warning "What this guide is NOT"
    This guide is not about how to configure correctly/at best vLLM or SGLang on Alps clusters.
    For more details about vLLM or SGLang parameters and best setup for a specific model have a look at <https://recipes.vllm.ai/> and <https://docs.sglang.io/>, respectively, while for what concerns the Alps cluster setup, you'll have to explore documentation for the specific cluster, experiment and benchmark.

### Prerequisites

This tutorial assumes you are able to access the cluster via SSH. To set up access to CSCS systems, follow the guide [here][ref-ssh], and read through the documentation about the [ML platform][ref-platform-mlp].

In particular, this tutorial aims at Beverin cluster, but it should be possible to adapt it with minor changes to other clusters as well.

### Get the vLLM/SGLang image

In this tutorial we are going to use a vLLM/SGLang official image for ROCm systems. From early 2026 the AMD's Docker images [`rocm/vllm`](https://hub.docker.com/r/rocm/vllm) and [`rocm/sgl-dev`](https://hub.docker.com/r/rocm/sgl-dev) (and others) have been deprecated (see, e.g., [here](https://docs.vllm.ai/en/v0.19.1/getting_started/installation/gpu/#use-amds-docker-images-deprecated) and [here](https://lmsysorg.mintlify.app/docs/hardware-platforms/amd_gpu#install-using-docker-recommended)) in favour of [`vllm/vllm-openai-rocm`](https://hub.docker.com/r/vllm/vllm-openai-rocm) and [`lmsysorg/sglang`](https://hub.docker.com/r/lmsysorg/sglang/tags) images, respectively. The following steps will show how to use the new images.

Beforehand, if you have not done already, let's create a directory to keep track of all images used with the CE. Since container images are large files and the filesystem is a shared resource, we need to apply [best practices for LUSTRE][ref-guides-storage-lustre] so they are properly distributed across storage nodes.

```console title="Container image directory with recommended LUSTRE settings"
mkdir -p $SCRATCH/ce-images
lfs setstripe -E 4M -c 1 -E 64M -c 4 -E -1 -c -1 -S 4M $SCRATCH/ce-images
```

Now we can pull the docker image in our container images directory just created. The following command allows to import a docker image as squashfs archive that can be used with [Container Engine][ref-container-engine].

=== "`vLLM`"
    !!! example ""
        ```console
        enroot import \
            -o $SCRATCH/ce-images/inference-rocm.sqfs \
            docker://vllm/vllm-openai-rocm:latest
        ```

=== "`SGLang`"
    !!! example "This uses Podman to pull the image first, to avoid issues related to filesystem permissions when using Enroot directly with Docker Hub."
        ```console
        export TAG=v0.5.18-rocm720-mi30x # replace with the latest rocm720-mi30x tag available at https://hub.docker.com/r/lmsysorg/sglang/tags
        podman pull docker://lmsysorg/sglang:$TAG
        enroot import \
            -o $SCRATCH/ce-images/inference-rocm.sqfs \
            podman://lmsysorg/sglang:$TAG
        ```

### Setup EDF

The following step is the creation of an Environment Definition File ([EDF][ref-ce-edf-reference]) where details on how to start the container are specified.
In particular, this tutorial makes use of [netstack][ref-ce-netstack-source] and related hooks for binding compatible network libraries (mainly `libfabric`, `CXI` and `aws-ofi-nccl`) inside the container.

Save this as a TOML file named `env-inference.toml` so that you can use it later.

```toml
image = "/capstor/scratch/cscs/<username>/ce-images/inference-rocm.sqfs"
writable = true
entrypoint = false

[annotations]
com.hooks.netstack.source = "artifact"
com.hooks.netstack.version = "26.07.1"
com.hooks.netstack.name = "gpu:rocm7,cxi:13.1.0,ofi:2.6.0,aws:1.20.0"

com.hooks.cxi.enabled = "true"
com.hooks.aws_ofi_nccl.enabled = "true"

[env]
# Note: this solves an hang happening at NCCL initialization time
HWLOC_COMPONENTS="-gl"

FI_PROVIDER="cxi"
FI_CXI_RX_MATCH_MODE="software"
FI_MR_CACHE_MONITOR="disabled"
```

### Launch a Single Node instance

At this point everything is ready, the CE image needs just to be launched and vLLM or SGLang started.

The simplest run possible is a single GPU instance

=== "`vLLM`"
    !!! example ""
        ```console
        srun --environment ./env-inference.toml -pmi300 \
            vllm serve Qwen/Qwen2.5-1.5B-Instruct
        ```

=== "`SGLang`"
    !!! example "This sets the maximum number of tokens explicitly to avoid issues with the `--mem-fraction-static` parameter."
        ```console
        srun --environment ./env-inference.toml -pmi300 \
            sglang serve Qwen/Qwen2.5-1.5B-Instruct --max-total-tokens 10240
        ```

or using multiple GPUs from the same node

=== "`vLLM`"
    !!! example ""
        ```console
        srun --environment ./env-inference.toml -pmi300 --gpus-per-task 4 \
            vllm serve Qwen/Qwen2.5-1.5B-Instruct --tensor-parallel-size 4
        ```

=== "`SGLang`"
    !!! example "This sets the maximum number of tokens explicitly to avoid issues with the `--mem-fraction-static` parameter."
        ```console
        srun --environment ./env-inference.toml -pmi300 --gpus-per-task 4 \
            sglang serve Qwen/Qwen2.5-1.5B-Instruct --tensor-parallel-size 4 --max-total-tokens 102400
        ```

### Use the instance

Once the vLLM/SGLang instance is serving, i.e. the master node prints out on which address and port it is listening, it provides the standard endpoint interface.

It can be queried for served LLMs with

```console
curl -s http://nid00xxxx:8000/v1/models | jq .
```

or a prompt can be submitted to one of the provided models

```console
curl -s http://nid00xxxx:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "prompt": "San Francisco is a",
        "max_tokens": 7,
        "temperature": 0
    }' | jq .
```

### Launch a Multi Node instance (with Slurm)

For multi-node instances a sbatch script like the following one is able to:

=== "`vLLM`"
    !!! example """
      - start `ray` on the master node
      - start `ray` on the workers nodes registering their resources and announcing themselves to the master node
      - just on the master node start `vllm serve` (with required parameters)
    """
        ```sbatch
        #!/bin/bash
        #SBATCH -J inference-instance
        #SBATCH -A csstaff
        #SBATCH -p mi300
        #SBATCH -t 01:00:00
        #SBATCH -N 2
        #SBATCH --ntasks-per-node=1
        #SBATCH --gpus-per-task=4
        #SBATCH --cpus-per-task=72
        #SBATCH --output=inference-%j.out

        export ENV_FILE=<absolute-path-to>/env-inference.toml

        export TENSOR_PARALLEL_SIZE=${SLURM_GPUS_ON_NODE} # Set it to the number of GPU per task
        export PIPELINE_PARALLEL_SIZE=${SLURM_NNODES} # Set it to the number of allocated GPU nodes

        export HF_HOME="/scratch/data/.cache"

        echo "[Main workflows] Set RAY configuration..."
        # Getting the master name and IP of the master node
        export MASTER_NODE=$(hostname)
        export MASTER_NODE_IP=$(hostname -i)

        # Setup RAY
        export PORT=46382
        export RAY_ADDRESS="${MASTER_NODE_IP}:${PORT}"

        export RAY_METRICS_ENABLED=0
        export RAY_DASHBOARD_ENABLED=0
        export RAY_PROMETHEUS_METRICS_ENABLED=1
        export RAY_event_stats_print_interval_ms=1000
        export RAY_ENABLE_RECORD_ACTOR_TASK_LOGS=1
        export RAY_METRICS_EXPORT_PORT=8080
        export RAY_GRAFANA_HOST="http://localhost:3000"
        export RAY_PROMETHEUS_HOST="http://localhost:9090"
        export RAY_GRAFANA_IFRAME_HOST="http://localhost:3000"
        export RAY_ENABLE_TIMELINE=1  # Critical for task/actor metrics
        export RAY_METRICS_GAUGE_PUSH_INTERVAL_S=1
        export RAY_DISABLE_USAGE_STATS=1
        export RAY_DEDUP_LOGS=0
        export RAY_TMP_DIR=/tmp/ray_tmp_${SLURM_JOB_ID}
        export RAY_grpc_client_keepalive_time_ms="30000"
        export RAY_grpc_client_keepalive_timeout_ms="10000"
        export RAY_grpc_server_keepalive_time_ms="30000"
        export RAY_grpc_server_keepalive_timeout_ms="10000"
        export RAY_CGRAPH_get_timeout="3600"
        export RAY_LOG_TO_STDERR=0

        echo "HEAD NODE: ${MASTER_NODE} ${MASTER_NODE_IP}"

        srun -ul -oinference-%j-%t.out --environment=${ENV_FILE} bash -c '
        set -x

        echo "Installing RAY..."
        pip install -q ray

        # Note: avoid it complaining
        export HIP_VISIBLE_DEVICES=$ROCR_VISIBLE_DEVICES
        unset ROCR_VISIBLE_DEVICES
        unset CUDA_VISIBLE_DEVICES

        echo "Starting RAY..."
        if [[ $SLURM_PROCID = 0 ]]; then
            echo "[Main workflows] Will serve RAY on: ${MASTER_NODE_IP}"
            export VLLM_HOST_IP=${MASTER_NODE_IP}
            ray start --head \
                --node-ip-address=$MASTER_NODE_IP \
                --port=$PORT \
                --num-cpus=${SLURM_CPUS_PER_TASK} \
                --num-gpus=${SLURM_GPUS_ON_NODE} \
                --temp-dir=$RAY_TMP_DIR \
                --disable-usage-stats || true

            while true; do
                alive_nodes=$(ray status | awk "/Active:/{flag=1;next}/Pending:/{flag=0}flag" | grep "node_" | wc -l)
                if ! [[ "$alive_nodes" =~ ^[0-9]+$ ]]; then
                    alive_nodes=0
                fi
                if [ "$alive_nodes" -ge "$SLURM_JOB_NUM_NODES" ]; then
                    break
                fi
                echo "Waiting for all nodes to join [$alive_nodes/$SLURM_JOB_NUM_NODES]"
                sleep 5
            done

            # ray status

            echo "Starting..."
            vllm serve Qwen/Qwen2.5-1.5B-Instruct \
                --tensor-parallel-size ${TENSOR_PARALLEL_SIZE} \
                --pipeline-parallel-size ${PIPELINE_PARALLEL_SIZE} \
                --distributed-executor-backend=ray\
                --gpu-memory-utilization 0.7

            if [ $? -eq 0 ]; then
                echo "JOB COMPLETED"
            else
                echo "JOB FAILED"
            fi
            exit $?
        else
            sleep 15

            export VLLM_HOST_IP=$(hostname -i)

            echo "Bringing ray worker up on ${VLLM_HOST_IP} at ${RAY_ADDRESS}"
            ray start --address="${RAY_ADDRESS}" \
                --node-ip-address=${VLLM_HOST_IP} \
                --num-cpus=${SLURM_CPUS_PER_TASK} \
                --num-gpus=${SLURM_GPUS_ON_NODE} \
                --block || true
        fi
        '
        ```

=== "`SGLang`"
    !!! example """
      - start `sglang` on every node with the correct parameters for multi-node serving
    """
        ```sbatch
        #!/bin/bash
        #SBATCH -J inference-instance
        #SBATCH -A csstaff
        #SBATCH -p mi300
        #SBATCH -t 01:00:00
        #SBATCH -N 2
        #SBATCH --ntasks-per-node=1
        #SBATCH --gpus-per-task=4
        #SBATCH --cpus-per-task=72
        #SBATCH --output=inference-%j.out

        export ENV_FILE=<absolute-path-to>/env-inference.toml

        export TENSOR_PARALLEL_SIZE=${SLURM_GPUS_ON_NODE} # Set it to the number of GPU per task
        export PIPELINE_PARALLEL_SIZE=${SLURM_NNODES} # Set it to the number of allocated GPU nodes

        export HF_HOME="/scratch/data/.cache"

        echo "[Main workflows] Set MULTI-NODE configuration..."
        export MASTER_ADDR=$(echo $SLURM_JOB_NODELIST | cut -d',' -f1 | tr -d '[]' | cut -d'-' -f1) # These variables are only available once srun starts this script on the nodes
        export MASTER_PORT=30001
        export PORT=30000

        srun -ul -oinference-%j-%t.out --environment=${ENV_FILE} bash -c '
            set -x

            if [[ $SLURM_PROCID = 0 ]]; then
                echo "[Main workflows] Will serve SGLang inference on: ${MASTER_ADDR}:${PORT}"
                echo SLURM_JOB_NODELIST=$SLURM_JOB_NODELIST
                echo SLURMD_NODENAME=$SLURMD_NODENAME
            fi    
            
            echo "Starting..."

            sglang serve \
                --port $PORT \
                --host 0.0.0.0 \
                --trust-remote-code \
                --dist-init-addr $MASTER_ADDR:$MASTER_PORT \
                --node-rank $SLURM_NODEID \
                --nnodes $SLURM_NNODES \
                --served-model-name qwen2.5-1.5b-instruct \
                --model-path Qwen/Qwen2.5-1.5B-Instruct \
                --tensor-parallel-size ${TENSOR_PARALLEL_SIZE} \
                --pipeline-parallel-size ${PIPELINE_PARALLEL_SIZE} \
                --max-total-tokens 1048576  # Set the maximum number of tokens explicitly instead of using --mem-fraction-static

            if [ $? -eq 0 ]; then
                echo "JOB COMPLETED"
            else
                echo "JOB FAILED"
            fi
            exit $?
        '
        ```


Save previous content in a `run-inference.sbatch` file and then use it to start the instance with

```console
sbatch run-inference.sbatch
```

which might require quite some time for completing the startup phase.
For this reason it might be useful to inspect instance logs with

```console
tail -f inference-*-0.out
```

Once the vLLM/SGLang inference instance is ready, it can be used exactly as how it has been done before for single node instances (see [here][use-the-instance]).
