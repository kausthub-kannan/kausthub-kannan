## AWS CloudWatch Logs & Metric Alarms

### What is CloudWatch?

CloudWatch is AWS's **observability service** for monitoring resources and applications in real time.

### CloudWatch Logs

- Collects, monitors, and stores log files from AWS services (EC2, Lambda, SageMaker, etc.)
- **Log Groups** → container for log streams (e.g., `/aws/sagemaker/TrainingJobs`)
- **Log Streams** → sequence of log events from a single source
- Supports **metric filters** — extract numeric values from logs to create custom metrics
- **Retention** can be set from 1 day to never expire

### CloudWatch Metrics

- Pre-built metrics for AWS services (CPU, memory, latency, etc.)
- **Custom Metrics** — push your own metrics (e.g., model accuracy, inference latency)
- **Namespaces** group related metrics (e.g., `AWS/SageMaker`)
- Resolution: **Standard** (1 min) or **High Resolution** (1 sec)

### CloudWatch Alarms

- Trigger actions when a metric crosses a threshold
- **States:** `OK` → `ALARM` → `INSUFFICIENT_DATA`
- **Actions on alarm:**
    - Send SNS notification
    - Trigger Auto Scaling
    - Stop/terminate/reboot EC2
- **Composite Alarms** — combine multiple alarms with AND/OR logic

### ML Relevance

- Monitor **SageMaker training job** metrics (loss, accuracy)
- Alert on **endpoint latency** or **invocation errors**
- Track **GPU/CPU utilization** on training instances

---

## 2. AWS X-Ray

### What is X-Ray?

A **distributed tracing service** that helps debug and analyze microservices and ML pipelines end-to-end.

### Key Concepts

|Concept|Description|
|---|---|
|**Trace**|Full end-to-end request journey|
|**Segment**|Work done by a single service|
|**Subsegment**|Granular breakdown within a segment|
|**Annotations**|Key-value pairs used for **filtering/indexing**|
|**Metadata**|Additional data, not indexed|
|**Service Map**|Visual graph of all connected services|

### How It Works

1. App sends trace data to X-Ray daemon
2. Daemon batches and sends to X-Ray API
3. X-Ray assembles into traces → Service Map

### ML Relevance

- Trace **Lambda → SageMaker endpoint** invocation chains
- Debug latency bottlenecks in **inference pipelines**
- Identify which microservice is failing in an **MLOps workflow**

---

## 3. AWS CloudTrail

### What is CloudTrail?

An **audit and governance service** that records **API calls** made in your AWS account — who did what, when, and from where.

### Key Concepts

- **Event** — a single recorded API call (e.g., `CreateTrainingJob`, `DeleteBucket`)
- **Trail** — configuration that delivers events to S3 / CloudWatch Logs
- **Management Events** — control plane operations (create, delete, modify resources) — enabled by default
- **Data Events** — resource-level operations (S3 object access, Lambda invocations) — must be explicitly enabled
- **Insights Events** — detect unusual API activity (e.g., spike in `TerminateInstances`)

### CloudTrail vs Real-Time

- **Not real-time** — events delivered within ~15 minutes
- For real-time: integrate with **CloudWatch Logs**

### ML Relevance

- Audit **who launched/stopped a SageMaker training job**
- Track **IAM role changes** affecting ML pipelines
- Compliance and security forensics for **data access on S3 datasets**

---

## 4. AWS Config

### What is AWS Config?

A **configuration compliance service** that continuously records the **state of your AWS resources** and evaluates them against desired rules.

### Key Concepts

- **Configuration Item** — snapshot of a resource at a point in time
- **Configuration History** — timeline of all changes to a resource
- **Config Rules** — evaluate resource configurations for compliance
    - **AWS Managed Rules** — pre-built (e.g., `s3-bucket-public-read-prohibited`)
    - **Custom Rules** — written in Lambda
- **Conformance Packs** — bundle of rules + remediation actions
- **Remediation** — auto-fix non-compliant resources via SSM Automation

### ML Relevance

- Ensure **SageMaker endpoints are encrypted**
- Verify **S3 buckets storing training data are not public**
- Track configuration drift in **ML infrastructure**

---

## 5. CloudWatch vs CloudTrail vs Config

> This is a **frequently tested comparison** in AWS ML Associate exam.

