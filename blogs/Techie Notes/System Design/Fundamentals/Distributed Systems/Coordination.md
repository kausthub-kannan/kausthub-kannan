On a single machine, coordination is cheap. Threads share memory, one clock tells the time to everyone, and a lock is a variable that everyone can see. In a distributed system none of this holds. Machines communicate only by sending messages over a network, and that network can delay, reorder, duplicate or drop messages. Each machine has its own clock, and the clocks disagree. Any machine can crash or pause at any moment, and from the outside a crashed machine looks the same as a slow one, since the only evidence is that no reply has arrived yet. There is no shared memory and no single global view of the system.

Two classic results explain why this is fundamentally hard. The Two Generals problem shows that two parties communicating over an unreliable link can never be completely certain that both have agreed, because the last message in any exchange might be lost. The FLP impossibility result shows that in a fully asynchronous system, no algorithm can guarantee consensus if even one process might crash. Real systems get around this using timeouts, randomization and majority voting, which give practical solutions that work almost all of the time, though they can never promise perfection. All the tools in these notes (locks, leader election, logical clocks, consensus, two-phase commit and sagas) are ways of coordinating despite these limits, and each has a cost.

## Distributed Locks

### Distributed Locks
A distributed lock gives mutual exclusion across processes on different machines: at any moment, only one holder may be inside a critical section. Typical uses are making sure that only one worker processes a job, that only one instance runs a scheduled task, that two users cannot book the same seat, or that a shared resource is modified by one writer at a time.

Distributed locks are much more difficult than local locks, for the following reasons.

|Problem|What goes wrong|
|---|---|
|Holder crashes|The lock is never released, and everyone else waits forever|
|Holder pauses|A process freezes for a long time (a garbage collection pause, a slow disk, a VM pause), its lock expires, another process takes the lock, then the first wakes up still believing it holds the lock|
|Network delay|A release or write message arrives much later than expected, after the lock has moved to someone else|
|Clock differences|Lock expiry that depends on clocks can end too early or too late on different machines|
|Lock service failure|If the lock service is a single machine, it becomes a single point of failure|

### Lease and fencing tokens
Since a holder might crash, locks are given as leases, which are locks with an expiry time (a TTL). If the holder does not finish or renew the lease in time, the lock is released automatically. This solves the crashed-holder problem but creates the paused-holder problem: a client may still be working when its lease has already expired and been granted to someone else, so two clients believe they hold the lock.

The correct solution is a fencing token. Each time the lock is granted, the lock service gives a number that increases every time. The client includes this token in every request it sends to the protected resource, and the resource remembers the highest token it has seen and rejects anything lower.

|Step|Event|
|---|---|
|1|Client A acquires the lock and receives token 33|
|2|Client A pauses for a long time, and its lease expires|
|3|Client B acquires the lock and receives token 34, then writes to storage with token 34|
|4|Client A wakes up, still thinking it owns the lock, and writes with token 33|
|5|Storage has already seen 34, so it rejects the write with token 33|

The key insight is that the lock alone cannot make the system safe. The protection must be enforced by the resource being protected. It also means that locks can be thought of for two distinct purposes. A lock for efficiency avoids duplicate work, such as two workers sending the same email, and an occasional double execution is only a nuisance, so a simple lock is enough. A lock for correctness protects data that must never be corrupted, and for that, a lock with fencing tokens on a system that provides strong consistency is required.

### Implementing Distributed Locks

