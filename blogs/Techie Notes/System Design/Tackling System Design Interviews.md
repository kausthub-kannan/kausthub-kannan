System Design questions never have a "THE" right answer. For the same end goal there would be many approaches. The idea is to meet the requirements rather than attaining the perfect solution. The below is a high-level process steps which could be taken to address system design questions.

### Understanding the Problem
The first step is to understand what the requirements are. Often in Product/Solution proposals, the idea proposed by the client are never clear. They are vague and very basic. Hence it is of a necessity to ask questions to the client. The requirements themselves are classified into two types (which is well known in the software world).

1. Functional Requirement:
   These are the core features of the solution which "makes" the solution. Consider Youtube as an example. Showing thumbnails, streaming audio-video, Playlisting, likes etc are the functional requirements. Often clients are much clearer on this but this requires continuous prompting from the engineer to ask further in depth question such as: Should the playlists be shareable? Should the thumbnails have multiple options and be customisable even after upload? A well defined FRs form a solid based avoiding re-iterations of designs. At the end of this sub-step we know what is in-scope and what is out of scope.
   
2. Non-functional requirement:
   NFRs form the soul of system design. When designing solutions for a smaller audience; let's say 100 users or as a proof-of-concept; you are least bothered about scalability.  But let's say you see 10000 users hitting your application for seconds, that's a nightmare. Hence the need to ask for NFRs are the most important in establishing a design. NFPs are many in number so it's quite difficult to start out of no where, hence the below template can be used to ask questions to the client in the process:
   - Scale - The number of users/request per unit time
   - Read vs Write - Do users read a lot of data on larger basis via your application OR do they write a lot?
   - Availability vs Consistency - What is worse, stale data or higher down time?
   - Latency vs Consistency -  What is important, uniformity and latest data or speed of deliverance?
   - Durability - What's the cost of data loss and lost time? (determine the level of durability based on this)
   - Retention - How long do you prefer to save data?
   
   Some solutions are domain specific - Let's say your creating AI Agent Solution to simulate decisions of leadership explaining, in such a case Security of the data matters a lot as it belongs to the Organisation, then security get included in the set of questions. 
   
   Often NFRs are not given straight forward. Numbers might be thrown too. For example, let's say you application gets 100M users per month (100/month) that ~50/s for write operation, that's not write heavy but the read requests are 400-1000/s, that's read heavy. This same strategy is used with others. Hence here are some numbers to remember:
   - 1 day ≈ **100,000 seconds** (really 86,400, but 100k is close enough)
   - 1 month ≈ **2.5 million seconds**
   - 1 char ≈ 1 byte; 1 KB = 1,000 bytes, 1 MB = 1,000 KB, 1 GB = 1,000 MB, 1 TB = 1,000 GB
   
   Example:
   Assumptions: 50M daily active users, 5 video views per user per day, 1 upload per 1,000 users per day, average video 300 MB, 5 minutes long.

| Estimate                   | Calculation                    | Result                                                                  |
| -------------------------- | ------------------------------ | ----------------------------------------------------------------------- |
| Views per second (read)    | 50M x 5 = 250M/day / 100k      | about 2,500/s (peak about 7,500/s)                                      |
| Uploads per second (write) | 50k/day / 100k                 | about 0.5/s                                                             |
| Read : write ratio         | 2,500 : 0.5                    | about 5,000 : 1, extremely read heavy                                   |
| New storage per day        | 50k x 300 MB                   | about 15 TB/day, about 5.5 PB/year                                      |
| Metadata size              | 1 KB per video x 50k/day x 365 | about 18 GB/year, fits a single database comfortably                    |
| Concurrent streams         | 2,500 starts/s x 300 s         | about 750k streams at once                                              |
| Egress bandwidth           | 750k x 2.5 Mbps                | about 1.9 Tbps, which no origin server can serve, so a CDN is mandatory |

### High-Level Design (Top-Down)
With requirements settled, design the solution top-down. Jumping into database design, replication or disaster recovery at step zero is premature, so start with the high-level design (HLD): the core, basic components and how a request moves through them. Keep it a conversation: when something is uncertain, ask and establish clarity before drawing.

HLD is deliberately shallow. You name the boxes (servers, a database without its type yet, caches, CDN, queues) and the arrows between them. You do not choose technologies or tune anything yet.

#### The HLD sequence
1. **Core entities.** List the nouns the system stores and moves around.
2. **API design.** Define the contract per functional requirement, starting from what the client calls. Template followed is:
```
<METHOD> /<resource>[/{id}[/<sub-resource>]] Auth: required / public Input: params, body Output: fields Pagination: cursor (for lists) Idempotent: yes / no Errors: 4xx / 5xx cases
```
3. **Core components.** Place the minimum boxes needed to satisfy the APIs.
4. **End-to-end flows.** Trace one request per FR from client to storage and back.
5. **Check against NFRs.** Does the read path survive the estimated load? Is any box a single point of failure?
6. **Pick deep-dive targets.** Mark the 2 or 3 spots where the NFRs bite hardest.

|Component|Role in the design|Why it is here|
|---|---|---|
|Client (web, mobile)|Calls APIs, plays video|Entry point|
|DNS|Maps the domain to the load balancer or nearest region|Routing|
|CDN|Serves video segments and thumbnails from edge locations|The estimate showed about 1.9 Tbps of egress|
|Load balancer / API gateway|Spreads requests, terminates TLS, authenticates, rate limits|Removes a single entry point|
|App servers (stateless)|Business logic for the APIs|Stateless, so any copy can serve any request and copies can be added freely|
|Database|Stores metadata: users, videos, comments, likes (type decided in the deep dive)|Source of truth for small, structured data|
|Blob / object storage|Stores raw and transcoded video files|Huge files do not belong in a database|
|Cache|Holds hot metadata and counters in memory|Reads are about 5,000 times more frequent than writes|
|Message queue|Hands uploaded videos to background workers|Decouples upload from slow processing|
|Transcoding workers|Convert each upload into several resolutions and formats|CPU heavy, so run asynchronously|
|Search index|Serves text search|Databases are poor at full-text search at scale|

