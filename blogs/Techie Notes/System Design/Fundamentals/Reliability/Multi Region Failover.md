A **multi-region architecture** runs a system across two or more geographically separate cloud regions (or datacentres) so that it can survive the loss of an entire region, serve users with lower latency, and meet data residency requirements.

This is one of the hardest topics in system design. It touches networking, data consistency, deployment, operations and cost all at once. It builds on the disaster recovery notes (RPO, RTO, backup and replication basics) and the resilience patterns notes (health checks, circuit breakers, graceful degradation), and it is usually the most expensive answer to the question "how available do we need to be?"

## Purpose of Multi Region

|Category|Item|Explanation|
|---|---|---|
|**Reasons to do it**|Survive a regional outage|Whole-region failures are rare but real (power, network, control-plane or software failures). Multi-AZ does not protect against these.|
||Strict RTO / RPO or availability targets|If the SLO is higher than a single region’s realistic availability (roughly 99.9 to 99.99 percent), you need more than one region.|
||Lower latency for global users|Serve users from the nearest region. Speed-of-light limits mean distance matters (Mumbai to London is roughly 110 to 130 ms round trip, to US East 180 to 220 ms).|
||Data residency and sovereignty|Laws may require data to stay in a country or bloc (GDPR, India’s DPDP Act, sector rules).|
||Regulatory or contractual requirements|Financial regulators, large customers, or government work may mandate geographic redundancy.|
||Provider or capacity risk|Reduced dependence on one region’s capacity or a single control plane.|
||Maintenance and migration flexibility|Drain a region to upgrade, migrate or test.|
|**Reasons not to (or to delay)**|Complexity multiplies|Data consistency, deployment, debugging, and incident response are all harder.|
||Cost|Typically 1.5x to 2.5x or more (duplicate infrastructure, cross-region data transfer, extra operations effort).|
||Most outages are not regional|Bad deployments, configuration errors, dependency failures and software bugs hit every region at once. Multi-region does not fix them, and a poorly managed multi-region setup can increase the risk of those errors.|
||Failover path is rarely exercised|It often fails when needed.|
||Multi-AZ may be enough|Many businesses are well served by multi-AZ plus good backups. A well-built multi-AZ design commonly delivers 99.9 to 99.99 percent availability.|

## Region, Zone and failure domain basics
|Term|Meaning|Typical failure it contains|
|---|---|---|
|**Host / rack**|A single machine or rack|Hardware faults|
|**Availability zone (AZ)**|An isolated datacentre (or group) within a region, with independent power, cooling and networking, connected by low-latency links (usually under 2 to 5 ms)|Datacentre fire, power or network failure|
|**Region**|A geographic area containing multiple AZs, tens to thousands of km from other regions|Regional power, networking, control-plane or natural disaster|
|**Cloud provider**|The whole provider|Provider-wide failure, account or billing problems|
|**Global / control plane**|Services that are global or centralised (IAM, DNS, some management APIs)|Global dependency failures|

- **Multi-AZ is synchronous-friendly** (low latency), while **multi-region is not** (tens to hundreds of ms), which is why consistency becomes the central problem.
- Check the **hidden regional or global dependencies** of "global" services. Some depend on a single region's control plane (for example, historically, certain IAM or console operations in a "home" region). Design failover so it **does not depend on the control plane of the region that is failing.**
- **Regions are not always as independent as they appear** (shared backbone networks, shared software versions, shared deployment pipelines). Software-level correlated failures are common.

## Architecture Patterns
### Active-passive (primary / standby)

```
             ┌────────────── Global traffic manager (DNS / GLB) ──────────────┐
             │                                                                │
        100% traffic                                                   0% traffic (standby)
             ▼                                                                ▼
   ┌─────────────────┐        async replication         ┌─────────────────┐
   │  Region A       │ ───────────────────────────────► │  Region B       │
   │  (primary)      │                                  │  (standby)      │
   │  App + DB (RW)  │                                  │  App + DB (RO)  │
   └─────────────────┘                                  └─────────────────┘
```

