## Types of Data:
1. Structured: Organized in a schema (like RDS), in columns and rows and easily queriable.
2. Unstructured: Doesn't have a predefined structure and easily queriable without pre-processing (like raw text dumps)
3. Semi-Structured: Partially structured via something like tags or categorized (like JSON files) and hence has a schema but inconsistent

## Properties of Data
1. **Volume**: The size or amount of data the organization is dealt in at that time. Useful to understand how to store given size of data and access them (higher the size difficult the scalability gets)
2. Velocity: Refers to the speed at which new data is generated collected and processed. Required to be understand to build system when rapid ingestion, real-time streaming, processing and high such data transfer and  access activities are performed
3. Variety: The type of data being handled and what's it's source. Data in real world are unclean and come in different format and hence to use them these different types of input data need to be made into an uniform type.

## Data Sources:
1. JDBC (Java Database Connectivity) - Platform-independent but Language dependent.
2. ODBC (Open Database Connectivity) - Platform-dependent but Language-independent
3. Logs
4. APIs
5. Streams

## Data Formats:
1. CSVs: These are for smaller datasets. They can be made editable and useful as exports/imports from databases. Quite useful when different systems need to access the same data.
2. JSON: Sem-structured nested data format. These are used in web-based interactions and as configuration files. NoSQL uses JSON based definition for schemas.
3. Avro: Binary format that stores both data and schema. Used in Bid Data and when the schema is dynamically. Ex: Kafka, Hadoop, Spark
4. Parquet: Allows for efficient compression and encoding schemas. This is used when column-based data handling is preferred over row based access hence optimizing I/O operations. Ex: AWS Redshift Spectrum

# Data Storage
## Data Warehouses (AWS Red Shift):
A centralized repository optimized for analysis where data from different sources is stored in structured format. Useful when the process is **ETL** oriented. It is typical useful when data is:
1. ETL process is done
2. Form OLAP tasks and analysis
3. **STAR and Snowflake Schema** is preferred
4. Read-Heavy operations

## Data Lakes (AWS S3):
A storage that holds large amount of raw unprocessed data which can be structured, unstructured or any data type. Useful when the process is **ELT** oriented. It is useful when data is:
1. Large volume and no pre-defined schema
2. Needs to be just loaded
3. Batch, real-time or streaming
4. Data Transformation needs to be performed and explored

## Data Lakehouse (AWS Lake Formation)
Hybrid data architecture that combines the best features of data lakes and data warehouses, aiming to provide the performance reliability and capabilities of a data warehouse while maintaining the flexibility, scale and low-cost storage of data lakes. It is useful when:
1. Data is both structured and unstructured
2. Allows schema-in-write and schema-in-read
3. Useful for both analystics and machine learning tasks
4. Helps in ACID transaction performance on Big Data

## Data Mesh
Data Mesh design allows domain-teams to own their own data but follows a centralized federated governance and standards. It's also called **Domain-based data management**. Example: If analytics team needs to access products data, they will access the products data domain stored and not the raw data itself. 

# ETL Pipelines
Defined as **Extract - Transform - Load** and used to make ingested data useful and turned into information. **AWS Glue** can perform these from end to end. For custom orchestrations, EventBridge, Lambdas, Step Functions and others can be used.

**Extract**:
1. Retrieve the data from the sources such as APIs, databases, flat files and others
2. Ensure the data being sources is integral and not corrupted
3. Can be done real-time or batch wise

**Transform**:
1. Data cleansing
2. Data enrichment
3. Data formatting
4. Data aggregation
5. Data Encode/Decoding
6. Handling interpolations

**Load**:
1. Move the data to the data storage (warehouses or RDS)
2. Can be done in batches or streams
3. Similar to extract, loading, data integrity needs to be maintained

