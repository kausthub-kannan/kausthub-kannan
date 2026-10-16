## Fine-Tuning Custom Models & Continued Pre-Training with Bedrock

### 1.1 Why Customise a Foundation Model?

|Situation|Recommended Approach|
|---|---|
|Model needs private/recent factual knowledge|RAG (no weight changes)|
|Model needs to follow a specific output format or style|Fine-tuning|
|Model answers incorrectly for a specialized domain|Continued Pre-training → Fine-tuning|
|Model needs to adopt a specific persona or tone|Fine-tuning|
|Reduce inference token usage (bake instructions into weights)|Fine-tuning|

Bedrock supports two customization modes:

1. **Fine-Tuning** — supervised learning on labeled `(prompt, completion)` pairs
2. **Continued Pre-Training** — unsupervised learning on unlabeled domain text

---

### 1.2 Fine-Tuning on Bedrock

#### Supported Models

- **Amazon Titan** Text Express, Text Lite
- **Cohere** Command, Command Light
- **Meta** LLaMA 2 (via JumpStart bridge — not all regions)
- Anthropic Claude models are **not fine-tunable** on Bedrock (use prompt engineering / RAG)

#### Training Data Format

- **JSONL** format — one JSON object per line
- Each line: `{"prompt": "...", "completion": "..."}`
- Stored in **Amazon S3**
- Recommended minimum: **~100 examples**; more is always better (1K–10K+ for robust results)
- Validation split: provide a separate validation JSONL for loss tracking

```json
{"prompt": "Classify the sentiment: 'The product broke after one day'", "completion": "Negative"}
{"prompt": "Classify the sentiment: 'Absolutely love this, works perfectly'", "completion": "Positive"}
```

#### Fine-Tuning Job Configuration

- **Base model** — select supported FM version
- **Training data URI** — S3 path to training JSONL
- **Validation data URI** — S3 path to validation JSONL (optional but recommended)
- **Hyperparameters:**

|Hyperparameter|Purpose|Typical Range|
|---|---|---|
|`epochCount`|Number of passes through training data|1–10|
|`batchSize`|Samples per gradient update|8–64|
|`learningRate`|Step size for weight updates|1e-6 – 1e-4|
|`learningRateWarmupSteps`|Steps before LR reaches its set value|0–100|

- **Output model** — stored as a private custom model in your Bedrock account
- **IAM role** — Bedrock assumes role with S3 read access for training data

#### Provisioned Throughput (Required for Custom Models)

- Fine-tuned models **cannot** be invoked on-demand — you must purchase **Provisioned Throughput**
- Provisioned Throughput = reserved model units (MUs) for your custom model
- Commitment options: **no commitment** (hourly, cancelable), **1 month**, **6 months** (discounted)
- Invoke custom model via its **model ARN** just like a base model

---

### 1.3 Continued Pre-Training (Domain Adaptation)

#### Purpose

- Expose the model to **large volumes of unlabeled domain text** before fine-tuning
- Model learns domain vocabulary, writing style, relationships, and entity patterns
- Use case: medical literature, legal documents, proprietary technical manuals, financial filings

#### Data Format

- **JSONL** but only the `"input"` field (no labels)
- Each line: `{"input": "raw domain text goes here..."}`
- Much larger datasets acceptable — 100MB to GBs of text

```json
{"input": "The hepatic portal vein carries nutrient-rich blood from the gastrointestinal tract to the liver..."}
{"input": "Section 12(b) of the Securities Exchange Act requires registration of securities listed on national exchanges..."}
```

#### Recommended Pipeline

```
Domain text corpus (S3)
        ↓
Continued Pre-Training job (Bedrock)
        ↓
Domain-adapted base model
        ↓
Fine-Tuning job on labeled task data
        ↓
Final custom model → Provisioned Throughput → Invoke
```

#### Key Differences: Fine-Tuning vs Continued Pre-Training

| Dimension   | Fine-Tuning                          | Continued Pre-Training       |
| ----------- | ------------------------------------ | ---------------------------- |
| Data        | Labeled `(prompt, completion)` pairs | Unlabeled raw text           |
| Goal        | Task behavior, format, style         | Domain knowledge, vocabulary |
| Data volume | 100–10K examples                     | 100K–millions of documents   |
| Runs after  | Base model or domain-adapted model   | Base model only              |
| Output      | Task-specialized model               | Domain-adapted model         |

