[](){#ref-managed-models}

# Managed LLM Models

This page explains how to request access, obtain credentials, use the service, and monitor consumption for the **Managed LLM Models** offering at CSCS.

The service provides Internet-accessible OpenAI/Anthropic-compatible inference endpoints backed by selected open-weight models (for example Apertus and other vetted models). Users consume from a shared pool of LLM models where requests are efficiently multiplexed across shared serving capacity, without needing to deploy, patch, scale, or operate the underlying serving stack.

This offering is intended for users who primarily need managed inference APIs. Private model deployments are not supported. Additional model requests can be discussed via [pablo.fernandez@cscs.ch](mailto:pablo.fernandez@cscs.ch), subject to review.

For privacy reasons, CSCS does not track user prompts or model responses. For operational reasons, such as service quality and latency, CSCS does collect infrastructure metrics and telemetry, including prompt and response lengths.

---

## Service at a glance

<div class="grid cards" markdown>

* :material-api: **Managed endpoints**

  Standard API access over HTTPS using familiar client libraries and tooling.

* :material-robot-outline: **Curated models**

  Selected models are made available and updated centrally.

* :material-finance: **Usage-based consumption**

  Resource accounting is based on token usage.

* :material-cloud-check: **No infrastructure management**

  No need to run GPUs, containers, autoscaling, or model servers yourself.

</div>

---

## Quick Start

Get your token from the [CSCS portal](https://portal.cscs.ch), then run:

```sh
curl -X GET "https://ai-gateway.svc.cscs.ch/v1/models" \
  -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
  -H "Content-Type: application/json"
```

If the request succeeds, your access is active and you can start using available models.

---

## Access process

### 1. Request access

The service is being rolled out in phases and is not yet generally available. To request early-access, contact [pablo.fernandez@cscs.ch](mailto:pablo.fernandez@cscs.ch) and briefly describe your use case, relevant project or organizational context, and an estimate of your expected requirements including load, preferred models, and availability expectations.

---

### 2. Obtain your authentication token

Once approved, your project receives an authentication token, which can be retrieved and managed through [https://portal.cscs.ch](https://portal.cscs.ch).

!!! todo
    Project key management is evolving. Future improvements include multiple keys per project, self-service rotation, revocation, scoped access, auditability, and quota or budget controls.

<!-- Screenshot placeholder: portal page showing where to retrieve the token -->

---

### 3. Endpoint URL

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

---

## First tests and examples

### List available models

```sh
curl -X GET "https://ai-gateway.svc.cscs.ch/v1/models" \
  -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
  -H "Content-Type: application/json"
```

---

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

---

### Claude Code CLI

Example environment configuration to be set before starting a `claude` session.

```sh
export ANTHROPIC_API_KEY=<AUTHENTICATION_TOKEN>
export ANTHROPIC_BASE_URL=https://ai-gateway.svc.cscs.ch/v1
export ANTHROPIC_MODEL=apertus-70b-instruct
```

---

## Resource consumption and monitoring

Quotas are currently assigned per project as token volumes. Tokens consumption is processed on the project allocation. This includes user prompts, generated responses, and internal reasoning tokens when applicable.

Token accounting currently does not account for the model chosen.

Aspects to keep in consideration:

* longer prompts increase cost and latency
* future pricing may differentiate across models with different compute costs

!!! todo
    Model-aware accounting is planned so token costs and quotas may differ across models.

### Current visibility

Quota state is available through the CSCS portal: [https://portal.cscs.ch](https://portal.cscs.ch).

More elaborated usage reporting and visibility features are being developed progressively. If you need interim reporting or quota visibility, contact the service team.

!!! todo
    Enhanced usage reporting, richer quota visibility, and system dashboards are being developed progressively.

### Deployment visibility roadmap

A future status page will provide fuller visibility into deployed models and their configuration, including deployment state, replica counts, load, startup expectations, templates, routing defaults and system prompts.

!!! todo
    A dedicated status page will provide deployment visibility such as model state, replicas, load, startup expectations, routing defaults, and related configuration details.

---

## Operational characteristics

Model deployment policies distinguish the following cases:

* single-site deployments, vs. geo-redundant deployments for higher availability
* scale-to-zero on inactivity, vs. keep warm with a minimum replica count (usually 1)

!!! todo
    Higher-availability service tiers and explicit SLO options for production workloads are planned for selected models.

---

## Good practices

### Security

* store tokens safely
* avoid exposing prompts containing sensitive data unless approved for your context

---

## Current limitations

* project key management is still evolving; currently one key is issued per project and rotation requires contacting the team
* detailed self-service telemetry is limited today
* model-specific configuration transparency is improving
* automatic-scaling of models still incur significant latency