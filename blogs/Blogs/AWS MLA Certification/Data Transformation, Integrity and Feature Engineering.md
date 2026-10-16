## 1. EMR and Hadoop

### 1.1 What Is Hadoop?

Apache Hadoop is an open-source framework for **distributed storage and processing of very large datasets** across clusters of commodity hardware.

**Core Hadoop Components:**

|Component|Role|
|---|---|
|**HDFS** (Hadoop Distributed File System)|Distributed block storage; splits files into blocks (default 128MB) replicated across nodes|
|**YARN** (Yet Another Resource Negotiator)|Cluster resource manager — allocates CPU and memory to applications|
|**MapReduce**|Programming model for parallel data processing (Map phase → Shuffle/Sort → Reduce phase)|
|**Hive**|SQL-like query interface over HDFS; compiles queries to MapReduce or Tez|
|**Pig**|Scripting language for data transformation pipelines|
|**HBase**|NoSQL columnar store on top of HDFS|
|**ZooKeeper**|Distributed coordination service (leader election, configuration)|

**MapReduce Pattern:**

```
Input Data (HDFS)
      ↓
MAP — each mapper processes a data split independently; emits (key, value) pairs
      ↓
SHUFFLE & SORT — framework groups all values by key across all mappers
      ↓
REDUCE — each reducer aggregates all values for its key group
      ↓
Output (HDFS)
```

**Hadoop limitations (why Spark replaced it for most workloads):**

- MapReduce writes intermediate results to disk at every step → very slow for iterative algorithms (ML)
- Complex multi-step pipelines require chaining multiple MapReduce jobs
- No in-memory processing

---

### 1.2 Amazon EMR (Elastic MapReduce)

EMR is AWS's **managed big data platform** — provisions, configures, and auto-scales Hadoop ecosystem clusters on EC2.

#### EMR Architecture

```
┌────────────────────────────────────────────────┐
│                  EMR Cluster                   │
│                                                │
│  Primary Node (Master)                         │
│  ├── YARN ResourceManager                      │
│  ├── HDFS NameNode                             │
│  └── Cluster coordination                      │
│                                                │
│  Core Nodes (1+)                               │
│  ├── YARN NodeManager (run tasks)              │
│  ├── HDFS DataNode (store data)                │
│  └── Cannot be removed without data loss       │
│                                                │
│  Task Nodes (0+)                               │
│  ├── YARN NodeManager only (run tasks)         │
│  ├── No HDFS storage                           │
│  └── Can be Spot instances; safely removable   │
└────────────────────────────────────────────────┘
```

#### EMR Storage Options

|Storage|Description|Best For|
|---|---|---|
|**HDFS**|Ephemeral storage on EC2 instance disks; fast; lost when cluster terminates|Intermediate processing; temp data|
|**EMRFS (S3)**|S3 as persistent HDFS substitute; cluster-independent|Primary data lake storage; decoupled from cluster|
|**Local FS**|Instance local disk; fastest; very limited|Buffer, scratch space|
|**EBS**|Attached to primary/core nodes; persistent within cluster lifetime|HDFS augmentation|

> **Exam tip:** Best practice is to store input/output data in **S3 (EMRFS)** and use HDFS only for intermediate iterative jobs data. This decouples storage from compute — you can terminate the cluster and data persists.
> 
> If data needs to be accessed by multiple cores; go with HDFS else Local FS

#### EMR Instance Types

|Node Type|Recommended Instances|Why|
|---|---|---|
|Primary|m5.xlarge+|Coordination only; not compute-intensive|
|Core|r5 (memory), d2 (storage), i3 (NVMe)|HDFS storage + compute|
|Task (Spot)|Same as Core but no HDFS|Pure compute scale-out at low cost|

#### EMR Auto Scaling

- **Managed Scaling** — EMR automatically scales core and task nodes based on YARN metrics (pending containers, available memory)
- **Custom Auto Scaling** — CloudWatch-based scale policies
- **Instance Fleet** — specify multiple instance types per fleet; EMR picks available capacity (great for Spot diversification)
- **Instance Group** — fixed instance type per group; simpler but less Spot resilient

#### EMR and S3

- **EMRFS** — native S3 integration; treat S3 paths like HDFS paths (`s3://bucket/prefix/`)
- **S3 Consistency** — EMRFS uses DynamoDB for consistent list/read-after-write (legacy; now S3 is strongly consistent natively)
- **Encryption:** SSE-S3, SSE-KMS, or CSE (Client-Side Encryption) via EMRFS encryption settings

#### Key EMR Use Cases (Exam)

- ETL pipelines at petabyte scale
- Log processing and analytics
- Machine learning feature engineering on large datasets
- SQL analytics with Hive or Presto
- Streaming with Spark Streaming or Flink on EMR

---

### 1.3 EMR Serverless

#### What It Is

EMR Serverless eliminates cluster management entirely — you submit jobs, AWS provisions and scales resources **automatically**, and you pay only for resources consumed during job execution.

#### EMR Serverless vs EMR on EC2

|Dimension|EMR on EC2|EMR Serverless|
|---|---|---|
|Infrastructure|You provision clusters|Fully managed; no clusters|
|Startup time|5–10 min cluster provisioning|Pre-initialized workers: seconds|
|Scaling|Manual or auto-scaling|Automatic; fully elastic|
|Cost model|Pay for cluster uptime (even idle)|Pay per vCPU-second and GB-second used|
|Best for|Persistent workloads; full control|Intermittent jobs; bursty workloads|
|Networking|Cluster in your VPC|Runs in AWS-managed VPC; optionally connect to your VPC|

#### EMR Serverless Key Concepts

|Concept|Description|
|---|---|
|**Application**|Logical container for Spark or Hive jobs; defines runtime (Spark 3.x, Hive)|
|**Job Run**|A single Spark or Hive job submitted to an application|
|**Pre-initialized Capacity**|Optional: keep N workers warm to eliminate cold start latency|
|**Worker Configuration**|Default: 4 vCPU + 16 GB RAM per worker; customizable per job|
|**Max Capacity**|Set ceiling on concurrent vCPU/memory to control cost|

#### How to Use

1. Create an **EMR Serverless Application** (Spark or Hive)
2. Submit jobs via **AWS Console**, **CLI**, **SDK**, or **Step Functions**
3. Provide: S3 URI for job script, S3 output path, IAM execution role
4. Monitor via EMR Serverless console or CloudWatch

---

### 1.4 Apache Spark on EMR

#### Why Spark Over MapReduce

|Aspect|MapReduce|Apache Spark|
|---|---|---|
|Processing|Disk-based at every step|**In-memory**; 10–100× faster for iterative algorithms|
|API|Low-level Java/Python|Rich high-level APIs (DataFrames, SQL, ML, Streaming)|
|ML support|No native ML|**MLlib** — distributed ML library|
|Streaming|Batch only|Spark Streaming, Structured Streaming|
|Interactive|No|Spark Shell, Jupyter notebooks|

#### Spark Core Concepts

