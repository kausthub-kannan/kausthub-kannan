System Design questions never have a "THE" right answer. For the same end goal there would be many approaches. The idea is to meet the requirements rather than attaining the perfect solution. The below is a high-level process steps which could be taken to address system design questions.

### Understanding the Problem
The first step is to understand what the requirements are. Often in Product/Solution proposals, the idea proposed by the client are never clear. They are vague and very basic. Hence it is of a necessity to ask questions to the client. The requirements themselves are classified into two types (which is well known in the software world).

1. Functional Requirement:
   These are the core features of the solution which "makes" the solution. Consider Youtube as an example. Showing thumbnails, streaming audio-video, Playlisting, likes etc are the functional requirements. Often clients are much clearer on this but this requires continuous prompting from the engineer to ask further in depth question such as: Should the playlists be shareable? Should the thumbnails have multiple options and be customisable even after upload? A well defined FRs form a solid based avoiding re-iterations of designs. At the end of this sub-step we know what is in-scope and what is out of scope.
   
2. Non-functional requirement:
   NFRs form the soul of system design. When designing solutions for a smaller audience; let's say 100 users or as a proof-of-concept; you are least bothered about scalability.  But let's say you see 10000 users hitting your application for seconds, that's a nightmare. Hence the need to ask for NFRs are the most imporant in establishing a design. NFPs are many in number so it's quite diffcult to start out of no where, hence the below template can be used to ask questions to the client in the process:
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