### Step 1: Understand the Problem
- Ask clarifying questions before designing anything
- Define scope: who are the users, what are the core features, what is out of scope?
- Organize your thoughts aloud so the interviewer can follow your reasoning

### Step 2: Clarify Non-Functional Requirements (NFRs)
NFRs drive the design. A system tolerating “some latency” is very different from one needing a **p99 of 50ms**.

- **Scale**: DAU, QPS, read/write ratio, data volume
- **Latency**: target p50/p99
- **Availability vs. consistency**: CAP trade-offs
- **Durability, security, and cost** constraints

### Step 3: High-Level Design (Top-Down)
- Start with **APIs**, but only for the functional requirements
- Draw the main components: clients, load balancers, app servers, caches, databases, queues, CDN
- Mention partitioning/sharding at this stage
- Walk through the main request flow end to end

### Step 4: Deep Dive and Trade-offs
- Define the **data schema** and choose the database, justified by the NFRs (e.g., SQL for strong consistency, NoSQL for scale and flexibility)
- Cover design constraints: scaling, security, caching, replication, and failure handling
- Propose **multiple solutions**, compare them with numbers (back-of-envelope estimates), discuss trade-offs, and conclude with a choice after discussing with the interviewer

### Step 5: Wrap Up
- Summarize the design and key decisions
- Name bottlenecks, risks, and possible future improvements
- Mention monitoring, observability, and failure scenarios