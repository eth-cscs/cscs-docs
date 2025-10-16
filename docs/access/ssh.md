[](){#ref-ssh}
# Using SSH

Before accessing CSCS clusters using SSH, first ensure that you have [created a user account][ref-account-management] that is part of a project that has access to the cluster, and have [multi factor authentication][ref-mfa] configured.

[](){#ref-ssh-service}
## Generating Keys with SSHService

It is not possible to authenticate with a username/password and user-created SSH keys.
Instead, it is necessary to use a certified SSH key created using the CSCS SSHService.

!!! note
    Keys are valid for 24 hours, after which a new key must be generated.

!!! warning
    The number of certified SSH keys is limited to **five per day**.
    Once you have reached this number you will not be able to generate new keys until at least one of these key expires or keys are revoked.

There are two methods for generating SSH keys using the SSHService, the [SSHService web app](https://sshservice.cscs.ch/) or by using a [command-line script](https://github.com/eth-cscs/sshservice-cli).

### Getting keys via the command line

On Linux and MacOS, the SSH keys can be generated and automatically installed using a command-line script.
This script is provided in pure Bash and in Python.
Python 3 is required together with packages listed in `requirements.txt` provided with the scripts.

!!! note
    We recommend to using a [virtual environment](https://user.cscs.ch/tools/interactive/python/#python-virtual-environments) for Python.

If this is the first time, download the ssh service from CSCS GitHub:

```bash
git clone https://github.com/eth-cscs/sshservice-cli
cd sshservice-cli
```

The next step is to use either the bash or python scripts:

=== "bash"
    Run the bash script in the `sshservice-cli` path:

    ```
    ./cscs-keygen.sh
    ```

=== "python"

    The first time you use the script, you can set up a python virtual environment with the dependencies installed:

    ```bash
    python3 -m venv mfa
    source mfa/bin/activate
    pip install -r requirements.txt
    ```

    Thereafter, activate the venv before using the script:

    ```bash
    source mfa/bin/activate
    python cscs-keygen.py
    ```

For both approaches, follow the on screen instructions that require you to enter your username, password and the six-digit OTP from the authenticator app on your phone.
The script generates the key pair (`cscs-key` and `cscs-key-cert.pub`) in your `~/.ssh` path:

```bash
> ls ~/.ssh/cscs-key*
/home/bobsmith/.ssh/cscs-key  /home/bobsmith/.ssh/cscs-key-cert.pub
```

### Getting keys via the web app

Access the SSHService web application by accessing the URL, [sshservice.cscs.ch](https://sshservice.cscs.ch).

1. Sign in with username, password and OTP
2. Select "Signed key" on the left tab and click on "Get a signed key"
3. On the next page a key pair is generated and ready to be downloaded. Download or copy/paste both keys.

Once generated, the keys need to be copied from where your browser downloaded them to your `~/.ssh` path, for example:
```bash
mv /download/location/cscs-key-cert.pub ~/.ssh/cscs-key-cert.pub
mv /download/location/cscs-key ~/.ssh/cscs-key
chmod 0600 ~/.ssh/cscs-key
```

### Adding a password to the key

Once the key has been generated using either the CLI or web interface above, it is strongly recommended that you add a password to the generated key using the [ssh-keygen](https://www.ssh.com/academy/ssh/keygen) tool.

```
ssh-keygen -f ~/.ssh/cscs-key -p
```

## Logging In

To ensure secure access, CSCS requires users to connect through the designated jump host Ela (`ela.cscs.ch`) before accessing any cluster.

Before trying to log into your target cluster, you can first check that the SSH key generated above can be used to access Ela:
```
ssh -i ~/.ssh/cscs-key ela.cscs.ch
```

To log into a target system at CSCS, you need to perform some additional setup to handle forwarding of SSH keys generated using the SSHService.
There are two alternatives detailed below.

[](){#ref-ssh-config}
### Adding Ela as a jump host in SSH Configuration

This approach configures Ela as a jump host and creates aliases for the systems that you want to access in `~/.ssh/config` on your laptop or PC.
The benefit of this approach is that once the `~/.ssh/config` file has been configured, no additional steps are required between creating a new key using MFA, and logging in.

Below is an example `~/.ssh/config` file that facilitates directly logging into the Daint, Santis and Clariden clusters using `ela.cscs.ch` as a Jump host:

```
Host ela
    HostName ela.cscs.ch
    User cscsusername
    IdentityFile ~/.ssh/cscs-key

Host daint
    HostName daint.alps.cscs.ch
    User cscsusername
    ProxyJump ela
    IdentityFile ~/.ssh/cscs-key
    IdentitiesOnly yes

Host santis
    HostName santis.alps.cscs.ch
    ProxyJump ela
    User cscsusername
    IdentityFile ~/.ssh/cscs-key
    IdentitiesOnly yes

Host clariden
    HostName clariden.alps.cscs.ch
    ProxyJump ela
    User cscsusername
    IdentityFile ~/.ssh/cscs-key
    IdentitiesOnly yes
```

!!! note ""
    :exclamation: Replace `cscsusername` with your CSCS username in the file above.

After saving this file, one can directly log into `daint.alps.cscs.ch` from your local system using the alias `daint`:

```
ssh daint
```

[](){#ref-ssh-agent}
### Using SSH Agent

Alternatively, the [SSH authentication agent](https://www.ssh.com/academy/ssh/add-command) can be configured to manage the keys.

Each time a new key is generated using the [SSHService][ref-ssh-service], add the key to the SSH agent:
```
ssh-add -t 1d ~/.ssh/cscs-key
```

??? warning "Could not open a connection to your authentication agent"
    If you see this error message, the ssh agent is not running.
    You can start it with the following command:
    ```
    eval $(ssh-agent)
    ```

Once the key has been configured, log into Ela using the `-A` flag, and then jump to the target system:
```bash
# log in to ela.cscs.ch
ssh -A cscsusername@ela.cscs.ch

# then jump to a cluster
ssh daint.cscs.ch
```

## SSH tunnel to a service on Alps compute nodes via ela

If you have a server listening on a compute node in an Alps cluster and want to reach it from your local computer, you can do the following: allocate a node, start your server bound to `localhost`, open an SSH tunnel that jumps through `ela` to the cluster, then use `http://localhost:PORT` locally.
Details on how to achieve this are below.

### Requirements
- SSH keys loaded in your agent (including MFA steps).
- Your CSCS username handy (replace `MYUSER` below).
- Know the compute node ID (e.g., `nid006554`) and the port of your running server.

### Allocate a node and run a server (or test server)
Tip: binding to `127.0.0.1` ensures the service is only reachable via your tunnel.

### Open the tunnel from your laptop
In a new local terminal:

```bash
MYUSER=cscsusername     # your username at CSCS
NODE=nid006554          # obtained from salloc or srun
PORT=6006               # example port
CLUSTER=daint           # cluster you want to reach

ssh -N -J ${MYUSER}@ela.cscs.ch,${MYUSER}@${CLUSTER}.alps.cscs.ch -L ${PORT}:localhost:${PORT}   ${MYUSER}@${NODE}
```
- First run may ask to trust the node’s host key — type `yes`.
- The command blocks while the tunnel is open (that is expected).

### Connect locally
With the service running and the tunnel open, you can now reach your service locally:

- Browser: `http://localhost:PORT`
- Terminal: `curl localhost:PORT`

### Clean up
- Stop the server (Ctrl-C on the compute node shell).
- End the Slurm allocation:
  ```bash
  scancel $SLURM_JOB_ID
  ```
- Close the tunnel (Ctrl-C in the tunnel terminal).

### Common troubleshooting (fast fixes)
- **Port already in use locally:** pick another `PORT` (e.g., 6007) in both server + tunnel.
- **Service not responding:** ensure the server binds to `127.0.0.1` and is running on the compute node; confirm `NODE` matches your allocation.
- **Auth prompts loop:** verify your SSH MFA to CSCS and the correct setup of the ssh agent.


[](){#ref-ssh-faq}
## Frequently encountered issues

??? warning "too many authentication failures"
    You may have too many keys in your ssh agent.
    Remove the unused keys from the agent or flush them all with the following command:
    ```bash
    ssh-add -D
    ```

??? warning "Permission denied"
    This might indicate that they key has expired.


??? warning "Could not open a connection to your authentication agent"
    If you see this error when adding keys to the ssh-agent, please make sure the agent is up, and if not bring up the agent using the following command:
    ```bash
    eval $(ssh-agent)
    ```

