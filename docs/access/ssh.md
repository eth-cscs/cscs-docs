[](){#ref-ssh}
# Using SSH

Before accessing CSCS clusters using SSH, first ensure that you have [created a user account][ref-account-management] that is part of a project that has access to the cluster, and have [multi factor authentication][ref-mfa] configured.

## SSH key management overview

Username/password authentication is not available for SSH access. Instead, you must use SSH keys signed by the CSCS infrastructure. The recommended approach is to use your existing SSH key and have it signed by CSCS.

Two methods are available for managing SSH keys:
- **Web Dashboard** (recommended for most users) — [account.cscs.ch](https://account.cscs.ch)
- **Command-line Interface** (for automation and scripting)

[](){#ref-ssh-key-management}
## Managing SSH keys at account.cscs.ch

The centralized key management dashboard at [account.cscs.ch](https://account.cscs.ch) allows you to generate, sign, list, and revoke SSH keys.

### Recommended: sign your existing SSH key

The recommended approach is to upload your existing SSH public key to be signed by CSCS. This avoids transferring private keys over the network and follows security best practices.

**Steps:**

1. Access [account.cscs.ch](https://account.cscs.ch) and log in with your CSCS credentials
2. Navigate to **SSH Keys** and select **Sign Key**
3. Paste your existing SSH public key (e.g., from `~/.ssh/id_ed25519.pub` or `~/.ssh/id_rsa.pub`)
4. Click **Sign Key** — CSCS will issue a signed certificate
5. Download the signed certificate (`~/.ssh/cscs-key-cert.pub`)
6. Your original private key remains on your machine

[Screenshot: account.cscs.ch SSH Keys page]

!!! info "Advantages"
    - Private key never leaves your machine
    - Use your existing SSH key infrastructure
    - Works with any SSH key type (RSA, ED25519, ECDSA)
    - Recommended for security

### Supported: generate a new key pair

If you don't have an SSH key, CSCS can generate one for you. This method is currently supported but will be phased out in favor of signing existing keys.

**Steps:**

1. Access [account.cscs.ch](https://account.cscs.ch) and log in with your CSCS credentials
2. Navigate to **SSH Keys** and select **Generate Key**
3. Optionally add a passphrase for additional security
4. Click **Generate** — CSCS creates and downloads a new key pair
5. Save the private key (`cscs-key`) to `~/.ssh/` with restricted permissions:
   ```bash
   chmod 0600 ~/.ssh/cscs-key
   ```

[Screenshot: account.cscs.ch Generate Key page]

**Note:** This method transfers the private key over HTTPS. Key generation will be phased out in favor of signing existing keys.

### Key validity and limits

!!! note
    - **Validity**: Keys are valid for 1 day by default
    - **Renewal**: Generate or sign a new key when needed for continued access
    - **Limit**: You can create up to 5 keys per day

[](){#ref-ssh-cli}
## Command-line access

The `cscs-key` CLI tool provides programmatic access to SSH key management for automation and scripting.

### Installation and setup

Visit the [cscs-key repository](https://github.com/rjanalik/cscs-key) for installation instructions and detailed documentation.

The CLI supports two authentication methods:

- **Browser session integration** — automatically uses your browser's Keycloak session
- **API keys** — for automation with service accounts

### Basic usage

Run `cscs-key --help` to see all available commands:

```bash
$ cscs-key --help
```

**Common commands:**

Sign an existing public key:
```bash
cscs-key sign --public-key ~/.ssh/id_ed25519.pub
```

Generate a new key pair:
```bash
cscs-key generate --output ~/.ssh/cscs-key
```

List your SSH keys:
```bash
cscs-key list
```

Revoke a key by serial number:
```bash
cscs-key revoke --serial <serial-number>
```

For more details and examples, refer to the [cscs-key documentation](https://github.com/rjanalik/cscs-key).

## Logging in

To ensure secure access, CSCS requires users to connect through the designated jump host Ela (`ela.cscs.ch`) before accessing any cluster.

Before trying to log into your target cluster, you can first check that your SSH key works with Ela:
```
ssh -i ~/.ssh/cscs-key ela.cscs.ch
```

To log into a target system at CSCS, you need to perform some additional setup to handle SSH key forwarding. There are two alternatives detailed below.

[](){#ref-ssh-config}
### Adding Ela as a jump host in SSH configuration

This approach configures Ela as a jump host and creates aliases for the systems that you want to access in `~/.ssh/config` on your laptop or PC.
The benefit of this approach is that once the `~/.ssh/config` file has been configured, no additional steps are required between creating or signing a new key, and logging in.

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
### Using SSH agent

Alternatively, the [SSH authentication agent](https://www.ssh.com/academy/ssh/add-command) can be configured to manage the keys.

When using signed keys or newly generated keys, add the private key to the SSH agent:
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

## SSH tunnel to a service on Alps compute nodes via Ela

If you have a server listening on a compute node in an Alps cluster and want to reach it from your local computer, you can do the following: allocate a node, start your server bound to `localhost`, open an SSH tunnel that jumps through `ela` to the cluster, then use `http://localhost:PORT` locally.
Details on how to achieve this are below.

Before starting, make sure you:

- [Have SSH keys loaded in your agent][ref-ssh-agent].
- Have your CSCS username handy (replace `MYUSER` below).
- Have your server running on a compute node on Alps.
  See the [Slurm documentation][ref-slurm] for help on how to allocate a node and start your server on a compute node.
- Know the compute node ID (e.g., `nid006554`) and the port of your running server.

!!! warning "Fast fixes when starting a server or before tunneling"
    - Port already in use locally: pick another PORT (e.g., 6007) in both your server and the tunnel command below.
    - Auth prompts loop: verify your SSH MFA to CSCS and that your SSH agent is correctly set up and loaded with your keys.

!!! tip "Binding to `127.0.0.1` ensures the service is only reachable via your tunnel"

To open the tunnel from your local computer:

```bash
MYUSER=cscsusername     # your username at CSCS
NODE=nid006554          # obtained from salloc or srun
PORT=6006               # example port
CLUSTER=daint           # cluster you want to reach

ssh -N -J ${MYUSER}@ela.cscs.ch,${MYUSER}@${CLUSTER}.alps.cscs.ch -L ${PORT}:localhost:${PORT} ${MYUSER}@${NODE}
```

The command blocks while the tunnel is open (that is expected).

!!! info "The first run may ask to trust the node's host key---type `yes`"

With the service running and the tunnel open, you can now reach your service locally:

- Browser: `http://localhost:PORT`
- Terminal: `curl localhost:PORT`

!!! warning "Fast fix if the service doesn't respond locally"
    - Service not responding: ensure the server binds to 127.0.0.1 and is running on the compute node; confirm NODE matches your current Slurm allocation.

To clean up afterwards:

- Stop the server (Ctrl-C on the compute node shell).
- End the Slurm allocation:
  ```bash
  scancel $SLURM_JOB_ID
  ```
- Close the tunnel (Ctrl-C in the tunnel terminal).

[](){#ref-ssh-revoke}
## Revoking SSH keys

You can revoke SSH keys when they are no longer needed or if compromised.

### Revoke via web dashboard

1. Access [account.cscs.ch](https://account.cscs.ch) and log in
2. Navigate to **SSH Keys** to view your active keys
3. Click the **Revoke** button next to the key you want to revoke
4. Confirm the revocation

[Screenshot: account.cscs.ch Revoke Key action]

### Revoke via CLI

To revoke a key using the command-line interface:

```bash
# Revoke a single key by serial number
cscs-key revoke --serial <serial-number>

# Revoke all active keys
cscs-key revoke-all
```

The revocation takes effect immediately across all CSCS systems.

[](){#ref-ssh-faq}
## Frequently encountered issues

??? warning "too many authentication failures"
    You may have too many keys in your ssh agent.
    Remove the unused keys from the agent or flush them all with the following command:
    ```bash
    ssh-add -D
    ```

??? warning "Permission denied"
    This might indicate that your key has expired or is not valid.
    Check the validity of your key at [account.cscs.ch](https://account.cscs.ch).
    If expired, sign or generate a new key.

??? warning "Could not open a connection to your authentication agent"
    If you see this error when adding keys to the ssh-agent, please make sure the agent is up, and if not bring up the agent using the following command:
    ```bash
    eval $(ssh-agent)
    ```

??? question "How long are SSH keys valid?"
    SSH keys are valid for 1 day by default. You will need to generate or sign a new key after it expires.

??? question "How do I use my own SSH key?"
    The recommended approach is to sign your existing SSH key using the dashboard or CLI. This allows you to use your own key infrastructure without transferring private keys over the network.

[](){#ref-ssh-legacy}
## Legacy: old SSH key management (deprecated)

!!! warning "⚠️ Deprecated — Migrate by Q2 2026"
    The old SSHService method described below is **deprecated**. All users should migrate to the [new key management dashboard](#ref-ssh-key-management) or [CLI](#ref-ssh-cli) by **Q2 2026**.

    The old method will no longer be available after Q2 2026.

### Generating keys with SSHService (old method)

The previous approach used the [SSHService web app](https://sshservice.cscs.ch/) or a [command-line script](https://github.com/eth-cscs/sshservice-cli).

#### Getting keys via the command line (old)

On Linux and MacOS, SSH keys could be generated and automatically installed using a command-line script.
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

#### Getting keys via the web app (old)

Access the old SSHService web application by accessing [sshservice.cscs.ch](https://sshservice.cscs.ch).

1. Sign in with username, password and OTP
2. Select "Signed key" on the left tab and click on "Get a signed key"
3. On the next page a key pair is generated and ready to be downloaded. Download or copy/paste both keys.

Once generated, the keys need to be copied from where your browser downloaded them to your `~/.ssh` path, for example:
```bash
mv /download/location/cscs-key-cert.pub ~/.ssh/cscs-key-cert.pub
mv /download/location/cscs-key ~/.ssh/cscs-key
chmod 0600 ~/.ssh/cscs-key
```

### Adding a password to the key (old method)

Once the key has been generated using either the old CLI or web interface above, it is strongly recommended that you add a password to the generated key using the [ssh-keygen](https://www.ssh.com/academy/ssh/keygen) tool.

```
ssh-keygen -f ~/.ssh/cscs-key -p
```

### Migration notes

To migrate from the old SSHService to the new system:

1. **Keep your existing private key** (`~/.ssh/cscs-key`)
2. **Extract the public key**: `ssh-keygen -y -f ~/.ssh/cscs-key > ~/.ssh/cscs-key.pub`
3. **Sign it with the new system**: Use [account.cscs.ch](https://account.cscs.ch) to sign `cscs-key.pub`
4. **Test access** before March 31, 2026
5. **Q2 2026**: Old SSHService will be retired

