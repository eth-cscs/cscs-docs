<div class="grid cards" markdown>
-   <p style="text-align:center">Visit <a href="https://inference.status.cscs.ch/">inference.status.cscs.ch</a> for the status of the inference service, models, and latest announcements.</p>
</div>

[](){#ref-inference-api}
# LLM Inference API Service

The LLM Inference API service provides [OpenAI](https://developers.openai.com/api/reference/overview)/[Anthropic](https://platform.claude.com/docs/en/api/overview)-compatible inference endpoints running selected open-weight LLM models such as [Apertus](https://apertvs.ai/) and other vetted models.
CSCS takes care of deploying, patching, scaling, and operating the underlying serving stack.

In order to maximize utilization and reduce costs, a reduced set of models is available. Private model deployment is not supported.
If you are interested to deploy a model that is not available in this service, we encourage using the [sml tool](https://github.com/swiss-ai/model-launch) developed by the Swiss AI community.

Privacy and confidentiality are essential to us.
CSCS does not record user prompts or model responses, and your data does not leave the infrastructure we control.
Usage follows the [CSCS user regulations][ref-policies-user-regulations].

## Service at a glance

<div class="grid cards" markdown>

* :material-api: **Managed endpoints**

  Standard API access over HTTPS using familiar client libraries and tooling.

* :material-robot-outline: **Curated frontier models**

  Selected SOTA models are made available and updated centrally.

* :material-cloud-check: **No infrastructure management**

  Let CSCS manage GPUs, containers, autoscaling, and model servers.

* :material-shield-lock: **Sovereign and private**

  Your data is yours and is processed entirely within CSCS in Switzerland.
  Prompts and responses are not recorded.

</div>

!!! note
    Because most of these models are trained by others, have inherent biases, and are aligned with their creators' principles, we highly recommend always auditing their results. 
    We recommend using [Apertus](https://apertvs.ai/), which is available in this service. Apertus is fully open---including data, methods and alignment principles---and is compliant with the EU AI Act. A global foundation to build on!


[](){#ref-inference-api-quickstart}
## Quick start

Before using the API, obtain a key by following the [access section][ref-inference-api-access].
Include this API key in every API request.
The base URL for the inference API is `https://api.inference.cscs.ch/v1`.

!!! note
    The examples below assume that the `CSCS_INFERENCE_API_KEY` environment variable is set to your API key.
    Please store it in a safe location using a password manager, not in e.g. `~/.bashrc`.

Query available models using the `/v1/models` endpoint:
```bash
curl -X GET "https://api.inference.cscs.ch/v1/models" \
  -H "Authorization: Bearer $CSCS_INFERENCE_API_KEY" \
  -H "Content-Type: application/json"
```

??? info "Example `/v1/models` response"
    ```console
    $ curl -s -X POST "https://api.inference.cscs.ch/v1/models" -H "Authorization: Bearer $CSCS_INFERENCE_API_KEY" -H "Content-Type: application/json" | jq
    {
      "data": [
        {
          "id": "swiss-ai/Apertus-70B-Instruct-2509",
          "created": 1782315799,
          "object": "model",
          "owned_by": "Envoy AI Gateway"
        },
        {
          "id": "swiss-ai/Apertus-8B-Instruct-2509",
          "created": 1782315799,
          "object": "model",
          "owned_by": "Envoy AI Gateway"
        },
        {
          "id": "apertus-ai/Apertus-v1.5-8B-Prerelease-2606",
          "created": 1782315799,
          "object": "model",
          "owned_by": "Envoy AI Gateway"
        },
        {
          "id": "zai-org/GLM-5.2",
          "created": 1782315799,
          "object": "model",
          "owned_by": "Envoy AI Gateway"
        },
        {
          "id": "moonshotai/Kimi-K2.7-Code",
          "created": 1782315799,
          "object": "model",
          "owned_by": "Envoy AI Gateway"
        }
      ],
      "object": "list"
    }
    ```

Get a response using the Apertus 70B model using the `/v1/chat/completions` endpoint:
```bash
curl -X POST "https://api.inference.cscs.ch/v1/chat/completions" \
    -H "Authorization: Bearer $CSCS_INFERENCE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model": "swiss-ai/Apertus-70B-Instruct-2509", "messages": [{"role": "user", "content": "Explain gradient descent in one paragraph."}], "temperature": 0.2}'

```

??? info "Example `/v1/chat/completions` response"
    ```console
    $ curl -s -X POST "https://api.inference.cscs.ch/v1/chat/completions" -H "Authorization: Bearer $CSCS_INFERENCE_API_KEY" -H "Content-Type: application/json" -d '{"model": "swiss-ai/Apertus-70B-Instruct-2509", "messages": [{"role": "user", "content": "Explain gradient descent in one paragraph."}], "temperature": 0.2}' | jq
    {
      "id": "chatcmpl-426afafa-2bfb-4412-a1cb-859fdc3ada0c",
      "object": "chat.completion",
      "created": 1782485315,
      "model": "swiss-ai/Apertus-70B-Instruct-2509",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Gradient descent is a fundamental optimization algorithm used in machine learning to minimize the cost or loss function of a model. It works by iteratively adjusting the model's parameters in the direction of steepest descent of the cost function, which is determined by the negative of the gradient of the cost function with respect to the parameters. The gradient points in the direction of the greatest increase of the function, so by moving in the opposite direction (negative gradient), the algorithm reduces the cost. The step size, or learning rate, determines how much to adjust the parameters in each iteration. If the learning rate is too small, the algorithm may take too long to converge; if it's too large, the algorithm may overshoot the minimum and fail to converge. Gradient descent is widely used in training neural networks and other machine learning models.",
            "refusal": null,
            "annotations": null,
            "audio": null,
            "function_call": null,
            "tool_calls": [],
            "reasoning": null
          },
          "logprobs": null,
          "finish_reason": "stop",
          "stop_reason": null,
          "token_ids": null,
          "routed_experts": null
        }
      ],
      "service_tier": null,
      "system_fingerprint": "vllm-0.23.0-tp4-712aba24",
      "usage": {
        "prompt_tokens": 69,
        "total_tokens": 233,
        "completion_tokens": 164,
        "prompt_tokens_details": null
      },
      "prompt_logprobs": null,
      "prompt_token_ids": null,
      "prompt_text": null,
      "kv_transfer_params": null
    }
    ```

[](){#ref-inference-api-access}
## Access

Access to the inference service is granted at the project level.

[](){#ref-inference-api-available-models}
### Available models and pricing

Available models, along with pricing information, are listed on the [cscs2go Inference API page](https://2go.cscs.ch/offering/swiss_academia/#inference-api).
The available models can also be listed for a given API key using the [`models` endpoint][ref-inference-api-endpoints] or on the Inference API UI page when creating a new key.

[](){#ref-inference-api-access-resource}
### Create an inference resource

An inference resource must be created for your project before any project member can create API keys.
Which procedure applies depends on the organization your project belongs to: projects in the SwissAI organization can create the resource directly in the project management portal (self-service), while projects from other organizations must request it through the CSCS Service Desk.

=== "Self-service (SwissAI)"
    The PI or deputy PI can create the inference resource directly in the [project management portal][ref-account-waldur]:

    - Click the "Add resource" button in the top left of the UI.
    - Select your project from the dropdown.
    - Choose the "Inference Service" category and the `Inference-api-u` offering.

    The credit for the inference resource is taken from your project's credit.

    If you are a project member, ask your PI or deputy PI to create the resource for you.

=== "Service Desk (other organizations)"
    As self-service is not available for your project, the PI or Deputy PI should create a ticket at the [CSCS Service Desk](https://support.cscs.ch) with the following details:

    - Service: Inference Service
    - Request: add an inference resource to project `<your project ID>`
    - Node hours to assign to the resource: `<amount>` from `<cluster>`

    The node hours you specify are deducted from your project's node hours on `<cluster>` and converted into inference credits for the resource; see the [institutional pricing page](https://2go.cscs.ch/offering/swiss_academia/institutional_customers/) for the current node-hour rate.

    ??? example "worked example (rate as of 1 July 2026)"
        At the node-hour rate of CHF 2.69 in effect on 1 July 2026, allocating 2,000 node hours on Daint (Grace-Hopper) corresponds to CHF 5,380 of inference credits.
        Always check the [institutional pricing page](https://2go.cscs.ch/offering/swiss_academia/institutional_customers/) for the current rate.

[](){#ref-inference-api-access-key}
### Create an API key

Once an inference resource has been created for your project, any project member can create API keys through the inference API UI.

1. Navigate to the [Inference API UI](https://ui.inference.cscs.ch/login) and authenticate.
1. Expand the inference resource created by the PI and press "Add Key".
     - Enter a key alias for the key. Choose a memorable name that you can distinguish among other keys in your project and resource.
     - Optionally set a token budget, reset period, or restrict the available models. Please note that the global resource limits apply as well.
1. Click "Create Key" and copy the generated key and store securely, for example in a password manager. The key will be displayed once.
1. Test that the key works by following the [quick start guide][ref-inference-api-quickstart].

!!! info "Viewing key usage"
    After creating a key, you can sign in to the Inference API UI with the key ("Sign in with access token" below the CSCS account login) to view usage statistics for that specific key.

[](){#ref-inference-api-endpoints}
## API

The base URL for the inference API is `https://api.inference.cscs.ch/v1`.
The following OpenAI- and Anthropic-compatible endpoints are available.


| Path                   | Purpose                                      |
|------------------------|----------------------------------------------|
| `/v1/models`           | Query available models                       |
| `/v1/chat/completions` | Chat completions (OpenAI)                    |
| `/v1/messages`         | Chat completions (Anthropic)                 |
| `/v1/embeddings`       | Get a vector representation of a given input |

When using the endpoints for example [through agents][ref-inference-api-coding-agents-setup], the framework will handle API requests for you.
For information on how to use the endpoints directly, see the [OpenAI](https://developers.openai.com/api/reference/overview) and [Anthropic](https://platform.claude.com/docs/en/api/overview) documentation.

[](){#ref-inference-api-coding-agents-setup}
## Setting up coding agents to use the inference service

Below are instructions for setting up [Claude Code](https://claude.com/product/claude-code) and [OpenCode](https://opencode.ai) to use the inference service.
For more information on using coding agents on Alps, see the [coding agents guide][ref-coding-agents].

### Claude Code

Set the following environment variables before starting a `claude` session.

```bash
export ANTHROPIC_AUTH_TOKEN=$CSCS_INFERENCE_API_KEY

export ANTHROPIC_BASE_URL=https://api.inference.cscs.ch
export ANTHROPIC_MODEL=moonshotai/Kimi-K2.7-Code
claude
```

### OpenCode

Add a custom provider to your OpenCode config file (typically `~/.config/opencode/opencode.jsonc`).

```json title="OpenCode configuration for the inference API"
{
  "$schema": "https://opencode.ai/config.json",
   // Set Kimi as default OpenCode model
  "model": "cscs/moonshotai/Kimi-K2.7-Code",
  "provider": {
    "cscs": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "CSCS Inference",
      "options": {
        "baseURL": "https://api.inference.cscs.ch/v1",
        // Set apiKey or use /connect after configuring the provider
        "apiKey": "{env:CSCS_INFERENCE_API_KEY}" 
      },
      "models": {
        "moonshotai/Kimi-K2.7-Code": {
          "name": "Kimi K2.7-Code"
        }
      }
    }
  }
}
```

Start OpenCode and run the `/connect` command.
Select "CSCS Inference" to choose the newly added provider, and enter your API key when prompted.
Once connected, you can choose models configured in the config.

!!! info
    OpenCode does not auto-discover available models.
    Models have to be explicitly configured in the config.
    Use the `/v1/models` endpoint to list available models for your key.

[](){#ref-inference-api-announcements}
## Announcements

Planned maintenance, incidents, and changes to the available models are published on the [service status page](https://inference.status.cscs.ch).
Everyone with access to a project that has an inference resource is subscribed automatically and can opt out at any time.

The same announcements are also posted in the `#inference-service` channel of the CSCS User Slack; see [get in touch][ref-get-in-touch] to join.

[](){#ref-inference-api-issues}
## Known issues and limitations

* Detailed self-service telemetry is limited today. Users interested in hourly/daily usage should record it from the client side.
* Documentation and model-specific configuration transparency are work in progress.
* The service is currently offered from a single infrastructure. Interruptions of the service should be expected due to incidents and/or planned maintenances.
* We currently do not distinguish between cached and uncached input tokens; please beware the costs when performing typical agentic usage.
