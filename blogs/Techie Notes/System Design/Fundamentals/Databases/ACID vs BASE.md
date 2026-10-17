ACID and BASE are two sets of promises a database can make about how it handles data. ACID puts correctness first: every transaction is safe and exact, even if it costs some speed. BASE puts availability and speed first: the system stays up and fast, and accepts that data may be slightly out of date for a short while. Neither is better. They suit different kinds of data.

## ACID
ACID is the traditional promise of relational databases such as PostgreSQL, MySQL and Oracle. It applies to a transaction, which is a group of operations treated as one unit.

| Letter         | Meaning                       | In plain words                                                                                                          |
| -------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| A: Atomicity   | All or nothing                | Either every step of the transaction happens, or none does. No half-finished work                                       |
| C: Consistency | Rules are never broken        | The data always follows its rules, such as balances never going negative or a foreign key always pointing to a real row |
| I: Isolation   | Transactions do not interfere | Transactions running at the same time behave as if they ran one after another                                           |
| D: Durability  | Saved means saved             | Once the database says "committed", the data survives crashes and power cuts                                            |

A transfer between two accounts shows it in code. Both updates succeed together, or neither takes effect.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
UPDATE accounts SET balance = balance + 500 WHERE id = 2;
COMMIT;   -- if anything fails before this point, ROLLBACK undoes everything
```

One note to avoid confusion: the "C" in ACID (data follows the rules) is not the same as the "C" in the CAP theorem (all nodes show the same latest data).

## BASE
BASE is the approach of many distributed NoSQL databases such as Cassandra, DynamoDB and CouchDB. The name was chosen as a playful opposite of ACID.

| Letter                  | Meaning                           | In plain words                                                                                                   |
| ----------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| BA: Basically Available | The system keeps working          | It answers requests even when some servers or parts of the network fail, though the answer may not be the newest |
| S: Soft state           | Data may change without new input | Because copies are still catching up with each other, the state of the system can shift over time on its own     |
| E: Eventual consistency | It will agree in the end          | If no new updates arrive, all copies eventually become the same, though not instantly                            |

## ACID vs BASE

| Aspect                    | ACID                                                   | BASE                                 |
| ------------------------- | ------------------------------------------------------ | ------------------------------------ |
| Priority                  | Correctness                                            | Availability and speed               |
| Data is always up to date | Yes                                                    | Not always, briefly stale            |
| Consistency               | Strong, immediate                                      | Eventual                             |
| During a network failure  | May refuse requests to stay correct                    | Keeps answering, may give older data |
| Scaling                   | Harder to scale out across many servers                | Designed to scale out easily         |
| Speed                     | Slower for writes, because of coordination and locking | Faster, because less waiting         |
| Typical databases         | PostgreSQL, MySQL, Oracle, SQL Server                  | Cassandra, DynamoDB, CouchDB, Riak   |
| CAP theorem leaning       | CP (consistency over availability)                     | AP (availability over consistency)   |
| Best for                  | Money, orders, inventory, bookings                     | Feeds, likes, carts, logs, analytics |

## Case Studies

### Bank Transfer (ACID)
Asha sends 500 rupees to Ravi. The bank must take 500 from Asha's account and add 500 to Ravi's.

Imagine this was done without ACID. The system subtracts 500 from Asha, then the server crashes before adding 500 to Ravi. The money has vanished, and neither person nor the bank can say where it went. Or imagine Asha has 600 rupees and starts two 500-rupee transfers at the same moment. If both check her balance before either has updated it, both look fine, and she spends 1,000 from a balance of 600.

ACID prevents each of these problems.
- Atomicity: the debit and the credit happen together, or neither happens. A crash in the middle rolls everything back.
- Consistency: a rule such as "balance cannot go below zero" is enforced, so the second transfer is rejected.
- Isolation: the two simultaneous transfers are handled as if one came first, so the second sees the reduced balance.
- Durability: after Asha sees "transfer successful", the record survives even if the server loses power a second later.

Why not BASE here? If the system served an old balance for a while, people could overdraw accounts or spend the same money twice. A wrong answer costs real money, so a short delay or an error is better than a wrong result. This is why banks, payment systems and stock trading use ACID databases.

### Likes on a Social Media Post (BASE)
A celebrity posts a video, and 100,000 people like it within a minute. Servers around the world are receiving likes at the same time.

Now think about doing this the ACID way. There is one like counter. Every like must lock it, update it and release it before the next one can proceed, and with servers in different continents, each update also has to be confirmed everywhere. Likes would queue up, the app would feel slow, and if the link between two regions broke, the system might refuse likes altogether.

BASE handles it differently.

- Basically available: each like is accepted immediately by the nearest server, and the app always responds, even if part of the network is down.
- Soft state: the servers copy likes to each other in the background, so for a few seconds, different servers hold slightly different counts.
- Eventually consistent: once the copies catch up, everyone sees the same total.

During those few seconds, one user might see 1,204,300 likes and another 1,204,150. Nobody is harmed by that, and no one will ever notice, while the benefits are large: instant response, no downtime and the ability to handle huge traffic by adding more servers. The same reasoning applies to comments, view counts, follower counts and news feeds.
