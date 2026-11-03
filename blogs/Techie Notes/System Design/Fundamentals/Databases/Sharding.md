When a database outgrows a single machine, partitioning alone is not enough. Partitioning splits a table into pieces, but all of them still sit on one server, so the CPU, memory, disk, and write throughput of that one server remain the ceiling. A single large Postgres instance can handle tens of terabytes and tens of thousands of writes per second, which is more than most applications will ever need. But once storage or write throughput exceeds what the biggest available machine can do, buying a bigger machine stops working.

Sharding solves this by splitting the data across multiple independent database servers. Each shard is a standalone database with its own CPU, memory, storage, and connection pool, and it stores only a subset of the rows. Together the shards make up the full dataset. Capacity grows by adding shards instead of buying bigger hardware.

The benefit is horizontal scale for storage, reads, and writes. The cost is complexity. Something has to decide which shard owns each row, queries that span shards become expensive, transactions across shards need distributed coordination, and adding or removing shards means moving data. Because of this, sharding should be a last resort after caching, indexing, read replicas, partitioning, and vertical scaling.

## Shard Key
The shard key is the column that decides which shard owns a row. It is the most important design decision, because it determines load distribution and which queries stay on a single shard. A good shard key has three properties:

|Property|Meaning|Example|
|---|---|---|
|High cardinality|Many distinct values, so data can be spread finely|`user_id`, `short_code`|
|Even distribution|No value or range receives most of the data or traffic|Hashed IDs|
|Query alignment|The most common query contains the key, so it hits one shard|“All posts for a user” sharded by `user_id`|
In an interview, always state the shard key explicitly and say why it was chosen.

## Distribution Strategy
Once the key is chosen, a strategy decides how key values map to shards. The strategies differ in how evenly they spread data and how painful it is to add shards later.

### Range Based Strategy
Each shard owns a contiguous range of key values.
```
RANGES = [
    (0,          10_000_000, "shard1"),
    (10_000_001, 20_000_000, "shard2"),
    (20_000_001, 30_000_000, "shard3"),
]

def route(user_id: int) -> str:
    for low, high, shard in RANGES:
        if low <= user_id <= high:
            return shard
```

It is simple and keeps neighbouring keys together, which supports range scans. The weakness is that load follows the data. In the early days only the first shard has data, and with monotonically increasing IDs all new and most active users land on the last shard, which becomes a hotspot. Ranges must be split before a shard gets too big. It fits data that falls into clean ranges and grows steadily, but it is not the usual production choice.

### Hash Based Sharding
The key is hashed and the result decides the shard.
```
import hashlib

def route(key: str, n_shards: int) -> int:
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return h % n_shards
```

A good hash function scrambles its input, so each shard receives close to an equal share and there are no ordering hotspots. The downsides are that range queries cannot be answered from one shard (neighbouring keys are scattered), and that changing the number of shards changes the result of `% N` for almost every key. Going from 3 shards to 4 means nearly all data must move.

### Consistent Hashing
Consistent hashing fixes the resharding problem. Both the shards and the keys are hashed onto a ring. To find a key’s shard, start at its position and walk clockwise to the first shard.
```
import bisect, hashlib

def h(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

class Ring:
    def __init__(self, nodes, vnodes=200):
        self.ring, self.keys = {}, []
        for node in nodes:
            for i in range(vnodes):          # virtual nodes
                pos = h(f"{node}#{i}")
                self.ring[pos] = node
                self.keys.append(pos)
        self.keys.sort()

    def get_node(self, key: str) -> str:
        idx = bisect.bisect(self.keys, h(key)) % len(self.keys)
        return self.ring[self.keys[idx]]
```

Adding a shard moves only about 1/N of the keys, and removing one hands its keys to the next shards on the ring. Virtual nodes place each physical shard on the ring many times, which evens out the distribution, spreads a failed node’s load across all the others instead of one neighbour, and lets stronger machines own more slices. This is the industry default: when someone says “shard by user ID”, hash-based sharding with consistent hashing is what is usually assumed. Cassandra and DynamoDB use it, and Redis Cluster uses a fixed 16,384-slot variant.

## Routing
A request must reach the shard that owns the key. There are three common approaches.

|Approach|How it works|Trade-off|
|---|---|---|
|Client-side|The application holds the ring or shard map|Fast and no extra hop, but every client must stay in sync|
|Proxy / router layer|A routing service (for example Vitess or mongos) forwards queries|Transparent to the app, but one more component to run|
|Coordinator nodes|Any node accepts the request and forwards it (Cassandra, Dynamo style)|No central router, more complex internally|

The ring or shard map is usually distributed through ZooKeeper, etcd, or gossip so that all participants agree on ownership.

## Challenges
### Hotspots
Even with a good key, one shard can receive far more traffic than the others. If a very popular user lands on shard 1, every view, like, and comment goes there while the other shards stay idle.
**Solution**:
1. Use Compound Shard key (if previous key was just name, you can use name and created at timestamp together)
2. Dedicate a shard if the peak keys are predictable
3. Cache the most read keys

### Cross Shard Operation
A query that does not contain the shard key must be sent to every shard and the results merged, which is called scatter-gather. “Get user 123’s profile” is fast, but “top 10 posts across the platform” needs a query on every shard plus a global ranking. These queries cannot be eliminated, but they should be the exception.
**Solution:**
1. Choose the right shard key
2. Cache

Sometimes there might be issue with Cross Shard Consistency. On a single database, moving money between two accounts is one atomic transaction. If the two accounts live on different shards, that guarantee disappears. There are two ways to solve it:
1. **Two-phase commit (2PC):** A coordinator asks all shards if they can commit, then tells them all to commit
2. **Saga:** A chain of small local steps, each with a compensating action that undoes it if a later step fails

> **Note: Resharding and Rebalancing**
Adding capacity means moving data between shards while the system is serving traffic. Consistent hashing limits the movement to about 1/N of the keys. Data is typically copied in the background, reads are served from both old and new locations during the migration (dual read), and ownership flips when the copy is complete. A useful technique is pre-splitting: create many logical shards (say 1,024) up front and map them onto a few physical machines. Growing then means moving whole logical shards to new machines without rehashing any keys.

