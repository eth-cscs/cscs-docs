[](){#ref-managed-llm-models}
# Managed LLM Models

This page provides guidance on how to obtain access to, use, and manage usage of our Managed LLM Models service. 

This service offers Internet-accessible OpenAI and Anthropic-compatible endpoints backed by a variety of open-source language models, without the need for users to manage the underlying infrastructure or models. 

Please note that this service does not support the deployment of private models, but if you need to include an additional model we are open to discussing your need.


## Access process

### Request for early access
Our Managed LLM Models service is currently in early access phase. To take advantage of it, please submit a request for early access to pablo.fernandez@cscs.ch, indicating your project context, specific needs, desired models and availability requirements.

### Obtaining the authentication token
Once your request is approved, an authentication token is issued for your project (see [Project Management][ref-account-management]) which you can obtain through [https://portal.cscs.ch](https://portal.cscs.ch). This is the token you will use to query the endpoints against [https://ai-gateway.svc.cscs.ch](https://ai-gateway.svc.cscs.ch).

### Testing the endpoint
```sh
curl -X GET "https://ai-gateway.svc.cscs.ch/v1/models" \
  -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
  -H "Content-Type: application/json"
```

