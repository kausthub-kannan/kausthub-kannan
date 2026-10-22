
Software architecture is the high-level structure of a system: how it is divided into parts, what each part is responsible for, how the parts communicate and where the data lives. It is a set of decisions that are expensive to change later, so they have a large effect on how easily the system can be built, deployed, scaled, understood and kept running. There is no single best architecture. Each style makes trade-offs between simplicity, scalability, speed of development and operational cost, and the right choice depends on the size of the team, the size of the problem and the stage of the product.

The main styles covered here are the monolith, the modular monolith, microservices, service-oriented architecture, serverless and event-driven architecture. Layered (n-tier) design is also covered, since it often sits inside them.

## Layered (n-tier) Architecture
Layered architecture organizes code, or sometimes servers, into horizontal layers where each layer has one responsibility and talks only to the layer directly below it. The classic version has three layers: a presentation layer (the user interface or API controllers), a business logic layer (the rules of the application) and a data access layer (the database code). When the layers run on different machines, it is called an n-tier architecture, such as a web browser, an application server and a database server.

This style is simple and familiar, and it separates concerns so that, for example, the database can be changed without touching the user interface. Its weakness is that all layers are usually packaged and deployed together, and a change that cuts across layers touches all of them. It describes how code is organized inside a system, which is why it is commonly found inside monoliths and inside each microservice.

## Monolith Architecture
A monolith is an application built as a single unit. All the features, such as user accounts, orders, payments, inventory and notifications, live in one codebase, are built into one deployable artifact and typically use one shared database. Parts of the application call each other through ordinary function calls within the same process, which is fast and simple.

### Advantages
Development is simple at the start, with one codebase to understand, one thing to build and run, and no network between components. Calls within the process are fast and reliable, and transactions that touch several features are easy, since one database can guarantee them with ACID properties. Testing is straightforward because the whole system can be run end to end on one machine. Deployment is a single artifact, and debugging is easier because everything is in one place, with a single stack trace and a single log. Operating costs are low, as there is little infrastructure to manage.

### Disadvantages
As the application and the team grow, the codebase becomes large and tangled, and a small change can have unexpected effects somewhere else, which makes people afraid to change it. The whole application must be built, tested and deployed together, so a one-line fix to one feature means redeploying everything, and releases become slow and risky. Scaling is all or nothing: if only the search feature is under heavy load, the entire application must be duplicated, wasting resources. A bug such as a memory leak in one module can bring down the whole application. The technology stack is fixed for everything, and many developers working on one codebase get in each other's way.

A monolith can still be scaled horizontally by running identical copies behind a load balancer, as long as it is stateless. Its limits are about the speed of development and the lack of independent scaling, not about being unable to run on multiple servers.

## Modular Monolith Architecture
A modular monolith is a middle path. It is still one deployable application with one database, but the code inside is divided into well-separated modules, each owning a business area such as orders or payments. Modules talk to each other only through clear public interfaces, and they do not reach into each other's internals or tables. This keeps most of the simplicity of a monolith while giving the clear boundaries that make it understandable and easy to change, and it makes a later split into microservices much easier, since the boundaries already exist. Many teams now recommend it as the best starting point for new products.

## Microservices
Microservices is an architecture where an application is built as a collection of small, independent services, each responsible for one business capability, running as its own process and communicating over the network. Instead of one big application, there might be separate user, product, order, payment, inventory and notification services, each with its own codebase, its own deployment and its own database.

### Core Principles
|Principle|Meaning|
|---|---|
|Single responsibility|Each service does one business job well, and is small enough for a small team to understand fully|
|Bounded context|Service boundaries follow the business domain (an idea from domain-driven design), so each service owns its own concepts and rules|
|Independent deployment|A service can be changed, tested and released on its own, without redeploying others|
|Database per service|Each service owns its data, and others can access it only through the service's API, never by reading its tables|
|Decentralized technology|Each team may choose the language and tools that suit its service|
|Design for failure|Any other service can be slow or down at any time, so each service must cope with that|
|Own your service|The team that builds a service also runs it (build it, run it), which follows Conway's law: system structure mirrors the team structure|

### Advantages
Services can be deployed independently, so teams release small changes often and with less risk. Each service can be scaled on its own, so only the heavily loaded one (say, search or checkout) gets more servers, which saves cost. A failure can be contained, so if the recommendation service fails, customers can still buy, provided the system is designed to degrade gracefully. Small codebases are easier to understand, and small teams can work in parallel without blocking each other. Different technologies can be used where they fit best, and services can be rewritten one at a time.

