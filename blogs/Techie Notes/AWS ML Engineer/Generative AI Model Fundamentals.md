## 1. Transformer Architecture

### 1.1 Why Transformers?

Before Transformers (2017), sequential models (RNN, LSTM) dominated NLP. Their key limitations:

- **Sequential processing** — cannot parallelize across time steps during training
- **Long-range dependency problem** — even LSTMs struggle to retain information across very long sequences
- **Fixed context window** — information from step 1 is diluted by step 500

Transformers solve all three by replacing recurrence with **self-attention** — every token can directly attend to every other token in a single operation.

> **Original paper:** _"Attention Is All You Need"_ — Vaswani et al., 2017

---

### 1.2 High-Level Architecture

The original Transformer is an **Encoder-Decoder** architecture:

```
Input Tokens
      ↓
[Input Embedding + Positional Encoding]
      ↓
┌─────────────────────────┐
│        ENCODER          │  ← N stacked identical layers
│  Multi-Head Self-Attn   │
│  Add & Norm             │
│  Feed-Forward Network   │
│  Add & Norm             │
└─────────────────────────┘
      ↓ (encoder output = context vectors)
┌─────────────────────────┐
│        DECODER          │  ← N stacked identical layers
│  Masked Multi-Head Attn │  ← can only attend to past tokens
│  Add & Norm             │
│  Cross-Attention        │  ← attends to encoder output
│  Add & Norm             │
│  Feed-Forward Network   │
│  Add & Norm             │
└─────────────────────────┘
      ↓
[Linear + Softmax]
      ↓
Output Token Probabilities
```

---

### 1.3 Input Embedding & Positional Encoding

**Token Embedding:**

- Each input token (word / sub-word) is mapped to a dense vector of dimension `d_model` (e.g., 512 or 768)
- Learned during training via an embedding matrix of shape `[vocab_size × d_model]`

**Positional Encoding:**

- Transformers have no recurrence → no inherent sense of order
- Positional encoding adds a **position-specific signal** to each token embedding
- Original paper: fixed sinusoidal encoding — `PE(pos, 2i) = sin(pos / 10000^(2i/d_model))`
- Modern LLMs: learned positional embeddings, **RoPE** (Rotary Position Embedding), **ALiBi** (Attention with Linear Biases)
- Final input = Token Embedding + Positional Encoding

---

### 1.4 Tokenization

Before embeddings, raw text is converted to tokens:

|Method|Description|Example|
|---|---|---|
|**Word-level**|Each word is a token|"playing" → ["playing"]|
|**Character-level**|Each character is a token|"cat" → ["c", "a", "t"]|
|**BPE (Byte-Pair Encoding)**|Iteratively merges frequent character pairs; used by GPT|"playing" → ["play", "ing"]|
|**WordPiece**|Similar to BPE but merges based on likelihood; used by BERT|"playing" → ["play", "##ing"]|
|**SentencePiece**|Language-agnostic; works on raw bytes; used by LLaMA|Model-independent tokenization|

- **Vocabulary size** is typically 32K–100K tokens
- LLMs consume **tokens**, not words — billing and context limits are measured in tokens
- Rule of thumb: ~1 token ≈ 0.75 words (English); other languages may use more tokens per word

---

## 2. Self-Attention Mechanism

### 2.1 Intuition

Self-attention allows each token in a sequence to **weigh the importance of every other token** when building its representation. The word "bank" in "river bank" attends strongly to "river"; in "bank account" it attends strongly to "account."

### 2.2 Query, Key, Value (QKV)

Each input token embedding `x` is projected into three vectors via learned weight matrices:

|Vector|Role|Analogy|
|---|---|---|
|**Query (Q)**|What this token is looking for|A search query|
|**Key (K)**|What information this token offers|A document label|
|**Value (V)**|The actual content to retrieve if matched|The document content|

**Attention computation:**

```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) × V
```

Step by step:

1. `QKᵀ` — dot product between query and all keys → **raw attention scores** (how relevant is each token)
2. `/ √d_k` — scale by root of key dimension to prevent softmax saturation (gradients vanish if scores are too large)
3. `softmax(...)` — convert scores to a probability distribution → **attention weights** (sum to 1)
4. `× V` — weighted sum of value vectors → **context-aware representation** for this token

### 2.3 Multi-Head Attention

Instead of one set of QKV projections, run `h` attention heads in parallel with different projections:

```
head_i = Attention(Q·W_i^Q, K·W_i^K, V·W_i^V)
MultiHead(Q,K,V) = Concat(head_1,...,head_h) · W^O
```

- Each head can **specialize** in different relationship types (syntax, coreference, semantic roles)
- Typical values: h = 8–128 heads; `d_k = d_model / h` per head
- Output dimension is the same as input → residual connections work cleanly

### 2.4 Masked Self-Attention (Decoder)

- In the decoder, each token may only attend to **previous tokens** (autoregressive generation)
- Achieved by adding a **causal mask** — setting future position scores to `-∞` before softmax → softmax outputs 0 for those positions
- This prevents the model from "cheating" by looking ahead during training

### 2.5 Cross-Attention (Encoder-Decoder)

- Queries come from the **decoder**, Keys and Values come from the **encoder output**
- Allows the decoder to attend to the full input sequence at every generation step
- Used in: machine translation, summarization, any seq2seq task

### 2.6 Attention Complexity

- Standard self-attention is **O(n²)** in sequence length — quadratic memory and compute
- For a sequence of 1000 tokens: 1M attention scores; for 10K tokens: 100M scores
- Modern solutions: **Sparse Attention**, **Flash Attention** (IO-aware exact attention), **Longformer**, **BigBird** (local + global attention)

---

## 3. Feed-Forward Network & Other Components

### 3.1 Position-wise Feed-Forward Network (FFN)

After attention, each token's representation passes through an identical 2-layer MLP independently:

```
FFN(x) = max(0, xW₁ + b₁)W₂ + b₂
```

- Inner dimension `d_ff` is typically 4× `d_model` (e.g., 2048 for d_model=512)
- Applies non-linearity (ReLU or GELU) between the two linear layers
- **GELU** (Gaussian Error Linear Unit) is preferred in modern LLMs — smoother than ReLU

### 3.2 Layer Normalization

- Applied after attention and FFN sub-layers (Pre-LN vs Post-LN debate)
- **Post-LN** (original paper): normalize after residual → less stable training
- **Pre-LN** (modern default): normalize before attention/FFN → more stable, easier to train deep models

### 3.3 Residual (Skip) Connections

- `Output = LayerNorm(x + Sublayer(x))` — adds the input directly to the sublayer output
- Prevents vanishing gradients; allows gradient to flow directly through the addition
- Essential for training very deep Transformers (100+ layers)

---

## 4. Attention-Based Neural Network Applications

### 4.1 Encoder-Only Models (Bidirectional)

- Full self-attention in both directions — each token sees the entire context
- Pre-trained with **Masked Language Modeling (MLM)** — randomly mask 15% of tokens; model predicts them
- Best for **understanding** tasks: classification, NER, question answering, semantic similarity

|Model|Notes|
|---|---|
|**BERT**|Foundational encoder-only; bidirectional attention|
|**RoBERTa**|BERT trained longer, more data, no NSP objective; generally better|
|**ALBERT**|Parameter sharing across layers; much smaller footprint|
|**DistilBERT**|Knowledge-distilled BERT; 60% smaller, 97% performance|
|**DeBERTa**|Disentangled attention (position and content separate); best GLUE scores|

### 4.2 Decoder-Only Models (Autoregressive)

- Causal (masked) self-attention — each token sees only previous tokens
- Pre-trained with **Causal Language Modeling (CLM)** — predict the next token given all previous
- Best for **generation** tasks: text generation, code, chat, reasoning

