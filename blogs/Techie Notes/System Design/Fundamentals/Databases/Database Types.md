A database is a system for storing data so that it can be found and changed quickly and safely. For decades the standard answer was the relational database, which stores data in tables and is queried with SQL. As applications grew to serve millions of users, handle huge volumes of data and store data that does not fit neatly into tables, new kinds of databases appeared, grouped together under the name NoSQL. Today the question is not which type is best, but which type fits the shape of the data and the way it will be used.

## SQL
A relational database stores data in tables made of rows and columns. Every table has a fixed schema, which defines the columns and their types in advance. Tables are linked through keys: a column in one table refers to the primary key of another, which lets the database join them. Examples are PostgreSQL, MySQL, Oracle, SQL Server and SQLite.

The strengths of SQL databases are that they provide ACID transactions, so data stays exact and safe, that the schema enforces structure and rules, that joins and complex queries are powerful and flexible, and that SQL is a mature, standard language with a huge ecosystem. Data is normally normalized, meaning each fact is stored once, which avoids duplication and inconsistency.

The weaknesses are that the fixed schema makes changes slower and more rigid, that joins across very large tables get expensive, and that scaling beyond one server takes more effort. SQL databases scale up easily and scale out for reads using replicas, but scaling writes across many servers needs sharding, which is complex, as in the partitioning and replication notes. Note that this is a matter of effort, not impossibility, and large systems do run on sharded SQL databases.

## NoSQL
NoSQL, often read as "not only SQL", is a broad name for databases that do not use the traditional table-and-join model. They were designed for horizontal scaling across many cheap servers, flexible or no fixed schema, and very high speed or volume for particular access patterns. Many follow the BASE approach from the ACID vs BASE notes, favoring availability and eventual consistency, although this varies and several now offer transactions as well. NoSQL is not a single technology. It is four main families, each with a different data model, plus some specialized kinds.

## SQL vs NoSQL
|Aspect|SQL (relational)|NoSQL|
|---|---|---|
|Data model|Tables with rows and columns|Key-value, documents, wide columns or graphs|
|Schema|Fixed, defined in advance|Flexible, often schema-less, or defined per query|
|Relationships|Joins across tables|Mostly embedded or duplicated data, few or no joins (except graph databases)|
|Query language|SQL, standard|Varies by database|
|Transactions|Strong ACID|Varies, often BASE, some now support transactions|
|Consistency|Strong|Often eventual, and often tunable|
|Scaling|Vertical first, reads scaled with replicas, writes need sharding|Designed to scale out horizontally|
|Data duplication|Avoided, through normalization|Accepted, to make reads fast|
|Best for|Structured data with relationships, where correctness matters|Huge scale, flexible data, specific access patterns|
|Examples|PostgreSQL, MySQL, Oracle|Redis, MongoDB, Cassandra, Neo4j|


## Types of NoSQL
### Key-Value Stores
The simplest model: the database is a large dictionary where each unique key maps to a value, and the value is opaque to the database. You can get, set and delete by key, and that is nearly all, which is exactly why it is so fast. Examples are Redis, Memcached and Amazon DynamoDB, which also supports a document-like structure.

|Strengths|Weaknesses|
|---|---|
|Extremely fast lookups, often in memory|Only lookup by key, no complex queries or joins|
|Simple, scales out easily by splitting keys across servers|Value has no structure the database can search inside|
|Supports expiry (TTL) for temporary data|Memory is expensive for large datasets|

Typical uses are caching, user sessions, shopping carts, rate-limit counters, leaderboards and feature flags, as in the caching notes.

### Document DB
Data is stored as documents, usually JSON (or BSON), where each document holds a complete record, including nested objects and lists. Documents in the same collection do not need to have the same fields. The database understands the structure, so it can index and query fields inside the document. Examples are MongoDB, CouchDB and Firestore.

The whole order, with its customer and items, is one document, so it can be read in one go without joining tables. In a SQL design, the same information would be spread over several tables.

|Strengths|Weaknesses|
|---|---|
|Flexible schema, easy to change and evolve|Data duplication, since related data is embedded in many documents|
|A whole object is stored and read together, so no joins|Joins across collections are limited and slower|
|Maps naturally to objects in application code|Keeping duplicated data consistent is up to the application|
|Rich queries and indexes on fields|Weaker for data with many relationships|

Typical uses are content management, product catalogs, user profiles, mobile and web app backends and any data whose shape varies.

### Wide Column Stores
Data is organized into tables with rows and columns, but unlike a relational table, each row can have different columns, and data is grouped and physically stored by a partition key, which determines which server holds the row. They are built for enormous scale, very high write throughput and spreading across several data centers, and they are usually leaderless and eventually consistent with tunable consistency, as in the replication notes. Examples are Apache Cassandra, ScyllaDB, HBase and Google Bigtable.

The key design rule is to model the table around the query, not around the entities. There are no joins, so a separate table is usually created for each way in which the data will be read.

|Strengths|Weaknesses|
|---|---|
|Massive write throughput and linear scaling|No joins, and limited ad hoc queries|
|Highly available, works across regions|Must design tables around known queries up front|
|No single point of failure|Eventual consistency, so careful design is needed|
|Efficient for time-ordered data|Operationally complex|

Typical uses are messaging and activity feeds, time-series and sensor data, event logs, recommendation data and anything with huge, write-heavy workloads.

### Graph DB
Data is stored as nodes (things, such as people or products) and edges, also called relationships (connections between things, such as "follows" or "bought"), and both can hold properties. Relationships are stored as first-class data, so following them is fast, even many hops deep, where a relational database would need many costly joins. Examples are Neo4j and Amazon Neptune.

|Strengths|Weaknesses|
|---|---|
|Very fast for deeply connected data and traversals|Not suited to simple bulk data or heavy aggregation|
|Natural model for networks of relationships|Harder to scale horizontally than other NoSQL types|
|Queries about connections are short and readable|Smaller ecosystem, and a different query language to learn|

Typical uses are social networks, recommendation engines, fraud detection (finding rings of linked accounts), knowledge graphs and network or route analysis.

### Few Other types
|Type|What it is for|Examples|
|---|---|---|
|Time-series|Data points ordered by time, such as metrics and sensor readings, with fast writes and time-range queries|InfluxDB, TimescaleDB, Prometheus|
|Search engine|Full-text search, filtering and ranking over large text data|Elasticsearch, OpenSearch|
|Vector|Storing and searching embeddings, for similarity search and AI applications|Pinecone, pgvector, Milvus|
|Columnar analytics (data warehouse)|Fast analysis over huge tables by storing data by column|BigQuery, Snowflake, Redshift|
|NewSQL|SQL and ACID transactions combined with horizontal scaling|Google Spanner, CockroachDB, TiDB|