### Disadvantages
|Challenge|Why it is hard|
|---|---|
|Network is unreliable|Calls between services can be slow, fail or time out, unlike in-process calls, so timeouts, retries and fallbacks are needed everywhere|
|Distributed data|No shared database means no simple joins or ACID transactions across services, and data is eventually consistent|
|Operational overhead|Dozens of services mean dozens of pipelines, deployments, configurations and monitoring dashboards|
|Debugging|A single user request passes through many services, so finding the failing one requires distributed tracing|
|Testing|End-to-end tests need many services running, so contract testing is used between them|
|Latency|Many network hops add delay compared with local calls|
|Versioning|An API change must not break other services that depend on it|
|Skills and cost|Needs mature DevOps, automation, monitoring and a larger infrastructure budget|

### Communication between Services
|Style|How it works|Tools|Use when|Drawback|
|---|---|---|---|---|
|Synchronous|The caller sends a request and waits for the reply|REST over HTTP, gRPC|A result is needed immediately, such as a price lookup|The caller is blocked, and a slow or failed service causes failures that spread to its callers|
|Asynchronous|The sender publishes a message or event and moves on|Message queues, Kafka, RabbitMQ, SNS|Work can be done later, or many services react to one event|Eventual consistency, harder to trace|

An API gateway is the single entry point for clients. It routes requests to the right service and handles authentication, rate limiting and TLS termination, as in the API and proxy notes. Service discovery lets services find each other's current addresses, since instances start, stop and move constantly, using a registry such as Consul, or the built-in DNS in Kubernetes. Each service runs several instances behind a load balancer. Central configuration stores settings outside the code. Containers (Docker) package each service with its dependencies, and an orchestrator such as Kubernetes runs, scales and heals them. A CI/CD pipeline for each service builds, tests and deploys it automatically. Finally, observability is essential and has three parts: centralized logs, metrics (rates, errors, latency) and distributed tracing, which follows one request across all services using a shared correlation ID.

### Service Discovery
In a monolith, one part calls another with a function call, and there is no question of where the other part is. In microservices, the Order service must call the Payment service over the network, which needs an address. Hardcoding an IP address does not work, because instances are constantly created and destroyed: autoscaling adds copies, deployments replace them, failures remove them, and containers get a new IP address every time they start. Service discovery is the mechanism that lets a service find the current, healthy network locations of the other services it needs, using a stable name such as "payments" instead of an address.

#### Registry
The heart of service discovery is the service registry, a database that maps each service name to the list of addresses (IP and port) of its currently running, healthy instances. Four things happen around it. Instances register themselves when they start. They stay registered by proving they are alive. Clients look up a name to get the instance list. And instances that disappear or become unhealthy are removed.

| Approach                 | How it works                                                                                                      | Examples                           | Pros                               | Cons                                                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ---------------------------------- | ---------------------------------------------------------- |
| Self-registration        | Each instance registers itself with the registry on startup, sends regular heartbeats and deregisters on shutdown | Netflix Eureka client              | Simple, no extra component         | Registration code in every service, tied to the registry   |
| Third-party registration | A separate component, usually the platform, watches for instances and registers them on their behalf              | Kubernetes, Consul agents, AWS ECS | Services stay unaware of discovery | Another component to run, and the platform must be trusted |

#### Client-side vs Service-side Discovery
| Aspect                   | Client-side discovery                                                     | Server-side discovery                                                                 |
| ------------------------ | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Who looks up the address | The calling service queries the registry itself                           | A load balancer or router queries the registry for it                                 |
| Who picks the instance   | The client, using its own load balancing logic                            | The load balancer                                                                     |
| Flow                     | Client asks the registry, gets a list, and calls an instance directly     | Client calls one stable address, and the load balancer forwards to a healthy instance |
| Network hops             | One (direct call)                                                         | Two (through the load balancer)                                                       |
| Client complexity        | High, discovery and balancing logic in every client and every language    | Low, the client just uses a name or address                                           |
| Registry coupling        | Clients depend on the registry                                            | Only the load balancer does                                                           |
| Examples                 | Netflix Eureka with Spring Cloud LoadBalancer, gRPC client-side balancing | Kubernetes Service, AWS load balancer with target groups, NGINX with Consul           |
| Weak point               | Every client needs a discovery library                                    | The load balancer must itself be highly available and can become a bottleneck         |

