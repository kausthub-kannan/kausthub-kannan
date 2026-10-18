**Observability** is the ability to understand what a system is doing internally by examining the data it emits. Monitoring tells you _that_ something is wrong, and observability helps you work out _why_, including for failures you didn't predict.

The three classic pillars are **logs**, **metrics** and **traces**. Each answers a different question, and they are most powerful when linked together.

| Logs                      | Metrics                                      | Traces                                            |                                                  |
| ------------------------- | -------------------------------------------- | ------------------------------------------------- | ------------------------------------------------ |
| **What**                  | Discrete, timestamped records of events      | Numeric measurements aggregated over time         | The path of a single request across services     |
| **Best at answering**     | "What exactly happened?"                     | "Is something wrong, and how bad?"                | "Where did the time go?" "Which service failed?" |
| **Cardinality tolerance** | High (each event is unique)                  | **Low** (every label combination is a new series) | High per trace, but usually sampled              |
| **Storage cost**          | High (volume-driven)                         | Low (pre-aggregated)                              | Medium to high (usually sampled)                 |
| **Granularity**           | Per event                                    | Per interval (for example every 15s)              | Per request                                      |
| **Typical use**           | Debugging, auditing, forensics               | Alerting, dashboards, capacity, SLOs              | Latency analysis, dependency mapping, root cause |
| **Typical tools**         | Loki, Elasticsearch, Splunk, CloudWatch Logs | Prometheus, Datadog, CloudWatch Metrics           | Jaeger, Tempo, Zipkin, X-Ray                     |

## Logs
A log is an immutable, timestamped record of something that happened. **Always prefer structured logs (JSON or key-value) over free text.** They are searchable, filterable and aggregatable without fragile regex parsing.

### Log levels
|Level|Use for|Notes|
|---|---|---|
|`TRACE` / `DEBUG`|Detailed diagnostic info|Off in production by default, enable temporarily per service|
|`INFO`|Normal significant events (startup, request completed, job finished)|Keep volume reasonable|
|`WARN`|Unexpected but handled (retry succeeded, fallback used, deprecated call)|Worth reviewing in aggregate|
|`ERROR`|An operation failed and needs attention|Should be actionable|
|`FATAL` / `CRITICAL`|The process cannot continue|Usually precedes a crash|

Rule of thumb: if an `ERROR` log never needs anyone to act on it, it should be a `WARN` or `INFO`. Too many noisy errors train people to ignore them.

## Metrics
Metrics are numeric measurements collected at regular intervals and stored as **time series**: a metric name, a set of labels (tags), and a series of `(timestamp, value)` pairs.

|Type|Behaviour|Example|
|---|---|---|
|**Counter**|Only goes up (resets on restart). Use `rate()` to get a per-second value.|Requests served, errors, bytes sent|
|**Gauge**|Goes up and down|Queue depth, memory in use, active connections, temperature|
|**Histogram**|Counts observations in buckets, allowing percentile estimates (and aggregation across instances)|Request latency, payload size|
|**Summary**|Calculates quantiles client-side|Percentiles per instance, but **cannot be aggregated** across instances|

**Prefer histograms over averages.** Averages hide tail latency: a service with 99 requests at 50ms and one at 5s has a 100ms average but a terrible p99. Always track **p50, p95, p99** (and sometimes p99.9).

### Frameworks for deciding what to measure

| Framework                        | Best for                                           | Letter / Signal | Measure                                     |
| -------------------------------- | -------------------------------------------------- | --------------- | ------------------------------------------- |
| RED method                       | Request-driven services                            | Rate            | Requests per second                         |
| RED method                       | Request-driven services                            | Errors          | Failed requests per second (or error ratio) |
| RED method                       | Request-driven services                            | Duration        | Latency distribution                        |
| USE method                       | Resources (CPU, disks, network, pools)             | Utilisation     | Percent of time or capacity in use          |
| USE method                       | Resources (CPU, disks, network, pools)             | Saturation      | Amount of queued or waiting work            |
| USE method                       | Resources (CPU, disks, network, pools)             | Errors          | Count of error events                       |
| Four Golden Signals (Google SRE) | Services overall (essentially RED plus saturation) | Latency         | How long requests take                      |
| Four Golden Signals (Google SRE) | Services overall (essentially RED plus saturation) | Traffic         | Demand on the system                        |
| Four Golden Signals (Google SRE) | Services overall (essentially RED plus saturation) | Errors          | Rate of failed requests                     |
| Four Golden Signals (Google SRE) | Services overall (essentially RED plus saturation) | Saturation      | How full the system is                      |

