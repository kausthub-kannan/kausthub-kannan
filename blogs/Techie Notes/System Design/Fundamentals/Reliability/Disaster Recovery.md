**Disaster recovery (DR)** is the set of policies, tools and procedures for restoring systems and data after a major failure: hardware loss, data corruption, human error, ransomware, a regional outage or a whole-site disaster.

Resilience patterns keep a system running through _small_ failures. DR is what you rely on when those defences are not enough and something large is lost. DR is closely related to, but distinct from, **high availability (HA)** and **business continuity planning (BCP)**.

|Term|Meaning|
|---|---|
|**Disaster**|An event causing prolonged or severe loss of service or data|
|**RPO** (Recovery Point Objective)|The maximum **amount of data loss** you can tolerate, measured in time|
|**RTO** (Recovery Time Objective)|The maximum **time to restore** service after a disaster|
|**RTA / RPA**|The _actual_ recovery time and point achieved in a test or real event|
|**MTD / MAO** (Maximum Tolerable Downtime / Maximum Acceptable Outage)|The longest outage the business can survive before serious damage|
|**WRT** (Work Recovery Time)|Time after systems are back to verify data, reconcile and resume operations|
|**Backup**|A separate copy of data kept so it can be restored later|
|**Replication**|Continuously copying changes to another system or location|
|**Failover**|Switching traffic and operations to a standby system|
|**Failback**|Returning to the original system once it is repaired|
|**Business Continuity Plan (BCP)**|The broader plan for keeping the _business_ running, of which IT DR is one part|

```
         disaster strikes
              │
  ◄───RPO────►│◄──────────────RTO──────────────►
  data lost    │   outage: service unavailable    │
              │                                   ▼
last good     ▼                              service restored
recovery  ─────────────────────────────────────────────► time
point
```

## RTO and RPO
RPO is measured **backwards from the disaster** to the last recoverable copy of the data.
- **RPO of 24 hours:** a nightly backup is enough, and you may lose up to a day of changes.
- **RPO of 5 minutes:** you need frequent log shipping or near-real-time replication.
- **RPO of 0:** no data loss at all, which requires **synchronous replication**, with a cost in latency and availability.

RTO is measured **forward from the disaster** to the point where service is restored.
- **RTO of 24 hours:** restoring from backups into new infrastructure may be acceptable.
- **RTO of 1 hour:** you need pre-provisioned infrastructure and automated recovery.
- **RTO of minutes or seconds:** you need hot standby and automated failover (active-active or active-passive).

### RTO vs RPO

|RPO / RTO|Typical approach|Relative cost|
|---|---|---|
|Days / days|Offsite backups, rebuild on demand|Lowest|
|Hours / hours|Regular backups plus infrastructure as code for quick rebuild|Low|
|Minutes / under 1 hour|Continuous log shipping or async replication, pilot light or warm standby|Medium|
|Seconds / minutes|Async replication to a hot standby with automated failover|High|
|Zero / near zero|Synchronous replication or active-active across sites|Highest|

|Tier|Examples|RPO|RTO|
|---|---|---|---|
|**Tier 0 / Critical**|Payments, core transactions, authentication|Near zero|Minutes|
|**Tier 1 / High**|Customer-facing apps, order management|Minutes|1 hour|
|**Tier 2 / Medium**|Internal tools, reporting|Hours|4 to 24 hours|
|**Tier 3 / Low**|Dev/test, archives|24 hours or more|Days|


## Backups
A backup is a **point-in-time copy of data, stored separately**, that can be restored after loss or corruption. Backups are the last line of defence and the main protection against **logical corruption** (bad deploys, accidental deletes, ransomware), which replication faithfully copies.

