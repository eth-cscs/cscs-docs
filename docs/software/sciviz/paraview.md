[](){#ref-uenv-paraview}
# ParaView

[ParaView](https://www.paraview.org/) is an open-source, multi-platform scientific data analysis and visualization tool that enables analysis and visualization of extremely large datasets. ParaView is both a general purpose, end-user application with a distributed architecture that can be seamlessly leveraged by your desktop or other remote parallel computing resources and an extensible framework with a collection of tools and libraries for various applications including scripting (using Python), web visualization (through trame and ParaViewWeb), or in situ analysis (with Catalyst).

!!! note "uenvs"

    [ParaView](https://www.paraview.org/) is provided on [ALPS][platforms-on-alps] via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.


## Running ParaView in batch mode with Python scripts

The following sbatch script can be used as a template.

=== "GH200"

    ```bash
    #SBATCH -N 1
    #SBATCH --ntasks-per-node=4
    #SBATCH --cpus-per-task=72
    #SBATCH --gpus-per-task=1
    #SBATCH -A <account>
    #SBATCH --uenv=paraview/5.13.2:v2 --view=paraview
    #SBATCH --hint=nomultithread

    export MPICH_GPU_SUPPORT_ENABLED=0

    srun --cpus-per-task=72 --cpu_bind=sockets /user-environment/ParaView-5.13/gpu_wrapper.sh /user-environment/ParaView-5.13/bin/pvbatch ParaViewPythonScript.py
    ```
    Current observation is that best performance is achieved using [one MPI rank per GPU][ref-slurm-gh200-single-rank-per-gpu]. How to run multiple ranks per GPU is described [here][ref-slurm-gh200-multi-rank-per-gpu].

=== "Eiger"

    ```bash
    #SBATCH -N 1
    #SBATCH --ntasks-per-node=128
    #SBATCH -A <account>
    #SBATCH --uenv=paraview/5.13.2:v2 --view=paraview
    #SBATCH --hint=nomultithread

    srun --cpus-per-task=128 /user-environment/ParaView-5.13/bin/pvbatch ParaViewPythonScript.py
    ```


## Using ParaView in client-server mode

A ParaView server can connect to a remote ParaView client installed on your desktop. Make sure to use the same version on both sides. Your local ParaView GUI client needs to create a SLURM job with appropriate parameters. We recommend that you make a copy of the file `/user-environment/ParaView-5.13/rc-submit-pvserver.sh` to your $HOME, such that you can further fine-tune it.

You will need to add the corresponding XML code to your local ParaView installation, such that the Connect menu entry recognizes the ALPS cluster. The following code would be added to your **local** `$HOME/.config/ParaView/servers.pvsc` file

!!! Example "XML code to add to your local ParaView settings"
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
    </Servers>
    ```
