## 1. Deployment Safeguards

### 1.1 Deployment Guardrails

Applies to **real-time** and **async** endpoints. Enables safe, controlled model rollouts via three traffic-shifting strategies:

| Mode            | How It Works                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **All-at-Once** | 100% of traffic shifts to the green (new) fleet immediately; blue (old) fleet is deleted only after green is confirmed healthy   |
| **Canary**      | A small portion of traffic (e.g., 5–10%) shifts to green first; blue is terminated only after green sustains healthy performance |
| **Linear**      | Traffic shifts to green incrementally in equal steps (e.g., 10% → 20% → ... → 100%) at defined intervals                         |


> **Blue = old/current model fleet | Green = new model fleet**

### 1.2 Auto Rollbacks

- Triggered automatically if CloudWatch alarms breach defined thresholds during a deployment
- Rolls traffic back to the blue fleet without manual intervention
- Works with all three guardrail modes

### 1.3 Shadow Tests

- Deploys a **shadow variant** alongside the live production variant
- Mirrors a percentage of live traffic to the shadow model — shadow responses are **not returned to the caller**
- Compares performance (latency, accuracy, error rate) between production and shadow
- Used to validate a new model in a production-like environment before promoting it to live traffic
- Monitor results in SageMaker and decide when to shift the model to production

---

## 2. SageMaker Docker Infrastructure

Every model in SageMaker — training and inference — is packaged and run as a **Docker container**.

### 2.1 Distributed Training

For distributed training across multiple machines:

- **Horovod** — ring-allreduce-based data parallelism (popular for TensorFlow/PyTorch)
- **Parameter Servers** — asynchronous gradient aggregation across workers

### 2.2 Docker Image Lifecycle

1. Write a `Dockerfile` defining the environment and entry point
2. Build the image locally or via CodeBuild
3. Push the image to **Amazon ECR**
4. Reference the ECR URI in SageMaker Training Job / Model definition

### 2.3 Directory Structure

**Training container expected layout:**

```
/opt/ml/
├── input/
│   ├── config/          # hyperparameters.json, resourceConfig.json
│   └── data/
│       └── <channel>/   # training data copied here (File mode)
├── model/               # write model artifacts here during training
├── output/
│   └── failure/         # write failure messages here
└── code/                # training script entry point
```

**Inference container expected layout:**

```
/opt/ml/
├── model/               # model artifacts loaded from S3
└── code/                # inference script (serve entry point)
```

**Combined image (training + inference in one image):**

```
/opt/ml/
├── input/               # training input data
├── model/               # shared model artifacts
├── output/
└── code/
    ├── train            # executable for training
    └── serve            # executable for inference
```

> **Note:** The `SAGEMAKER_PROGRAM` environment variable must be set to define the entry point script when using the SageMaker Python SDK framework containers.

### 2.4 Production Variants

- Multiple model versions can be deployed behind a **single endpoint**
- Route `X%` of traffic to each variant (e.g., 90% → v1, 10% → v2)
- Increase allocation to a variant only when confident about performance
- Useful for A/B testing and gradual rollouts without Deployment Guardrails

---

## 3. Edge Deployment

### 3.1 SageMaker Neo

- **Compiles** trained models for a specific target hardware architecture
- Supported targets: ARM, Intel, NVIDIA processors, and others
- Supports frameworks: TensorFlow, PyTorch, MXNet, ONNX, XGBoost, DarkNet, Keras
- Output: an optimized compiled artifact for the target device

### 3.2 Neo + AWS IoT Greengrass

|Component|Role|
|---|---|
|**SageMaker Neo**|Compiles and optimizes the model for the target hardware|
|**AWS IoT Greengrass**|Deploys the compiled model and runs inference **on the edge device**|

> Neo handles the compile step; Greengrass handles the runtime deployment and local inference.

---

## 4. Deployment Methods & Tools

### 4.1 SageMaker JumpStart

- Deploy **pre-trained foundation and ML models** to pre-configured endpoints in one click
- Covers models from Hugging Face, Stability AI, and AWS-native models
- Also provides solution templates and example notebooks

### 4.2 ModelBuilder (SageMaker SDK)

- Programmatically configure deployment settings from code
- Infers container, serializer/deserializer, and instance type automatically
- Simplifies the path from a trained model object to a deployable SageMaker model

### 4.3 AWS CloudFormation (CFT)

- Declare SageMaker resources as infrastructure-as-code
- Key resource type: `AWS::SageMaker::Model`
- Also supports: `AWS::SageMaker::EndpointConfig`, `AWS::SageMaker::Endpoint`

---

## 5. Inference Types

|Type|Latency|Use Case|Infrastructure|
|---|---|---|---|
|**Real-Time Inference**|Low (ms)|Interactive, synchronous workloads|Persistent always-on endpoint|
|**Serverless Inference**|Variable (cold start possible)|Infrequent / spiky traffic with long idle periods|No infra management; scales to zero|
|**Async Inference**|Minutes (queued)|Large payloads, long processing times, non-interactive|SQS-backed queue; output written to S3|
|**Batch Transform**|Batch|Offline scoring of entire datasets|No persistent endpoint needed|

