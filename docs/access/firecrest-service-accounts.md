[](){#ref-firecrest-service-accounts}
# FirecREST Service Accounts

Service Accounts provide programmatic, non-interactive access to CSCS resources.
They can also be used to authenticate requests to FirecREST instead of a personal [OAuth2 client application][ref-devportal-application].

This is useful for automated workflows that need to call FirecREST but should not be tied to a personal user account or Developer Portal application.

!!! warning "Experimental"
    Calling FirecREST with a Service Account API key is an experimental service.
    The endpoints and the authentication flow described on this page can change without a deprecation period.

    Service Accounts are not allowed to use these endpoints by default: each Service Account has to be explicitly allowlisted first.
    To request access, open a ticket at the [CSCS Service Desk](https://support.cscs.ch) stating the name of the Service Account and the project it belongs to.

!!! note "Requesting a Service Account"
    To use FirecREST with a Service Account you first need a Service Account and its API key.
    See [Requesting a Service Account][ref-account-create-service-account] for how to create one.

## Authenticating with an API key

The Service Account API key is passed in the `X-API-Key` header.
Unlike the standard FirecREST endpoints, the Service Account proxy endpoint does not require an OAuth2 access token.

```bash title="List FirecREST systems using a Service Account"
curl -s -X GET "https://f7t-pat.api.svc.cscs.ch/hpcp/status/systems" \
     -H "X-API-Key: $CSCS_API_KEY"
```

## Service Account endpoints

The Service Account FirecREST proxy is available at `https://f7t-pat.api.svc.cscs.ch/<platform>`.
The platform path selects which FirecREST deployment the request is forwarded to.

| Platform                          | Endpoint                                 | Clusters                                                         |
|-----------------------------------|------------------------------------------|------------------------------------------------------------------|
| [HPC Platform][ref-platform-hpcp] | `https://f7t-pat.api.svc.cscs.ch/hpcp`   | [Daint][ref-cluster-daint], [Eiger][ref-cluster-eiger]           |
| [ML Platform][ref-platform-mlp]   | `https://f7t-pat.api.svc.cscs.ch/mlp`    | [Bristen][ref-cluster-bristen], [Clariden][ref-cluster-clariden] |
| [C&W Platform][ref-platform-cwp]  | `https://f7t-pat.api.svc.cscs.ch/cw`     | [Santis][ref-cluster-santis]                                     |

The API surface under each endpoint is the same as the corresponding [FirecREST v2 deployment][ref-firecrest].

## Using pyFirecREST

[pyFirecREST][pyfirecrest] does not yet natively support `X-API-Key` authentication.
Until it does, the client can be configured with an `httpx` request hook that replaces the bearer token with the API key header.

The following example shows a reusable helper that builds a `Firecrest` client for Service Account access.
The second half of the script uses the client to inspect systems, user information and files.

```python title="FirecREST Service Account client with pyFirecREST"
import json
import os
import sys

import httpx
from firecrest.v2 import Firecrest


DEFAULT_URL = "https://f7t-pat.api.svc.cscs.ch/hpcp"
API_KEY_HEADER = "X-API-Key"

API_KEY = os.environ.get("CSCS_API_KEY")
if not API_KEY:
    print("Set the CSCS_API_KEY environment variable")
    sys.exit(1)


class ApiKeyAuth:
    """Placeholder auth object that suppresses token-based authentication."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_access_token(self) -> str:
        return "unused-api-key-auth"


def _api_key_hook(api_key: str):
    """Return an httpx request hook that swaps bearer auth for the API key."""

    def hook(request: httpx.Request) -> None:
        request.headers.pop("Authorization", None)
        request.headers[API_KEY_HEADER] = api_key

    return hook


def create_client(
    api_key: str,
    firecrest_url: str = DEFAULT_URL,
) -> Firecrest:
    """Build a ``Firecrest`` client that authenticates with ``X-API-Key``."""
    client = Firecrest(
        firecrest_url=firecrest_url,
        authorization=ApiKeyAuth(api_key),
        verify=True,
    )

    hook = _api_key_hook(api_key)
    client._session.event_hooks["request"].append(hook)

    # close_session()/create_new_session() build a fresh httpx.Client, which
    # would come without our hook, so re-install it on every new session.
    original_create_new_session = client.create_new_session

    def create_new_session_with_hook() -> None:
        original_create_new_session()
        client._session.event_hooks["request"].append(hook)

    client.create_new_session = create_new_session_with_hook
    return client


SYSTEM = "daint"
client = create_client(api_key=API_KEY, firecrest_url=DEFAULT_URL)

#
# using the client
#

print(f"Server version: {client.server_version() or 'unknown'}")
systems = client.systems()
print(f"\nSystems ({len(systems)}):")
for system in systems:
    print(f"  - {system.get('name')}")

print("\nUser info:")
user = client.userinfo(system_name=SYSTEM)
print(json.dumps(user, indent=2))

print("\nHome directory:")
username = user["user"]["name"]
for entry in client.list_files(system_name=SYSTEM, path=f"/users/{username}"):
    print(f"  {entry.get('permissions', ''):>10}  {entry.get('name')}")

client.close_session()
```

!!! warning "Keep your API key secret"
    The Service Account API key is a credential.
    Store it in a secret manager or CI/CD variable and never commit it to a repository.

## Further information

* [FirecREST][ref-firecrest]
* [Service Accounts][ref-service-accounts]
* [Developer Portal][ref-devportal]
* [pyFirecREST documentation][pyfirecrest]

[pyfirecrest]: https://pyfirecrest.readthedocs.io/
