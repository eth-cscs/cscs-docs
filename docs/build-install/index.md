[](){#ref-building}
# Building and Installing Software

CSCS provides commonly used software and tools on Alps, however many use cases will require first installing software on a system before you can start working.
Modern HPC applications and software stacks are often very complicated, and there is no one-size-fits-all method for building and installing them.

<div class="grid cards" markdown>

-   :fontawesome-solid-earth: [__Programming Environments__][ref-software-prgenvs]

    Programming environments are your first option if you want to install an application (and its dependencies) from source, or set up a Python/Julia environment.

    CSCS provides the following uenv:

    [:octicons-arrow-right-24: prgenv-gnu][ref-uenv-prgenv-gnu]

    [:octicons-arrow-right-24: prgenv-nvfortran][ref-uenv-prgenv-nvfortran]

    [:octicons-arrow-right-24: linalg][ref-uenv-linalg]

    [:octicons-arrow-right-24: julia][ref-uenv-julia]

    And containers are used to deploy:

    [:octicons-arrow-right-24: Cray Programming Environment][ref-cpe]

</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-truck-fast: __Packaging and Deployment__

    How to create containers or uenv, and how to share them with your colleagues and community.

    [:octicons-arrow-right-24: build containers with podman][ref-build-containers]

    [:octicons-arrow-right-24: use the uenv build service][ref-uenv-build]

</div>

<div class="grid cards" markdown>

- :fontawesome-solid-hammer: __Software Building Guides__

    How to create containers or uenv, and how to share them with your colleagues and community.

    [:octicons-arrow-right-24: building software using uenv][ref-build-uenv]

    Coming soon: how to install Python software stacks.

</div>

