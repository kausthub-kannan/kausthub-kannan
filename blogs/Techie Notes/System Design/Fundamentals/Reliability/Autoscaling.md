**Capacity planning** is the practice of making sure a system has enough resources (compute, memory, storage, network, database throughput, third-party quota) to meet demand with acceptable performance and cost, both today and in the future.

**Autoscaling** is the automatic adjustment of resources in response to demand. It is the _reactive_ half of capacity management, while planning and forecasting are the _proactive_ half. You need both: autoscaling handles the variation you can't predict, and planning handles the limits, lead times and costs that autoscaling can't.

|Layer|Timescale|Question it answers|
|---|---|---|
|Capacity planning|Weeks to months|"Will we have enough, and what will it cost?"|
|Autoscaling|Seconds to minutes|"How many instances do we need right now?"|
|Load shedding / back-pressure|Milliseconds|"What do we do when demand exceeds what we have right now?"|

Autoscaling alone is not a substitute for planning. New capacity takes time to arrive (provisioning, startup, warm-up), and there are hard limits (quotas, database connections, downstream services) that autoscaling can't push past.

## Capacity Planning
1. **Understand demand:** what drives load (requests, users, data volume, batch jobs), and its patterns (daily, weekly, seasonal, event-driven).
2. **Measure the cost of one unit of work:** how much CPU, memory, I/O and network a request or job needs.
3. **Find each component's limit:** through load tests and production data (see the next section).
4. **Forecast demand:** from history, growth trends and business plans.
5. **Calculate required capacity:** forecast demand x cost per unit, plus headroom.
6. **Compare with current capacity,** identify gaps, bottlenecks and lead times.
7. **Act:** provision, reserve, re-architect, or optimise.
8. **Review regularly,** and feed back real numbers.

|Resource|What to watch|
|---|---|
|**Compute (CPU)**|Utilisation, run queue, throttling (especially cgroup/container CPU limits)|
|**Memory**|Usage, swap, OOM kills, garbage collection pressure|
|**Storage**|Capacity, growth rate, IOPS, throughput, latency, inode counts|
|**Network**|Bandwidth, packets per second, connection counts, NAT gateway limits, cross-AZ traffic|
|**Database**|Connections, query throughput, replication lag, lock contention, storage growth|
|**Caches**|Memory, hit ratio, eviction rate, connection count|
|**Queues and streams**|Throughput, partitions, consumer lag, retention storage|
|**Third-party APIs**|Rate limits, quotas, per-second caps|
|**Cloud quotas**|vCPU limits, IP addresses, load balancer counts, API rate limits|
|**People and process**|On-call load, support volume (often forgotten, but real capacity constraints)|

### Measuring Demands
Pick **meaningful demand metrics** that map to resource use:

- Requests per second (RPS), broken down by endpoint type (reads vs writes, cheap vs expensive)
- Concurrent users or sessions
- Messages per second, bytes per second
- Jobs per hour, records processed
- Business drivers: orders, sign-ups, active customers, GB stored

Then derive the **resource cost per unit**, for example "1 vCPU handles about 150 RPS of the product API at p99 under 200 ms."

### Forecasting methods
|Method|Description|Good for|
|---|---|---|
|**Trend extrapolation**|Linear or exponential fit on historical growth|Steady growth|
|**Seasonality-aware time series**|Models daily, weekly and yearly cycles (Holt-Winters, Prophet, ARIMA)|Cyclical demand|
|**Business-driven (bottom-up)**|Convert the sales, marketing and product plan into load (for example "10x users after launch")|Launches, campaigns, new markets|
|**Event-based**|Specific known peaks (sales events, festivals, tax deadlines, sports finals, exam results)|Predictable spikes|
|**Scenario / what-if**|Best, expected and worst cases|Uncertain situations|
|**Queueing and performance models**|Use theory to predict behaviour as utilisation rises|Understanding non-linear effects|

- Use **peak** load, not just averages. You provision for the peak (or the percentile you commit to).
- Include **growth in data and per-user activity**, not only user count.
- Track **forecast accuracy** and improve the model over time.
- Always forecast with **ranges**, not one number.
- Include seasonality that matters for your market (for example Diwali and festive sales in India, Black Friday, end-of-quarter, tax season).

