HTTP is stateless: each request arrives with no memory of the previous one. After a user logs in, the server needs a way to recognize that user on every later request without asking for the password again. This is session management, and there are two main approaches: the server remembers the user (server-side sessions), or the client carries a signed proof of identity (tokens such as JWT). A different but related problem is letting one application act on a user's behalf in another service without handing over a password, which is what OAuth 2.0 solves. These three topics are often used together, so it is important to be clear about what each one is for.

|Topic|What it is|Answers|
|---|---|---|
|Session|Server stores the login state, and the client holds an ID|"Who is this request from?"|
|JWT|A signed token that contains the identity and claims|"Who is this request from?", without the server storing anything|
|OAuth 2.0|A protocol for delegated access|"Can this app access my data in that service, and how much?"|

## Session Management

### Server Side Sessions
After the user logs in successfully, the server creates a session: a record on the server holding who the user is, when the session started and any other state. It generates a long, random, unguessable session ID and sends it to the browser in a cookie. The browser sends this cookie automatically with every request, and the server looks the ID up to find the session.

The sessions is established in below steps:
1. POST /login (email + password)
2. Server verifies, creates session {id: "9f8a...", userId: 42}, stores it
3. Response: Set-Cookie: sid=9f8a...; HttpOnly; Secure; SameSite=Lax
4. Later requests: Cookie: sid=9f8a...  ->  server looks up the session
5. POST /logout -> server deletes the session, the ID stops working

The big advantage of sessions is control. Because the state lives on the server, a session can be ended instantly, for example on logout, a password change or a suspected breach, and nothing sensitive is stored in the browser, only a meaningless ID. The disadvantage is that the server must store and look up the session on every request. In a system with several servers behind a load balancer, this means the sessions must be shared, which is why session data is kept in a fast shared store such as Redis, as in the scaling and caching notes, instead of in the memory of one server. The alternative, sticky sessions, ties each user to one server and complicates scaling and failover.

### Cookie Security Settings
The cookie that holds the session ID must be protected, since anyone who steals it can pretend to be the user.

|Attribute|What it does|
|---|---|
|HttpOnly|JavaScript cannot read the cookie, which protects it from theft through XSS (cross-site scripting)|
|Secure|The cookie is sent only over HTTPS|
|SameSite (Lax or Strict)|The browser does not send the cookie on most cross-site requests, which greatly reduces CSRF attacks|
|Expires or Max-Age|Limits how long the cookie lives|
|Domain and Path|Restrict which sites and URLs receive the cookie|

### Good Practices
- Generate session IDs with a cryptographically secure random generator, with enough length that guessing is impossible.
- Create a new session ID at login. Reusing the ID from before login allows session fixation, where an attacker plants a known ID and waits for the victim to log in with it.
- Use two timeouts: an idle timeout (for example 30 minutes without activity) and an absolute timeout (for example 24 hours, however active the user is).
- Destroy the session on the server at logout. Deleting only the cookie in the browser is not enough.
- Require re-authentication for sensitive actions, such as changing a password or making a large payment.
- Defend against CSRF, where another website tricks the browser into sending a request with the user's cookie, using SameSite cookies and anti-CSRF tokens for state-changing requests.
- Always use HTTPS, as in the TLS notes, since a session ID sent in plain text can be captured.

## JWT
A JWT is a compact, signed token that carries information, called claims, about the user and the token itself. Because it is signed, any server that has the right key can check that it is genuine and unmodified, without looking anything up in a database. This is why a JWT is called self-contained and why it fits stateless services.

A JWT has three parts, separated by dots: `header.payload.signature`. The header and payload are JSON objects encoded in Base64URL, and the signature is computed over them with a key.

| Part      | Contents                                    | Example (decoded)                                                                                                                     |
| --------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Header    | Signing algorithm and the key ID            | `{"alg": "RS256", "typ": "JWT", "kid": "key-1"}`                                                                                      |
| Payload   | The claims                                  | `{"iss": "https://auth.example.com", "sub": "42", "aud": "orders-api", "exp": 1760000900, "iat": 1760000000, "scope": "orders:read"}` |
| Signature | Signature of the encoded header and payload | Computed with a secret or private key                                                                                                 |

