Replication means keeping copies of the same data on multiple machines, called replicas or nodes, so that each one holds the same dataset. When data is written on one machine, the change is sent to the others, so they stay in sync. The copies are usually placed on different servers, in different racks, data centers or even regions.

|Reason|What replication provides|
|---|---|
|High availability|If one machine fails, another already has the data and can take over, so the system stays up|
|Read scalability|Read requests can be spread across many replicas, so the primary is not overwhelmed|
|Lower latency|Replicas can be placed close to users in different regions, so reads are served from nearby|
|Durability|Data survives the loss of a disk, a server or a whole data center|
|Maintenance and analytics|Backups, reports and heavy queries can run on a replica without slowing the main database|

The hard part is that data changes. If data never changed, replication would simply be copying. Every write must reach every copy, copies are separated by an unreliable network that can be slow or fail, and during the time it takes for a change to spread, the replicas disagree. Almost every design decision in replication is about how to handle that gap, and it is the direct link to the CAP and PACELC notes.

## Replication vs Other types

|Concept|What it does|Copies of the same data|Purpose|
|---|---|---|---|
|Replication|Keeps full copies of the data on several nodes|Yes|Availability, read scaling, durability|
|Partitioning|Splits a table into pieces on one server|No|Faster queries, easier maintenance|
|Sharding|Splits data across servers, each holding a different part|No|Scale storage and write throughput|
|Backup|Saves a point-in-time copy for recovery|Yes, but offline and not live|Recovery from disasters and mistakes|

Large systems combine them: data is sharded across servers, and each shard is replicated for availability. Replication is also not a replacement for backups. If someone accidentally runs a DROP TABLE or a bad update, replication faithfully copies that mistake to every replica within moments, so backups and point-in-time recovery are still needed.

## Replication Architectures
| Architecture                    | Who accepts writes                           | Who serves reads     | Examples                                                   | Best for                                    |
| ------------------------------- | -------------------------------------------- | -------------------- | ---------------------------------------------------------- | ------------------------------------------- |
| Leader-follower (single-leader) | Only the leader                              | Leader and followers | PostgreSQL, MySQL, MongoDB replica sets, Redis, SQL Server | Most applications, simple and consistent    |
| Multi-leader                    | Several leaders, usually one per data center | All nodes            | MySQL group setups, CouchDB, some multi-region setups      | Multi-region writes, offline-capable apps   |
| Leaderless                      | Any replica                                  | Any replica          | Cassandra, Riak, DynamoDB (internally)                     | Very high availability and write throughput |

## Leader-Follower Replication
#### Synchronous vs Asynchronous Replication in Leader-Follower

|Aspect|Synchronous|Asynchronous|Semi-synchronous|
|---|---|---|---|
|When the client gets the ack|After the follower has the data|Right after the leader writes|After one chosen follower has it|
|Write latency|Higher, includes the network round trip and follower write|Lowest|Moderate|
|Data loss if the leader crashes|None for acknowledged writes, since a follower has them|Possible, since recent writes may not have reached followers|Very unlikely, since at least one follower has each write|
|Follower freshness|Up to date|Lags behind, so reads may be stale|The synchronous follower is up to date, the others lag|
|Availability of writes|Lower, since a slow or down follower can block writes|Highest, since slow followers do not affect writes|Good, if the synchronous follower fails another can take over that role|
|Consistency|Strong|Eventual|Strong for the synchronous follower, eventual for the others|
|PACELC position|Leans toward consistency (EC)|Leans toward latency (EL)|A compromise between them|
|Typical use|Financial and critical data, within a region|Cross-region replicas, read scaling, analytics|The most common production setting for important data|

The problem with fully synchronous replication is that every follower becomes a point of failure for writes: if even one is slow or unreachable, the leader cannot complete writes and the whole system stalls. For this reason, having all followers synchronous is rarely done. Semi-synchronous replication avoids this by requiring only one synchronous follower, and if it fails, one of the asynchronous followers is promoted to take its place, so at least two nodes always hold every acknowledged write.