|Approach|How it works|Strengths|Weaknesses|
|---|---|---|---|
|Database row lock or advisory lock|The lock is a row lock or an advisory lock in a relational database|Simple, uses infrastructure that already exists, released automatically when the session ends|Load on the database, only as available as that database|
|Optimistic locking (version column)|Updates succeed only if the version has not changed|No lock to hold, no lock to leak|Retries on conflict, not suitable for long operations|
|Redis single instance|`SET key token NX PX ttl` creates a key only if it does not exist, with an expiry|Fast and simple|If the Redis node fails or is replicated asynchronously, two clients may both get the lock, and there are no fencing tokens|
|Redlock (Redis, multiple nodes)|Acquire the lock on a majority of independent Redis nodes|Better availability than one node|Debated: relies on timing and clock assumptions and provides no fencing tokens, so it is not recommended where correctness is critical|
|ZooKeeper|The lock is an ephemeral sequential node, and the client with the lowest number holds it|Strong consistency, the lock is released automatically if the client's session dies, sequence numbers can serve as fencing tokens|Heavier to run, more complex|
|etcd or Consul|Locks use leases and sessions on top of a consensus-based store|Strongly consistent, leases with keep-alive, revision numbers usable as fencing tokens|Requires running and operating the cluster|

## Leader Election
Many systems need exactly one node to play a special role: the primary database that accepts writes, the scheduler that triggers jobs, the coordinator that assigns work to others. Leader election is the process by which a group of nodes agrees on which one is the leader, and chooses a new one when it fails. Leader election is closely related to locks: the leader is effectively the holder of a lock that must be renewed, and failing to renew it triggers a new election.

The difficulty is the same as for locks. The nodes cannot tell a dead leader from a slow one, so a leader that is merely paused might wake up and continue acting as a leader after another has been elected, which causes split brain, where two leaders operate at the same time. Safe election therefore needs a rule that at most one leader can exist for a given period, and fencing so that an old leader's actions are rejected.

|Approach|How it works|Notes|
|---|---|---|
|Bully algorithm|The node with the highest ID that is alive becomes leader, and any node that notices the leader is gone starts an election|Simple, but depends on reliable failure detection and has issues in a partitioned network|
|Lease via a coordination service|Nodes compete to create a key or ephemeral node in ZooKeeper, etcd or Consul, and the winner is leader while it keeps renewing its lease|Common and practical, for example Kubernetes controllers use a Lease object|
|Consensus protocol (Raft, Paxos)|Nodes vote, and a candidate needs a majority|Safe by design, used inside databases and coordination services|

### Leader Election in Raft
Raft is the best known consensus algorithm, designed to be understandable. Each node is in one of three states: follower, candidate or leader. Time is divided into numbered terms, and each term has at most one leader. The leader sends regular heartbeats to followers. If a follower hears nothing for a randomly chosen election timeout (typically a few hundred milliseconds), it assumes the leader is gone, increments the term, becomes a candidate and asks the others for votes. Each node votes for at most one candidate per term and only for one whose log is at least as up to date as its own. A candidate that receives votes from a majority becomes the leader and starts sending heartbeats. The random timeouts make it unlikely that two nodes start elections at the same moment, and if a vote is split, a new election with new random timeouts follows.

Several properties come from this. Requiring a majority means that two leaders can never be elected in the same term, because two majorities always overlap in at least one node. This is why clusters use an odd number of nodes: 3 nodes tolerate 1 failure, 5 tolerate 2, and 4 nodes tolerate only 1, the same as 3. Term numbers act like fencing tokens, since any message from a leader with an older term is ignored. And a leader that is cut off from the majority cannot commit any writes and steps down, so the minority side of a partition cannot make progress, which is the CP choice from the CAP notes.

## Clocking and Ordering
Every computer's clock drifts, and clocks on different machines never agree exactly. NTP keeps them close, usually within milliseconds, but it can also move a clock suddenly, even backwards. So comparing timestamps from different machines to decide what happened first is unreliable. For example, with last-write-wins conflict handling, a skewed clock can make an older write look newer and silently throw away the real latest one. Two simple rules help: use a monotonic clock, which only moves forward, to measure durations and timeouts, and do not trust wall-clock time to order events across machines.

Instead, systems order events by cause and effect. If event A could have influenced event B (for example A sent a message that B received), then A happened before B. If neither could have influenced the other, they are concurrent. Logical clocks track this without needing real time.