- All writes go to the primary. The standby receives replicated data and is promoted on failover.
- **Pros:** simpler consistency (a single writer), easier to reason about, lower cost than active-active.
- **Cons:** standby capacity may sit idle (or be unproven), failover takes time, async replication risks data loss (RPO above zero), and the standby can quietly rot if never exercised.
- **Variants:** _pilot light_ (compute mostly off), _warm standby_ (scaled-down), _hot standby_ (full size), and _active-passive with read-local_ (the standby serves reads only, which exercises it and reduces latency, but reads may be stale).

### Active-active (all regions serve traffic)

```
        Users ──► Global traffic manager (latency / geo routing) ◄── Users
                         │                              │
                         ▼                              ▼
              ┌─────────────────┐   bi-directional   ┌─────────────────┐
              │  Region A       │ ◄────────────────► │  Region B       │
              │  App + DB (RW)  │   replication      │  App + DB (RW)  │
              └─────────────────┘                    └─────────────────┘
```

- Every region accepts traffic, and often writes. If one fails, the others absorb its load.
- **Pros:** best availability and latency, no cold standby, failover is mostly "stop routing to the bad region", and the capacity is in constant use and constantly proven.
- **Cons:** the data consistency problem is hard (multi-writer conflicts), higher cost and operational complexity, and each region must be able to **absorb the failed region's load** (so each runs below about 50 to 60 percent capacity with two regions, or you accept degradation).

### Active-active variants (very important to distinguish)

|Variant|How writes work|Consistency|Notes|
|---|---|---|---|
|**Active-active reads, single-writer region**|Reads served locally everywhere. Writes forwarded to one home region.|Strong for writes, local reads may be stale|Common and pragmatic. Writes pay cross-region latency.|
|**Partitioned / home-region (geo-sharded)**|Each user, tenant or entity has a **home region** that owns its writes. Other regions hold replicas for failover.|Strong within an entity's home|Avoids write conflicts by design. Needs routing by entity and a failover plan per partition.|
|**Multi-writer with conflict resolution**|Any region accepts any write. Changes replicate asynchronously and are merged.|Eventual (with conflict resolution)|Highest availability and lowest write latency, but the app must tolerate conflicts.|
|**Globally consistent database**|A distributed consensus database spanning regions|Strong (linearisable or externally consistent)|Spanner, CockroachDB, YugabyteDB. Higher write latency (cross-region quorum), simpler app logic.|

### Cell-based architecture

Divide the system into independent **cells** (each a full stack serving a subset of users). Cells can be placed in different regions, and a failure or bad deploy affects only that cell's users ("blast radius reduction"). Combined with multi-region, a cell has a **primary region and a failover region**. This is used by large providers to keep failure domains small.

### Choosing between active-passive and active-active

|Question|Points toward|
|---|---|
|Can we tolerate minutes of downtime and a little data loss?|Active-passive (warm standby)|
|Do we need near-zero RTO and seconds-of-RPO?|Active-active (or hot standby with sync-ish replication)|
|Is data naturally partitionable by user, tenant or geography?|Active-active with home regions|
|Is the data highly shared and write-heavy with global contention?|Single-writer region, or a globally consistent database|
|Can the app tolerate eventual consistency and merge conflicts?|Multi-writer active-active|
|Do we have strong ops maturity and testing culture?|Active-active is viable|
|Is cost a major constraint?|Pilot light or warm standby|

## Traffic routing and Failover
Getting users to the right region, and moving them when a region fails, is a big part of the problem.

### Routing mechanisms

|Mechanism|How it works|Failover speed|Notes|
|---|---|---|---|
|**DNS-based routing** (Route 53, Azure Traffic Manager, Cloudflare, NS1)|Returns different IP addresses based on health, latency, geography, weight|Limited by **TTL** and resolver caching (seconds to minutes, sometimes longer)|Simple and universal. Some clients and resolvers ignore low TTLs. Use short TTLs (30 to 60 s) for failover records.|
|**Anycast / global load balancers** (Google Cloud Global LB, AWS Global Accelerator, Cloudflare, Azure Front Door)|One IP advertised from many locations. Traffic enters at the nearest edge and is forwarded over the provider backbone to a healthy backend.|**Seconds** (no DNS caching problem)|Faster failover and better performance. Provider-specific.|
|**CDN with origin failover**|The CDN has primary and secondary origins and fails over on errors|Seconds to tens of seconds|Great for web and static or cacheable content|
|**Client-side routing / SDK logic**|The client holds a list of endpoints and retries on another|Fast, under client control|Common for mobile apps and APIs. Needs careful rollout and endpoint discovery.|
|**BGP / network-level**|Withdraw or announce routes|Fast but operationally heavy|Typically for large operators|
|**Service mesh / multi-cluster**|Mesh routes across clusters and regions (Istio, Linkerd, Cilium Cluster Mesh)|Seconds|Internal service-to-service traffic|

