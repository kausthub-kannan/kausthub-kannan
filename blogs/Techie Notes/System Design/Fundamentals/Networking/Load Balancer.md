A load balancer is a system that distributes incoming traffic across multiple servers so that no single server gets overloaded. Clients send requests to one address, the load balancer's, and it decides which backend server should handle each request. This keeps the application fast because the work is spread out, and it improves availability because if one server fails, the load balancer simply stops sending traffic to it and the others keep serving users. It also lets the system handle a very large number of simultaneous users, since capacity can be increased by adding more servers behind the load balancer (horizontal scaling) instead of buying one ever-bigger machine.

![Load Balancer](../../../../assets/excalidraw/System Design/Fundamentals/Networking/Load Balancer.excalidraw)

## Types

### By Implementation
1. **Hardware load balancer:** Dedicated physical device built only for distributing traffic. These are very powerful and can handle enormous volumes with high performance, but they are expensive and harder to scale, so they are mostly used by large companies and data centers. F5 is a well-known example.

2. **Software load balancer:** Ordinary program that runs on a normal server, typically Linux, and does the balancing in software. NGINX and HAProxy are the most common examples. It is far cheaper and more flexible than hardware, and it can be scaled or reconfigured easily, which is why it is the most commonly used option. In some setups the same server that does other jobs also runs the load balancing software.

3. **Cloud load balancer:** Managed service run by a cloud provider, such as AWS Elastic Load Balancing, Google Cloud Load Balancing or Azure Load Balancer. The provider handles scaling, patching and availability of the load balancer itself, and you pay for usage. For most modern systems this is the default choice because there is nothing to maintain.

### By OSI Layer
1. **Layer 4:** A Layer 4 load balancer works at the transport layer. It looks only at information like the source and destination IP address, port and TCP or UDP protocol, and forwards the connection without looking at the content of the request. Because it does so little inspection, it is very fast and efficient, but it is not smart: it cannot tell the difference between a request for an image and a request for an API call.

2. **Layer 7:** A Layer 7 load balancer works at the application layer. It can read the actual HTTP request, including the URL path, headers, cookies and API details, and make routing decisions based on them. For example, it can send /api traffic to one group of servers and /images traffic to another, route a user to the same server based on a cookie, or send mobile and desktop users to different backends. This makes it much smarter and more flexible, at the cost of more processing per request, so it is slightly slower than Layer 4.

## Load Balancer Algorithms

The choice of server is made by a balancing algorithm, and the right one depends on the workload.

- Round robin: requests go to each server in turn. Simple, and works well when servers are equal and requests are similar.
- Weighted round robin: stronger servers receive proportionally more requests.
- Least connections: the request goes to the server currently handling the fewest active connections. Good when requests take uneven amounts of time.
- IP hash: the client's IP decides the server, so the same client keeps reaching the same server.
- Consistent hashing: used when servers are added or removed often, such as with caches, because only a small share of keys move to a different server.

## Sticky Sessions
Some applications store user session data on the server itself, so a user must keep reaching the same server or their session is lost. Sticky sessions (session affinity) solve this by pinning a user to one server, using a cookie or the client IP. The drawback is that load becomes uneven and a failing server loses its users' sessions. The better design is to make servers stateless and keep session data in a shared store such as Redis, so any server can handle any request.

## Features of LB

Many load balancers do more than distribute traffic. Layer 7 load balancers can cache frequently requested content and serve it directly without involving the backend, which reduces load and speeds up responses, although dedicated caches and CDNs usually do this job better. They commonly perform SSL/TLS termination, meaning they handle the encryption work so backend servers do not have to. They can also rate limit abusive clients and act as a reverse proxy that hides the backend servers from the public internet, which improves security.

### Server status check
A load balancer constantly checks whether each backend server is healthy, either by pinging it or by requesting a specific health endpoint at regular intervals. If a server fails the check, it is taken out of rotation automatically, and it is added back once it recovers. This is the mechanism behind the high availability of a load-balanced system, and it is why users usually never notice a single server crashing.

### Anycast 
A network routing technique, not a load balancing algorithm. The same IP address is announced from many locations around the world, and the internet's routing (BGP) delivers each user's traffic to the nearest location advertising that address. This lets multiple servers in different places sit behind the same IP while each user reaches the closest one. It is how DNS root servers and many CDNs work, and it is a major reason global services respond quickly and survive the loss of a location.

### Regional routing
A regional load balancer distributes traffic across servers inside a single region, which in cloud terms usually means several data centers called availability zones that sit close together. A user's request reaches the load balancer, which spreads it across servers in different zones (Example: us-east-1, us-east-2). Because the zones are physically separate but connected by fast links, the system survives the loss of a server, a rack or even a whole zone, and users see very low latency between the load balancer and the backends. AWS Application Load Balancer and Network Load Balancer are examples, and they typically work at Layer 4 or Layer 7 as described above.