# AWS S3
AWS S3 is a vital data services provided. Some of the major points to be remembered are:
1. Supports maximum of 5 TB size per bucket
2. Metadata can be added which supports text
3. Maximum of 10 tags can be added
4. S3 is very highly durable .i.e. one object out of 10,000,000 object will be lost in the duration of 10000 years
5. S3 also has high availability .i.e. object are only not available for 53 minutes in a year

## S3 Bucket Policy:
Bucket policies can be used across different buckets over cross-accounts. There are two key access control lists (ACLs); Object ACL for finer grained control on data access and Bucket ACL for more broader control. Bucket level JSON based policies can be used which provides an effective way to control what service or user can allowed or denied to access

*Note:
Public access: Any anonyms web user can access the objects
IAM User access: Add specific permission what the accessing users can perform
IAM Role access: for other AWS services like EC2, lambdas and others to access the objects
Bucket policy: IAM user from another account to access the bucket. To access the bucket IAM or bucket policy should allow with no explicit deny*

## S3 Versioning:
It allows bucket level version where objects can be protected from unintended deletes. By default the version is null. Note that when enabled it does not version previous existing data, for which S3 Batch Versioning needs to be performed.

## S3 Replication
For replication of objects (for backups) below should be noted:
- Versioning needs to be enabled
- Buckets where replication will be done can be of different accounts
- Copying occurs is asynchronous
- Requires IAM permission to perform the copying to S3
- Similar to versioning, Batch replication needs to be used to replicate existing data
- Objects deleted in main bucket can be deleted and marked as deleted in replicated bucket
- Chaining of replication is not possible .i.e. when bucket 1 is replicated by bucket 2 and same with bucket 3; objects of bucket 1 would not be replicated in bucket 3.

It can be done in two different ways:
1. CRR (Cross region replication) - Used for compliance, where lower latency access is not required, replication across accounts
2. SRR (Same region replication) - Used for log aggregation and live replication

## S3 Storage Classes
1. **AWS S3 Standard**:
   It has Low latency and can be frequently accessed. It can only sustain 2 concurrent latency failures. 
   Use Case: Big Data, Applications (Web/Mobile), Content Access
   
2. **AWS S3 Standard IA**:
   Compared to Standard, S3 has less frequent access but lower costs.
   Use Case: Backups
   
3. **AWS S3 One Zone IA**:
   One Zone is similar to Standard IA but has high durability in given specific regional zone but reduced availability (99.95%) 
   Use Case: Secondary Backups (data which is already on-premise or can be re-created)
   
4. **AWS S3 Glacier Instant**:
   It quite useful as lowers cost for archival and backups. But this incurs Storage and Retrieval costs. 
   - Instant type allows for data access across quarters with minimum 90 days storage.
   - Flexible is similar to instant but provides three ways to configure the availability for retrieval. Expediten: 1-5 minutes, Standard: 3-5 hours; Bulk: 5-12 hours
   - Deep Archive allows for long term storage 
   
5. **AWS S3 Intelligent Tiering**:
   It requires a small monitoring and tiering fee but the retrieval is free. It moves the object to different access tiers automatically based on usage. The available tiers are:
   - Default tier: Frequent Access
   - Infrequent tier: Access only after 30 days
   - Archive tier: Access only after 90 days
   - Bulk Archive tier: Access only after 90 - 700 days (configurable)
   - Deep Archive tier: Access only after 180 - 700 days (configurable)