The standard claims are the following.

|Claim|Meaning|
|---|---|
|iss|Issuer, who created the token|
|sub|Subject, who the token is about, usually the user ID|
|aud|Audience, which service the token is meant for|
|exp|Expiry time, after which the token must be rejected|
|iat|Issued-at time|
|nbf|Not valid before this time|
|jti|Unique ID of the token, useful for revocation|

A very important point: a normal JWT is signed, not encrypted. Anyone who holds the token can decode the payload and read it, so secrets and sensitive personal data should never be placed in it. The signature only guarantees that the contents have not been changed. (An encrypted variant, JWE, exists but is less common.)

### Signing Algorithms
|Type|Algorithms|How it works|Use when|
|---|---|---|---|
|Symmetric|HS256|One shared secret both signs and verifies|A single service issues and verifies its own tokens|
|Asymmetric|RS256, ES256|A private key signs, and the public key verifies|Many services must verify tokens but only the auth server may issue them|

With asymmetric signing, the authorization server publishes its public keys, usually in a JWKS (JSON Web Key Set) endpoint, and each API selects the right key using the `kid` header. The APIs never hold the signing key, so a compromise of one API cannot be used to forge tokens. This is the same public/private key idea as in the TLS notes.

### JWT API Verification
On every request, the API reads the token from the `Authorization: Bearer <token>` header and checks, in order: that the signature is valid using the expected algorithm and key, that the token has not expired (`exp`), that the issuer (`iss`) is the one it trusts, and that the audience (`aud`) is itself. Only then does it trust the claims, such as the user ID and scopes, and apply its authorization rules. No database lookup is needed, so any server can verify the token, which makes it easy to scale horizontally.

### Strength vs Weakness
|Strengths|Weaknesses|
|---|---|
|Stateless, so no session store and easy scaling|Hard to revoke: a token stays valid until it expires, even after logout or a breach|
|Works across many services, domains and mobile apps|Larger than a session ID, and sent with every request|
|Verification is local and fast|Claims can go stale, for example a user's role changes but the token still carries the old one|
|Carries useful claims, so services need fewer lookups|If stolen, it can be used by anyone until it expires|
|Fits microservices and API gateways|Easy to implement insecurely|

### Access Token vs Refresh Token
Because a JWT cannot be easily revoked, the standard approach is to make the access token short-lived, usually 5 to 15 minutes, which limits the damage if it leaks. To avoid forcing the user to log in again every few minutes, the server also issues a refresh token, which is long-lived (days or weeks) and can only be used to obtain new access tokens from the authorization server. Refresh tokens are stored more carefully and are kept on the server side as records, so they can be revoked. Good practice is refresh token rotation: each time a refresh token is used, a new one is issued and the old one is invalidated, so that a stolen refresh token that is used twice can be detected and the whole session cut off.

## OAuth 2.0
OAuth 2.0 is an authorization framework that lets an application obtain limited access to a user's resources in another service, on the user's behalf, without ever seeing the user's password. Before OAuth, a photo-printing site that wanted your photos from another service would ask for your username and password there, which gave it full access to everything with no way to limit or withdraw it. With OAuth, you log in only at the service that owns the data, you approve a specific, limited permission, and the app receives a token that can do only that and that can be revoked.

|Role|Who it is|Example|
|---|---|---|
|Resource owner|The user who owns the data|You|
|Client|The application that wants access|A photo-printing app|
|Authorization server|Authenticates the user, asks for consent and issues tokens|Google's login and consent service|
|Resource server|The API that holds the data and accepts tokens|Google Drive's API|

Key terms: a scope is a named permission that limits access, such as `drive.read`. An access token is the credential the client sends to the resource server. A refresh token is used to get new access tokens. The redirect URI is where the authorization server sends the user back after approval, and it must match one registered in advance exactly.

### Authorization Code Flow with PKCE
This is the recommended flow for web apps, single-page apps and mobile apps. PKCE (Proof Key for Code Exchange, pronounced "pixy") protects it against interception of the authorization code, and it is now advised even for clients that have a secret.