#### DNS Discovery
The simplest form of discovery uses DNS. A service name resolves to the IP addresses of its instances, and the caller just uses the name. In Kubernetes, every Service gets a DNS name served by CoreDNS, and the Service has a stable virtual IP that spreads traffic across the healthy pods behind it.

#### Discovery Tools
| Tool                  | Type                                              | Notes                                                                              |
| --------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Consul                | Registry with health checks and a key-value store | Uses Raft consensus, offers DNS and HTTP interfaces, and works across data centers |
| etcd                  | Distributed key-value store                       | Strongly consistent, it is the store behind Kubernetes                             |
| Apache ZooKeeper      | Coordination service                              | Older and widely used for discovery and leader election, strongly consistent       |
| Netflix Eureka        | Registry for client-side discovery                | Favors availability, so it can keep serving a slightly stale list during failures  |
| Kubernetes (built in) | Platform-level discovery                          | Services and CoreDNS, with no separate registry to run                             |
| AWS Cloud Map         | Managed registry                                  | Integrates with ECS and other AWS services                                         |

#### Mitigating Service Discovery problems

| Problem                      | Cause                                                                 | Mitigation                                                      |
| ---------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------- |
| Stale entries                | A crashed instance stays listed until its TTL or health check expires | Short heartbeat intervals, active health checks, client retries |
| Registry outage              | The registry is a single point of failure                             | Cluster it and let clients cache the last known list            |
| Traffic to unready instances | Instance registered before it can serve requests                      | Use readiness checks before listing                             |
| Flapping                     | An unhealthy instance repeatedly joins and leaves                     | Thresholds before removal and before re-adding                  |
| DNS caching                  | Resolvers hold old addresses beyond their usefulness                  | Low TTLs or discovery through the platform, not plain DNS       |

#### Service Mesh
A service mesh such as Istio or Linkerd moves discovery, load balancing, retries, timeouts and encryption out of the application and into a small proxy (a sidecar, often Envoy) that runs next to each service instance. A central control plane keeps track of all instances and pushes the current list to every sidecar. The application just calls another service by name, and its sidecar finds a healthy instance, balances the load, retries on failure and encrypts the connection with mutual TLS. This gives consistent behavior across all languages without libraries in each service, at the cost of running and understanding another layer of infrastructure.

### Resilience Patterns
Because any service can fail, microservices rely on defensive patterns. Timeouts stop a caller from waiting forever. Retries with exponential backoff handle brief failures without flooding a recovering service. A circuit breaker stops calling a service that is failing and returns quickly instead, giving it time to recover.

|Circuit breaker state|Behavior|
|---|---|
|Closed|Normal operation, requests pass through, failures are counted|
|Open|Too many failures, so calls are rejected immediately without trying, and a fallback is used|
|Half-open|After a wait, a few test requests are allowed, and success closes the circuit while failure reopens it|

### Data Consistency - Sagas
With a database per service, a business operation that spans several services cannot use one transaction. A saga solves this by splitting the operation into a sequence of local transactions, each in one service, with a compensating action to undo it if a later step fails. For placing an order, the steps might be to create the order, reserve the stock, charge the payment and arrange shipping, and if the payment fails, the stock reservation is released and the order is cancelled.

|Saga type|How it works|Pros|Cons|
|---|---|---|---|
|Choreography|Each service reacts to events from others and publishes its own, with no central controller|Simple, loosely coupled|The overall flow is hard to see and follow as it grows|
|Orchestration|A central orchestrator tells each service what to do next and handles failures|Clear flow, easy to monitor|The orchestrator is an extra component and a coupling point|

The outbox pattern, from the message queue notes, is used to publish events reliably along with the database change. The system is eventually consistent, so the product must be designed for it, for example by showing "order received" before the payment is confirmed.

### Example: E-Commerce Application
| Service      | Responsibility                 | Own data                 | Typical store                            |
| ------------ | ------------------------------ | ------------------------ | ---------------------------------------- |
| User         | Accounts, login, profiles      | Users, credentials       | Relational database                      |
| Catalog      | Products, descriptions, prices | Product data             | Document database, with a cache          |
| Search       | Product search                 | Search index             | Elasticsearch                            |
| Cart         | Shopping cart                  | Cart contents            | Redis                                    |
| Order        | Creating and tracking orders   | Orders                   | Relational database                      |
| Payment      | Charging customers             | Payment records          | Relational database, strictly consistent |
| Inventory    | Stock levels                   | Stock counts             | Relational database                      |
| Notification | Email, SMS, push               | Templates, delivery logs | Queue plus database                      |

