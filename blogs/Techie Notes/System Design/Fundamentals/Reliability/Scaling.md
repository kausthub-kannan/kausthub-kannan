Scalability is the ability of a system to handle a growing amount of work, such as more users, more requests or more data, without a drop in performance and without a complete redesign. A system that serves 100 users happily but collapses at 100,000 is not scalable. Scaling is the act of adding capacity to meet that growth. Capacity here means the amount of work the system can handle at once, which is limited by its CPU, memory, disk, network and software design. At some point one of these resources runs out, and that resource is the bottleneck. Scaling is mostly the work of finding the current bottleneck and removing it, then finding the next one.

Three terms are often mixed up. Performance is how fast the system responds to one request. Scalability is whether performance holds up as the load grows. Elasticity is the ability to add and remove capacity automatically as the load changes, which matters in the cloud, where you pay for what you use.

## Vertical Scaling
Vertical scaling means making a single machine more powerful by adding more CPU cores, more RAM, faster disks or a faster network connection. A server with 8 GB of RAM is replaced by one with 64 GB. It is the simplest way to scale because the application does not change at all: there is still one server, one database and one set of data, so no distribution problems appear. It is often the right first step and is commonly used for databases, which are hard to distribute.

Its limits are serious. There is a hard ceiling, since a single machine can only be made so big, and the largest machines are enormously expensive, with cost rising faster than capacity. Upgrading usually needs downtime, because the machine must be restarted or replaced. And most importantly it leaves a single point of failure: if that one big server fails, the whole system goes down.

## Horizontal Scaling
Horizontal scaling means adding more machines and spreading the work across them, so that ten ordinary servers share a load that one server could not handle. A load balancer distributes incoming requests among them. There is no real upper limit, since more machines can always be added, and it uses inexpensive commodity hardware. It also improves availability, because if one machine fails the others continue to serve traffic, and servers can be added or removed without downtime.

The price is complexity. The application must be designed so that work can be split across machines. Data has to be partitioned or replicated, which brings in consistency questions from the CAP and PACELC notes. Machines must communicate over a network, which is slower and less reliable than memory inside one machine. And there is more to operate and monitor. Large systems such as those of Google, Netflix and Amazon are built almost entirely on horizontal scaling.

Horizontal scaling requires stateless service. To scale a service by adding identical copies, any copy must be able to handle any request. This is only possible if the servers are stateless, meaning that a server does not keep user-specific data, such as login sessions or shopping carts, in its own memory. If it did, a user's second request sent to a different server would find nothing. The state must be moved out into shared systems: sessions and cache data into Redis, files into object storage, and permanent data into the database. Once servers are stateless, they become interchangeable, and a load balancer can send each request anywhere, add new servers at any time and remove failed ones without anyone noticing. This is the same reason REST APIs are designed to be stateless.

|Aspect|Vertical scaling (scale up)|Horizontal scaling (scale out)|
|---|---|---|
|What changes|The size of one machine|The number of machines|
|Example|Moving from 8 GB to 64 GB RAM|Going from 2 servers to 20 servers|
|Complexity|Low, no application changes|High, requires distributed design|
|Upper limit|Hard limit set by the biggest available machine|Practically unlimited|
|Cost pattern|Gets disproportionately expensive at the high end|Roughly linear, using cheap commodity hardware|
|Downtime to scale|Usually needed|Usually none, machines are added live|
|Fault tolerance|Single point of failure|Survives the loss of individual machines|
|Load balancer needed|No|Yes|
|Data consistency|Simple, one copy of the data|Harder, data is replicated or partitioned|
|Network overhead|None, everything is in one machine|Present, machines talk over the network|
|Best for|Small to medium systems, databases early on, quick fixes|Large, growing, highly available systems|

## Scaling different layers of System
|Layer|How it scales|Related notes|
|---|---|---|
|Traffic entry|GeoDNS and anycast send users to the nearest region, and multiple load balancers share the traffic|DNS, load balancer|
|Static content|A CDN serves images, video and scripts from edge servers, removing that load from the origin|CDN|
|Application servers|Stateless servers are cloned behind a load balancer and added or removed with demand|Load balancer, API|
|Caching|A cache such as Redis answers repeated reads so the database sees fewer requests, and the cache itself scales by sharding keys across nodes with consistent hashing|Caching|
|Slow or bursty work|Queues absorb spikes and workers process tasks in the background, with more workers added as the queue grows|Message queue|
|Database reads|Read replicas copy the data and share the read traffic|CAP, PACELC|
|Database data volume and writes|Partitioning on one server, then sharding across servers|Database partitioning|
|Files and media|Object storage services scale almost without limit, and are served through the CDN|CDN|

### Scaling Databases
The database is usually the hardest layer to scale, because it holds state that must stay correct, and application servers are comparatively easy. The usual progression moves from the cheapest and simplest steps to the most complex ones.

