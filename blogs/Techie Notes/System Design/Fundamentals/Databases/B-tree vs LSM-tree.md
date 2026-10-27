To improve database access performance, databases use specialized data structures to organize data on disk and minimize expensive disk I/O operations. Two widely used approaches are **B-Trees** and **Log-Structured Merge-Trees (LSM-Trees)**.

The choice between them depends on the workload, particularly the balance between read-heavy and write-heavy operations.

## B-Tree
B-Trees are a well-established data structure used by many relational databases, including MySQL and PostgreSQL, for indexes. They maintain data in a balanced, ordered tree structure, allowing efficient searches/reads.

Each node contains sorted keys and pointers to child nodes. Starting from the root, the database compares the search key with the keys in the current node and follows the appropriate pointer until it reaches the target data.

B-Trees are well suited for **OLTP (Online Transaction Processing)** workloads that require frequent point lookups and range queries. Their balanced structure keeps the number of tree levels relatively small, enabling efficient reads.

However, writes can be expensive. Inserting, updating, or deleting entries may require modifying existing pages, splitting nodes, updating pointers, or rebalancing the tree. These operations can result in random disk I/O and additional write overhead.
### Read
The search key is compared against the keys in the root node. If it is smaller than a key, the pointer to that key’s left child is followed. If it is larger than all keys, the rightmost pointer is followed. This repeats down the tree until the key is found or a leaf is reached. Because nodes hold many sorted keys, each step is a binary search within the node. The tree height is O(log n), so a lookup costs O(log n).
### Write
The read process finds the node where the value belongs. If the node has space, the value is inserted in sorted position. If the node has no space (**overflow**), its median key is found and promoted to the parent, and the node splits into two nodes around that median. If the parent overflows too, the split repeats upward.
### Deletion
The read process finds the key, and it is removed from the node. If the node falls below the minimum key count (**underflow**), it borrows a key from a sibling through the parent. If the sibling has no spare keys either, the two nodes merge, and the parent key that separated them is demoted into the merged node. This can cascade upward.

**Note**:
In case of update there are two possibilities. If the key value (which determines the sort) is not being updated then the simple read operation id done and the non-key value is updated. In case of updating the key itself (such as an ID), deletion is done followed by fresh write/insert.
## LSM-Tree
LSM-Trees are widely used in write-intensive storage engines and databases, including Apache Cassandra and RocksDB. Instead of immediately updating an on-disk tree for every write, they accumulate writes in memory and periodically flush them to disk.

When a write arrives, it is typically recorded in a **write-ahead log (WAL)** for durability and inserted into an in-memory structure called a **MemTable**. When the MemTable reaches a configured threshold, its contents are flushed to disk as an immutable, sorted file, commonly called an SSTable (Sorted String Table).

This approach converts many small, potentially random writes into larger, sequential disk writes, improving write throughput.

However, reads can be more expensive because the requested data may exist in the MemTable, the most recent SSTables, or older SSTables. The database may need to check multiple locations before finding the correct value.
### Read
The key is first looked up in the memtable (and any immutable memtables waiting to be flushed). If it is found there, that value is returned. Otherwise the SSTables are searched from newest to oldest. For each one, its Bloom filter is checked first. A “definitely not present” answer skips the file without any disk access. A “possibly present” answer sends the lookup through the file’s sparse index to the right block, which is read and searched. The first match is the latest version, so the search stops there. A false positive costs one wasted block read. Level 0 files may overlap and must all be checked, while each deeper level needs at most one file.
### Write
The write is first appended to the write-ahead log (WAL) for crash safety and then inserted into the memtable, a sorted in-memory structure. No existing data is modified, so an update is just a newer version of the key. When the memtable reaches its size limit, it becomes immutable and is flushed to disk as a new SSTable at Level 0. Its Bloom filter and index are built during the flush. In the background, **compaction** merges SSTables into larger sorted files at deeper levels, discarding overwritten versions and building a fresh Bloom filter for each new file.
### Deletion
A delete is a normal write that records a **tombstone** for the key. A read that meets the tombstone stops and reports the key as not found, even if older SSTables still hold the value. Bloom filters cannot remove entries, so the key stays in the filters of the old files and in the filter of the file holding the tombstone. Space is reclaimed only during compaction. When the merge reaches the bottom level, where no older data can remain below, both the tombstone and the values it shadowed are dropped, and the new files get fresh Bloom filters without that key.

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