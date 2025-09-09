[](){#ref-gssr-containers}
# gssr - Containers Guide

The following guide will explain how to install and use `gssr` within a container.

Most CSCS users leverage on the base containers with pre-installed CUDA from Nvidia.
As such, in the following documentation, we will use a PyTorch base container as an example. 

## Preparing a container with `gssr`

### Base Container from Nvidia

The most commonly used Nvidia container used on Alps is the [Nvidia's PyTorch container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch). Typically the latest version is preferred for the most up-to-date functionalities of PyTorch.

#### Example: Preparing a Nvidia PyTorch ContainerFile  
```dockerfile
FROM --platform=linux/arm64 nvcr.io/nvidia/pytorch:25.08-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y wget rsync rclone vim git htop nvtop nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installing gssr
RUN pip install gssr

# Install your application and dependencies as required
...
```
As you can see from the above example, gssr can easily be installed with a `RUN pip install gssr` command. 

Once your `ContainerFile` is ready, you can build it on any Alps platforms with the following commands to create a container with label `mycontainer`.

```bash
srun -A {groupID} --pty bash
# Once you have an interactive session, use podman command to build the 
# container
# -v is to mount the fast storage on Alps into the container. 
podman build -v $SCRATCH:$SCRATCH -t mycontainer:0.1 .
# Export the container from the podman's cache to a local squashFS file with 
# enroot
enroot import -x mount -o mycontainer.sqsh podman://local:mycontainer:0.1
```

Now you should have a squashFS file of your container. Please note that you should replace `mycontainer` label to any other label of your choice. The version `0.1` can also be omitted or replaced with another version as required. 

## Create CSCS configuration for Container

The next step is to tell CSCS container engine solution where your container is and how you would like to run it. To do so, you will have to create a`{label}.toml` file in your `$HOME/.edf` directory.

### Example of a `mycontainer.toml` file
```
image = "/capstor/scratch/cscs/username/{yourDir}/mycontainer.sqsh"
mounts = ["/capstor/scratch/cscs/username:/capstor/scratch/cscs/username"]
workdir = "/capstor/scratch/cscs/username"
writable = true

[annotations]
com.hooks.dcgm.enabled = "true"
```

Please note that the `mounts` line is important if you want $SCRATCH to be available in your container. You can also mount a specific directory or file in $HOME and/or $SCRATCH as required. You should modify the username and the image directory as per your setup. 

To use `gssr` in a container, you will need the `dcgm` hook that is configured in the `[annotations]` section to enable DCGM libraries to be available within the container.

### Run the application and container with gssr

To invoke `gssr`, you can do the following in your sbatch file.

#### Example of a mycontainer.sbatch file
```
#!/bin/bash
#SBATCH -N4
#SBATCH -A groupname
#SBATCH -J mycontainer
#SBATCH -t 1:00:00
#SBATCH ...

srun --environment=mycontainer bash -c 'gssr --wrap="python abc.py"'

```

Please replace the text `...` for any other SBATCH configuration that your job requires.
The `--environment` flag tells Slurm which container (name of the toml file)  you would like to run. 
The `bash -c` requirement is to initialise the bash environment within your container.

If no `gssr` is used, the `srun` command in your container should like that.:

```
srun --environment=mycontainer bash -c 'python abc.py'.
```

Now you are ready to submit your sbatch file to slurm with `sbatch` command.

## Analyze the output

Once your job successfully concluded, you should find a folder named `profile_out_{slurm_jobid}` where `gssr` json outputs are in.

To analyze the outputs, you can do so interactively within any containers where `gssr` is installed, e.g., `mycontainer` we have in this guide.

To get an interactive session of this container:

```
srun -A groupname --environment=mycontainer --pty bash
cd {directory where the gssr output data is generated}
```
Alternatively, you can install `gssr` locally and copy the `profile_out_{slurm_jobid}` to your computer and visualize it locally.

#### Metric Output
The profiled output can be analysed as follows.:

    gssr analyze -i ./profile_out

#### PDF File Output with Plots

    gssr analyze -i ./profile_out --report

A/Multiple PDF report(s) will be generated.

