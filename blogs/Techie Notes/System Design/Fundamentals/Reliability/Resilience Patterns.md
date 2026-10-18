Distributed systems fail partially and unpredictably: a dependency gets slow, a node dies, a queue backs up. These patterns keep a local failure from turning into a system-wide outage. They work best **together**, and each one has a specific failure it guards against.

## Resilience Patterns
|Pattern|Failure it guards against|Core idea|
|---|---|---|
|Timeouts|A call that hangs forever, holding threads and connections|Bound how long you wait|
|Retries|Transient errors (blips, brief overload)|Try again, carefully|
|Circuit breaker|A dependency that is persistently failing|Stop calling it for a while|
|Bulkhead|One slow dependency eating all shared resources|Isolate resource pools|
|Back-pressure|Producers overwhelming consumers|Push the "slow down" signal upstream|
|Graceful degradation|Total outage when one feature breaks|Serve a reduced but useful response|
|Health checks|Routing traffic to broken instances|Detect and remove unhealthy nodes|

```
Request
  └─ Timeout           (bound each call)
      └─ Retry         (recover from transient failures)
          └─ Circuit breaker   (stop hammering a dead dependency)
              └─ Bulkhead      (contain the blast radius)
                  └─ Fallback / graceful degradation   (still give the user something)
```

## TImeouts
### Timeouts
**Every network call needs a timeout.** Without one, a slow dependency makes callers wait indefinitely, threads and connections pile up, and the caller fails too. Many client libraries default to no timeout or a very long one, so set it explicitly.

### Types of Timeouts
|Timeout|What it bounds|
|---|---|
|Connect timeout|Time to establish the TCP/TLS connection|
|Read / response timeout|Time waiting for data after the request is sent|
|Write timeout|Time to send the request|
|Overall / request timeout|Total time for the whole operation, including retries|
|Idle timeout|How long an unused connection stays open|

### Choosing Values
- Base it on the dependency's observed latency, for example **p99 or p99.9 plus headroom**, not on guesswork.
- Keep connect timeouts short (hundreds of milliseconds to a few seconds). A failed connect is usually a hard failure.
- Make sure timeouts shrink as you go down the call chain. If service A waits 2s for B, B must not wait 5s for C, or B keeps working on a request A has already abandoned.

### Deadline Propagation
Instead of each hop picking its own timeout, pass a **deadline** (an absolute time or remaining budget) with the request. Each service computes how much time is left and gives up if the budget is spent. gRPC supports this natively; with HTTP you can pass a header such as `X-Request-Deadline`.

```
Client budget: 1000 ms
  Gateway        uses 50 ms   -> passes 950 ms remaining
    Service A    uses 200 ms  -> passes 750 ms remaining
      Service B  must answer within 750 ms or abort
```

## Retries
Retries recover from **transient** failures: dropped packets, a node restarting, brief throttling. They are dangerous when used carelessly.

|Retry|Don't retry|
|---|---|
|Network errors, connection resets|4xx client errors (400, 401, 403, 404, 422)|
|Timeouts (with care)|Business-logic failures|
|502, 503, 504|Anything not safe to repeat (see idempotency)|
|429 (honouring `Retry-After`)|Errors the dependency says are permanent|

### Exponential backoff with jitter
Waiting longer between attempts gives the dependency time to recover. **Jitter** (randomness) stops all clients from retrying at the same instant.

Common jitter strategies:
- **No jitter:** `base * 2^attempt`. This causes synchronized retry waves.
- **Full jitter:** `random(0, base * 2^attempt)`. A solid default.
- **Equal jitter:** half fixed, half random.
- **Decorrelated jitter:** each wait is based on the previous wait. Spreads load well.

### Idempotency
A retry may execute an operation twice (the first attempt succeeded but the response was lost). Operations that change state must be **idempotent**, typically via an **idempotency key** sent by the client and stored by the server. The server stores the result under that key and returns the same result for repeats.

### Retry budgets and storms
Suppose each of 3 layers retries 3 times. One failing request at the bottom becomes `3 x 3 x 3 = 27` requests. During an outage this **retry amplification** can crush a dependency that is trying to recover.

Mitigations:
- **Retry at one layer only**, usually the one closest to the user or the edge. Lower layers fail fast.
- **Retry budget:** cap retries to a percentage of normal traffic (for example, 10 percent of requests may be retries). Envoy and Finagle support this.
- **Token bucket:** each success adds tokens, each retry spends one. When the bucket is empty, stop retrying.
- Always put an **overall deadline** on the whole retry sequence.

### Hedged requests
For latency-sensitive reads, send a second request to another replica if the first hasn't answered after, say, the p95 latency. Use the first response and cancel the other. It reduces tail latency at the cost of some extra load. Only use it for idempotent, read-only calls.

## Circuit breakers
A circuit breaker wraps calls to a dependency and **stops calling it when it is clearly failing**. This avoids wasting resources on doomed calls, gives the dependency room to recover, and lets callers fail fast.

