[](){#access-ssh}
# Using SSH

Before accessing CSCS clusters using SSH, first ensure that you have [created a user account][account-management] that is part of a project that has access to the cluster, and have [multi factor authentification][mfa] configured.

It is not possible to authenticate with a username/password and user-created SSH keys: it is necessary to use a certified SSH key created using the CSCS SSHService, which is documented below.

!!! note
    Keys are valid for 24 hours, after which a new key must be generated.

!!! warning
    The number of certified SSH keys is limited to **five per day**.
    Once you have reached this number you will not be able to generate new keys until at least one of these key expires or keys are revoked.

## Generating Keys with SSHService

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

    Therafter, activate the venv before using the script:

    ```bash
    source mfa/bin/activate
    python cscs-keygen.py
    ```

For both approaches, follow the on screen instructions that require you to enter your username, password and the six-digit OTP from the authentifactor app on your phone.
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

## Logging in with the generated keys

Set up a passphrase on the private key:
```
ssh-keygen -f ~/.ssh/cscs-key -p
```

Add the key to the SSH agent:
```
ssh-add -t 1d ~/.ssh/cscs-key
```

??? warning "Could not open a connection to your authentification agent"
    If you see this error message, the ssh agent is not running.
    You can start it with the following command:
    ```
    eval $(ssh-agent)
    ```

Once the key has been configured, you can log in to CSCS' login system Ela:
```bash
# log in to ela.cscs.ch
> ssh -A cscs_username@ela.cscs.ch

# then jump to a cluster
> ssh clariden
```

### Set up SSH Config

To simplify logging in, you can edit (or create) the SSH configuration file `$HOME/.ssh/config` on your laptop or PC.
A simple configuration for that simplifies logging into [Clariden][clariden] is:

```
Host ela
    HostName ela.cscs.ch
    ForwardAgent yes
    # replace with your CSCS username
    User username

Host clariden
    HostName clariden.alps.cscs.ch
    ProxyJump ela
    # replace with your CSCS username
    User username

Host daint
    HostName daint.alps.cscs.ch
    ProxyJump ela
    # replace with your CSCS username
    User username
```

With this configuration, you can log into Clariden directly using the name clariden that was defined in `Host clariden`.

```bash
ssh clariden
```

## Frequently encountered issues

??? warning "too many authentification failures"
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