|Concept|Description|
|---|---|
|**SparkContext / SparkSession**|Entry point to Spark; manages cluster connection|
|**RDD** (Resilient Distributed Dataset)|Immutable distributed collection; low-level API; fault-tolerant|
|**DataFrame**|Distributed table with named columns; optimized via Catalyst; preferred API|
|**Dataset**|Typed DataFrame; strongly typed in Scala/Java|
|**Partition**|Unit of parallelism; each partition processed by one task|
|**Driver**|JVM process that runs main program; coordinates workers|
|**Executor**|JVM process on worker nodes; executes tasks|
|**Stage**|Set of tasks with no shuffle between them|
|**Shuffle**|Redistributing data across partitions (expensive — involves disk write + network)|

#### Spark on EMR: Execution Flow

```
SparkSession (driver on primary node)
      ↓
DAG (Directed Acyclic Graph) of transformations built by Catalyst optimizer
      ↓
DAG Scheduler → splits into stages at shuffle boundaries
      ↓
Task Scheduler → submits tasks to YARN ResourceManager
      ↓
YARN → assigns tasks to Executor JVMs on core/task nodes
      ↓
Executors run tasks → results returned to driver or written to S3
```

#### Key Spark Transformations and Actions

**Transformations (lazy — build DAG):**

- `filter()`, `select()`, `withColumn()`, `groupBy()`, `join()`, `union()`, `repartition()`, `coalesce()`

**Actions (trigger execution):**

- `show()`, `count()`, `collect()`, `write()`, `save()`

#### Spark MLlib on EMR

MLlib provides distributed implementations of common ML algorithms:

|Algorithm Type|Available in MLlib|
|---|---|
|Classification|Logistic Regression, Decision Tree, Random Forest, GBT, SVM, Naïve Bayes|
|Regression|Linear Regression, Decision Tree, Random Forest, GBT|
|Clustering|K-Means, Gaussian Mixture, Bisecting K-Means|
|Dimensionality Reduction|PCA, SVD|
|Recommendation|ALS (Alternating Least Squares) — collaborative filtering|
|Feature Engineering|VectorAssembler, StandardScaler, StringIndexer, OneHotEncoder, TF-IDF, Word2Vec|

**MLlib Pipeline API:**

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier

pipeline = Pipeline(stages=[
    StringIndexer(inputCol="category", outputCol="category_idx"),
    VectorAssembler(inputCols=["feature1", "feature2", "category_idx"], outputCol="features"),
    StandardScaler(inputCol="features", outputCol="scaled_features"),
    RandomForestClassifier(featuresCol="scaled_features", labelCol="label")
])
model = pipeline.fit(train_df)
```

#### EMR + SageMaker Integration

- Train on EMR (large-scale feature engineering) → write features to S3 → train model in SageMaker
- Use **SageMaker Processing Jobs** with a Spark container for distributed preprocessing
- **SageMaker Feature Store** — write features from Spark directly into the feature store

---

## 2. Feature Engineering

### 2.1 Why Feature Engineering?

> "The features you choose matter more than the algorithm you use."

- ML models can only learn from the information provided as features
- Raw data is rarely in the right form for learning — domain knowledge encoded as features dramatically improves performance
- Feature engineering includes: imputation, outlier handling, encoding, scaling, transformation, creation, and selection

---

### 2.2 Curse of Dimensionality

As the number of features (dimensions) increases, the volume of the feature space grows **exponentially**, causing several problems:

|Problem|Description|
|---|---|
|**Data sparsity**|Fixed training samples become increasingly sparse in high-dimensional space; no local neighborhood is dense|
|**Distance metric breakdown**|Euclidean distance becomes meaningless — all points appear equidistant; affects KNN, clustering, SVM|
|**Overfitting**|Model finds spurious correlations in noise across many features|
|**Computational cost**|Training time grows with dimensionality|
|**Visualization impossible**|Cannot inspect or understand feature relationships beyond 3D|

**The core insight:** In high dimensions, you need **exponentially more data** to maintain the same density of samples. If you need 100 samples per dimension in 1D, you need 100^10 samples in 10D to maintain the same density.

#### Mitigation Strategies

|Strategy|Method|Notes|
|---|---|---|
|**Dimensionality Reduction**|PCA, t-SNE, UMAP, autoencoders|Compress to lower-dimensional representation|
|**Feature Selection**|Filter (correlation), Wrapper (RFE), Embedded (L1/LASSO)|Remove irrelevant/redundant features|
|**Regularization**|L1 (LASSO drives weights to 0), L2 (Ridge shrinks weights)|Penalize complexity|
|**Domain knowledge**|Engineer fewer, higher-quality features|Better than many noisy features|
|**More data**|If dimensionality is fixed, get more samples|Expensive; not always possible|

---

### 2.3 Imputing Missing Data

#### Types of Missingness

|Type|Description|Implication|
|---|---|---|
|**MCAR** (Missing Completely At Random)|Missingness is unrelated to any observed or unobserved variable|Safe to impute; drop rows also acceptable|
|**MAR** (Missing At Random)|Missingness depends on other observed variables (not the missing value itself)|Can impute using other features|
|**MNAR** (Missing Not At Random)|Missingness depends on the missing value itself (e.g., high-earners skip income field)|Bias if ignored; hardest to handle|

#### Imputation Methods

|Method|When to Use|Risk|
|---|---|---|
|**Drop rows**|MCAR; very few missing rows|Loses data; biases if not MCAR|
|**Drop column**|>50% missing in column; column not important|Loses potentially useful signal|
|**Mean imputation**|Numerical; MCAR; roughly normal distribution|Distorts variance; creates artificial spike at mean|
|**Median imputation**|Numerical; skewed distribution; outliers present|More robust than mean for skewed data|
|**Mode imputation**|Categorical; MCAR|Creates artificial modal spike|
|**Constant imputation**|When missing = meaningful category (e.g., "None")|Sometimes the right semantic choice|
|**KNN imputation**|When missingness is MAR; data has meaningful structure|Computationally expensive at scale|
|**Regression / model imputation**|Predict missing values from other features|Risk of leakage if imputation model uses target|
|**MICE** (Multiple Imputation by Chained Equations)|Complex MAR; multiple missing features|Computationally expensive; best statistical approach|
|**Forward/Backward fill**|Time series — use previous or next observation|Only for sequential data|

#### Missing Indicator Feature

- Add a binary feature `feature_X_was_missing` (1 = was missing, 0 = was present)
- Preserves the information that the value was missing — MNAR data especially benefits from this
- Use alongside any imputation method

---

### 2.4 Handling Outliers

#### Detection Methods

|Method|How It Works|Best For|
|---|---|---|
|**Z-score**|Flag if `|x - μ|
|**IQR (Interquartile Range)**|Flag if `x < Q1 - 1.5×IQR` or `x > Q3 + 1.5×IQR`|Skewed data; robust to extreme values|
|**Isolation Forest**|Anomaly detection algorithm; isolates outliers via random splits|High-dimensional; multivariate outliers|
|**DBSCAN**|Density-based clustering; points in low-density regions = outliers|Complex, non-linear distributions|
|**Visual**|Box plots, scatter plots, histogram inspection|Exploratory analysis; low dimensions|

