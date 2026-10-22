DNS translates a human-readable domain name like example.com into the IP address of the server that hosts it. Computers communicate using IP addresses, but people remember names, so DNS acts as the internet's phonebook. It is important to understand that DNS only returns the IP address. It does not fetch any content itself. Once the client has the IP, it opens a TCP connection to that address (with a TLS handshake on top for HTTPS) and sends an HTTP request. The server then responds with the actual text, images and videos.

## How Resolution Works

![DNS](../../../../assets/excalidraw/System Design/Fundamentals/Networking/DNS.excalidraw)

When a browser or app needs to reach a domain, it first has to resolve that hostname into an IP. The lookup starts locally, at the browser cache, then the OS cache (handled by a small component called the stub resolver), and then the router. If none of them know the answer, the stub resolver forwards the query to a recursive resolver, which is usually run by the ISP or a public service such as Google (8.8.8.8) or Cloudflare (1.1.1.1).

The recursive resolver also keeps a cache, and since it serves a huge number of users, most popular domains are already cached there. This is why the majority of lookups never go beyond this point. When the resolver does not have the answer, it starts at the top of the DNS hierarchy and works its way down. It asks a root server, which does not know the IP but replies with the addresses of the TLD servers responsible for the extension (.com, .org, .in). The resolver then asks the TLD server, which replies with the authoritative name servers for that specific domain. Finally the resolver asks the authoritative server, which holds the real records and returns the IP address. The resolver caches this answer for a limited time, passes it back to the client, and the client connects to the server.

### Recursive vs Iterative Resolution

These two terms describe who does the work. From the client's point of view the query is recursive: the client asks the resolver once and waits until it gets a final answer or an error. The resolver, however, performs iterative queries against the root, TLD and authoritative servers. In iterative resolution, each server does not chase the answer on the resolver's behalf. It simply replies with either the answer or a referral saying who to ask next. This is also why a root server should never be described as returning the IP address. It only points the resolver one level down.

## The DNS Hierarchy

DNS is a distributed, hierarchical database, and that design is the reason it scales to the entire internet. No single server knows every domain. Responsibility is delegated level by level: root servers know where the TLD servers are, TLD servers know where the authoritative servers for each domain are, and authoritative servers know the actual records.

There are 13 logical root server identities, but each one is served by many physical machines spread across the world using anycast, where the same IP address is announced from multiple locations and traffic reaches the nearest one. Zones are also replicated across primary and secondary name servers, so the loss of one machine does not take a domain offline.

## Caching and TTL

Caching exists at every layer, and TTL (Time To Live) is the setting that controls it. Every DNS record carries a TTL, which tells caches how long they may reuse the answer before asking again. This creates the main trade-off in DNS. A low TTL means changes and failovers take effect quickly, but resolvers send more queries to the authoritative servers. A high TTL reduces load and speeds up lookups, but changes to a record take a long time to reach everyone.

The commonly heard phrase "DNS takes 24 to 48 hours to propagate" is really just old cached answers living out their TTL. Nothing is being pushed across the internet. Because of this, the standard practice before a migration is to lower the TTL well in advance, make the change, and raise it again afterwards. Failed lookups are cached too, which is called negative caching, so that queries for domains that do not exist do not repeatedly hit the authoritative servers.

## Record Types

DNS stores more than just IP addresses, and each type of record has a different job.

- A: maps a domain to an IPv4 address
- AAAA: maps a domain to an IPv6 address
- CNAME: makes one name an alias of another name
- NS: lists the authoritative name servers for a domain
- MX: lists the mail servers for a domain
- TXT: free-form text, used for domain verification and email policies like SPF

One limitation worth knowing is that a CNAME cannot be placed on the root of a domain (example.com itself), only on subdomains. DNS providers work around this with their own ALIAS or ANAME record types.

## Registrar, DNS Host and Glue Records

People often mix up the registrar and the DNS host. The registrar (GoDaddy, Namecheap) is where you buy the domain, and its job is to tell the TLD which name servers are authoritative for it. The DNS host (Route 53, Cloudflare) is the service that actually stores and serves your records. They can be the same company or different ones.

Glue records solve a circular dependency. If the name server for example.com is ns1.example.com, a resolver would need to resolve example.com to find its own name server. To break the loop, the TLD servers store the IP address of ns1.example.com directly alongside the delegation, so the resolver can reach it without another lookup.

## Transport

DNS queries normally use UDP on port 53 because it is fast and the messages are small. When a response is too large for a UDP packet, the query falls back to TCP. Plain DNS is unencrypted, so modern setups use DoH (DNS over HTTPS) or DoT (DNS over TLS) to stop others on the network from seeing or tampering with the queries.

In system design, DNS is more than a lookup service. It is often the first layer of traffic routing. With GeoDNS or latency-based routing, the authoritative server returns a different IP depending on where the user is, sending them to the nearest data center. CDNs depend on exactly this: the DNS answer points the user to a nearby edge server instead of the origin. DNS can also do simple load balancing by returning multiple IPs for one domain (round robin), though full load balancing is a separate topic handled by dedicated load balancers.

DNS also supports failover. Managed services like Route 53 run health checks and stop returning the IPs of unhealthy servers. The limitation is that caching makes this slow, since clients and ISPs may keep using the old IP until the TTL expires, and you cannot force them to refresh. DNS providers are also a single point of failure. The 2016 attack on Dyn took down many major websites at once, so important systems often use multiple DNS providers.

Two more uses come up in practice. Split-horizon (private) DNS gives internal clients different answers from external ones, for example resolving a service to a private IP inside a company network. And inside clusters, DNS acts as service discovery: Kubernetes CoreDNS and Consul let services find each other by name instead of hard-coded IPs.

## Security

DNS was designed in a time when trust was assumed, so it has several known weaknesses. In cache poisoning (or DNS spoofing), an attacker injects a fake record into a resolver's cache so users are sent to a malicious server. DNSSEC defends against this by digitally signing records so resolvers can verify them. In a DNS amplification attack, the attacker sends small spoofed UDP queries that trigger much larger responses aimed at the victim, flooding them with traffic. In DNS hijacking, a compromised resolver or a stolen registrar account is used to redirect a domain's traffic.