## Amazon Comprehend

**What it is:** Fully managed NLP service — no ML experience needed.

| Capability                         | Detail                                                                       |
| ---------------------------------- | ---------------------------------------------------------------------------- |
| **NER (Named Entity Recognition)** | Extracts entities — people, places, dates, organizations, quantities, brands |
| **Sentiment Analysis**             | Classifies text as Positive, Negative, Neutral, or Mixed                     |
| **Key Phrase Extraction**          | Pulls out the most important phrases from text                               |
| **Language Detection**             | Identifies the language of the input text                                    |
| **PII Detection**                  | Identifies and can redact personal information                               |
| **Topic Modelling**                | Groups a large collection of documents into topics automatically             |
| **Syntax Analysis**                | Parts of speech tagging (noun, verb, adjective etc.)                         |

### Comprehend Custom

| Feature                       | Detail                                                                               |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| **Custom Classification**     | Train a model to classify documents into your own defined categories                 |
| **Custom Entity Recognition** | Train a model to detect domain-specific entities (e.g. product codes, medical terms) |
| **Training data required**    | You provide labelled examples first                                                  |
| **Multi-label support**       | A document can belong to multiple classes                                            |
| **Cross-account sharing**     | Custom models can be shared across AWS accounts                                      |

**Exam scenarios:**

- _Categorise customer support emails automatically_ → Comprehend Custom Classification
- _Extract medical terms from clinical notes_ → Comprehend Custom Entity Recognition
- _Detect if product reviews are positive or negative_ → Comprehend Sentiment Analysis

---

## Amazon Translate

**What it is:** Neural machine translation service for converting text between languages at scale.

| Feature                       | Detail                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------- |
| **Use case**                  | Localising websites, apps, and content for different regions/demographics       |
| **Scale**                     | Handles large volumes efficiently in batch or real-time                         |
| **Custom Terminology**        | You can provide a glossary so brand names/terms are never mistranslated         |
| **Formality setting**         | Can control formal vs informal tone in output                                   |
| **Active Custom Translation** | Fine-tune translation output with parallel data (your own translation examples) |

**Exam scenario:** _A global e-commerce company wants to serve product descriptions in 20 languages_ → **Translate + S3 batch job**

---

## Amazon Transcribe

**What it is:** Automatic Speech Recognition (ASR) — converts audio/speech into text.

| Feature                     | Detail                                                                       |
| --------------------------- | ---------------------------------------------------------------------------- |
| **ASR Engine**              | Deep learning based, handles accents and background noise                    |
| **PII/PHI Redaction**       | Automatically detects and removes sensitive info from transcripts            |
| **Auto Language Detection** | Identifies the spoken language without you specifying it                     |
| **Speaker Diarisation**     | Labels who said what in a multi-speaker conversation                         |
| **Custom Vocabulary**       | Add domain-specific words (medical terms, product names) to improve accuracy |
| **Custom Language Model**   | Train on your own text data for highly domain-specific transcription         |
| **Toxicity Detection**      | Detects harassment, hate speech, profanity using tone, pitch, and text cues  |
| **Streaming transcription** | Real-time transcription via WebSocket                                        |

**Exam scenarios:**

- _Medical dictation with clinical terminology_ → Transcribe + Custom Vocabulary / Custom Language Model
- _Call centre compliance — detect abusive language_ → Transcribe Toxicity Detection
- _Auto-generate subtitles for videos_ → Transcribe → S3

---

## Amazon Polly

**What it is:** Text-to-Speech (TTS) service — converts text into natural-sounding audio.

|Feature|Detail|
|---|---|
|**Standard voices**|Pre-built voices across many languages|
|**Neural TTS (NTTS)**|More natural, human-like speech quality|
|**Lexicons**|Define how specific words are pronounced (e.g. "www" → "world wide web")|
|**SSML support**|Speech Synthesis Markup Language — control pace, pitch, pauses, emphasis, whisper|
|**Speech Marks**|Metadata about when each word/sentence is spoken (useful for lip-sync or highlighting)|
|**Brand voice**|Custom voice creation for a company (enterprise feature)|

**Exam scenario:** _Accessibility feature — read out article content_ → **Polly with NTTS voices**

---

## Amazon Rekognition

**What it is:** Computer vision service for analysing images and videos.

