## 1. Least Privilege Principle

### What is it?

Grant **only the minimum permissions** required to perform a task — nothing more.
### Core Ideas

- Every user, role, service, or application should have **exactly the access it needs**
- Start with **zero permissions** and add as needed
- Regularly **audit and revoke** unused permissions

### In Practice

- Use **IAM policies** scoped to specific resources (ARNs), not wildcards (`*`)
- Prefer **IAM Roles** over long-lived IAM User keys
- Use **permission boundaries** to cap maximum permissions
- Enable **IAM Access Analyzer** to detect overly broad access

### ML Relevance

- SageMaker training job role should only access **its specific S3 bucket**, not all buckets
- Notebook instance role should **not have admin access**
- Data scientists should not have access to **production endpoints**

---

## 2. Data Masking and Anonymization

### What is it?

Techniques to **protect sensitive data** while preserving its utility for ML training and analysis.

### Key Techniques

|Technique|Description|Reversible?|
|---|---|---|
|**Masking**|Replace sensitive values with placeholders (`***-**-1234`)|No|
|**Tokenization**|Replace data with a random token mapped in a secure vault|Yes (with vault)|
|**Pseudonymization**|Replace identifiers with pseudonyms|Yes (with key)|
|**Anonymization**|Remove all PII permanently|No|
|**Generalization**|Reduce precision (exact age → age range)|No|
|**Noise Addition**|Add statistical noise (differential privacy)|No|

### AWS Tools

- **AWS Glue** — transform and mask data in ETL pipelines
- **Amazon Macie** — auto-detect PII in S3 using ML
- **AWS Lake Formation** — column-level and row-level security on data lakes

### ML Relevance

- Training data must be **scrubbed of PII** before use (GDPR, HIPAA compliance)
- Use **synthetic data generation** as an alternative to real sensitive data
- Anonymize datasets stored in **S3 / Feature Store**

---

## 3. SageMaker Security: Encryption at Rest and in Transit

### Encryption at Rest

Data stored on disk is encrypted.

|Resource|Encryption Option|
|---|---|
|S3 (training data, model artifacts)|SSE-S3, SSE-KMS, CSE|
|EBS volumes (notebook/training instances)|AWS KMS CMK|
|SageMaker Feature Store|KMS encryption|
|SageMaker Studio EFS|KMS-managed|

- Specify `KmsKeyId` in training job, endpoint, and notebook configs
- Without KMS key → AWS uses **default encryption** (managed key)

### Encryption in Transit

Data moving between services is encrypted.

- All SageMaker API calls use **TLS 1.2+**
- Data between training instances uses **inter-node encryption** — enable via `EnableInterContainerTrafficEncryption: true`
- May **increase training time** slightly due to overhead

### ML Relevance

- Required for **HIPAA / PCI-DSS** compliant ML workloads
- Enabling inter-node encryption is critical for **distributed training on sensitive data**

---

## 4. SageMaker Security: VPCs, IAM, Logging & Monitoring

### VPC for SageMaker

- By default, SageMaker runs in an **AWS-managed network** (outside your VPC)
- Configure SageMaker to run **inside your VPC** for network isolation
- Requires specifying **SubnetIds** and **SecurityGroupIds**
- Use **VPC Endpoints** (PrivateLink) to access S3/SageMaker APIs without internet

### IAM for SageMaker

- Each job/resource needs an **Execution Role** with appropriate policies
- Common managed policies:
    - `AmazonSageMakerFullAccess` — broad (avoid in prod)
    - `AmazonSageMakerReadOnly` — for monitoring roles
- Scope roles by **resource ARN** and **condition keys**

### Logging & Monitoring

|Tool|What It Captures|
|---|---|
|**CloudWatch Logs**|Training job logs, endpoint logs, container stdout/stderr|
|**CloudWatch Metrics**|Invocation counts, latency, CPU/GPU utilization|
|**CloudTrail**|API calls (CreateTrainingJob, DeleteEndpoint, etc.)|
|**SageMaker Debugger**|Training anomalies, vanishing gradients, overfitting|
|**SageMaker Model Monitor**|Data drift, model quality drift in production|