![PKCE](../../../../assets/excalidraw/System Design/Fundamentals/Security/PKCE.excalidraw)

The steps in detail:

1. The client generates a random code verifier, derives from it a code challenge (its SHA-256 hash, Base64URL-encoded), and a random `state` value. It redirects the user to the authorization server.
2. The user logs in to the authorization server, and sees which permissions the app requests, and approves them.
3. The authorization server redirects back to the client's redirect URI with a short-lived, single-use authorization code and the same `state`. The client checks that `state` matches, which protects against CSRF.
4. The client sends the code to the token endpoint, together with the original code verifier. The server hashes the verifier and compares it with the challenge it saw earlier, so an attacker who stole the code but lacks the verifier cannot use it.
5. The server responds with tokens, and the client calls the resource server with `Authorization: Bearer <access_token>`.

The reason for going through the browser and then exchanging a code, instead of returning the token directly, is that the browser redirect passes through places such as history and logs where tokens would leak, while the code is useless without the verifier and is exchanged over a direct back-channel request.

### Grant Types
|Grant type|Used for|Notes|
|---|---|---|
|Authorization Code (with PKCE)|Web, mobile and single-page apps acting for a user|The standard choice|
|Client Credentials|Machine-to-machine calls, with no user involved|A backend service authenticates with its own ID and secret|
|Device Code|Devices with no browser or keyboard, such as TVs and command-line tools|The user approves on another device|
|Refresh Token|Getting a new access token without the user logging in again|Used with the other flows|
|Implicit (legacy)|Returned the token directly in the browser redirect|Deprecated, since tokens leak and cannot be protected|
|Resource Owner Password (legacy)|The app collects the user's password directly|Deprecated, since it defeats the point of OAuth|

### Opaque vs JWT token
OAuth does not define what an access token looks like, and there are two common designs.

|Aspect|Opaque token|JWT access token|
|---|---|---|
|Content|A random string with no meaning|A signed token containing claims|
|How the API validates it|Calls the authorization server's introspection endpoint|Checks the signature and claims locally|
|Revocation|Easy and immediate|Hard, depends on short expiry|
|Speed and load|An extra network call per check, which can be cached|No call, scales easily|
|Information exposed to the client|None|Claims are readable|

**Note on OpenID:**
OAuth 2.0 on its own says nothing about who the user is, only that the app has been given permission. OpenID Connect (OIDC) adds a thin identity layer on top. When the client includes the `openid` scope, the authorization server also returns an ID token, which is a JWT containing claims about the user, such as `sub`, `email` and `name`, and when and how they authenticated. The ID token is for the client app to learn who logged in, and the access token is for calling APIs, so the two must not be mixed up. "Sign in with Google" is OIDC, and "allow this app to read your Google Drive" is OAuth.

## Common Attack Patterns
| Attack                            | What happens                                                 | Defense                                                                       |
| --------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Session fixation                  | Attacker sets a known session ID before login                | Issue a new ID at login                                                       |
| Session hijacking                 | Session ID or token is stolen                                | HTTPS, HttpOnly and Secure cookies, short lifetimes, bind or monitor sessions |
| XSS                               | Malicious script steals tokens from the page                 | HttpOnly cookies, input escaping, Content Security Policy                     |
| CSRF                              | Another site makes the browser send an authenticated request | SameSite cookies, anti-CSRF tokens, the OAuth `state` parameter               |
| Authorization code interception   | Attacker steals the code from the redirect                   | PKCE                                                                          |
| Redirect URI manipulation         | Attacker redirects the code or token to their own site       | Require exact-match registered redirect URIs                                  |
| JWT algorithm confusion or "none" | Forged tokens are accepted                                   | Fix the allowed algorithms, always verify the signature                       |
| Token replay                      | A stolen token is reused                                     | Short expiry, HTTPS, refresh token rotation                                   |
| Over-broad scopes                 | A token can do more than needed                              | Request and grant the minimum scope                                           |
| Confused audience                 | A token meant for one API is accepted by another             | Always validate `aud`                                                         |