#### Treatment Options

|Treatment|Method|When|
|---|---|---|
|**Remove**|Drop the row|Confirmed data error; small number of outliers|
|**Cap / Winsorize**|Replace values beyond percentile threshold (e.g., p1 and p99) with threshold value|Many outliers; want to preserve row count|
|**Log transform**|`log(x+1)` compresses extreme values|Right-skewed distributions (income, counts)|
|**Binning**|Discretize into buckets — extreme values fall into "very high" bin|Reduces outlier impact|
|**Impute as missing**|Treat as missing and impute|When outlier is likely a measurement error|
|**Keep**|Intentionally retain|If outliers are real signal (e.g., fraud = rare extreme transaction)|

> **Exam tip:** For tree-based models (XGBoost, Random Forest), outliers are **less problematic** because splits are based on rank order. For distance-based models (KNN, K-Means, SVM) and linear models, outliers severely distort results — scaling and capping are critical.

---

### 2.5 Binning (Discretization)

Convert a continuous numerical feature into discrete categorical bins.

**Why bin:**

- Reduce sensitivity to outliers
- Capture non-linear relationships for linear models
- Reduce noise in continuous measurements
- Create interpretable features

**Types:**

|Type|Description|Example|
|---|---|---|
|**Fixed-width (equal-width)**|Divide range into N equal-width intervals|Age: [0-20), [20-40), [40-60), [60+]|
|**Quantile (equal-frequency)**|Each bin contains roughly equal number of samples|Each quartile = 25% of data|
|**Custom / domain-driven**|Bins defined by business rules|Credit scores: Poor <580, Fair 580-669, Good 670-739, Excellent 740+|
|**Optimal binning**|Statistical methods maximize information value (IV) relative to target|Credit risk modeling|

**Risks:** Binning discards information about variation within a bin; choosing wrong bin boundaries can hide important signal.

---

### 2.6 Transformations

#### Numerical Transformations

| Transformation  | Formula                                                               | Use Case                                                   |
| --------------- | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| **Log**         | `log(x)` or `log(x+1)`                                                | Right-skewed; compresses large values (income, population) |
| **Square Root** | `√x`                                                                  | Moderate right skew; counts data                           |
| **Box-Cox**     | Parametric family including log and power transforms; finds optimal λ | General skew correction; requires positive values          |
| **Yeo-Johnson** | Extension of Box-Cox for zero and negative values                     | More general than Box-Cox                                  |
| **Power**       | `x^p` (p<1 reduces skew; p>1 increases it)                            | Flexible; p=0.5 is square root                             |
| **Reciprocal**  | `1/x`                                                                 | Speeds; rates; ratios                                      |

#### Target Encoding (for regression targets)

- Apply log transform to right-skewed regression targets (house prices, salaries) for better model fit
- **Must inverse-transform predictions** after inference to return to original scale

---

### 2.7 Encoding Categorical Variables

ML algorithms require numerical input — categorical features must be encoded.

|Encoding|Method|When to Use|Risk|
|---|---|---|---|
|**Label Encoding**|Map each category to an integer (0, 1, 2, ...)|Ordinal categories (Low/Med/High); tree-based models|Implies ordinal relationship where none may exist|
|**One-Hot Encoding (OHE)**|Create binary column per category|Nominal; linear models; low cardinality (<20 categories)|Dimensionality explosion for high-cardinality features|
|**Target Encoding**|Replace category with mean of target for that category|High-cardinality nominal; tree-based models|Data leakage — must use only training fold's mean|
|**Frequency / Count Encoding**|Replace category with its frequency in training data|High-cardinality; preserves frequency signal|Doesn't capture relationship with target|
|**Binary Encoding**|Convert label integer to binary bits; create one column per bit|High-cardinality; compromise between OHE and label|Less interpretable|
|**Ordinal Encoding**|Manual integer mapping preserving order|Explicitly ordinal features|Requires domain knowledge for ordering|
|**Hashing**|Hash category to fixed-size bucket|Very high cardinality (millions of categories)|Hash collisions; not reversible|
|**Embedding**|Learn dense vector representation|High-cardinality; neural networks|Requires sufficient training data to learn good embeddings|

> **Exam tip:** For SageMaker built-in algorithms, **one-hot encoding** is typically required for nominal categorical features. XGBoost handles label-encoded categoricals natively. Linear Learner always needs OHE.

---

### 2.8 Feature Scaling

Scaling ensures all features contribute proportionally to distance and gradient computations.

| Method                        | Formula                   | Output Range           | Use When                                                       |
| ----------------------------- | ------------------------- | ---------------------- | -------------------------------------------------------------- |
| **Min-Max Normalization**     | `(x - min) / (max - min)` | [0, 1]                 | Fixed range needed; bounded data; neural networks              |
| **Standardization (Z-score)** | `(x - μ) / σ`             | (-∞, ∞); mean=0, std=1 | Default choice; data approximately normal                      |
| **Robust Scaling**            | `(x - median) / IQR`      | Centered but unbounded | Outliers present; more robust than standardization             |
| **Max Abs Scaling**           | `x / max(                 | x                      | )`                                                             |
| **L2 Normalization**          | `x / ‖x‖₂`                | Unit norm per sample   | When direction matters more than magnitude (cosine similarity) |

**Which algorithms need scaling:**

|Needs Scaling|Does NOT Need Scaling|
|---|---|
|Linear / Logistic Regression|Decision Trees|
|SVM|Random Forest|
|KNN|XGBoost / GBT|
|K-Means|LightGBM|
|PCA|Naïve Bayes|
|Neural Networks||

> **Critical exam rule:** Always fit the scaler **only on training data** and apply the fitted scaler to validation and test data. Fitting on the full dataset causes **data leakage**.

---

### 2.9 Shuffling

Shuffling randomizes the order of training samples before each epoch.

**Why shuffle:**

- Prevents the model from learning order-based spurious patterns
- Ensures each mini-batch is a random sample → reduces gradient variance
- Particularly critical when data arrives sorted by class label — without shuffling, batches contain only one class

**When NOT to shuffle:**

- **Time series data** — shuffling destroys temporal dependencies; use time-ordered train/validation splits
- **Sequence models** — when order within a sequence is the signal

---

## 3. SageMaker AI — Data Processing, Training & Deployment

### 3.1 End-to-End SageMaker Workflow

```
Raw Data (S3)
      ↓
SageMaker Processing Job (preprocess / feature engineering / split)
      ↓
Processed Data (S3)
      ↓
SageMaker Training Job (train model on processed data)
      ↓
Model Artifacts (S3)
      ↓
SageMaker Model (register in Model Registry)
      ↓
SageMaker Endpoint (real-time) or Batch Transform (offline)
      ↓
SageMaker Model Monitor (continuous quality monitoring)
```