|Model Family|Notes|
|---|---|
|**GPT-2 / GPT-3 / GPT-4**|OpenAI; scaled up CLM; emergent few-shot ability|
|**LLaMA / LLaMA 2 / LLaMA 3**|Meta; open-weights; widely fine-tuned|
|**Mistral / Mixtral**|Efficient; Mixtral uses Mixture of Experts (MoE)|
|**Amazon Titan**|AWS native; available on Bedrock|
|**Claude**|Anthropic; trained with Constitutional AI|
|**Falcon**|Technology Innovation Institute|

### 4.3 Encoder-Decoder Models (Seq2Seq)

- Encoder processes input with full bidirectional attention; decoder generates output autoregressively
- Pre-trained with **Span Corruption** (T5 style) — mask spans of text; model reconstructs
- Best for: translation, summarization, question generation, dialogue

|Model|Notes|
|---|---|
|**T5**|"Text-to-Text Transfer Transformer" — frames all tasks as text-to-text|
|**BART**|Denoising autoencoder; strong for summarization|
|**mT5**|Multilingual T5|
|**Flan-T5**|T5 instruction-tuned on many tasks; strong zero-shot/few-shot|

### 4.4 Vision Transformers (ViT)

- Splits image into **fixed-size patches** (e.g., 16×16 pixels); each patch is flattened and embedded
- Patches treated as tokens; standard Transformer encoder applied
- **Class token** (CLS) prepended; its output used for image classification
- Competitive with CNNs on large datasets; data-hungry

### 4.5 Multimodal Applications

|Application|Architecture|
|---|---|
|**Image Captioning**|CNN encoder (image) + Transformer decoder (text)|
|**Visual QA**|Transformer processes image patches + text jointly|
|**Text-to-Image**|Diffusion model guided by Transformer text encoder (CLIP, DALL-E)|
|**Speech Recognition**|Transformer encoder processes mel-spectrograms (Whisper)|
|**Code Generation**|Decoder-only Transformer trained on code (Codex, CodeLlama)|

---

## 5. How GPT Works

### 5.1 Architecture

GPT (Generative Pre-trained Transformer) is a **decoder-only** Transformer:

- N layers of: Masked Multi-Head Self-Attention → LayerNorm → FFN → LayerNorm
- No encoder; no cross-attention
- **Autoregressive generation** — outputs one token at a time, each token appended to the context for the next step

### 5.2 Pre-training

- Trained on massive text corpora (internet text, books, code) via **Causal Language Modeling**
- Objective: maximize `P(x_t | x_1, x_2, ..., x_{t-1})` for every position simultaneously during training
- Trained with **teacher forcing** — ground truth tokens used as input during training (not previously generated tokens)
- Scale drives capability: GPT-3 = 175B parameters; trained on ~570GB of filtered text

### 5.3 The Scaling Laws (Chinchilla)

- **Kaplan et al. (2020):** model performance scales as a power law with compute, data, and parameters
- **Hoffmann et al. (2022, Chinchilla):** for a fixed compute budget, optimal training uses ~**20 tokens per parameter**
    - GPT-3 (175B) was undertrained; optimal would need ~3.5T tokens
    - LLaMA 2 (7B) trained on 2T tokens — deliberately overtrained for inference efficiency

### 5.4 Inference / Generation

**Decoding strategies:**

|Strategy|Mechanism|Use Case|
|---|---|---|
|**Greedy Decoding**|Always pick highest probability token|Fast; repetitive; low quality|
|**Beam Search**|Maintain top-k partial sequences; pick best complete sequence|Translation, summarization|
|**Temperature Sampling**|Divide logits by T before softmax; T>1 → more random, T<1 → more deterministic|Creative generation|
|**Top-K Sampling**|Sample from top K most probable tokens only|Balanced quality + diversity|
|**Top-P (Nucleus) Sampling**|Sample from smallest token set whose cumulative probability ≥ p|Preferred for open-ended generation|
|**Repetition Penalty**|Downweight logits of previously generated tokens|Reduces repetition|

