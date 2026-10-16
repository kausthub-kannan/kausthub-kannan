## 1. Dimensions of Responsible AI

### 1.1 Explainability

Explainability is the degree to which the **internal mechanics and decisions** of an ML model can be understood by humans — both developers and end users.

#### Why It Matters (Exam Context)

- Regulatory compliance (GDPR "right to explanation", EU AI Act, HIPAA)
- Identifying and correcting bias
- Debugging unexpected model behavior
- Building trust with end users and stakeholders

#### Explainability Techniques

|Technique|Scope|How It Works|
|---|---|---|
|**SHAP** (SHapley Additive exPlanations)|Global + Local|Assigns each feature a contribution value based on game-theoretic Shapley values; model-agnostic|
|**LIME** (Local Interpretable Model-agnostic Explanations)|Local|Fits a simple interpretable model (linear) around a specific prediction|
|**Integrated Gradients**|Local|For neural networks; attributes prediction to input features by integrating gradients along a path|
|**Partial Dependence Plots (PDP)**|Global|Shows marginal effect of one or two features on predicted outcome|
|**Feature Importance** (tree-based)|Global|Built-in to tree models (XGBoost, RF); measures impurity reduction per feature|
|**Attention Weights**|Local (LLMs/Transformers)|Visualizes which tokens the model attended to; not always faithful to true reasoning|

#### Explainability vs Complexity Trade-off

```
High Explainability ◄─────────────────────────────► High Performance
                                                      (usually)
Linear Regression → Decision Tree → Random Forest → Gradient Boosting → Deep Neural Network

Interpretable by design          ←────────────────────── Requires post-hoc explanation tools
```

- **Intrinsic interpretability:** Linear models, shallow decision trees — explainable by design
- **Post-hoc explainability:** SHAP, LIME applied after training to black-box models
- **Key exam principle:** Choose the **simplest model that meets performance requirements** — if a logistic regression achieves acceptable accuracy, there is no justification for deploying a deep neural network in a regulated context

---

### 1.2 Privacy and Security

#### Data Privacy

|Risk|Mitigation|
|---|---|
|Training data contains PII|Anonymize, pseudonymize, or tokenize before training|
|Model memorizes training data|Differential privacy during training; limit memorization via regularization|
|Data leakage via model outputs|Output filtering (Guardrails PII redaction); prompt injection detection|
|Unauthorized data access|IAM policies, S3 bucket policies, VPC endpoints, encryption at rest and in transit|

#### Privacy Techniques

- **Differential Privacy** — add calibrated statistical noise to training data or gradients so that the model cannot be used to infer whether a specific individual was in the training set
- **Federated Learning** — train models across distributed data sources without centralizing raw data; only model gradients are shared
- **Data Minimization** — collect and use only the data strictly necessary for the task
- **Anonymization** — remove all direct and indirect identifiers (k-anonymity, l-diversity)
- **Tokenization / Pseudonymization** — replace sensitive values with non-sensitive placeholders (reversible, unlike anonymization)

#### Security Controls for ML Systems

|Layer|Controls|
|---|---|
|**Data**|S3 encryption (SSE-S3, SSE-KMS), VPC endpoints, bucket policies, Macie for PII detection|
|**Training**|SageMaker training in VPC (no internet access), IAM execution roles with least privilege|
|**Model artifacts**|Encrypt S3 model artifacts with KMS; restrict access to model registry|
|**Inference**|HTTPS endpoints only; VPC-hosted endpoints; API Gateway + WAF for public endpoints|
|**Audit**|CloudTrail for all API calls; SageMaker Model Monitor for inference monitoring|
|**Supply chain**|Verify base model provenance; scan Docker images for CVEs (ECR image scanning)|

#### Model Inversion & Membership Inference Attacks

- **Model Inversion** — attacker queries model to reconstruct training data
- **Membership Inference** — attacker determines whether a specific record was in the training set
- Mitigations: differential privacy, output prediction confidence rounding, rate limiting inference API