### Example Metrics
|Layer|Metrics|
|---|---|
|HTTP service|Request rate, error rate by status class, latency histogram by route|
|Database|Query latency, connections in use, pool wait time, replication lag, slow query count, lock waits|
|Cache|Hit ratio, evictions, memory usage, latency|
|Queue / stream|Depth, consumer lag, age of oldest message, publish and consume rate, dead-letter count|
|Runtime|GC pause time, heap usage, thread count, event loop lag, open file descriptors|
|Host / container|CPU, memory, disk I/O, network, restarts, throttling|
|Resilience|Circuit breaker state, retry count, bulkhead rejections, timeouts, fallback usage|
|Business||

### Cardinality
Every unique combination of label values creates a separate time series. High-cardinality labels cause memory blow-ups and large bills.

|Safe labels (bounded)|Dangerous labels (unbounded)|
|---|---|
|`service`, `env`, `region`|`user_id`, `email`, `session_id`|
|`method`, `status_code`|`request_id`, `trace_id`|
|`route` (the **template**, such as `/users/:id`)|Raw URL paths with IDs|
|`error_type`|Full error messages|

If you need per-user or per-request detail, that belongs in **logs or traces**, not metric labels. Estimate series count as the product of label cardinalities (`5 services x 20 routes x 5 status classes x 3 regions = 1,500 series` per metric).

### Collection models

|Model|How it works|Examples|
|---|---|---|
|**Pull**|The metrics system scrapes an endpoint (`/metrics`) on each target|Prometheus|
|**Push**|The app or agent sends metrics to a backend|StatsD, Datadog agent, OTLP exporters|

Pull makes it easy to detect a target that is down and avoids overwhelming the backend. Push suits short-lived jobs (batch, serverless), although Prometheus also offers a Pushgateway for those.

## Tracing
A trace follows **one request as it travels through many services**, showing the timing and relationships of every step.
### Core concepts

|Term|Meaning|
|---|---|
|**Trace**|The whole journey of one request, identified by a trace ID|
|**Span**|One unit of work within a trace (an HTTP handler, a DB query, a message publish). It has a name, start time, duration, status and attributes|
|**Parent / child**|Spans form a tree. A child span is work done on behalf of its parent|
|**Span context**|The trace ID, span ID and flags that are propagated between services|
|**Attributes**|Key-value metadata on a span (`http.route`, `db.statement`, `user.tier`)|
|**Events**|Timestamped annotations within a span (such as exceptions)|
|**Links**|References between spans that aren't parent/child (for example a batch job processing many messages)|
|**Baggage**|Key-value data propagated across services (use sparingly, it is sent on every call)|
### Context propagation
For a trace to span services, the trace context must be passed along with every call.
- **HTTP/gRPC:** headers, most commonly the **W3C Trace Context** standard:
- **Messaging (Kafka, SQS, RabbitMQ):** put the context in message headers or attributes so the consumer continues the trace (or links to it).
- **In-process:** use language context mechanisms (Go `context.Context`, Java `Context`, Python `contextvars`) so child spans attach to the right parent, especially across threads and async boundaries.
- Any service that doesn't propagate context **breaks the trace** into disconnected fragments. Gateways, proxies, queues and legacy services are common culprits.

### instrumentation
|Approach|Description|
|---|---|
|**Auto-instrumentation**|Agents or libraries that wrap common frameworks, HTTP clients and DB drivers with no code changes. Quick to adopt.|
|**Manual instrumentation**|You create spans around business logic that matters.|
|**Service mesh / eBPF**|The proxy or kernel-level tooling emits spans for network calls. Good coverage, but little visibility inside the app.|

### Sampling
|Strategy|Decision made|Pros|Cons|
|---|---|---|---|
|**Head-based**|At the start of the trace (for example, keep 1 percent)|Simple, cheap|Can miss rare errors and slow requests|
|**Tail-based**|After the trace completes, in a collector|Can keep **all errors and slow traces** plus a baseline sample|Needs buffering and more infrastructure|
|**Adaptive / dynamic**|Rate adjusts to traffic|Stable cost|More complex|
|**Always-on for key flows**|100 percent for certain routes or tenants|Full detail where it matters|Higher cost|

A strong default is **tail-based sampling that keeps all error traces, all traces above a latency threshold, and a small random percentage of the rest**.