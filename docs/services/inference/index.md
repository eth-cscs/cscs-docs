[](){#ref-inference}
# Inference

!!! under-construction "Inference services are in beta"
    Inference services are under development.
    We are seeking additional early-access users, particularly novel use cases, to help shape the service design.
    Please contact Pablo Fernandez at [`pablo.fernandez@cscs.ch`](mailto:pablo.fernandez@cscs.ch) if you are interested.

!!! todo
    Add an introduction that says __what the inference service is__

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Managed Model Access__

    Managed, internet-accessible [OpenAI API](https://developers.openai.com/api/docs)-compatible inference providing open-weight models (e.g., [Apertus](https://apertvs.ai/)), with token-based resource consumption.

    [:octicons-arrow-right-24: Managed LLM models][ref-inference-managed]

</div>
<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Hybrid Kubernetes Namespaces__

    Internet-accessible Kubernetes namespaces backed by mixed hardware resources, combining Grace-Hopper GPU nodes with commodity CPU-only virtual machines.
    Designed for users who need to develop and operate ML-centric services (e.g., RAG) and use cases beyond LLMs.
    Resource consumption is based on assigned CPU, GPU, memory, and storage.

    !!! under-construction
        This service is not yet available.

-   :fontawesome-solid-layer-group: __Blueprints for re-deployments__ 

    Deployment-ready blueprints for re-creating the GPU Hybrid Namespaces model on segregated infrastructure where stronger privacy, confidentiality, or compliance controls are required.
    They preserve the same flexibility for custom ML-centric services, resource-based consumption, and mixed-hardware Kubernetes operations, while adapting the platform to stricter isolation boundaries.

    !!! under-construction
        This service is not yet available.

</div>