---

### 1.3 Safety

Safety in AI means preventing models from causing **physical, psychological, financial, or societal harm**.

#### Categories of Safety Risk

|Category|Example|
|---|---|
|**Direct harm**|Medical AI giving incorrect dosing; autonomous vehicle making unsafe decision|
|**Facilitated harm**|LLM providing instructions for dangerous activities|
|**Discriminatory harm**|Loan model denying credit based on protected attributes|
|**Psychological harm**|Chatbot encouraging self-harm; addictive engagement patterns|
|**Societal harm**|Large-scale generation of misinformation; deepfakes|

#### Safety Mitigations

- **Red-teaming** — adversarial testing by a dedicated team attempting to elicit harmful outputs; mandatory before deployment of high-risk AI systems
- **Constitutional AI (Anthropic Claude)** — model critiques and revises its own outputs against a set of principles
- **RLHF + safety reward models** — human labelers rate outputs for safety; reward model trained; PPO optimizes against it
- **Output filtering (Guardrails)** — detect and block harmful content post-generation
- **Human-in-the-loop (HITL)** — route high-risk or low-confidence decisions to humans before action is taken
- **Staged rollout** — canary/shadow deployment to limit blast radius of unsafe model behavior
- **Kill switch / circuit breaker** — ability to instantly disable or roll back a deployed model

#### AWS Safety Context

- **Bedrock Guardrails** — content filters for hate, violence, sexual content, prompt attacks
- **Bedrock Guardrails Denied Topics** — block specific unsafe conversation directions
- **SageMaker Clarify** — detect bias that can lead to discriminatory outcomes

---

### 1.4 Controllability

Controllability is the ability of humans to **understand, intervene in, and override** AI system behavior at any point.

#### Dimensions of Controllability

|Dimension|Description|
|---|---|
|**Interruptibility**|Ability to pause or stop the AI system during execution|
|**Correctability**|Ability to update or retrain the model when it behaves incorrectly|
|**Overridability**|Human can override any AI decision before it takes effect|
|**Auditability**|Complete log of decisions, inputs, and outputs for review|
|**Scope limitation**|AI system operates only within a defined action space|

#### AWS Controllability Tools

|Tool|Controllability Feature|
|---|---|
|**SageMaker Pipelines**|Step-by-step approval gates; conditional execution|
|**SageMaker Model Registry**|Manual approval/rejection before deployment|
|**Bedrock Agents HITL**|`ReturnOfControl` — pause agent and require human input|
|**A2I (Augmented AI)**|HITL loop for any ML prediction requiring human review|
|**Bedrock Guardrails**|Hard policy enforcement on all model inputs and outputs|
|**CloudTrail + EventBridge**|Full audit trail; trigger alerts on anomalous model behavior|
|**SageMaker Model Monitor**|Alerts when model quality degrades; enables rollback|

#### HITL Patterns

```
High Confidence → Automated action
Low Confidence → Route to human reviewer → Reviewed decision → Feedback to model
```

- HITL does not mean reviewing every prediction — it means routing **edge cases and low-confidence predictions** to humans
- Human decisions fed back as labeled data → continuous improvement loop

---

### 1.5 Veracity and Robustness

#### Veracity — Can the Model Tell the Truth?

|Problem|Description|Mitigation|
|---|---|---|
|**Hallucination**|Model generates plausible but false information|RAG, grounding checks (Bedrock Guardrails), lower temperature|
|**Outdated knowledge**|Model knowledge cutoff means facts may be stale|RAG with current data sources|
|**Confident wrong answers**|Model expresses high confidence when incorrect|Calibration techniques; uncertainty quantification|
|**Sycophancy**|Model tells users what they want to hear rather than the truth|RLHF with truthfulness reward; adversarial testing|
|**Citation fabrication**|Model invents fake sources|Enforce retrieval-grounded responses; citation verification|