### Headroom and target utilisation
Never plan to run at 100 percent. Queueing theory shows latency grows **non-linearly** as utilisation approaches saturation: at 50 percent busy, waits are modest; at 90 percent they are many times longer; near 100 percent they explode.

|Resource|Common target utilisation at peak|
|---|---|
|Stateless app CPU|50 to 70 percent|
|Databases|40 to 60 percent (they degrade badly under load and scale slowly)|
|Memory|70 to 80 percent, leaving room for spikes and GC|
|Disk space|Alert at 70 to 80 percent, act before 85 to 90 percent|
|Network|50 to 70 percent|

Headroom should also cover:

- **Failure of a zone or node** (N+1 or N+2): if you have 3 zones and lose one, the remaining two must carry the load. That means each zone runs at no more than about 66 percent of its capacity at peak.
- **Deployments:** rolling updates temporarily reduce capacity.
- **Traffic spikes** faster than autoscaling can react.
- **Degraded dependencies** (slower downstream means more concurrent work in flight).

**N+1 example:** to serve 10,000 RPS with instances that each handle 1,000 RPS, plus tolerating 2 failures at a time, you need 10 + 2 = 12 instances (more with extra headroom for spikes).

### Little's Law and concurrency
**Little's Law:** `L = λ x W`

- `L` = average number of requests in the system (concurrency)
- `λ` = arrival rate (requests per second)
- `W` = average time each request spends in the system (seconds)

Example: 500 requests per second with 200 ms average latency means `500 x 0.2 = 100` concurrent requests in flight. If each instance can handle 25 concurrent requests, you need at least 4 instances, plus headroom. This also tells you why a slow dependency (higher `W`) suddenly increases concurrency and exhausts thread pools and connections (see the bulkhead pattern).

### Example - Product API

|Input|Value|
|---|---|
|Peak traffic today|2,000 RPS|
|Growth forecast|8 percent per month|
|Campaign next quarter|+50 percent for 3 days|
|Capacity per instance (tested)|250 RPS at 60 percent CPU, p99 under 250 ms|
|Target utilisation|60 percent (already included in the 250 RPS figure)|
|Failure tolerance|Survive loss of 1 of 3 zones|

Calculation for 3 months ahead:

- Baseline peak: `2,000 x 1.08^3 ≈ 2,520` RPS
- With campaign: `2,520 x 1.5 ≈ 3,780` RPS
- Instances for 3,780 RPS: `3,780 / 250 ≈ 15.1`, so 16 instances
- Zone-loss tolerance: spread over 3 zones means 16 across 3 is about 5 to 6 per zone. Losing a zone leaves about 10 to 11 instances (roughly 2,500 to 2,750 RPS capacity), which is not enough. To survive a zone loss at campaign peak, you need `16 / (2/3) = 24` instances, 8 per zone.
- Cost and decision: either 24 instances for the campaign window only (scale up via scheduled scaling), or accept degraded service in a zone failure during the campaign.

### Bottleneck analysis
Throughput is capped by the **slowest, least scalable component** (often the database, a shared lock, a single-threaded service, a connection pool, or a third-party API).

- Find the bottleneck first. Adding app servers does nothing if the database is the limit.
- After you fix one bottleneck, the next appears. Plan iteratively.
- Use **Amdahl's Law** and **Universal Scalability Law** to reason about why adding nodes yields diminishing (or even negative) returns when there is serialisation (locks) or coordination overhead (cross-node chatter, contention).

### Artefacts
- A **capacity model** (spreadsheet or tool) linking demand drivers to resource needs.
- A **bottleneck and limits register:** each component's known limit, how it was measured, and the lead time to raise it.
- A **forecast and review calendar** (monthly or quarterly) plus pre-event reviews.
- **Quota and reservation tracking** with owners.
- Capacity KPIs on dashboards: utilisation, headroom remaining, time-to-exhaustion for each resource.