The asynchronous option has a serious weakness: if the leader fails and its recent writes had not reached any follower, those writes are lost forever after failover, even though the client was told they succeeded. For many applications, such as social media, this is acceptable in return for speed and availability. Asynchronous replication is also the practical choice between distant regions, since waiting on a round trip across continents for every write would be too slow.

A common real-world setup combines the two: replicas within the same region or availability zone are synchronous, since the latency is small, and replicas in other regions are asynchronous.

#### Replication Methods
|Method|What is sent to followers|Pros|Cons|
|---|---|---|---|
|Statement-based|The SQL statements themselves|Compact|Non-deterministic functions such as NOW() or RANDOM() give different results on each node, and side effects can differ|
|WAL shipping (physical)|The low-level write-ahead log of byte changes|Exact copy, efficient, the PostgreSQL default|Tied to the database version and storage format, so the follower must be identical, and it cannot replicate only some tables|
|Logical (row-based)|A description of the row changes (insert, update, delete)|Works across versions, can replicate selected tables, can feed other systems|Slightly more overhead|
|Trigger-based|Application or trigger code records the changes|Very flexible|Slow and error-prone|

#### Lags in Replication
With asynchronous replication, followers are always slightly behind, usually by milliseconds, but sometimes by seconds or minutes under heavy load or network trouble. This delay is called replication lag, and a system reading from followers sees eventual consistency. It causes several confusing anomalies that a user can notice.

|Anomaly|What the user sees|Example|Common fix|
|---|---|---|---|
|Not reading your own writes|You make a change, reload, and your change is missing|You post a comment, the page refreshes from a lagging follower and the comment is gone|Read recently changed or the user's own data from the leader, or read from a follower only if it has caught up to the user's last write|
|Non-monotonic reads|Data goes backwards in time|One refresh shows a new comment, the next (from a more lagged follower) shows none|Pin each user to the same follower, for example by hashing the user ID|
|Violation of consistent prefix|Effects appear before causes|A reply is seen before the question it answers, when the two are on different shards|Keep causally related writes in the same partition|

These are handled in the application, or by choosing a database consistency level, not by the replication mechanism itself. The general rule is that if an application cannot tolerate stale reads for a certain feature, that feature should read from the leader (or from a synchronous follower), and everything else can use the followers.

#### Failovers
When the leader fails, the system must promote a follower to be the new leader, which is called failover. It can be manual, with an administrator deciding, or automatic. Automatic failover follows several steps. First, the failure is detected, usually when the leader stops responding to heartbeats for a set timeout. Second, a new leader is chosen, ideally the follower with the most up-to-date data, through an election in which the remaining nodes vote. Third, the system is reconfigured so that clients send writes to the new leader and the other followers replicate from it. Fourth, when the old leader comes back, it must be demoted to a follower and not be allowed to act as a leader.

Failover is risky and full of subtle problems.

|Problem|What goes wrong|Mitigation|
|---|---|---|
|Lost writes|With asynchronous replication, the new leader may not have the last writes of the old leader|Use synchronous or semi-synchronous replication for important data, and promote the most up-to-date follower|
|Split brain|Two nodes both believe they are the leader and both accept writes, so the data diverges and may be corrupted|Fencing (cutting the old leader off from clients and storage), and requiring a majority of nodes to agree on a leader|
|Wrong timeout|A short timeout triggers needless failovers on a brief network blip, a long one prolongs the outage|Tune the timeout carefully and require several failed checks|
|Inconsistent with other systems|The lost writes may include IDs that were already shared with a cache or another system, which are then reused|Avoid depending on data that could be lost, or reconcile after failover|
|Clients still pointing to the old leader|Requests keep failing or go to the wrong node|Use a virtual IP, DNS update, a proxy or service discovery to redirect clients|

Tools handle much of this. Patroni, with a consensus store such as etcd or Consul, manages PostgreSQL clusters. MySQL uses tools like Orchestrator, Redis uses Sentinel, MongoDB replica sets run elections automatically, and managed services such as Amazon RDS Multi-AZ keep a synchronous standby in another zone and fail over automatically.

