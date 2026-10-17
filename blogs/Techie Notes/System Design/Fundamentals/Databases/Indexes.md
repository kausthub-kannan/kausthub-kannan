An index is an extra data structure that the database keeps beside a table so that it can find rows quickly without reading the whole table. It works like the index at the back of a book: instead of reading every page to find a topic, you look it up in a sorted list that tells you exactly which pages to go to. Without an index on the column you are searching, the database must do a full table scan, reading every row, which takes time proportional to the table size. With an index, it finds the rows in logarithmic time, which for a table of a hundred million rows means a handful of steps instead of a hundred million.

The price is that indexes take storage space, and every INSERT, UPDATE or DELETE must also update every index on the table, which slows down writes. Indexing is therefore always a trade-off: faster reads for slower writes and more space.

## Types of Indexes
### B-Tree Indexes
The B-tree (in practice usually a B+ tree) is the default index in nearly all relational databases. It is a balanced, sorted tree. The top node points to a few child nodes covering ranges of values, those point further down, and the bottom level (the leaves) holds the indexed values together with a pointer to the row. All leaves are at the same depth, and in a B+ tree they are linked in order, so reading a range is just walking along the leaves. A tree with branches of hundreds of entries each reaches millions of rows in only three or four levels, which is why lookups are so fast.

Because the data is sorted, a B-tree supports equality (`=`), ranges (`<`, `>`, `BETWEEN`), prefix matches (`LIKE 'abc%'`), `ORDER BY` and `MIN`/`MAX`, all without extra sorting.

### Clustered vs Non-Clustered Indexes

|Aspect|Clustered index|Non-clustered (secondary) index|
|---|---|---|
|What it is|The table's rows are physically stored in the order of this index|A separate structure that points to the rows|
|How many per table|Only one, since rows can only be in one physical order|Many|
|Lookup|Leaf holds the row itself, so no extra step|Finds the entry, then follows a pointer to the row|
|Range queries on the key|Very fast, since neighbouring rows are stored together|Slower, since rows may be scattered|
|Examples|The primary key in MySQL InnoDB, clustered index in SQL Server|Any additional index|

PostgreSQL works differently: its tables are heaps and every index is a secondary index pointing to the row's location, so there is no automatically maintained clustered index. In InnoDB, secondary indexes store the primary key value and look the row up through the clustered index, which is one reason a short primary key matters there.

### Other types of Indexes
|Type|How it works|Use|
|---|---|---|
|B-tree|Sorted balanced tree|Default, equality and ranges|
|Hash|Hash of the value|Equality only, no ranges|
|GIN (inverted)|Maps values inside a column to the rows that contain them|Full-text search, arrays, JSON|
|GiST and R-tree|Tree of overlapping regions|Geographic and spatial data, nearest-neighbour searches|
|BRIN|Stores the min and max of blocks of rows|Huge tables where values follow the physical order, such as timestamps in a log table|
|Bitmap|A bit array per value|Low-cardinality columns in analytics, in Oracle and data warehouses|

## Composite, Covering, Partial and Expression Indexes
A composite index covers several columns, and the order of the columns matters, because the index is sorted by the first column, then by the second within it, and so on. It can serve queries that use a leftmost prefix of its columns, which is called the leftmost prefix rule.
```sql
CREATE INDEX idx_users_country_city ON users (country, city);

-- uses the index:      WHERE country = 'IN' AND city = 'Pune'
-- uses the index:      WHERE country = 'IN'
-- cannot use it well:  WHERE city = 'Pune'   (the leading column is missing)
```

A good rule for column order is to put equality-filtered columns first and the range or sort column last. A covering index contains all the columns a query needs, so the database can answer from the index alone, an index-only scan, without touching the table at all.

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id) INCLUDE (total);

SELECT customer_id, total FROM orders WHERE customer_id = 42;   -- served from the index
```
A partial index covers only the rows that match a condition, which makes it small and cheap. An expression index is built on a computed value.

```sql
-- only index the rows that are queried
CREATE INDEX idx_active_users_created ON users (created_at) WHERE status = 'active';

-- makes WHERE LOWER(email) = '...' fast
CREATE INDEX idx_users_lower_email ON users (LOWER(email));
```

## Indexes to be NOT used cases
|Situation|Why|Fix|
|---|---|---|
|A function on the column, such as `WHERE LOWER(email) = ...`|The index is on the raw value|Create an expression index|
|Leading wildcard, such as `LIKE '%abc'`|A sorted index cannot search by the end of a value|Use full-text or trigram search|
|Wrong column order in a composite index|Leftmost prefix is missing|Reorder the index or add another one|
|Data type mismatch|The value gets converted, which prevents using the index|Match the types|
|Low selectivity, such as an index on a true/false column|Most rows match, so a full scan is cheaper|Avoid, or use a partial index|
|Outdated statistics|The planner chooses badly|Run ANALYZE|
|Tiny table|Scanning is already fast|No index needed|

## Inverted or Reverse Indexes
A regular (forward) index goes from a row to its values. An inverted index goes the other way: it maps each term to the list of documents that contain it, the way the index at the back of a book maps a word to its pages. It is the core of every search engine and of full-text search. The list for each term is called a postings list.

Take three documents.

|Doc|Text|
|---|---|
|1|fast database|
|2|fast search engine|
|3|database search|

The inverted index built from them is as follows.

|Term|Documents|
|---|---|
|fast|1, 2|
|database|1, 3|
|search|2, 3|
|engine|2|

To answer a search for `fast AND database`, the engine looks up the two terms and intersects their lists (1, 2 and 1, 3), giving document 1, without reading any document. Before indexing, the text goes through analysis: it is split into tokens, converted to lowercase, common stop words such as "the" are optionally removed, and words are reduced to their root (stemming, so "running" becomes "run"). Results are then ranked by relevance with scoring methods such as TF-IDF or BM25, which favor documents where the term is frequent and the term itself is rare overall.

Elasticsearch, OpenSearch and Solr are built on Lucene, which keeps an inverted index in each shard, stored as immutable segments that are merged in the background. New documents become searchable after a short refresh interval, which is why search is described as near real-time.

The phrase "reverse index" is sometimes used for another thing: a reverse key index in Oracle, which reverses the bytes of the key before indexing to spread out sequential inserts, such as a rising ID, that would otherwise all land on the same index block. It reduces contention at the price of losing range scans on that column. When people discuss search, though, "reverse index" nearly always means the inverted index above.

## Index Guidelines
Index the columns used in WHERE, JOIN, ORDER BY and GROUP BY clauses, particularly foreign keys. Prefer columns with many distinct values. Design composite indexes around real query patterns, and drop unused or duplicate indexes, since each one slows writes. Check plans with `EXPLAIN ANALYZE` instead of guessing, and remember that on small tables or write-heavy tables, fewer indexes are better.