---

### 1.4 Model Evaluation After Customization

- Use **Bedrock Model Evaluation** to compare base vs custom model
- Automatic metrics: ROUGE-L, METEOR, BERTScore, accuracy (for classification)
- Human evaluation: send output pairs to internal reviewers or MTurk
- Define evaluation prompt dataset as JSONL in S3
- Review results in the Bedrock console; choose which model to deploy

---

## 2. RAG Fundamentals with Bedrock

### 2.1 Why RAG?

|Problem|How RAG Solves It|
|---|---|
|LLM knowledge cutoff|Retrieve up-to-date external documents at query time|
|Hallucination|Ground answer in retrieved verified source text|
|Private / proprietary data|Index internal documents; not baked into model weights|
|Cost of fine-tuning|Retrieval is cheaper than re-training|
|Auditability|Can cite retrieved sources in responses|

### 2.2 RAG Architecture

```
┌─────────────────────────────────────────────────────┐
│                  INGESTION PIPELINE                  │
│                                                      │
│  Documents (S3)                                      │
│      ↓                                               │
│  Chunking (split into passages)                      │
│      ↓                                               │
│  Embedding Model (convert each chunk → vector)       │
│      ↓                                               │
│  Vector Store (index vectors with metadata)          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  QUERY PIPELINE                      │
│                                                      │
│  User Query                                          │
│      ↓                                               │
│  Embed Query (same embedding model)                  │
│      ↓                                               │
│  Vector Similarity Search → Top-K chunks             │
│      ↓                                               │
│  Construct Prompt: [System] + [Context] + [Query]    │
│      ↓                                               │
│  LLM generates grounded response                     │
│      ↓                                               │
│  (Optional) Return source citations                  │
└─────────────────────────────────────────────────────┘
```

### 2.3 Retrieval Methods

|Method|Mechanism|Pros|Cons|
|---|---|---|---|
|**Dense Retrieval**|Embed query + documents; cosine similarity search|Semantic understanding; handles paraphrase|Requires embedding model; compute intensive|
|**Sparse Retrieval (BM25/TF-IDF)**|Keyword frequency matching|Fast; interpretable; no embeddings needed|Misses synonyms and semantic meaning|
|**Hybrid Retrieval**|Combine dense + sparse scores (e.g., RRF — Reciprocal Rank Fusion)|Best of both; handles both semantic and keyword queries|More complex pipeline|
|**Re-ranking**|Pass top-N dense results through a cross-encoder reranker|High precision for top results|Adds latency; extra model call|

**Bedrock Knowledge Bases default**: dense retrieval (vector similarity) with optional hybrid search.

### 2.4 Similarity Metrics

|Metric|Formula|When to Use|
|---|---|---|
|**Cosine Similarity**|`cos(θ) = (A·B) / (‖A‖‖B‖)`|Normalized embeddings; most common default|
|**Dot Product**|`A · B`|When vectors are already normalized (equivalent to cosine)|
|**Euclidean Distance (L2)**|`‖A - B‖`|When magnitude differences are meaningful|

### 2.5 Chunking Strategies (Core + Bedrock Addendum)

Chunking is how source documents are split into retrievable passages. It is one of the most impactful decisions in a RAG pipeline.

#### Fixed-Size Chunking

- Split document every N tokens regardless of content boundaries
- **Chunk size**: 256–512 tokens typical
- **Overlap**: 10–20% overlap between adjacent chunks to prevent context loss at boundaries
- Simple but can cut sentences or paragraphs mid-thought

#### Sentence-Based Chunking

- Split on sentence boundaries using NLP sentence segmentation
- Respects linguistic units; better coherence per chunk
- May produce very short or very long chunks if sentence lengths vary

#### Paragraph / Semantic Chunking

- Split on paragraph breaks or semantic topic shifts
- Produces more coherent, context-complete chunks
- **Semantic chunking** uses embedding similarity between consecutive sentences to detect topic shifts — merge sentences into chunks until similarity drops below a threshold

#### Hierarchical Chunking

- Two levels: **parent chunks** (large, ~2K tokens) and **child chunks** (small, ~256 tokens)
- Embed and retrieve **child chunks** (precision) but return **parent chunk** content to the LLM (context)
- Solves the precision vs context completeness tradeoff