### States
```
          failures exceed threshold
   ┌──────────────────────────────────┐
   │                                  ▼
CLOSED                              OPEN
(normal, calls pass through)        (calls rejected immediately)
   ▲                                  │
   │ trial calls succeed              │ after cool-down timeout
   │                                  ▼
   └──────────────────────────── HALF-OPEN
                                  (limited trial calls)
                                  │
                                  └─ trial fails -> back to OPEN
```

| State         | Behaviour                                                                                            |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| **Closed**    | Requests flow normally. Failures are counted.                                                        |
| **Open**      | Requests fail immediately (or go to a fallback) without touching the dependency.                     |
| **Half-open** | After a cool-down, a few trial requests are allowed. Success closes the circuit, failure reopens it. |

### Key configuration
|Setting|Meaning|Typical thinking|
|---|---|---|
|Failure rate threshold|Percent of failed calls that trips the breaker|50 percent over a window is common|
|Minimum call volume|Don't evaluate until at least N calls in the window|Avoids tripping on 1 of 2 failed calls|
|Sliding window|Count-based (last N calls) or time-based (last N seconds)|Time-based suits variable traffic|
|Slow-call threshold|Treat calls slower than X as failures|Catches degradation, not just errors|
|Open-state wait time|How long to stay open before half-open|Seconds to tens of seconds|
|Half-open permitted calls|Number of trial calls|A small number, such as 3 to 10|

## Bulkheads
Named after ship bulkheads: watertight compartments so one breach doesn't sink the whole vessel. In software, **isolate resources so a problem in one area can't exhaust everything**.

**The problem it solves:** a service calls dependencies A, B and C from one shared thread pool. A becomes slow, its calls hold threads, the pool drains, and now calls to the healthy B and C can't get a thread either. One slow dependency has taken down the whole service.

|Form|How it isolates|
|---|---|
|**Thread-pool bulkhead**|Separate thread pool per dependency or feature. Strong isolation, with some overhead.|
|**Semaphore bulkhead**|Limit concurrent calls with a counter. Lightweight, but the caller's thread still blocks.|
|**Connection-pool isolation**|Separate connection pools per downstream service or per tenant.|
|**Process or container isolation**|Run critical and non-critical workloads in different processes, pods or nodes.|
|**Queue isolation**|Separate queues or consumer groups for different workloads.|
|**Tenant / customer isolation**|Quotas or cells per tenant so a noisy tenant can't starve others.|
|**Cell-based architecture**|The whole system is split into independent cells, each serving a subset of users. A failure affects one cell only.|
|**Availability-zone / region isolation**|Failure domains at the infrastructure level.|

### Sizing
- Use **Little's Law**: `concurrency ≈ throughput x latency`. If you expect 100 req/s to a dependency with 200ms average latency, you need about 20 concurrent slots. Add headroom for p99.
- Keep the wait time short or zero. A bulkhead that queues requests for seconds just moves the problem.
- Reserve capacity for **critical paths** (checkout, login) separately from nice-to-haves (recommendations, analytics).
- Bulkheads **reject** excess load quickly. That is the point, and rejections should be handled by a fallback or a clear error such as 503.
- Pair with circuit breakers: the bulkhead limits how much damage a slow dependency can do, and the breaker stops calling it altogether once it is clearly failing.
- Monitor pool utilisation, queue depth and rejection counts.

## Back Pressure
Back-pressure is how a **slow consumer tells a fast producer to slow down**, rather than silently accumulating work until it runs out of memory or latency explodes.

Without it, the usual outcomes are unbounded queues, growing latency (all work is stale by the time it is handled), out-of-memory crashes, and cascading failure.

