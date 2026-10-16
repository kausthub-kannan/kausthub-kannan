An API (Application Programming Interface) is a defined way for one piece of software to talk to another. It sets out what requests can be made, what format they must follow and what response will come back, so the two sides do not need to know anything about each other's internal code. In web systems, the term usually means an HTTP API: a client such as a mobile app, a browser or another service sends a request to a URL on a server, and the server processes it and returns a response, usually in JSON. The API is the contract between the two sides. As long as the contract stays the same, the server can change its database, language or architecture without breaking any client.

When a client calls an API, it first resolves the domain through DNS, which may route it to the nearest region using GeoDNS or anycast. The request is encrypted with TLS, may pass through a CDN or reverse proxy and then a load balancer, and then reaches one of many identical application servers. Those servers check a cache such as Redis before falling back to the database. The API is the front door that this whole path leads to, so its design affects the performance, security and scalability of the entire system.

## HTTP Methods
|Method|Purpose|Safe|Idempotent|Example|Notes|
|---|---|---|---|---|---|
|GET|Read a resource|Yes|Yes|GET /users/42|Responses can be cached|
|POST|Create a resource or trigger an action|No|No|POST /orders|Sending twice may create two records|
|PUT|Replace a resource completely|No|Yes|PUT /users/42|Client sends the full object|
|PATCH|Update part of a resource|No|Not guaranteed|PATCH /users/42|Depends on how it is implemented|
|DELETE|Remove a resource|No|Yes|DELETE /users/42|Deleting twice leaves the same end state

## Status Code
|Range|Meaning|Code|Name|When it is used|
|---|---|---|---|---|
|2xx|Success|200|OK|Request succeeded and a body is returned|
|2xx|Success|201|Created|A new resource was created|
|2xx|Success|202|Accepted|Request accepted, processing happens in the background|
|2xx|Success|204|No Content|Success with nothing to return, such as after DELETE|
|3xx|Redirection|301|Moved Permanently|The resource has a new permanent URL|
|3xx|Redirection|304|Not Modified|Cached copy is still valid|
|4xx|Client error|400|Bad Request|Malformed or invalid input|
|4xx|Client error|401|Unauthorized|Not authenticated, or the credentials are invalid|
|4xx|Client error|403|Forbidden|Authenticated but not allowed|
|4xx|Client error|404|Not Found|The resource does not exist|
|4xx|Client error|409|Conflict|Clashes with the current state, such as a duplicate|
|4xx|Client error|429|Too Many Requests|Rate limit exceeded|
|5xx|Server error|500|Internal Server Error|Unexpected failure on the server|
|5xx|Server error|502|Bad Gateway|A proxy got an invalid response from the upstream server|
|5xx|Server error|503|Service Unavailable|Server overloaded or down for maintenance|
|5xx|Server error|504|Gateway Timeout|A proxy timed out waiting for the upstream server|

## Authentication vs Authorisation
|Aspect|Authentication (AuthN)|Authorization (AuthZ)|
|---|---|---|
|Question it answers|Who are you?|What are you allowed to do?|
|Happens|First|After authentication|
|Based on|Credentials: password, token, API key, biometrics|Roles, permissions, policies, ownership of the resource|
|Typical mechanisms|Sessions, JWT, API keys, OpenID Connect|RBAC, ACLs, OAuth 2.0 scopes|
|Failure status code|401 Unauthorized|403 Forbidden|
|Example|Logging in with email and password|A regular user trying to open an admin page is blocked|

## APIs in Production

### Sync vs Async Endpoints
In a synchronous API the client waits until the work is done and the answer is returned. This is fine for quick operations, but poor for long-running ones such as video processing or report generation, where the connection could time out. For these, the API accepts the request, places the job on a queue, immediately returns a 202 (accepted) response with a job ID, and does the work in the background. The client then checks a status endpoint or receives a webhook when the job is complete. This keeps the API responsive and lets the work be scaled separately.
### Rate Limiting and Throttling
Without limits, a single client, a buggy script or an attacker could overwhelm an API. Rate limiting restricts how many requests a client may make in a period, for example 100 per minute per user or API key, and returns 429 when the limit is exceeded. This protects the system, keeps usage fair between clients and defends against abuse and brute-force attacks. Common algorithms are the token bucket, which allows short bursts while enforcing an average rate, and the sliding window, which counts requests over a moving time period. In a distributed system, the counters are normally kept in a shared store such as Redis, so that all servers apply the same limit.

### Pagination, Filtering and Sorting
An endpoint like GET /orders could return millions of records, which would be slow and wasteful, so large collections are returned in pages. Offset pagination uses a page number or offset and a limit, such as ?offset=40&limit=20. It is simple but becomes slow on large tables, and results can shift if data is added while the user is paging. Cursor pagination returns a pointer to the last item seen, such as ?after=abc123, and fetches the next items from there, which is faster and more stable for large or fast-changing data. Filtering and sorting are normally expressed as query parameters, such as ?status=shipped&sort=date.