|Capability|Detail|
|---|---|
|**Object & Scene Detection**|Labels objects, scenes, activities in images/video|
|**Facial Analysis**|Age range, emotions, gender, glasses, pose estimation|
|**Facial Search**|Compare faces against a collection (1:N search)|
|**Text Detection**|Reads text inside images (OCR)|
|**Celebrity Recognition**|Identifies public figures|
|**Content Moderation**|Detects inappropriate content (nudity, violence, etc.)|
|**PPE Detection**|Detects safety gear in workplace images|
|**Video Analysis**|All above capabilities extended to video with timestamps|
|**Custom Labels**|Train with a few hundred images to detect your own custom objects|

### Key Integration for MLA

- Can integrate with **Augmented AI (A2I)** to route low-confidence detections to human review

**Exam scenarios:**

- _Flag unsafe content uploaded by users_ → Rekognition Content Moderation + A2I
- _Find all images in a library containing a specific person_ → Rekognition Facial Search
- _Detect safety vest compliance on a factory floor_ → Rekognition PPE Detection or Custom Labels

---

## Amazon Lex

**What it is:** Build conversational chatbots using voice and text — same technology powering Alexa.

| Feature            | Detail                                                               |
| ------------------ | -------------------------------------------------------------------- |
| **Intents**        | What the user wants to do (e.g. BookFlight, CheckBalance)            |
| **Slots**          | Parameters the bot collects (e.g. date, destination)                 |
| **Fulfilment**     | Lambda is invoked to fulfil the intent once all slots are filled     |
| **Voice + Text**   | Supports both input modes                                            |
| **Multi-language** | Supports multiple languages in the same bot                          |
| **Integration**    | Works with Connect (call centres), Slack, Facebook Messenger, Twilio |
|                    |                                                                      |

**Exam scenario:** _Build a customer service bot that books appointments and checks order status_ → **Lex + Lambda**

---

## Amazon Personalize

**What it is:** Fully managed real-time recommendation system — same tech as Amazon.com recommendations.

|Recipe Type|Use Case|
|---|---|
|**USER_PERSONALIZATION**|Recommend items tailored to a specific user|
|**PERSONALIZED_RANKING**|Re-rank a list of items for a specific user|
|**POPULAR_ITEMS**|Recommend trending/popular items (no user history needed)|
|**RELATED_ITEMS**|"Customers also viewed" style recommendations|
|**USER_SEGMENTATION**|Segment users by behaviour|

|Feature|Detail|
|---|---|
|**Cold start**|Handles new users and new items with exploration strategies|
|**Real-time events**|Ingests clickstream data in real-time to update recommendations|
|**Contextual recommendations**|Can factor in context like device, time of day, location|
|**Filters**|Exclude already-purchased items, out-of-stock items, etc.|

**Exam scenario:** _E-commerce site wants personalised product recommendations for each user_ → **Personalize USER_PERSONALIZATION recipe**

---

## Amazon Textract

**What it is:** Extracts text, forms, and tables from scanned documents — goes beyond basic OCR.

|Feature|Detail|
|---|---|
|**Raw text extraction**|Reads printed and handwritten text|
|**Form extraction**|Extracts key-value pairs (e.g. Name: John, DOB: 01/01/1990)|
|**Table extraction**|Preserves table structure from documents|
|**Query-based extraction**|Ask specific questions about the document (e.g. "What is the invoice total?")|
|**Medical Textract**|Specialised for medical forms and clinical documents|
|**Integration**|Works with A2I for human review of low-confidence extractions|

**Exam scenario:** _Automatically process thousands of scanned loan application forms_ → **Textract → Lambda → DynamoDB**

---

## Amazon Kendra

**What it is:** Intelligent enterprise document search powered by ML — understands natural language queries.

|Feature|Detail|
|---|---|
|**Natural language search**|Ask questions in plain English, not just keyword search|
|**Fact extraction**|Pulls direct answers from documents, not just relevant documents|
|**Incremental learning**|Learns from user feedback and interactions over time|
|**Data sources**|S3, SharePoint, Confluence, Salesforce, RDS, OneDrive, and more|
|**Document types**|PDF, HTML, Word, PowerPoint, FAQs|
|**Access control**|Respects document-level permissions|
|**Custom tuning**|Boosting and tuning relevance for specific queries|

**Exam scenario:** _Internal knowledge base search for employees across thousands of policy documents_ → **Kendra**

---

## Amazon Augmented AI (A2I)

**What it is:** Human-in-the-loop review system for ML predictions that fall below a confidence threshold.

```
ML Model makes prediction
        ↓
High confidence → Sent directly to application
Low confidence → Routed to A2I Human Review Workflow
        ↓
Human reviewer makes decision
        ↓
Result sent to application + can be used to retrain model
```

