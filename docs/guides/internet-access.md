[](){#ref-guides-internet-access}
# Internet Access on Alps

The [Alps network][ref-alps-hsn] is mostly configured with private IP addresses (`172.28.0.0/16`).
Login nodes have public IP addresses which means that they can directly access the internet, while compute nodes access the internet through NAT.

!!! warning "Public IPs are a shared resource"
    Be aware that public IPs, whether on login nodes or through NAT, are essentially a shared resource.
    Many services will rate limit or block usage based on the IP address if abused.
    An example is pulling container images from Docker Hub.
    [Authenticating with Docker Hub][ref-ce-third-party-private-registries] makes their rate limit apply per user instead.

## Accessing the public IP of a node

When on a login node configured with a public IP address, you can retrieve the public IP address for example as follows:

```console
$ curl api.ipify.org
148.187.6.19
```