|Feature|CloudWatch|CloudTrail|AWS Config|
|---|---|---|---|
|**Primary Purpose**|Performance monitoring & alerting|API call auditing|Resource compliance & history|
|**Answers**|_"Is my resource healthy?"_|_"Who did what?"_|_"What changed & is it compliant?"_|
|**Data Type**|Metrics, logs, events|API call logs|Configuration snapshots|
|**Real-Time?**|Yes|~15 min delay|Near real-time|
|**Retention**|Configurable|90 days (free), S3 for longer|Indefinite (in S3)|
|**ML Use Case**|Monitor training/inference metrics|Audit SageMaker API usage|Ensure ML infra is compliant|

### Memory Trick

- **CloudWatch** = _"How is it performing?"_
- **CloudTrail** = _"Who touched it?"_
- **Config** = _"What does it look like and should it look like that?"_

---

## 6. AWS Budgets

### What is AWS Budgets?

A **cost control service** that lets you set custom budgets and receive alerts when costs or usage exceed thresholds.

### Budget Types

|Type|Tracks|
|---|---|
|**Cost Budget**|Actual or forecasted spend ($)|
|**Usage Budget**|Service usage (e.g., SageMaker instance-hours)|
|**Reservation Budget**|RI/Savings Plan utilization or coverage|
|**Savings Plans Budget**|Savings Plan usage and coverage|

### Alerts

- Notify via **SNS / Email** when thresholds are crossed
- Can trigger **Lambda** for automated responses (e.g., stop non-critical jobs)
- Up to **5 alerts per budget**

### ML Relevance

- Set budget for **SageMaker training instance usage** to avoid runaway costs
- Alert when **spot instance spending** exceeds threshold
- Monitor per-team or per-project ML spend using **tags**

---

## 7. AWS Cost Explorer

### What is Cost Explorer?

An **interactive cost analysis tool** for visualizing, understanding, and forecasting your AWS spend.

### Key Features

- Pre-built reports: **Monthly costs by service, by linked account, by tag**
- **Granularity:** Daily, Monthly, Hourly (hourly requires extra cost)
- **Filtering:** By service, region, instance type, tags, linked accounts
- **Forecasting:** Predicts future spend based on historical patterns (up to 12 months)
- **Rightsizing Recommendations** — suggests cheaper instance types
- **Savings Plans recommendations** — estimates savings from commitment plans

### vs AWS Budgets

| Cost Explorer | AWS Budgets                   |                         |
| ------------- | ----------------------------- | ----------------------- |
| Purpose       | Analyze past & forecast spend | Set limits & get alerts |
| Proactive?    | Reactive (historical)         | Proactive (alerts)      |
| Forecasting   | Yes                           | Yes (basic)             |

### ML Relevance

- Identify **most expensive SageMaker operations** (training vs hosting)
- Analyze **data transfer costs** between S3 and training instances
- Use tags (e.g., `project=churn-model`) to break down ML project costs

---

## 8. AWS Trusted Advisor

### What is Trusted Advisor?

An **automated best-practice checker** that analyzes your AWS account across 5 pillars.

### The 5 Pillars

|Pillar|Example Checks|
|---|---|
|**Cost Optimization**|Idle EC2 instances, underutilized RIs|
|**Performance**|High-utilization EC2, CloudFront optimizations|
|**Security**|Open S3 buckets, MFA not enabled on root|
|**Fault Tolerance**|No Multi-AZ RDS, missing EBS snapshots|
|**Service Limits**|Approaching SageMaker instance quotas|

### Support Plan Access

| Check Category            | Basic/Developer | Business/Enterprise |
| ------------------------- | --------------- | ------------------- |
| Core security checks      | ✅               | ✅                   |
| All checks                | ❌               | ✅                   |
| Programmatic access (API) | ❌               | ✅                   |

### ML Relevance

- Check if **SageMaker service limits** are near quota before large training jobs
- Identify **idle notebook instances** wasting money
- Ensure **S3 data lake buckets** are not publicly exposed

---

## Quick Exam Summary

```
CloudWatch    → Monitor & Alert (metrics, logs, alarms)
X-Ray         → Trace & Debug (distributed systems)
CloudTrail    → Audit (API calls, who did what)
Config        → Compliance (what changed, is it right?)
Budgets       → Cost Limits & Alerts
Cost Explorer → Cost Analysis & Forecasting
Trusted Advisor → Best Practice Recommendations (5 pillars)
```