**Key inference parameters:**

- `temperature` — controls randomness (0 = deterministic, 1 = standard, >1 = creative)
- `top_p` — nucleus sampling threshold (typical: 0.9–0.95)
- `top_k` — number of candidates in top-k sampling
- `max_tokens` / `max_new_tokens` — max output length
- `stop_sequences` — halt generation at specific strings

### 5.5 Context Window

- The **context window** is the maximum number of tokens the model can process at once (input + output combined)
- GPT-2: 1024 tokens; GPT-4: 128K tokens; Claude 3: 200K tokens
- Information outside the context window is **not accessible** — no memory by default
- Patterns for handling long context: **chunking**, **retrieval-augmented generation (RAG)**, **sliding window attention**

### 5.6 Emergent Abilities

Capabilities that appear suddenly at scale and were absent in smaller models:

- **Few-shot learning** — learn a task from a few examples in the prompt with no weight updates
- **Chain-of-thought reasoning** — model reasons step-by-step when prompted
- **In-context learning** — adapt to new tasks from prompt examples alone
- **Instruction following** — follow natural language directives without task-specific fine-tuning

---

## 6. LLM Key Terms

### 6.1 Foundational Concepts

|Term|Definition|
|---|---|
|**Parameters**|Learnable weights of the model; "7B model" = 7 billion parameters|
|**Tokens**|Atomic units of text processed by the model; ~0.75 words on average|
|**Context window**|Max tokens processed in a single forward pass (input + output)|
|**Prompt**|The input text given to the model to elicit a response|
|**Completion**|The model's output text|
|**Temperature**|Sampling randomness control (0 = greedy, 1 = default, >1 = creative)|
|**Hallucination**|Model generates plausible-sounding but factually incorrect content|
|**Grounding**|Connecting model outputs to verified external knowledge (RAG, tools)|

### 6.2 Prompt Engineering Techniques

|Technique|Description|
|---|---|
|**Zero-shot**|Ask model to do task with no examples|
|**Few-shot**|Provide 2–10 input/output examples in the prompt|
|**Chain-of-Thought (CoT)**|Ask model to reason step-by-step ("Let's think step by step")|
|**Self-Consistency**|Sample multiple reasoning chains; take majority vote|
|**ReAct**|Reason + Act — model interleaves thinking and tool calls|
|**System Prompt**|Persistent instructions that set model behavior and persona|

### 6.3 RAG (Retrieval-Augmented Generation)

- Augments LLM with **real-time retrieval** from an external knowledge base
- Solves: knowledge cutoff, hallucination, domain-specific knowledge, private data

**RAG Pipeline:**

```
User Query
    ↓
Query Embedding (embedding model)
    ↓
Vector Similarity Search (vector DB: FAISS, OpenSearch, Pinecone)
    ↓
Top-K Relevant Chunks Retrieved
    ↓
[Retrieved context + Original query] → LLM
    ↓
Grounded Response
```

**AWS RAG Stack:** Amazon Bedrock Knowledge Bases + OpenSearch Serverless (vector engine) + Titan Embeddings

### 6.4 Agents

- LLM-powered systems that can **reason, plan, and use tools** to accomplish multi-step goals
- **ReAct loop:** Thought → Action (tool call) → Observation → Thought → ...
- Tools: web search, code execution, database queries, API calls, file I/O
- **AWS:** Amazon Bedrock Agents — managed agent runtime with tool integration and memory

### 6.5 Model Performance Metrics

|Metric|What It Measures|Higher = Better?|
|---|---|---|
|**Perplexity**|How "surprised" the model is by the test set; `exp(cross-entropy loss)`|No (lower = better)|
|**BLEU**|n-gram overlap between generated and reference text (translation)|Yes|
|**ROUGE**|Recall-oriented n-gram overlap (summarization)|Yes|
|**BERTScore**|Semantic similarity using BERT embeddings (vs. n-gram)|Yes|
|**MMLU**|Multi-task knowledge benchmark (57 subjects)|Yes|
|**HumanEval**|Functional correctness of generated code|Yes|