### Monolith vs Microservices
|Aspect|Monolith|Microservices|
|---|---|---|
|Structure|One codebase and one deployable unit|Many small independent services|
|Communication|In-process function calls|Network calls (REST, gRPC) and messages|
|Data|One shared database|Database per service|
|Transactions|Simple ACID transactions|Sagas and eventual consistency|
|Deployment|All or nothing|Each service independently|
|Scaling|Whole application as one|Each service on its own|
|Fault isolation|One bug can bring down everything|Failures can be contained|
|Technology|One stack for everything|Different stacks per service|
|Team structure|One team or tightly coordinated teams|Small autonomous teams per service|
|Development speed|Fast at the start, slows as it grows|Slower to set up, faster later at large scale|
|Operational complexity|Low|High|
|Testing and debugging|Easy, all in one place|Hard, needs tracing and contract tests|
|Latency|Low|Higher because of network hops|
|Best for|Startups, small teams, simple or new products|Large systems, many teams, parts with very different scaling needs|

A distributed monolith is the most common failure. The system is split into services, but they are tightly coupled, share a database or must be deployed together, so it has all the costs of microservices with none of the benefits. A shared database between services breaks independence, since a table change breaks other services. Services that are too small (nano-services) create more overhead than value. Long chains of synchronous calls make the system as fragile as its weakest service and add latency at every hop. And starting with microservices before the domain is understood leads to wrong boundaries that are expensive to fix.

## Serverless Architecture
In serverless architecture, the application is built from small functions or managed services that run on demand, and the cloud provider handles all servers, scaling and patching. Developers upload code, such as an AWS Lambda function, which runs when triggered by an HTTP request, a queue message, a file upload or a schedule, and they pay only for the time it runs, with nothing charged when idle. It scales automatically from zero to thousands of parallel runs.

The benefits are no server management, automatic scaling and low cost for uneven or occasional workloads. The drawbacks are cold starts (a delay when a function that has been idle is started again), time and memory limits per run, difficulty in running long tasks, stateless functions that need external storage, vendor lock-in and harder local testing and debugging. It suits event-driven jobs such as image processing after upload, scheduled tasks and lightweight APIs, and is less suited to constant, heavy, latency-sensitive workloads, where permanent servers can be cheaper.

## Event-Driven Architecture
In event-driven architecture, components communicate by producing and reacting to events, which are records that something happened, such as "order placed" or "payment completed". Producers publish events to a broker such as Kafka or RabbitMQ, without knowing who consumes them, and any number of consumers react independently. This gives very loose coupling, since a new service can be added by simply subscribing to an event, and it handles bursts well. The cost is that the flow of logic is spread across many components and harder to follow, and the system is eventually consistent.

Two patterns often go with it. Event sourcing stores the full sequence of events as the source of truth and rebuilds the current state by replaying them, giving a complete history and audit trail. CQRS (Command Query Responsibility Segregation) uses separate models for writing and for reading, so that each can be optimized and scaled separately, with the read side often built from the events. Both add considerable complexity, so they are used only where their benefits are needed.

## Architecture Comparison

|Style|Deployment unit|Strengths|Weaknesses|Best for|
|---|---|---|---|---|
|Layered / n-tier|Usually one application|Simple, familiar, clear separation of concerns|Changes cut across layers, often deployed together|Small to medium business applications|
|Monolith|One unit|Simple to build, test, deploy and debug|Hard to scale parts, slows down as it grows|Startups and new products|
|Modular monolith|One unit with strong internal modules|Simplicity with clear boundaries, easy to split later|Needs discipline to keep modules separate|Most new products, a safe default|
|Microservices|Many independent services|Independent scaling and deployment, fault isolation, team autonomy|High operational and data complexity|Large systems and many teams|
|SOA|Coarse-grained shared services|Enterprise reuse and integration|Heavy central bus, shared data|Large enterprises with legacy systems|
|Serverless|Functions on demand|No servers, automatic scaling, pay per use|Cold starts, limits, vendor lock-in|Event-driven and spiky workloads|
|Event-driven|Components linked by events|Loose coupling, handles bursts|Harder to trace, eventual consistency|Real-time and highly decoupled systems|