#### Robustness — Does the Model Behave Consistently Under Pressure?

|Threat|Description|Mitigation|
|---|---|---|
|**Distributional shift**|Input data at inference differs from training distribution|Model Monitor data quality checks; retrain on updated data|
|**Adversarial inputs**|Carefully crafted inputs designed to fool the model|Adversarial training; input validation; Guardrails prompt attack filter|
|**Prompt injection**|Malicious instructions embedded in user input or retrieved documents|Bedrock Guardrails prompt attack filter (HIGH strength)|
|**Jailbreaking**|User attempts to bypass safety constraints|Constitutional AI; Guardrails; red-teaming|
|**Covariate shift**|Feature distributions change over time|Model Monitor feature drift detection; scheduled retraining|
|**Label shift**|Output class distribution changes over time|Model Monitor prediction drift; retrain with new labels|

#### Robustness Testing

- **A/B testing** — compare model versions on live traffic
- **Shadow testing** — run new model in parallel; compare outputs without serving to users
- **Stress testing** — evaluate under extreme inputs, edge cases, high load
- **Slice analysis** — evaluate performance broken down by subgroups (age, geography, device) to detect disparate failure modes

---

### 1.6 Governance

Governance is the **organizational framework** of policies, processes, roles, and tools that ensure AI systems are developed and operated responsibly.

#### Governance Pillars

|Pillar|Components|
|---|---|
|**Accountability**|Named ownership of each model; clear escalation paths|
|**Transparency**|Model cards; audit logs; explainability reports|
|**Compliance**|Regulatory alignment (GDPR, HIPAA, SOC 2); data residency controls|
|**Risk Management**|Risk classification of models; tiered review process by risk level|
|**Lifecycle Management**|Version control; deprecation policies; retraining schedules|
|**Auditability**|Immutable logs of all training data, model versions, predictions|

#### Model Risk Tiers

- **High risk:** Healthcare diagnosis, credit scoring, criminal justice, autonomous vehicles — require the most rigorous review, HITL, explainability
- **Medium risk:** Recommendation engines, content moderation — moderate review; monitor closely
- **Low risk:** Internal tools, search ranking — lighter governance process

---

## 2. AWS Tools for Responsible AI

### 2.1 Amazon SageMaker Clarify

SageMaker Clarify provides **bias detection, model explainability, and evaluation** integrated into the SageMaker ecosystem.

#### Bias Detection

**Pre-training bias** — measured before model training on the raw dataset:

|Metric|What It Measures|
|---|---|
|**Class Imbalance (CI)**|Imbalance in representation of different demographic groups in the training data|
|**Difference in Proportions of Labels (DPL)**|Difference in positive label rates between groups (e.g., loan approval rate for Group A vs Group B)|
|**Kullback-Leibler (KL) Divergence**|Distribution divergence between groups in a feature|
|**Jensen-Shannon (JS) Divergence**|Symmetric version of KL; bounded between 0 and 1|
|**Total Variation Distance (TVD)**|Maximum difference in probability distributions between groups|

**Post-training bias** — measured after model training on predictions:

|Metric|What It Measures|
|---|---|
|**Difference in Positive Proportions of Predictions (DPPP)**|Difference in positive prediction rates between groups|
|**Disparate Impact (DI)**|Ratio of positive prediction rates between groups; `DI < 0.8` triggers "80% rule" (legal threshold)|
|**Accuracy Difference**|Difference in accuracy between demographic groups|
|**Recall Difference**|Difference in recall — does model miss positives more for one group?|
|**Specificity Difference**|Difference in specificity — false alarm rate disparity|
|**Treatment Equality (TE)**|Ratio of false negatives to false positives per group|

> **Exam tip:** Pre-training metrics tell you if the **data** is biased. Post-training metrics tell you if the **model's decisions** are biased. Both need to be evaluated.

