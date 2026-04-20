[](){#ref-inference}
# Inference

Inference services are under development at CSCS and gradually becoming available to interested users. The roll-out of the different services and features is happening in phases.

We are seeking additional early-access users, particularly those with use cases not yet considered, to help shape our ongoing design phase. If you are interested in exploring early-access opportunities, please contact [pablo.fernandez@cscs.ch](mailto:pablo.fernandez@cscs.ch).


<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __OpenAI and Anthropic-compatible endpoints__

    Managed, Internet-accessible OpenAI/Anthropic-compatible inference endpoints using vetted open-weight models (e.g., Apertus), with token-based resource consumption.

    [:octicons-arrow-right-24: Managed LLM models][ref-managed-models]

</div>
<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Hybrid Kubernetes Namespaces__

    Internet-accessible Kubernetes namespaces backed by mixed hardware resources, combining Grace-Hopper GPU nodes with commodity CPU-only virtual machines. Designed for users who need to develop and operate ML-centric services (e.g., RAG) and use cases beyond LLMs. Resource consumption is based on assigned CPU, GPU, memory, and storage.

    !!! under-construction
        This service is not yet generally available. Its documentation is pending.

-   :fontawesome-solid-layer-group: __Blueprints for re-deployments__ 

    Deployment-ready blueprints for re-creating the GPU Hybrid Namespaces model on segregated infrastructure where stronger privacy, confidentiality, or compliance controls are required. They preserve the same flexibility for custom ML-centric services, resource-based consumption, and mixed-hardware Kubernetes operations, while adapting the platform to stricter isolation boundaries.

    !!! under-construction
        This service is not yet available.

</div>