### 3.2 SageMaker Processing Jobs

- Spin up managed compute (EC2) → copy data from S3 → run your container → output to S3 → terminate compute
- Use for: data preprocessing, feature engineering, train/val/test splitting, model evaluation, bias analysis
- Built-in containers: **Scikit-learn**, **Spark** (with SparkMagic), **XGBoost**
- Custom containers: bring your own Docker image in ECR
- Fully managed: no cluster management; pay per job duration

```python
from sagemaker.sklearn.processing import SKLearnProcessor

processor = SKLearnProcessor(
    framework_version="1.0-1",
    instance_type="ml.m5.xlarge",
    instance_count=1,
    role=role
)
processor.run(
    code="preprocessing.py",
    inputs=[ProcessingInput(source="s3://bucket/raw/", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination="s3://bucket/processed/")]
)
```

### 3.3 SageMaker Training Jobs

- Pulls Docker image from ECR → spins up compute → copies training data from S3 → trains → saves artifacts to S3 → terminates
- Configurable: instance type, count, volume size, max runtime, Spot training, VPC config
- **Managed Spot Training** — up to 90% cost reduction; enable checkpointing to survive interruptions
- **Warm Pools** — keeps instances alive between iterative jobs (avoids cold start)

### 3.4 SageMaker Deployment (Recap)

|Mode|Use Case|
|---|---|
|**Real-Time Endpoint**|Synchronous predictions; persistent; low latency|
|**Serverless Inference**|Infrequent traffic; scales to zero|
|**Async Inference**|Large payloads; long inference time; non-blocking|
|**Batch Transform**|Offline scoring of full dataset; no endpoint|

---

## 4. SageMaker Ground Truth & Label Generation

### 4.1 What Is Ground Truth?

SageMaker Ground Truth is a **managed data labeling service** — it orchestrates human annotators to label raw data (images, text, audio, video) and produces labeled datasets for supervised ML training.

### 4.2 Workflow

```
Unlabeled Data (S3)
      ↓
Labeling Job (Ground Truth)
  ├── Task UI (built-in or custom)
  ├── Worker Pool (Mechanical Turk / Private / Vendor)
  └── Auto-labeling (Active Learning) — ML pre-labels high-confidence examples
      ↓
Labeled Dataset (JSON manifest in S3)
      ↓
Training (SageMaker Training Job)
```

### 4.3 Built-In Task Types

|Category|Task Types|
|---|---|
|**Image**|Image classification, Object detection (bounding box), Semantic segmentation, Image keypoint labeling|
|**Text**|Text classification, Named entity recognition (NER), Text span selection|
|**Video**|Video classification, Video object detection and tracking|
|**3D Point Cloud**|3D object detection, 3D semantic segmentation (for autonomous vehicle / LiDAR data)|

### 4.4 Automated Data Labeling (Active Learning)

- Ground Truth can **automatically label** a subset of data using a trained ML model
- **Process:**
    1. A small seed dataset is labeled by humans
    2. A model is trained on the seed labels
    3. Model labels remaining data with confidence scores
    4. High-confidence labels are accepted automatically (saved cost)
    5. Low-confidence examples are sent to human workers
    6. Human labels augment the training set → model improves iteratively
- Can reduce labeling cost by **up to 70%**
- Requires enough seed labels for the active learning model to be meaningful (~hundreds)

### 4.5 Output Format

Ground Truth outputs an **augmented manifest** — a JSONL file where each line is:

```json
{
  "source-ref": "s3://bucket/image.jpg",
  "label": 1,
  "label-metadata": {
    "confidence": 0.98,
    "class-name": "cat",
    "human-annotated": "yes",
    "type": "groundtruth/image-classification"
  }
}
```

This format is directly ingestible by SageMaker Training Jobs.

### 4.6 Worker Pools

|Pool|Description|Best For|
|---|---|---|
|**Amazon Mechanical Turk**|Public crowdsourced workforce; thousands of workers|General-purpose tasks; scalable; lower cost|
|**Private Workforce**|Your own employees or contractors; controlled via Amazon Cognito|Sensitive or proprietary data; domain expertise required|
|**AWS Marketplace (Vendor)**|Curated third-party annotation companies|Specialized domains (medical imaging, legal, NLP)|

### 4.7 Quality Control

- **Annotation consolidation** — multiple workers label same item; consensus algorithm selects final label
- **Ground Truth Plus** — fully managed labeling service where AWS manages the workforce and quality

---

## 5. Amazon Mechanical Turk (MTurk)

### 5.1 What It Is

MTurk is a **crowdsourcing marketplace** for tasks that require human intelligence (Human Intelligence Tasks — HITs). Used both standalone and as the Mechanical Turk worker pool in Ground Truth.

### 5.2 Use in ML Context

|Use Case|Description|
|---|---|
|**Data labeling**|Classify images, annotate text, transcribe audio|
|**Data collection**|Survey responses, preference rankings|
|**Model evaluation**|Rate model outputs for quality, relevance, safety|
|**RLHF preference data**|Compare two LLM responses; select preferred one|
|**Content moderation**|Flag inappropriate content for training safety models|

### 5.3 Key Concepts

|Concept|Description|
|---|---|
|**HIT** (Human Intelligence Task)|A single unit of work (label this image)|
|**Requester**|Entity posting HITs (you / your organization)|
|**Worker (Turker)**|Human completing HITs|
|**Reward**|Payment per completed HIT (set by requester)|
|**Qualification**|Requirements workers must meet (location, accuracy score, approval rate)|
|**Approval Rate**|% of HITs a worker has had approved; filter workers with >95% for higher quality|

### 5.4 Quality vs. Ground Truth Integration

- MTurk accessed directly via MTurk API or via **Ground Truth** (which handles the orchestration)
- Ground Truth's annotation consolidation handles inter-worker disagreement automatically
- For sensitive data: use Private Workforce (not MTurk) to keep data within your org

---

## 6. SageMaker Data Wrangler

### 6.1 What It Is

SageMaker Data Wrangler is a **low-code data preparation tool** inside SageMaker Studio that provides a visual interface for importing, transforming, and exporting data for ML.

### 6.2 Data Sources

- Amazon S3 (CSV, Parquet, JSON, ORC, TSV)
- Amazon Athena
- Amazon Redshift
- Amazon EMR
- Snowflake
- Databricks

### 6.3 Core Capabilities

|Capability|Detail|
|---|---|
|**Import**|Connect to data sources; preview data in browser|
|**Transform**|300+ built-in transforms: encoding, imputation, scaling, type cast, string ops, date extraction|
|**Custom Transform**|Write Python (Pandas), PySpark, or SQL transformations|
|**Data Insights**|Auto-generates statistics and visualizations per feature|
|**Quick Model**|Train a quick validation model to check feature quality before full training|
|**Bias Report**|Run Clarify pre-training bias analysis within the UI|
|**Explainability Report**|SHAP feature importance within the UI|
|**Export**|Export flow as: SageMaker Pipeline step, Processing Job, Feature Store ingestion, Python code|

