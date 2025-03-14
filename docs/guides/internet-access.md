[](){#ref-guides-internet-access}
# Internet Access on Alps

The [Alps network][ref-alps-hsn] is mostly configured with private IP addresses (`172.28.0.0/16`).
Login nodes have public IP addresses which means that they can directly access the internet, while a proxy server provides internet access for compute nodes.

??? info "Compute node proxy configuration"

    Compute nodes are configured with the following environment variables to use the proxy server:
    
    ```bash
    export https_proxy=http://proxy.cscs.ch:8080
    export http_proxy=http://proxy.cscs.ch:8080
    export no_proxy=.local, .cscs.ch, localhost, 148.187.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
    export HTTPS_PROXY=http://proxy.cscs.ch:8080
    export HTTP_PROXY=http://proxy.cscs.ch:8080
    export NO_PROXY=.local, .cscs.ch, localhost, 148.187.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
    ```

!!! warning "Public IPs are a shared resource"
    Be aware that public IPs, whether on login nodes or through the proxy, are essentially a shared resource.
    Many services will rate limit or block usage based on the IP address if abused.
    An example is pulling container images from Docker Hub.
    [Authenticating with Docker Hub][ref-ce-third-party-private-registries] makes their rate limit apply per user instead.

## Using SSH through the proxy server 

While use of the proxy server is transparent for most use cases, others need additional configuration for compute nodes.
An example is cloning git repositories from GitHub over SSH.
Cloning over https works without additional configuration.
To make SSH use the proxy server, add the following to your `~/.ssh/config` file:

``` title="~/.ssh/config"
Match Host *,!148.187.0.0/16,!192.168.0.0/16,!172.16.0.0/12,!10.0.0.0/8exec "hostname -I | grep -vqF 148.187."
    ProxyCommand nc -X connect -x proxy.cscs.ch:8080 %h %p
```

This configuration takes into account that login and compute nodes require a different setup.

??? warning "Error message when cloning without the proxy set up for SSH"
    When cloning a git repository without the correct SSH configuration, cloning will time out as follows:
    ```bash
    [daint][<user>@daint-ln001 ~]$ git clone git@github.com:open-mpi/ompi.git
    Cloning into 'ompi'...
    ssh: connect to host github.com port 22: Connection timed out
    fatal: Could not read from remote repository.

    Please make sure you have the correct access rights
    and the repository exists.
    ```

## Accessing the public IP of a node

When on a login node configured with a public IP address, you can retrieve the public IP address for example as follows:

```bash
[daint][<user>@daint-ln001 ~]$ curl api.ipify.org
148.187.6.19
```