| S3 Class                          | Access Pattern                                   | Retrieval                      | AZ / Durability | Min. Storage | Cost                | **Typical Use Case / Exam Keyword**                                                     |
| --------------------------------- | ------------------------------------------------ | ------------------------------ | --------------- | ------------ | ------------------- | --------------------------------------------------------------------------------------- |
| **S3 Standard**                   | **Frequently accessed**                          | **Immediate, ms**              | **Multi-AZ**    | None         | $$$                 | **General purpose**, ML datasets, data lakes, web/mobile apps, frequently accessed data |
| **S3 Express One Zone**           | **Very frequently accessed + latency-sensitive** | **Very fast, single-digit ms** | **Single AZ**   | None         | $$                  | **High-performance ML workloads**, low-latency data access, frequently accessed data    |
| **S3 Intelligent-Tiering**        | **Unknown / changing access pattern**            | Immediate for active tiers     | **Multi-AZ**    | None         | $$ + monitoring fee | **Don't know how frequently data will be accessed**; automatically optimizes cost       |
| **S3 Standard-IA**                | **Infrequently accessed** but needs fast access  | **Immediate, ms**              | **Multi-AZ**    | **30 days**  | $                   | **Backups**, disaster recovery, long-lived data accessed occasionally                   |
| **S3 One Zone-IA**                | **Infrequently accessed**                        | **Immediate, ms**              | **Single AZ**   | **30 days**  | $                   | **Re-creatable secondary data**, secondary backups, thumbnails                          |
| **S3 Glacier Instant Retrieval**  | **Rarely accessed (~quarterly)**                 | **Immediate, ms**              | **Multi-AZ**    | **90 days**  | Very $              | **Archive that still needs instant access**, medical images, archived media             |
| **S3 Glacier Flexible Retrieval** | **Rarely accessed (~1–2×/year)**                 | **Minutes → hours**            | **Multi-AZ**    | **90 days**  | Very low            | **Backup & disaster recovery**, archives where immediate access isn't required          |
| **S3 Glacier Deep Archive**       | **Very rarely accessed (~yearly)**               | **Hours**                      | **Multi-AZ**    | **180 days** | **Lowest**          | **Long-term archive**, compliance, digital preservation                                 |
## S3 Life Cycles
Life cycles are used to set to move objects across storage classes
1. Transition Actions:
   Configure objects to transition to another storage class. Move objects to Standard IA for 60 days then to Glacier for 6 months.
   
2. Expiration Actions:
   
## S3 Analystics
It helps to decide when to transition object (does not work for One-Zone IAs and Glaciers). It takes approximately 24-48 hours to see the stats. Quite useful to improve life cycle rules.

## S3 Event Notification
The available actions are: Create, Remove, Replicate, Restored. To configure these:
1. Requires attached IAM polices of (SNS / SQS / Lambda) to the S3 bucket
2. It can be attached to event bridge (useful when rules, multiple notifications need to be performed) but note that all events will trigger the EventBridge

## S3 Performance

## S3 Encryption
The objects are encrypted in S3 can be performed or customized in below ways:
1. **SSE (S3)**:
   - Server side encryption with AWS S3 managed keys AES26 encryption
   - Enabled by default
   - Managed and owned by AWS. 

2. **SSE (KMS)**: 
   - Same as SSE (S3) but with Key Management Services (KMS)
   - Uses KMS and hence gives user control 
   - Requires *aws:kms* header to be passed
   - The key to encrypt is from kms configured by user
   - KMS Quota Limitations affects uploads and downloads

3. **SSE-C** :
   - Customized Key are used
   - Fully managed by customer outside AWS
   - Keys would not be stored by S3
   - HTTPS must be used and the keys come through this header

4. **Client Side Encrypt**:
   - Client is responsible to encrypt the data and pass the data to S3
   - Client handles both encryption and decryption

## S3 Encryption in Transit (SSL/TLS)
There are two options: HTTP (no encryption), HTTPS (encrypted on flight) which is recommended.

*Note:*
*aws:SecureTransport is useful to configure if user can access s3 data via what transit (in policy giving it is given as when false upload is not allowed; it would make only S3 accessible via https)*

## S3 Access Points
- Access points makes it easy for use groups to access require data.
- These APs have their own VPCs, DNS and rules
- It can be configured such that the APs can be accessed only withing a VPC. While doing so the VPC endpoints require access to the APs and S3.

## S3 Object lambda
For use cases where data needs to be modified just before accessing it, S3 Object Lambda is made for it. The client hits a S3 Object Lambda Access Point which triggers a Lambda which in turn uses S3 Access Point to access the objects/data from S3.

