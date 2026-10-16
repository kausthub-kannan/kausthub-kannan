As an application grows, a single table can reach hundreds of millions or billions of rows. Queries then have to scan or search through enormous amounts of data, indexes become large and slow to maintain, and routine jobs like backups, vacuuming and deleting old data take a very long time. Partitioning solves this by dividing one huge table into smaller, more manageable pieces called partitions, all of which stay inside the same database server. To the application, it still looks like one table, and queries are written the same way, but the database stores the data as several physical pieces and decides internally which pieces to look at.

The benefits come from not touching all the data every time. With partition pruning, the database looks at the query condition, works out which partitions could contain matching rows, and skips the rest entirely, so queries scan far fewer rows and use less CPU and memory. Each partition has its own smaller indexes, which fit in memory more easily. Maintenance becomes simpler because operations can target one partition: old data can be removed by dropping a whole partition instead of running a huge, slow DELETE, and a partition can be archived, backed up or moved to cheaper storage independently.

It is important to be clear about what partitioning does not do. Because everything stays on one server, it does not add extra machines, so it is limited by the CPU, memory and disk of that one server, and it does not protect against that server failing. Scaling across multiple servers is sharding, which is covered later in these notes.

## Horizontal vs Vertical Partitioning
There are two basic ways to cut a table. Horizontal partitioning splits by rows, so each partition has the same columns but holds a different group of rows. Vertical partitioning splits by columns, so each piece has all of the rows' identity (the key) but only some of the columns.

|Aspect|Horizontal partitioning|Vertical partitioning|
|---|---|---|
|What is split|Rows|Columns|
|Structure of each piece|Same columns, different rows|Same rows (linked by key), different columns|
|Decided by|A partition key such as date, region or ID|How often and together columns are accessed|
|Main benefit|Fewer rows scanned, easier data lifecycle management|Narrow, frequently used data stays small and fast, heavy data is kept away|
|Typical use|Orders by month, events by user|Separating a user's login info from a large profile or image data|
|Built into PostgreSQL|Yes, declarative partitioning|No, done by designing separate tables|
|Drawback|Queries without the partition key scan all partitions|Needs a join to bring the columns back together|

## Horizontal Partitioning Methods
Horizontal partitioning is carried out using one of three methods, which differ in how the database decides which partition a row belongs to. The column used to decide is called the partition key, and choosing it well is the most important design decision.
### Range Partitioning
Range partitioning assigns each row to a partition based on which range its key falls in. It is the most common method and is ideal for time-series data such as orders, logs and events. In this example, an orders table is split by year of order date.
```sql
CREATE TABLE orders (
    order_id    BIGSERIAL,
    customer_id BIGINT         NOT NULL,
    order_date  DATE           NOT NULL,
    amount      NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (order_id, order_date)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE orders_2026 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Catches any row that fits no range
CREATE TABLE orders_default PARTITION OF orders DEFAULT;
```

The lower bound of a range is inclusive and the upper bound is exclusive, so a row dated 2025-12-31 goes into orders_2025, and 2026-01-01 goes into orders_2026. Rows are inserted into the parent table as usual, and PostgreSQL routes each one to the correct partition. When a query filters on the partition key, pruning means only the relevant partition is read.
```sql
-- Only orders_2026 is scanned
EXPLAIN
SELECT * FROM orders
WHERE order_date >= '2026-03-01' AND order_date < '2026-04-01';
```

The big operational advantage is how easily old data is removed. Instead of deleting millions of rows one by one, the partition is detached and dropped, which is nearly instant.
```sql
ALTER TABLE orders DETACH PARTITION orders_2025;
DROP TABLE orders_2025;
```

### List Partitioning
List partitioning assigns rows to a partition based on an explicit list of values for the key. It suits categories, such as the region of a customer, and it can be used to keep data for different regions together, which also helps with data residency rules.
```sql
CREATE TABLE customers (
    customer_id BIGSERIAL,
    name        TEXT NOT NULL,
    region      TEXT NOT NULL,
    PRIMARY KEY (customer_id, region)
) PARTITION BY LIST (region);

CREATE TABLE customers_asia PARTITION OF customers
    FOR VALUES IN ('IN', 'SG', 'JP');

CREATE TABLE customers_europe PARTITION OF customers
    FOR VALUES IN ('DE', 'FR', 'GB');

CREATE TABLE customers_other PARTITION OF customers DEFAULT;
```

A query such as `SELECT * FROM customers WHERE region = 'IN'` reads only customers_asia. The weakness is that the partitions can end up very uneven, since one region may have far more customers than another, and every new category that matters needs a new partition or lands in the default one.

### Hash Partitioning
Hash partitioning is used when there is no natural range or category, or when the aim is to spread data and load evenly. The database applies a hash function to the partition key, and the result decides the partition. In PostgreSQL, a partition is defined by a modulus (the total number of partitions) and a remainder (which bucket this partition owns), so that the hash of the key divided by the modulus gives the bucket number. Here a user events table is split into four partitions by user ID.
```sql
CREATE TABLE user_events (
    event_id   BIGSERIAL,
    user_id    BIGINT      NOT NULL,
    event_type TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (event_id, user_id)
) PARTITION BY HASH (user_id);

CREATE TABLE user_events_p0 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE user_events_p1 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE user_events_p2 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE user_events_p3 PARTITION OF user_events
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

Because a good hash function distributes values randomly and evenly, each partition ends up holding about a quarter of the rows, and no partition becomes a hotspot. A lookup like `WHERE user_id = 42` is pruned to exactly one partition. The downsides are that range queries such as `WHERE user_id BETWEEN 100 AND 200` cannot be pruned and must scan every partition, since neighbouring IDs are scattered, and that changing the number of partitions later means rows must be redistributed, which is a heavy operation.

## Pitfalls in choosing Partition key
|Pitfall|What happens|How to handle it|
|---|---|---|
|Query does not use the partition key|The database must scan every partition, which can be slower than an unpartitioned table|Pick a key that matches the main query patterns|
|Too many partitions|Query planning gets slower and metadata grows|Keep partitions to a reasonable number, usually from tens to a few hundred|
|Hotspot on the newest range partition|All new writes hit one partition|Use hash, or sub-partition the range partition|
|Unique constraints need the partition key|A global unique ID across partitions is not enforced by the key alone|Include the partition key in the key, or enforce uniqueness in the application|
|Manual partition management|Missing future partitions make inserts fail or fall into the default partition|Automate creation, for example with the pg_partman extension|
|Skewed data|One list or hash bucket is much bigger than the rest|Review the distribution and adjust the scheme|

## Partition vs Sharding
| Aspect                        | Partitioning                                               | Sharding                                                                |
| ----------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| Where the data lives          | On one database server                                     | Spread across multiple servers                                          |
| Main goal                     | Faster queries and easier maintenance                      | Scale storage and throughput beyond one machine                         |
| Scaling type                  | Does not add machines, so limited by one server's hardware | Horizontal scaling, add more servers                                    |
| Who manages it                | The database engine handles routing and pruning            | The application or a routing layer must know which shard holds the data |
| Cross-piece queries and joins | Simple, handled by the same database                       | Hard, and cross-shard transactions need distributed coordination        |
| Failure impact                | If the server fails, all partitions are gone               | A shard failing affects only its portion of the data                    |
| Complexity                    | Moderate                                                   | High, with rebalancing, routing and operational overhead                |
| Examples                      | PostgreSQL declarative partitioning, MySQL partitions      | MongoDB sharding, Citus for PostgreSQL, Vitess for MySQL, Cassandra     |