|Step|What it does|Helps with|Trade-off|
|---|---|---|---|
|Tune queries and add indexes|Makes each query cheaper|Slow reads|Indexes slow down writes slightly|
|Add a cache|Serves repeated reads from memory|Read-heavy load|Stale data, cache invalidation|
|Scale up the server|More CPU, RAM, faster disks|Everything, temporarily|Costly, has a ceiling|
|Read replicas|Copies of the database serve reads while one primary takes writes|Read-heavy load|Replication lag, so replicas can be briefly stale|
|Partitioning|Splits big tables inside one server|Large tables, maintenance|Still limited to one server|
|Sharding|Splits data across several servers by a shard key|Data volume and write throughput|Complex routing, cross-shard queries and transactions are hard|
|Separate read and write models (CQRS)|Uses different stores optimized for reads and for writes|Very different read and write patterns|More moving parts and eventual consistency|
|Move suitable data to NoSQL|Uses databases built for horizontal scaling|Massive, simple-access data|Weaker joins and transactions|

## Autoscaling
Autoscaling adds and removes servers automatically based on demand, which is how elasticity is achieved. The system watches a metric such as CPU use, requests per second, memory or queue length, and when it passes a threshold, new instances are started, and when it falls, they are removed. This saves money during quiet periods and protects the system during busy ones.

|Type|How it decides|Example|
|---|---|---|
|Reactive|Responds to current metrics|Add servers when average CPU stays above 60 percent|
|Scheduled|Follows a known pattern|Scale up every day at 8 am before office traffic arrives|
|Predictive|Uses past data to forecast demand|Prepare for a recurring weekly spike before it starts|

A Kubernetes example of reactive horizontal autoscaling follows. It keeps between 3 and 20 copies of a service and adds copies when average CPU use goes above 60 percent.

A few details matter in practice. New servers take time to start, so scaling should begin before the limit is reached, and a cooldown period prevents the system from rapidly adding and removing servers (flapping). When removing servers, they should finish current requests first (connection draining). Setting a sensible minimum keeps the system available, and a maximum controls cost and protects downstream systems such as the database from being flooded by suddenly having many more clients.

## Back-of-the-Envelope Capacity Estimation
System design usually starts with a rough estimate of the load, to decide whether scaling is needed and how much. Suppose an app has 10 million daily active users, and each user makes about 10 requests a day.

|Step|Calculation|Result|
|---|---|---|
|Requests per day|10,000,000 users x 10 requests|100 million per day|
|Average requests per second|100,000,000 / 86,400 seconds|About 1,150 per second|
|Peak requests per second|Average x 3 (peak factor)|About 3,500 per second|
|Servers needed|3,500 / 500 per server|About 7 servers|
|With headroom and redundancy|Add spare capacity for failures and growth|About 10 servers|

The numbers are only estimates, but they show whether one server is enough (it is not here), roughly how many are needed, and what grows next. The same method is used for storage, such as multiplying the number of records by their size and by the growth rate, and for bandwidth.

## Fixing bottlenecks
Scaling without measurement wastes effort, since adding more application servers does nothing if the real bottleneck is the database. The approach is to measure first, using monitoring of CPU, memory, disk and network use, request rates, error rates and latency percentiles such as p95 and p99 (the experience of the slowest 5 percent and 1 percent of requests, which averages hide). Load testing with tools such as k6, JMeter or Locust shows where the system breaks before real users do. Once the slowest component is found, it is fixed, and the system is measured again, because the bottleneck simply moves to the next weakest part. Typical culprits are slow database queries, missing indexes, lock contention, an overloaded single service, chatty calls between services and a lack of caching.

## Different Scaling Techniques
|Technique|Idea|
|---|---|
|Load balancing|Spread requests over many servers|
|Caching|Remember results to avoid repeating work|
|CDN|Move content close to users|
|Replication|Keep copies of data to share reads and survive failures|
|Partitioning and sharding|Split data so each piece is smaller and independent|
|Asynchronous processing|Move slow work to queues and workers|
|Stateless design|Make any server able to handle any request|
|Rate limiting and backpressure|Protect the system from more load than it can take|
|Denormalization|Store data in a way that avoids expensive joins on reads|
|Microservices|Scale each part of the system independently|

### Predicting Architecture growth
|Stage|Situation|Problem|Typical fix|
|---|---|---|---|
|1|Everything on one server|Resources run out, one failure takes everything down|Split the database onto its own server|
|2|Separate app and database servers|App server is overloaded|Add more app servers behind a load balancer, make them stateless|
|3|Many app servers, one database|Database is overloaded with reads|Add caching and read replicas|
|4|Static content slowing the servers and distant users are slow|Latency and bandwidth cost|Add a CDN and object storage|
|5|Traffic bursts, slow tasks block requests|Spikes overload downstream services|Add message queues and background workers|
|6|Database writes or data volume too large|Single database cannot keep up|Partition tables, then shard the data|
|7|Users worldwide, region outages|Latency and availability across regions|Multi-region deployment with GeoDNS and replicated data|

