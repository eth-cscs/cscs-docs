[](){#ref-guides-internet-access}
# Internet Access on Alps

The [Alps network][ref-alps-hsn] is mostly configured with private IP addresses (`172.28.0.0/16`).
Login nodes have public IP addresses which means that they can directly access the internet, while compute nodes access the internet through NAT.

!!! warning "Public IPs are a shared resource"
    Be aware that public IPs, whether on login nodes or through NAT, are essentially a shared resource.
    Many services will rate limit or block usage based on the IP address if abused.
    An example is pulling container images from Docker Hub.
    [Authenticating with Docker Hub][ref-ce-third-party-private-registries] makes their rate limit apply per user instead.
    See also the [guidelines below][ref-guides-internet-access-ext]

## Accessing the public IP of a node

When on a login node configured with a public IP address, you can retrieve the public IP address for example as follows:

```console
$ curl api.ipify.org
148.187.6.19
```

[](){#ref-guides-internet-access-ext}
## Guidelines on communicating with external services (web scraping, bulk downloads,…)

Communication with external services from Alps is provided by a high-capacity 400 GBit/s connection to [SWITCH](https://www.switch.ch/en/network/ip-access).
SWITCH provides internet services to the research and education infrastructure in Switzerland.

However, communication with external services is not the focus of CSCS, it is rather seen as a way to enable the use of our resources, so for example as explained below from Alps **do not** put load on services that do not expect it, for example through **scraping**.

### Shared resources

If you need to heavily interact with external systems there are some caveats that you have to keep in mind, in general some resources are shared resources, and a single user should not monopolize their use.

To avoid abuse there are measures in place at CSCS, on the transit networks, and on the remote systems, but these measures are often very blunt and would affect the CSCS as whole, so care should be taken to avoid triggering them.
We have a good relationship with SWITCH, so if we trigger some of their fail-safes (for example their anti-DDoS tools), they will contact us. Other might take action without telling us anything.

For example a website might blacklist IPs, or whole subnets from CSCS, which would make the service unavailable for all other CSCS users too.
Many sites use content delivery networks (CDN), like Cloudflare, Akamai, or similar, and if those blacklist the CSCS many users will be affected.
In addition, once we are blacklisted, it's extremely difficult and long be able to get out of these blacklists.

!!! info
    Sites do not publish the number of requests/queries per second that trigger blacklisting, for some obvious reason that bad-intentioned people would stay just below this limit.

So you should be mindful of your usage, in particular of the number of requests to the DNS and the network bandwidth.
Every access to a different domain will trigger a DNS request, using multiple nodes does not solve the problem, because they will still be hitting the same DNS resolver.

CSCS has protection in place for our public DNS server, but other DNS servers might decide to blacklist the originator of all those requests.
Alps uses an internal DNS, which is also used to resolve the different nodes in alps, and does not have special protections against abuse.
For this reason **avoid scraping from Alps**, as it could lead to it being blacklisted.

!!! warning
    The high-capacity of the CSCS-SWITCH connection can saturate the connection of a large provider like Google, which would affect all Swiss Google users.

### Conclusions

Before any large scale sustained use of external resources think carefully about the load you are putting on the CSCS, network and target, both in number of requests and size of the request.

Try to change the perspective: how quickly do you really need the whole data? Can you or should you use resources outside Alps, or even outside CSCS? Maybe geo-distributed?

Also reach out to us, so that we are aware of what you are doing, and react quickly if we reach out to you. This last part worked well until now, and it is important that it continues to work well.

Even if you did your homework and calculated that your load is acceptable it is important to understand that at the end it's the aggregated load across all users that counts, and if suddenly many users add an "acceptable" load it might not be so acceptable after all.

Finally here we do not touch the legal aspect of the data collection which we expect you to clear separately: copyright/licensing issues, and storage of data that might contain private information, and consequently needs to be handled with due diligence to avoid data breaches.

We want to support your ground breaking research, let's work together to find an acceptable solution for everybody, in the end being ethical is also about this.