|Clock|How it works|What it can tell you|
|---|---|---|
|Lamport clock|One counter per node. Increase it on every event. When receiving a message, set it to the larger of your counter and the message's counter, plus one|If A caused B, A has the smaller number. It cannot tell you whether two events were concurrent|
|Vector clock|A list of counters, one per node, sent along with messages|Can tell whether one event came before another or whether they were concurrent, so conflicting updates can be detected. Used in Dynamo-style databases|
|Hybrid logical clock|Real time plus a small counter|Stays close to real time while keeping a correct causal order. Used in CockroachDB and MongoDB|

When everyone must agree on one exact order, the usual answer is to let a single leader hand out sequence numbers, or to use a consensus log such as Raft. Kafka keeps order only inside a partition, so related events are sent to the same partition.

## Distributed Transactions
Sometimes one operation must change data in several databases or services, such as taking money from one account and adding it to another. Either everything must happen or nothing must, even if a machine crashes in the middle. There are two main approaches.

### Two-Phase Commit (2PC)
A coordinator runs the transaction in two steps. In step one (prepare), it asks every participant whether it can commit. Each participant saves its work, locks the data and answers yes or no, and a yes is a promise that it will commit if told to. In step two (commit), if everyone said yes, the coordinator tells everyone to commit, and if anyone said no, it tells everyone to roll back.

This gives strong all-or-nothing results, but it has a serious weakness: if the coordinator crashes after the participants said yes, they are stuck waiting with their locks held, because they cannot decide on their own. It is also slow, since it needs several network round trips, and every participant must be available. For these reasons, it is used between a few databases that need strict correctness, but rarely across microservices.

### The Saga Pattern
A saga splits the operation into a series of small local transactions, one per service, each committed right away. If a later step fails, the earlier steps are undone by running compensating actions, which are new operations that reverse the effect. For an order, the steps might be create order, reserve stock, charge payment and ship, and if the payment fails, the stock is released and the order is cancelled. The steps can be coordinated by services reacting to each other's events (choreography) or by a central controller giving the instructions (orchestration).

The catch is that a saga has no isolation, so other users can briefly see half-finished states, such as an order that is pending. Each step and each compensation must also be safe to repeat, since messages can be delivered twice, so they should be idempotent.

| _                         | Two-phase commit                           | Saga                                      |
| ------------------------- | ------------------------------------------ | ----------------------------------------- |
| All-or-nothing            | Strongly, at once                          | Eventually, by undoing steps              |
| Others see half-done work | No                                         | Yes                                       |
| Speed and availability    | Slower, all participants must be up        | Faster, steps run independently           |
| Risk                      | Blocks if the coordinator fails            | Needs correct compensation code           |
| Best for                  | A few databases needing strict correctness | Microservices and long business workflows |

The best approach is often to avoid distributed transactions altogether, by keeping data that must change together in the same service and database, and using the outbox pattern and idempotent consumers when events must cross services.

## Coordination Trade offs
Every method above makes machines wait for each other. That waiting makes things slower (every step needs a network round trip), less available (the operation needs enough nodes to be reachable, so a partition can stop it), and more complex (stuck locks, split brain, half-finished transactions). This is the same trade-off as in the CAP and PACELC notes, seen from a different angle: stronger guarantees need more coordination, and more coordination costs speed and availability.

So the guiding rule is to use the weakest coordination that still protects what really matters. Some things need strict coordination, like never spending the same money twice or never giving one seat to two people. Many things do not, like counters, likes and feeds, which can be eventually consistent, and a rare conflict can be fixed afterwards with a compensation or an apology.

|If you need|Use|
|---|---|
|Only one worker to run a job, and a rare duplicate is harmless|A simple lease lock, for example in Redis|
|Safe exclusive access to important data|A lock from etcd or ZooKeeper with fencing tokens, or a version column|
|One node in charge|Leader election with Raft, etcd, ZooKeeper or Kubernetes leases|
|To order events across machines|Logical clocks, or a single leader or log that assigns the order|
|To detect conflicting updates|Vector clocks or version vectors|
|Strict all-or-nothing across a few databases|Two-phase commit|
|A workflow across microservices|A saga, with idempotent steps|
|High availability and speed, with temporary differences allowed|Eventual consistency|