The limit of a regional load balancer is that it only knows about its own region. If the entire region goes down, whether from a power failure, a network problem or a cloud outage, the regional load balancer goes down with it, and it cannot help users who are physically far from that region and suffer high latency simply because of distance.

### Global routing
A global load balancer distributes traffic across multiple regions around the world. It exists to solve problems a regional balancer cannot. The first is latency: a user in India should be served from Mumbai, not Virginia, because the speed of light and the number of network hops add real delay. The second is disaster recovery: if a whole region fails, traffic is moved to a healthy region. The third is compliance, since some laws require that data of users in certain countries stays inside that country. The fourth is capacity, since traffic can be shifted between regions when one is overloaded or when a new release is being rolled out gradually.

Global balancing usually works in two tiers. The global layer decides which region a user should go to, and then the regional load balancer in that region decides which server handles the request. The global layer is built with one of three techniques: GeoDNS or latency-based DNS routing, anycast, or a global proxy network such as Google Cloud's global load balancer or Cloudflare, which uses anycast to give the whole world one IP address and then forwards requests to the best backend region.

---

Since all traffic passes through the load balancer, the load balancer itself must not be the weak point. The usual solution is to run at least two in an active-passive or active-active pair, so another one takes over if one fails. Cloud load balancers do this automatically behind the scenes. For global systems, a second layer of balancing, such as DNS or anycast, spreads traffic across the load balancers themselves.


### Note on GeoDNS
GeoDNS is DNS that returns different answers depending on where the query comes from. When a recursive resolver asks the authoritative server for example.com, the authoritative server looks at the source IP of the query, maps it to a location using a geo-IP database, and returns the IP address of the region chosen for that location. A resolver in Mumbai might get the IP of the Mumbai data center while a resolver in Frankfurt gets the IP of the Frankfurt data center, even though both asked for the same domain name. The load balancing decision therefore happens at DNS time, before the client has even connected to anything.

Providers such as Route 53, Cloudflare and NS1 offer several routing policies, and they can be combined.

- Geolocation routing: users from a given country or continent always go to a specified region. Useful for compliance and for regional content.
- Latency-based routing: the provider measures real network latency from different parts of the internet to each region and returns the region with the lowest latency. This is often better than pure geography, because the closest region on the map is not always the fastest.
- Weighted routing: a percentage of traffic goes to each endpoint, useful for gradual rollouts and testing.
- Failover routing: health checks monitor the primary region, and if it fails, DNS starts returning the IP of the backup region.

GeoDNS has real limitations. The authoritative server sees the location of the resolver, not the user, so someone in India using a resolver based in the US may be sent to the wrong region. An extension called EDNS Client Subnet partly fixes this by passing part of the user's network address along, but it is not universally supported. Geo-IP databases are also not perfectly accurate. Caching is the biggest issue: because answers are cached for the length of the TTL, a failover is not instant, and some users keep going to the dead region until their cache expires. Finally, DNS has no idea how busy a server currently is, so it distributes by location and policy, not by live load.

It helps to contrast GeoDNS with anycast. With GeoDNS, different locations receive different IP addresses, and DNS does the steering. With anycast, there is one IP address announced from many places, and the network routing steers each user to the nearest one. Anycast reacts faster to failures because routing updates immediately, without waiting for DNS caches to expire, while GeoDNS gives more explicit control through policies. Large systems often use both.

## Load balancer as Reverse proxy
To understand this, start with the two kinds of proxy. A forward proxy sits in front of clients. Users send their requests to it, and it makes requests to the internet on their behalf, which hides the identity of the clients, for example in a corporate network or a VPN. A reverse proxy sits in front of servers. Clients send their requests to it believing it is the real server, and it quietly forwards the request to a backend server and returns the response. The client never talks to the backend directly and may not even know it exists.

A Layer 7 load balancer is exactly this. It accepts the client's connection and ends it there, reads the HTTP request, picks a backend server using its algorithm, opens a separate connection to that backend, forwards the request, and then relays the response back to the client. Because it is a full proxy with two separate connections, it can do far more than distribute traffic. It hides the IP addresses and structure of the backend servers, which improves security. It can terminate SSL/TLS so backends do not need to handle encryption. It can route by URL path or header, compress responses, cache content, rate limit clients, and block malicious requests when combined with a web application firewall. It can also reuse long-lived connections to the backends, which lowers the cost of handling many short client connections.

One practical detail is that the backend now sees the load balancer's IP address as the source of every request, not the real client's. To keep the client's address available for logging and security rules, the proxy adds a header such as X-Forwarded-For containing the original IP.

The two terms are related but not identical. Every Layer 7 load balancer is a reverse proxy, but a reverse proxy is not necessarily a load balancer, since a reverse proxy in front of a single server only provides security, caching and SSL termination without distributing anything. A Layer 4 load balancer may not behave as a full proxy at all, since some simply forward packets without creating a separate backend connection. Tools like NGINX and HAProxy are used as both reverse proxies and load balancers, which is why the terms are often used interchangeably in practice.