#### **Bedrock Knowledge Bases Chunking Strategies (Exam Addendum)**

|Strategy|Description|Best For|
|---|---|---|
|**Default (Fixed-Size)**|Split at fixed token count with configurable overlap|General purpose; fastest to set up|
|**Fixed-Size Chunking**|Explicit control: set `maxTokens` (100–8192) and `overlapPercentage` (0–99%)|When you know expected query/answer scope|
|**Semantic Chunking**|Groups semantically similar sentences using embedding similarity; configurable buffer size and breakpoint percentile|Long, varied documents where topic shifts naturally|
|**Hierarchical Chunking**|Parent + child chunk dual-level indexing; child chunks retrieved, parent returned to LLM|Complex documents (contracts, manuals, reports)|
|**No Chunking**|Each document treated as a single chunk|Very short documents; FAQs; already-chunked data|
|**Lambda-Based Custom Chunking**|Invoke a Lambda function to apply completely custom splitting logic|Proprietary document formats, complex layouts, tables|

**Chunking configuration in Bedrock Console:**

- Go to Knowledge Base → Data Source → Edit → Chunking Strategy
- `maxTokens`: max tokens per chunk
- `overlapPercentage`: % of tokens shared between consecutive chunks
- Semantic: `bufferSize` (sentences before/after breakpoint), `breakpointPercentileThreshold` (sensitivity to topic shifts)

**Impact of chunk size:**

- **Smaller chunks** → higher retrieval precision, less noise in context, risk of missing surrounding context
- **Larger chunks** → more context per retrieved passage, risk of irrelevant content diluting the answer

---

## 3. Vector Stores & Embeddings with Bedrock

### 3.1 Embeddings

An embedding is a **dense vector** (list of floats) that encodes the **semantic meaning** of text. Texts with similar meaning have vectors that are close together in the embedding space.

**Properties:**

- Dimensionality: 256 to 4096 floats depending on model
- Computed by a dedicated embedding model — different from the generative LLM
- **Same embedding model** must be used for both ingestion and query time

#### Amazon Titan Embeddings Models (Bedrock)

|Model|Dimensions|Context|Best For|
|---|---|---|---|
|`amazon.titan-embed-text-v1`|1536|8K tokens|English text, general RAG|
|`amazon.titan-embed-text-v2:0`|256 / 512 / 1024 (configurable)|8K tokens|Flexible size; lower cost at 256-dim|
|`amazon.titan-embed-image-v1`|1024|Text + image|Multimodal search (image + text in same space)|

**Cohere Embed on Bedrock:**

- `cohere.embed-english-v3` / `cohere.embed-multilingual-v3`
- Supports batching up to 96 texts per call
- 1024 dimensions; strong multilingual support

#### Embedding Best Practices

- Use the **same model version** at ingest and query time — different models produce incompatible spaces
- Normalize vectors before storing if using dot product similarity
- For multilingual content, use a multilingual embedding model
- Monitor **embedding drift** if you swap models later — re-embed the entire corpus

---

### 3.2 Vector Stores

A vector store (vector database) indexes high-dimensional embedding vectors and enables fast **approximate nearest neighbor (ANN)** search.

#### ANN Algorithms

|Algorithm|Used In|Notes|
|---|---|---|
|**HNSW** (Hierarchical Navigable Small World)|OpenSearch, Pinecone, Weaviate|Fast, memory-efficient graph-based index|
|**IVF** (Inverted File Index)|FAISS|Clusters vectors; searches only nearest clusters|
|**FAISS Flat**|FAISS|Exact search; no approximation; slow at scale|
|**ScaNN**|Google; some DBs|Highly optimized for large-scale ANN|

#### Vector Stores Supported by Bedrock Knowledge Bases

|Vector Store|Type|Notes|
|---|---|---|
|**Amazon OpenSearch Serverless**|Managed, serverless|**Default and easiest**; auto-scales; built-in vector engine|
|**Amazon Aurora PostgreSQL**|Managed relational + vector|Uses `pgvector` extension; good for existing Aurora users|
|**Amazon RDS PostgreSQL**|Managed relational + vector|`pgvector`; full RDS control|
|**Amazon Neptune Analytics**|Graph + vector|Combine graph traversal with vector search|
|**Pinecone**|Third-party managed|High performance; serverless option|
|**MongoDB Atlas**|Third-party managed|Integrated document + vector search|
|**Redis Enterprise**|Third-party managed|In-memory; ultra-low latency|