---

## 5. IAM Introduction: Users, Groups, Policies

### What is IAM?

**Identity and Access Management** — controls **who** can do **what** on **which** AWS resources.

### Core Components

```
IAM Account
├── Users        → Individual identities (people or apps)
├── Groups       → Collection of users sharing permissions
├── Roles        → Assumable identities for services/apps
└── Policies     → JSON documents defining permissions
```

### Key Facts

- IAM is **global** — not region-specific
- **Root account** — has full access; should never be used daily; enable MFA
- Permissions are **deny by default** — explicit allow required
- **Explicit Deny** always overrides any Allow

---

## 6. IAM Users and Groups

### IAM Users

- Represents a **person or application**
- Has credentials: **password** (console) and/or **access keys** (CLI/SDK)
- Can belong to **multiple groups**
- Best practice: **never use root**, create individual IAM users

### IAM Groups

- Logical collection of users
- Assign **policies to groups**, not individual users (easier management)
- A user can belong to **multiple groups**
- Groups **cannot be nested** (no groups within groups)

### Best Practices

- Create a group per role: `Admins`, `DataScientists`, `MLEngineers`
- Attach least-privilege policies to each group
- Rotate access keys regularly

---

## 7. AWS Console Simultaneous Access

### What is it?

Multiple IAM users can log into the **same AWS account simultaneously** using different credentials — each session is independent.

### How It Works

- Each user logs in at: `https://<account-id>.signin.aws.amazon.com/console`
- Sessions are **isolated** — one user's actions don't affect another's session
- **AWS Organizations** allows switching between accounts via **role switching**

### ML Relevance

- Data scientists and ML engineers can work in the **same account simultaneously**
- Use **resource tagging** to track who created which training jobs

---

## 8. IAM Policies

### What is a Policy?

A **JSON document** that defines permissions — what actions are allowed or denied on which resources.

### Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-ml-bucket/*",
      "Condition": {
        "StringEquals": {"aws:RequestedRegion": "us-east-1"}
      }
    }
  ]
}
```

### Policy Types

|Type|Description|
|---|---|
|**AWS Managed**|Pre-built by AWS, reusable|
|**Customer Managed**|Created by you, reusable|
|**Inline**|Embedded directly in a user/group/role; 1:1 relationship|
|**Resource-Based**|Attached to a resource (e.g., S3 bucket policy)|
|**Permission Boundary**|Sets maximum permissions a role can have|
|**SCP (Service Control Policy)**|Org-level guardrails via AWS Organizations|

### Evaluation Logic

```
Explicit Deny? → DENY
↓
SCP allows? → Check next
↓
Permission boundary allows? → Check next
↓
Identity policy allows? → ALLOW
↓
Default → DENY
```

---

## 9. IAM Roles

### What is a Role?

An IAM identity that can be **assumed temporarily** by AWS services, users, or applications — no long-term credentials.

### Common Use Cases

|Role Type|Used By|
|---|---|
|**Service Role**|SageMaker, Lambda, EC2 to call other AWS services|
|**Cross-Account Role**|Access resources in another AWS account|
|**Federated Role**|SSO users, SAML, Cognito identity pools|
|**Instance Profile**|EC2 instances assuming a role|

### How Role Assumption Works

1. Entity calls `sts:AssumeRole`
2. AWS STS returns **temporary credentials** (Access Key + Secret + Session Token)
3. Credentials expire (15 min to 12 hours)

### ML Relevance

- SageMaker training job assumes a **SageMaker Execution Role** to read S3 and write model artifacts
- Lambda invoking a SageMaker endpoint needs a role with `sagemaker:InvokeEndpoint`

---

## 10. Encryption 101

### Encryption Types

|Type|Description|
|---|---|
|**Symmetric**|Same key for encrypt & decrypt (fast) — used for data|
|**Asymmetric**|Public key encrypts, private key decrypts — used for key exchange|
|**Envelope Encryption**|Data encrypted with Data Key (DEK); DEK encrypted with Master Key (CMK)|

### Encryption Contexts

- **At Rest** — data stored on disk (EBS, S3, RDS)
- **In Transit** — data moving over network (TLS/SSL)
- **In Use** — data being processed (AWS Nitro Enclaves)

### Envelope Encryption (Used by AWS KMS)

```
Plaintext Data
     ↓ encrypted with DEK (Data Encryption Key)
