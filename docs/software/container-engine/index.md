[](){#ref-container-engine}
# Container Engine

The Container Engine (CE) toolset is designed to enable computing jobs to seamlessly run inside Linux application containers, thus providing support for containerized user environments.

## Concept

Containers effectively encapsulate a software stack; however, to be useful in HPC computing environments, they often require the customization of bind mounts, environment variables, working directories, hooks, plugins, etc. 
To simplify this process, the Container Engine (CE) toolset supports the specification of user environments through Environment Definition Files.

An Environment Definition File (EDF) is a text file in the [TOML format](https://toml.io/en/) that declaratively and prescriptively represents the creation of a computing environment based on a container image.
Users can create their own custom environments and share, edit, or build upon already existing environments.

The Container Engine (CE) toolset leverages its tight integration with the Slurm workload manager to parse Fs directly from the command line or batch script and instantiate containerized user environments seamlessly and transparently.

Through the EDF, container use cases can be abstracted to the point where end users perform their workflows as if they were operating natively on the computing system.

## Benefits

 * *Freedom*: Container gives users full control of the user space. The user can decide what to install without involving a sysadmin.
 * *Reproducibility*: Workloads consistently run in the same environment, ensuring uniformity across job experimental runs.
 * *Portability*: The self-contained nature of containers simplifies the deployment across architecture-compatible HPC systems.
 * *Seamless Access to HPC Resources*: CE facilitates native access to specialized HPC resources like GPUs, interconnects, and other system-specific tools crucial for performance.

## Quick Start

Let's set up a containerized Ubuntu 24.04 environment on the scratch folder (`${SCRATCH}`).

### Step 1. Create an environment 

Save this file below as `ubuntu.toml` in `${HOME}/.edf` directory (the default location of EDF files).
Create `${HOME}/.edf` if the folder doesn't exist.
A more detailed explanation of each entry for the EDF can be seen in the [EDF reference][ref-ce-edf-reference].

```toml
image = "library/ubuntu:24.04"
mounts = ["/capstor/scratch/cscs/${USER}:/capstor/scratch/cscs/${USER}"]
workdir = "/capstor/scratch/cscs/${USER}"
```

### Step 2. Launch a program 

Use Slurm on the login node to launch a program inside the environment.
Notice that the environment (EDF) is specified with the `--environment` option. 
CE pulls the image automatically when the container starts.

```console
$ srun --environment=ubuntu echo "Hello" 
Hello
```

Or, use `--pty` to directly enter the environment.

```console
$ srun --environment=ubuntu --pty bash
[compute-node]$ 
```

!!! Example "Entering the environment on Daint"
    ```console
    [daint-ln002]$ srun --environment=ubuntu --pty bash   # (1)

    [nid005333]$ pwd                                      # (2)
    /capstor/scratch/cscs/<username>

    [nid005333]$ cat /etc/os-release                      # (3)
    PRETTY_NAME="Ubuntu 24.04 LTS"
    NAME="Ubuntu"
    VERSION_ID="24.04"
    ...

    [nid005333]$ exit                                     # (4)
    [daint-ln002]$
    ```

    1.  Starting an interactive shell session within the Ubuntu 24.04 container deployed on a compute node using `srun --environment=ubuntu --pty bash`.
    2.  Check the current folder (dubbed _the working directory_) is set to the user's scratch folder, as per EDF.
    3.  Show the OS version of your container (using `cat /etc/os-release`) based on Ubuntu 24.04 LTS.
    4.  Exiting the container (`exit`), returning to the login node.