#### OpenSearch Serverless as Vector Store (Exam Detail)

- Collection type: **Vector Search**
- Index: create with `knn_vector` field type and HNSW engine
- Bedrock manages index creation automatically when using Knowledge Bases
- Query: `knn` query type; returns `_score` based on cosine similarity

#### Metadata Filtering

- Each chunk stored with **metadata** (source document, page, date, category, etc.)
- At query time, apply **pre-filters** on metadata before vector search → narrows search space
- Example: filter `{"category": "legal"}` before semantic search → only retrieves legal documents
- Bedrock Knowledge Bases supports metadata filtering via `filter` parameter in `Retrieve` API

---

### 3.3 Bedrock Knowledge Bases — Deep Dive

#### Architecture

```
Data Sources (S3, Confluence, SharePoint, Salesforce, Web Crawl)
        ↓
Bedrock KB ingestion job
        ├─ Chunk documents (configurable strategy)
        ├─ Embed chunks (Titan or Cohere embedding model)
        └─ Store vectors + metadata in vector store
```

#### Data Sources Supported

- **Amazon S3** — PDF, TXT, HTML, DOCX, XLSX, CSV, Markdown
- **Confluence** — pages and spaces
- **SharePoint** — sites and document libraries
- **Salesforce** — Knowledge Articles
- **Web Crawler** — seed URLs; configurable crawl depth
- Custom data sources via **Lambda data source connector**

#### Ingestion

- **Sync** — triggered manually or on schedule; scans for new/modified/deleted documents
- Incremental sync — only re-processes changed documents
- Check sync status: `COMPLETE`, `IN_PROGRESS`, `FAILED`

#### Query APIs

|API|Description|
|---|---|
|`Retrieve`|Returns raw retrieved chunks with scores and metadata — no LLM call|
|`RetrieveAndGenerate`|End-to-end RAG: retrieves chunks AND calls LLM to generate response|

**`RetrieveAndGenerate` parameters:**

- `knowledgeBaseId` — ID of your KB
- `modelArn` — FM to use for generation (any Bedrock text model)
- `numberOfResults` — top-K chunks to retrieve (default 5; range 1–100)
- `retrievalConfiguration.vectorSearchConfiguration.filter` — metadata filter
- `retrievalConfiguration.vectorSearchConfiguration.overrideSearchType` — `SEMANTIC` or `HYBRID`

#### Guardrails Integration

- Apply a Bedrock Guardrail to a Knowledge Base query
- Guardrail checks: input, retrieved context, and generated output
- Add `guardrailConfiguration.guardrailId` to `RetrieveAndGenerate` call

#### Citations & Source Attribution

- `RetrieveAndGenerate` response includes `citations` array
- Each citation: source chunk text, document S3 URI, page number, chunk metadata
- Use citations to build "Show sources" UI features

---

## 4. Content Filtering with AWS Bedrock Guardrails

### 4.1 What Are Guardrails?

Guardrails are **policy-based content filters** applied independently of the FM. They intercept inputs and outputs, evaluate them against defined policies, and either pass, block, or redact content. They work with **any Bedrock model** and can also be applied to fine-tuned custom models.

```
User Input → [Guardrail INPUT check] → FM Inference → [Guardrail OUTPUT check] → Response
                    ↓ (if blocked)                            ↓ (if blocked)
              "Sorry, I can't..."                       "Sorry, I can't..."
```

---

### 4.2 Guardrail Components

#### 4.2.1 Content Filters (Harmful Content)

Filters content across **6 harm categories** at configurable **strength levels**:

|Category|What It Catches|
|---|---|
|**Hate**|Content promoting discrimination based on race, gender, religion, ethnicity, etc.|
|**Insults**|Demeaning or disrespectful language|
|**Sexual**|Explicit sexual content|
|**Violence**|Content glorifying or describing violence|
|**Misconduct**|Criminal activity, fraud, impersonation|
|**Prompt Attack**|Prompt injection and jailbreak attempts|

**Filter Strength Levels** (per category, separately for input and output):

