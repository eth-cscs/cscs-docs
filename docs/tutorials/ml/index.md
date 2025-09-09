[](){#ref-tutorials-ml}
# Machine Learning Platform Tutorials

The LLM tutorials gradually introduce key concepts of the Machine Learning Platform in a series of hands-on examples. A particular focus is on the [Container Engine][ref-container-engine] for managing the runtime environment.

In the [first tutorial][software-ml-llm-inference-tutorial], you will learn how to run inference with a LLM on a single node using a container from the NVIDIA GPU Cloud (NGC). Concepts such as container environment description, layering a thin virtual environment on top of the container image, and job launching/monitoring will be introduced.

Building on the first tutorial, in the [second tutorial][software-ml-llm-fine-tuning-tutorial] you will learn how to train (fine-tune) a LLM on multiple GPUs on a single node. For this purpose, you will use HuggingFace's `accelerate` and see best practices for dataset management.

In the [third tutorial][software-ml-llm-nanotron-tutorial], you will apply the techniques from the previous tutorials to enable distributed (pre-)training of a model in `nanotron` on multiple nodes. In particular, this tutorial makes use of model-parallelism and introduces the usage of `torchrun` to manage jobs on individual nodes.

!!! note
    The focus for these tutorials is on introducing concepts of the Machine Learning Platform. As such, they do not necessarily discuss the latest advancements or steps required to obtain maximum performance. For this purpose, consult the framework-specific pages, such as the one for [PyTorch][ref-software-pytorch]. 