## Consensus-Based Replication
An approach that avoids many failover problems is to replicate through a consensus algorithm such as Raft or Paxos. A write is considered committed only when a majority (quorum) of nodes have stored it, and leader election is part of the protocol, with the guarantee that a new leader will always have all committed writes and that there cannot be two leaders at once. In a group of three nodes, the loss of one is tolerated, and in five, the loss of two. This gives strong consistency and automatic safe failover, at the cost of waiting for a majority on each write and of needing an odd number of nodes. It is used in etcd, ZooKeeper, Consul, Google Spanner and CockroachDB, and it connects to the CP side of the CAP theorem.

## Multi-Leader Replication
In multi-leader replication, more than one node accepts writes, and each leader replicates its changes to the others. The most common setup has one leader per data center, with each leader serving the users of its region. A user in India writes to the Mumbai leader and a user in Germany writes to the Frankfurt leader, so both get low write latency, and each region keeps working if the link between regions fails. It is also used by applications with offline support, such as calendar and notes apps, where each device acts as a leader and syncs later, and by collaborative editing tools.

|Aspect|Single-leader|Multi-leader|
|---|---|---|
|Write latency for distant users|High, writes travel to the one leader|Low, writes go to the local leader|
|Tolerance of a data center outage|Writes stop until failover|Other data centers keep accepting writes|
|Tolerance of network problems between regions|Weak|Strong, replication catches up later|
|Write conflicts|None|Possible, and a major complication|
|Complexity|Low|High|

The central problem is write conflicts. If two users change the same record at the same time on two different leaders, each write is accepted locally, and the conflict is only discovered when the changes are replicated. The system must then decide on the result.

|Conflict handling approach|How it works|Trade-off|
|---|---|---|
|Avoid conflicts|Route all writes for a given record to the same leader, for example by user's home region|The best option when possible, but it fails if a user moves or a region fails|
|Last write wins (LWW)|Keep the write with the latest timestamp|Simple, but silently loses the other write and depends on synchronized clocks|
|Merge the values|Combine the changes, for example by joining text or taking the union of sets|Works for some data types only|
|CRDTs and operational transformation|Data structures and algorithms designed so concurrent edits merge automatically|Powerful for collaboration, complex to build|
|Custom application logic|Store both versions and ask the application or the user to resolve them|Flexible but needs extra code|

Multi-leader setups are generally avoided unless there is a real need, since conflict resolution is subtle and many surprising bugs, such as with auto-incrementing keys, constraints and triggers, appear. When replication between leaders is arranged in a ring or star, a change can also take a long path or loop, so each write carries an identifier of its origin to prevent loops.

## Leaderless Replication
In leaderless replication, popularized by Amazon's Dynamo and used in Cassandra and Riak, there is no leader at all. A client sends each write to several replicas in parallel, and any replica can accept a write or answer a read. With N replicas, a write is successful when W of them acknowledge it, and a read asks R of them and takes the newest value. If R + W > N, the set of replicas read must overlap with the set written, so a read is guaranteed to include at least one up-to-date copy. For example, with N = 3, W = 2 and R = 2, the system tolerates one unavailable replica for both reads and writes. This is the quorum rule from the CAP.

Since replicas can miss writes while they are down, leaderless systems have repair mechanisms.

|Mechanism|What it does|
|---|---|
|Read repair|When a read finds that some replicas hold an old value, the client or coordinator writes the newest value back to them|
|Hinted handoff|If a replica is unreachable, another node temporarily stores its writes (a hint) and delivers them when it comes back|
|Anti-entropy|A background process compares replicas, often using Merkle trees, and copies any missing data|
|Sloppy quorum|When the usual nodes are unreachable, writes are accepted by other nodes temporarily, which improves availability but weakens the quorum guarantee|
|Version vectors|Track which updates have been seen so concurrent writes can be detected and kept as conflicting siblings, or resolved|

Leaderless replication has no failover, so there is no pause when a node fails, and it offers very high availability and write throughput. The cost is weaker consistency guarantees even with quorums, because of edge cases such as sloppy quorums and concurrent writes, plus the same conflict resolution challenges as multi-leader systems.