---

## 7. Fine-Tuning & Transfer Learning with Transformers

### 7.1 Transfer Learning Paradigm

```
Pre-training (massive data, massive compute, general language understanding)
        ↓
Foundation Model (general-purpose representation)
        ↓
Fine-tuning / Adaptation (task-specific data, much less compute)
        ↓
Task-Specific Model
```

- Pre-training is done **once** by large research organizations
- Fine-tuning is done by practitioners on task-specific data
- Transfer learning works because lower layers learn universal features (syntax, semantics); upper layers are task-specific

### 7.2 Full Fine-Tuning

- Update **all model parameters** on a labeled task-specific dataset
- Highest performance but requires:
    - Substantial labeled data (thousands to millions of examples)
    - Large GPU memory (must store model + optimizer states + gradients)
    - Risk of **catastrophic forgetting** — overwrites pre-trained knowledge

### 7.3 Parameter-Efficient Fine-Tuning (PEFT)

Fine-tune a **small subset of parameters** while keeping most of the pre-trained model frozen.

#### 7.3.1 LoRA (Low-Rank Adaptation)

- Inserts **low-rank decomposition matrices** into attention weight matrices
- Instead of updating `W` (d×d), trains two small matrices `A` (d×r) and `B` (r×d) where `r << d`
- `ΔW = B × A`; merged into original weights at inference (no latency overhead)
- **Rank r** is a hyperparameter — typical values: 4, 8, 16, 64
- Reduces trainable parameters by **10,000×** compared to full fine-tuning
- **QLoRA** — quantize the frozen base model to 4-bit; run LoRA on top → fine-tune 65B models on a single GPU

#### 7.3.2 Adapter Layers

- Insert small trainable **bottleneck FFN layers** inside each Transformer block
- Only adapter parameters are updated; original weights frozen
- Slightly slower inference than LoRA (extra layers at inference time)

#### 7.3.3 Prefix Tuning / Prompt Tuning

- Prepend a sequence of **trainable soft tokens** to the input
- Only these virtual tokens are updated; model weights fully frozen
- Requires no modification to model architecture
- Less effective than LoRA for smaller models but scalable for very large ones

#### 7.3.4 PEFT Comparison

|Method|Trainable Params|Inference Overhead|Memory|Best For|
|---|---|---|---|---|
|Full Fine-Tuning|100%|None|Very High|Maximum performance, sufficient data|
|Adapter|0.5–5%|Small (extra layers)|Low|Moderate resource constraint|
|LoRA|0.1–1%|None (merged)|Very Low|Most practical PEFT method|
|QLoRA|0.1–1%|None|Extremely Low|Consumer GPU fine-tuning|
|Prefix Tuning|<0.1%|Slight (longer input)|Minimal|Frozen model, soft prompting|

### 7.4 Instruction Fine-Tuning (IFT)

- Fine-tune on a dataset of `(instruction, response)` pairs
- Teaches the model to **follow natural language instructions** across many task types
- Often combined with **RLHF** for alignment

### 7.5 RLHF (Reinforcement Learning from Human Feedback)

The alignment technique used to create ChatGPT, Claude, and similar models:

```
Step 1 — Supervised Fine-Tuning (SFT)
  Fine-tune on high-quality (prompt, response) pairs from human demonstrators

Step 2 — Reward Model Training
  Collect human preferences: show two model outputs, ask which is better
  Train a reward model to predict human preference score

Step 3 — PPO Fine-Tuning (Reinforcement Learning)
  Use PPO (Proximal Policy Optimization) to optimize the LLM
  to maximize the reward model's score
  + KL divergence penalty to prevent drifting too far from SFT model
```

**DPO (Direct Preference Optimization)** — newer, simpler alternative to RLHF:

- Skips the reward model entirely
- Directly optimizes the policy on preference pairs with a classification-style loss
- Simpler, more stable, increasingly preferred