### Backup Types
|Type|What it captures|Pros|Cons|
|---|---|---|---|
|**Full**|Everything|Simplest, fastest restore|Slow, large, expensive to run often|
|**Incremental**|Changes since the **last backup** (of any type)|Small and fast|Restore needs the full backup plus every increment in the chain|
|**Differential**|Changes since the **last full backup**|Faster restore than incremental (full plus one differential)|Grows larger until the next full|
|**Incremental forever / synthetic full**|One full, then incrementals, merged into synthetic fulls on the backup server|Efficient on bandwidth and storage|Depends on backup software, more complex|
|**Snapshot**|Storage-level point-in-time view (copy-on-write)|Very fast to create|Often on the same storage system, so **not a true independent backup** unless copied elsewhere|
|**Continuous data protection (CDP) / log-based**|Every change, so you can restore to any moment|Near-zero RPO, point-in-time recovery|More complex, higher cost|

### Backup levels
|Level|Description|Notes|
|---|---|---|
|**File-level**|Individual files and folders|Granular restore|
|**Block / image-level**|Entire disk or volume|Fast full-system recovery, bare-metal restore|
|**Application-consistent**|Coordinated with the application (flush buffers, quiesce, use VSS or database hooks)|Needed for reliable database and application restores|
|**Crash-consistent**|Like pulling the power plug (state on disk at that instant)|Usually recoverable, but databases may need to replay logs, and some may not recover cleanly|

### 3-2-1 Rule
- **3** copies of your data (production plus two backups)
- **2** different storage media or types
- **1** copy offsite (different location or region)

**3-2-1-1-0:** add **1** copy that is **offline or immutable** (air-gapped, object lock) and **0** errors after backup verification (restore tests). This is the modern recommendation, mainly because of ransomware.

### Retention
Keep multiple generations so you can go back before a problem began, not just the latest copy. A common **GFS (grandfather-father-son)** scheme:

|Generation|Frequency|Typical retention|
|---|---|---|
|**Son** (daily)|Daily|7 to 35 days|
|**Father** (weekly)|Weekly|4 to 12 weeks|
|**Grandfather** (monthly)|Monthly|12 months or more|
|**Yearly**|Yearly|Years, per compliance|

Retention is driven by RPO needs, how long it takes to **notice** corruption (silent corruption can go unnoticed for weeks), and legal or regulatory requirements. Balance against the **right to erasure** (for example GDPR): deleted personal data may persist in backups, so document how and when it ages out.

### Storing backups
|Location|Notes|
|---|---|
|**Same host or disk**|Not a backup. It dies with the system.|
|**Same datacentre, different storage**|Protects against disk and host failure only|
|**Different availability zone**|Protects against zone failure|
|**Different region**|Protects against regional disaster. Check data residency rules.|
|**Different account / subscription / tenant**|Protects against credential compromise and accidental deletion. **Strongly recommended.**|
|**Offline / air-gapped (tape, offline vault)**|Strongest ransomware protection|

Keep backups in a **separate security domain**: separate credentials, separate account, and permissions that production systems cannot use to delete them.

### Backup lifecycle
```
Schedule -> Capture -> Verify integrity -> Encrypt -> Copy offsite/cross-account
     -> Retain per policy -> Monitor & alert -> Restore test -> Expire/delete
```

- **A backup is only proven by a successful restore.** Test restores regularly, including a full recovery into a clean environment.
- **Automate** scheduling, verification and alerting. Alert on **missed or failed backups**, backup size anomalies (suddenly tiny or huge) and restore-test failures.
- **Encrypt** backups in transit and at rest, and protect the keys separately. Losing the keys means losing the backups.
- **Back up configuration and infrastructure definitions too:** infrastructure as code, secrets (in a secure manager), DNS records, certificates, CI/CD pipelines, IAM and network configuration.
- **Back up SaaS data.** Providers protect their platform, but typically not you from your own mistakes (Microsoft 365, Google Workspace, Salesforce, GitHub). This is the shared responsibility model.
- **Document and rehearse the restore procedure.** The time to figure it out is not during the incident.
- **Measure restore time**, not just backup time. Restoring terabytes can take many hours depending on bandwidth and rehydration.
- **Mind the restore path:** cloud archive tiers (such as Glacier Deep Archive) can take hours to retrieve and cost more to read.