### Strategies
|Strategy|Description|Trade-off|
|---|---|---|
|**Bounded queues**|Fixed-size buffer. When full, block or reject the producer.|Simple and effective. Choose block vs reject deliberately.|
|**Load shedding**|Deliberately drop excess requests (return 503 or 429) once capacity is exceeded.|Protects the service. Some users get errors.|
|**Rate limiting**|Cap the request rate per client, tenant or API key (token bucket, leaky bucket, sliding window).|Protects against abuse and noisy neighbours.|
|**Adaptive concurrency limits**|Dynamically adjust the allowed in-flight requests based on observed latency (like TCP congestion control, for example Netflix's concurrency-limits).|Self-tuning, but more complex.|
|**Pull-based consumption**|Consumers request work at their own pace (Kafka consumers, SQS polling).|Natural back-pressure. Lag builds in the broker instead.|
|**Reactive streams**|Consumers signal demand explicitly (`request(n)`), as in Reactor, RxJava and Akka Streams.|Built into the protocol. Requires the whole pipeline to be reactive.|
|**Flow control in protocols**|TCP windowing, HTTP/2 flow control, gRPC streaming.|Free, but only at the transport layer.|
|**Drop / sample / coalesce**|For telemetry or UI events, drop old or duplicate items.|Fine when data loss is acceptable.|

### Load Shedding
- Decide **what to drop**: lowest priority first (background jobs, anonymous traffic) and protect critical traffic.
- Shed **early and cheaply**, at the edge or at the front of the request path, before spending resources.
- Return a meaningful response: `503 Service Unavailable` or `429 Too Many Requests` with a `Retry-After` header so clients back off.
- **LIFO or "newest first"** queue handling during overload can help, because old requests have probably already timed out on the client side.
- Use CPU, queue depth or latency as the shedding signal, not just request count.

### Rate limiting algorithms
|Algorithm|Behaviour|
|---|---|
|Fixed window|Simple counter per time window. Allows bursts at window edges.|
|Sliding window|Smoother, more accurate, more memory.|
|Token bucket|Allows controlled bursts, refilling at a steady rate. Very common.|
|Leaky bucket|Smooths output to a constant rate.|

## Graceful degradation
When something breaks, **keep serving a reduced but useful experience** instead of failing completely. It requires deciding in advance which features are essential and which are optional.

|Technique|Example|
|---|---|
|**Serve cached or stale data**|Show the last known product list if the catalogue service is down. Use `stale-while-revalidate` or `stale-if-error`.|
|**Default / static fallback**|Show generic recommendations or "popular items" instead of personalised ones.|
|**Disable non-critical features**|Turn off reviews, recommendations or live chat so checkout still works.|
|**Feature flags / kill switches**|Switch off expensive or failing features at runtime without a deploy.|
|**Read-only mode**|If the primary database is unavailable, allow browsing but block writes, with a clear message.|
|**Reduce quality**|Lower image resolution, skip personalisation, shorten result lists, lower search precision.|
|**Async fallback**|Accept the request, queue it, and complete it later ("we'll email you when it's done").|
|**Partial responses**|Return the sections that worked and mark the failed ones as unavailable.|
|**Priority tiers**|Under load, serve paying or critical users first.|

### Designing
1. **Classify dependencies:** _critical_ (can't work without it) vs _non-critical_ (nice to have). Authentication and payment are critical, while recommendations are not.
2. **Define the fallback for each non-critical dependency** before an incident, and test it.
3. **Make failure visible to the user** where it matters ("Recommendations are temporarily unavailable") rather than showing a blank section or a spinner.
4. **Avoid hidden data corruption.** A fallback that returns wrong data (for example a stale price at checkout) can be worse than an error. Know where staleness is acceptable.
5. **Keep fallbacks simple and independent.** A fallback that calls another remote service has its own failure modes. Prefer local cache or static defaults.

## Health Checks
Health checks let infrastructure (load balancers, orchestrators, service discovery) **detect unhealthy instances and stop sending traffic to them**, or restart them.

### Types
|Check|Question it answers|Action on failure|
|---|---|---|
|**Liveness**|"Is the process alive and not stuck?"|Restart the instance|
|**Readiness**|"Can this instance serve traffic right now?"|Remove from load balancing, don't restart|
|**Startup**|"Has the app finished starting?"|Delay other probes, restart if it never starts|

### Shallow vs deep checks

|                | Shallow                                         | Deep                                                                                                      |
| -------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| What it checks | Process responds (`200 OK`)                     | Dependencies too (database, cache, downstream services)                                                   |
| Speed          | Fast, cheap                                     | Slower, more load                                                                                         |
| Risk           | May report healthy while unable to do real work | **Can cause cascading failure** if a shared dependency blips and every instance reports unhealthy at once |

### Guidance
- **Liveness should be shallow.** It should only reflect whether the process itself is stuck. If liveness checks the database and the database goes down, every instance gets restarted for no benefit.
- **Readiness can include critical local dependencies** (can this instance reach its own database connection pool?), but be careful with shared downstream dependencies. If all instances fail readiness together, the load balancer has nowhere to send traffic. Many load balancers have a "panic mode" that ignores health when too many hosts are unhealthy, so know how yours behaves.
- Keep health endpoints **fast, cheap and without side effects**, with their own timeouts.
- Don't make health checks depend on the same thread pool as real traffic. A saturated pool will fail the check and trigger restarts, which makes overload worse.

### Related mechanisms
- **Passive health checking / outlier detection:** the load balancer or mesh watches real traffic and ejects instances with high error rates or latency (Envoy outlier detection).
- **Graceful shutdown:** on SIGTERM, fail readiness first, finish in-flight requests, then exit. Combine with a `preStop` delay so the load balancer has time to stop sending traffic.
- **Connection draining:** keep serving existing connections for a short time while removing the instance from rotation.
- **Heartbeats and leases:** nodes report in periodically and are considered dead if they stop (used in cluster membership, leader election).
- **Synthetic monitoring / canaries:** external probes that exercise real user flows end to end.

## All together in action
```
incoming request
   │
   ├─ rate limiter / load shedder     (back-pressure: reject excess early)
   │
   ├─ bulkhead                        (limit concurrent calls to this dependency)
   │     │
   │     ├─ circuit breaker           (fail fast if the dependency is known bad)
   │     │     │
   │     │     ├─ retry w/ backoff + jitter, under a retry budget
   │     │     │     │
   │     │     │     └─ call with timeout / propagated deadline
   │     │     │
   │     │     └─ on failure -> fallback
   │     │
   │     └─ on rejection -> fallback
   │
   └─ graceful degradation            (return the best response possible)

infrastructure: health checks route traffic away from broken instances
```