### 7.6 Domain Adaptation vs Task Adaptation

|Type|What It Does|Example|
|---|---|---|
|**Domain Adaptation**|Continue pre-training on domain-specific unlabeled text|Train on medical literature to improve medical understanding|
|**Task Adaptation (Fine-Tuning)**|Fine-tune on labeled examples of a specific task|Fine-tune on sentiment-labeled reviews for sentiment classification|
|**Both**|Domain adapt first, then task fine-tune|Common for specialized domains (legal, medical, financial)|

### 7.7 When to Use Each Approach

|Approach|When to Use|
|---|---|
|**Prompt Engineering / RAG**|Model already capable; need up-to-date or private knowledge|
|**Fine-tuning (PEFT/LoRA)**|Need specific style, format, or domain; labeled data available|
|**Full Fine-tuning**|Maximum performance critical; ample data and compute|
|**Pre-training from scratch**|Entirely new domain/language with no related base model|

---

## 8. AWS Foundation Models & SageMaker JumpStart for Gen AI

### 8.1 Amazon Bedrock

Bedrock is AWS's **fully managed generative AI service** — access foundation models via API without managing infrastructure.

**Key concepts:**

|Concept|Detail|
|---|---|
|**Model Access**|Request access to each FM family separately; some auto-approved, some require justification|
|**Invocation**|`InvokeModel` (synchronous), `InvokeModelWithResponseStream` (streaming)|
|**Pricing**|Per input/output token (on-demand) or **Provisioned Throughput** (reserved capacity)|
|**No data retention**|Inputs/outputs not used to train Anthropic/other base models|
|**VPC support**|Bedrock endpoints usable within VPC via PrivateLink|

### 8.2 Foundation Models Available on Bedrock

|Provider|Model Family|Strengths|
|---|---|---|
|**Anthropic**|Claude 3 (Haiku, Sonnet, Opus)|Long context, reasoning, safety|
|**Amazon**|Titan Text, Titan Embeddings, Titan Multimodal|Native AWS integration, embeddings|
|**Meta**|LLaMA 2, LLaMA 3|Open-weights; customizable|
|**Mistral AI**|Mistral 7B, Mixtral 8x7B|Efficient; MoE architecture|
|**Cohere**|Command, Embed|Enterprise NLP, embeddings|
|**Stability AI**|Stable Diffusion XL|Image generation|
|**AI21 Labs**|Jurassic|Long-form text generation|

### 8.3 Amazon Titan Models (Exam Focus)

|Model|Use Case|
|---|---|
|**Titan Text Express**|Fast, cost-efficient text generation|
|**Titan Text Premier**|Higher quality text generation|
|**Titan Text Lite**|Lightest, lowest cost|
|**Titan Embeddings G1 / V2**|Text embeddings for RAG, semantic search|
|**Titan Multimodal Embeddings**|Joint image + text embeddings|
|**Titan Image Generator**|Text-to-image generation|

### 8.4 Bedrock Key Features

#### Knowledge Bases (Managed RAG)

- Upload documents to S3; Bedrock handles chunking, embedding, and indexing into **OpenSearch Serverless** (vector store)
- Query via `RetrieveAndGenerate` API — end-to-end RAG in one call
- Also supports: Aurora PostgreSQL, Redis Enterprise, Pinecone, MongoDB Atlas as vector stores

#### Bedrock Agents

- Orchestrates multi-step tasks using **ReAct pattern**
- Define tools as **Action Groups** backed by Lambda functions or OpenAPI schemas
- Built-in **memory**: session memory (within conversation) and persistent memory (across sessions)
- Integrates with Knowledge Bases for RAG within agent reasoning

#### Bedrock Guardrails

- Content filtering for: **hate speech, violence, sexual content, prompt injection, PII**
- **Topic denial** — block conversations about specific topics (e.g., competitor products)
- **Grounding check** — verify model responses are grounded in retrieved context (hallucination detection)
- **Sensitive info redaction** — automatically mask PII in inputs and outputs
- Applied to any model on Bedrock; independent of the model itself

