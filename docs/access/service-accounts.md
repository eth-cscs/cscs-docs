[](){#ref-service-accounts}
# Service Accounts

Service Accounts provide programmatic, non-interactive access to CSCS project resources. Unlike personal accounts, they are designed for automated workflows such as CI/CD pipelines, scheduled jobs, and scripts that need to authenticate with HPC systems without human interaction.

Use a Service Account when:

- You need to run SSH commands from a CI/CD pipeline (e.g., GitHub Actions, GitLab CI).
- You have scripts that execute multiple cluster operations in sequence.
- You want to isolate automated access from your personal credentials.

To use Service Accounts, you'll need the [`cscs-key` CLI tool][ref-ssh-cli], a helper that wraps the authentication flow described below into simple commands.
Alternatively, you can implement the flow yourself using the raw API calls documented here.

!!! note "Requesting a Service Account"
    If you need to request a Service Account, please see [Requesting a Service Account][ref-account-create-service-account] in the accounts and projects documentation.


## Creating a Service Account in Waldur

Once enabled, you can create a Service Account in your [Waldur project][ref-account-waldur] at [`https://portal.cscs.ch/projects/`](https://portal.cscs.ch/projects/).

1. Navigate to your project's **Team** tab.
2. Click **Add** -> **Service account**.
3. Follow the prompts to create a new Service Account.

!!! note "Copy the API Key right away"
    Upon creation, an API Key will be shown **only once**. Copy and store it securely immediately, it cannot be retrieved later. If lost, the key must be rotated.

!!! warning "Keep your API Key secure"
    The `CSCS_API_KEY` environment variable overrides the default OIDC authentication in `cscs-key`. Avoid setting it globally (e.g., in `.bashrc`), as this would break personal interactive use. Use it only within the scope of your scripts or CI/CD environment.

[](){#ref-service-accounts-quick-auth}
## Quick Authentication with `cscs-key`

Once you have your API Key, `cscs-key` can generate a short-lived certificate in a single command:

```bash
CSCS_API_KEY=<YOUR_API_KEY> cscs-key sign --duration 1min
```

!!! note "Use a separate SSH key pair for Service Accounts"
    We recommend using a different SSH key pair for Service Accounts to keep automated and personal access cleanly separated. Use the `-f` flag to specify the key:
    ```bash
    CSCS_API_KEY=<YOUR_API_KEY> cscs-key sign --duration 1min -f ~/.ssh/cscs-key-sa
    ```

## Authentication Flow

Cluster access requires two API calls: first to obtain a **JWT Token** from your API Key, then to use that token to retrieve a signed **SSH Certificate**.

```
API Key  ->  JWT Token  ->  SSH Certificate  ->  Cluster Login
```

The `cscs-key` tool [handles this flow for you][ref-service-accounts-quick-auth]. If you prefer to call the API directly, follow Steps 1 and 2 below.

### 1. Request a JWT Token

```bash
JWT_RESPONSE=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-service-account/api/v1/auth/token" \
  -H "X-API-Key: $CSCS_API_KEY")

JWT_TOKEN=$(echo "$JWT_RESPONSE" | jq -r '.access_token')
```

### 2. Sign an SSH Certificate (Recommended)

If you already have an SSH key pair, request only a signed certificate. This is the preferred approach because it avoids generating a new private key on every authentication.

```bash
GENERATE=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-ssh-service/api/v1/ssh-keys/sign" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"public_key": "<YOUR_PUBLIC_KEY>"}')

echo "$GENERATE" | jq -r '.sshKey.publicKey' > ~/.ssh/cscs-key-sa-cert.pub
```

### 3. Generate a Full SSH Key Pair (Deprecated)

!!! warning "Deprecated"
    This method generates a new private key on every call and is no longer recommended. Use Step 2 instead. This endpoint may be removed in a future release.

Use this only if your environment does not support pre-existing SSH key pairs:

```bash
GENERATE=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-ssh-service/api/v1/ssh-keys" \
  -H "Authorization: Bearer $JWT_TOKEN")

echo "$GENERATE" | jq -r '.sshKey.privateKey' > ~/.ssh/cscs-key-sa
echo "$GENERATE" | jq -r '.sshKey.publicKey'  > ~/.ssh/cscs-key-sa-cert.pub
chmod 600 ~/.ssh/cscs-key-sa
```

## Certificate Validity and Renewal

All credentials issued through this flow are valid for **1 minute**. This is sufficient for:

- Single commands run interactively.
- Interactive shell sessions (the session stays alive after the certificate expires).

However, each non-interactive SSH invocation (`ssh <host> <command>`) opens a new connection and requires a valid certificate. You must request a fresh certificate before **each command**.

## Using Service Accounts in CI/CD Pipelines

### 1. Configure your SSH client

See the [SSH documentation][ref-ssh-config] for general SSH configuration.
For Service Accounts, we recommend using a separate wildcard pattern and key pair to avoid interfering with your personal configuration:

```
Host sa-*
    IdentityFile ~/.ssh/cscs-key-sa
    User svc_account_name

Host sa-ela
    HostName ela.cscs.ch

Host sa-clariden
    HostName clariden.cscs.ch
    ProxyJump sa-ela
```

### 2. Define helper functions

The following helper functions are designed as an example for use in **scripts and CI/CD pipelines only**, not for local interactive use.

!!! note "Environment variables"
    CI/CD should be the only place where the `CSCS_API_KEY` environment variable is set.
    In this example, `CSCS_SA_USERNAME` is also defined, but the username can be retrieved from the `sign` API response as well.

```bash
get_certificate() {
    local JWT_TOKEN=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-service-account/api/v1/auth/token" \
        -H "X-API-Key: $CSCS_API_KEY" | jq -r '.access_token')

    local CERT=$(curl -s -X POST "https://authx-gateway.svc.cscs.ch/api-ssh-service/api/v1/ssh-keys/sign" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"public_key\": \"$(cat ~/.ssh/cscs-key-sa.pub)\"}")

    echo "$CERT" | jq -r '.sshKey.publicKey' > ~/.ssh/cscs-key-sa-cert.pub
}

sa_ssh() {
    get_certificate && ssh "$CSCS_SA_USERNAME@$1" "${@:2}"
}
```

Using these helper functions we can automatically refresh the certificate before every SSH command:

```bash
sa_ssh sa-clariden srun your-job.sh
sa_ssh sa-clariden sbatch my-script.slurm
```
