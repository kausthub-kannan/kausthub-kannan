PACELC is an extension of the CAP theorem, proposed by Daniel Abadi in 2010. It is read as "if Partition, then Availability or Consistency; Else, Latency or Consistency." The first half, PAC, is just CAP: when the network between nodes breaks, a distributed system must choose between staying available and staying consistent. The second half, ELC, is the new part: even when the network is perfectly healthy, a distributed system still has to choose between low latency and strong consistency.

It exists because CAP, while correct, is incomplete as a design tool. It only describes what happens during a network partition, and partitions are rare. A system spends almost all of its life in normal operation, and during that time it still faces a trade-off that affects every single request. PACELC captures both situations, which is why it describes real databases more accurately than CAP alone.

## How PACELC handles better than CAP
CAP only has something to say when the network is broken. Everything that happens while the network is healthy, which is nearly all of a system's life, is outside its scope. The following case study shows two designs that CAP cannot tell apart for most of the time, and how PACELC separates them.

**Example:**
ShopNow is an online store with customers worldwide. Its database keeps three replicas (copies of the same data on different servers): one in Mumbai, one in Frankfurt and one in Virginia, USA. The warehouse that packs and ships orders runs in Mumbai. When data is written, the copies must be updated, and there are two basic ways to do it:

- Synchronous replication: the system waits until the other replicas confirm the write before telling the client it succeeded.
- Asynchronous replication: the system confirms the write as soon as one nearby node has it, and copies it to the other replicas in the background.

ShopNow is considering two designs, and we follow one event through both: a customer in the USA changes the delivery address on an order, and a moment later the Mumbai warehouse reads that order to print the shipping label

1. Asynchronous Replication: 
   The customer's change is saved on the Virginia replica and acknowledged in about 2 ms, so the page feels instant. The update is then copied to Frankfurt and Mumbai in the background, which takes a few hundred milliseconds because of the distance. If the warehouse in Mumbai reads the order during that window, it still sees the old address, and a label for the wrong address may be printed. Nothing has failed here, and the network is perfectly healthy. The staleness is simply the cost of not waiting.

2. Synchronous Replication
   The write is acknowledged only after all replicas confirm it. Since the nearest and furthest replicas are on opposite sides of the world, the customer waits roughly 300 ms for the save to complete (an illustrative figure, since a round trip between the USA and India alone is around 200 ms). In return, the moment the customer sees the confirmation, every replica has the new address, so the warehouse can never read the old one.

CAP can only label the five minutes of failure. It cannot describe the difference that every customer and every warehouse worker experiences on every request: a 2 ms save with a risk of a stale read, against a 300 ms save with no such risk. It also cannot explain the stale label in Design A, because that problem occurs with no partition at all, and CAP says nothing about staleness without a partition.

PACELC covers both situations by giving each design two labels, one for the partition case and one for normal operation.

|Aspect|Design A|Design B|
|---|---|---|
|During a partition|Chooses availability (PA)|Chooses consistency (PC)|
|Normal operation|Chooses latency (EL)|Chooses consistency (EC)|
|PACELC label|PA/EL|PC/EC|
|Save latency for the customer|About 2 ms|About 300 ms|
|Can the warehouse read an old address|Yes, for a short window|No|
|Experience during a link failure|US customers keep working, conflicts resolved afterwards|US customers see errors until the link is back|
What the company chooses is based on the need - as said system design never as the perfect answer

## Reading the PACELC Notation
A system is described with two choices, one for each situation, written as a pair such as PA/EL.

|Part|Situation|Choice|Meaning|
|---|---|---|---|
|PA|During a Partition|Availability|Keep answering requests, accept that data may be stale or conflicting|
|PC|During a Partition|Consistency|Refuse some requests to keep the data correct|
|EL|Else (normal operation)|Latency|Respond quickly, even if replicas may not yet be in sync|
|EC|Else (normal operation)|Consistency|Wait for replicas to agree, accept slower responses|

### The Four Combinations

|Type|During a partition|Normal operation|Typical examples|Good for|
|---|---|---|---|---|
|PA/EL|Stays available|Favors low latency|Cassandra, DynamoDB (default settings), Riak|Social feeds, like counters, shopping carts, activity logs, anything that tolerates brief staleness|
|PA/EC|Stays available|Favors consistency|MongoDB is often cited here, depending on its settings|Systems that want correct data normally but prefer answering over failing during a partition|
|PC/EL|Protects consistency|Favors low latency|Yahoo PNUTS|A less common combination, where normal reads are fast but a partition makes the system strict|
|PC/EC|Protects consistency|Favors consistency|Google Spanner, HBase, VoltDB, ZooKeeper, etcd|Banking, payments, inventory, coordination and configuration data|
## Real World Examples
Cassandra and DynamoDB are PA/EL by default. By default, they accept writes quickly on a node close by and replicate in the background, so they are very fast and stay available even during failures, and the price is that a read may briefly return older data.

Google Spanner is PC/EC. It provides strong consistency across the globe by using synchronized atomic clocks (TrueTime) and by waiting a short, deliberate time before committing a transaction, so that ordering is guaranteed. The price is higher write latency compared to an eventually consistent store, and the design is acceptable because Spanner is built for data like financial records, where correctness matters most.

Traditional single-leader databases with synchronous replicas, such as a primary with synchronous standbys in PostgreSQL, behave as EC, since a commit waits for the standby to confirm and every commit pays that latency. The same database with asynchronous replicas is EL, since commits are fast but a replica read may lag.

Some scenarios are ...

| Data in an e-commerce system     | Wrong answer vs no answer                     | Cost of staleness vs cost of latency          | Suitable behavior |
| -------------------------------- | --------------------------------------------- | --------------------------------------------- | ----------------- |
| Payments and account balances    | A wrong answer is far worse                   | Correctness matters more than speed           | PC/EC             |
| Inventory count at checkout      | Overselling is costly                         | Correctness matters at the moment of purchase | PC/EC             |
| Product catalog and descriptions | Slightly old data is harmless                 | Fast pages matter most                        | PA/EL             |
| Shopping cart                    | Available cart matters more than perfect sync | Speed and availability matter                 | PA/EL             |
| Likes, views and recommendations | Counts being off is harmless                  | Speed matters most                            | PA/EL             |