# EC2 Storage Volumes

| Feature                 | EBS (Elastic Block Store)                                                                 | EFS (Elastic File System)                  |
| ----------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------ |
| **Type**                | Network block storage (like a USB stick over network)                                     | Managed NFS (Network File System)          |
| **Instances**           | One instance at a time (CCP level)                                                        | Multiple EC2 instances simultaneously      |
| **Availability Zone**   | Locked to a specific AZ                                                                   | Accessible across all AZs                  |
| **Data Persistence**    | Persists after termination (root volume deleted by default, configurable)                 | Persistent, pay-per-use                    |
| **Detachability**       | Can be detached and re-attached to other instances                                        | Mounted, not detached like a block device  |
| **Pricing**             | Provisioned capacity (pay for what you allocate)                                          | Pay per use (pay for what you store)       |
| **Volume Modification** | Can modify type, size, and performance while instance is running (size can only increase) | Scales automatically, no manual resizing   |
| **Performance**         | Has network latency; multiple elastic types available                                     | Managed performance                        |
| **Use Cases**           | General block storage, OS drives, databases                                               | Data sharing, content sharing, web serving |
| **OS Compatibility**    | Linux & Windows                                                                           | Linux only (not Windows-compatible AMIs)   |

*Note:*
- ***EBS** is the right choice when you need low-latency block storage tied to a single instance - think databases or boot volumes.*
- ***EFS** shines when multiple instances need to read/write the same files concurrently — think shared web assets or ML training data across a fleet.*
- *The key tradeoff is **flexibility vs. simplicity**: EBS gives you more control over performance tiers (gp2, gp3, io1, etc.), while EFS is fully managed and scales transparently.*

# AWS FSx
FSx is a **fully managed third-party file system service**. Instead of building your own NFS like EFS, FSx gives you battle-tested file systems as a managed service.

| Feature             | **FSx for Windows File Server**                 | **FSx for Lustre**                     |
| ------------------- | ----------------------------------------------- | -------------------------------------- |
| **Built on**        | Windows Server (SMB protocol)                   | Lustre (open-source HPC file system)   |
| **Compatible with** | Windows-based EC2                               | Linux EC2                              |
| **Use case**        | Windows workloads, Active Directory integration | **HPC, ML training, big data**         |
| **S3 Integration**  | No                                              | Yes — can read directly from S3        |
| **Performance**     | Standard enterprise performance                 | Extremely high throughput, low latency |
| **MLA Relevance**   | Low                                             | **High**                               |
# Kinesis Data streams
It is used to collect and stream data in real-time
- Retention up to 365 days
- Ability to replay/reprocess data
- Data cannot be deleted until it expires
- Data up to 10MB (real-use case: small but multiple sets of data)
- Partition ID based ordering
- KMS encryption and HTTPS encryption enabled
- Kinesis Producer Library (KPL) to write an optimized producer application

Modes:

| Feature                        | **Provisioned Mode**                    | **On-Demand Mode**               |
| ------------------------------ | --------------------------------------- | -------------------------------- |
| **Capacity Management**        | You manually specify number of shards   | AWS auto-scales capacity         |
| **Throughput (Write)**         | 1 MB/s or 1,000 records/s per shard     | Up to 200 MB/s write by default  |
| **Throughput (Read)**          | 2 MB/s per shard                        | Up to 400 MB/s read by default   |
| **Scaling**                    | Manual — you add/remove shards yourself | Automatic based on traffic       |
| **Pricing**                    | Pay per shard-hour                      | Pay per GB in + GB out           |
| **Cost at low traffic**        | Can be cheaper (predictable baseline)   | More expensive (minimum charges) |
| **Cost at high/spiky traffic** | Can get expensive if over-provisioned   | More cost-efficient              |
| **Best for**                   | Predictable, steady workloads           | Unpredictable or spiky traffic   |
| **Operational overhead**       | Higher — you manage shard splits/merges | Low — fully managed              |