|Feature|Detail|
|---|---|
|**Built-in integrations**|Rekognition (content moderation), Textract (document extraction)|
|**Custom workflows**|Build human review for any ML model output|
|**Workforce options**|Amazon Mechanical Turk, private internal team, or AWS Marketplace vendors|
|**Confidence threshold**|You define what "low confidence" means|

**Exam scenario:** _Medical image analysis — auto-approve high confidence, send unclear scans to radiologists_ → **A2I custom workflow**

---

## AWS Hardware for AI

|Chip|Purpose|Key Detail|
|---|---|---|
|**AWS Trainium**|**Training** large deep learning models|Optimised for 100B+ parameter models, up to 50% cost reduction vs GPU training|
|**AWS Inferentia**|**Inference / Serving** trained models|High throughput, low latency, low cost per inference|

**Memory trick:** **Train**ium = **Train**ing. **Infer**entia = **Infer**ence.

**Exam scenario:** _Reduce cost of serving a large language model at scale_ → **Inferentia**

---

## Amazon Q Business

**What it is:** Enterprise AI assistant — a chatbot built on your company's own internal knowledge and data.

|Feature|Detail|
|---|---|
|**Underlying tech**|Powered by Amazon Bedrock under the hood|
|**Data Connectors**|S3, RDS, Aurora, Redshift, Microsoft 365, Google Drive, Confluence, Salesforce, and more|
|**Plugins**|Jira, ServiceNow, Salesforce — can take actions, not just answer questions|
|**Actions**|Can do things like submit time-off requests, create tickets, query databases|
|**Admin Controls**|Guardrails for what the assistant can/cannot say or do|
|**IAM Controls**|User-level permissions — users only see documents they have access to|
|**Grounding**|Answers are grounded in company data, not hallucinated|

---

## Amazon Q Apps

**What it is:** Allows non-technical users to build lightweight internal apps using natural language — no code required.

|Feature|Detail|
|---|---|
|**Input**|Natural language description of what the app should do|
|**Data**|Leverages company's internal data connected via Q Business|
|**Output**|Shareable mini-app (form, workflow, summariser)|
|**Use case**|Rapid internal tooling without developer involvement|

**Exam scenario:** _HR team wants a leave policy Q&A tool without engineering resources_ → **Q Apps on top of Q Business**

---

## Amazon Q Developer

**What it is:** AI coding assistant and AWS expert — think GitHub Copilot but AWS-native.

|Feature|Detail|
|---|---|
|**Code generation**|Suggests and generates code inline in IDE|
|**AWS expertise**|Answers questions about AWS services, architecture, best practices|
|**Account-aware**|Can query your actual AWS account (cost analysis, resource inventory)|
|**Security scanning**|Scans code for vulnerabilities|
|**Software agents**|Can autonomously implement features, write tests, do refactoring|
|**IDE support**|VS Code, JetBrains, Visual Studio, AWS Cloud9|
|**CLI support**|Works in terminal for AWS CLI assistance|

---

## Quick Reference — Which Service for What

|Scenario|Service|
|---|---|
|Sentiment / NER on text|**Comprehend**|
|Translate content to another language|**Translate**|
|Speech to text|**Transcribe**|
|Text to speech|**Polly**|
|Image / video analysis|**Rekognition**|
|Build a chatbot|**Lex**|
|Product recommendations|**Personalize**|
|Extract data from scanned forms/docs|**Textract**|
|Search across enterprise documents|**Kendra**|
|Human review for low-confidence predictions|**A2I**|
|Company internal AI assistant|**Q Business**|
|No-code internal app builder|**Q Apps**|
|AI coding + AWS assistant|**Q Developer**|
|Train massive models cheaply|**Trainium**|
|Serve models cheaply at scale|**Inferentia**|

**Note:** When to use AI Managed service over custom models

| Signal in the question                                                                                                               | Likely answer                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Standard use case (image labels, text sentiment, translation, forecasting, recommendations) + no mention of custom/proprietary needs | **Managed AI service** (Rekognition, Comprehend, Translate, Forecast, Personalize, Textract, Transcribe) |
| Need for domain-specific model, unique data patterns, full control over architecture/features                                        | **Custom model** — SageMaker built-in algorithm or bring-your-own-model                                  |
| Need to minimize ML expertise/dev time, fast time-to-market                                                                          | **Managed AI service**                                                                                   |
| Requirement to fine-tune on proprietary data with specific business logic not covered by generic APIs                                | **Custom model**                                                                                         |