**Time-to-exhaustion** is a very useful alert: "at the current growth rate, this disk will be full in 9 days." Many metrics systems support it (Prometheus `predict_linear`).

## Load testing
|Test type|Purpose|
|---|---|
|**Baseline / smoke**|Verify the system works at low load and the test setup is valid|
|**Load test**|Expected peak load. Do SLOs hold?|
|**Stress test**|Push beyond limits to find the breaking point and failure mode|
|**Spike test**|Sudden jump in traffic. How fast does the system (and autoscaler) respond?|
|**Soak / endurance test**|Sustained load for hours or days. Finds leaks, slow degradation, resource exhaustion|
|**Scalability test**|Increase load and resources together. Does throughput scale linearly?|
|**Capacity / breakpoint test**|Find the maximum sustainable throughput within SLOs|
|**Failure-under-load test**|Kill nodes or a zone during a load test to validate N+1 and failover|

**Tools:** k6, Gatling, Locust, JMeter, Artillery, wrk and hey (simple HTTP), vegeta, cloud load testing services.

- **Use realistic traffic:** replay production traffic (sanitised) or model the real mix of endpoints, payload sizes, think time, data distributions and cache behaviour. Hot-key skew matters.
- **Use production-like environments and data volumes.** Tests on tiny datasets hide database problems.
- **Measure from outside**, and watch the whole system (CPU, memory, GC, DB, queue depth, connection pools), not only response times.
- **Use open-model load** (fixed arrival rate) rather than only closed-model (fixed number of virtual users). Closed models slow down as the server slows, hiding overload (this is called _coordinated omission_). Real users keep arriving regardless.
- **Find the knee:** the point where latency starts rising sharply. Your safe operating capacity is meaningfully below it.
- Record the **capacity per instance at your target SLO**, and re-measure after significant code or infrastructure changes.
- **Test autoscaling itself:** how long from load increase to new capacity serving traffic?
- Consider careful **testing in production** (canary, shadow traffic, controlled load) when staging can't match scale. Coordinate with the team and have safeguards.

## Autoscaling
Autoscaling adjusts capacity automatically based on **signals** and **rules**.

### Types
|Type|Description|Example|
|---|---|---|
|**Horizontal**|Add or remove instances, pods or tasks|Kubernetes HPA, AWS ASG, Azure VMSS, Cloud Run instances|
|**Vertical**|Change the resource size of an instance or pod|Kubernetes VPA, resizing a database instance|
|**Cluster / node autoscaling**|Add or remove the underlying machines so there is room for workloads|Cluster Autoscaler, Karpenter|
|**Serverless / scale to zero**|The platform scales from 0 to N per request or event|Lambda, Cloud Functions, Cloud Run, Knative|
|**Storage / throughput autoscaling**|Adjust provisioned capacity|DynamoDB auto scaling, Aurora storage, serverless DB capacity units|

### Policy Types
|Policy|How it works|Best for|
|---|---|---|
|**Target tracking**|Keep a metric near a target (for example average CPU at 60 percent) and let the system compute the changes|Most workloads. Simple and stable.|
|**Step scaling**|Different actions at different thresholds (CPU above 70 percent add 2, above 85 percent add 5)|Faster response to large deviations|
|**Simple scaling**|One action per alarm, then a cooldown|Legacy. Avoid when target tracking will do|
|**Scheduled scaling**|Change capacity at known times|Predictable patterns (business hours, nightly batch, events)|
|**Predictive scaling**|Forecast load from history and pre-scale ahead of demand (for example AWS predictive scaling)|Strong cyclical patterns with slow startup|
|**Event / queue-driven**|Scale on the amount of pending work (queue length, lag)|Workers and consumers (KEDA, SQS-based ASG scaling)|
|**Manual**|An operator decides|Rare events, emergencies, safety limits|

### Scaling Metrics
The best metric is one that is **correlated with load, responds proportionally to added capacity, and is available quickly.**

