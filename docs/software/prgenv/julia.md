[](){#ref-uenv-julia}
# julia

The `julia` uenv provides a complete HPC setup for running Julia efficiently at scale, using the supercomputer hardware optimally. 
Unlike in traditional approaches, this Julia HPC setup enables you to update Julia yourself using the included preconfigured community tool [`juliaup`](https://github.com/JuliaLang/juliaup). 
It also does not preinstall any packages site-wide. Instead, for HPC key packages that benefit from using locally built libraries (`MPI.jl`, `CUDA.jl`, `AMDGPU.jl`, `HDF5.jl`, `ADIOS2.jl`, etc.), this uenv provides the libraries and presets package preferences and environment variables for an automatic optimal installation and usage of these packages using these local libraries. 
As a result, you only need to type, e.g., `] add CUDA` in the Julia REPL, in order to install `CUDA.jl` optimally. 
The `julia` uenv internally relies on the community scripting project [JUHPC](https://github.com/JuliaParallel/JUHPC) to achieve this.

## Versioning

The naming scheme is `julia/<version>`, where `<version>` has the `YY.M[M]` format, for example September 2024 is `24.9`, and May 2025 would be `25.5`. 
The release schedule is not fixed; new versions will be released, when there is a compelling reason to update.

| version   | node types | system |
|-----------|-----------|--------|
| 24.9      | gh200, zen2 | daint, eiger, todi |
| 25.5      | gh200, zen2 | daint, eiger, santis, clariden, bristen |

=== "25.5"

    The key updates in version `25.5:v1` from the version `24.9` were:

    * enabling compatibility with the latest `uenv` version `8.0`
    * changing the installation directory
    * adding the `jupyter` view
    * upgrading to `cuda@12.8` and `cray-mpich@8.1.30`
    
    !!! info "HPC key libraries included"
        * cray-mpich/8.1.30
        * cuda/12.8.0
        * hdf5/1.14.5
        * adios2/2.10.2

## How to use

Find and pull a Julia uenv image, e.g.:
```bash
uenv image find julia       # list available julia images
uenv image pull julia/25.5  # copy version[:tag] from the list above
```

Start the image and activate the Julia[up] HPC setup by loading the following view(s):
=== "`juliaup`"
    !!! example ""
        ```bash
        uenv start julia/25.5:v1 --view=juliaup
        ```

=== "`juliaup` and `modules`"
    !!! example "This activates also modules for the available libraries like, e.g, `cuda`."
        ```bash
        uenv start julia/25.5:v1 --view=juliaup,modules
        ```

There is also a view `jupyter` available, which is required for [using Julia in JupyterHub][using-julia-in-jupyterhub].

!!! info "Automatic installation of Juliaup and Julia"
    The installation of `juliaup` and the latest `julia` version happens automatically the first time when `juliaup` is called:
    ```bash
        juliaup
    ```

Note that the `julia` uenv is built extending the `prgenv-gnu` uenv. 
As a result, it provides also all the features of `prgenv-gnu`. 
Please see [the `prgenv-gnu` documentation][ref-uenv-prgenv-gnu-how-to-use] for details. 
You can for example load the `modules` view to see the exact versions of the libraries available in the uenv.

## Background on Julia for HPC

[Julia](https://julialang.org/) is a programming language that was designed to solve the "two-language problem", the problem that prototypes written in an interactive high-level language like MATLAB, R or Python need to be partly or fully rewritten in lower-level languages like C, C++ or Fortran when a high-performance production code is required. 
Julia, which has its origins at MIT, can however reach the performance of C, C++ or Fortran despite being high-level and interactive. 
This is possible thanks to Julia's just-ahead-of-time compilation: code can be executed in an interactive shell as usual for prototyping languages, but functions and code blocks are compiled to machine code right before their first execution instead of being interpreted (note that modules are pre-compiled).

Julia is optimally suited for parallel computing, supporting, e.g., MPI (via [`MPI.jl`](https://github.com/JuliaParallel/MPI.jl)) and threads similar to OpenMP. 
Moreover, Julia's GPU packages ([`CUDA.jl`](https://github.com/JuliaGPU/CUDA.jl), [`AMDGPU.jl`](https://github.com/JuliaGPU/AMDGPU.jl), etc.) enables writing native Julia code for GPUs [1], which can reach similar efficiency as CUDA C/C++ [2] or the analog for other vendors. 
Julia was shown to be suitable for scientific GPU supercomputing at large scale, enabling near optimal performance and nearly ideal scaling on thousands of GPUs on Piz Daint [2,3,4,5]. 
Packages like [ParallelStencil.jl](https://github.com/omlins/ParallelStencil.jl) [[4](https://doi.org/10.21105/jcon.00138)] and [ImplicitGlobalGrid.jl](https://github.com/eth-cscs/ImplicitGlobalGrid.jl) [[3](https://doi.org/10.21105/jcon.00137)] enable to unify prototype and high-performance production code in one single codebase. 
Furthermore, Julia permits direct calling of C/C++ and Fortran libraries without glue code. 
It also features similar interfaces to prototyping languages as, e.g., Python, R and MATLAB. 
Finally, the [Julia PackageCompiler](https://github.com/JuliaLang/PackageCompiler.jl) enables to compile Julia modules in order to create shared libraries that are callable from C or other languages (a comprehensive [Proof of Concept](https://github.com/omlins/libdiffusion) was already available in 2018 and the PackageCompiler has matured very much since).

## References

[1] Besard, T., Foket, C., & De Sutter B. (2018). Effective Extensible Programming: Unleashing Julia on GPUs. IEEE Transactions on Parallel and Distributed Systems, 30(4), 827-841

[2] Räss, L., Omlin, S., & Podladchikov, Y. Y. (2019). Porting a Massively Parallel Multi-GPU Application to Julia: a 3-D Nonlinear Multi-Physics Flow Solver. JuliaCon Conference, Baltimore, US.

[3] Omlin, S., Räss, L., Utkin I. (2024). Distributed Parallelization of xPU Stencil Computations in Julia. The Proceedings of the JuliaCon Conferences, 6(65), 137, https://doi.org/10.21105/jcon.00137

[4] Omlin, S., Räss, L. (2024). High-performance xPU Stencil Computations in Julia. The Proceedings of the JuliaCon Conferences, 6(64), 138, https://doi.org/10.21105/jcon.00138

[5] Omlin, S., Räss, L., Kwasniewski, G., Malvoisin, B., & Podladchikov, Y. Y. (2020). Solving Nonlinear Multi-Physics on GPU Supercomputers with Julia. JuliaCon Conference, virtual.