### Versioning
APIs live for years, and clients such as mobile apps cannot all be updated at once, so changes that would break existing clients need a new version. The most common approach is to put the version in the URL, such as /v1/users and /v2/users. Some APIs use a header instead. Old versions are kept running for a period and then retired with notice. Adding a new optional field is generally safe and does not need a new version, while removing or renaming a field, or changing its meaning, does.

### Error Handling and Responses
A good API gives consistent, helpful responses. Errors should use the correct status code and a structured body that contains a machine-readable error code and a human-readable message, without leaking internal details like stack traces. Successful responses should have a consistent format, and the API should validate all input on the server, since the client can never be trusted. Timeouts and retry behavior should be defined, and clients should retry with exponential backoff, meaning they wait longer between each attempt, so that a struggling server is not hit with a wave of retries.

### Idempotency
Idempotency in APIs is the property that ensures making the same request multiple times produces the same intended effect as making it once. For example, in a payment API, a client might retry a payment request because the server's response was lost. Without idempotency, this could result in the customer being charged multiple times. To prevent this, the client sends a unique idempotency key with the request, and the server uses that key to identify duplicate requests and return the previously stored result instead of processing the payment again. This is particularly important in distributed systems, where network failures, timeouts, and retries are common.

## API Gateway
In systems with many services, clients should not need to know each service's address or deal with each one's security separately. An API gateway is a single entry point that sits in front of all the services and is essentially a reverse proxy with extra features. It routes each request to the correct service, handles authentication, rate limiting, TLS termination, logging and monitoring in one place, and can cache responses, combine results from several services and translate between protocols. It simplifies clients and keeps these shared concerns out of the individual services. Its drawback is that it can become a single point of failure and a bottleneck, so it must be scaled and replicated behind a load balancer.

## API Types
APIs can be classified in two useful ways: by who is allowed to use them, and by the style they use to communicate.

By access:

| Type               | Who uses it                   | Example                                              | Notes                                             |
| ------------------ | ----------------------------- | ---------------------------------------------------- | ------------------------------------------------- |
| Public (open)      | Any developer                 | Weather or maps API                                  | Needs strong rate limiting and good documentation |
| Partner            | Selected business partners    | Payment or logistics integration                     | Access controlled by agreements and keys          |
| Private (internal) | Teams inside one company      | Microservice to microservice calls                   | Hidden from the internet, can change faster       |
| Composite          | Clients needing combined data | Gateway call that gathers data from several services | Reduces the number of round trips                 |

By style:

|Aspect|REST|GraphQL|gRPC|SOAP|
|---|---|---|---|---|
|Data format|JSON (usually)|JSON|Protocol Buffers (binary)|XML|
|Transport|HTTP/1.1 or HTTP/2|HTTP, usually POST|HTTP/2|HTTP and others|
|Endpoints|Many, one per resource|Single endpoint|Defined service methods|Single endpoint, defined by WSDL|
|Who decides the response shape|Server|Client|Contract (proto file)|Contract (WSDL)|
|Speed|Good|Good, depends on queries|Very fast|Slower, heavy XML|
|Caching|Easy, uses HTTP caching|Harder, since everything is a POST|Limited|Limited|
|Streaming|No (needs add-ons)|Via subscriptions|Yes, built in|No|
|Browser support|Excellent|Excellent|Needs a proxy layer|Possible but clumsy|
|Best for|Public APIs, general web services|Mobile apps and complex UIs needing flexible data|Internal microservice communication|Legacy enterprise and banking systems|
|Main drawback|Over-fetching and under-fetching|Complex server, risk of expensive queries|Not human-readable, weak browser support|Verbose and rigid|

REST is the default choice for most public APIs because it is simple, well understood and cache-friendly. GraphQL is chosen when clients need flexibility over the data they receive, gRPC when speed between internal services matters most, and SOAP mostly when integrating with older systems that already require it.

## Real-Time and Event-Driven Communication
Standard request-response APIs only let the client ask, and sometimes the server needs to push updates. Several techniques exist, and they differ in direction, efficiency and complexity.

|Technique|How it works|Direction|Good for|Drawback|
|---|---|---|---|---|
|Polling|Client asks repeatedly at fixed intervals|Client to server|Simple status checks|Wasteful, since most requests return nothing new|
|Long polling|Request is held open until the server has data|Client to server, then response|Near real-time updates with simple setup|Many open connections, reconnect after each response|
|Server-Sent Events|Server streams updates over one open HTTP connection|Server to client only|Live feeds, notifications|One-way only|
|WebSockets|Persistent two-way connection|Both ways|Chat, live collaboration, games|Harder to scale, since connections are stateful|
|Webhooks|Server calls a URL registered by the client when an event happens|Server to server|Payment confirmations, event notifications|Receiver must be reachable and handle retries|
