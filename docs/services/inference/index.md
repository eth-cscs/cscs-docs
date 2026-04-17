[](){#ref-inference}
# Inference

Inference services are currently under development at CSCS and are gradually becoming available to interested users. We are actively seeking additional early-access users to inform our ongoing design phase. If you are interested in discussing your early-access potential and use-case details, please reach out to pablo.fernandez@cscs.ch.

## Roadmap Overview

The development and roll-out of our inference services are happening in distinct phases. This section offers a high-level view of the envisioned features and planned service offerings. While we cannot commit to specific timelines for general availability, we invite you to influence our priority decisions by discussing your interests and requirements with us through pablo.fernandez@cscs.ch.

- **[Managed LLM Models][ref-managed-llm-models]**: This service provides Internet-accessible OpenAI and Anthropic-compatible endpoints, powered by selected open-source models such as Apertus. It is designed for organizations that primarily need inference endpoints without having to manage the underlying infrastructure or models. Users are allocated resources based on token usage. While we may add additional models based on user inquiries, any new model deployments are subject to internal vetting processes. It's important to note that this service does not support the deployment of privately-accessible models.

- **Self-Managed Inference Sandboxes**: This service offers Internet-accessible Kubernetes namespaces, backed by hybrid compute resources including Grace-Hopper GPU nodes. It is intended for users who require the flexibility to customize their inference workflows, such as running GUIs or RAG service, and run inference services based on non-LLM-based models. Resource allocations are defined based on computational resources (e.g., CPU, GPU, memory, and storage) assigned to each namespace. This option supports users with diverse model needs beyond simple LLM-based inference.

- **Higher-Availability**: To enhance service reliability and uptime, we leverage CSCS’s multi-site infrastructure (Lugano and Lausanne) to potentially make critical components of our services geo-redundant. This will enable us to support a higher level of service availability.

- **Privacy-Preserving Self-Managed Inference Sandboxes**: A variant of the self-managed sandboxes tailored for use-cases that require stringent privacy and confidentiality. Like the regular self-managed service, it allows for custom workflows and resource allocations but with enhanced privacy features.

Access to the above inference services can be granted to existing [projects](#ref-account-management).

If you have any further questions or would like to discuss your specific use-case, please contact pablo.fernandez@cscs.ch.