Encrypted Data
     +
Encrypted DEK (DEK encrypted with CMK/Master Key)
```

- Only the **CMK never leaves KMS**
- You store encrypted DEK alongside your data

---

## 11. AWS KMS (Key Management Service)

### What is KMS?

Managed service to **create, rotate, and control cryptographic keys** used to encrypt AWS data.

### Key Types

|Type|Description|
|---|---|
|**AWS Managed Keys**|Auto-created per service (free), limited control|
|**Customer Managed Keys (CMK)**|You create and control; $1/month per key|
|**AWS Owned Keys**|Used internally by AWS; you have no visibility|

### Key Features

- Automatic **key rotation** (annually for CMKs)
- Integrated with **S3, EBS, RDS, SageMaker, Secrets Manager**, etc.
- All key usage logged to **CloudTrail**
- **Multi-Region Keys** — replicate keys across regions

### Key Policies

- Every CMK has a **resource-based policy** (Key Policy)
- Must explicitly allow IAM roles/users to use the key

### ML Relevance

- Encrypt **S3 training datasets** with CMK using SSE-KMS
- Encrypt **SageMaker model artifacts** and EBS volumes
- Use **Key Grants** to allow SageMaker service to use your CMK

---

## 12. AWS Secrets Manager

### What is it?

A service to **store, rotate, and retrieve secrets** (passwords, API keys, DB credentials) securely.

### Key Features

- **Automatic rotation** — integrates with RDS, Redshift, DocumentDB natively
- Custom rotation via **Lambda function**
- Secrets encrypted using **KMS**
- Access controlled via **IAM + resource-based policies**
- **Versioning** — maintains previous secret versions during rotation

### vs SSM Parameter Store

|Feature|Secrets Manager|SSM Parameter Store|
|---|---|---|
|Cost|~$0.40/secret/month|Free (standard tier)|
|Auto Rotation|✅ Native|❌ Manual/Lambda|
|Cross-account|✅|Limited|
|Best For|DB credentials, API keys|Config values, feature flags|

### ML Relevance

- Store **database credentials** for SageMaker Feature Store connections
- Store **third-party API keys** used in ML inference Lambda functions
- Rotate **RDS credentials** used by training pipelines automatically

---

## 13. AWS WAF (Web Application Firewall)

### What is WAF?

A **Layer 7 (HTTP/HTTPS) firewall** that protects web applications from common exploits.

### Key Concepts

- **Web ACL** — set of rules applied to requests
- **Rules** — conditions to inspect (IP, headers, body, URI)
- **Rule Groups** — reusable bundles of rules
- **Actions:** `Allow`, `Block`, `Count`, `CAPTCHA`

### What WAF Protects Against

- SQL Injection
- Cross-Site Scripting (XSS)
- Bad bots and scrapers
- Rate-based attacks (simple rate limiting)
- Geographic-based blocking

### Deployable On

- **CloudFront** (edge — global)
- **Application Load Balancer**
- **API Gateway**
- **AppSync**

### ML Relevance

- Protect **SageMaker real-time endpoints** exposed via API Gateway
- Rate-limit inference API to prevent abuse
- Block malicious inputs that could exploit model serving infrastructure

---

## 14. AWS Shield

### What is Shield?

A **DDoS protection service** operating at Layers 3, 4, and 7.

### Tiers

|Feature|Shield Standard|Shield Advanced|
|---|---|---|
|Cost|Free (automatic)|~$3,000/month|
|Protection|L3/L4 DDoS|L3/L4/L7 DDoS|
|DDoS Response Team|❌|✅ 24/7 DRT access|
|Cost Protection|❌|✅ (AWS credits for spike costs)|
|Real-time Visibility|❌|✅|
|WAF Integration|❌|✅|

### ML Relevance

- Protect **public-facing ML APIs** from volumetric DDoS attacks
- Shield Advanced covers **API Gateway and CloudFront** fronting ML endpoints

---

## 15. VPC, Subnets, Internet Gateway, NAT Gateway

### VPC (Virtual Private Cloud)

Your **private, isolated network** within AWS. You control IP ranges, subnets, routing, and gateways.

```
VPC (e.g., 10.0.0.0/16)
├── Public Subnet (10.0.1.0/24)  → Has route to Internet Gateway
└── Private Subnet (10.0.2.0/24) → No direct internet; uses NAT
```

### Subnets

- **Public Subnet** — resources accessible from internet (ALB, Bastion hosts)
- **Private Subnet** — resources NOT accessible from internet (RDS, SageMaker training, Lambda)
- Each subnet lives in **one Availability Zone**

### Internet Gateway (IGW)

- Attached to VPC to **allow internet access** for public subnets
- **Horizontally scaled, redundant, HA** — no management needed
- Route table must have `0.0.0.0/0 → IGW` for internet access

### NAT Gateway

- Allows **private subnet resources to initiate outbound internet traffic** (e.g., download packages)
- Internet cannot initiate connections **back** to private resources
- Deployed in a **public subnet**; private subnet routes `0.0.0.0/0 → NAT Gateway`
- **Managed by AWS** — highly available per AZ

### ML Relevance

- SageMaker training instances in **private subnets** use NAT Gateway to pull Docker images
- Keep **S3 training data and model stores** in private subnets
- Use **VPC Endpoints** instead of NAT for S3 (cheaper, no internet exposure)

---

## 16. NACL, Security Groups, VPC Flow Logs

### Security Groups (SG)

- **Instance-level** firewall (attached to ENI)
- **Stateful** — return traffic automatically allowed
- Only **Allow** rules (no explicit deny)
- Rules evaluated **all at once**

### Network ACL (NACL)

- **Subnet-level** firewall
- **Stateless** — must explicitly allow both inbound AND outbound
- Supports both **Allow and Deny** rules
- Rules evaluated **in order** (lowest number first); first match wins

### SG vs NACL Comparison

|Feature|Security Group|NACL|
|---|---|---|
|Level|Instance (ENI)|Subnet|
|Stateful?|✅ Yes|❌ No|
|Allow & Deny?|Allow only|Both|
|Rule Order|All evaluated|Sequential|
|Default|Deny all inbound|Allow all|

### VPC Flow Logs

- Capture **IP traffic metadata** going to/from network interfaces
- Stored in **CloudWatch Logs or S3**
- Does NOT capture packet content — only metadata (source IP, dest IP, port, action)
- Used for **security auditing, traffic analysis, troubleshooting**

### ML Relevance

- Flow Logs help detect **unexpected outbound traffic** from training instances
- NACLs block entire IP ranges; SGs control per-resource access to **SageMaker endpoints**

---

## 17. VPC Peering, Endpoints, VPN, Direct Connect

### VPC Peering

- **Private connectivity** between two VPCs (same or different accounts/regions)
- Traffic stays on **AWS backbone** — no internet
- **Non-transitive** — A↔B and B↔C does NOT mean A↔C
- No overlapping CIDR blocks allowed

### VPC Endpoints

Connect to AWS services **without internet, NAT, or IGW** — traffic stays within AWS.

|Type|Description|
|---|---|
|**Gateway Endpoint**|For **S3 and DynamoDB** only; free; added to route table|
|**Interface Endpoint**|For all other services (SageMaker, KMS, etc.); powered by PrivateLink; costs apply|

### AWS VPN

- **Site-to-Site VPN** — encrypted tunnel between on-premises network and VPC over public internet
- **Client VPN** — remote users connect to VPC from their devices
- Quick to set up; bandwidth limited by internet connection

### AWS Direct Connect

- **Dedicated private physical connection** between on-premises and AWS
- Consistent latency, higher throughput, no internet dependency
- Takes **weeks to provision**; more expensive
- Supports **1 Gbps, 10 Gbps, 100 Gbps**

### VPN vs Direct Connect

|Feature|VPN|Direct Connect|
|---|---|---|
|Setup Time|Minutes|Weeks|
|Encryption|✅ (IPSec)|❌ (add VPN on top)|
|Reliability|Internet dependent|Dedicated line|
|Cost|Low|High|
|Bandwidth|Up to ~1.25 Gbps|Up to 100 Gbps|

### ML Relevance

- Use **S3 Gateway Endpoint** in SageMaker VPC configs — free and keeps data off internet
- **Direct Connect** for large-scale data ingestion from on-prem to S3 for ML training
- **VPC Peering** to share a centralized SageMaker endpoint across multiple team VPCs

---

## 18. AWS PrivateLink

### What is PrivateLink?

A service that allows **private, secure access to AWS services or your own services** from a VPC — without exposing traffic to the public internet.

### How It Works

```
Consumer VPC
└── Interface Endpoint (ENI with private IP)
        ↓ (PrivateLink / AWS backbone)
