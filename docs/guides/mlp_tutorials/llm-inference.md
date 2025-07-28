[](){#ref-mlp-llm-inference-tutorial}

# LLM Inference Tutorial

This tutorial will guide you through the steps required to set up a PyTorch container and do ML inference.
This means that we load an existing machine learning model, prompt it with some custom data, and run the model to see what output it will generate with our data.

To complete the tutorial, we get a PyTorch container from Nvidia's GPU Cloud (NGC), customize it to suit our needs, and tell the Container Engine how to run it.
Finally, we set up and run a python script to run the machine learning model and generate some output.

The model we will be running is Google's [Gemma-7B](https://huggingface.co/google/gemma-7b-it#description) in the instruction-tuned variant. This is an LLM similar in style to popular chat assistants like ChatGPT, which can generate text responses to text prompts that we feed into it.

## Gemma-7B Inference using NGC PyTorch

### Prerequisites

This tutorial assumes you are able to access the cluster via SSH. To set up access to CSCS systems, follow the guide [here][ref-ssh], and read through the documentation about the [ML Platform][ref-platform-mlp].

For clarity, we prepend all shell commands with the hostname and any active Python virtual environment they are executed in. E.g. `clariden-lnXXX` refers to a login node on Clariden, while `nidYYYYYY` is a compute node (with placeholders for numeric values). The commands listed here are run on Clariden, but can be adapted slightly to run on other vClusters as well.

!!! note
     Login nodes are a shared environment for editing files, preparing and submitting SLURM jobs as well as inspecting logs. They are not intended for running significant data processing or compute work. Any memory- or compute-intensive work should instead be done on compute nodes.
     
     If you need to move data [externally][ref-data-xfer-external] or [internally][ref-data-xfer-internal], please follow the corresponding guides using Globus or the `xfer` queue, respectively.

### Build a modified NGC PyTorch Container

In theory, we could just go ahead and use the vanilla container image to run some PyTorch code.
However, chances are that we will need some additional libraries or software.
For this reason, we need to use some docker commands to build on top of what is provided by Nvidia.
To do this, we create a new directory for recipes to build containers in our home directory and set up a [Dockerfile](https://docs.docker.com/reference/dockerfile/):

```console
[clariden-lnXXX]$ cd $SCRATCH
[clariden-lnXXX]$ mkdir -p tutorials/gemma-7b
[clariden-lnXXX]$ cd tutorials/gemma-7b
```

Use your favorite text editor to create a file `Dockerfile` here. The Dockerfile should look like this:

```dockerfile title="$SCRATCH/tutorials/gemma-7b/Dockerfile"
FROM nvcr.io/nvidia/pytorch:24.01-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y python3.10-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

The first line specifies that we are working on top of an existing container.
In this case we start `FROM` an [NGC PyTorch container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch).
Next, we set an environment variable with `ENV` that helps us run `apt-get` in the container.
Finally, we `RUN` the package installer `apt-get` to install python virtual environments.
This will let us install python packages later on without having to rebuild the container again and again.
There's a bunch of extra commands in this line to tidy things up.
If you want to understand what is happening, take a look at the [Docker documentation](https://docs.docker.com/develop/develop-images/instructions/#apt-get).

!!! note "Recent changes in NGC releases"
    Starting with the 24.11 release, NGC PyTorch no longer requires the installation of the Python venv module. That is, the Dockerfile simplifies to only the first line, e.g. for the `25.06` release

    ```dockerfile
    FROM nvcr.io/nvidia/pytorch:25.06-py3
    ```

    The remaining steps can then be performed equivalently, replacing the version number `24.01` by the one chosen in the Dockerfile (e.g. `25.06`).
    
    It is generally recommended to stick to one of the most recent versions of NGC, unless there is a strong reason from your application to stick to an old version for compatibility.

Now that we've setup the Dockerfile, we can go ahead and pass it to [Podman](https://podman.io/) to build a container.
Podman is a tool that enables us to fetch, manipulate, and interact with containers on the cluster.
For more information, please see the [Container Engine][ref-container-engine] page.
To use Podman, we first need to configure some storage locations for it.
This step is straightforward, just create the file in your home:

```toml title="$HOME/.config/containers/storage.conf"
[storage]
  driver = "overlay"
  runroot = "/dev/shm/$USER/runroot"
  graphroot = "/dev/shm/$USER/root"

[storage.options.overlay]
  mount_program = "/usr/bin/fuse-overlayfs-1.13"
```

!!! warning
    If `$XDG_CONFIG_HOME` is set, place this file at `$XDG_CONFIG_HOME/containers/storage.conf` instead.

Before building the container image, we create a dedicated directory to keep track of all images used with the CE. Since container images are large files and the filesystem is a shared resource, we need to apply [best practices for LUSTRE][ref-guides-storage-lustre] so they are properly distributed across storage nodes.

```console title="Container image directory with recommended LUSTRE settings"
[clariden-lnXXX]$ mkdir -p $SCRATCH/ce-images
[clariden-lnXXX]$ lfs setstripe -E 4M -c 1 -E 64M -c 4 -E -1 -c -1 -S 4M \
  $SCRATCH/ce-images # (1)!
```

1. This makes sure that files stored subsequently end up on the same storage node (up to 4 MB), on 4 storage nodes (between 4 and 64 MB) or are striped across all storage nodes (above 64 MB)

To build a container with Podman, we need to request a shell on a compute node from [Slurm][ref-slurm], pass the Dockerfile to Podman, and finally import the freshly built container to the dedicated directory using enroot.
Slurm is a workload manager which distributes workloads on the cluster.
Through Slurm, many people can use the supercomputer at the same time without interfering with one another.


```console
[clariden-lnXXX]$ srun -A <ACCOUNT> --pty bash
[nidYYYYYY]$ podman build -t ngc-pytorch:24.01 . # (1)!
# ... lots of output here ...
[nidYYYYYY]$ enroot import -x mount \
  -o $SCRATCH/ce-images/ngc-pytorch+24.01.sqsh \
  podman://ngc-pytorch:24.01 # (2)!
# ... more output here ...
```

1. This builds the container image with the current working directory as the build context. The `Dockerfile` inside that directory is implicitly used as a recipe. If it is named differently use the `-f path/to/Dockerfile` option.  
2. The newly built container image is imported and stored under `$SCRATCH/ce-images`.

where you should replace `<ACCOUNT>` with your project account ID.
At this point, you can exit the Slurm allocation by typing `exit`.
You should be able to see a new Squashfs file in your container image directory:

```console
[clariden-lnXXX]$ ls $SCRATCH/ce-images
ngc-pytorch+24.01.sqsh
```

This squashfs file is essentially a compressed container image, which can be run directly by the container engine.
We will use our freshly-built container `ngc-pytorch+24.01.sqsh` in the following steps to run a PyTorch script that loads the Google Gemma-7B model and performs some inference with it.

!!! note
    In order to import a container image from a registry without building additional layers on top of it, we can directly use `enroot` (without `podman`). This is useful in this tutorial if we want to use a more recent NGC PyTorch container that was released since `24.11`. Use the following syntax for importing the `25.06` release:

    ```console
    [nidYYYYYY]$ enroot import -x mount \
      -o $SCRATCH/ce-images/ngc-pytorch+25.06.sqsh docker://nvcr.io#nvidia/pytorch:25.06-py3
    ```


### Set up an EDF

We need to set up an EDF (Environment Definition File) which tells the Container Engine what container image to load, which paths to mount from the host filesystem, and what plugins to load. Use your favorite text editor to create a file `ngc-pytorch-gemma-24.01.toml` for the container engine. The EDF should look like this:

```toml  title="$SCRATCH/tutorials/gemma-7b/ngc-pytorch-gemma-24.01.toml"
image = "${SCRATCH}/ce-images/ngc-pytorch+24.01.sqsh" # (1)!

mounts = [
    "/capstor",
    "/iopsstor"
] # (2)!

workdir = "${SCRATCH}/tutorials/gemma-7b" # (3)!

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

If you've decided to build the container somewhere else, make sure to supply the correct path to the `image` variable. 

The `image` variable defines which container we want to load.
This could either be a container from an online docker repository, like `nvcr.io/nvidia/pytorch:24.01-py3`, or in our case, a local squashfs file which we built ourselves.

The `mounts` variable defines which directories we want to mount where in our container.
In general, it's a good idea to use a directory under `/capstor/scratch` directory to store outputs from any scientific software as this filesystem is optimized for sequential write-operations as described in [Alps storage][ref-alps-storage]. This particularly applies to e.g. checkpoints from ML training, which we will see in the next tutorials (and there it matters also to apply good LUSTRE settings beforehand as for container images). In this tutorial, we will not generate a lot of output, but it's a good practice to stick to anyways.

Finally, the `workdir` variable tells the container engine where to start working.
If we request a shell, this is where we will find ourselves dropped initially after starting the container.

### Set up a Python Virtual Environment

This will be the first time we run our modified container.
To run the container, we need allocate some compute resources using Slurm and launch a shell, just like we already did to build the container.
This time, we also use the `--environment` option to specify that we want to launch the shell inside the container specified by our gemma-pytorch EDF file:

```console
[clariden-lnXXX]$ cd $SCRATCH/tutorials/gemma-7b
[clariden-lnXXX]$ srun -A <ACCOUNT> \
  --environment=./ngc-pytorch-gemma-24.01.toml --pty bash
```

PyTorch is already setup in the container for us.
We can verify this by asking pip for a list of installed packages:

```console
user@nidYYYYYY$ python -m pip list | grep torch
pytorch-quantization      2.1.2
torch                     2.2.0a0+81ea7a4
torch-tensorrt            2.2.0a0
torchdata                 0.7.0a0
torchtext                 0.17.0a0
torchvision               0.17.0a0
```

However, we will need to install a few more Python packages to make it easier to do inference with Gemma-7B.
While it is best practice to install stable dependencies in the container image, we can maintain frequently changing packages in a virtual environment built on top of the container image.
The `--system-site-packages` option of the Python `venv` creation command ensures that we install packages _in addition_ to the existing packages and don't accidentally re-install a new version of PyTorch shadowing the one that has been put in place by Nvidia.
Next, we activate the environment and use pip to install the two packages we need, `accelerate` and `transformers`:

```console
user@nidYYYYYY$ python -m venv --system-site-packages venv-gemma-24.01
user@nidYYYYYY$ source venv-gemma-24.01/bin/activate
(venv-gemma-24.01) user@nidYYYYYY$ pip install \
  accelerate==0.30.1 transformers==4.38.1 huggingface_hub[cli]
# ... pip output ...
```

Before we move on to running the Gemma-7B model, we additionally need to make an account at [HuggingFace](https://huggingface.co), get an API token, and accept the [license agreement](https://huggingface.co/google/gemma-7b-it) for the [Gemma-7B](https://huggingface.co/google/gemma-7b) model. You can save the token to `$SCRATCH` using the huggingface-cli:

```console
(venv-gemma-24.01) user@nidYYYYYY$ export HF_HOME=$SCRATCH/huggingface
(venv-gemma-24.01) user@nidYYYYYY$ huggingface-cli login
```

At this point, you can exit the Slurm allocation again by typing `exit`.
If you `ls` the contents of the `gemma-inference` folder, you will see that the `venv-gemma-24.01` virtual environment folder persists outside of the Slurm job.

!!! note
    Keep in mind that
     
     * this virtual environment won't actually work unless you're running something from inside the PyTorch container.
    This is because the virtual environment ultimately relies on the resources packaged inside the container.
     * every Slurm job making use of this virtual environment will need to activate it first (_inside_ the `srun` command). 

Since [`HF_HOME`](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables#hfhome) will not only contain the API token, but also be the storage location for model, dataset and space caches of `huggingface_hub` (unless `HF_HUB_CACHE` is set), we also want to apply proper LUSTRE striping settings before it gets populated.

```console
[clariden-lnXXX]$ lfs setstripe -E 4M -c 1 -E 64M -c 4 -E -1 -c -1 -S 4M \
  $SCRATCH/huggingface
```

### Run Inference on Gemma-7B

Cool, now you have a working container with PyTorch and all the necessary Python packages installed! Let's move on to Gemma-7B.
We write a Python script to load the model and prompt it with some custom text.
The Python script should look like this:

```python title="$SCRATCH/tutorials/gemma-7b/gemma-inference.py"
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

All that remains is to run the python script inside the PyTorch container.
There are several ways of doing this.
As before, you could just use Slurm to get an interactive shell in the container.
Then you would source the virtual environment and run the Python script we just wrote.
There's nothing wrong with this approach per se, but consider that you might be running much more complex and lengthy Slurm jobs in the future.
You'll want to document how you're calling Slurm, what commands you're running on the shell, and you might not want to (or might not be able to) keep a terminal open for the length of time the job might take.
For this reason, it often makes sense to write a batch file, which enables you to document all these processes and run the Slurm job regardless of whether you're still connected to the cluster.

Create a Slurm batch file `submit-gemma-inference.sh`. It should look like this:

```bash title="$SCRATCH/tutorials/gemma-7b/submit-gemma-inference.sh"
#!/bin/bash
#SBATCH --account=<ACCOUNT>
#SBATCH --job-name=gemma-inference
#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=288
#SBATCH --output logs/slurm-%x-%j.out

export HF_HOME=$SCRATCH/huggingface
export TRANSFORMERS_VERBOSITY=info

cd $SCRATCH/tutorials/gemma-7b # (1)!

set -x

srun -ul --environment=./ngc-pytorch-gemma-24.01.toml bash -c "
    source venv-gemma-24.01/bin/activate
    python gemma-inference.py
"
```

1. Change directory if submitted with sbatch from a different directory

The first few lines of the batch script declare the shell we want to use to run this batch file and pass several options to the Slurm scheduler.
After this, we `cd` to our working directory and `srun` the command in our container environment that `source`s our virtual environment and finally runs our inference script.

The operations performed before the `srun` command resemble largely the operations performed on the login node above and, in fact, happen in the host environment. If you need to perform these steps in the container environment as well, you can alternatively use the `#SBATCH --environment=path/to/ngc-pytorch-gemma-24.01.toml` option _instead of_ using `--environment` with `srun`.

!!! warning "#SBATCH --environment"
    Use of the `--environment` option for `sbatch` is still considered experimental and could result in unexpected behavior. In particular, avoid mixing `#SBATCH --environment` and `srun --environment` in the same job.

    Use of `--environment` is currently only recommended for the `srun` command. 

Once you've finished editing the batch file, you can save it and run it with Slurm:

```console
[clariden-lnXXX]$ sbatch submit-gemma-inference.sh
```

This command should just finish without any output and return you to your terminal.
At this point, you can follow the output in your shell using `tail -f logs/slurm-gemma-inference-<job-id>.out`.
Besides you're free to do whatever you like; you can close the terminal, keep working, or just wait for the Slurm job to finish.
You can always check on the state of your job by logging back into the cluster and running `squeue -l --me`.
Once your job finishes, you will find a file in the same directory you ran it from, named something like `logs/slurm-gemma-inference-<job-id>.out`, and containing the output generated by your Slurm job.
For this tutorial, you should see something like the following:


```console
[clariden-lnXXX]$ cat logs/slurm-gemma-inference-543210.out
/capstor/scratch/cscs/user/gemma-inference/venv-gemma-24.01/lib/python3.10/site-packages/huggingface_hub/file_download.py:1132: FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
  warnings.warn(
Gemma's activation function should be approximate GeLU and not exact GeLU.
Changing the activation function to `gelu_pytorch_tanh`.if you want to use the legacy `gelu`, edit the `model.config` to set `hidden_activation=gelu`   instead of `hidden_act`. See https://github.com/huggingface/transformers/pull/29402 for more details.
Loading checkpoint shards: 100%|██████████| 4/4 [00:03<00:00,  1.13it/s]
/capstor/scratch/cscs/user/gemma-inference/venv-gemma-24.01/lib/python3.10/site-packages/huggingface_hub/file_download.py:1132: FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
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

Congrats! You've run Google Gemma-7B inference on four GH200 chips simultaneously.
Move on to the next tutorial or try the challenge.

!!! info "Collaborating in Git"

    In order to track and exchange your progress with colleagues, you can use standard `git` commands on the host, i.e. in the directory `$SCRATCH/tutorials/gemma-7b` run
    ```console
    [clariden-lnXXX]$ git init .
    [clariden-lnXXX]$ git remote add origin \
      git@github.com:<github-username>/alps-mlp-tutorials-gemma-7b.git # (1)!
    [clariden-lnXXX]$ ... # git add/commit
    ```

    1. Use any alternative Git hosting service instead of Github

    where you can replace `<github-username>` by the owner of the Github repository you want to push to.

    Note that for reproducibility, it is recommended to always track the Dockerfile, EDF and your application code alongside in a Git repository.


### Challenge

Using the same approach as in the latter half of step 4, use pip to install the package `nvitop`. This is a tool that shows you a concise real-time summary of GPU activity. Then, run Gemma and launch `nvitop` at the same time:

```console
(venv-gemma-24.01) user@nidYYYYYY$ python gemma-inference.py \
  > gemma-output.log 2>&1 & nvitop
```

Note the use of bash `> gemma-output.log 2>&1` to hide any output from Python.
Note also the use of the single ampersand `'&'` which backgrounds the first command in order to run `nvitop` exclusively in the foreground.

After a moment, you will see your Python script spawn on all four GPUs, after which the GPU activity will increase a bit and then go back to idle.
At this point, you can hit `q` to quite nvitop and you will find the output of your Python script in `gemma-output.log`.
