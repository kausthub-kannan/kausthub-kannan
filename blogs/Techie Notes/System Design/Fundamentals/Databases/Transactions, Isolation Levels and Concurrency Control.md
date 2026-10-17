
## Transactions and the Concurrency Problem
A transaction is a group of operations that the database treats as one unit, with the ACID guarantees described in the ACID vs BASE notes. The Isolation guarantee is the subject here: when many transactions run at the same time, each should behave as if it ran alone. Perfect isolation (running one transaction at a time) would be very slow, so databases offer levels that allow some interference in exchange for speed. To choose a level, you need to know the problems that can occur.

### Concurrency Anomalies
|Anomaly|What happens|Example|
|---|---|---|
|Dirty read|You read data that another transaction has changed but not yet committed, and it may be rolled back|T1 sets a balance to 0 but has not committed, T2 reads 0, then T1 rolls back|
|Non-repeatable read|You read the same row twice in one transaction and get different values, because someone committed a change in between|T1 reads a price of 100, T2 changes it to 120 and commits, T1 reads again and sees 120|
|Phantom read|You run the same query twice and get different sets of rows, because someone inserted or deleted matching rows|T1 counts 5 active orders, T2 adds a new one, T1 counts 6|
|Lost update|Two transactions read the same value, both modify it and write back, so one change overwrites the other|Two withdrawals both read balance 100 and write 70, losing one withdrawal|
|Write skew|Two transactions read overlapping data, make decisions based on it and write to different rows, together breaking a rule that neither broke alone|Two doctors both check that at least two are on call, and both go off call, leaving none|

## Isolation Levels
The SQL standard defines four isolation levels, from weakest to strongest, according to which anomalies they allow.

|Isolation level|Dirty read|Non-repeatable read|Phantom read|Notes|
|---|---|---|---|---|
|Read Uncommitted|Possible|Possible|Possible|Rarely used|
|Read Committed|Prevented|Possible|Possible|Default in PostgreSQL, Oracle and SQL Server|
|Repeatable Read|Prevented|Prevented|Possible by the standard|Default in MySQL InnoDB|
|Serializable|Prevented|Prevented|Prevented|Results are as if transactions ran one at a time|

Real databases differ from the textbook table. PostgreSQL treats Read Uncommitted as Read Committed, so dirty reads never happen. Its Repeatable Read uses snapshot isolation, which also prevents phantoms but still allows write skew, and only its Serializable level prevents everything. MySQL InnoDB's Repeatable Read uses a snapshot for ordinary reads plus gap locks to limit phantoms. The stronger the level, the more locking, waiting or transaction aborts, so throughput drops. The usual choice is Read Committed for most work, and Serializable, or explicit locking, for the specific operations where correctness depends on it.

### Concurrency Control: Three Approaches
Isolation levels describe the guarantee. Concurrency control is the mechanism the database uses to provide it.

|Approach|Idea|Strengths|Weaknesses|
|---|---|---|---|
|Pessimistic (locking)|Assume conflicts will happen, so lock the data before using it|Simple to reason about, safe under heavy contention|Waiting, deadlocks, reduced concurrency|
|Optimistic|Assume conflicts are rare, work without locks, and check at commit time that nothing changed, retrying if it did|No lock waiting, good when conflicts are rare|Wasted work and retries under high contention|
|MVCC|Keep multiple versions of each row, so readers see a consistent snapshot and do not block writers|Readers never block writers and writers never block readers|Old versions must be cleaned up, long transactions cause bloat|

### Locking
Databases use shared locks for reading, which many transactions can hold at once, and exclusive locks for writing, which only one can hold. Locks can apply to a row, a page or a whole table. Under two-phase locking (2PL), a transaction acquires locks as it goes and releases none until it commits or rolls back, which guarantees serializability but limits concurrency. An application can request a lock explicitly with `SELECT ... FOR UPDATE`.

A deadlock happens when two transactions each hold a lock the other needs, so neither can continue. The database detects the cycle and aborts one of them, so applications must be ready to retry. Deadlocks are reduced by always acquiring locks in the same order, keeping transactions short and avoiding user interaction inside a transaction.

### MVCC
Multi-version concurrency control keeps several versions of a row. A write creates a new version and does not overwrite the old one, and each transaction reads the version that was current when its snapshot was taken. This lets reads proceed without waiting for writes, which is why PostgreSQL, MySQL InnoDB and Oracle perform well under mixed workloads. PostgreSQL stores versions in the table itself and removes dead ones with VACUUM, while InnoDB keeps old versions in undo logs. The costs are bloat from old versions and the problems caused by long-running transactions, which stop old versions from being removed.