#### Explainability with Clarify

- Uses **SHAP values** to explain individual predictions and global feature importance
- Generates an **explainability report** stored in S3
- Works with: tabular models (XGBoost, linear), NLP (token-level attribution), computer vision (image attribution)
- Integrated into SageMaker Processing Jobs — runs as a processing job alongside or after training

#### Model Evaluation with Clarify

- Evaluate FMs on standard benchmarks: **accuracy, robustness, toxicity, stereotyping, factual knowledge**
- Evaluation datasets: built-in curated datasets or bring your own
- Generates a structured **evaluation report** for model selection and compliance documentation
- Supports: Bedrock models, SageMaker endpoints, custom model inference scripts

#### Clarify + Model Monitor Integration

- Clarify generates a **bias baseline** from training data
- Model Monitor runs a scheduled **bias monitoring job** against live inference data
- Compares live prediction distributions against baseline → emits CloudWatch metrics
- Alert when `DI < 0.8` or other bias thresholds are breached in production

---

### 2.2 SageMaker Model Monitor

Model Monitor continuously monitors deployed models for **quality degradation** in production.

#### Four Monitor Types (Exam Critical)

|Monitor|Detects|Baseline|
|---|---|---|
|**Data Quality**|Feature distribution drift (covariate shift) — input features differ from training|Statistics computed from training data|
|**Model Quality**|Prediction metric degradation (accuracy, F1, AUC dropping)|Ground truth labels compared to predictions|
|**Bias Drift**|Model predictions becoming more biased over time|Clarify bias baseline|
|**Feature Attribution Drift**|SHAP feature importance rankings shifting over time|Clarify explainability baseline|

#### How It Works

```
Training Data → Clarify / Monitor baselining job → Baseline statistics stored in S3
       ↓
Endpoint with Data Capture enabled → Logs inference input/output to S3
       ↓
Scheduled monitoring job → Compares captured data to baseline
       ↓
Violations stored in S3 → CloudWatch metrics emitted
       ↓
CloudWatch Alarm → SNS notification / EventBridge trigger / Auto-rollback
```

#### Key Configuration

- **Data Capture** — must enable on endpoint to log requests/responses to S3
- **Capture percentage** — what % of traffic to log (e.g., 10–100%)
- **Monitoring schedule** — cron expression (e.g., hourly, daily)
- **Constraint file** — auto-generated from baseline; defines acceptable ranges per feature
- **Statistics file** — computed distributions from baseline dataset

---

### 2.3 Amazon Augmented AI (A2I)

A2I provides **Human-in-the-Loop (HITL)** workflows for ML predictions that require human review.

#### How A2I Works

```
ML Prediction
      ↓
Confidence check (above/below threshold?)
      ├── HIGH confidence → Automated decision (no human needed)
      └── LOW confidence → A2I creates human review task
                                ↓
                    Human reviewer (Amazon Mechanical Turk / private workforce / vendor)
                                ↓
                    Reviewed label sent back to application
                                ↓
                    Optionally: reviewed data used to retrain model
```

#### Key Components

|Component|Description|
|---|---|
|**Human Review Workflow**|Defines task UI, worker pool, conditions that trigger review|
|**Task UI**|Custom or built-in Liquid template for reviewing images, text, documents|
|**Worker Pool**|Amazon Mechanical Turk (crowdsourced), Private Workforce (internal employees), AWS Marketplace (vendor)|
|**Activation Conditions**|Confidence threshold, random sampling %, or always review|
|**Output**|Human decision stored in S3 as JSON|

#### Built-In A2I Task Types

- **Amazon Textract** — review document extraction results
- **Amazon Rekognition** — review image moderation decisions
- **Custom** — wrap any ML model (SageMaker endpoint, Bedrock, external)

#### A2I vs Labeling Ground Truth