### 6.4 Data Wrangler Flow

A Data Wrangler flow (`.flow` file) is a **JSON-serialized DAG** of data transformations:

```
[Data Source] → [Transform 1] → [Transform 2] → ... → [Export]
```

- Flows are **reproducible and versionable** — check into Git
- Can be re-executed as SageMaker Processing Jobs in production pipelines

### 6.5 When to Use Data Wrangler vs Alternatives

|Scenario|Tool|
|---|---|
|Interactive, low-code EDA and prep|Data Wrangler|
|Production ETL at scale|AWS Glue or SageMaker Processing (Spark)|
|Complex SQL transformations|Athena or Redshift|
|Automated ML feature engineering|SageMaker Autopilot|

---

## 7. SageMaker Studio & Canvas

### 7.1 SageMaker Studio

SageMaker Studio is the **unified, web-based IDE** for the full ML lifecycle.

**Components accessible from Studio:**

|Component|Purpose|
|---|---|
|**JupyterLab / Notebooks**|Interactive development; Spark, Python, R kernels|
|**Data Wrangler**|Low-code data preparation|
|**Feature Store**|Store and retrieve features|
|**Experiments**|Track training runs, metrics, hyperparameters|
|**Pipelines**|Build, schedule, monitor ML pipelines|
|**Autopilot**|AutoML|
|**Model Registry**|Version and approve models|
|**Model Monitor**|Production drift monitoring|
|**Debugger**|Training job inspection|
|**JumpStart**|Pre-trained models and solution templates|
|**Canvas**|No-code ML (via Studio interface)|

**Studio Domain:** Organizational isolation unit; each user has a profile with isolated file system (EFS) and configurable app settings.

### 7.2 SageMaker Canvas

Canvas is a **no-code ML application** for business analysts who want to build and use ML models without writing code.

|Feature|Detail|
|---|---|
|**Data import**|S3, Redshift, Snowflake, Salesforce, Google Analytics|
|**AutoML**|Automated model training (wraps Autopilot)|
|**Problem types**|Binary classification, multi-class, regression, time series forecasting, text classification, image classification|
|**Predictions**|Single prediction (row-by-row) or batch prediction|
|**What-if analysis**|Change input values and see how prediction changes|
|**Model sharing**|Share built models with data scientists for further refinement in Studio|
|**Collaboration**|Data scientists can import Canvas models into Studio for fine-tuning|
|**Pricing**|Session-based billing (per hour of Canvas usage)|

**Canvas Time Series Forecasting:**

- Built-in holiday calendars per country
- Handles missing values and irregular time steps
- Generates probabilistic forecasts (confidence intervals)
- Uses AutoML under the hood (DeepAR, Prophet, etc.)

---

## 8. Partial Dependence Plots (PDP) & SHAP

### 8.1 Partial Dependence Plots (PDP)

A PDP shows the **marginal effect of one or two features** on the predicted outcome, averaging out all other features.

**How it's computed:** For feature `X_j`, for each value `v` in the range of `X_j`:

1. Set all rows' value of `X_j` to `v`
2. Get model predictions for all rows
3. Average the predictions → that's the PDP value at `v`

```
PDP(v) = (1/n) Σ f(x_1, ..., x_{j-1}, v, x_{j+1}, ..., x_p)
```

**Interpretation:**

- Flat PDP → feature has little marginal effect
- Upward slope → higher feature value → higher prediction
- U-shaped → non-linear relationship
- 2D PDP → shows interaction between two features

**Limitations:**

- Assumes feature independence — if feature is correlated with others, setting it independently is unrealistic
- Averages out heterogeneous effects (subgroup effects hidden) → use **ICE plots** (Individual Conditional Expectation)

**ICE Plots:** One line per sample showing how prediction changes as feature value changes — reveals heterogeneous effects that PDP averages hide.

---

### 8.2 SHAP (SHapley Additive exPlanations)

SHAP provides **consistent, theoretically grounded feature attribution** for any model, based on cooperative game theory.

**Core idea:** The SHAP value for feature `i` is its **average marginal contribution** to the prediction across all possible coalitions (subsets) of features.

```
SHAP value for feature i = E[f(x)] when feature i is present  -  E[f(x)] when feature i is absent
(averaged across all possible subsets of other features)
```

**Additive property:** Sum of all SHAP values + base value (mean prediction) = actual model prediction for that sample:

```
f(x) = base_value + SHAP₁ + SHAP₂ + ... + SHAPₙ
```

#### SHAP Visualization Types

|Plot|What It Shows|
|---|---|
|**Waterfall Plot**|Single prediction: each feature's contribution stacked from base to final prediction|
|**Force Plot**|Single prediction: horizontal visualization of feature contributions pushing prediction higher (red) or lower (blue)|
|**Beeswarm / Summary Plot**|Global: all features; each point = one sample; position = SHAP value; color = feature value|
|**Bar Plot**|Global mean absolute SHAP value per feature (global importance ranking)|
|**Dependence Plot**|SHAP value vs feature value for one feature (colored by interaction feature)|
|**Heatmap**|All features × all samples as a matrix|

#### SHAP Variants by Model Type

|Variant|Model Type|Speed|
|---|---|---|
|**TreeSHAP**|Tree-based models (XGBoost, Random Forest, LightGBM)|Fast; exact O(TLD²)|
|**LinearSHAP**|Linear models (Logistic Regression, Linear SVC)|Fast; exact|
|**DeepSHAP**|Neural networks|Approximate; based on DeepLIFT|
|**KernelSHAP**|Any model (model-agnostic)|Slow; approximate; uses weighted linear regression|
|**GradientSHAP**|Neural networks + gradient computation|Approximate|

#### SHAP in SageMaker Clarify

- Clarify runs KernelSHAP or TreeSHAP depending on model type
- Generates a **global SHAP report** (mean absolute SHAP per feature) and per-sample SHAPs
- Stored as JSON in S3; viewable in Studio or Data Wrangler
- Used as baseline for **Feature Attribution Drift** monitoring

---

## 9. SageMaker Feature Store

### 9.1 What It Is

SageMaker Feature Store is a **centralized repository** for storing, retrieving, sharing, and reusing ML features across teams and models.

**Problems it solves:**

- Feature recomputation — same feature computed independently by multiple teams
- Training-serving skew — different code computes features at training vs inference time
- Feature discovery — no central catalog to find existing features
- Point-in-time correctness — need features as they existed at a past training time

---

### 9.2 Key Concepts

|Concept|Description|
|---|---|
|**Feature Group**|Logical container of related features; like a table with a schema|
|**Record**|A single entity's feature values at a point in time|
|**Record Identifier**|Unique ID for each entity (e.g., customer_id, product_id)|
|**Event Time**|Timestamp of when the feature values were observed; enables time-travel queries|
|**Online Store**|Low-latency (single-digit ms) DynamoDB-backed store for real-time inference|
|**Offline Store**|S3-backed columnar store (Parquet) with Glue catalog integration; for training|

---

