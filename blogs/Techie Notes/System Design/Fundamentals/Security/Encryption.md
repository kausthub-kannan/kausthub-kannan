Encryption turns readable data (plaintext) into unreadable data (ciphertext) using an algorithm and a key, so that only someone with the right key can turn it back. Data can be exposed in three states, and each needs its own kind of protection.

|State|Where the data is|Main threat|Protection|
|---|---|---|---|
|In transit|Moving across a network between a client and a server, or between two services|Eavesdropping and tampering on the path, such as public Wi-Fi, a compromised router or a man-in-the-middle|TLS, mTLS, VPN, SSH|
|At rest|Stored on disk, in a database, in object storage or in a backup|Stolen disks, leaked backups or snapshots, a lost laptop, an insider with physical access|Disk, database and object-storage encryption, application-level encryption|
|In use|Loaded in memory and being processed|Memory dumps, a compromised host|Access controls, and advanced options such as confidential computing|

The standard choice is AES with a 256-bit key in an authenticated mode such as AES-GCM, which also detects any tampering. Asymmetric encryption uses a public and private key pair, and is slower, so it is used to exchange keys and prove identity (RSA, elliptic curve algorithms such as ECDH and ECDSA), not for bulk data. Modern CPUs have built-in AES instructions, so the performance cost of symmetric encryption is small.

|Concept|Reversible?|Needs a key?|Purpose|Example|
|---|---|---|---|---|
|Encryption|Yes, with the key|Yes|Keep data confidential|Encrypting a file or a database column|
|Hashing|No, one-way|No (a salt is added for passwords)|Verify integrity, store passwords|Storing passwords with bcrypt or Argon2|
|Encoding|Yes, by anyone|No|Change the format, not protect|Base64, URL encoding|

Passwords should be hashed, not encrypted, because the system never needs to recover the original. Base64 is not security at all.

## Encryption in Transit
Data in transit passes through many machines that are not under your control: Wi-Fi access points, ISPs and internet routers. Without encryption, anyone on that path can read the data, record it, or alter it. Encryption in transit provides three things: confidentiality (nobody can read it), integrity (nobody can change it without detection) and authentication (you are talking to the real server, and not an impostor).

### TLS and HTTPs
TLS (Transport Layer Security) is the standard for encrypting traffic between two parties, and HTTPS is simply HTTP carried over TLS. The mechanics, covered in the SSL/TLS notes, are that the server proves its identity with a certificate signed by a trusted certificate authority, the two sides agree on a session key through a handshake (using ephemeral Diffie-Hellman for forward secrecy), and then all data is encrypted with the fast symmetric session key. TLS 1.3 is the current version and needs fewer round trips, and TLS 1.2 is the minimum that should still be allowed, with the older SSL, TLS 1.0 and TLS 1.1 disabled.

HTTPS for browsers is only the most visible case. Every network hop that carries sensitive data should be protected.

|Path|Technology|
|---|---|
|Browser or mobile app to server|HTTPS (TLS)|
|Client to database|TLS on the database connection|
|Service to service inside the data center|TLS, or mutual TLS (mTLS), often provided by a service mesh|
|Between offices or to a cloud network|VPN with IPsec or WireGuard|
|Remote administration|SSH|
|File transfer|SFTP or FTPS, and not plain FTP|
|Email between servers|STARTTLS, and the user's own encryption for real privacy|
|DNS queries|DNS over HTTPS (DoH) or DNS over TLS (DoT), as in the DNS notes|
|Wireless networks|WPA2 or WPA3|

### Mutual TLS (mTLS)
In ordinary TLS, only the server presents a certificate, and the client proves itself separately with a password or token. In mutual TLS, both sides present certificates and verify each other. This is widely used between microservices, so that a service can be certain which other service is calling, and it is a core part of zero trust networking, where the network is never trusted just for being internal. Service meshes such as Istio and Linkerd issue and rotate these certificates automatically for every service.

### TLS Termination and the Internal Network
As described in the proxy and load balancer notes, TLS is often terminated at a load balancer, reverse proxy or CDN edge, which decrypts the traffic and forwards it onward. If the hop from there to the backend uses plain HTTP, the data is exposed inside the internal network, where an attacker who has gained a foothold could read it. Security-sensitive systems therefore re-encrypt the traffic to the backend (TLS to the origin), or use mTLS inside the cluster, and do not assume the private network is safe.

### End-to-End Encryption
Ordinary TLS protects data only between two points, and the server at the end can read it. End-to-end encryption (E2EE) means that only the two communicating users can read the message, and not even the service in the middle, because the encryption keys exist only on the users' devices. Messaging apps such as Signal and WhatsApp work this way. The trade-off is that the service cannot search, moderate or recover the content for the users.

## Encryption at Rest
Encryption at rest protects stored data, so that if someone obtains the storage medium itself, they get only unreadable ciphertext. The realistic threats it handles are a stolen or lost laptop or server, a discarded disk, a leaked database backup or cloud snapshot, a misconfigured storage bucket, and someone with direct access to the underlying files. It is also a requirement in most compliance standards, such as PCI DSS for card data, HIPAA for health data and data protection laws such as GDPR.