|Service|Purpose|
|---|---|
|**SageMaker Ground Truth**|Label raw data to **create** training datasets|
|**Amazon A2I**|Review and correct **model predictions** in production (post-deployment HITL)|

---

### 2.4 SageMaker ML Governance

#### 2.4.1 SageMaker Role Manager

- **Purpose:** Simplify IAM permission management for ML personas without requiring deep IAM expertise
- Three predefined ML personas:
    - **Data Scientist** — access to notebooks, training jobs, model development; no deployment
    - **MLOps Engineer** — deployment, monitoring, model registry management; no training data access
    - **Data Engineer** — data pipeline access, S3, Glue, Athena; no model access
- Administrators can create **custom personas** by composing predefined permission sets
- Enforces **least privilege** by default — data scientists cannot accidentally deploy to production; MLOps cannot access raw training data
- Generates IAM policies automatically from selected permissions

#### 2.4.2 Model Cards

A **Model Card** is a structured documentation artifact for an ML model capturing everything needed to understand, evaluate, and govern its use.

**Standard Model Card contents:**

|Section|Contents|
|---|---|
|**Model Overview**|Name, version, type, owner, use case, creation date|
|**Intended Use**|Approved use cases; out-of-scope uses; target users|
|**Training Details**|Dataset description, features, training algorithm, hyperparameters|
|**Evaluation Results**|Metrics (accuracy, F1, AUC, RMSE); evaluation dataset; bias metrics|
|**Ethical Considerations**|Known biases; limitations; fairness assessment|
|**Caveats and Recommendations**|Known failure modes; conditions where model should not be used|
|**Status**|`Active`, `Retired`, `Deprecated`|

- Stored in SageMaker and linked to a model in the **Model Registry**
- Can be exported as PDF for regulatory filing or stakeholder distribution
- Support **model card versions** — updated as the model evolves

#### 2.4.3 Model Dashboard

- Centralized **single-pane-of-glass** view of all models across an AWS account
- Displays: model status, endpoint health, monitoring status, drift alerts, bias metrics, pending approvals
- Links to: Model Registry version, Model Card, active monitoring jobs, CloudWatch metrics
- Supports filtering by model group, status, risk level
- **Exam use case:** "How would you give an ML governance team visibility into all deployed models?" → SageMaker Model Dashboard

---

### 2.5 Bedrock Model Evaluation

Bedrock provides managed model evaluation for Foundation Models:

|Evaluation Type|Method|Use Case|
|---|---|---|
|**Automatic**|Algorithmic metrics (ROUGE, METEOR, BERTScore, accuracy) on a labeled dataset|Fast, reproducible; good for classification and summarization|
|**Human**|Send output pairs to human reviewers (internal workforce or MTurk)|Subjective quality, tone, safety, instruction-following|
|**LLM-as-judge**|Use a separate FM to evaluate outputs of the target FM|Scalable subjective evaluation; requires a strong judge model|

**Evaluation dimensions:**

- **Accuracy** — factual correctness against ground truth
- **Robustness** — performance on adversarial / edge case prompts
- **Toxicity** — rate of harmful or offensive outputs
- **Stereotyping** — presence of stereotyped associations
- **Factual Knowledge** — correct recall of world knowledge

---

## 3. ML Design Principles

### 3.1 The Ten Principles

#### 1. Assign Ownership

- Every model, dataset, pipeline, and endpoint must have a **named human owner** and a **team owner**
- Ownership responsibilities: model performance, retraining decisions, incident response, regulatory compliance
- Documented in the Model Card under "Model Owner"
- Without ownership, no one is accountable when a model fails in production

#### 2. Provide Protection (Security Controls)

- Apply **defense in depth** — multiple independent security layers
- IAM least-privilege roles for every pipeline stage (data access, training, deployment, inference)
- Encrypt data at rest (KMS) and in transit (TLS 1.2+)
- Network isolation: training and inference in **VPC with no internet access**; use VPC endpoints for AWS services
- Enable **CloudTrail** for full audit of every API call
- Scan model artifacts and Docker images for vulnerabilities
- Rotate credentials; never hardcode secrets in training scripts (use **AWS Secrets Manager**)