Provider Service (AWS service or your NLB-backed service)
```

### Key Concepts

- **Interface VPC Endpoint** — ENI in your subnet with a private IP; uses PrivateLink under the hood
- **Endpoint Service** — your own service exposed to other VPCs via PrivateLink (backed by NLB)
- Traffic **never leaves AWS network**
- Supports **cross-account and cross-region** (with some limits)

### PrivateLink vs VPC Peering

|Feature|PrivateLink|VPC Peering|
|---|---|---|
|Use Case|Access a specific service|Full VPC-to-VPC access|
|Direction|One-way (consumer → provider)|Bidirectional|
|CIDR Overlap OK?|✅ Yes|❌ No|
|Scalability|Highly scalable|Complex at scale|

### ML Relevance

- Access **SageMaker API and Runtime privately** from within your VPC
- Expose your **custom ML inference service** to other teams via PrivateLink without VPC peering
- Required for **high-security ML workloads** where no internet exposure is acceptable

---

## Quick Reference Cheat Sheet

```
Least Privilege     → Minimum permissions needed, always
Data Masking        → Protect PII before ML training (Macie, Glue)
Encryption at Rest  → KMS CMK for S3, EBS, SageMaker artifacts
Encryption Transit  → TLS + inter-node encryption for distributed training
IAM Users/Groups    → People/apps → grouped → policies attached
IAM Roles           → Assumed by services (SageMaker, Lambda); temp credentials
IAM Policies        → JSON; Deny > Allow; check SCP → boundary → identity
KMS                 → Managed keys; envelope encryption; logged to CloudTrail
Secrets Manager     → Store & auto-rotate credentials; KMS-encrypted
WAF                 → L7 protection (SQLi, XSS); on ALB/API GW/CloudFront
Shield              → DDoS protection; Standard=free; Advanced=$3k/mo
VPC                 → Private network; public + private subnets
IGW                 → Internet access for public subnets
NAT Gateway         → Outbound internet for private subnets
Security Group      → Stateful, instance-level, allow only
NACL                → Stateless, subnet-level, allow + deny
VPC Endpoints       → S3/DynamoDB=Gateway (free); others=Interface (PrivateLink)
Direct Connect      → Dedicated line on-prem to AWS; fast & reliable
PrivateLink         → Private access to services without internet; no CIDR conflicts
```