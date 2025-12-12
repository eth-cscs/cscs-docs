[](){#ref-uenv-paraview}
# ParaView

!!! info ""
    Paraview is [supported software][ref-support-apps] on Alps.
    See the [main applications page][ref-software] for more information.

[ParaView](https://www.paraview.org/) is an open-source, multi-platform scientific data analysis and visualization tool, which enables analysis and visualization of extremely large datasets.

ParaView is both:

- a general purpose end-user application with a distributed architecture, that can be seamlessly leveraged by your desktop or other remote parallel computing resources, and
- an extensible framework with a collection of tools and libraries for various applications, including scripting (using Python), web visualization (through Trame and ParaViewWeb), and in situ analysis (with Catalyst).

ParaView is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv].

[](){#ref-paraview-one-time-setup}
## One-time setup

!!! warning "Before starting you should have already pulled a ParaView uenv (see [uenv quick-start guide][ref-uenv-quickstart])"

CSCS provides helper scripts that are very handy for launching live sessions and batch rendering.

To install these utilities, the simplest approach is to place them in a directory that is part of your `PATH`.
A common convention is to create a personal `~/bin` directory and add it to your `PATH`.

```bash
mkdir ~/bin && echo 'export PATH=~/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
uenv run paraview/6.0.1 -- cp -r /user-environment/helpers/. ~/bin
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
To do that, your local ParaView client needs to connect to a `pvserver` running on Alps compute nodes, which is started using a SLURM job with appropriate parameters.

It can be done manually each time, or ParaView can be configured to do that for you auto-magically. 🪄

### Connecting using an PVSC configuration file

A [ParaView Server Configuration (PVSC)](https://docs.paraview.org/en/latest/ReferenceManual/parallelDataVisualization.html#paraview-server-configuration-files) file is an XML file that contains one or more server configurations.

!!! note ""
    This is a very simple configuration that at each connection to Alps Daint it prompts you for:

    - [uenv image label][ref-uenv-labels] to use (it will be stored for next time)
    - SLURM arguments for the allocation (every time it proposes the default value)
    - TCP port to use for the reverse connection

    ```xml
    <Servers>
      <Server name="CSCS Alps Daint" resource="csrc://daint.cscs.ch:11111" timeout="-1">
        <CommandStartup>
          <Options>
            <Option name="UENV" label="ParaView uenv" save="true" readonly="false">
              <String default="paraview/6.0.1"/>
            </Option>
            <Option name="SLURM_ARGS" label="SLURM Arguments" readonly="false">
              <String default="-n4 -pdebug -t10"/>
            </Option>
            <Option name="PV_SERVER_PORT" label="Server Port" readonly="false">
              <Range type="int" min="11111" max="65535"/>
            </Option>
          </Options>
          <SSHCommand exec="paraview-reverse-connect" delay="0" process_wait="0">
            <SSHConfig>
              <PortForwarding/>
            </SSHConfig>
            <Arguments>
              <Argument value="$UENV$"/>
              <Argument value="$PV_SERVER_PORT$"/>
              <Argument value="$SLURM_ARGS$"/>
            </Arguments>
          </SSHCommand>
        </CommandStartup>
      </Server>
    </Servers>
    ```

    !!! tip
        You can use this as a starting point for more advanced setups and customizations.

        See the official documentation about [PVSC files](https://docs.paraview.org/en/latest/ReferenceManual/parallelDataVisualization.html#paraview-server-configuration-files) for examples and details.

An easy way to add a server configuration to your ParaView is to create it in a file with `*.pvsc` extension, and then load it in ParaView with **File → Connect... → Load Servers**.
This will add the configuration(s) provided to the list of available server proposed when you click on **File → Connect...**.

You can manipulate the list of server configurations from the dialog, and changes will be reflected (on ParaView UI exit) in a file called `servers.pvsc` in your ParaView user settings directory.

### A more advanced and versatile configuration

This is the most versatile way to configure ParaView client-server connection to Alps, as **it allows you to customize (any part of) the command directly from the ParaView UI**.

You can achieve the same exact results either by creating a PVSC file as described in the previous section with the following content:

```xml
<Servers>
  <Server name="CSCS Alps" resource="csrc://localhost:10111" timeout="-1">
    <CommandStartup>
      <Command process_wait="0" delay="0" exec="ssh">
        <Arguments>
          <Argument value="-R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$"/>
          <Argument value="daint.cscs.ch"/>
          <Argument value="--"/>
          <Argument value="paraview-reverse-connect"/>
          <Argument value="paraview/6.0.1"/>
          <Argument value="$PV_SERVER_PORT$"/>
          <Argument value="-n4 -pdebug --gpus-per-task=1"/>
        </Arguments>
      </Command>
    </CommandStartup>
  </Server>
</Servers>
```

Or by adding a new server configuration directly from the ParaView UI:

- **File → Connect... → Add Server**
- Specify a name for the configuration
- Select **Reverse Connection**
- Click on **Configure**
- Select **Startup Type: Command**

And type in the following command:

```bash
ssh -R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$ daint.cscs.ch -- paraview-reverse-connect paraview/6.0.1 $PV_SERVER_PORT$ -n4 -pdebug --gpus-per-task=1
```

#### Understanding and customizing the command

Let's dissect the command in order to fully understand it, so you can customize it for your needs.
In the command it is possible to identify two parts separated by "`--`":

- SSH connection
- ParaView server launch with `paraview-reverse-connect`

##### SSH connection

```bash
ssh -R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$ daint.cscs.ch
```

This first part runs locally on your workstation and specifies how to connect to Alps via SSH.

You should **use whatever SSH option you are normally using to connect to Alps**.
What's **important is having `-R $PV_SERVER_PORT$:localhost:$PV_SERVER_PORT$`**, which is responsible of forwarding the port specified in the GUI (if it is busy, you can try a different one) from your local workstation to Alps.

##### ParaView server launch with `paraview-reverse-connect`

```bash
paraview-reverse-connect paraview/6.0.1 $PV_SERVER_PORT$ -n4 -pdebug --gpus-per-task=1
```

The second part uses `paraview-reverse-connect` (see [how to obtain it][ref-paraview-one-time-setup]), which runs on the Alps login node to launch a SLURM job, that will execute ParaView `pvserver` instances on compute nodes, that will (reverse) connect with your ParaView UI on your workstation.

The first two arguments are required, and they are:

- the [uenv image label][ref-uenv-labels] and
- the port you are forwarding via SSH.

After them, it is possible to specify any srun option, giving you full control on the allocation request (e.g. time, partition).
