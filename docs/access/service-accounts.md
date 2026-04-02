[](){#ref-service-accounts}
# Service Accounts

Service Accounts allow users to integrate CI/CD pipelines with HPC systems managed by CSCS. They provide programmatic, non-interactive access to project resources, making them suitable for automated workflows and pipeline authentication.

## Requesting a Service Account

Service Accounts are scoped to a **single project** and grant access to all resources within it. To obtain one, the **Project PI** must submit a request to a **Platform Manager** via an SD Ticket on the Service Desk.

Once approved and enabled, the **Service accounts** menu entry will appear under the **Team** tab of your project.

## Creating a Service Account

1. Navigate to your project's **Members** tab.
2. Click on **Service Account**.
3. Follow the prompts to create a new Service Account.

!!! note "Important"
    Upon creation, an API Key will be shown **only once**. Copy and store it securely immediately, as it cannot be retrieved later. If lost, a new Service Account must be created.

### Quick Key Generation with `cscs-key`

Once you have your API Key, you can use the `cscs-key` tool to generate a short-lived key directly:

```bash
CSCS_API_KEY=<YOUR_API_KEY> cscs-key sign --duration 1min
```

!!! warning "Be careful about setting environment variables"
    The presence of `CSCS_API_KEY` will override the default OIDC authentication method in `cscs-key`. This can be a security risk if not handled carefully. For example, if you set `CSCS_API_KEY` in your `.bashrc`, you will not be able to use `cscs-key` for your personal use.

## Authentication Flow

Cluster access requires two API calls: first to obtain a **JWT Token** from your API Key, then to obtain an **SSH Key Pair** (or just a certificate) from the JWT Token.

```
API Key  ->  JWT Token  ->  SSH Key Pair / Certificate  ->  Cluster Login
```

### Step 1 - Request a JWT Token

```bash
JWT_RESPONSE=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-service-account/api/v1/auth/token" \
  -H "X-API-Key: $CSCS_API_KEY")

JWT_TOKEN=$(echo "$JWT_RESPONSE" | jq -r '.access_token')
```

### Step 2 - Request Only an SSH Certificate (Recommended)

If you already have an existing SSH key pair, you can request only a signed certificate. This is the preferred approach when the environment can be configured accordingly, as it avoids generating new private keys on every authentication.

```bash
GENERATE=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-ssh-service/api/v1/ssh-keys/sign" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"public_key": "<YOUR_PUBLIC_KEY>"}')

echo "$GENERATE" | jq -r '.sshKey.publicKey' > ~/.ssh/cscs-key-sa-cert.pub
```

### Step 2a - Request an SSH Key Pair (Deprecated)

Use the JWT Token to generate a full SSH key pair and certificate:

```bash
GENERATE=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-ssh-service/api/v1/ssh-keys" \
  -H "Authorization: Bearer $JWT_TOKEN")

echo "$GENERATE" | jq -r '.sshKey.privateKey' > ~/.ssh/cscs-key
echo "$GENERATE" | jq -r '.sshKey.publicKey'  > ~/.ssh/cscs-key-cert.pub
chmod 600 ~/.ssh/cscs-key
```
## Certificate Validity and Renewal

All credentials issued through this flow are valid for **1 minute**. This is sufficient for:

- Single commands run interactively.
- Interactive shell sessions (the session stays alive after the certificate expires).

### Handling Sequential Commands

When running commands non-interactively via `ssh <host> <command>`, each invocation opens a **new SSH connection** and requires a **valid certificate**. You must therefore request a fresh certificate before each command.

#### 1. Configure your SSH client

Add an entry to `~/.ssh/config` for your target cluster (e.g., Clariden):

```
Host sa-*
    IdentityFile ~/.ssh/cscs-key
    CertificateFile ~/.ssh/cscs-key-sa-cert.pub
    User svc_account_name
    IdentitiesOnly yes

Host sa-ela
    HostName ela.cscs.ch
    ProxyJump none

Host sa-clariden
    HostName clariden.cscs.ch
    StrictHostKeyChecking no
    ProxyJump sa-ela
```

#### 2. Define a `get_certificate` helper

Add the following to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
get_certificate() {
    local JWT_TOKEN=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-service-account/api/v1/auth/token" \
        -H "X-API-Key: $CSCS_SA_API_KEY" | jq -r '.access_token')

    local CERT=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-ssh-service/api/v1/ssh-keys/sign" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"public_key\": \"$(cat ~/.ssh/cscs-key.pub)\"}")

    echo "$CERT" | jq -r '.sshKey.publicKey' > ~/.ssh/cscs-key-sa-cert.pub
}
```

#### 3. Define an `sa_ssh` convenience wrapper

```bash
sa_ssh() {
    get_certificate && ssh "$CSCS_SA_USERNAME@$1" "${@:2}"
}
```

This wrapper automatically refreshes the certificate before every SSH command:

```bash
sa_ssh sa-clariden srun your-job.sh
sa_ssh sa-clariden sbatch my-script.slurm
```

!!! note "Note"
    For CI/CD pipelines, call `get_certificate` at the start of each step that connects to the cluster, rather than once at the top of the pipeline. Certificates will expire between steps if the pipeline takes longer than 1 minute.