### DNS Routing policies
|Policy|Use|
|---|---|
|**Failover**|Primary and secondary. Switch when health checks fail (active-passive).|
|**Latency-based**|Send users to the region with the lowest latency (active-active)|
|**Geolocation / geoproximity**|Route by user location, for residency or to bias traffic|
|**Weighted**|Split a percentage of traffic. Good for gradual shifts, canarying a region, and drains.|
|**Multi-value / multi-answer**|Return several healthy IPs|

Cavets:
- **TTL is a hint, not a guarantee.** Resolvers, operating systems, browsers, JVMs and corporate proxies often cache longer. Expect a long tail of clients using the old address for minutes to hours.
- **Health checks** should be reliable and from multiple vantage points, and ideally check **real functionality** (a deep check of the critical path), not only that a port is open. But avoid checks so deep that a minor dependency failure triggers a full regional failover.
- **DNS provider availability matters.** Use a highly available DNS service, possibly multiple providers for critical domains. The DNS control plane may be unavailable in a regional event, so **pre-configure automated failover records** rather than relying on making changes manually during the incident.
- Prefer **health-check-driven automatic DNS failover** for the data plane, but be careful about flapping. Add hysteresis.

## Data layer
The application tier is typically easy to run in several regions. The **data tier** determines whether failover is safe and how much data you lose.

### Approaches

|Approach|RPO|Write latency|Notes|
|---|---|---|---|
|**Asynchronous cross-region replication**|Seconds to minutes (the lag)|Unaffected|Most common. Data loss on failover equals replication lag.|
|**Synchronous cross-region replication**|Zero|Every write pays a cross-region round trip (often 50 to 200+ ms)|Rare across distant regions. Availability risk if the remote region is unreachable (writes may block).|
|**Quorum / consensus across regions**|Zero (committed data survives the loss of a minority)|Higher write latency (waits for a majority across regions)|Spanner, CockroachDB, YugabyteDB, etcd-style systems. Needs 3 regions (or 3 failure domains) to tolerate loss of one.|
|**Multi-writer with eventual consistency**|Near zero, but with possible conflicts|Local writes are fast|DynamoDB Global Tables, Cassandra multi-DC, Cosmos DB multi-region writes|

### Data store choices
|Store|Multi-region options|
|---|---|
|**Relational (PostgreSQL, MySQL)**|Cross-region async read replicas with manual or orchestrated promotion. Managed: Aurora Global Database (typically under 1 s lag, fast managed failover), Cloud SQL cross-region replicas, Azure SQL failover groups.|
|**Globally distributed SQL**|Google Spanner, CockroachDB, YugabyteDB, TiDB. Strong consistency, multi-region survival goals, but higher write latency and a different operational model.|
|**Key-value / document NoSQL**|DynamoDB Global Tables (multi-active, last-writer-wins), Cosmos DB (selectable consistency levels, multi-region writes), MongoDB Atlas global clusters, Cassandra and ScyllaDB multi-DC|
|**Object storage**|S3 Cross-Region Replication, GCS dual- and multi-region buckets, Azure geo-redundant storage. Usually asynchronous.|
|**Caches**|Typically per-region (rebuild on failover). Global options: Redis Enterprise Active-Active (CRDT-based), ElastiCache Global Datastore|
|**Message queues and streams**|Kafka MirrorMaker 2 or Cluster Linking, Kinesis cross-region, Pub/Sub global, SQS is regional (replicate with app-level logic). Consumer offset translation needs care.|
|**Search indexes**|Cross-cluster replication, or rebuild from the source of truth|
|**File systems**|EFS replication, Azure Files GRS, FSx replication|