### 5.1 AWS Inference Recommender

- Automatically benchmarks your model across multiple instance types
- Measures latency, throughput, and cost
- Provides a ranked recommendation for the optimal instance type for your SLA requirements
- Two modes: **Default** (quick, uses built-in benchmarks) and **Advanced** (custom load test with your traffic pattern)

### 5.2 Inference Pipeline

- Chains **multiple Docker containers** into a single endpoint
- Example: `Preprocessing container → Prediction container → Postprocessing container`
- Supports both **real-time** and **batch transform** invocations
- Each container is independent — can be built in different frameworks

---

## 6. Model Monitor

### 6.1 Model Monitor Overview

Continuously monitors deployed models for quality degradation across four dimensions:

| Monitor Type                                | What It Detects                                                                    |
| ------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Data Quality Monitor**                    | Feature distribution drift vs. training baseline (Training time measure)           |
| **Model Quality Monitor**                   | Prediction accuracy/metric degradation over time (Inference Metric)                |
| **Bias Drift Monitor** (via Clarify)        | Changes in model bias against protected groups                                     |
| **Feature Attribution Drift** (via Clarify) | Shifts in SHAP-based feature importance distributions (How do features contribute) |

### 6.2 Data Capture

- Enable **Data Capture** on a real-time endpoint to log request/response payloads to S3
- Captured data is used as input for Model Monitor baselines and scheduled monitoring jobs
- Configurable capture percentage (e.g., capture 10% of traffic)

### 6.3 Model Monitor + Clarify

- SageMaker Clarify integrates with Model Monitor to add **bias and explainability monitoring**
- Generates a baseline from training data; scheduled jobs compare live traffic against it
- Emits CloudWatch metrics → trigger alarms → auto-rollback or alert

---

## 7. MLOps Orchestration & Integration

### 7.1 SageMaker + Kubernetes

- SageMaker Operators for Kubernetes — trigger SageMaker jobs from a K8s cluster
- Enables **hybrid on-prem + cloud** ML pipelines
- Integrates with existing pipelines built on **Kubeflow** or native Kubernetes

### 7.2 Container Orchestration Options

|Service|Role in MLOps|
|---|---|
|**Amazon ECS**|Run training/inference containers without K8s overhead|
|**Amazon EKS**|Kubernetes-native ML workloads; integrates with Kubeflow|
|**AWS Batch**|Managed batch compute for large-scale data processing and training jobs|

### 7.3 Infrastructure as Code

| Tool                         | Use Case                                                            |
| ---------------------------- | ------------------------------------------------------------------- |
| **AWS CloudFormation (CFT)** | Declarative IaC for SageMaker and all AWS resources                 |
| **AWS CDK**                  | Programmatic IaC (Python/TypeScript) — generates CFT under the hood |

### 7.4 CI/CD & Deployment Automation

| Service              | Role                                                                        |
| -------------------- | --------------------------------------------------------------------------- |
| **AWS CodePipeline** | Orchestrates end-to-end CI/CD pipelines (source → build → test → deploy)    |
| **AWS CodeDeploy**   | Automates model/application deployment with rollback support                |
| **GitFlow**          | Branching strategy: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` |
| **GitHub Flow**      | Simplified: feature branches off `main`, merge via pull request             |

### 7.5 Event-Driven & Workflow Orchestration

|Service|Role|
|---|---|
|**AWS EventBridge**|Event bus — triggers pipelines on S3 upload, model registry approval, schedule, etc.|
|**AWS Step Functions**|Serverless state machine — orchestrates multi-step ML workflows with branching, retries, and parallelism|
|**Amazon MWAA** (Managed Workflows for Apache Airflow)|DAG-based workflow orchestration; ideal for teams already using Airflow|

> **Choosing between them:** Step Functions for AWS-native, low-latency orchestration; MWAA for complex DAG logic or migration of existing Airflow pipelines.

### 7.6 Data Governance

| Service                         | Role                                                                                                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS Lake Formation**          | Centralized data lake governance — manages data access, permissions, and cataloging on top of S3                                                              |
| **Lake Formation Data Filters** | Fine-grained access control — column-level and row-level security on Glue Data Catalog tables; ensures only authorized ML pipelines access sensitive features |

---

## 8. MLOps Quick Reference

```
Source Control (Git)
        ↓
CodePipeline / GitHub Actions
        ↓
Build & Test (CodeBuild / pytest)
        ↓
SageMaker Pipeline (data prep → train → evaluate → register)
        ↓
Model Registry (approve/reject)
        ↓
EventBridge trigger on approval
        ↓
Deploy with Guardrails (Canary / Linear / All-at-Once)
        ↓
Model Monitor + Clarify (ongoing)
        ↓
Auto Rollback if alarm breaches
```