#### Model Evaluation

- Automatic evaluation using predefined metrics (ROUGE, BERTScore, accuracy)
- Human evaluation via **Amazon Mechanical Turk** integration or private reviewer teams
- **Model Evaluation on Bedrock** — compare multiple FMs on your own prompt dataset

#### Bedrock Model Customization

- **Fine-tuning** — upload labeled training data (JSONL); Bedrock handles the fine-tuning job on a managed cluster
- **Continued Pre-training** — provide domain-specific unlabeled text; extends pre-training
- Fine-tuned models stored as a private model version; invoked same as base models
- Supports: Titan, Cohere Command models for fine-tuning

### 8.5 SageMaker JumpStart for Gen AI

|Feature|Detail|
|---|---|
|**Model Hub**|300+ pre-trained models including LLaMA 2/3, Falcon, Mistral, Stable Diffusion, Flan-T5|
|**One-click deploy**|Deploy pre-configured endpoint with auto-selected instance type|
|**Fine-tuning**|Fine-tune supported models (LLaMA, Falcon, etc.) via UI or SDK with your own dataset|
|**Solution Templates**|End-to-end notebooks for QA, summarization, text-to-image, etc.|
|**Private Deployment**|Models run in your AWS account — data never leaves your VPC|
|**Pricing**|Pay for underlying SageMaker instance + optional fine-tuning compute|

**JumpStart vs Bedrock:**

|Dimension|SageMaker JumpStart|Amazon Bedrock|
|---|---|---|
|**Infrastructure**|You manage endpoints and instances|Fully managed, serverless|
|**Model access**|Deploy to your VPC; run in your account|API-based; model runs in Bedrock's managed infra|
|**Customization**|Full control: fine-tune, PEFT, quantize|Managed fine-tuning (limited model selection)|
|**Latency control**|Full control over instance type and scaling|Less direct control|
|**Cost model**|Instance-based (always-on or auto-scaling)|Token-based (on-demand) or provisioned|
|**Best for**|Teams needing full control or complex fine-tuning|Rapid prototyping and production API access|

### 8.6 Amazon CodeWhisperer / Amazon Q

|Service|Role|
|---|---|
|**Amazon Q Developer** (formerly CodeWhisperer)|AI coding assistant — code completion, security scanning, test generation, inline suggestions in IDE|
|**Amazon Q Business**|Enterprise chatbot over internal documents — integrates with S3, SharePoint, Salesforce, Jira|
|**Amazon Q in QuickSight**|Natural language BI — generate dashboards from plain English queries|

### 8.7 AWS PartyRock

- **No-code** generative AI app builder on Bedrock
- Build and share AI-powered apps in the browser
- Educational / rapid prototyping tool; not for production workloads

---

## 9. Diffusion Models (Stable Diffusion on AWS)

### 9.1 How Diffusion Models Work

```
Forward Process (Training):
  Image → gradually add Gaussian noise over T steps → pure noise

Reverse Process (Generation):
  Pure noise → trained model predicts and removes noise at each step → clean image
```

- The model learns to **denoise** — predicts the noise added at each step
- **U-Net** architecture with attention layers typically used as the denoiser
- **CLIP** text encoder converts text prompt to embedding that guides denoising (conditioning)
- **Latent Diffusion Models (LDM)** — operate in compressed latent space (not pixel space) → much faster (Stable Diffusion)

### 9.2 Key Concepts

|Term|Definition|
|---|---|
|**Guidance Scale (CFG)**|How strongly to follow the text prompt (1 = ignore, 7–12 = balanced, >15 = strict/distorted)|
|**Inference Steps**|More steps → higher quality but slower (typical: 20–50)|
|**Seed**|Random seed for reproducibility|
|**Negative Prompt**|What to exclude from the image|
|**ControlNet**|Add structural conditioning (edge maps, depth, pose) on top of Stable Diffusion|

