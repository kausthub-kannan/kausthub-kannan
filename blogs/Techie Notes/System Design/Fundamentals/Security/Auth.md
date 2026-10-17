Authentication (AuthN) answers "who are you?" and authorization (AuthZ) answers "what are you allowed to do?". Authentication always comes first, since the system cannot decide what you may do until it knows who you are. A hotel is a good picture of it: showing your ID at the front desk proves who you are (authentication), and the key card you receive opens only your own room and the gym, not the other guests' rooms or the staff office (authorization).

## Authentication
Authentication verifies an identity by checking something the user has proved. The proof can be of three kinds, and combining two or more of them is called multi-factor authentication (MFA), which is much safer than a password alone.

| Factor             | What it is            | Examples                                      |
| ------------------ | --------------------- | --------------------------------------------- |
| Something you know | A secret in your head | Password, PIN                                 |
| Something you have | A device or object    | Phone with an OTP app, hardware key, SMS code |
| Something you are  | A physical trait      | Fingerprint, face scan                        |

After a successful login, the server does not ask for the password on every request. It hands the client a proof of the login to send with later requests, which is usually either a session ID stored in a cookie, with the session data kept on the server, or a signed token such as a JWT, which the server can verify without storing anything. Passwords themselves must never be stored as plain text, only as slow salted hashes (bcrypt, scrypt or Argon2), and every login must go over HTTPS.

## Authorization
Authorization decides what an already identified user may see or do. It is checked on every request, on the server, and never trusted to the client. The common models are the following.

|Model|How it decides|Example|
|---|---|---|
|ACL (access control list)|A list on each resource says who may access it|This file is readable by Asha and Ravi|
|RBAC (role-based)|Permissions belong to roles, and users are given roles|An "admin" can delete users, an "editor" can edit posts|
|ABAC (attribute-based)|Rules based on attributes of the user, resource and context|A doctor may view a record only for patients in their own hospital during working hours|

A guiding rule is the principle of least privilege: give each user and service only the access it needs and nothing more.

## Authentication vs Authorization
| Aspect              | Authentication                                     | Authorization                                        |
| ------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| Question            | Who are you?                                       | What can you do?                                     |
| Order               | First                                              | After authentication                                 |
| Based on            | Credentials: password, OTP, biometrics, token      | Roles, permissions, policies, ownership              |
| Visible to the user | Yes, a login screen                                | Usually not, the user just sees what they may access |
| Failure response    | 401 Unauthorized (really "not authenticated")      | 403 Forbidden                                        |
| Common technologies | Passwords, MFA, sessions, JWT, OpenID Connect, SSO | RBAC, ABAC, ACLs, OAuth 2.0 scopes                   |
| Example             | Logging in with email and password                 | A normal user being blocked from the admin page      |