### Fixing the Classic Problems
|Problem|Fixes|
|---|---|
|Lost update|Use an atomic update such as `SET balance = balance - 30`, lock the row with `FOR UPDATE`, use optimistic locking with a version column, or use Serializable|
|Write skew|Use Serializable, lock the rows that the decision depends on, or enforce the rule with a constraint|
|Phantoms|Use Serializable, or range or predicate locks|
|Double booking|Use a conditional update that checks the state in the same statement|

## CDC - Change Data Capture
Change data capture is a technique for detecting every change (insert, update and delete) made to a database and delivering these changes, in order and in near real time, to other systems. Instead of periodically copying whole tables, CDC turns the database into a stream of events such as "order 42 changed from pending to shipped".

A real system rarely has a single database. The same data must also appear in a search index, a cache, a data warehouse, other microservices and analytics pipelines, and these need to stay in sync. The tempting approach is the dual write: the application writes to the database, then also writes to the search index or publishes a message. This is fragile. If the application crashes between the two writes, or one of them fails, the systems drift apart permanently, and two concurrent writers can apply their updates in a different order in each system. CDC fixes this by using the database as the single source of truth and deriving everything else from its own record of changes.

|Method|How it works|Pros|Cons|
|---|---|---|---|
|Polling with a timestamp or version column|A job periodically queries for rows where `updated_at` is newer than the last check|Simple, no special setup|Misses deletes and intermediate changes, adds query load, delayed, needs a reliable column|
|Triggers|Database triggers write each change into an audit table|Captures all changes, works anywhere|Slows every write, adds complexity to the schema|
|Log-based CDC|Reads the database's own transaction log (WAL, binlog, oplog)|Very low impact, captures every change including deletes, in commit order, near real time|Needs database configuration, depends on the database's log format|
|Application-level dual write|The application publishes events itself|No database access needed|Unreliable, as explained above, and should be avoided|

Log-based CDC is the standard modern approach. Every database already records each change in a log, so that it can recover from a crash and feed replicas, as described in the replication notes. A CDC tool reads this same log as one more consumer, so it does not add any load to the queries of the application.

|Database|Log used by CDC|
|---|---|
|PostgreSQL|Write-ahead log, read through logical decoding and replication slots|
|MySQL and MariaDB|Binary log (binlog)|
|MongoDB|Oplog, exposed through change streams|
|SQL Server|Built-in CDC tables and the transaction log|
|Oracle|Redo logs, for example through LogMiner|

### Typical FLow
```
 [ App ] --> [ Database ] --WAL--> [ CDC connector (Debezium) ] --> [ Kafka ]
                                                                      |
                              +---------------------+-----------------+-----------------+
                              |                     |                                   |
                       [ Elasticsearch ]      [ Redis cache ]                  [ Data warehouse ]
                       (search stays in sync)  (invalidate on change)         (analytics, reporting)
```

Debezium is the best known open-source tool. It runs on Kafka Connect, reads the database log and publishes each change to a Kafka topic, usually one per table. Other options include AWS Database Migration Service, Maxwell and managed data pipeline products such as Fivetran and Airbyte. Putting Kafka in the middle means that any number of consumers can read the same stream at their own pace and replay it, as in the message queue notes.

### Use cases
|Use case|How CDC helps|
|---|---|
|Keeping a search index in sync|Changes in the database update Elasticsearch within moments|
|Cache invalidation or update|A change event triggers removal or refresh of the cached entry, instead of waiting for a TTL|
|Data warehouse and analytics feeds|Changes flow continuously to the warehouse without heavy batch exports|
|Event-driven microservices|Other services react to changes in a service's data without that service publishing events by hand|
|Database migration with no downtime|The new database is kept in sync with the old one during the move|
|Audit trails and history|A complete record of what changed, and when|
|Read models and materialized views|Precomputed views are updated incrementally, instead of through full refreshes|

### Out of the box pattern
service, which other services should not depend on. The outbox pattern fixes this. The application writes its business change and a meaningful event, such as "OrderPlaced", into an outbox table in the same transaction, which guarantees both or neither. A CDC connector then reads the outbox table from the log and publishes those events to Kafka. This gives reliable event publishing, with no dual write, and with events designed as a stable contract, and it is the standard way to implement the reliable messaging needed by sagas, as in the architecture and coordination notes.

### CDC vs Replication
|Aspect|Database replication|CDC|
|---|---|---|
|Purpose|Make an identical copy for availability and read scaling|Feed changes to other, often different, systems|
|Target|Usually the same database engine|Anything: Kafka, search, warehouse, cache, another database type|
|Form of the data|Physical or full logical copy|Stream of individual change events|
|Consumers|One replica per copy|Many independent consumers|