*Note:
Writing is slow in Kinesis with operations like List, Describe, Create have limits of 5-20 calls per second. Write and read have shared level limits. When the producer is large, use KPL to batch things up while when it is small just use PutRecords or  Kinesis Recorder. Implement a retry mechanism because of the limits.*

*Note:
On Consumer side of Kinesis, GetRecords might return empty, just retry.*

# AWS Data Firehose
AWS managed service to pull streaming data from Applications/SDK/Clients or Kinesis/Cloud Watch and can be integrated with an optional Lambda to process the data being pull (1MB at a time for a record) and then can be stored in S3/Redshift/Open Search or 3rd Party Storage like Splunk/Datadog etc.

1. It is pay for what you use and being serverless
2. Near Real-time capability 
3. Highly useful for custom data transformations

## Kinesis Data Analytics
Kinesis Data Analytics lets you **process and analyze streaming data in real-time using SQL or Apache Flink** — without managing any infrastructure. You point it at a Kinesis stream, write your query, and get results out the other side.

| **KDA for SQL**   | **KDA for Apache Flink**                      |                                                    |
| ----------------- | --------------------------------------------- | -------------------------------------------------- |
| **Language**      | Standard SQL                                  | Java, Scala, Python                                |
| **Complexity**    | Simple transformations, filters, aggregations | Complex stateful stream processing                 |
| **Use case**      | Quick analytics on streams                    | Advanced ML feature engineering, complex pipelines |

It fits the Pipeline as shown below:

```
Kinesis Data Streams / Firehose
        ↓
Kinesis Data Analytics (transform, filter, aggregate in real-time)
        ↓
Destination: S3 / Redshift / another Kinesis Stream / Lambda
```

| Capability                 | Detail                                                                  |
| -------------------------- | ----------------------------------------------------------------------- |
| **Real-time aggregations** | Rolling averages, counts, sums over time windows                        |
| **Anomaly detection**      | Built-in `RANDOM_CUT_FOREST` function for detecting outliers in streams |
| **Time windowing**         | Tumbling, Sliding, and Session windows                                  |
| **Reference data**         | Can join a live stream against a static S3 table                        |
| **Output destinations**    | S3, Redshift, Kinesis Streams, Kinesis Firehose, Lambda                 |

RANDOM_CUT_FOREST is a **built-in ML algorithm** inside KDA for SQL that detects anomalies in a stream without you training a model. Exam loves this.
- Detects **unusual spikes, drops, or patterns** in real-time data
- Assigns an **anomaly score** to each record
- You set a threshold — records above it are flagged
- Example scenario: _"detect fraudulent transactions in a payment stream in real-time"_ → **KDA + RANDOM_CUT_FOREST**

## Time Windows 

| Window Type  | How it works                                | Example                                       |
| ------------ | ------------------------------------------- | --------------------------------------------- |
| **Tumbling** | Fixed, non-overlapping chunks               | Count events every 5 mins                     |
| **Sliding**  | Moves forward continuously, windows overlap | Average over last 5 mins, updated every 1 min |
| **Session**  | Groups activity with gaps in between        | User session analytics                        |

| Scenario                                             | Answer                     |
| ---------------------------------------------------- | -------------------------- |
| Real-time anomaly detection on a stream              | KDA + Random Cut Forest    |
| Transform stream data before loading to Redshift     | KDA for SQL                |
| Complex stateful processing / ML inference on stream | KDA for Apache Flink       |
| Just store stream data to S3 without transformation  | Kinesis Firehose (not KDA) |

The key distinction the exam draws is **KDA = real-time processing/analytics**, whereas **Firehose = just delivery**. If the scenario involves any computation on the stream, KDA is in the answer.

