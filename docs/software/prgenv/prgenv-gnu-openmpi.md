[](){#ref-uenv-prgenv-gnu-openmpi}
# prgenv-gnu-openmpi

The `prgenv-gnu-openmpi` uenv is otherwise similar to [`prgenv-gnu`][ref-uenv-prgenv-gnu] except it provides OpenMPI instead of Cray MPICH.

!!! warning "OpenMPI is not officially supported on CSCS systems"
    Cray MPICH is the preferred, and officially supported, MPI implementation on CSCS systems.
    OpenMPI is provided on a best effort basis.
    While most applications should work correctly with OpenMPI, there may be missing features, broken functionality, or bad performance compared to Cray MPICH.
    Issues are best reported upstream, but CSCS is happy to help facilitate and coordinate issue reporting if you [get in touch][ref-get-in-touch].
    
Use of the uenv is similar to [`prgenv-gnu`][ref-uenv-prgenv-gnu].
See the [OpenMPI documentation][ref-communication-openmpi] for important information on configuring OpenMPI to take advantage of the Slingshot network.
    
### Versions

=== "25.11"
    TODO
