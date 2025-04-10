[](){#ref-mlp-llm-inference-tutorial}

# LLM Inference Tutorial

This tutorial will guide you through the steps required to set up a PyTorch container and do ML inference. This means that we load an existing machine learning model, prompt it with some custom data, and run the model to see what output it will generate with our data.

To complete the tutorial, we get a PyTorch container from Nvidia, customize it to suit our needs, and tell the Container Engine how to run it. Finally, we set up and run a python script to run the machine learning model and generate some output.

The model we will be running is Google's [Gemma-7B](https://huggingface.co/google/gemma-7b#description), an LLM similar in style to the popular ChatGPT, which can generate text responses to text prompts that we feed into it.

## Gemma-7B Inference using NGC PyTorch

### Prequisites

This tutorial assumes you are able to access the cluster via SSH. To set up access to CSCS systems, follow the guide [here][ref-ssh], and read through the documentation about the [ML Platform][ref-platform-mlp].

###  Set up Permissions for the Nvidia NGC Catalog

Some [Nvidia NGC](https://www.nvidia.com/en-us/gpu-cloud) containers can only be downloaded with a valid API token, so we need to set one up. Create an account and setup your API token in the [Nvidia NGC container catalog](https://catalog.ngc.nvidia.com). Then, use your favorite text editor to create a credentials file `~/.config/enroot/.credentials` for enroot. Enroot will be responsible for fetching the container image from NGC behind the scenes. The credentials file should look like this:

```
machine nvcr.io login $oauthtoken password <API-TOKEN>
```

Make sure to replace `<API-TOKEN>` with your actual token.

### Modify the NGC Container

In theory, we could now just go ahead and use the container to run some PyTorch code. However, chances are that we will need some additional libraries or software. For this reason, we need to use some docker commands to build a container on top of what is provided by Nvidia. To do this, we create a new directory for building containers in our home directory and set up a [Dockerfile](https://docs.docker.com/reference/dockerfile/):

```
[cluster][user@cluster-ln001 ~]$ cd $SCRATCH
[cluster][user@cluster-ln001 user]$ mkdir pytorch-24.01-py3-venv && cd pytorch-24.01-py3-venv
```

Use your favorite text editor to create a file `Dockerfile` here. The Dockerfile should look like this:

```
FROM nvcr.io/nvidia/pytorch:24.01-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3.10-venv && apt-get clean && rm -rf /var/lib/apt/lists/*
```

The first line specifies that we are working on top of an existing container. In this case we start `FROM`  an NGC PyTorch container. Next, we set an `ENV`ironment variable that helps us run `apt-get` in the container. Finally, we `RUN` the package installer `apt-get` to install python virtual environments. This will let us install python packages later on without having to rebuild the container again and again. There's a bunch of extra commands in this line to tidy things up. If you want to understand what is happening, take a look at the [Docker documentation](https://docs.docker.com/develop/develop-images/instructions/#apt-get).

Now that we've setup the Dockerfile, we can go ahead and pass it to [Podman](https://podman.io/) to build a container. Podman is a tool that enables us to fetch, manipulate, and interact with containers on the cluster. For more information, please see the [Container Engine][ref-container-engine] page. To use Podman, we first need to configure some storage locations for it. This step is straightforward, just make the file `$HOME/.config/containers/storage.conf` (or `$XDG_CONFIG_HOME/containers/storage.conf` if `XDG_CONFIG_HOME` is set):

```
[storage]
  driver = "overlay"
  runroot = "/dev/shm/$USER/runroot"
  graphroot = "/dev/shm/$USER/root"

[storage.options.overlay]
  mount_program = "/usr/bin/fuse-overlayfs-1.13"
```


To build a container with Podman, we need to request a shell on a compute node from [SLURM][ref-slurm], pass the Dockerfile to Podman, and finally import the freshly built container using enroot. SLURM is a workload manager which distributes workloads on the cluster. Through SLURM, many people can use the supercomputer at the same time without interfering with one another in any way:

```
[cluster][user@cluster-ln001 pytorch-24.01-py3-venv]$ srun -A <ACCOUNT> --pty bash
[cluster][user@nid001234 pytorch-24.01-py3-venv]$ podman build -t pytorch:24.01-py3-venv .
# ... lots of output here ...
[cluster][user@nid001234 pytorch-24.01-py3-venv]$ enroot import -x mount -o pytorch-24.01-py3-venv.sqsh podman://pytorch:24.01-py3-venv
# ... more output here ...
```

where you should replace `<ACCOOUNT>` with your project account ID. At this point, you can exit the SLURM allocation by typing `exit`. You should be able to see a new squashfile next to your Dockerfile:

```
[cluster][user@cluster-ln001 pytorch-24.01-py3-venv]$ ls
Dockerfile  pytorch-24.01-py3-ven.sqsh
```

This squashfile is essentially a compressed container image, which can be run directly by the container engine. We will use our freshly-built container `pytorch-24.01-py3-venv.sqsh` in the following steps to run a PyTorch script that loads the Google Gemma-7B model and performs some inference with it.

### Set up an EDF

We need to set up an EDF (Environment Definition File) which tells the Container Engine what container to load, where to mount it, and what plugins to load. Use your favorite text editor to create a file `~/.edf/gemma-pytorch.toml` for the container engine. The EDF should look like this:

```
image = "/capstor/scratch/cscs/<USER>/pytorch-24.01-py3-venv/pytorch-24.01-py3-venv.sqsh"

mounts = ["/capstor", "/users"]

writable = true

[annotations]
com.hooks.aws_ofi_nccl.enabled = "true"
com.hooks.aws_ofi_nccl.variant = "cuda12"

[env]
FI_CXI_DISABLE_HOST_REGISTER = "1"
FI_MR_CACHE_MONITOR = "userfaultfd"
NCCL_DEBUG = "INFO"
```

Make sure to replace `<USER>` with your actual CSCS username. If you've decided to build the container somewhere else, make sure to supply the correct path to the `image` variable. 

The `image` variable defines which container we want to load. This could either be a container from an online docker repository, like `nvcr.io/nvidia/pytorch:24.01-py3`, or in our case, a local squashfile which we built ourselves.

The `mounts` variable defines which directories we want to mount where in our container. In general, it's a good idea to use the scratch directory to store outputs from any scientific software. In our case, we will not generate a lot of output, but it's a good practice to stick to anyways.

Finally, the `workdir` variable tells the container engine where to start working. If we request a shell, this is where we will find ourselves dropped initially after starting the container.

### Set up the Python Virtual Environment

This will be the first time we run our modified container. To run the container, we need allocate some compute resources using Slurm and launch a shell, just like we already did to build the container. This time, we also use the `--environment` option to specify that we want to launch the shell inside the container specified by our gemma-pytorch EDF file:

```
[cluster][user@cluster-ln001 ~]$ cd $SCRATCH && mkdir -p gemma-inference && cd  gemma-inference
[cluster][user@cluster-ln001 gemma-inference]$ srun -A <ACCOUNT> --environment=gemma-pytorch --container-workdir=$PWD --pty bash
```

PyTorch is already setup in the container for us. We can verify this by asking pip for a list of installed packages:

```
user@nid001234:/capstor/scratch/cscs/user/gemma-inference$ python -m pip list | grep torch
pytorch-quantization      2.1.2
torch                     2.2.0a0+81ea7a4
torch-tensorrt            2.2.0a0
torchdata                 0.7.0a0
torchtext                 0.17.0a0
torchvision               0.17.0a0
```

However, we will need to install a few more Python packages to make it easier to do inference with Gemma-7B. We create a virtual environment using python-venv. The `--system-site-packages` option ensures that we install packages in addition to the existing packages and don't accidentally install a new version of PyTorch over the one that has been put in place by Nvidia. Next, we activate the environment and use pip to install the two packages we need, `accelerate` and `transformers`:

```
user@nid001234:gemma-inference$ python -m venv --system-site-packages ./gemma-venv
user@nid001234:gemma-inference$ source ./gemma-venv/bin/activate
(gemma-venv) user@nid001234:/capstor/scratch/cscs/user/gemma-inference$ python -m pip install accelerate==0.30.1 transformers==4.38.1
# ... pip output ...
```

Before we move on to running the Gemma-7B model, we additionally need to make an account at [HuggingFace](https://huggingface.co), get an API token, and accept the [license agreement](https://huggingface.co/google/gemma-7b-it) for the [Gemma-7B](https://huggingface.co/google/gemma-7b) model. You can save the token to `$SCRATCH` using the huggingface-cli:

```
user@nid001234:gemma-inference$ pip install -U "huggingface_hub[cli]"
user@nid001234:gemma-inference$ HF_HOME=$SCRATCH/huggingface huggingface-cli login 
```

At this point, you can exit the SLURM allocation again by typing `exit`. If you `ls` the contents of the `gemma-inference` folder, you will see that the `gemma-venv` virtual environment folder persists outside of the SLURM job. Keep in mind that this virtual environment won't actually work unless you're running something from inside the PyTorch container. This is because the virtual environment ultimately relies on the resources packaged inside the container.

### Run Inference on Gemma-7B

Cool, now you have a working container with PyTorch and all the necessary Python packages installed! Let's move on to Gemma-7B.  We write a Python script `$SCRATCH/gemma-inference/gemma-inference.py` to load the model and prompt it with some custom text. The Python script should look like this:

```
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("google/gemma-7b-it")
model = AutoModelForCausalLM.from_pretrained("google/gemma-7b-it", device_map="auto")

input_text = "Write me a poem about the Swiss Alps."
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=1024)
print(tokenizer.decode(outputs[0]))
```

Feel free to change the `input_text` variable to whatever prompt you like.

All that remains is to run the python script inside the PyTorch container. There are several ways of doing this. As before, you could just use Slurm to get an interactive shell in the container. Then you would source the virtual environment and run the python script we just wrote. There's nothing wrong with this approach per se, but consider that you might be running much more complex and lengthy Slurm jobs in the future. You'll want to document how you're calling Slurm, what commands you're running on the shell, and you might not want to (or might not be able to) keep a terminal open for the length of time the job might take. For this reason, it often makes sense to write a batch file, which enables you to document all these processes and run the Slurm job regardless of whether you're still connected to the cluster.

Create a SLURM batch file `gemma-inference.sbatch` anywhere you like, for example in your home directory. The SLURM batch file should look like this:

```bash title="gemma-inference.sbatch"
#!/bin/bash
#SBATCH --job-name=gemma-inference
#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=288
#SBATCH --environment=gemma-pytorch
#SBATCH --account=<ACCOUNT>

export HF_HOME=$SCRATCH/huggingface
export TRANSFORMERS_VERBOSITY=info

cd $SCRATCH/gemma-inference/
source ./gemma-venv/bin/activate

set -x

python ./gemma-inference.py
```

The first few lines of the batch script declare the shell we want to use to run this batch file and pass several options to the SLURM scheduler. You can see that one of these options is one we used previously to load our EDF file. After this, we `cd` to our working directory, `source` our virtual environment and finally run our inference script.

As an alternative to using the `#SBATCH --environment=gemma-pytorch` option you can also run the code in the above script wrapped into an `srun -A <ACCOUNT> -ul --environment=gemma-pytorch bash -c "..."` statement. The tutorial on nanotron e.g. uses this pattern in `run_tiny_llama.sh`.

Once you've finished editing the batch file, you can save it and run it with SLURM:

```
[cluster][user@cluster-ln001 ~]$ sbatch ./gemma-inference.sbatch
```

This command should just finish without any output and return you to your terminal. At this point, you can follow the output in your shell using `tail -f slurm-<job-id>.out`. Besides you're free to do whatever you like; you can close the terminal, keep working, or just wait for the Slurm job to finish. You can always check on the state of your job by logging back into the cluster and running `squeue -l --me`. Once your job finishes, you will find a file in the same directory you ran it from, named something like `slurm-<job-id>.out`, and containing the output generated by your Slurm job. For this tutorial, you should see something like the following:


```bash 
[cluster][user@cluster-ln001 gemma-inference]$ cat ./slurm-543210.out 
/capstor/scratch/cscs/user/gemma-inference/gemma-venv/lib/python3.10/site-packages/huggingface_hub/file_download.py:1132: FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
  warnings.warn(
Gemma's activation function should be approximate GeLU and not exact GeLU.
Changing the activation function to `gelu_pytorch_tanh`.if you want to use the legacy `gelu`, edit the `model.config` to set `hidden_activation=gelu`   instead of `hidden_act`. See https://github.com/huggingface/transformers/pull/29402 for more details.
Loading checkpoint shards: 100%|██████████| 4/4 [00:03<00:00,  1.13it/s]
/capstor/scratch/cscs/user/gemma-inference/gemma-venv/lib/python3.10/site-packages/huggingface_hub/file_download.py:1132: FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
  warnings.warn(
<bos>Write me a poem about the Swiss Alps.

In the heart of Switzerland, where towering peaks touch sky,
Lies a playground of beauty, beneath the watchful eye.
The Swiss Alps, a majestic force,
A symphony of granite, snow, and force.

Snow-laden peaks pierce the heavens above,
Their glaciers whisper secrets of ancient love.
Emerald valleys bloom with flowers,
A tapestry of colors, a breathtaking sight.

Hiking trails wind through meadows and woods,
Where waterfalls cascade, a silent song unfolds.
The crystal clear lakes reflect the sky above,
A mirror of dreams, a place of peace and love.

The Swiss Alps, a treasure to behold,
A land of wonder, a story untold.
From towering peaks to shimmering shores,
They inspire awe, forevermore.<eos>
```

Congrats! You've run Google Gemma-7B inference on four GH200 chips simultaneously. Move on to the next tutorial or try the challenge.

### Challenge

Using the same approach as in the latter half of step 4, use pip to install the package `nvitop`. This is a tool that shows you a concise real-time summary of GPU activity. Then, run Gemma and launch nvitop at the same time:

```
(gemma-venv) user@nid001234:/capstor/scratch/cscs/user/gemma-inference$ python ./gemma-inference.py > ./gemma-output.log 2>&1 & nvitop
```

Note the use of bash `> ./gemma-output.log 2>&1` to hide any output from Python. Note also the use of the single ampersand `'&'` which backgrounds the first command and runs `nvitop` on top.

After a moment, you will see your Python script spawn on all four GPUs, after which the GPU activity will increase a bit and then go back to idle. At this point, you can hit `q` to quite nvitop and you will find the output of your Python script in `./gemma-output.log`.

### Collaborating in Git

In order to track and exchange your progress with colleagues, it is recommended to store the EDF, Dockerfile and your application code alongside in a Git repository in a directory on `$SCRATCH` and share it with colleagues.