#### 3. Enable Resiliency (Fault Tolerance and Recoverability)

- **Fault tolerance:** Design systems to continue operating when individual components fail
    - Multi-AZ SageMaker endpoints; auto-scaling; load balancing
    - Managed Spot Training with checkpointing — recover from instance interruption
- **Recoverability:** Ability to restore correct behavior after a failure
    - SageMaker Model Registry — always have a previously approved model version ready for rollback
    - Deployment Guardrails auto-rollback on CloudWatch alarm
    - Checkpoint training jobs — resume from last saved state
    - Regular backup of training data and model artifacts to versioned S3

#### 4. Enable Reusability

- Build modular pipelines where components (data processing, feature engineering, evaluation) can be **reused across projects**
- Store reusable components in SageMaker Pipeline steps or as shared SageMaker Processing containers
- Feature Store for reusable, precomputed features — compute once, use many
- Parameterize all pipeline steps to avoid hardcoding project-specific values

#### 5. Version Control

- **Code:** Git (CodeCommit, GitHub, GitLab) — every training script, configuration, and infrastructure definition
- **Data:** S3 versioning, DVC (Data Version Control), SageMaker Feature Store with time-travel queries
- **Models:** SageMaker Model Registry — every trained model registered with version, metrics, and lineage
- **Experiments:** SageMaker Experiments — track every training run, hyperparameter, metric
- **Infrastructure:** IaC via CloudFormation or CDK — version-controlled environment definitions
- **Goal:** Full reproducibility — given a model version, you can reconstruct exactly what data and code produced it

#### 6. Optimize Resources

- Right-size compute: match instance type to workload (memory-bound → m5; compute-bound → c5; GPU → p3/p4)
- Use **Managed Spot Training** for up to 90% cost savings on training (with checkpointing)
- Use **SageMaker Warm Pools** for iterative development to avoid cold-start overhead
- Use **SageMaker Training Compiler** to accelerate GPU utilization
- Auto-scale inference endpoints — don't over-provision; scale based on actual traffic
- Delete unused endpoints immediately — idle endpoints still incur cost

#### 7. Reduce Cost

- **Right-sizing:** Profile training jobs; use the smallest instance that meets time requirements
- **Spot instances:** Up to 90% training cost reduction
- **Serverless inference:** Use SageMaker Serverless Inference for infrequent traffic patterns
- **Batch Transform:** For offline scoring; no persistent endpoint; pay only per job
- **Bedrock on-demand vs Provisioned Throughput:** Use on-demand for variable traffic; Provisioned for predictable high-volume
- **Quantization:** Reduce model size (FP32 → INT8) for cheaper inference with minimal accuracy loss
- **Model distillation:** Train a smaller student model from a large teacher; cheaper inference
- **Monitor and alert on cost:** AWS Cost Explorer + Budgets alerts for ML workloads

#### 8. Enable Automation

- Automate the **full ML lifecycle** to reduce human error and accelerate iteration
- CI/CD for ML (MLOps):
    - Code commit → automated training job → evaluation → model registry registration → approval gate → deployment
- Trigger retraining automatically on: scheduled basis, data drift alert (Model Monitor), performance degradation
- **SageMaker Pipelines** — define the full ML pipeline as code; re-execute on trigger
- **EventBridge** — event-driven automation (model approved → trigger deployment)
- **Step Functions** — orchestrate complex multi-step workflows with error handling
- **Automated hyperparameter tuning (AMT)** — replace manual grid search with Bayesian optimization

#### 9. Enable Continuous Improvement

- ML models are **not static** — data distributions change; the world changes; models must adapt
- Continuous improvement loop:

```
Production inference
        ↓
Model Monitor detects drift or degradation
        ↓
Alert triggers retraining pipeline
        ↓
New model trained on updated data
        ↓
Evaluated against current production model (challenger vs champion)
        ↓
If challenger wins → staged rollout (Canary/Linear) → replace champion
        ↓
Old model version retained in registry for rollback
```

- **Human feedback loop:** Use A2I human reviews as labeled data for retraining
- **Active learning:** Selectively label the most informative unlabeled examples (high uncertainty predictions)
- Track model performance over time in SageMaker Experiments and Model Dashboard

#### 10. Minimize Environmental Impact

- ML training is computationally intensive; large models have significant carbon footprints
- **AWS sustainability measures:**
    - AWS operates with a commitment to **100% renewable energy** by 2025 (and beyond)
    - Use **AWS regions with higher renewable energy availability** for large training jobs (e.g., US East N. Virginia, EU Ireland)
    - AWS publishes a **Carbon Footprint Tool** — measure CO₂ emissions of your AWS workloads
- **ML-level measures:**
    - Prefer smaller, efficient models when accuracy requirements allow
    - Use **knowledge distillation** — smaller student models with large-model-quality outputs
    - Use **quantization** and **pruning** to reduce compute per inference
    - Use **Managed Spot Training** — fewer idle instances, more efficient use of existing hardware
    - Stop training early (early stopping) when the model has converged
    - Cache feature engineering outputs in **SageMaker Feature Store** — don't recompute the same features repeatedly

---

## 4. The ML Lifecycle

### 4.1 Full Cycle

```
Business Goal
      ↓
ML Problem Framing
      ↓
Data Collection & Processing
      ↓
Model Development (train, tune, evaluate)
      ↓
Deployment
      ↓
Monitoring
      ↓
(if degradation detected)
      ├──────────────────────► Model Development (retrain)
      └──────────────────────► Data Processing (reprocess with new data)
      ↓
Back to Business Goal (measure ROI, reassess)
```

Each arrow is bidirectional — failure or new information at any stage can send you back to an earlier stage.

---

### 4.2 Business Goal Identification

This is the **most important phase** — a technically excellent model solving the wrong problem delivers no value.

#### Key Activities

**1. Identify the Right Spot on the Explainability vs Complexity Spectrum**

- Regulatory environments (healthcare, finance, legal) may **mandate** explainable models regardless of performance
- Consumer-facing products prioritize performance; internal tools may tolerate less explainability
- Document the justification for model complexity in the Model Card
- If a simpler model achieves 95% of the performance of a complex one with full explainability, prefer the simpler model in regulated contexts

**2. Monitor Model Against Business Requirements**

- Define **business-level metrics** alongside ML metrics:

|ML Metric|Corresponding Business Metric|
|---|---|
|Precision / Recall|Cost of false positives vs false negatives (fraud costs, customer churn)|
|Latency (p99)|User experience SLA; revenue impact of slow predictions|
|Throughput|Peak transaction volume; Black Friday capacity|
|Model uptime|SLA agreement; regulatory availability requirement|

**3. Validate ML Data Permissions, Privacy, Software, and License Terms**

- Confirm data collection was **legally authorized** and consent obtained where required
- Check **data residency** requirements (EU data must stay in EU)
- Review **open-source model licenses** (Apache 2.0 allows commercial use; GPL may not)
- Verify **dataset licenses** (ImageNet: research only; Common Crawl: commercial ok with attribution)
- Check **third-party API terms** if scraping data or using external embeddings
- Document all data sources, licenses, and permissions in the Model Card

**4. Determine Key Performance Indicators (KPIs)**

Define KPIs before model development — not after:

|Category|Example KPIs|
|---|---|
|**Accuracy KPIs**|Recall ≥ 0.90 for fraud detection; RMSE ≤ $50 for price prediction|
|**Operational KPIs**|p99 latency ≤ 200ms; endpoint availability ≥ 99.9%|
|**Fairness KPIs**|Disparate Impact ≥ 0.8 across all demographic groups|
|**Safety KPIs**|Zero safety incidents per 100K predictions|
|**Cost KPIs**|Inference cost per prediction ≤ $0.001|

