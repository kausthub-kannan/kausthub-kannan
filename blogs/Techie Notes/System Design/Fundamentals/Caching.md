A simple system can fetch data from the database on every request, and the database is the permanent home of the data, so this works fine at small scale. As the number of users grows, the same data gets requested again and again, and the database becomes a bottleneck. Each query reads from disk, which is slow compared to memory, and the database can only handle a limited number of queries at once, so latency increases, response times suffer and eventually the database may fail under the load.

Caching solves this by keeping a temporary copy of frequently used data in a much faster storage layer, usually memory, so that most requests are answered without touching the database at all. The idea works because of a common access pattern: a small portion of the data is requested far more often than the rest, such as a trending product, a popular profile or the home page. Caching that hot data gives a large speed improvement for a small amount of storage, and it also protects the database from load.

## Cache Hits and Misses
When a request arrives, the system looks in the cache first. If the data is there, it is a cache hit, and the response is returned immediately. If it is not there, it is a cache miss, so the system reads the data from the database, returns it to the user and also stores a copy in the cache for next time. The proportion of requests served from the cache is the cache hit ratio, and it is the main measure of how effective a cache is. A high hit ratio means most traffic never reaches the database.

## Caching in Systems
Caching is not one single component. It appears at many layers of a system, and a single request often passes through several caches before it reaches the database.

- Browser cache: the user's own browser stores website files such as images, CSS and JavaScript, so repeat visits do not download them again.
- Forward proxy cache: a proxy in a company or ISP network stores frequently visited websites for all the users behind it.
- CDN cache: edge servers around the world store static content such as images, thumbnails, videos and scripts close to users.
- Reverse proxy or load balancer cache: a server in front of the application can store responses and serve repeated requests itself.
- Application cache (Redis, Memcached): stores dynamic data such as user profiles, sessions, computed results and frequently needed database records.
- Database cache: the database itself keeps frequently read data pages and sometimes query results in memory, so repeated queries are faster.
- DNS cache: browsers, operating systems and resolvers remember domain-to-IP answers for the length of the TTL.

## In-memory cache (Redis)
Redis is the most widely used cache. It is an in-memory data store, which means it keeps all its data in RAM instead of on disk. Memory is orders of magnitude faster than disk, so Redis can answer in well under a millisecond and handle a very large number of requests per second. It stores data as key-value pairs: the application gives a key, such as user:42:profile, and gets back the stored value, which makes lookups direct and fast. Redis also supports richer structures such as lists, sets, sorted sets and hashes, which is why it is used for things like leaderboards, session storage and rate limiting along with plain caching. Memcached is a simpler alternative that only does key-value caching.

The trade-off is that RAM is expensive and limited compared to disk, so a cache cannot hold everything and is meant to hold only the data that benefits most. Data in a cache is also treated as temporary and disposable: the database remains the source of truth, and if the cache loses its data, the system can rebuild it from the database. Redis can optionally save data to disk for persistence, but when it is used as a cache, the data is usually given an expiry time and is expected to come and go.

## Caching Strategies
The important design question is how the cache and the database interact, and there are several standard patterns.

1. **Cache-aside (or lazy loading):** Here the application controls everything. It checks the cache first, and on a miss it reads the database and then writes the result into the cache. This is the most common pattern. It only caches data that is actually requested, and if the cache fails the system still works by reading the database, but the first request for each item is slow, and the data can become stale if the database changes afterwards.

2. **Read-Through:** In read-through, the application only talks to the cache, and the cache itself is responsible for loading the data from the database on a miss. The behavior is similar to cache-aside, but the loading logic lives in the cache layer instead of the application.

3. **In Write-Through:** Here, every write goes to the cache and the database together, and the write is complete only when both are updated. The cache is therefore always consistent with the database, and reads are fast, but writes are slower because they must do two operations, and data that is written but never read wastes cache space.

4. **In write-back (or write-behind):** Here, writes go only to the cache first, and the cache saves them to the database later, in the background and often in batches. Writes are very fast and the database load is reduced, but there is a risk of losing data if the cache fails before it has been saved, so it is used where speed matters more than perfect durability.

5. **In write-around:** In write-around, writes go straight to the database and skip the cache, and data enters the cache only when it is read. This avoids filling the cache with data that is written once and rarely read, but a read right after a write will be a miss.

### Eviction Policy:
Since the cache is smaller than the database, it will eventually become full, and it must decide which entries to remove to make room. This decision is made by the eviction policy.
1. LRU (Least Recently Used) removes the item that has not been accessed for the longest time, and is the most common choice because recently used data is likely to be used again. 
2. LFU (Least Frequently Used) removes the item accessed least often, which keeps consistently popular items. 
3. FIFO (First In First Out) removes the oldest entry regardless of how often it is used, which is simple but less effective. 
4. TTL (Time To Live) gives each entry an expiry time after which it is automatically removed, which limits how stale the data can get.

## Common Problems in Caching
A cache stampede (or thundering herd) happens when a very popular entry expires, and many requests all miss at the same moment and all rush to the database to rebuild it, which can overload it. It is reduced with locks so only one request rebuilds the entry, by refreshing popular entries before they expire, or by adding random variation to expiry times.

A cache avalanche is the bigger version of this, where many entries expire at the same time, or the whole cache goes down, and a flood of traffic reaches the database. Using different TTLs, running the cache with replication and high availability, and protecting the database with rate limits all help.

Cache penetration happens when requests ask for data that does not exist, such as random or malicious IDs. These are always misses, so every one of them goes to the database. This is handled by caching the "not found" result for a short time or by placing a Bloom filter in front that quickly rejects keys that cannot exist.

### Distributed Caching
A single cache server is limited in memory and is also a single point of failure, so large systems use a distributed cache, where the data is split across many cache servers, a technique called sharding or partitioning. The client or a proxy decides which server holds a key, usually using consistent hashing, which makes sure that adding or removing a server only moves a small part of the keys and not all of them. Replicas of each shard are kept so that the cache survives a server failure, and Redis Cluster is a common example of this setup.

## Concept of Write-through and Write-back
In caching, when data is updated in the cache, the main memory or underlying database can also be updated immediately. This is called write-through caching. It priorities data consistency and durability but can increase write latency.

In write-back caching, updates are made to the cache first and propagated to the underlying storage asynchronously, prioritising lower write latency. However, if the cache fails before the updates are persisted, data may be lost.

A dirty bit identifies whether a cache entry has been modified but not yet written to the underlying storage. It helps determine which entries need to be flushed during write-back.