The CAP theorem is a fundamental result about distributed data systems, meaning systems where data is stored on multiple servers (nodes) connected by a network. It was proposed by Eric Brewer in 2000 and later formally proved by Seth Gilbert and Nancy Lynch. It says that a distributed system can provide at most two out of three guarantees at the same time: Consistency, Availability and Partition tolerance. In practice, the sharper way to put it is that when the network breaks, the system must choose between consistency and availability. It is used constantly in system design because it explains why different databases behave the way they do and helps in choosing the right one for a use case.

|Letter|Property|What it guarantees|Example|
|---|---|---|---|
|C|Consistency|Every read returns the most recent write, or an error. All nodes appear to hold the same data at the same time|After you update your profile, every user and every server immediately sees the new profile|
|A|Availability|Every request to a working node gets a response, even if that response may not contain the latest data|The app always shows you something, even if it is slightly outdated|
|P|Partition tolerance|The system keeps working even when the network between nodes breaks or messages are lost|Two data centers lose connection to each other but both keep running|

Consider two database servers, Node A and Node B, each holding a copy of the same data, such as a user's account balance of 100. They stay in sync by sending updates to each other over the network. Now the network link between them breaks, which is a partition. A client writes a new balance of 50 to Node A. Node A cannot pass this update to Node B. Then another client reads the balance from Node B. The system now has two choices, and neither is free.

- Choose consistency: Node B refuses to answer, or returns an error, because it cannot be sure its data is current. The data is never wrong, but the system is unavailable for that request.
- Choose availability: Node B answers with the balance it has, which is 100. The system stays responsive, but the answer is stale, so consistency is lost.

There is no third option, because there is no way for Node B to know the latest value without talking to Node A, and the network does not allow that. This is the heart of the theorem.

## CP vs AP vs CA

|Aspect|CP (Consistency + Partition tolerance)|AP (Availability + Partition tolerance)|CA (Consistency + Availability)|
|---|---|---|---|
|Behavior during a partition|Rejects or delays some requests to keep data correct|Keeps answering, but data may be stale or conflicting|Not tolerant of partitions, so only valid without a network split|
|Data guarantee|Always correct, never stale|Eventually consistent|Strong consistency on a single node|
|Downside|Some requests fail or time out|Users may see old data, conflicts must be resolved later|Cannot be distributed safely|
|Typical examples|ZooKeeper, etcd, HBase, MongoDB (default settings), Google Spanner|Cassandra, DynamoDB, CouchDB, Riak|Single-node PostgreSQL or MySQL|
|Suited for|Banking, payments, inventory, leader election, configuration|Social feeds, likes and view counts, shopping carts, product catalogs|Small systems on one server|

The right choice depends on what a wrong answer costs compared to an unavailable system. For a bank transfer, a stale balance could allow overdrawing an account or a double spend, so it is better to refuse the operation temporarily than to give an incorrect answer. For inventory in a limited sale, showing a stale count could lead to overselling. These need CP behavior. For a social media feed or a like counter, seeing a post a few seconds late or a count slightly off is harmless, but a page that fails to load is a direct loss of users, so availability matters more. These suit AP behavior. Many large systems use both: a CP store for critical data such as payments, and an AP store for high-volume, tolerant data such as feeds and recommendations.

A familiar example from earlier notes is DNS, which is deliberately AP. Resolvers serve cached answers until the TTL expires, so different users can briefly see different IP addresses after a change, but DNS keeps answering and the data converges once the caches expire. Caches and CDNs follow the same pattern, trading a little freshness for speed and availability.

## Concept of Eventual Consistency
AP systems typically provide eventual consistency, meaning that if no new updates are made, all replicas will eventually converge to the same value, though not instantly. After the partition heals, the nodes exchange the writes they missed and reconcile. When two nodes accepted conflicting writes during the partition, the system needs a rule to resolve them.

|Technique|How it helps|
|---|---|
|Last write wins|Keeps the update with the latest timestamp. Simple, but can silently discard data and depends on clocks|
|Vector clocks|Track the order of updates so the system can detect real conflicts instead of guessing|
|CRDTs|Data structures designed so that concurrent updates always merge correctly, such as counters and sets|
|Read repair|When a read finds replicas disagreeing, the stale ones are fixed on the spot|
|Hinted handoff|A node temporarily stores writes meant for a down node and delivers them when it recovers|
|Anti-entropy|Background processes compare replicas and sync differences|

## Quorums and Tunable Consistency
Many distributed databases let you tune the trade-off between consistency, latency, and availability using quorums. Suppose data is stored on \(N\) replicas. A write quorum \(W\) specifies how many replicas must acknowledge a write before it is considered successful, while a read quorum \(R\) specifies how many replicas are consulted during a read.

When \(R + W > N\), the read and write quorums must overlap, assuming they refer to the same replica set. This helps the read discover the latest write, provided the database correctly tracks versions and resolves conflicts. For example, with \(N = 3\), choosing \(W = 2\) and \(R = 2\) guarantees quorum overlap and can provide strong consistency when supported by the database's replication protocol. Choosing \(W = 1\) and \(R = 1\) reduces coordination and latency but can allow stale reads. However, quorum overlap alone does not guarantee strong consistency: the database must also handle concurrent writes, version tracking, and conflict resolution correctly. Higher quorum requirements generally increase coordination and can reduce availability during failures, while lower requirements can improve responsiveness at the cost of consistency guarantees.