### 9.3 Dual Store Architecture

```
Feature Engineering (Spark / Python)
      ↓
PutRecord API → writes to both stores simultaneously
      ├── Online Store (DynamoDB) → real-time inference lookups
      └── Offline Store (S3 + Glue Catalog) → training dataset creation
```

**Online Store:**

- Single record lookup by `RecordIdentifier` → returns latest feature values
- Latency: ~1–5ms → suitable for real-time endpoint inference
- No SQL; key-value lookup only

**Offline Store:**

- Append-only S3 log with all historical records and event times
- Queryable via **Amazon Athena** (Glue catalog auto-created)
- Supports **point-in-time correct queries** — get feature values as they existed at training time (prevent leakage)
- Data format: Parquet (columnar, efficient for analytical queries)

---

### 9.4 Point-in-Time Correctness

Critical for training dataset creation:

```sql
-- Get feature values as they existed at or before the label event time
-- Prevents future leakage — don't use features that were updated after the label was observed
SELECT a.customer_id, a.label_timestamp, b.feature1, b.feature2
FROM labels a
LEFT JOIN feature_store b
ON a.customer_id = b.customer_id
AND b.event_time <= a.label_timestamp
-- Take the most recent feature record before the label event
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY a.customer_id, a.label_timestamp
    ORDER BY b.event_time DESC
) = 1
```

---

### 9.5 Feature Store Integration

|Integration|How|
|---|---|
|**SageMaker Training**|Query offline store via Athena; use results as training data|
|**SageMaker Processing**|Write engineered features directly to Feature Store|
|**Real-Time Endpoints**|Inference code calls `GetRecord` on online store at prediction time|
|**Data Wrangler**|Export transformation flow output directly to Feature Store|
|**SageMaker Pipelines**|Feature ingestion as a pipeline step|

---

## 10. AWS Glue

### 10.1 What Is AWS Glue?

AWS Glue is a **fully managed serverless ETL (Extract, Transform, Load) service** built on Apache Spark. It handles data discovery, cataloging, transformation, and loading without managing servers.

### 10.2 Core Components

|Component|Description|
|---|---|
|**Data Catalog**|Central metadata repository (databases, tables, schemas, partitions) — like an Apache Hive Metastore|
|**Crawler**|Automatically scans data sources; infers schema; populates Data Catalog|
|**ETL Jobs**|Spark-based (or Python Shell) transformation scripts; serverless|
|**Triggers**|Schedule or event-based job execution|
|**Workflows**|Chain multiple crawlers and jobs with dependencies|
|**Connections**|JDBC connections to databases (RDS, Redshift, MySQL, etc.)|
|**Glue Studio**|Visual ETL job builder|
|**DataBrew**|No-code data preparation|
|**Data Quality**|Managed data quality rules and monitoring|

### 10.3 Glue Data Catalog

- **Single source of truth** for metadata across the AWS analytics ecosystem
- Tables in the Data Catalog are queryable by: **Athena**, **EMR**, **Redshift Spectrum**, **SageMaker**
- Organized as: `Catalog → Databases → Tables → Partitions`
- **Partitioning** — Glue catalog stores partition metadata; Athena uses it to skip irrelevant S3 prefixes
- **Schema evolution** — update table schemas without rewriting data (add columns, change types)
- **Lake Formation integration** — fine-grained access control over catalog tables

### 10.4 Glue Crawlers

- Scan S3, JDBC databases, DynamoDB to **auto-discover schema**
- Infer data types and partition structure
- Run on schedule or on-demand
- Output: tables in Glue Data Catalog with schema
- **Classifier** — custom logic for non-standard formats (custom grok pattern, XML schema, JSON path)

### 10.5 Glue ETL Jobs

**Job Types:**

|Type|Runtime|Use Case|
|---|---|---|
|**Spark**|Distributed PySpark / Scala Spark|Large-scale transformation|
|**Python Shell**|Single-node Python|Small datasets; simple scripts; data orchestration|
|**Spark Streaming**|Spark Structured Streaming|Near-real-time ETL from Kinesis, Kafka, S3|
|**Ray**|Distributed Python (Ray)|Python-first distributed workloads|

**Glue DynamicFrame:**

- Glue's extension of Spark DataFrame
- Handles **schema inconsistencies** natively — fields with multiple types, missing fields
- `ResolveChoice` — decide how to handle ambiguous types
- Convert to/from Spark DataFrame with `.toDF()` / `DynamicFrame.fromDF()`

**Worker Types:**

|Worker|vCPU|Memory|Best For|
|---|---|---|---|
|G.1X|4|16 GB|Standard ETL|
|G.2X|8|32 GB|Memory-intensive joins|
|G.4X|16|64 GB|Very large datasets|
|G.8X|32|128 GB|Largest scale ETL|
|Z.2X|8|64 GB|ML transforms (FindMatches)|

**Glue ML Transforms:**

- **FindMatches** — identifies duplicate or matching records across datasets (entity resolution/deduplication) using ML

---

## 11. AWS Glue Studio

### 11.1 What It Is

Glue Studio is a **visual ETL tool** — drag-and-drop interface to build Glue ETL jobs without writing Spark code.

### 11.2 Key Features

|Feature|Detail|
|---|---|
|**Visual DAG builder**|Connect source → transform → target nodes visually|
|**Source nodes**|S3, Glue Catalog, JDBC, Kinesis, Kafka|
|**Transform nodes**|ApplyMapping, Filter, Join, Union, SelectFields, DropFields, FillMissingValues, SplitFields|
|**Target nodes**|S3 (Parquet, CSV, JSON, ORC), Glue Catalog, JDBC, Redshift|
|**Code view**|Toggle between visual and PySpark code; auto-generated code is editable|
|**Job monitoring**|Visual run history; task-level metrics|
|**Notebook integration**|Interactive development before deploying as a job|

### 11.3 Glue Studio vs Data Wrangler

|Dimension|Glue Studio|SageMaker Data Wrangler|
|---|---|---|
|Primary use|ETL data pipelines (data engineering)|ML feature preparation (data science)|
|Scale|Serverless Spark (petabyte scale)|Managed Processing Job (ML scale)|
|User|Data engineer|Data scientist|
|Output|Data lake (S3), Redshift|SageMaker training data, Feature Store|
|ML integration|Exports to S3 for downstream ML|Direct Feature Store and Pipeline integration|

---

## 12. AWS Glue Data Quality

### 12.1 What It Is

Glue Data Quality provides **managed data quality checks** within ETL pipelines — detect, alert, and block bad data before it reaches downstream systems or ML models.

### 12.2 DQDL (Data Quality Definition Language)

Rules are written in DQDL — a simple declarative language:

```
Rules = [
    IsComplete "customer_id",                              -- no nulls in this column
    IsUnique "customer_id",                               -- no duplicates
    ColumnValues "age" between 0 and 120,                 -- valid range
    ColumnValues "email" matches ".*@.*\\..*",            -- regex format check
    RowCount > 1000,                                       -- minimum row count
    ColumnCorrelation "feature1" "feature2" between -0.9 and 0.9,  -- correlation check
    IsComplete "label" with threshold >= 0.95             -- allow up to 5% missing
]
```

