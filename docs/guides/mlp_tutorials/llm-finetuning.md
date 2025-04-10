[](){#ref-mlp-llm-finetuning-tutorial}

# LLM Finetuning Tutorial

This tutorial will take the model from the [LLM Inference][ref-mlp-llm-inference-tutorial] tutorial and show you how to perform finetuning. This means that we take the model and train it on some new custom data to change its behavior.

To complete the tutorial, we set up some extra libraries that will help us to update the state of the machine learning model. We also write a script that will allow us to unlock more of the performance offered by the cluster, by running our fine-tuning task on two or more nodes.

### Prerequisites

This tutorial assumes you've already successfully completed the [LLM Inference][ref-mlp-llm-inference-tutorial] tutorial. For fine-tuning Gemma, we will rely on the NGC PyTorch container and the libraries we've already installed in the Python environment used previously.

### Set up TRL

We will use HuggingFace TRL to fine-tune Gemma-7B on the [OpenAssistant dataset](https://huggingface.co/datasets/OpenAssistant/oasst_top1_2023-08-25). First, we need to update our Python environment with some extra libraries to support TRL. To do this, we can launch an interactive shell in the PyTorch container, just like we did in the previous tutorial. Then, we install `peft`:

```
[cluster][user@cluster-ln001 gemma-inference]$ cd $SCRATCH/gemma-inference
[cluster][user@cluster-ln001 gemma-inference]$ srun --environment=gemma-pytorch --container-workdir=$PWD --pty bash
user@nid001234:/bret/scratch/cscs/user/gemma-inference$ source ./gemma-venv/bin/activate
(gemma-venv) user@nid001234:/bret/scratch/cscs/user/gemma-inference$ python -m pip install peft==0.11.1
# ... pip output ...
```

Next, we also need to clone and install the `trl` Git repository so that we have access to the fine-tuning scripts in it. For this purpose, we will install the package in editable mode in the virtual environment. This makes it available in python scripts independent of the current working directory and without creating a redundant copy of the files.

```
[cluster][user@cluster-ln001 ~]$ git clone https://github.com/huggingface/trl -b v0.7.11
[cluster][user@cluster-ln001 ~]$ pip install -e ./trl   # install in editable mode
```

When this step is complete, you can exit the shell by typing `exit`.

### Finetune Gemma-7B

t this point, we can set up a fine-tuning script and start training Gemma-7B. Use your favorite text editor to create the file `fine-tune-gemma.sh` just outside the trl and gemma-venv directories:

```bash title="fine-tune-gemma.sh"
#!/bin/bash

source ./gemma-venv/bin/activate

set -x
 
export HF_HOME=$SCRATCH/huggingface
export TRANSFORMERS_VERBOSITY=info

ACCEL_PROCS=$(( $SLURM_NNODES * $SLURM_GPUS_PER_NODE ))

MAIN_ADDR=$(echo "${SLURM_NODELIST}" | sed 's/[],].*//g; s/\[//g')
MAIN_PORT=12802

accelerate launch --config_file trl/examples/accelerate_configs/multi_gpu.yaml \
           --num_machines=$SLURM_NNODES --num_processes=$ACCEL_PROCS \
           --machine_rank $SLURM_PROCID \
           --main_process_ip $MAIN_ADDR --main_process_port $MAIN_PORT \
           trl/examples/scripts/sft.py \
           --model_name google/gemma-7b \
           --dataset_name OpenAssistant/oasst_top1_2023-08-25 \
           --per_device_train_batch_size 2 \
           --gradient_accumulation_steps 1 \
           --learning_rate 2e-4 \
           --save_steps 200 \
	       --max_steps 400 \
           --use_peft \
           --lora_r 16 --lora_alpha 32 \
           --lora_target_modules q_proj k_proj v_proj o_proj \
           --output_dir gemma-finetuned-openassistant
```

This script has quite a bit more content to unpack. We use HuggingFace accelerate to launch the fine-tuning process, so we need to make sure that accelerate understands which hardware is available and where. Setting this up will be useful in the long run because it means we can tell SLURM how much hardware to reserve, and this script will setup all the details for us.

The cluster has four GH200 chips per compute node. We can make them accessible to scripts run through srun/sbatch via the option `--gpus-per-node=4`. Then, we calculate how many processes accelerate should launch. We want to map each GPU to a separate process, this should be four processes per node. We multiply this by the number of nodes to obtain the total number of processes. Next, we use some bash magic to extract the name of the head node from SLURM environment variables. Accelerate expects one main node and launches tasks on the other nodes from this main node. Having sourced our python environment at the top of the script, we can then launch Gemma fine-tuning. The first four lines of the launch line are used to configure accelerate. Everything after that configures the `trl/examples/scripts/sft.py` Python script, which we use to train Gemma.

Next, we also need to create a short SLURM batch script to launch our fine-tuning script:

```bash title="fine-tune-sft.sbatch"
#!/bin/bash
#SBATCH --job-name=gemma-finetune
#SBATCH --time=00:30:00
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=288
#SBATCH --account=<ACCOUNT>

set -x

srun -ul --environment=gemma-pytorch --container-workdir=$PWD bash fine-tune-gemma.sh
```

We set a few Slurm parameters like we already did in the previous tutorial. Note that we leave the number of nodes unspecified. This way, we can decide the number of nodes we want to use when we launch the batch job using Slurm.

Now that we've setup a fine-tuning script and a Slurm batch script, we can launch our fine-tuning job. We'll start out by launching it on two nodes. It should take about 10-15 minutes to fine-tune Gemma:

```
[cluster][user@cluster-ln001 ~]$ sbatch --nodes=1 fine-tune-sft.sbatch
```

### Compare finetuned Gemma against default Gemma

We can reuse our python script from the first tutorial to do inference on the Gemma model that we just fine-tuned. Let's try out a different prompt in `gemma-inference.py`:

```
input_text = "What are the 5 tallest mountains in the Swiss Alps?"
```

We can run inference using our batch script from the previous tutorial:

```
[cluster][user@cluster-ln001 ~]$ sbatch ./gemma-inference.sbatch
```

Inspecting the output should yield something like this:

```
<bos>What are the 5 tallest mountains in the Swiss Alps?

The Swiss Alps are home to some of the tallest mountains in the world. Here are
the 5 tallest mountains in the Swiss Alps:

1. Mont Blanc (4,808 meters)
2. Matterhorn (4,411 meters)
3. Dom (4,161 meters)
4. Jungfrau (4,158 meters)
5. Mont Rose (4,117 meters)<eos>
```

Next, we can update the model line in our Python inference script to use the model that we just fine-tuned:

```
model = AutoModelForCausalLM.from_pretrained("gemma-finetuned-openassistant/checkpoint-400", device_map="auto")
```

If we re-run inference, the output will be a bit more detailed and explanatory, similar to output we might expect from a helpful chatbot. One example looks like this:

```
<bos>What are the 5 tallest mountains in the Swiss Alps?

The Swiss Alps are home to some of the tallest mountains in Europe, and they are a popular destination for mountai
neers and hikers. Here are the five tallest mountains in the Swiss Alps:

1. Mont Blanc (4,808 m/15,774 ft): Mont Blanc is the highest mountain in the Alps and the highest mountain in Euro
pe outside of Russia. It is located on the border between France and Italy, and it is a popular destination for mo
untaineers and hikers.

2. Dufourspitze (4,634 m/15,203 ft): Dufourspitze is the highest mountain in Switzerland and the second-highest mo
untain in the Alps. It is located in the Valais canton of Switzerland, and it is a popular destination for mountai
neers and hikers.

3. Liskamm (4,527 m/14,855 ft): Liskamm is a mountain in the Bernese Alps of Switzerland. It is located in the Ber
n canton of Switzerland, and it is a popular destination for mountaineers and hikers.

4. Weisshorn (4,506 m/14,783 ft): Weisshorn is a mountain in the Pennine Alps of Switzerland. It is located in the
 Valais canton of Switzerland, and it is a popular destination for mountaineers and hikers.

5. Matterhorn (4,478 m/14,690 ft): Matterhorn is a mountain in the Pennine Alps of Switzerland. It is located in the Valais canton of Switzerland, and it is a popular destination for mountaineers and hikers.

These mountains are all located in the Swiss Alps, and they are a popular destination for mountaineers and hikers. If you are planning a trip to the Swiss Alps, be sure to check out these mountains and plan your itinerary accordingly.
```

Your output may look different after fine-tuning, but in general you will see that the fine-tuned model generates more verbose output. Double-checking the output reveals that the list of mountains produced by Gemma is not actually correct. The following table lists the 5 tallest Swiss peaks, according to Wikipedia.


1. Dufourspitze 4,634m
2. Nordend 4,609m
3. Zumsteinspitz 4,563m
4. Signalkuppe 4,554m
5. Dom 4,545m

This is an important reminder that machine-learning models like Gemma need extra checks to confirm any generated outputs.