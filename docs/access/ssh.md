[](){#ref-ssh}
# Using SSH

Before accessing CSCS clusters using SSH, first ensure that you have [created a user account][ref-account-management] that is part of a project that has access to the cluster, and have [multi factor authentication][ref-mfa] configured.

## SSH key management overview

Username+password authentication is not available for SSH access.
Instead, you must use SSH keys signed by CSCS.
The recommended approach is to generate the SSH key locally and then have it signed by CSCS.

Two methods are available for managing SSH keys:

- **Command-line app** `cscs-key`
- **Web Dashboard**  [user-account.cscs.ch](https://user-account.cscs.ch)

[](){#ref-ssh-cli}
## Command-line access

The CLI interface to the SSH service is called `cscs-key`, an open source tool developed by CSCS to simplify managing keys.

### Installation

To install `cscs-key`, use Homebrew on macOS or Linux, or download a release binary from the [GitHub releases page](https://github.com/eth-cscs/cscs-key/releases) on any platform.
For a manual install, unpack the archive and place the binary in a directory on your `PATH` (`$HOME/.local/bin` on macOS/Linux, `$HOME\bin` on Windows).
The snippets below set `TAG=v1.1.0` — replace it with the [latest release tag](https://github.com/eth-cscs/cscs-key/releases).
On Windows, choose the PowerShell tab for the native binary, or the Linux tab when running inside [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

=== "Homebrew (macOS, Linux)"
    ```console title="install cscs-key from Homebrew"
    $ brew install eth-cscs/tap/cscs-key
    $ cscs-key --version
    cscs-key 1.1.0
    ```

=== "macOS (Apple Silicon)"
    ```console title="install cscs-key on Apple Silicon Mac"
    $ TAG=v1.1.0
    $ mkdir -p $HOME/.local/bin
    $ cd $HOME/.local/bin
    $ curl -LO https://github.com/eth-cscs/cscs-key/releases/download/$TAG/cscs-key-$TAG-aarch64-apple-darwin.tar.gz
    $ tar -xzvf cscs-key-$TAG-aarch64-apple-darwin.tar.gz
    $ rm cscs-key-$TAG-aarch64-apple-darwin.tar.gz
    $ cscs-key --version
    cscs-key 1.1.0
    ```

=== "Linux (x86_64)"
    ```console title="install cscs-key on x86_64 Linux"
    $ TAG=v1.1.0
    $ mkdir -p $HOME/.local/bin
    $ cd $HOME/.local/bin
    $ curl -LO https://github.com/eth-cscs/cscs-key/releases/download/$TAG/cscs-key-$TAG-x86_64-unknown-linux-musl.tar.gz
    $ tar -xzvf cscs-key-$TAG-x86_64-unknown-linux-musl.tar.gz
    $ rm cscs-key-$TAG-x86_64-unknown-linux-musl.tar.gz
    $ cscs-key --version
    cscs-key 1.1.0
    ```

=== "Windows (x86_64, PowerShell)"
    ```pwsh-session title="install cscs-key on Windows"
    PS> $TAG = "v1.1.0"
    PS> mkdir $HOME\bin -Force
    PS> cd $HOME\bin
    PS> curl.exe -LO "https://github.com/eth-cscs/cscs-key/releases/download/$TAG/cscs-key-$TAG-x86_64-pc-windows-msvc.zip"
    PS> Expand-Archive -Path "cscs-key-$TAG-x86_64-pc-windows-msvc.zip" -DestinationPath .
    PS> Remove-Item "cscs-key-$TAG-x86_64-pc-windows-msvc.zip"
    PS> cscs-key --version
    cscs-key 1.1.0
    ```

The final `cscs-key --version` step prints the version when the install worked.
If it instead reports that `cscs-key` cannot be found, the install directory is not on your shell's `PATH`.
Add it once with the snippet below, then open a new terminal and try again.

??? note "Add the install directory to your `PATH`"
    === "Zsh"
        ```bash title="add ~/.local/bin to PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        ```

    === "Bash"
        ```bash title="add ~/.local/bin to PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        ```

    === "PowerShell"
        ```powershell title="add $HOME\bin to PATH for the current user"
        $userPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
        [Environment]::SetEnvironmentVariable('PATH', "$userPath;$HOME\bin", 'User')
        ```

You can also build it from source by cloning the git repository and following the instructions in the README.

### Setup SSH keys

First, generate the key pair using [`ssh-keygen`](https://www.ssh.com/academy/ssh/keygen).

```bash
ssh-keygen -t ed25519 -f ~/.ssh/cscs-key
```
!!! note
    The key only needs to be generated once, and does not need to be run every time your signed key expires.

And add this key to your [SSH config](#ref-ssh-config) or add it to your [SSH agent](#ref-ssh-agent).

### Usage

To see all available commands run:

```console
$ cscs-key --help
```

To sign an existing public key:
```console
$ cscs-key sign
```
The default private key is `~/.ssh/cscs-key`.
You can specify a different private key using the `-f, --file` option.
The default duration of the signed key is 1 day.
You can specify a different duration using the `-d, --duration` option.
Possible values are `1d` or `1min`.

??? note "generate a new key pair (deprecated)"
    !!! warning
        Generating the SSH key on the server is deprecated and will be removed in the future.

    It is possible to generate the SSH key locally and then sign it using the cscs-key sign command.
    ```console
    cscs-key gen
    ```
    The default private key is `~/.ssh/cscs-key`.
    You can specify a different private key using the `-f, --file` option.
    The default duration of the signed key is 1 day.
    You can specify a different duration using the `-d, --duration` option.
    Possible values are `1d` or `1min`.

The `cscs-key` command can be used to summarise the status of all of your signed SSH keys:
```console
$ cscs-key list
╭────────────────────┬──────────┬────────────┬────────────────────────────╮
│ Serial Number      │ Valid    │ Expiration │ Expire Time                │
╞════════════════════╪══════════╪════════════╪════════════════════════════╡
│ 202800351141013664 │ ✅ VALID │ in a day   │ 2026-04-01 16:15:20 +02:00 │
├────────────────────┼──────────┼────────────┼────────────────────────────┤
│ 202344484062892129 │ ✅ VALID │ in a day   │ 2026-04-01 16:09:12 +02:00 │
╰────────────────────┴──────────┴────────────┴────────────────────────────╯
```

The `-a, --all` flag will also include expired and revoked keys in the output of `cscs-key list`.

Keys can be revoked using the serial number, which can be found using the `cscs-key list` command above.
```console
$ cscs-key revoke 202800351141013664
202800351141013664: ✅ Key revoked successfully
```
Use `-a, --all` option to revoke all valid keys.

For more details about any command please refer to help with `-h, --help`.

!!! note
    The app supports three authentication methods:

    - **OpenID Connect**: Web browser window opens where user authenticates with the CSCS credentials.
    - **OAuth2 Device Authorization Grant** for remote headless machines, enabled by `--headless` flag.
    - **API keys**: For automation with service accounts. See [Service Accounts][ref-service-accounts] for details.

### Shell completion

To enable completion on every shell start, add to your shell config (e.g. `~/.bashrc`):

```bash
source <(cscs-key completion <shell>)
```

Supported shells: `bash`, `zsh`, `fish`, `powershell`, `elvish`.

[](){#ref-ssh-key-management}
## Managing SSH keys at user-account.cscs.ch

The centralized key management dashboard at [user-account.cscs.ch](https://user-account.cscs.ch) allows you to generate, sign, list, and revoke SSH keys in your browser.

!!! info
    The dashboard is an alternative to the `cscs-key` command line tool.
    If you are comfortable using `cscs-key` we recommend sticking to that interface.

### Sign your existing SSH key

The recommended approach is to upload your existing SSH public key to be signed by CSCS.
This avoids transferring private keys over the network and follows security best practices.

1. Access [user-account.cscs.ch](https://user-account.cscs.ch) and log in with your CSCS credentials
2. Navigate to **SSH Keys** and select **Sign Key**
3. Paste your existing SSH public key (e.g., from `~/.ssh/id_ed25519.pub` or `~/.ssh/id_rsa.pub`)
4. Click **Sign Key** — CSCS will issue a signed certificate
5. Download the signed certificate (`~/.ssh/cscs-key-cert.pub`)
6. Your original private key remains on your machine

!!! info "Advantages"
    - Private key never leaves your machine
    - Use your existing SSH key infrastructure
    - Works with any SSH key type (RSA, ED25519, ECDSA)
    - Recommended for security

??? info "Generate a new key pair (deprecated)"
    If you don't have an SSH key, CSCS can generate one for you.
    This method is currently supported but will be phased out in favor of signing existing keys.

    Steps:

    1. Access [user-account.cscs.ch](https://user-account.cscs.ch) and log in with your CSCS credentials
    2. Navigate to **SSH Keys** and select **Generate Key**
    3. Optionally add a passphrase for additional security
    4. Click **Generate** — CSCS creates and downloads a new key pair
    5. Save the private key (`cscs-key`) to `~/.ssh/` with restricted permissions:
       ```bash
       chmod 0600 ~/.ssh/cscs-key
       ```

    **Note:** This method transfers the private key over HTTPS which should be avoided.

### Key validity and limits

!!! note
    - **Validity**: Keys are valid for 1 day by default
    - **Renewal**: Generate or sign a new key when needed for continued access
    - **Limit**: You can create up to 5 keys per day

## Logging in

To ensure secure access, CSCS requires users to connect through the designated jump host Ela (`ela.cscs.ch`) before accessing any cluster.

Before trying to log into your target cluster, you can first check that your SSH key works with Ela:
```
ssh -i ~/.ssh/cscs-key ela.cscs.ch
```

To log into a target system at CSCS, you need to perform some additional setup to handle SSH key forwarding.
There are two alternatives detailed below.

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
    If you see this error message, the SSH agent is not running.
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

1. Access [user-account.cscs.ch](https://user-account.cscs.ch) and log in
2. Navigate to **SSH Keys** to view your active keys
3. Click the **Revoke** button next to the key you want to revoke
4. Confirm the revocation

### Revoke via CLI

To revoke a key using the command-line interface:

```bash
# Revoke a single key by serial number
cscs-key revoke --serial <serial-number>

# Revoke all active keys
cscs-key revoke-all
```

The revocation takes effect immediately across all CSCS systems.

[](){#ref-ssh-known-issues}
## Known issues

??? warning "too many authentication failures"
    You may have too many keys in your SSH agent.
    Remove the unused keys from the agent or flush them all with the following command:
    ```bash
    ssh-add -D
    ```

??? warning "Permission denied"
    This might indicate that your key has expired or is not valid.
    Check the validity of your key at [user-account.cscs.ch](https://user-account.cscs.ch).
    If expired, sign or generate a new key.

??? warning "Could not open a connection to your authentication agent"
    If you see this error when adding keys to the ssh-agent, please make sure the agent is up, and if not bring up the agent using the following command:
    ```bash
    eval $(ssh-agent)
    ```

[](){#ref-ssh-legacy}
## Legacy: old SSH key management

!!! warning "Retired from Q2 2026"
    The old SSHService ([sshservice.cscs.ch](https://sshservice.cscs.ch)) and the associated command-line script have been retired starting Q2 2026.
    All users must use the [new key management dashboard](#ref-ssh-key-management) or [CLI](#ref-ssh-cli).