1. **What is the source of truth for each dataset,** and which region owns writes?
2. **What RPO is acceptable per dataset?** Payments may need zero loss, while analytics may tolerate hours.
3. **Can the data be partitioned by owner** (user, tenant, geography) so that conflicts cannot happen?
4. **What happens to writes in flight** (not yet replicated) when a region fails? Are they lost, reconciled later, or recoverable from the failed region once it returns?
5. **What consistency do reads need?** Can a user read stale data after failover? Do they need read-your-writes?
6. **How do derived and secondary systems behave** (caches, search indexes, queues, analytics)? Can they be rebuilt in the target region, and how long does that take?

### Data loss on async failover
When you fail over from a region with asynchronous replication, **writes committed in the failed region but not yet replicated are not in the new primary.** Options:

- **Accept the loss** (document RPO).
- **Reconcile later:** when the old region recovers, extract the missing transactions, review them, and replay or compensate (manual or automated, which needs conflict handling since new writes occurred).
- **Reduce the window:** lower lag with a better network, tuned replication, and smaller transactions.
- **Business-level mitigation:** idempotent clients, retries with idempotency keys, user-visible "pending" status, event sourcing from a durable log that is itself replicated, or an outbox pattern.
- **Synchronous or quorum replication** for the data that cannot be lost, with the latency cost.

Note: Refer CAP and PACELC Theorem before proceeding

### Conflict Resolution

|Strategy|How it works|Pros|Cons|
|---|---|---|---|
|**Avoid conflicts (partition ownership)**|Each entity has a single home region for writes|No conflicts|Needs routing by entity. Failover of the partition must be handled|
|**Last-writer-wins (LWW)**|Highest timestamp wins|Simple, automatic|Silently discards writes. Depends on clock accuracy and ordering|
|**Version vectors / vector clocks**|Detect concurrent updates and surface both versions|Detects conflicts accurately|The app must merge. Complexity|
|**CRDTs (conflict-free replicated data types)**|Data structures that merge deterministically (counters, sets, registers, maps)|Automatic, convergent, no lost updates for supported types|Limited data types, semantic design needed|
|**Application-level merge**|Custom logic (for example, merge shopping carts by union)|Fits the domain|You must write and test it|
|**Operational transformation / event sourcing**|Replicate operations or events and re-apply|Rich, auditable|Complex|
|**Single-writer for specific invariants**|Route the sensitive operations (for example, payments) to one region|Preserves invariants|Higher latency, availability tied to that region|

**Invariants that cross entities are the hard cases:** uniqueness (usernames, emails), balances that must not go negative, inventory that must not oversell. These need a **single authority or consensus**, because merge-based replication can't enforce them. Typical solutions are routing those operations to a home region, using a globally consistent database, or using compensating actions (such as refunding an oversold item).

**Clock caveats:** don't trust wall clocks for ordering across regions without care. Clock skew breaks LWW. Use hybrid logical clocks, or TrueTime-style bounded clocks (Spanner), or version numbers.

## Stateless and Stateful Components
|Component|Multi-region approach|
|---|---|
|**Stateless services**|Deploy identical copies in each region. Easy.|
|**Sessions**|Use stateless tokens (JWT with shared signing keys or JWKS), or replicate session stores, or accept re-login on failover|
|**Authentication / identity**|Identity is critical and must survive a region loss. Use a multi-region identity provider, replicate user stores, and keep signing keys available in every region.|
|**Secrets and keys (KMS)**|Multi-region keys or replicated secrets. Verify that decryption works in the failover region.|
|**Configuration and feature flags**|Distributed to every region, with a fail-static default if the control plane is unreachable|
|**Caches**|Usually regional and rebuilt. Plan for cold-cache load on the database after failover.|
|**Queues and background jobs**|Decide what happens to in-flight messages. Make consumers idempotent. Avoid processing the same job in two regions.|
|**Scheduled jobs / cron**|Run in one region at a time (leader election or per-region ownership), or you get duplicate runs|
|**File uploads / media**|Replicated object storage, with the CDN serving from the nearest copy|
|**Third-party integrations**|Webhooks, payment providers and email services need allowlists, callback URLs and credentials configured for every region|
|**Certificates and domains**|Valid in all regions. Automate renewal in each.|
|**Observability**|Must keep working during a regional outage (see below)|