### 12.3 Integration Points

|Where Applied|Method|
|---|---|
|**Glue ETL Job**|Add `EvaluateDataQuality` transform node in Glue Studio|
|**Data Catalog**|Scheduled data quality evaluation on catalog tables|
|**Standalone**|Run as independent Glue job|

### 12.4 Actions on Failure

|Action|Description|
|---|---|
|**Log**|Record violations; job continues|
|**Alert**|Publish to CloudWatch; trigger SNS notification|
|**Fail Job**|Stop ETL job if quality rules violated (gate before bad data reaches ML training)|

### 12.5 Importance for ML

- Prevents **garbage in, garbage out** — bad training data produces bad models
- Quality metrics published to CloudWatch → alert when production data quality degrades (early warning for data drift)
- Required for **ML governance** — document data quality before model training

---

## 13. AWS Glue DataBrew

### 13.1 What It Is

Glue DataBrew is a **no-code, visual data preparation tool** for data analysts — 250+ built-in transformations without writing code.

### 13.2 Core Concepts

|Concept|Description|
|---|---|
|**Dataset**|Connected data source (S3, Glue Catalog, Redshift, JDBC, Data Exchange)|
|**Project**|Interactive workspace for exploring and transforming a dataset|
|**Recipe**|Ordered sequence of transformation steps applied to a dataset|
|**Job**|Executes a Recipe at scale on full dataset; output to S3|
|**Profile**|Auto-generated statistical summary of dataset (distributions, nulls, correlations)|
|**Ruleset**|Data quality rules applied during profiling or job execution|

### 13.3 Built-In Transformations

|Category|Examples|
|---|---|
|**Filter**|Remove rows by condition, deduplication, outlier removal|
|**Clean**|Fix whitespace, case normalization, special character removal|
|**Format**|Date parsing, number formatting, string manipulation|
|**Aggregate**|Group by + aggregate (sum, mean, count)|
|**Nest / Unnest**|Flatten JSON arrays; structure/destructure|
|**Join / Append**|Combine multiple datasets|
|**Encode**|One-hot encoding, label encoding|
|**Scale**|Min-max normalization, Z-score standardization|
|**Impute**|Fill missing with mean, median, mode, custom value|

### 13.4 Handling PII in DataBrew Transformations

DataBrew provides specific transforms for **detecting and protecting PII**:

#### PII Detection

- **Profile job** automatically detects PII columns using pattern matching and ML-based entity detection
- Detected PII types: **NAME, ADDRESS, EMAIL, PHONE, SSN, CREDIT_CARD, DATE_OF_BIRTH, PASSPORT, DRIVER_LICENSE, IP_ADDRESS, URL, BANK_ACCOUNT**
- Profile report flags columns containing PII with their entity type and % of values detected

#### PII Handling Transforms

|Transform|Method|Description|
|---|---|---|
|**Redact**|Replace with fixed string|`John Smith` → `*****`|
|**Mask**|Replace with format-preserving mask|`john@email.com` → `****@email.com`|
|**Hash**|Apply SHA-256 or MD5|`123-45-6789` → `abc123...` (one-way)|
|**Encrypt**|AES-256 encryption with KMS key|Reversible; decrypt later if needed|
|**Delete**|Remove the entire column|When column is not needed for ML|
|**Substitute**|Replace with synthetic value|Replace real name with fake name|
|**Format**|Partial reveal — show last 4 digits only|`****-****-****-1234`|

**DataBrew + KMS:**

- `Encrypt` transform uses AWS KMS CMK — only holders of the KMS key can decrypt
- Encrypted output stored in S3 remains protected even if S3 bucket access is obtained

#### Best Practice for ML PII Handling

```
Raw data with PII (S3, restricted access)
      ↓
DataBrew Profile Job → identify PII columns
      ↓
DataBrew Recipe → hash/encrypt/remove PII columns
      ↓
DataBrew Job → output PII-free dataset to separate S3 bucket
      ↓
SageMaker Training Job → trains on PII-free data
```

---

## 14. AWS Athena

### 14.1 What Is Athena?

Amazon Athena is a **serverless, interactive SQL query engine** for querying data directly in **Amazon S3** without loading it into a database. Based on **Presto** (open-source distributed SQL engine).

- No infrastructure to manage; no clusters to provision
- Pay per query: **$5 per TB of data scanned**
- Supports: CSV, JSON, Parquet, ORC, Avro, TSV, compressed formats (gzip, Snappy, LZO)
- Query results stored in S3; accessible via console, API, JDBC/ODBC

### 14.2 Athena and Glue Data Catalog

Athena uses the **AWS Glue Data Catalog** as its metadata store — they are deeply integrated:

```
S3 Data
      ↓
Glue Crawler → auto-discovers schema → Glue Data Catalog (database + table)
      ↓
Athena reads table definition from Glue Catalog → queries S3 data directly
      ↓
Query results → S3 (results bucket) → consumed by application / SageMaker
```

- Athena databases = Glue Catalog databases
- Athena tables = Glue Catalog tables
- Any table registered in Glue Catalog is immediately queryable in Athena
- Changes to schema in Glue Catalog are immediately reflected in Athena queries

**Athena Federated Query:**

- Query data sources beyond S3 using **Lambda-based connectors**
- Supported: RDS, DynamoDB, Redshift, ElasticSearch, CloudWatch Logs, DocumentDB, custom JDBC sources
- Combine S3 and non-S3 data in a single SQL query

---

### 14.3 Athena Performance Optimization

**Cost and performance are the same problem** — Athena charges per byte scanned; reducing scan = faster + cheaper.

#### 1. Use Columnar Formats

|Format|Scan Efficiency|Why|
|---|---|---|
|**Parquet**|Excellent|Column-level skip; dictionary encoding; per-column compression|
|**ORC**|Excellent|Column-level skip; stripe-level min/max statistics; Bloom filters|
|**CSV / JSON**|Poor|Full row scan; cannot skip columns|

**Rule:** Always convert raw CSV/JSON to Parquet or ORC before querying at scale.

#### 2. Use Compression

|Codec|Splittable|Best For|
|---|---|---|
|**Snappy**|Yes (Parquet/ORC)|Default for Parquet; fast decompress|
|**GZIP**|No (standalone)|Higher compression ratio; not splittable in CSV|
|**LZO**|Yes|Legacy; avoid for new data|
|**ZSTD**|Yes (Parquet/ORC)|Best ratio + speed; modern choice|

**Rule:** Splittable compression allows Athena to parallelize reading large files across workers.

#### 3. Partition Your Data

- Partition S3 data by query predicates (e.g., `year=2024/month=01/day=15/`)
- Declare partitions in Glue Catalog
- Athena's partition pruning skips irrelevant S3 prefixes entirely → dramatic scan reduction