### 9.3 Stable Diffusion on AWS

- Available via **Amazon Bedrock** (Stability AI models) — `stability.stable-diffusion-xl-v1`
- Available via **SageMaker JumpStart** — deploy SDXL as a SageMaker endpoint
- Input: JSON with `text_prompts`, `cfg_scale`, `steps`, `seed`
- Output: Base64-encoded image bytes

---

## 10. Key Gen AI Exam Scenarios

### Choosing the Right AWS Service

|Need|AWS Service|
|---|---|
|Quick FM API access, no infra management|Amazon Bedrock|
|RAG over private documents|Bedrock Knowledge Bases|
|Multi-step agent with tools|Bedrock Agents|
|Content moderation for LLM outputs|Bedrock Guardrails|
|Fine-tune open-source LLM with full control|SageMaker JumpStart|
|Code generation in IDE|Amazon Q Developer|
|Enterprise Q&A over internal knowledge|Amazon Q Business|
|Text-to-image|Bedrock (Stability AI) or JumpStart|
|Evaluate multiple FMs|Bedrock Model Evaluation|
|Embed text for semantic search / RAG|Amazon Titan Embeddings|

### Choosing Adaptation Strategy

|Situation|Approach|
|---|---|
|LLM doesn't know your private data|RAG (Bedrock Knowledge Bases)|
|LLM doesn't follow your output format / style|Fine-tuning (LoRA or managed Bedrock fine-tuning)|
|LLM answers incorrectly for your domain|Domain adaptation (continued pre-training) then fine-tune|
|Reduce hallucination|RAG + Guardrails grounding check|
|Reduce cost at high throughput|Provisioned Throughput on Bedrock|
|Reduce latency for real-time chat|Streaming (`InvokeModelWithResponseStream`)|

### Hallucination Mitigation

|Technique|How It Helps|
|---|---|
|**RAG**|Grounds answers in retrieved verified documents|
|**Lower temperature**|Reduces randomness; model more conservative|
|**Bedrock Guardrails grounding check**|Compares output against retrieved context; blocks ungrounded claims|
|**Chain-of-thought prompting**|Forces step-by-step reasoning; reduces confident wrong answers|
|**Self-consistency**|Multiple samples; majority vote|
|**Model fine-tuning**|Teach domain-specific factual knowledge|

---

## 11. Quick Reference Summary

### Transformer Component Cheat Sheet

|Component|Purpose|
|---|---|
|Token Embedding|Convert tokens to dense vectors|
|Positional Encoding|Inject sequence order information|
|Multi-Head Self-Attention|Contextualize each token against all others|
|Masked Attention|Prevent decoder from seeing future tokens|
|Cross-Attention|Decoder attends to encoder output|
|FFN|Per-token non-linear transformation|
|Layer Norm|Stabilize training across depths|
|Residual Connection|Prevent vanishing gradient; enable depth|

### Model Architecture Decision Tree

```
Task requires understanding (classification, NER, QA)?
  → Encoder-only (BERT, RoBERTa, DeBERTa)

Task requires generation (chat, summarization, code)?
  → Decoder-only (GPT, LLaMA, Mistral, Titan)

Task is seq2seq (translation, structured summarization)?
  → Encoder-Decoder (T5, BART, Flan-T5)

Working with images?
  → CNN for extraction OR ViT for full attention
  → Diffusion model for generation
```

### Fine-Tuning Decision Tree

```
Do you need up-to-date or private factual knowledge?
  YES → RAG (no fine-tuning needed)

Do you need specific output format, style, or behavior?
  YES → Fine-tuning (LoRA/PEFT preferred)

Do you have labeled task-specific data (1K+ examples)?
  YES → Task fine-tuning
  NO  → Few-shot prompting or prompt engineering first

Do you have limited GPU memory?
  YES → QLoRA or Bedrock managed fine-tuning
  NO  → Full fine-tuning or LoRA
```