## Failover Mechanics
### Types
|Type|Description|Pros|Cons|
|---|---|---|---|
|**Automatic**|Health checks and automation switch traffic and promote data without human action|Fastest RTO, works at 3 a.m.|Risk of false positives, flapping, split-brain, premature data-loss decisions|
|**Semi-automatic / human-approved**|Automation detects and prepares, a human approves the key step (for example database promotion)|Balance of speed and safety|Slower, needs on-call responsiveness|
|**Manual**|Humans run a runbook|Deliberate|Slowest. Prone to error under pressure.|

Common practice is **automatic traffic failover for stateless layers** and **human-approved promotion for the primary database** when async replication means data loss is possible. Fully automatic data promotion is reasonable where the loss window is small and well understood, or where the data layer handles it itself (consensus databases, managed global databases).

## Failback
Returning to the original region is often harder than the failover, and it is frequently left unplanned.

|Concern|Guidance|
|---|---|
|**Is it truly healthy?**|Verify the original region thoroughly before returning. Underlying problems may recur.|
|**Data re-sync**|The old primary has diverged: it may hold unreplicated writes, and the new primary has newer data. Typically **re-seed or rewind the old primary as a replica** of the new one, then catch up.|
|**Reconcile lost writes**|Review and replay or compensate for writes that were stranded in the failed region.|
|**Choose the timing**|Fail back during low traffic, with a rollback plan, not in a rush.|
|**Gradual traffic shift**|Use weighted routing to move traffic back incrementally, watching metrics.|
|**Planned switchover (zero data loss)**|Quiesce writes, wait for replication to catch up fully, then promote. Faster and safer than emergency failover because there is no data loss.|
|**Or don't fail back**|Sometimes the old DR region just becomes the new primary and the recovered region becomes the standby. This avoids a second disruptive switch.|
|**Restore redundancy**|Until the recovered region is back in sync, you are running without a standby, so treat it as an elevated-risk period.|

## Split Brain
Two regions both believe they are the primary and accept writes, which causes divergent data that is painful or impossible to merge.

**Causes:** network partition between regions, an overeager automatic failover, an old primary that wasn't fenced and comes back.

**Prevention**
- **Quorum / majority consensus:** require a majority of voters (spread across at least 3 failure domains or regions) to elect or hold the primary role.
- **A witness or arbiter in a third location** to break ties (a third region or independent site).
- **Fencing / STONITH:** ensure the old primary is forcibly stopped, isolated or demoted before the new one is promoted (revoke its credentials, shut off its network, use storage-level fencing, or use leases that expire).
- **Leases and epochs / fencing tokens:** every write carries a monotonically increasing token, and the storage layer rejects writes from stale primaries.
- **Single control authority** for role changes.

## Partial Failures
The hardest failures are not clean outages but **degradation:** elevated latency, packet loss, a single dependency failing, or one-way network problems.

- A region can be "up" by health check but unusable (slow database, high error rate on one service).
- **Cross-region links** can degrade, raising replication lag or breaking quorum without any region being fully down.
- **Asymmetric partitions:** region A can reach B but not vice versa, or each region sees different views of health.
- **Dependency regional failure:** your app is fine, but a payment provider or identity provider in that region is not.

Mitigations: health signals based on **real user-impact metrics** (SLO burn, error rate, latency) rather than only liveness, **per-dependency circuit breakers and fallbacks**, **partial failover** (shift specific traffic classes or only affected tenants), hysteresis to avoid flapping, and clear **human decision points** for ambiguous situations.

## Deployment and configuration across regions
Multi-region increases the blast radius of **bad changes,** since a faulty global rollout can take down every region at once, defeating the purpose.