- `NONE` — no filtering
- `LOW` — catch only high-confidence, explicit violations
- `MEDIUM` — balanced (recommended starting point)
- `HIGH` — aggressive; may produce false positives on legitimate content

> **Exam tip:** Content filters are applied **independently** to input and output. You can set output filtering stricter than input (e.g., let technical security questions in but block harmful technical details in the response).

---

#### 4.2.2 Denied Topics

Block conversations about **specific topics** you define in natural language:

```json
{
  "name": "competitor-products",
  "definition": "Questions or discussions about products or services offered by competitors",
  "examples": ["Is product X better than yours?", "What does CompanyY charge for this?"],
  "type": "DENY"
}
```

- Define up to **30 denied topics** per guardrail
- Each topic: a name, natural language definition, and up to 5 examples
- The FM behind Guardrails classifies whether the input/output matches any denied topic
- On match: blocked with a configurable denial message

**Use cases:** Block competitor discussion, legal topics requiring professional advice, politically sensitive topics, out-of-scope use cases.

---

#### 4.2.3 Sensitive Information Redaction (PII)

Automatically detect and handle **Personally Identifiable Information (PII)**:

**Built-in PII entity types:**

|Entity|Example|
|---|---|
|`NAME`|John Smith|
|`EMAIL`|john@example.com|
|`PHONE`|+1-555-0100|
|`US_SSN`|123-45-6789|
|`CREDIT_DEBIT_CARD_NUMBER`|4111 1111 1111 1111|
|`AWS_ACCESS_KEY`|AKIAIOSFODNN7EXAMPLE|
|`IP_ADDRESS`|192.168.1.1|
|`URL`|https://example.com|
|`AGE`|42 years old|
|`US_PASSPORT_NUMBER`|123456789|
|`DRIVER_ID`|D123-4567-8901|

**Actions per entity type:**

- `ANONYMIZE` — replace with a type placeholder: `{NAME}`, `{EMAIL}`, etc.
- `BLOCK` — block the entire request if PII detected

**Custom regex patterns** — define your own patterns for proprietary identifiers (employee IDs, policy numbers, etc.)

---

#### 4.2.4 Grounding Check (Hallucination Detection)

Validates that the **model's response is grounded** in the source context provided:

- **Grounding score**: measures how much of the response is supported by the retrieved context
- **Relevance score**: measures how relevant the retrieved context is to the user's query
- Configure **threshold** (0.0–1.0): responses below threshold are blocked
- Works with RAG pipelines — pass retrieved context as `grounding source`

```python
guardrail_config = {
    "groundingPolicyConfig": {
        "groundingThreshold": 0.7   # block if < 70% grounded
    }
}
```

**When to use:** Any RAG application where factual accuracy is critical (medical, legal, financial Q&A).

---

#### 4.2.5 Word Filters

Block specific words, phrases, or profanity:

- **Managed word list** — AWS-maintained profanity list (toggle on/off)
- **Custom word list** — up to 10,000 words/phrases; exact match or substring
- Applied to both input and output independently

---

### 4.3 Guardrail Versioning

- Guardrails support **versions** — create a snapshot of a guardrail configuration
- `DRAFT` — working version; changes here don't affect production
- **Version** (1, 2, 3...) — immutable snapshots; reference in production inference
- Update: make changes to DRAFT → create new version → update application to reference new version

---

### 4.4 Applying Guardrails

**With any Bedrock model (InvokeModel):**

```json
{
  "modelId": "anthropic.claude-3-sonnet-...",
  "guardrailIdentifier": "arn:aws:bedrock:...:guardrail/abc123",
  "guardrailVersion": "1",
  "trace": "ENABLED"
}
```

**With Knowledge Bases (RetrieveAndGenerate):**

```json
{
  "guardrailConfiguration": {
    "guardrailId": "abc123",
    "guardrailVersion": "1"
  }
}
```

**With Bedrock Agents:** Assign guardrail at agent creation; applied to all agent interactions automatically.

---

### 4.5 Guardrail Trace

Enable `trace: "ENABLED"` to get a detailed breakdown of guardrail decisions:

- Which policies were evaluated
- What was detected (entity type, confidence, topic match)
- What action was taken (BLOCKED, ANONYMIZED, PASSED)
- Useful for debugging and compliance auditing