```sql
-- Query only scans s3://bucket/year=2024/month=01/ prefix
SELECT * FROM sales WHERE year='2024' AND month='01';
```

- **Partition projection** — define partition logic in table properties; Athena computes partitions without Glue Catalog entries → eliminates `MSCK REPAIR TABLE` overhead

#### 4. File Size Optimization

- Too many small files → high S3 API overhead (list + open per file)
- Optimal file size: **128MB–1GB per file** in Parquet/ORC
- Coalesce small files using Glue ETL or EMR before Athena queries
- Use **Glue compaction** or **OPTIMIZE** (Iceberg tables) to compact small files periodically

#### 5. Use Workgroups

- Organize queries by team; set **per-query data scanned limits** (e.g., 10 GB max per query)
- Set **per-workgroup S3 results location**
- Enforce encryption on results
- Track cost per team via workgroup usage metrics

#### 6. Query Optimization Tips

- `SELECT` only needed columns (column pruning)
- Filter on partition columns first
- Avoid `SELECT *`; avoid `ORDER BY` on large result sets (forces single-node sort)
- Use `APPROXIMATE COUNT DISTINCT` (`approx_distinct()`) for cardinality estimates
- Push aggregations and filters before joins

---

### 14.4 ACID Transactions in Athena

By default, S3 is **not ACID-compliant** — no atomic updates, no isolation, potential dirty reads. Athena supports ACID transactions via **Apache Iceberg**, **Apache Hudi**, and **Apache Delta Lake** table formats.

#### Apache Iceberg on Athena (Primary Exam Focus)

Iceberg provides full ACID semantics on S3 data:

|ACID Property|How Iceberg Provides It|
|---|---|
|**Atomicity**|All changes in a transaction either fully commit or are rolled back; managed via metadata files|
|**Consistency**|Table always transitions between valid states; schema and partition evolution tracked|
|**Isolation**|Snapshot isolation — each query reads from a consistent snapshot; concurrent writers don't interfere|
|**Durability**|Committed metadata files stored in S3; transaction log is immutable|

**Iceberg Key Capabilities on Athena:**

|Capability|SQL|
|---|---|
|**Insert**|`INSERT INTO iceberg_table VALUES (...)`|
|**Update**|`UPDATE iceberg_table SET col=val WHERE condition`|
|**Delete**|`DELETE FROM iceberg_table WHERE condition`|
|**Merge (Upsert)**|`MERGE INTO iceberg_table USING source ON condition WHEN MATCHED THEN UPDATE ... WHEN NOT MATCHED THEN INSERT ...`|
|**Time Travel**|`SELECT * FROM iceberg_table FOR SYSTEM_TIME AS OF TIMESTAMP '2024-01-01'`|
|**Rollback**|`ALTER TABLE iceberg_table EXECUTE rollback(snapshot_id)`|
|**Compaction**|`ALTER TABLE iceberg_table OPTIMIZE REWRITE DATA USING BIN_PACK`|
|**Expire Snapshots**|`ALTER TABLE iceberg_table EXECUTE expire_snapshots(...)`|

**Iceberg Metadata Structure:**

```
S3 Table Prefix
├── data/          ← Parquet data files
└── metadata/
    ├── v1.metadata.json     ← Table metadata (schema, partitions, snapshot history)
    ├── snap-xxx.avro        ← Snapshot manifest lists
    └── manifests/           ← Manifest files (lists of data files per snapshot)
```

---

### 14.5 Fine-Grained Access Control in Athena

Athena integrates with **AWS Lake Formation** for column-level and row-level access control.

#### Lake Formation Data Filters on Athena

Without Lake Formation: S3 bucket/prefix level access only (everyone who can query a table sees all rows and columns).

With Lake Formation:

|Control Level|What It Does|
|---|---|
|**Database-level**|Grant/deny access to entire database|
|**Table-level**|Grant/deny access to specific tables|
|**Column-level**|Grant access to specific columns only — excluded columns appear as if they don't exist|
|**Row-level**|Filter rows based on column values — user only sees rows matching their filter|
|**Cell-level**|Combination: filter specific cells to specific users|

**How it works with Athena:**

```
Athena Query → Lake Formation IAM-integrated check → applies data filter
      ↓
Query only scans permitted columns and rows → results returned without restricted data
```

**Configuration:**

1. Enable Lake Formation as the metadata catalog for Athena
2. Revoke default IAMAllowedPrincipals from tables
3. Grant fine-grained permissions to specific IAM users/roles/groups

**Use case for ML:**

- Data science team: access to all features for model training
- Business analyst: access to aggregated metrics only; no PII columns
- Compliance team: access to audit columns; no model features
- All enforced by Lake Formation without changing data or creating copies

---

## 15. Quick Reference Summary

### Feature Engineering Decision Tree

```
Continuous numerical feature
├── Skewed? → Log or Box-Cox transform
├── Outliers? → Winsorize (cap) or robust scaling
├── Missing? → Median impute (skewed) or mean (normal) + missing indicator
└── Need to discretize? → Quantile binning

Categorical feature
├── Ordinal? → Label/Ordinal encode
├── Nominal, low cardinality (<20)? → One-Hot Encoding
├── Nominal, high cardinality? → Target encoding (with cross-val) or Frequency encoding
└── For neural network? → Learned embeddings

Before training
├── Scale features? → Standardize (Z-score) for linear/distance models
├── Tree models? → No scaling needed
└── Always → Fit scaler/encoder on TRAIN only; apply to val/test
```

### AWS Analytics Tool Selection

|Need|Service|
|---|---|
|Serverless SQL on S3|Athena|
|Visual ETL, serverless Spark|Glue Studio + Glue ETL|
|Auto-discover schema from S3|Glue Crawler|
|No-code data prep|Glue DataBrew|
|Data quality rules in pipeline|Glue Data Quality|
|Central metadata catalog|Glue Data Catalog|
|Managed Spark/Hadoop cluster|EMR on EC2|
|Serverless Spark job|EMR Serverless|
|Low-code ML feature prep|SageMaker Data Wrangler|
|Feature reuse across teams|SageMaker Feature Store|
|No-code ML for business users|SageMaker Canvas|
|ACID transactions on S3|Athena + Iceberg|
|Column/row-level access on S3|Lake Formation + Athena|
|Label raw training data|SageMaker Ground Truth|
|Human review of predictions|Amazon A2I|
|Crowdsourced labeling|Amazon Mechanical Turk|

### Glue Tool Comparison

|Tool|User|Code?|Scale|Output|
|---|---|---|---|---|
|**Glue ETL**|Data Engineer|PySpark|Petabyte|S3, Redshift, JDBC|
|**Glue Studio**|Data Engineer|Visual (auto-generates code)|Petabyte|S3, Redshift, JDBC|
|**Glue DataBrew**|Data Analyst|No-code|Large datasets|S3, Glue Catalog|
|**Data Wrangler**|Data Scientist|Low-code|ML scale|Feature Store, S3|
|**Canvas**|Business Analyst|No-code|N/A (AutoML)|Predictions|