**5. Define Return on Investment (ROI) and Opportunity Cost**

```
ROI = (Value Generated by ML Solution - Total Cost of ML Solution)
      ─────────────────────────────────────────────────────────────
                     Total Cost of ML Solution
```

- **Value generated:** Revenue uplift, cost reduction, churn prevention, fraud avoided, manual labor replaced
- **Total cost:** Data labeling, compute (training + inference), engineering time, monitoring, retraining, governance overhead
- **Opportunity cost:** What else could those resources accomplish? Would a rules-based system suffice?
- **Break-even analysis:** How long before ML solution pays for its development cost?
- A high-accuracy model that costs more than the problem it solves is still a bad business decision

---

## 5. Responsible AI Quick Reference

### AWS Responsible AI Toolkit

|Tool|What It Does|Stage|
|---|---|---|
|**SageMaker Clarify**|Bias detection (pre/post-training), SHAP explainability, FM evaluation|Pre-training, Post-training, Monitoring|
|**SageMaker Model Monitor**|Data quality, model quality, bias drift, feature attribution drift alerts|Production monitoring|
|**Amazon A2I**|HITL for low-confidence predictions; human review workflows|Production inference|
|**Bedrock Guardrails**|Content filtering, topic denial, PII redaction, grounding check, word filters|Inference (LLM applications)|
|**Bedrock Model Evaluation**|Evaluate FMs on accuracy, toxicity, stereotyping, robustness|Model selection, compliance|
|**SageMaker Role Manager**|Least-privilege IAM persona management for ML teams|Team governance|
|**SageMaker Model Cards**|Structured model documentation; intended use; bias results|Lifecycle documentation|
|**SageMaker Model Dashboard**|Centralized model fleet visibility; monitoring status; alerts|Operations governance|
|**AWS CloudTrail**|Immutable audit log of all API calls|Compliance, security auditing|
|**AWS Macie**|PII detection in S3 training data|Data privacy|

### Bias Mitigation Workflow

```
1. Identify sensitive attributes (race, gender, age, etc.)
2. Run Clarify pre-training bias analysis → check CI, DPL metrics
3. Apply mitigation if needed:
   - Resample / reweight training data
   - Collect more data for underrepresented groups
   - Remove proxy features correlated with sensitive attributes
4. Train model
5. Run Clarify post-training bias analysis → check DI, recall difference
6. If DI < 0.8 → model fails fairness threshold → do not deploy
7. Deploy with Model Monitor bias job → alert if DI drifts below threshold
```

### Exam Scenario: Responsible AI

|Scenario|Answer|
|---|---|
|"Model is making biased loan decisions by demographic group"|SageMaker Clarify post-training bias → check Disparate Impact → apply reweighting or collect more data|
|"LLM producing harmful content in production"|Bedrock Guardrails content filters (HIGH strength on violence/hate); also add denied topics|
|"Need to explain individual credit decisions to regulators"|SageMaker Clarify SHAP local explainability; store explanation report per prediction|
|"Customer support bot hallucinating policy information"|Bedrock Knowledge Bases RAG + Guardrails grounding check (threshold ≥ 0.75)|
|"Data scientists are deploying models directly to prod without review"|SageMaker Role Manager (deny deployment permissions for data scientist persona) + Model Registry approval gate|
|"Track all model versions and who approved them"|SageMaker Model Registry + CloudTrail audit log|
|"Centralized view of all 50 deployed model health statuses"|SageMaker Model Dashboard|
|"Low-confidence fraud predictions need human review before action"|Amazon A2I with activation condition on confidence score threshold|
|"Legal requires a document explaining the model"|SageMaker Model Card — export as PDF|