---

### 4.6 Guardrails Pricing

- Charged per **1,000 text units** processed (input + output separately)
- Additional charge for **grounding check** (per KB of context evaluated)
- Grounding check is the most expensive component — use selectively

---

## 5. Building LLM Agents / Agentic AI with Bedrock Agents

### 5.1 What Is an Agent?

A Bedrock Agent is a managed **ReAct-pattern** orchestrator that:

1. **Reasons** about a user goal
2. **Selects and calls tools** (action groups)
3. **Observes** the result
4. **Iterates** until the goal is achieved or it cannot proceed
5. **Generates** a final response to the user

All orchestration (prompt construction, tool call parsing, loop control) is managed by Bedrock — you don't write the ReAct loop yourself.

---

### 5.2 Core Components

```
User Request
      ↓
┌──────────────────────────────────────────────┐
│               BEDROCK AGENT                  │
│                                              │
│  Foundation Model (reasoning engine)         │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │  System     │  │   Action Groups      │  │
│  │  Prompt     │  │  (tools / APIs)      │  │
│  │  (Orchestr.) │  │                      │  │
│  └─────────────┘  └──────────────────────┘  │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │  Knowledge  │  │      Memory          │  │
│  │  Bases      │  │  (session/long-term) │  │
│  └─────────────┘  └──────────────────────┘  │
│  ┌─────────────┐                            │
│  │  Guardrails │                            │
│  └─────────────┘                            │
└──────────────────────────────────────────────┘
      ↓
Response (+ trace of reasoning steps)
```

---

### 5.3 Action Groups

Action groups are the **tools** an agent can invoke. Each action group has:

- A **name and description** (shown to the FM so it knows when to use it)
- An **API schema** (OpenAPI 3.0 YAML/JSON) defining the functions, parameters, and return types
- A **Lambda function** that executes the actual logic

#### Action Group Types

|Type|Description|
|---|---|
|**Lambda-backed**|Agent calls a Lambda function; Lambda handles any backend logic (DB query, API call, computation)|
|**Return of Control**|Agent returns control and parameters to the calling application — app runs the action and passes result back|
|**Built-in: Code Interpreter**|Agent generates and executes Python code in a sandboxed environment; no Lambda needed|
|**Built-in: User Input**|Agent pauses and explicitly asks the user for a missing required parameter|

#### OpenAPI Schema Example

```yaml
openapi: "3.0.0"
info:
  title: "Inventory API"
  version: "1.0"
paths:
  /check-stock:
    get:
      summary: "Check current stock level for a product"
      parameters:
        - name: productId
          in: query
          required: true
          schema:
            type: string
      responses:
        "200":
          description: "Stock level"
```

#### Lambda Function Pattern

```python
def lambda_handler(event, context):
    action = event["actionGroup"]
    function = event["function"]
    parameters = event.get("parameters", [])

    # Extract params
    param_dict = {p["name"]: p["value"] for p in parameters}

    # Execute logic
    result = check_stock(param_dict["productId"])

    return {
        "actionGroup": action,
        "function": function,
        "functionResponse": {
            "responseBody": {
                "TEXT": {"body": str(result)}
            }
        }
    }
```

---

### 5.4 Orchestration & ReAct Loop (Detailed)

Bedrock Agents use a **system prompt** (the orchestration prompt) injected automatically. The ReAct loop proceeds:

```
Step 1 — THINK
  Agent FM receives: system prompt + conversation history + user query
  FM produces: reasoning text about what to do next

Step 2 — ACT (optional)
  FM decides to call a tool → generates structured function call
  Bedrock parses → invokes Lambda → waits for response

Step 3 — OBSERVE
  Lambda result injected back into context

Step 4 — THINK again
  FM reasons about result, decides if goal is achieved or more steps needed

Repeat Steps 2–4 up to maxAgentIterations (default 5, max 20)

Step 5 — RESPOND
  FM generates final natural language response
```

**Agent Trace** — enable to see every Thought → Action → Observation step for debugging:

- `PRE_PROCESSING_TRACE` — input validation
- `ORCHESTRATION_TRACE` — each ReAct step with full FM reasoning
- `POST_PROCESSING_TRACE` — output formatting
- `GUARDRAIL_TRACE` — guardrail decisions

---

