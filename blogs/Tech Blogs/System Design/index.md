# System Design Roadmap Checklist

## 1. Fundamentals
### 0. Foundations

- [ ]  Back-of-the-envelope estimation
- [ ]  Latency numbers every engineer should know

### 1. Core Architecture

- [ ]  Monolith vs microservices
- [ ]  Horizontal vs vertical scaling
- [ ]  Stateless vs stateful services
- [x]  Load balancing
- [x]  Reverse proxies and API gateways
- [ ]  Service discovery
- [ ]  Synchronous vs asynchronous communication

### 2. Databases and Data Management

- [ ]  SQL vs NoSQL
- [ ]  ACID vs BASE
- [ ]  B-tree vs LSM-tree
- [ ]  Indexes
- [ ]  Normalization and denormalization
- [ ]  Transactions, isolation levels and concurrency control
- [ ]  Materialized views
- [ ]  Change data capture (CDC)
- [ ]  Object storage and file storage
- [ ]  Search engines and inverted indexes

### 3. Scaling and Performance

- [x]  Caching (strategies, invalidation, eviction)
- [x]  CDN
- [ ]  Replication: leader-follower, multi-leader, leaderless
- [ ]  Synchronous vs asynchronous replication
- [x]  Sharding and partitioning
- [ ]  Consistent hashing

### 4. Distributed Systems

- [x]  CAP theorem and PACELC
- [ ]  Consistency models
- [x]  Eventual consistency and conflict resolution
- [ ]  Quorums and read/write consistency
- [ ]  Distributed locks and leader election
- [ ]  Clock synchronization, logical clocks and ordering
- [ ]  Distributed transactions: two-phase commit and the Saga pattern
- [ ]  Coordination trade-offs
- [ ]  Deduplication and idempotent consumers

### 5. Messaging and Streaming

- [ ]  Message queues
- [ ]  Pub-sub
- [ ]  Event streams
- [ ]  Delivery guarantees (at-most-once, at-least-once, exactly-once)
- [ ]  Consumer groups

### 6. API Design and Traffic Control

- [x]  REST, gRPC and GraphQL
- [x]  Pagination
- [x]  Idempotency
- [x]  Versioning
- [x]  Rate limiting

### 7. Reliability and Operations

- [ ]  Timeouts and retries
- [ ]  Circuit breakers
- [ ]  Bulkheads
- [ ]  Back-pressure
- [ ]  Graceful degradation
- [ ]  Health checks
- [ ]  Observability: logs, metrics and distributed tracing
- [ ]  SLIs, SLOs and SLAs
- [ ]  Disaster recovery: backups, replication, RPO and RTO
- [ ]  Multi-region architecture and failover
- [ ]  Capacity planning and autoscaling

### 8. Security and Infrastructure

- [ ]  Authentication vs authorization
- [ ]  OAuth 2.0, JWT and session management
- [ ]  Encryption in transit and at rest
- [ ]  Secrets management
- [ ]  Network fundamentals: DNS, TCP, TLS and HTTP
- [ ]  Containers and orchestration fundamentals


## 2. Backend System Design

### Classic Design Problems

- [ ] URL shortener
- [ ] Rate limiter
- [ ] Key-value store / distributed cache
- [ ] News feed / Twitter timeline
- [ ] Chat system / WhatsApp
- [ ] Notification system
- [ ] Search autocomplete / typeahead
- [ ] Video streaming / file storage
- [ ] Payment system or ride-sharing

### Backend Technologies

- [ ] Redis
- [ ] Kafka
- [ ] PostgreSQL / MySQL
- [ ] DynamoDB / Cassandra
- [ ] Elasticsearch / OpenSearch
- [ ] S3 / blob storage
- [ ] API gateways and service meshes
- [ ] WebSockets, SSE and long polling
- [ ] ZooKeeper / etcd
- [ ] Vector databases: Pinecone, pgvector, FAISS, Milvus

### Backend Design Patterns

- [ ] Scaling reads and writes
- [ ] Real-time updates
- [ ] Contention and double-booking prevention
- [ ] Large file uploads and delivery
- [ ] Long-running asynchronous tasks
- [ ] Multi-step workflows and the saga pattern
- [ ] Reliable event publishing: outbox pattern and CDC
- [ ] Multi-region architecture and failover

### Advanced Backend Design Problems

- [ ] Ticket booking / Ticketmaster
- [ ] Top-K, leaderboards and trending systems
- [ ] Distributed job scheduler
- [ ] Web crawler
- [ ] Metrics, logging and monitoring system
- [ ] Collaborative editor / Google Docs
- [ ] Distributed lock service / unique ID generator
- [ ] E-commerce checkout and inventory

## 3. AI/ML System Design Fundamentals

- [ ] Problem framing and deciding whether ML is necessary
- [ ] Business objectives and ML task selection
- [ ] Data sources, labels, sampling and class imbalance
- [ ] Feature engineering and feature stores
- [ ] Training-serving skew
- [ ] Model selection and baseline models
- [ ] Training pipelines and experiment tracking
- [ ] Offline and online evaluation
- [ ] Classification, retrieval and ranking metrics
- [ ] A/B testing and guardrail metrics
- [ ] Model serving, batching, caching and fallbacks
- [ ] Data drift, concept drift and monitoring
- [ ] Feedback loops, bias and fairness

### Core ML Architecture

- [ ] Multi-stage retrieval and ranking
- [ ] Two-tower models
- [ ] Embeddings and approximate nearest-neighbour search
- [ ] Cold-start problems
- [ ] Online vs offline feature stores
- [ ] Batch vs real-time inference
- [ ] Quantisation and distillation
- [ ] Retraining triggers and drift detection

## 4. AI/ML System Design Problems

- [ ] Recommendation systems
- [ ] Search ranking
- [ ] Fraud and abuse detection
- [ ] RAG chatbot / enterprise document Q&A
- [ ] Ad click prediction (CTR)
- [ ] Harmful-content and spam moderation
- [ ] LLM inference serving platform
- [ ] ML platform: feature store and training pipeline

## 5. LLM and Generative AI Systems

- [ ] Tokenisation and context windows
- [ ] RAG: chunking, embeddings, retrieval, reranking and grounding
- [ ] Fine-tuning vs RAG vs prompting
- [ ] LLM evaluation: LLM-as-judge and golden datasets
- [ ] Guardrails and hallucination mitigation
- [ ] Caching, streaming, cost and latency optimisation
- [ ] Continuous batching
- [ ] KV cache
- [ ] GPU memory and throughput optimisation
- [ ] Model routing and autoscaling

## 6. Advanced AI/ML Design Considerations

- [ ] Retrieval using ANN indexes such as HNSW and IVF
- [ ] Hybrid search: BM25 and embeddings
- [ ] Learning-to-rank and ranking evaluation
- [ ] Precision-recall trade-offs and imbalanced datasets
- [ ] Position bias and feedback loops
- [ ] Counterfactual bias in logged data
- [ ] Shadow and canary deployments
- [ ] Pipeline orchestration, lineage, versioning and reproducibility

## 7. Interview Practice and Revision

- [ ] Practise classic backend design questions
- [ ] Practise advanced backend design questions
- [ ] Practise ML and LLM design questions
- [ ] Conduct mock interviews
- [ ] Review weak areas
- [ ] Prepare project-based interview examples
- [ ] Maintain concise design notes covering architecture, trade-offs, estimates and failure scenarios