## Replication
Replication **continuously copies data** from a primary to one or more secondaries, giving you a nearly up-to-date copy ready for failover.

### Synchronous vs Asynchronous replication
|                         | Synchronous                                                                          | Asynchronous                                                               |
| ----------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| **How**                 | A write is acknowledged only after the replica has also committed it                 | A write is acknowledged immediately, and the replica catches up afterwards |
| **RPO**                 | **Zero** (no committed data lost)                                                    | Non-zero, equal to the replication lag at failure time                     |
| **Latency impact**      | Adds replica round-trip time to every write                                          | Minimal                                                                    |
| **Distance**            | Practical only for short distances (same metro or nearby zones)                      | Works across continents                                                    |
| **Availability impact** | A replica outage can block or slow writes (unless a quorum or fallback mode is used) | Primary is independent of replica health                                   |
| **Typical use**         | Zero-data-loss requirements, within a metro or region                                | Cross-region DR, read scaling                                              |

**Semi-synchronous** is a middle ground: wait for at least one replica to receive (not necessarily apply) the write. A **quorum** approach (Raft, Paxos, Aurora's 4-of-6) acknowledges once a majority confirm.

### Topologies
|Topology|Description|Notes|
|---|---|---|
|**Primary / replica (leader / follower)**|One writer, several read replicas|Most common. Failover means promoting a replica.|
|**Multi-primary (multi-master)**|Several nodes accept writes|Needs conflict resolution. Complex.|
|**Chain / cascading**|Replica feeds another replica|Reduces load on the primary|
|**Active-passive**|Standby is idle, ready to take over|Simple, but the standby capacity is "wasted"|
|**Active-active**|All sites serve traffic|Best availability, hardest data consistency|
|**Quorum / consensus group**|Majority must agree on each write|Strong consistency, tolerates minority failure|

### Replication methods
|Level|How|Examples|
|---|---|---|
|**Storage / block-level**|The storage array or volume layer copies blocks|SAN replication, DRBD, EBS cross-region snapshots, Azure Site Recovery|
|**Hypervisor / VM-level**|Replicates whole virtual machines|VMware SRM, Hyper-V Replica|
|**Database-level (log-based)**|Ships the write-ahead log or binlog|PostgreSQL streaming replication, MySQL binlog replication, SQL Server Always On, Oracle Data Guard|
|**Logical replication**|Replicates row changes (or a subset of tables)|PostgreSQL logical replication, CDC with Debezium|
|**Object / file replication**|Copies objects between buckets or file systems|S3 Cross-Region Replication, rsync, GCS dual-region|
|**Application-level**|The app writes to multiple stores (dual writes)|Fragile, since failures can leave stores inconsistent. Prefer CDC or an event log.|
|**Managed global databases**|The platform handles multi-region replication|Aurora Global Database, DynamoDB Global Tables, Cosmos DB, Spanner, Cloud SQL replicas|

### Replication lag
In asynchronous replication, **lag** is the delay before a replica reflects the primary. It determines your real RPO.

- **Monitor lag continuously** (seconds behind primary, bytes or WAL position behind) and **alert** when it exceeds your RPO.
- Lag increases under write spikes, long-running transactions, large batch jobs, network congestion and under-provisioned replicas.
- Reading from replicas means reads can be **stale**, so design for read-your-writes where needed (route a user's reads to the primary shortly after a write).

### Failure considerations
|Concern|What to plan|
|---|---|
|**Detection**|Reliable failure detection, avoiding false positives from brief network blips|
|**Split-brain**|Two nodes both think they are primary and accept writes, which causes divergent data. Prevent with **quorum, fencing (STONITH), leases** and a third-site witness.|
|**Promotion**|Choose the most up-to-date replica. Verify it has applied all available logs.|
|**Data loss on async failover**|Writes not yet replicated are lost (up to the lag). Decide in advance whether to accept it. Record or reconcile where possible.|
|**Redirecting clients**|DNS (watch TTLs and caching), load balancers, virtual IPs, service discovery, connection strings|
|**Reconfiguring the old primary**|Once recovered, it must rejoin as a replica (it may need rewinding or re-seeding), not as a second primary|
|**Warm-up**|Cold caches and connection pools can make the first minutes slow|
|**Automatic vs manual**|Automatic is faster but risks flapping and split-brain. Manual is slower but deliberate. Many teams automate within a region and require a human decision for cross-region.|

## Backup vs Replication
|                            | Replication                          | Backups                                                                    |
| -------------------------- | ------------------------------------ | -------------------------------------------------------------------------- |
| **Protects against**       | Hardware, host, zone or site failure | Data corruption, accidental or malicious deletion, ransomware, bad deploys |
| **Corruption or deletion** | **Replicated instantly** to the copy | **Not affected** (the point-in-time copy remains)                          |
| **RPO**                    | Seconds to zero                      | As frequent as backups (minutes to hours) unless using log-based PITR      |
| **RTO**                    | Seconds to minutes (failover)        | Minutes to many hours (restore)                                            |
| **Point-in-time recovery** | No (only the current state)          | Yes, to any retained point                                                 |
| **Cost**                   | Ongoing running infrastructure       | Mostly storage, cheaper                                                    |
| **Typical role**           | High availability and fast DR        | Last-resort recovery and history                                           |

## Point-In-Time Recovery (PITR)
Combine a base backup with continuous archiving of transaction logs (PostgreSQL WAL archiving, MySQL binlogs, SQL Server log backups, Aurora and RDS PITR). You can then restore to **any moment**, for example "five seconds before the bad migration ran". PITR gives a very low RPO with the corruption protection that replication lacks.

## DR Strategies
|Strategy|Description|RPO|RTO|Cost|
|---|---|---|---|---|
|**Backup and restore**|Back up data to another region or location. After a disaster, provision infrastructure and restore.|Hours|Hours to days|$|
|**Pilot light**|Core data is continuously replicated, with a minimal always-on footprint (for example, the database replica). Application servers are off or defined as code, and are scaled up on failover.|Minutes|Tens of minutes to hours|$$|
|**Warm standby**|A scaled-down but fully functional copy runs continuously and can serve traffic. On disaster, scale it up and route traffic.|Seconds to minutes|Minutes|$$$|
|**Multi-site active-active (hot)**|Full capacity in multiple regions, all serving live traffic. Failure of one region is absorbed by the others.|Near zero|Near zero (seconds to minutes)|$$$$|

```
Backup & restore   ●─────────────○ (everything rebuilt after the event)
Pilot light        ●●────────────○ (data live; compute started on demand)
Warm standby       ●●●●──────────○ (small live copy; scale up)
Active-active      ●●●●●●●●●●●●●●● (full capacity in 2+ regions at all times)
                   cheaper/slower ───────────► costlier/faster
```

1. Start from **RPO and RTO per tier**.
2. Pick the **cheapest strategy that meets the objectives**.
3. Use **different strategies for different tiers** (active-active for payments, backup and restore for internal reports).
4. Consider **operational complexity**. Active-active needs data-consistency design (conflict resolution, global transactions) and carries more day-to-day operating risk.

## Faster DR
- **Infrastructure as code** (Terraform, CloudFormation, Pulumi) so environments can be rebuilt reliably and quickly.
- **Immutable, versioned images and artefacts** stored in the DR region (container registries, AMIs, packages).
- **Configuration and secrets** replicated securely to the DR site.
- **Automation and runbooks** for failover, and for failback.
- **DNS and traffic management** with low TTLs and health-checked failover (Route 53, Azure Traffic Manager, Cloudflare, global load balancers).
- **Capacity reservations** in the DR region. A region-wide event means many customers fail over at once, so spare capacity is not guaranteed.
- **Independent control plane:** don't let DR depend on tooling or identity systems that live only in the failed region.

## DR Failure Scenario
|Scenario|Replication|Backups|Multi-AZ / region|Notes|
|---|---|---|---|---|
|Disk or host failure|✅|✅|✅|Local redundancy (RAID, multi-AZ) handles most of this|
|Availability zone outage|✅ (cross-AZ)|✅|✅|Multi-AZ designs|
|Regional outage|✅ (cross-region)|✅ (cross-region copy)|✅|Cross-region DR|
|Accidental deletion / bad migration|❌ replicates the mistake|✅ (PITR)|❌|Needs backups, versioning, delayed replicas|
|Application bug corrupting data|❌|✅|❌|Backups with sufficient retention|
|Ransomware / malicious insider|❌ may encrypt or delete replicas|✅ if **immutable and isolated**|❌|Immutable, separate-account backups|
|Compromised cloud account|❌|✅ only if stored in a **separate account**|❌|Account isolation|
|Cloud provider or vendor failure|❌|✅ if stored elsewhere|⚠️ same provider|Multi-cloud or offsite backups for the most critical data|
|Software or config rollout failure|⚠️|✅|⚠️|Safe deployment practices, rollbacks, canaries|
|Expired certificate / lost key / DNS mistake|❌|⚠️|❌|Shared dependencies. Cover them in the DR plan.|
|Human error (wrong environment)|❌|✅|❌|Guardrails, least privilege, deletion protection|

## Backup and Restore for common systems
|System|Typical approach|
|---|---|
|**Relational databases (PostgreSQL, MySQL, SQL Server)**|Base backups plus continuous log archiving for PITR (pgBackRest, Barman, WAL-G, XtraBackup, managed automated backups). Streaming replicas for HA. Test restores.|
|**Managed DBs (RDS, Cloud SQL, Azure SQL)**|Automated backups and PITR, snapshots copied cross-region or cross-account, cross-region read replicas for DR. Enable deletion protection.|
|**NoSQL (DynamoDB, Cassandra, MongoDB)**|On-demand and continuous backups (PITR), global tables or multi-DC replication. Cassandra snapshots and repair.|
|**Object storage (S3, GCS, Blob)**|Versioning, MFA delete or Object Lock, cross-region or cross-account replication, lifecycle rules.|
|**File systems / block volumes**|Scheduled snapshots copied to another region or account, plus file-level backup for granular restore.|
|**Kubernetes**|Back up etcd (or rely on managed control plane), cluster config as code (GitOps), persistent volumes via CSI snapshots (Velero, Kasten). Treat workloads as rebuildable from Git.|
|**Virtual machines**|Image-level backups, replication (Site Recovery, SRM), golden images plus IaC.|
|**Message queues / streams (Kafka)**|Mirror topics (MirrorMaker, Cluster Linking), back up topic config and consumer offsets, long retention or tiered storage.|
|**Search indexes (Elasticsearch, OpenSearch)**|Snapshots to object storage. Often rebuildable from the source of truth, so decide whether to back up or reindex.|
|**Caches (Redis)**|Usually rebuildable, so treat as disposable unless used as a primary store. If it is, use persistence (AOF/RDB) and replication.|
|**SaaS tools**|Third-party backup tools or export APIs|
|**Secrets and keys**|Replicate secrets managers and KMS keys per vendor guidance. Keep an offline escrow of root keys and recovery codes.|
|**Source code and CI/CD**|Mirror repositories, back up pipeline definitions and artefact stores|


## Ransomware and Immutable Backups
- **Immutability (WORM):** Object Lock (S3 compliance or governance mode), immutable blob storage, immutable backup repositories, so backups can't be altered or deleted for the retention period, even by admins.
- **Air gap / logical air gap:** offline tapes or a vault account with no standing network access or credentials from production.
- **Separate credentials and account:** backup administration is not reachable with production credentials. Use MFA, and require multi-person approval (**multi-party authorisation**) for deleting backups or shortening retention.
- **Least privilege:** the production system can _write_ backups but cannot _delete_ or _modify_ them.
- **Anomaly detection:** alert on sudden changes in backup size, change rate or deletion attempts. Mass encryption looks like a spike in changed data.
- **Clean-room recovery:** restore into an isolated environment, scan for malware and persistence mechanisms, and only then reconnect. Restoring straight into a still-compromised environment re-infects it.
- **Retention long enough** to reach back before the infection (attackers often dwell for weeks).
- **Test the ransomware recovery scenario specifically,** including rebuilding identity (Active Directory) and core infrastructure, which many plans forget.

## DR Planning
1. **Scope and objectives:** systems covered, tiers, RPO and RTO per tier.
2. **Risk and business impact analysis (BIA):** threats, likelihood, cost of downtime and data loss.
3. **Architecture and strategy per tier:** backup, replication, standby type.
4. **Dependencies map:** DNS, identity, networking, secrets, certificates, third-party APIs, and the order to recover them.
5. **Roles and responsibilities:** incident commander, DR lead, communications lead, service owners, with **backups for each** (people are unavailable in disasters).
6. **Declaration criteria:** who can declare a disaster, and at what thresholds (for example, "primary region unavailable for more than 15 minutes").
7. **Communication plan:** internal channels (with an out-of-band option in case chat or email is down), customer and status page updates, regulator notification where required.
8. **Runbooks:** step-by-step failover, restore and failback procedures.
9. **Contact lists and access:** vendors, cloud support, break-glass credentials stored somewhere that survives the disaster.
10. **Testing schedule and success criteria.**
11. **Maintenance process:** review after every significant architecture change and at least annually.

## DR Runbook
- **Concrete and executable:** exact commands, console steps, links, and expected outputs, written so someone unfamiliar can follow it under stress.
- **Ordered by dependency:** identity and network first, then data stores, then applications, then traffic.
- **Includes verification steps** after each stage (data integrity checks, smoke tests, consistency checks).
- **Includes decision points** (for example "if replication lag exceeds RPO, escalate to the business before promoting").
- **Stored where you can reach it during an outage:** not only in the system that is down.
- **Includes failback**, which is often harder than failover.

## Testing DR
|Test type|Description|Disruption|
|---|---|---|
|**Plan review / checklist**|Walk through the documents, verify contacts and access|None|
|**Tabletop exercise**|A team talks through a scenario step by step, finding gaps in decisions and communication|None|
|**Backup restore test**|Restore backups to an isolated environment and verify data integrity|Low|
|**Component failover test**|Fail over a single database or service|Low to medium|
|**Simulation / walkthrough in staging**|Full DR run in a non-production copy|Low|
|**Full failover (game day)**|Actually switch production to the DR site, then fail back|Medium to high, but the only real proof|
|**Chaos engineering**|Inject failures (kill instances, drop a zone) to validate automation|Controlled|
|**Unannounced drill**|Surprise scenario to test real readiness|Higher|

## Compilance
- **Encryption** of backups and replication traffic (TLS, at-rest encryption), with **key management** that survives the disaster (keys replicated or escrowed, otherwise data is unrecoverable).
- **Access control:** least privilege, MFA, audit logging for backup and DR tooling, break-glass procedures that are tested.
- **Data residency and sovereignty:** cross-region replication and offsite backups must respect legal limits on where data may live (GDPR, India's DPDP Act, sector rules).
- **Retention and deletion obligations:** balance legal retention minimums against deletion rights, and document how deleted data ages out of backups.
- **Regulatory frameworks** often mandate DR and testing: ISO 27001 and ISO 22301, SOC 2, PCI-DSS, HIPAA, RBI and SEBI guidelines for Indian financial entities, DORA for EU financial entities. Keep evidence (test reports, results) for audits.
- **Secure the DR environment** to the same standard as production. A weaker DR site is an attractive attack path.