# AWS MSK
MSK stands for **Managed Streaming for Apache Kafka**. It's AWS's fully managed Kafka service — you get all the power of Apache Kafka without managing brokers, ZooKeeper, or cluster infrastructure yourself.

|Concept|Detail|
|---|---|
|**Brokers**|MSK manages the Kafka broker nodes for you|
|**Topics**|How data is organized in Kafka (like Kinesis shards but more flexible)|
|**Producers**|Apps that write data into topics|
|**Consumers**|Apps that read from topics|
|**Retention**|Data can be retained for much longer than Kinesis (up to indefinitely)|
|**Protocol**|Native Kafka API — existing Kafka apps work without code changes|

## MSK Serverless

No cluster provisioning at all — fully automatic scaling.

| Feature        | Detail                                                                  |
| -------------- | ----------------------------------------------------------------------- |
| **Capacity**   | Auto-scales storage and compute                                         |
| **Pricing**    | Pay per partition-hour + data in/out                                    |
| **Use case**   | Unpredictable workloads, teams that don't want to manage cluster sizing |
| **Limitation** | Fewer config options vs provisioned MSK                                 |
## MSK Connect

This is a managed version of **Kafka Connect** — a framework for streaming data between Kafka and external systems without writing custom code.

```
External Source (S3, RDS, MongoDB, Salesforce...)
        ↓
    MSK Connect (Connector)
        ↓
    MSK / Kafka Topic
        ↓
    MSK Connect (Connector)
        ↓
External Sink (S3, Redshift, OpenSearch, DynamoDB...)
```

|Feature|Detail|
|---|---|
|**What it does**|Moves data in and out of Kafka using pre-built connectors|
|**Connector types**|Source connectors (pull data in) and Sink connectors (push data out)|
|**Managed**|AWS handles scaling, patching, and availability|
|**Connectors available**|S3, Redshift, OpenSearch, DynamoDB, Debezium (CDC), and more|
|**MLA relevance**|Ingesting data from databases/SaaS into a ML feature pipeline|

Key exam scenario: _"Stream database changes into S3 for ML training without custom ETL code"_ → **MSK Connect with a Debezium CDC source connector**

## Kinesis vs MSK (Kafka) — Comparison Table

| Feature                  | **Kinesis Data Streams**                      | **Amazon MSK (Kafka)**                                     |
| ------------------------ | --------------------------------------------- | ---------------------------------------------------------- |
| **Type**                 | AWS-native proprietary                        | Open-source Apache Kafka, managed by AWS                   |
| **Protocol**             | Kinesis API only                              | Native Kafka API                                           |
| **Portability**          | AWS-only                                      | Kafka apps portable across clouds/on-prem                  |
| **Data unit**            | Record (up to 1 MB)                           | Message (configurable, up to 10 MB default)                |
| **Ordering**             | Per shard                                     | Per partition                                              |
| **Scaling unit**         | Shards (Provisioned) or automatic (On-Demand) | Partitions — more flexible                                 |
| **Retention**            | 1 day default, up to 365 days                 | Configurable, unlimited with tiered storage                |
| **Replication**          | Managed by AWS                                | Configurable replication factor                            |
| **Consumer groups**      | Limited                                       | Full Kafka consumer group support                          |
| **Serverless option**    | On-Demand mode                                | MSK Serverless                                             |
| **Security**             | IAM native                                    | IAM + SASL/SCRAM + TLS                                     |
| **Ease of use**          | Easier — AWS native, less config              | More complex — Kafka expertise helps                       |
| **Operational overhead** | Very low                                      | Low (managed) but higher than Kinesis                      |
| **Pricing model**        | Per shard-hour or per GB                      | Per broker-hour + storage                                  |
| **Ecosystem**            | AWS services only                             | Huge Kafka ecosystem (Kafka Connect, Kafka Streams, Flink) |
| **Best for**             | Simple AWS-native streaming pipelines         | Complex pipelines, existing Kafka workloads, multi-cloud   |



 

