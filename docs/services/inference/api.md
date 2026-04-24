[](){#ref-inference-api}
# LLM Inference API Service

!!! under-construction "The LLM Inference API service is in beta"
    This service is under development.
    
    * We are currently exploring the potential adoption of this service, as well as the business model to cover for its cost.
    * Capacity and availability is limited. Downtimes and slowdowns are to be expected.
    * The models that are available can change over time.
    * Access to the Beta is upon invitation, without any cost.
    * Carefully read the [objectives and limitations][ref-inference-api-beta] of the Beta below 
    
    Please contact Pablo Fernandez at [`pablo.fernandez@cscs.ch`](mailto:pablo.fernandez@cscs.ch) if you are interested to participate in the Beta, describing your use case, relevant project or organizational context, and an estimate of your expected requirements including load, preferred models, and availability expectations.

The LLM Inference API service provides Internet-accessible OpenAI/Anthropic-compatible inference endpoints backed by selected open-weight models (for example Apertus and other vetted models).
Users consume from a shared pool of LLM models where requests are efficiently multiplexed across shared serving capacity, without needing to deploy, patch, scale, or operate the underlying serving stack.

Private model deployments are not supported. If you are interested to deploy a model that is not available in this service, we encourage using the [sml tool](https://github.com/swiss-ai/model-launch) developed by the Swiss AI community.

For privacy reasons, CSCS does not track user prompts or model responses.

For operational reasons, such as service quality and latency, CSCS does collect infrastructure metrics and telemetry, including prompt and response lengths.

Usage of sensitive or personal data is not allowed.

## Service at a glance

<div class="grid cards" markdown>

* :material-api: **Managed endpoints**

  Standard API access over HTTPS using familiar client libraries and tooling.

* :material-robot-outline: **Curated models**

  Selected models are made available and updated centrally.

* :material-cloud-check: **No infrastructure management**

  No need to run GPUs, containers, autoscaling, or model servers yourself.

</div>

[](){#ref-inference-api-quickstart}
## Quick Start

Get your token from the [CSCS portal](https://portal.cscs.ch), then run:

```sh
curl -X GET "https://ai-gateway.svc.cscs.ch/v1/models" \
  -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
  -H "Content-Type: application/json"
```

If the request succeeds, your access is active and you can start using available models.

[](){#ref-inference-api-access}
## Access

### Request access

Early usage of this service requires an invitation. If you would like to participate, please contact Pablo Fernandez ([`pablo.fernandez@cscs.ch`](mailto:pablo.fernandez@cscs.ch)) describing your use case, relevant project or organizational context, and an estimate of your expected requirements including load, preferred models, and availability expectations.

### Obtain your authentication token

Approved projects are given an authentication token, which can be retrieved and managed through [project management portal][ref-account-waldur].

!!! todo
    Add a screenshot to see how to obtain the API key
    <!-- Screenshot placeholder: portal page showing where to retrieve the token -->

### Use the API

!!! todo
    Provide a very short example of how to use the token with the API.

    Then provide a link to proper docs for the API

Use the gateway base URL:

```text
https://ai-gateway.svc.cscs.ch
```

Common API paths include:

```text
/v1/models
/v1/chat/completions
/v1/embeddings
```
## Example use cases

This section provides practical examples of how to use the API for common tasks.

### List available models

```sh
curl -X GET "https://ai-gateway.svc.cscs.ch/v1/models" \
  -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
  -H "Content-Type: application/json"
```

!!! todo
    show example output

### Chat completion request

```sh
curl -X POST "https://ai-gateway.svc.cscs.ch/v1/chat/completions" \
  -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "apertus-70b-instruct",
    "messages": [
      {"role": "user", "content": "Explain gradient descent in one paragraph."}
    ],
    "temperature": 0.2
  }'
```

!!! todo
    show example output

### Claude Code CLI

Example environment configuration to be set before starting a `claude` session.

```sh
export ANTHROPIC_API_KEY=<AUTHENTICATION_TOKEN>
export ANTHROPIC_BASE_URL=https://ai-gateway.svc.cscs.ch/v1
export ANTHROPIC_MODEL=apertus-70b-instruct
```

## Resource consumption and monitoring

Token consumption can be observed using the API

!!! todo
    Add an example on how to use the API toget accounting info


### Reducing consumption

* longer prompts increase cost and latency
* future costs may differentiate across models with different computational load

[](){#ref-inference-api-beta}
## Objectives of the Beta

The goal of this Beta is to understand what is missing before having an operational service. We need answers to understand:

* single-site deployments, vs. geo-redundant deployments for higher availability
* understand usage patterns (e.g. scale-to-zero on inactivity, vs. keep warm with a minimum replica count)
* what are the models that should be offered, under which conditions
* what the balance is with the existing capacity and future cost.
* what is the right accounting metric to be used

### Known issues and limitations

* project key management is still evolving; currently one key is issued per project and rotation requires contacting the team
* detailed self-service telemetry is limited today
* documentation and model-specific configuration transparency is improving
* load balancing and other QoS needs to be understood
