[](){#ref-inference-api}
# LLM Inference API Service

[](){#ref-inference-api-beta}
!!! under-construction "The LLM Inference API service is in beta"
    This service is under development, and is available by request to help CSCS build the service.
    During the beta we want to understand the following:

    * Single-site deployments vs. geo-redundant deployments for higher availability.
    * Usage patterns (e.g. scale-to-zero on inactivity, vs. keep warm with a minimum replica count).
    * Which models that should be offered, and under which conditions?
    * The trade-off between existing capacity and future cost.
    * What are the appropriate accounting metrics?

    During the beta users should expect that:

    * Capacity and availability is limited. Downtimes and slowdowns are to be expected.
    * The models that are available can change over time.
    * Access to the Beta is upon invitation, without any cost.

    Please contact Pablo Fernandez at [`pablo.fernandez@cscs.ch`](mailto:pablo.fernandez@cscs.ch) if you are interested to participate in the Beta, describing your use case, relevant project or organizational context, and an estimate of your expected requirements including load, preferred models, and availability expectations.

The LLM Inference API service provides Internet-accessible OpenAI/Anthropic-compatible inference endpoints backed by selected open-weight models (for example Apertus and other vetted models).
Users consume from a shared pool of LLM models where requests are efficiently multiplexed across shared serving capacity, without needing to deploy, patch, scale, or operate the underlying serving stack.

Private model deployments are not supported. If you are interested to deploy a model that is not available in this service, we encourage using the [sml tool](https://github.com/swiss-ai/model-launch) developed by the Swiss AI community.

Usage of sensitive or personal data is not allowed. For privacy reasons, CSCS does not track user prompts or model responses. CSCS collects infrastructure metrics and telemetry, including prompt and response lengths, in order to monitor and improve service quality.


## Service at a glance

<div class="grid cards" markdown>

* :material-api: **Managed endpoints**

  Standard API access over HTTPS using familiar client libraries and tooling.

* :material-robot-outline: **Curated models**

  Selected models are made available and updated centrally.

* :material-cloud-check: **No infrastructure management**

  Let CSCS manage GPUs, containers, autoscaling, and model servers.

* :material-shield-lock: **Sovereign and private**

  Your data is yours and is processed entirely within CSCS in Switzerland.
  Prompts and responses are not tracked.

</div>

[](){#ref-inference-api-quickstart}
## Quick Start

Before starting, you need an API token (see the the [access guide][ref-inference-api-access]).
Once you have your token, it must be provided with every call to the API.

!!! example "opencode CLI"
    Example environment configuration to be set before starting a `claude` session.
    ```console
    $ export ANTHROPIC_API_KEY=<AUTHENTICATION_TOKEN>
    $ export ANTHROPIC_BASE_URL=https://llm-proxy.svc.cscs.ch/v1
    $ export ANTHROPIC_MODEL=apertus-70b-instruct
    ```

!!! example "List available models"
    ```console
    $ curl -X GET "https://llm-proxy.svc.cscs.ch/v1/models" \
      -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
      -H "Content-Type: application/json"
    ```

!!! example "Chat completion request"
    ```console
    $ curl -X POST "https://llm-proxy.svc.cscs.ch/chat/completions" \
      -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "Apertus-70B-Instruct-2509",
        "messages": [
          {"role": "user", "content": "Explain gradient descent in one paragraph."}
        ],
        "temperature": 0.2
      }'
    ```

[](){#ref-inference-api-access}
## Access

### Request access

Early usage of this service requires an invitation.
If you would like to participate, please contact Pablo Fernandez ([`pablo.fernandez@cscs.ch`](mailto:pablo.fernandez@cscs.ch)) describing your use case, relevant project or organizational context, and an estimate of your expected requirements including load, preferred models, and availability expectations.

### Obtain your authentication token

Approved projects are given an authentication token, which can be retrieved and managed through [project management portal][ref-account-waldur]. The following images illustrates.

![Inference Service within the CSCS User Portal](../images/services/inference-api-key.png)

## API

The service is accessed through the gateway base URL `https://llm-proxy.svc.cscs.ch`.

With common API paths including:

| path | purpose |
| ---- | ------- |
| `/v1/models`           | query available models |
| `/v1/chat/completions` | chat completions |
| `/v1/embeddings`       | get a vector representation of a given input |

!!! todo
    Describe API support.
    If we provide both OpenAI and Anthropic APIs, is it sufficient to provide links to external documentation for these APIs, with notes about any differences?

[](){#ref-inference-api-guides}
## Guides

### Reducing consumption

* longer prompts increase cost and latency
* future costs may differentiate across models with different computational load

[](){#ref-inference-api-issues}
## Known issues and limitations

* Project key management is still evolving; currently one key is issued per project and rotation requires contacting the team.
* Detailed self-service telemetry is limited today.
* Documentation and model-specific configuration transparency are work in progress.
* Load balancing and other QoS need to be understood.