- **Roll out region by region** (and cell by cell) with bake time and automated health gates: one region (a canary region) first, then others. Never deploy to all regions simultaneously.
- **Keep regions on consistent versions,** but allow controlled version skew during rollouts. Ensure forward and backward compatibility of APIs, schemas and messages (expand and contract migrations).
- **Database schema changes:** must be compatible with both old and new code and work across replicas. Apply carefully with replication in mind.
- **Infrastructure as code** with the same modules per region and region-specific variables, to prevent **configuration drift.** Detect drift automatically.
- **Config and feature flags:** roll out progressively, with per-region control and a kill switch. A global config push is a classic outage cause.
- **Avoid hidden single points of failure:** a single CI/CD system, container registry, artifact store, secrets manager, DNS provider, identity provider or monitoring stack located in one region. Replicate or make them region-independent.
- **Pin and replicate artefacts** (images, packages, models) to each region so deployments and scaling do not depend on a remote region.
- **Quotas and capacity:** parity across regions, verified regularly.

## Observability for multi-region
- **Monitor from outside** each region (external synthetic probes from several locations), so you can see a region's health when it can't report its own.
- **Make telemetry resilient:** metrics, logs and traces pipelines must keep working (or fail gracefully) when a region fails. Use a separate region or provider for the monitoring and paging stack, or at least replicate it.
- **Label everything with region** (and zone, cell, version), so dashboards and alerts can compare regions side by side.
- **Key multi-region signals:**
    - **Replication lag** per link (seconds and bytes), with alerts against RPO
    - Cross-region **latency and packet loss**
    - **Traffic distribution** per region, and capacity headroom in each
    - **Failover readiness:** standby health, config parity, last successful failover test
    - **Per-region SLIs** (error rate and latency) and a **global SLI**
    - Conflict counts and resolution outcomes (for multi-writer)
    - Health-check results from several vantage points
- **Out-of-band communications:** incident chat, paging and the status page must not depend solely on the region that is failing.
- **Distributed tracing across regions** helps diagnose cross-region calls, but beware that cross-region calls in the request path (a service in region A calling a service in region B) hurt latency and create hidden dependencies. Keep request paths **region-local** where possible.

## Testing multi-region failover
|Test|Description|
|---|---|
|**Tabletop exercises**|Walk through scenarios and decisions. Test communication and roles.|
|**Component failover tests**|Fail over a database or service individually, and measure data loss and time|
|**Traffic shift drills**|Move a percentage (then all) of traffic to another region and verify capacity, latency, correctness|
|**Region evacuation / "drain" drills**|Take a region fully out of rotation on a schedule and run entirely from the other(s)|
|**Game days / chaos experiments**|Simulate a regional outage (block network, kill workloads, disable dependencies) in a controlled way|
|**Full DR failover and failback**|Real production switch and return. The only complete proof.|
|**Replication and data integrity checks**|Compare data between regions, verify checksums, test restore from the replica|
|**Unannounced drills**|Check real readiness, with safeguards|

## Latency
- **Cross-region calls are slow and variable,** with round trips of tens to hundreds of milliseconds, plus egress cost. A single request making several sequential cross-region calls becomes unusably slow.
- **Design for region-local request paths:** each request should be served end-to-end within one region, using local replicas, local caches and local queues.
- **Use CDNs and edge compute** for static and cacheable content, and for terminating connections close to users.
- **Route users to the nearest healthy region,** and consider how data placement affects it (a user near Mumbai whose data is homed in Frankfurt is slow for every write).