### Deep Dive
Now dive into the details of the targets you marked in the HLD. What type of database? Scale vertically or horizontally? How is reliability set up? What recovery is needed, and how long is data kept? The NFRs drive every answer, so for each decision state the requirement, the options, the choice and the trade-off.

**Steps**
1. Restate the NFR that forces the decision (for example: 5,000:1 read to write).
2. List 2 or 3 realistic options.
3. Choose one and give the reason in a sentence.
4. Name what you give up. A choice without a stated cost is not a design decision.

Pattern followed for this is:
```
1. Requirement: <the NFR or number that forces this> 
2. Options: A, B, (C) 
3. Choice: <one>, because <one sentence> 
4. Cost: <what we give up>
```
### Wrapping Up
Finally summarise the entire design. Establish the bottlenecks and improvements. Dive surface level into monitoring, observeability , and failure scenarios.

### EXAMPLE
![URL Shortner](../../assets/excalidraw/System Design/URL Shortner.excalidraw)
Design a URL shortener where users paste a long URL and receive a unique short URL. Visiting the short URL redirects to the original (primary) URL.
#### Requirement Analysis
**FRs:**
1. Every long URL submitted produces a unique short URL.
2. Every read of a short URL redirects to the original URL.
3. Analytics (secondary, but part of the scope).

**Clarifying questions**

| Question                            | Decision                                                                                                                                                                                                               |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Do we need authentication?          | No. It is overkill for this use case. If the client insists, it can be handled at the API gateway.                                                                                                                     |
| Do we need analytics?               | Yes, but not as a core requirement. It helps us understand user scale and demographics and predict scaling needs. For the current scope we track a small set of basic metrics (e.g. click count, timestamp, referrer). |
| How many links are created per day? | Assume 5M-10M requests per day, with every request treated as a fresh user since there is no auth or session management.                                                                                               |

**NFRs:**
- **Write throughput:** 1K-6k writes/sec (see the note below on this number).
- **Read throughput:** about 100x writes, so roughly 100K-600K reads/sec.
- **Read-heavy system:** short links are created to be shared, so reads dominate.
- **Low redirect latency:** the redirect is the hot path.
#### High Level Design (HLD)
**Components:** API Gateway → Application Server → Cache → Database
Given the read RPS, a cache sits in front of the database to reduce DB hits.

#### API 1: Generate short URL
```
POST /api/v1/generate
Auth: Public

Request body (JSON):
{
  "url": "<original URL to be shortened>"
}

Response (JSON), Status: 201 Created
{
  "responseId": "<unique id for the response>",
  "shortUrl": "<unique generated short URL>"
}
```
#### API 2: Redirect to original URL
```
GET /{shortUrl}
Auth: Public

Param:
  shortUrl: the short URL generated earlier

Response:
  Status: 302 Found
  Header: Location: <original URL>
```
> We use **302 over 301** because analytics is enabled. A 301 is cached by browsers, so repeat clicks would never reach our server.
  
**Flow:**
**Write path**
1. The user calls `/api/v1/generate` with the URL to shorten.
2. The server generates a unique ID and stores it in the database along with the original URL.
3. The server returns the short URL.

**Read path**
1. The user hits the short URL.
2. The server checks the cache first.
3. On a cache miss, it looks up the database (and populates the cache).
4. The server returns a 302 redirect to the original URL.

#### Deep Dive
**Short URL Generation**
Quick correction on the name: it’s **Base62**, not 62-bit. It means 62 _symbols_ (`0-9`, `a-z`, `A-Z`), so each character carries log₂(62) ≈ 5.95 bits. At 500M users, 6-7 length would be enough. We take unique ID and generate the code (short url).

We get the ID from Range allocation (Redis) where each app server leases a block (e.g. 1M IDs) and hands them out locally. Coordination happens once per million writes, not per write. 

**Database**
SQL based approach could be taken with sharding in picture. SQL would be much easier to be integrated given that our data is structured. A single table is enough to meet the requirements of below schema:
```
urls
-----
short_code   PK (shard key)
long_url
created_at
expires_at   (nullable)
```

**Sharding**
Storage is the driver: ~90-450 TB over 5 years does not fit on one node (see the earlier estimate). Throughput and storage forces the need for sharding. 

1. How do we shard?
   To preserve high carnality we take short-code/short-url. 

2. Partitioning strategy?
   Hashing would be right approach but on `mod N` might cause problem when we auto-scale servers (number of servers/nodes change) or a server fails. This forces keys to be distributed causing misses. Hence Consistent hashing would be better. 

**Analytics Pipeline**
This is the last functional requirement encountered at the beginning. For analytics pipeline the key aspect is the asynchronous nature. When a click or search of new URL is done we do not want the user to wait due latency caused by processing analytics for the click. Hence we would require a queue. Assuming we take Kafka, we push stats data such as click timestamp, number of click and others to the Kafka queue. Later via a consumer we write it to data house (like ClickHouse) in the background. Via the stats API we obtain the analytics. 

In the user click flow all what happens is a single push to Kafka, that's it; immediately user gets the redirection with no wait time for the analytics to be processed. In the background we have the consumer taking care of data push to data house.

Further deep dive could be done upon:
1. Cleaning up after URL has expired (via background cleaners and read time checks)
2. Security when it comes to the short-code generation
3. Stopping abuse via rate-limiting the API