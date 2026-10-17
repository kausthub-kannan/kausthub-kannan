To improve database access performance, databases use specialized data structures to organize data on disk and minimize expensive disk I/O operations. Two widely used approaches are **B-Trees** and **Log-Structured Merge-Trees (LSM-Trees)**.

The choice between them depends on the workload, particularly the balance between read-heavy and write-heavy operations.

## B-Tree
B-Trees are a well-established data structure used by many relational databases, including MySQL and PostgreSQL, for indexes. They maintain data in a balanced, ordered tree structure, allowing efficient searches, insertions, and deletions.

Each node contains sorted keys and pointers to child nodes. Starting from the root, the database compares the search key with the keys in the current node and follows the appropriate pointer until it reaches the target data.

B-Trees are well suited for **OLTP (Online Transaction Processing)** workloads that require frequent point lookups, updates, and range queries. Their balanced structure keeps the number of tree levels relatively small, enabling efficient reads.

However, writes can be expensive. Inserting, updating, or deleting entries may require modifying existing pages, splitting nodes, updating pointers, or rebalancing the tree. These operations can result in random disk I/O and additional write overhead.

## LSM-Tree
LSM-Trees are widely used in write-intensive storage engines and databases, including Apache Cassandra and RocksDB. Instead of immediately updating an on-disk tree for every write, they accumulate writes in memory and periodically flush them to disk.

When a write arrives, it is typically recorded in a **write-ahead log (WAL)** for durability and inserted into an in-memory structure called a **MemTable**. When the MemTable reaches a configured threshold, its contents are flushed to disk as an immutable, sorted file, commonly called an SSTable (Sorted String Table).

This approach converts many small, potentially random writes into larger, sequential disk writes, improving write throughput.

However, reads can be more expensive because the requested data may exist in the MemTable, the most recent SSTables, or older SSTables. The database may need to check multiple locations before finding the correct value.

### Bloom Filters
Bloom filters help reduce unnecessary disk reads by probabilistically checking whether an SSTable might contain a particular key.

- If the filter says the key is **definitely absent**, the database can skip that SSTable.    
- If the filter says the key **might be present**, the database must check the SSTable because false positives are possible.

## B-Tree vs LSM Tree

|Aspect|B-tree|LSM-tree|
|---|---|---|
|Primary design goal|Efficient reads and balanced read/write performance|High write throughput|
|Write strategy|Updates existing tree pages|Buffers writes in memory and flushes sorted data to disk|
|Disk I/O pattern|Can involve random writes|Typically uses sequential writes for flushed SSTables|
|Read performance|Generally efficient, with direct tree traversal|May require checking multiple data structures or SSTables|
|Range queries|Efficient due to ordered keys and leaf traversal|Supported, but may require merging results from multiple SSTables|
|Write amplification|Can arise from page updates, splits, and storage-level behavior|Can be substantial due to repeated compaction|
|Read amplification|Usually relatively low|Can be higher when multiple SSTables must be checked|
|Space amplification|Depends on page utilization and storage overhead|Can increase due to overlapping SSTables and obsolete versions awaiting compaction|
|Optimization techniques|Page caching, tree balancing, fill-factor tuning|Bloom filters, block caches, compaction, and leveled or tiered strategies|
|Common examples|MySQL InnoDB, PostgreSQL indexes|RocksDB, LevelDB, Cassandra, HBase|

## Case Studies 

### Case Study: Banking Transaction Database (B-Trees)
Consider a banking application that processes account balance checks, transfers, and transaction queries. A customer checking their balance needs a quick lookup by account ID. A transfer may also require reading and updating multiple account records while maintaining transactional consistency.

A B-Tree-based storage engine is a strong fit for this workload because it supports efficient point lookups and updates. For example, MySQL's InnoDB engine uses B+Tree indexes for primary and secondary indexes. The database can locate an account by traversing its index rather than scanning the entire table. Frequently accessed index and data pages can also be served from memory.

**Why B-Trees fit:** The workload requires predictable read performance, efficient updates, range queries, and transactional guarantees.

Note that B-Trees alone do not guarantee transaction correctness; mechanisms such as transactions, locking, and multiversion concurrency control are also important.

### Case Study: High-Volume Event Ingestion (LSM-Tree)
Consider an application that continuously receives millions of events from IoT devices, application logs, or user activity streams. The workload is dominated by inserts, with events appended continuously and queried later for analytics or troubleshooting.

An LSM-Tree-based storage engine, such as RocksDB, can buffer incoming writes in memory and flush them to disk as sorted SSTables. This reduces the need to update existing on-disk structures for every incoming event. Bloom filters can help skip SSTables that do not contain a requested event key, while compaction consolidates data and removes obsolete versions when appropriate.

**Why LSM-Trees fit:** The workload benefits from high write throughput and can tolerate the additional read and background-compaction costs.

However, the actual performance depends on the read/write ratio, key distribution, compaction strategy, hardware, and configuration. An LSM-Tree is not automatically faster for every write-heavy workload.