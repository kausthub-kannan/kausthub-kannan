Plain HTTP sends everything as readable text. Between a client and a server, the data passes through many routers, Wi-Fi networks and ISPs, and anyone positioned along that path, such as an attacker on public Wi-Fi, can read it, record it or even change it. Passwords, card numbers and personal messages would all be exposed. Encryption solves this by scrambling the data so that anyone who intercepts it sees only meaningless bytes. HTTPS is simply HTTP carried over an encrypted connection, and that encryption is provided by SSL/TLS.

SSL (Secure Sockets Layer) was the original protocol, and TLS (Transport Layer Security) is its successor. All versions of SSL are now deprecated and insecure, and modern systems use TLS 1.2 or TLS 1.3. The name "SSL certificate" has stuck out of habit, so people still say SSL when they mean TLS. In practice the two terms are used interchangeably, but it is worth knowing that the protocol actually running today is TLS.

## Encryption Techniques

### Symmetric
In symmetric encryption, the same single key is used to encrypt the data on one side and decrypt it on the other. The client encrypts with the key, and the server decrypts with the same key. Algorithms such as AES are very strong and very fast, which makes them ideal for encrypting large amounts of data like pages, images and video.

It is a common misunderstanding that symmetric encryption is weak because it uses only one key. The encryption itself is strong. The real problem is key distribution. Both sides need to have the same key, but if the client has to send that key to the server over the internet, an eavesdropper can capture it and then decrypt everything. Symmetric encryption is therefore safe only after both sides have somehow agreed on a secret key without anyone else learning it.

### Asymmetric
![Asymmetric Encryption](../../../../assets/excalidraw/System Design/Fundamentals/Security/Asymmetric Encryption.excalidraw)
Asymmetric encryption solves the key sharing problem by using a pair of mathematically linked keys: a public key and a private key. The public key can be shared with anyone, and the private key is never shared. Data encrypted with the public key can only be decrypted with the matching private key, so anyone can send a secret message to the key owner, but only the owner can read it.

So when a client wants to send data to a server, it encrypts the data with the server's public key, and only the server can decrypt it with its own private key. The same works in the other direction using the client's public key and the client's private key. Neither private key ever travels across the network. The drawback is that asymmetric encryption is much slower and more computationally expensive than symmetric encryption, so it is not practical for encrypting all the data of a connection.

### Hybrid - TLS technique
Because each type has a weakness, TLS combines them. Asymmetric cryptography is used only at the start of the connection to securely agree on a shared secret, and that secret becomes a symmetric session key. All the actual data is then encrypted quickly with the symmetric session key. The session key is temporary and is thrown away when the connection ends. Modern TLS generates this key using an ephemeral Diffie-Hellman exchange, which has an important property called forward secrecy: even if the server's private key is stolen in the future, previously recorded traffic still cannot be decrypted.

## Issue of Eavesdropping 
Asymmetric encryption still has one serious weakness. When the client asks for the server's public key, the key travels across the network, and an attacker sitting in the middle can intercept it and replace it with their own public key. The client, unaware of this, encrypts its data with the attacker's key. The attacker decrypts it with their own private key, reads it, then re-encrypts it with the server's real public key and passes it on. Neither side notices anything wrong, but the attacker sees everything. This is called a man-in-the-middle attack.

The core issue is trust: the client has no way of knowing whether the public key it received really belongs to the server it wants to talk to. SSL/TLS certificates exist to solve exactly this.

### Solution to Public Key modification
A certificate is a digital document that links a public key to the identity of a server. It contains the domain name, the server's public key, the name of the organization that issued it, its validity period and a digital signature from that issuer. The issuer is a Certificate Authority (CA), a trusted organization such as Let's Encrypt, DigiCert or Sectigo, whose job is to verify that the person requesting a certificate really controls the domain. The server sends this certificate to the client instead of sending just a bare public key.

When issuing a certificate, the CA takes the important details, mainly the server's public key and the domain information, and runs them through a hash function such as SHA-256 to produce a fixed-size fingerprint called a hash. The CA then encrypts this hash with its own private key. The result is the digital signature. The server sends the certificate, containing the public key and details together with this signature, to the client.

The client then verifies it in two steps. First, it uses the CA's public key to decrypt the signature, which gives back the original hash the CA created, call it h1. Second, it independently computes a hash of the public key and details it received in the certificate using the same method, call it h2. If h1 and h2 are equal, the certificate has not been altered, and the public key is genuine. If an attacker had swapped the public key, h2 would not match h1, and the browser would reject the connection with a warning.

The attacker cannot get around this because producing a valid signature requires the CA's private key, which only the CA has. The attacker also cannot simply replace the whole certificate with their own, because a CA will not issue a valid certificate for a domain to someone who does not control it.

The client needs the CA's public key to check the signature, and it gets it without any network request. Browsers and operating systems ship with a built-in trust store containing the public keys of a list of trusted root CAs. In practice, root CAs rarely sign server certificates directly, since their keys are kept very secure and offline. Instead, a root CA signs an intermediate CA, and the intermediate CA signs the server's certificate. The server sends its certificate along with the intermediate certificates, and the client follows the chain upward, verifying each signature until it reaches a root it already trusts. If any link in the chain is missing, expired or invalid, the browser shows a security warning.

![TLS Handshake](../../../../assets/excalidraw/System Design/Fundamentals/Security/TLS Handshake.excalidraw)

## TLS Handshake
The steps that happen when a client connects to an HTTPS server, in simplified form, are the following.

1. The client sends a hello message listing the TLS versions and encryption methods it supports, along with a random value.
2. The server replies with its chosen version and method, its own random value, and its certificate.
3. The client verifies the certificate: the signature and chain of trust, that the domain name matches, and that it has not expired.
4. The client and server perform a key exchange, and the server proves it owns the certificate's private key by signing part of the handshake.
5. Both sides independently compute the same symmetric session key.
6. Each side confirms the handshake, and from then on all application data is encrypted with the session key.

TLS 1.3 shortened this process to fewer round trips, which makes connections start faster than before.

## Certificate Lifecycle
Certificates have a limited validity, typically from 90 days (Let's Encrypt) up to about a year, so that a compromised key is not usable forever. They must be renewed before expiry, and an expired certificate causes browsers to block the site, which is a common cause of production outages, so renewal is normally automated. If a private key is stolen or a certificate was issued by mistake, it can be revoked, and clients can check revocation status using CRLs (Certificate Revocation Lists) or OCSP (Online Certificate Status Protocol). A self-signed certificate is one signed by its own key and not by a CA. It is encrypted but not trusted by browsers, so it is only suitable for testing and internal systems.