### 5.5 Agent Memory

#### Session Memory (Short-Term)

- Maintains conversation context **within a session** (session ID scoped)
- Agent remembers what was said earlier in the same conversation
- Automatically managed; clears when session ends or times out

#### Long-Term Memory (Across Sessions)

- Summarizes and persists key facts from past sessions
- Stored in a **managed memory store** (backed by Bedrock infrastructure)
- At the start of a new session, relevant past facts are retrieved and injected into the system prompt
- Enable via `memoryConfiguration` in agent definition
- Memory types: `SESSION_SUMMARY` — summarizes past conversations

```python
memory_config = {
    "enabledMemoryTypes": ["SESSION_SUMMARY"],
    "storageDays": 30   # how long to retain memory
}
```

---

### 5.6 Knowledge Base Integration with Agents

- Attach one or more Bedrock Knowledge Bases to an agent
- During reasoning, the agent **autonomously decides when to query the KB** based on the user's question
- No explicit action group needed — KB retrieval is a native agent capability
- Configure: which KB, retrieval instructions (natural language hint to FM), max retrieved results

```
Agent reasoning: "The user asked about refund policies. I should check the company knowledge base."
→ KB retrieve: "refund policy"
→ Top-3 chunks returned
→ Agent incorporates into response
```

---

### 5.7 Agent Aliases & Versions

|Concept|Description|
|---|---|
|**Draft**|Working version; used during development; not for production|
|**Version**|Immutable snapshot of agent configuration (FM, action groups, KB, instructions)|
|**Alias**|Named pointer to a version; use aliases in production — update alias to new version without changing application code|
|**Routing Config**|An alias can route traffic across multiple versions by % (for A/B testing)|

**Best practice:** Never reference `DRAFT` in production; always create a version and alias.

---

### 5.8 Prompt Override (Advanced)

Bedrock Agents use four built-in prompts you can **override** with custom templates:

|Prompt|When Used|Customization Use Case|
|---|---|---|
|**Pre-processing**|Before main orchestration; validates and classifies user input|Add domain-specific input validation|
|**Orchestration**|The main ReAct reasoning prompt|Add custom personas, reasoning constraints, tool usage instructions|
|**Knowledge Base response generation**|Formats KB retrieval results|Custom citation format, response structure|
|**Post-processing**|Formats final response before returning to user|Enforce output format, add disclaimers|

Provide custom prompts as **XML-formatted Bedrock prompt templates** stored inline or in S3.

---

### 5.9 Multi-Agent Collaboration (Supervisor Pattern)

Bedrock supports **multi-agent architectures** where a supervisor agent orchestrates sub-agents:

```
User
  ↓
Supervisor Agent (high-level planning and routing)
  ├── Sub-Agent A: HR Policy Expert (KB: HR documents)
  ├── Sub-Agent B: IT Support Agent (Action: ServiceNow API)
  └── Sub-Agent C: Finance Agent (Action: SAP query + KB: Finance docs)
```

- Supervisor invokes sub-agents via **inline agent action groups**
- Each sub-agent is a fully independent Bedrock Agent with its own FM, KB, and tools
- Supervisor reasons about which sub-agent to call and synthesizes results
- **Collaboration mode:** `SUPERVISOR` or `SUPERVISOR_ROUTER` (LLM-based routing vs explicit routing)

---

### 5.10 Inline Agents (Runtime Configuration)

- Define agent instructions, action groups, and KB associations **at invocation time** rather than statically
- Use `InvokeInlineAgent` API instead of `InvokeAgent`
- Enables **dynamic agent behavior** — same Bedrock infrastructure but different tools per user/session
- Use case: multi-tenant SaaS where each tenant has different tools and data sources

---

### 5.11 Code Interpreter Action Group

- Enable Python code execution **without a Lambda function**
- Agent generates Python code → Bedrock executes in a sandboxed environment → returns stdout/result
- Capabilities: data analysis, chart generation, math computation, string manipulation, CSV parsing
- Security: sandboxed; no internet access; no persistent state between calls
- Input files: pass files to the agent session → code interpreter can read them
- Output: text results + optionally generated files (images, CSVs)

**Ideal for:** Data analysis agents, financial calculation agents, report generation agents.

---

### 5.12 Return of Control (ROC)