## Data residency and sovereignty
- Laws and policies may restrict where personal or regulated data is stored or processed (GDPR cross-border transfer rules, India's DPDP Act and sectoral data localisation rules such as RBI's payment data requirements, China's PIPL, and others).
- **Partition by jurisdiction:** keep regulated data in the permitted regions, and make failover **within the allowed boundary** (for example, failing over from one EU region to another EU region, not to the US).
- This can conflict with global failover, so decide which data is subject to residency rules, and design **region pairs or groups** accordingly.
- Consider **metadata and logs,** which may also contain personal data.
- Be careful with backups, replicas, analytics pipelines and support tooling, which can quietly copy data across borders.

## Compliance and Evidence
Regulators in finance, healthcare and government often require documented DR, tested failover and evidence (test results, RTO and RPO achieved). Examples include RBI and SEBI guidance for Indian financial institutions, DORA in the EU, and sector standards such as PCI-DSS, HIPAA, ISO 22301 and ISO 27001. Keep records of drills and results.

## Cost
|Cost driver|Notes|
|---|---|
|**Duplicate compute**|Active-active often means 2x or more capacity (each region must absorb the other's load on failure)|
|**Duplicate data storage**|Full copies in every region|
|**Cross-region data transfer**|Replication traffic, multi-region API calls, log and metric shipping. A major, often surprising cost.|
|**Global services**|Global load balancers, accelerators, global databases (often priced per replicated write)|
|**Licensing**|Standby and multi-region database licences|
|**Operations**|Engineering time for design, automation, testing, drills, and on-call complexity|
|**Observability**|More telemetry, plus separate monitoring infrastructure|
|**Compliance overhead**|Audits and residency controls|

- **Tier by criticality:** active-active only for tier-0 services, warm standby or pilot light for the rest, backups for the least critical.
- **Pilot light or warm standby** with scaling up on failover, accepting a slower RTO.
- **Reserve capacity** in the DR region for critical tiers only (committed discounts for the baseline).
- **Minimise cross-region chatter:** compress replication, replicate only what is needed, process logs locally and ship aggregates.
- **Right-size standby databases** (but ensure they can handle production load after promotion).
- **Quantify the benefit:** compare the added cost to the expected cost of a regional outage (probability x impact), plus the value of latency gains and compliance.

## Cloud Specific Blocks
| Need                           | AWS                                                                                               | Google Cloud                                                                                | Azure                                         |
| ------------------------------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------- |
| **Global traffic routing**     | Route 53 (failover, latency, geo, weighted), Global Accelerator, CloudFront                       | Global external load balancer (anycast), Cloud DNS, Cloud CDN                               | Front Door, Traffic Manager                   |
| **Cross-region relational DB** | Aurora Global Database, RDS cross-region read replicas                                            | Cloud SQL cross-region replicas, AlloyDB cross-region replication, **Spanner multi-region** | Azure SQL failover groups and geo-replication |
| **Global NoSQL**               | DynamoDB Global Tables                                                                            | Firestore multi-region, Bigtable replication                                                | Cosmos DB multi-region writes                 |
| **Object storage replication** | S3 Cross-Region Replication, Multi-Region Access Points                                           | Dual-region and multi-region buckets                                                        | GRS / GZRS, object replication                |
| **Compute DR / replication**   | AWS Elastic Disaster Recovery, AMI and snapshot copy                                              | Regional MIGs, snapshot copy                                                                | Azure Site Recovery                           |
| **Messaging**                  | SNS and SQS are regional (replicate via app logic), EventBridge global endpoints, MSK replication | Pub/Sub (global), Kafka replication                                                         | Service Bus geo-disaster recovery             |
| **Secrets and keys**           | Secrets Manager replication, KMS multi-Region keys                                                | Secret Manager replication, Cloud KMS                                                       | Key Vault replication and paired regions      |
| **IaC and fleet management**   | CloudFormation StackSets, Terraform                                                               | Terraform, Config Controller                                                                | ARM and Bicep, Terraform                      |
| **Failover orchestration**     | Application Recovery Controller (readiness checks, routing controls)                              | Traffic Director, custom automation                                                         | Azure Site Recovery plans                     |


## Flow
```
1. What are the business RTO / RPO / availability targets (per tier)?
        │
        ├─ Hours / hours, cost-sensitive  ──►  Cross-region backups + IaC (backup & restore)
        │
        ├─ ~1 hour / minutes              ──►  Pilot light or warm standby, async replication
        │
        ├─ Minutes / seconds              ──►  Hot standby, managed global DB, automated failover
        │
        └─ Seconds / ~zero, global users  ──►  Active-active
                 │
                 ├─ Data partitionable by user/tenant/geo?  ──► Home-region active-active
                 ├─ Need strong global consistency?          ──► Globally consistent DB (Spanner, CockroachDB)
                 └─ Can tolerate eventual consistency?       ──► Multi-writer + conflict resolution (CRDT/LWW/merge)

2. Do residency rules restrict where data may go?  ──► Constrain region pairs by jurisdiction.
3. Do we have the ops maturity to test and run it? ──► If not, pick the simpler option and mature first.
```