|Metric|Good for|Caveats|
|---|---|---|
|**CPU utilisation**|CPU-bound stateless services|Misleading for I/O-bound, or when limits throttle|
|**Memory**|Memory-bound workloads|Doesn't drop when instances are added (often GC and caching dominate). Often a poor scaling signal.|
|**Requests per second per instance**|Web and API services|Needs a known per-instance capacity|
|**Concurrency / in-flight requests**|Services where latency varies|Closely tied to Little's Law. A great signal|
|**Latency (p95, p99)**|Direct SLO link|Lagging and noisy, and rises when a _dependency_ is slow (adding instances won't help)|
|**Queue depth / age of oldest message / consumer lag**|Workers, streaming consumers|Prefer _backlog per consumer_ or time-to-drain over raw depth|
|**Custom business metrics**|Domain-specific load (active sessions, jobs pending)|Needs instrumentation|
|**Scheduled / time-based**|Known patterns|Not adaptive|

- For queue consumers, scale on **backlog per worker** (`messages / workers`) or on the **age of the oldest message** relative to your processing-time objective.
- For I/O-bound services, CPU is often a poor signal. Use RPS or concurrency instead.
- **Avoid scaling on a metric that doesn't improve when you add capacity** (for example, latency caused by a slow database) because you will scale up to the maximum for no benefit.
- Use **multiple metrics** where sensible. Most autoscalers take the maximum recommended replica count.

### Timing
The delay between "load rises" and "capacity is serving traffic" is the sum of:

```
metric collection delay  (e.g. 15-60 s scrape / aggregation)
+ evaluation period       (e.g. 1-5 min of sustained breach to avoid flapping)
+ provisioning time       (VM boot: 1-5 min; pod scheduling: seconds, plus a node if none free: 1-3 min)
+ application startup     (JIT warm-up, cache fill, DB connection setup, health check passing)
+ load balancer registration / readiness delay
```

This can easily add up to **several minutes**. A spike that doubles traffic in 30 seconds will overwhelm you long before new instances arrive. Ways to cope:

- **Keep headroom** (target utilisation of 50 to 60 percent, not 90).
- **Scale on a leading indicator** (RPS or queue depth rather than lagging CPU).
- **Pre-scale** with schedules or predictive scaling for known events.
- **Reduce startup time:** smaller images, lazy initialisation, pre-warmed pools, ahead-of-time compilation, snapshotting (for example Lambda SnapStart).
- Use **warm pools** (AWS Warm Pools) or **overprovisioning pods** (see below).
- Protect the system meanwhile with **rate limiting, load shedding and graceful degradation.**

### Preventing flapping and oscillation
Poorly tuned autoscalers repeatedly scale up and down (thrash), wasting money and destabilising the service.

|Technique|Description|
|---|---|
|**Cooldown / stabilisation window**|Wait after a scaling action before another. HPA's `behavior.scaleDown.stabilizationWindowSeconds` is typically longer than for scale-up.|
|**Asymmetric policy**|**Scale up fast, scale down slowly.** Adding capacity is cheap insurance, while removing it too eagerly causes outages.|
|**Hysteresis**|Different thresholds for scaling out and in (out above 70 percent, in below 40 percent)|
|**Rate limits on change**|For example, add at most 100 percent or 4 pods per minute and remove at most 10 percent per 5 minutes|
|**Minimum and maximum bounds**|Floor for availability and cost-safe ceiling|
|**Smoothing**|Use averages over windows rather than instantaneous values|
|**Don't scale in during a rollout or incident**|

### Min, max and desired capacity
- **Minimum:** enough to survive a failure and serve baseline traffic. Not zero for latency-sensitive services (unless cold starts are acceptable). Distribute across zones, with at least 2 or 3 replicas for availability.
- **Maximum:** protects against runaway scaling (a bug, an attack, a retry storm) and runaway cost. It must be high enough for real peaks and also consistent with downstream limits (database connections, third-party quotas). Alert when you sit at max.
- **Account quotas:** raise cloud limits well ahead of need, since autoscaling silently stops at the quota.

### Scale in safety
Removing capacity can break things if done carelessly.
- **Graceful shutdown:** handle SIGTERM, stop accepting new requests (fail readiness), finish in-flight work, close connections, then exit.
- **Connection draining / deregistration delay** on load balancers.
- **Termination grace period** long enough for longest requests or jobs.
- **PodDisruptionBudgets** (Kubernetes) to keep a minimum number of replicas during voluntary disruptions.
- **Scale-in protection** for instances that are busy with long-running work (ASG instance protection), or design work to be resumable.
- For **queue workers**, make sure a worker removed mid-job doesn't lose the message (visibility timeouts, acknowledgements after completion, idempotent processing).


## Autoscaling in different frameworks
### Autoscaling on Kubernetes
|Component|Scales|Based on|
|---|---|---|
|**HPA** (Horizontal Pod Autoscaler)|Number of pod replicas|CPU, memory, custom or external metrics|
|**VPA** (Vertical Pod Autoscaler)|Pod CPU and memory requests and limits|Observed usage|
|**KEDA**|Pod replicas (including to and from zero)|Event sources: queues, streams, cron, Prometheus queries, many more|
|**Cluster Autoscaler**|Nodes in a node group|Pending (unschedulable) pods|
|**Karpenter**|Nodes (flexible instance selection)|Pending pods. Provisions right-sized nodes quickly and consolidates|
|**Knative / serverless frameworks**|Pods per request concurrency, to zero|Request concurrency|

- **CPU utilisation is relative to the pod's CPU request.** If requests are set wrongly (too high or too low), HPA behaves wrongly. Set **requests** from measured usage.
- **Don't use HPA and VPA on the same metric (CPU or memory) for the same workload** in auto-update mode, because they fight. Use VPA in recommendation mode, or HPA on custom metrics with VPA on resources.
- **CPU limits cause throttling** that hurts latency even when the node has spare CPU. Many teams set CPU requests but omit CPU limits (a debated topic). Memory limits are still important, since exceeding them causes OOM kills.
- **Readiness probes and startup probes** matter: new pods don't receive traffic until ready, and HPA ignores pods that are not yet ready when computing utilisation.
- **Cluster autoscaling is the slow part:** pod scheduling takes seconds, but if no node has room, a new node must boot (often 1 to 3 minutes or more). Mitigate with:
    - **Overprovisioning / pause pods:** low-priority placeholder pods that reserve spare capacity and get evicted immediately when real pods need the space.
    - Karpenter's faster, right-sized provisioning.
    - Keeping a small **warm buffer** of nodes.
- **Pod topology spread constraints and anti-affinity** to spread replicas across zones and nodes, so scaling also maintains availability.
- **PodDisruptionBudgets** protect against too many simultaneous voluntary evictions during scale-down and node consolidation.
- **Priority classes** make sure critical workloads get capacity first when resources are tight.
- **Resource quotas and limit ranges** per namespace prevent one team from consuming the whole cluster.
- **KEDA** is excellent for event-driven workers:

### Autoscaling on cloud VMs and Managed services
|Platform|Mechanism|Notes|
|---|---|---|
|**AWS**|EC2 Auto Scaling Groups (target tracking, step, scheduled, predictive), ECS Service Auto Scaling, Application Auto Scaling (DynamoDB, Aurora replicas, Lambda provisioned concurrency), Fargate|Use warm pools and instance refresh. Mix On-Demand with Spot using mixed-instances policies|
|**Azure**|Virtual Machine Scale Sets, App Service autoscale, AKS (cluster autoscaler), Azure Functions|Rule-based and schedule-based|
|**Google Cloud**|Managed Instance Groups autoscaler, Cloud Run, GKE autopilot and cluster autoscaler|Cloud Run scales on concurrency, down to zero|
|**Serverless (Lambda, Cloud Functions)**|Per-request or per-event scaling|Watch **concurrency limits**, cold starts, and downstream limits (a function that scales to thousands can flatten a database)|

- **Scale to zero** saves cost but adds **cold start** latency. Use provisioned or minimum instances for latency-sensitive paths.
- **Concurrency limits** (reserved and provisioned concurrency on Lambda, max instances on Cloud Run) protect downstream systems.
- Functions that scale out quickly can **overwhelm connection-limited databases.** Use connection pooling (RDS Proxy, PgBouncer), queues as buffers, and concurrency caps.
- Use **Spot (preemptible) instances** for fault-tolerant, stateless or batch workloads at large discounts, with **diversification** across many instance types and zones to reduce interruption risk.
- Keep a **baseline of On-Demand (or reserved/committed)** capacity for the always-needed floor.
- Handle **interruption notices** (2-minute warning on AWS) with graceful drain.

### Scaling Stateful systems and databases
|Technique|Description|Notes|
|---|---|---|
|**Vertical scaling**|Larger instance|The first move for most databases, but has a ceiling and may need a restart or failover|
|**Read replicas**|Offload reads|Handles read-heavy load. Replication lag means stale reads|
|**Caching**|Redis or Memcached in front of the database|Often the highest-leverage fix. Plan for cache stampedes and cold-cache recovery|
|**Connection pooling / proxies**|PgBouncer, ProxySQL, RDS Proxy|Connections are a scarce resource and a common failure point as app replicas scale out|
|**Sharding / partitioning**|Split data across nodes by key|Needed for write scaling. Complex (resharding, hot shards, cross-shard queries)|
|**CQRS and denormalised read models**|Separate write and read stores|Scales reads independently|
|**Queues and write buffering**|Absorb bursts, apply at a steady rate|Trades immediacy for stability (also a back-pressure tool)|
|**Managed autoscaling databases**|Aurora Serverless v2, DynamoDB on-demand and auto scaling, Cosmos DB autoscale, Spanner|Reduces the operational burden, but understand scaling speed, minimum and maximum limits and cost|
|**Archival and data lifecycle**|Move or delete old data|Controls storage growth and keeps hot data small|

- **Connection exhaustion:** if 10 pods each hold 50 connections, scaling to 100 pods makes 5,000 connections, which may exceed the database's limit. Size pools with the maximum replica count in mind.
- **Hot partitions and hot keys:** uneven distribution caps throughput regardless of total capacity.
- **Storage growth and IOPS:** disks can usually grow online, but IOPS and throughput tiers may have separate limits and cooldowns.
- **Rebalancing cost:** adding nodes to Kafka, Cassandra or Elasticsearch triggers data movement that consumes I/O and network, sometimes making things temporarily worse. Plan scale-out _before_ the crunch.
- **Scale-in of stateful systems** is risky. Prefer scale-out and keep conservative scale-in policies, with explicit procedures for removing nodes.
- **Replication and failover headroom:** replicas must also handle the primary's load after failover.

## Scaling Whole 
A system scales only as far as its **least scalable dependency.** Autoscaling one tier can simply shift the bottleneck, or push the problem downstream.

```
Users -> CDN -> Load balancer -> API (autoscaled) -> Services -> Database / Cache / Queue / 3rd-party APIs
                                    ▲                              ▲
                          scales easily                    often the real limit
```

- **Scale tiers in proportion.** Doubling API replicas without extra database capacity just moves the failure.
- **Know downstream limits** (connections, rate limits, third-party quotas) and enforce them with bulkheads, concurrency caps, rate limiting and queues.
- **Watch for retry amplification:** when a tier slows down, upstream retries add load, which autoscaling then chases. Apply timeouts, retry budgets and circuit breakers (see the resilience patterns notes).
- **Cap autoscaling maximums** at what downstream systems can actually handle.
- **Include shared infrastructure** in planning: load balancers (pre-warming for sudden spikes on some platforms), NAT gateways, DNS query limits, service meshes, logging and metrics pipelines (they can drown under a traffic spike), and CI/CD.
- **Observability scales with traffic too,** so plan its capacity and cost.

## Spikes and Special Events
|Scenario|Area|Action|Details|
|---|---|---|---|
|**Predictable events** (sales, festivals, launches, exams)|1. Forecast|Estimate the peak|Use past events and business expectations, with a safety multiple.|
||2. Load test|Test at or above the forecast|Include the failure scenarios.|
||3. Pre-scale|Scale before the event|Use scheduled or manual scaling instead of reactive scaling. Raise minimums, warm caches, pre-warm load balancers where required, and warm JIT and connection pools.|
||4. Quotas|Raise limits early|Raise quotas and reservations with cloud and third-party providers.|
||5. Change freeze|Freeze risky changes|Apply the freeze around the event.|
||6. Degradation levers|Prepare fallbacks|Feature flags to turn off expensive features, static fallbacks, queue-based ordering, and a virtual waiting room for extreme demand (Queue-it, Cloudflare Waiting Room).|
||7. War room|Staff it|Clear roles, dashboards and runbooks.|
||8. Scale down|Reduce deliberately|Keep the increased capacity long enough to absorb tail traffic.|
|**Unpredictable spikes** (viral content, attacks, retries)|Edge protection|Filter at the edge|CDN caching, WAF, DDoS protection, bot management, rate limiting.|
||Load shedding|Protect the core|Load shedding and back-pressure (see the resilience notes).|
||Reactive scaling|Scale fast|Fast reactive scaling, with headroom and leading indicators.|
||Traffic differentiation|Prioritise users|Protect authenticated and paying users, and degrade anonymous or low-priority traffic first.|
||Surge vs attack|Tell them apart|Scaling up to absorb a DDoS can be very expensive. Cap the maximum and block malicious traffic at the edge.|
|**Thundering herd and cold starts**|Cache stampede|Prevent simultaneous misses|Many requests miss at once and hit the database. Use request coalescing, jittered TTLs, early refresh and locks.|
||Mass restart or reconnect|Stagger reconnects|After an outage, all clients reconnect at once. Use jittered backoff and gradual ramp-up (slow start in load balancers).|
||Cold instances|Warm them up|Empty caches and unoptimised code mean less load handled at first. Use slow-start and warm-up routines.|

## Cost Optimisation
|Lever|Description|
|---|---|
|**Right-sizing**|Match instance size to actual usage (CPU and memory utilisation data, VPA recommendations, cloud right-sizing tools)|
|**Autoscaling and schedules**|Scale down off-peak, shut down dev and test environments out of hours|
|**Commitments**|Savings Plans, Reserved Instances, committed use discounts for the predictable baseline|
|**Spot / preemptible**|Large discounts for interruptible workloads|
|**Graviton / ARM and newer instance generations**|Better price-performance for many workloads|
|**Storage tiering**|Lifecycle policies to colder, cheaper tiers|
|**Efficiency work**|Profiling, caching, query optimisation, and removing wasted work often reduces both cost and latency|
|**Bin packing and consolidation**|Higher node utilisation in Kubernetes (Karpenter consolidation)|
|**Data transfer awareness**|Reduce cross-AZ and cross-region traffic, use CDN and private connectivity|
|**Cost visibility**|Tagging, per-team and per-service cost allocation (showback and chargeback), anomaly alerts, FinOps practice|

## Monitoring and Feedback

**Dashboards and metrics to maintain**\
- Utilisation versus capacity for each resource, with **peak** and **p95** views.
- **Saturation signals:** queue depth, run queue, thread pool use, connection pool wait, throttling, GC time.
- **Headroom remaining** and **time-to-exhaustion** for finite resources (disk, quotas, IPs, partitions).
- **Autoscaler behaviour:** current vs desired vs max replicas, scaling events, time to scale, time spent at max, pending pods, failed scale-ups (quota or capacity errors).
- Demand versus capacity trend, forecast vs actual.
- **Cost per unit of work.**
- **SLO and error budget status,** because capacity shortfalls show up as latency and errors first.

**Alerts**
- Autoscaler **at max** for more than a few minutes
- Resource approaching **quota or hard limits**
- **Scaling failing** (insufficient capacity, quota exceeded, failed instance launches)
- **Time-to-exhaustion** below a threshold
- Sustained high **saturation** despite autoscaling
- Unusual **scaling churn** (flapping)
- **Cost anomalies**

**Review rhythm**
- Weekly or monthly: utilisation, trends, scaling behaviour, cost.
- Quarterly: forecast vs actual, update the capacity model, re-run load tests, review limits and architecture.
- Before every major launch or event: dedicated capacity review.
- After incidents: add capacity lessons to the register.