- Agent identifies needed action and its parameters → **returns to the calling application** instead of invoking Lambda
- Application executes the action using its own infrastructure/credentials
- Application returns result to agent via `InvokeAgent` with `returnControlInvocationResults`
- **When to use:** Actions that require user confirmation in the UI, actions requiring specific credentials the Lambda shouldn't hold, highly latency-sensitive actions

---

## 6. Bedrock Flows (Prompt Flows)

### 6.1 What Are Bedrock Flows?

A **visual orchestration tool** for building deterministic multi-step GenAI workflows without writing application code.

```
[Input Node]
      ↓
[Condition Node] — route based on input type
      ├── [Prompt Node] — LLM call for classification
      │         ↓
      │   [Iterator Node] — process list items
      │         ↓
      │   [Knowledge Base Node] — retrieve relevant docs
      │         ↓
      │   [Prompt Node] — generate grounded response
      └── [Lambda Node] — fallback to custom logic
              ↓
[Output Node]
```

### 6.2 Node Types

|Node|Purpose|
|---|---|
|**Input / Output**|Entry and exit points of the flow|
|**Prompt**|Call any Bedrock FM with a defined prompt template|
|**Knowledge Base**|Retrieve from a Bedrock KB|
|**Agent**|Invoke a Bedrock Agent|
|**Lambda**|Run a Lambda function|
|**Condition**|Branch based on boolean or string conditions|
|**Iterator**|Process each item in a list; collect results|
|**Collector**|Aggregate iterator outputs back into a list|
|**Storage**|Read/write to S3|

### 6.3 Flows vs Agents

|Dimension|Bedrock Agents|Bedrock Flows|
|---|---|---|
|Control flow|**Dynamic** (LLM decides next step)|**Deterministic** (predefined graph)|
|Complexity|Higher (handles ambiguous, multi-step goals)|Lower (structured, predictable workflows)|
|Auditability|Trace-based|Visual graph; easy to audit|
|Latency|Variable (multi-step LLM reasoning)|More predictable|
|Best for|Autonomous task completion, complex reasoning|Structured pipelines, consistent workflows|

---

## 7. Key Exam Scenarios & Decision Framework

### Choosing Between RAG vs Fine-Tuning vs Prompt Engineering

```
Does the model need access to frequently updated or private data?
  YES → RAG (Knowledge Bases)

Does the model need to match a very specific output style or format?
  YES → Fine-tuning

Does the model perform poorly on domain-specific terminology?
  YES → Continued Pre-training → then Fine-tuning

Does prompt engineering already achieve acceptable results?
  YES → Stick with prompt engineering (cheapest, fastest)

Is the use case fully automatable with external tool calls?
  YES → Bedrock Agents

Is the workflow deterministic and structured?
  YES → Bedrock Flows
```

### Guardrail Configuration by Use Case

|Use Case|Key Guardrail Config|
|---|---|
|Customer service bot|Denied topics (competitors), content filters (MEDIUM), PII anonymization|
|Medical Q&A|Grounding check (threshold 0.8+), content filters (HIGH for misconduct), no PII in output|
|Internal HR chatbot|PII anonymization (NAME, SSN, DOB), denied topics (legal advice)|
|Code generation assistant|Prompt attack filter (HIGH), custom word filter (credential patterns)|
|Financial advisor bot|Grounding check, denied topics (specific investment recommendations), ANONYMIZE financial IDs|

### Vector Store Selection

|Requirement|Best Choice|
|---|---|
|Easiest setup, no infra management|OpenSearch Serverless|
|Already using Aurora PostgreSQL|Aurora + pgvector|
|Combine graph relationships + vectors|Neptune Analytics|
|Ultra-low latency (sub-ms)|Redis Enterprise|
|Highest scale, managed SaaS|Pinecone|
|Mixed document + vector queries|MongoDB Atlas|

### Chunking Strategy Selection

|Document Type|Best Chunking Strategy|
|---|---|
|General web content, articles|Fixed-size (512 tokens, 10% overlap)|
|Long reports, research papers|Hierarchical (parent 2K / child 256)|
|Mixed-topic documents|Semantic chunking|
|Short FAQs, product descriptions|No chunking|
|Proprietary formats (XML, JSON, custom)|Lambda-based custom chunking|
|Legal / financial contracts|Hierarchical|