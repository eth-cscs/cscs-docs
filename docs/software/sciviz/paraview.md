[](){#ref-uenv-paraview}
# ParaView

!!! info ""
    Paraview is [supported software][ref-support-apps] on Alps.
    See the [main applications page][ref-software] for more information.

[ParaView](https://www.paraview.org/) is an open-source, multi-platform scientific data analysis and visualization tool, which enables analysis and visualization of extremely large datasets.

!!! note "[ParaView](https://www.paraview.org/) is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv]"
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

ParaView is both a general purpose, end-user application with a distributed architecture that can be seamlessly leveraged by your desktop or other remote parallel computing resources, and an extensible framework with a collection of tools and libraries for various applications including scripting (using Python), web visualization (through Trame and ParaViewWeb), or in situ analysis (with Catalyst).

[](){#ref-paraview-one-time-setup}
## One-time setup

!!! warning "Before starting you should have already pulled a ParaView uenv (see [uenv quick-start guide][ref-uenv-quickstart])"

CSCS provides helper scripts that are very handy for launching live sessions and batch rendering.

To install these utilities, the simplest approach is to place them in a directory that is part of your `PATH`.
A common convention is to create a personal `~/bin` directory and add it to your `PATH`.

```bash
mkdir ~/bin && echo 'export PATH=~/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
uv run paraview/6.0.1 -- cp /user-environment/helpers/. ~/bin
```

!!! info ""
    You can then test that helpers scripts are installed correctly

    ```console
    $ paraview-reverse-connect
    Usage: paraview-reverse-connect <uenv-label> <server-port> [<srun-option>]*
    ```

    ```console
    $ bind-gpu-vtk-egl
    Usage: bind-gpu-vtk-egl <cmd> [args...]
    This wrapper is supposed to be used in a SLURM job.
    ```

## Running ParaView in batch mode with Python scripts

The following sbatch script can be used as template for running ParaView in batch mode.

=== "GH200"

    !!! note
        Current observation is that best performance is achieved using [one MPI rank per GPU][ref-slurm-gh200-single-rank-per-gpu].
        How to run multiple ranks per GPU is described [here][ref-slurm-gh200-multi-rank-per-gpu].

    ```bash
    #SBATCH -N 1
    #SBATCH --ntasks-per-node=4
    #SBATCH --cpus-per-task=72
    #SBATCH --gpus-per-task=1
    #SBATCH -A <account>
    #SBATCH --uenv=paraview/6.0.1 --view=default
    #SBATCH --hint=nomultithread

    srun --cpus-per-task=72 bind-gpu-vtk-egl pvbatch your-paraview-python-script.py
    ```

=== "Eiger"

    ```bash
    #SBATCH -N 1
    #SBATCH --ntasks-per-node=128
    #SBATCH -A <account>
    #SBATCH --uenv=paraview/6.0.1 --view=default
    #SBATCH --hint=nomultithread

    srun --cpus-per-task=128 pvbatch your-paraview-python-script.py
    ```

## Using ParaView in client-server mode

!!! warning "Make sure to use the same version on both sides."

A ParaView server can connect to a remote ParaView client installed on your workstation.
To do that, your local ParaView client needs to connect to a `pvserver` on a compute node on Alps, which is started using a SLURM job with appropriate parameters.

It can be done manually each time, or ParaView can be configured to do that for you automagically. 🪄

### Create a *reverse-connection* Configuration

!!! note
    Once you create a configuration, you can always edit its port and its command.
    Or you can create a new one with a different preset.

The most simple and versatile way to reverse connect from Alps is to create a new configuration with the following steps:

- **File &rarr; Connect ... &rarr; Add Server**
- Specify a name for the configuration
- Select **Reverse Connection**
- Click on **Configure**
- Select **Startup Type: Command**
- Type the command (follows)

The command should look like this

```bash
ssh -R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$ daint.cscs.ch -- paraview-reverse-connect paraview/6.0.1 $PV_SERVER_PORT$ -N1 -n4 --gpus-per-task=1 -pdebug
```

Let's split it and understand the various parts, so you can customise it for your needs.

In the command it is possible to identify two sections separated by "`--`":

1. `ssh -R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$ daint.cscs.ch`
2. `paraview-reverse-connect paraview/6.0.1 $PV_SERVER_PORT$ -N1 -n4 --gpus-per-task=1 -pdebug`

The first part with `ssh` command runs locally on your workstation and specifies how to connect to Alps via SSH.
**You should use whatever option you are normally using to connect to Alps**.
What's **important is having** `-R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$`, which is responsible of forwarding the port specified in the GUI (if it is busy, you can try a different one) from your local workstation to Alps.

The latter `paraview-reverse-connect` command (see [how to obtain it][ref-paraview-one-time-setup]) runs on the Alps login node to start a SLURM job which will run ParaView `pvserver` instances on compute nodes, that will (reverse) connect with your ParaView UI on your workstation.
The two arguments are required, and they are the [uenv image label][ref-uenv-labels] and the port you are forwarding via SSH.
After them, it is possible to specify any srun option, giving full control on the allocation request (e.g. time, partition).

### GUI

You will need to add the corresponding XML code to your local ParaView installation, such that the Connect menu entry recognizes the ALPS cluster.
The following code would be added to your **local** `$HOME/.config/ParaView/servers.pvsc` file

??? Example "XML code to add to your local ParaView settings"
    ```xml
    <Servers>
      <Server name="Reverse-Connect-Daint.Alps" configuration="" resource="csrc://:11111" timeout="-1">
        <CommandStartup>
          <Options>
            <Option name="MACHINE" label="remote cluster" save="true">
              <String default="daint"/>
            </Option>
            <Option name="SSH_USER" label="SSH Username" save="true">
              <String default="your-userid"/>
            </Option>
            <Option name="ACCOUNT" label="Account to be charged" save="true">
              <String default="your-projectid"/>
            </Option>
            <Option name="RESERVATION" label="reservation name" save="true">
              <Enumeration default="none">
                <Entry value="" label="none"/>
              </Enumeration>
            </Option>
            <Option name="SSH_CMD" label="SSH command" save="true">
              <File default="/usr/bin/ssh"/>
            </Option>
            <Option name="REMOTESCRIPT" label="The remote script which generates the SLURM job" save="true">
              <String default="/users/your-userid/rc-submit-pvserver.sh"/>
            </Option>
            <Option name="PVNodes" label="Number of cluster nodes" save="true">
              <Range type="int" min="1" max="128" step="1" default="1"/>
            </Option>
            <Option name="PVTasks" label="Number of pvserver per node" save="true">
              <Range type="int" min="1" max="4" step="1" default="4"/>
            </Option>
            <Option name="Queue" label="Queue" save="true">
              <Enumeration default="normal">
                <Entry value="normal" label="normal"/>
                <Entry value="debug" label="debug"/>
              </Enumeration>
            </Option>
            <Option name="MemxNode" label="MemxNode" save="true">
              <Enumeration default="standard">
                <Entry value="high" label="high"/>
                <Entry value="standard" label="standard"/>
              </Enumeration>
            </Option>
            <Option name="VERSION" label="VERSION ?" save="true">
              <Enumeration default="5.13.2:v2">
                <Entry value="5.13.2:v2" label="5.13.2:v2"/>
              </Enumeration>
            </Option>
            <Option name="PV_SERVER_PORT" label="pvserver port" save="true">
              <Range type="int" min="1024" max="65535" step="1" default="1100"/>
            </Option>
            <Option name="NUMMIN" label="job wall time" save="true">
              <String default="00:29:59"/>
            </Option>
            <Option name="SESSIONID" label="Session id" save="true">
              <String default="ParaViewServer"/>
            </Option>
          </Options>
          <Command exec="$SSH_CMD$" delay="5" process_wait="0">
            <Arguments>
              <Argument value="-A"/>
              <Argument value="-l"/>
              <Argument value="$SSH_USER$"/>
              <Argument value="-R"/>
              <Argument value="$PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$"/>
              <Argument value="$MACHINE$"/>
              <Argument value="$REMOTESCRIPT$"/>
              <Argument value="$SESSIONID$"/>
              <Argument value="$NUMMIN$"/>
              <Argument value="$PVNodes$"/>
              <Argument value="$PVTasks$"/>
              <Argument value="$PV_SERVER_PORT$"/>
              <Argument value="$MACHINE$"/>
              <Argument value="$VERSION$"/>
              <Argument value="$Queue$"/>
              <Argument value="$MemxNode$"/>
              <Argument value="$ACCOUNT$"/>
              <Argument value="$RESERVATION$;"/>
              <Argument value="sleep"/>
              <Argument value="6000"/>
            </Arguments>
          </Command>
      </CommandStartup>
      </Server>
    </Servers>
    ```