Encryption at rest can be applied at several layers. The higher the layer, the more targeted the protection, and the more work it takes to implement.

|Layer|What is encrypted|Examples|Protects against|Does not protect against|
|---|---|---|---|---|
|Full-disk or volume encryption|The entire disk or volume, transparently|BitLocker, FileVault, LUKS, encrypted cloud volumes (AWS EBS)|Stolen or lost physical disks|Anyone who can use the running, unlocked system|
|File or object storage encryption|Each file or object|S3 server-side encryption (SSE-S3, SSE-KMS), Azure Storage and Google Cloud Storage encryption|Direct access to storage media and leaked raw storage|A user or service with permission to read the object|
|Database encryption (TDE)|The database's data files, logs and backups|Transparent Data Encryption in SQL Server, Oracle, MySQL and cloud databases such as RDS|Stolen database files and backups|Queries by anyone with database access, including SQL injection|
|Column or field-level encryption|Specific sensitive columns|pgcrypto, application code|Database administrators, leaked dumps and over-broad database access|Compromise of the application that holds the key|
|Application-level encryption|Data encrypted by the application before it is ever sent to storage|Encryption libraries and cloud SDKs|Almost every storage-side exposure|Compromise of the application, and complexity|

Full-disk and database-level encryption are transparent: the system decrypts the data automatically as it is read, so applications need no changes. That is exactly why they offer limited protection, as covered below. Column-level and application-level encryption give the strongest protection for the most sensitive fields, such as national ID numbers or card numbers, but data encrypted this way cannot be searched or indexed directly, unless special techniques such as deterministic encryption or tokenization are used.

### Key Management
Encryption is only as strong as the protection of its keys. A strong cipher with a badly handled key gives no security, and a lost key means the data is gone forever. This is why most of the practical work in encryption at rest is about managing keys.

|Option|What it is|Notes|
|---|---|---|
|KMS (key management service)|A managed service that creates, stores and uses keys, and logs each use|AWS KMS, Google Cloud KMS, Azure Key Vault, HashiCorp Vault. The usual choice|
|HSM (hardware security module)|A tamper-resistant device that holds keys and never lets them out|Used for the highest assurance and compliance (FIPS 140), and underlies cloud KMS offerings|
|Secrets manager|A store for application secrets and credentials|AWS Secrets Manager, Vault|
|Keys in code, config files or the same disk as the data|Hardcoded or stored next to the encrypted data|Never do this, since it makes the encryption pointless|

### Envelope Encryption
Calling a KMS to encrypt every large file would be slow, and the master key must never leave the KMS. The standard solution is envelope encryption, which uses two levels of keys. A data encryption key (DEK) encrypts the actual data, and a key encryption key (KEK), the master key that stays inside the KMS, encrypts (wraps) the data key.

|Step|What happens|
|---|---|
|1|The application asks the KMS to generate a data key. The KMS returns it in two forms: plaintext, and encrypted under the master key|
|2|The application encrypts the data locally with the plaintext data key (AES-GCM)|
|3|The application discards the plaintext data key from memory, and stores the encrypted data key beside the encrypted data|
|4|To read the data, the application sends the encrypted data key to the KMS, which decrypts it only if the caller is authorized, and returns the data key|
|5|The application decrypts the data, then discards the data key again|

This design has several advantages. The master key never leaves the KMS or HSM. Only a tiny key is sent to the KMS, and the bulk data is encrypted locally at full speed. Every object or record can have its own data key, so the exposure of one key affects only that data. Rotating the master key only requires re-wrapping the small data keys, and not re-encrypting all the data. And every use of the master key is logged and controlled by access policies, which is what cloud services such as S3 SSE-KMS, EBS and RDS do behind the scenes.

### Key Practices
- Keep keys separate from the data they protect, in different systems with different access rights, so that a single breach does not expose both.
- Rotate keys regularly and when a compromise is suspected, and design for it, for example by storing a key ID with every ciphertext so that old data can still be decrypted with the old key while new data uses the new one.
- Apply least privilege to key access, so that only the specific services that need to decrypt can do so, and audit every use.
- Back up keys securely, because losing a key makes all the data encrypted with it permanently unrecoverable.
- Never put keys in source code, container images, logs or version control.
- Use well-known algorithms and libraries (AES-GCM, ChaCha20-Poly1305, modern TLS), and never design your own cryptography.

With transparent encryption (disk, database or storage level), the system decrypts data automatically for any authorized request. So if an attacker steals the application's credentials, exploits SQL injection or compromises a server that has access to the keys, they receive plain data, since the system itself is serving it. Encryption at rest defends against someone obtaining the storage media or backups, not against someone using the live system through legitimate access paths. The remaining defenses are strong authentication and authorization, least privilege, network security, monitoring, and field-level or application-level encryption for the most sensitive data, where even database administrators and compromised database accounts only see ciphertext.