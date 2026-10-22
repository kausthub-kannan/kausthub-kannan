A WebSocket is a communication protocol that enables full-duplex communication between a client and a server over a single, long-lived connection. In the traditional HTTP request-response model, the client starts every exchange and the server can only answer. With WebSockets, both sides can send messages independently at any time while the connection stays open, so the server can push data to the client the moment something happens, without the client asking.

The protocol is standardized in RFC 6455. It is commonly used for real-time applications such as live delivery tracking, chat, multiplayer games, collaborative editors, live dashboards and financial market updates. The connection uses `ws://` for unencrypted communication and `wss://` for encrypted communication. In production, `wss://` is the one to use, because it runs over TLS and protects data in transit, as covered in the SSL/TLS notes.

Before WebSockets, the options for getting live data over plain HTTP were awkward. Polling asks the server repeatedly, which wastes requests when nothing has changed, and long polling holds a request open until there is something to send, but needs a new request after every message. Each HTTP request also carries headers (cookies, authentication and so on), which can be larger than the actual message. A WebSocket pays the connection setup cost once, after which each message has only a few bytes of framing overhead.

|Aspect|HTTP request-response|WebSocket|
|---|---|---|
|Who can send|Client asks, server answers|Both sides, at any time|
|Connection|Usually short-lived, a new exchange per request|One long-lived connection|
|Overhead per message|Full headers each time|A few bytes of framing|
|Server push|Not natively|Native|
|State|Stateless|Stateful, the connection itself is state|
|Caching|Easy, built into HTTP|Not applicable|
|Load balancing and scaling|Easy, any request can go to any server|Harder, a connection is tied to one server|
|Best for|Standard APIs and pages|Real-time, frequent, two-way updates|

WebSockets also differ from Server-Sent Events (SSE), which are one-way from server to client over HTTP. SSE is simpler and sufficient when the client only needs to receive updates, such as a live feed, and WebSockets are the better choice when the client also needs to send frequent messages, such as in chat or games.

## Working

### Establishing Connection
A WebSocket connection begins with an ordinary HTTP request. The client asks the server to upgrade the connection to the WebSocket protocol.

```
GET /ws HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

If the server accepts, it replies with the status code `101 Switching Protocols`.

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

The `Sec-WebSocket-Accept` value is computed from the client's key, which proves to the client that the server really understands WebSockets. After this, the same TCP connection stops carrying HTTP and carries WebSocket frames instead, so no further HTTP requests are made for each message. Starting with HTTP is also what lets WebSockets pass through ports 80 and 443 and work with existing web infrastructure.

### Message Exchange
Once connected, the client and server send messages independently. In a delivery tracking app, the client can send a subscription for a specific order, and the server can push location updates, delivery status changes and notifications as they happen. Messages can be text (usually JSON) or binary data. Besides data frames, the protocol defines control frames: ping and pong, which check that the other side is alive, and close, which ends the connection in an orderly way.

### Connection Termination
A WebSocket connection stays open until either side closes it, the network fails or an intermediary, such as a proxy or load balancer, ends it. A persistent connection does not guarantee it will stay alive forever, so applications must detect failures and reconnect. A clean close uses a close frame with a status code.

![Web Sockets](../../../../assets/excalidraw/System Design/Fundamentals/Networking/Web Sockets.excalidraw)

|Code|Meaning|
|---|---|
|1000|Normal closure|
|1001|Going away, for example the server is shutting down or the user left the page|
|1008|Policy violation, for example failed authorization|
|1011|The server hit an unexpected error|
|1006|Abnormal closure, reported locally when the connection dropped without a close frame|

## Load balancing in Websockets
Unlike ordinary HTTP requests, which an L7 load balancer can route independently to any backend, a WebSocket connection stays attached to the server that accepted it for as long as it lasts. The balancing decision is made once, at connection time. This changes how load balancing works:
- The LB must pass the **upgrade handshake** through (an L7 LB has to forward the `Upgrade` and `Connection` headers; an L4 LB just relays bytes and needs no special support).
- The LB must tolerate **long-lived connections**, so idle timeouts have to be raised. Sending periodic **ping/pong heartbeats** is better than relying on a huge timeout alone, because it keeps the connection from looking idle and also detects dead peers.

If the server holding a connection fails, all of its connections are lost, and clients must reconnect (landing on another server) and resume. That’s another reason for the reconnect logic discussed earlier.

For distributing load, **least connections** usually works better than round robin, because connections last very different lengths of time and the number currently open is what actually loads a server. Also, existing connections never move: a newly added server only receives _new_ connections, so rebalancing means gradually draining and reconnecting clients.

Load balancers come in two kinds, and they treat WebSockets differently. An **L4 load balancer** works at the TCP level: it looks only at IPs and ports, picks a backend when the connection’s first packet arrives, and relays that connection’s traffic to the same backend from then on, without reading or terminating anything. The WebSocket upgrade passes through as ordinary bytes, so it needs no special WebSocket support, and it adds very little overhead. The tradeoff is that it can’t see the HTTP content, so it can’t route by URL path or header, and TLS is usually passed through for the backend to handle. An **L7 load balancer** (nginx, Envoy, an AWS ALB) terminates the client’s TCP and TLS connections, reads the HTTP upgrade request, and opens a separate connection to the chosen backend, relaying WebSocket frames between the two. This lets it route by path or host (for example `/ws` to a WebSocket pool and everything else to the REST servers), authenticate during the upgrade, and handle TLS centrally. But it must be configured to forward the `Upgrade` and `Connection` headers, and its idle timeouts must be raised, because it holds two live connections per client and will cut either one if it sits quiet too long. For both types, the balancing decision happens once, at connection time, and the connection stays pinned to that backend until it closes.

## Scaling
Suppose a customer is connected to gateway 1, watching their delivery, and the driver's location update arrives at gateway 2. Gateway 2 has no connection to that customer, so how does the update reach them?

The standard answer is a publish/subscribe backplane. Every gateway subscribes to a shared message system, such as Redis Pub/Sub, Kafka or NATS, for the topics its connected clients care about. When a location update comes in, it is published once to a topic such as `order:42`, and every gateway that holds a subscriber for that order receives it and pushes it down the right socket.

This keeps the gateways thin and interchangeable: they only hold open connections and forward messages, while the real state lives elsewhere, such as the latest driver location in Redis, so a client that reconnects can immediately get the current state. This approach ties back to the message queue and scaling notes, and it follows the same rule as stateless services: keep as little state as possible in the server process.

The number of connections one server can hold is limited by memory (each connection takes some tens of kilobytes or more) and by operating system limits such as the number of open file descriptors. A well-tuned server can hold tens or hundreds of thousands of idle connections, but the real limit depends on how much traffic each one carries, so capacity should be tested and the number of gateways scaled out as connections grow. Autoscaling is usually based on the number of open connections, not on CPU alone.

![Scaling Web Sockets](../../../../assets/excalidraw/System Design/Fundamentals/Networking/Scaling Web Sockets.excalidraw)

## Security
| Concern                        | What to do                                                                                                                                                                                                                              |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unencrypted traffic            | Always use `wss://` so the data is protected by TLS                                                                                                                                                                                     |
| Authentication                 | Browsers cannot set custom headers on a WebSocket, so authenticate with a cookie, a short-lived token sent as the first message, or a one-time ticket obtained over HTTP. Avoid long-lived tokens in the URL, since URLs end up in logs |
| Authorization                  | Check on every subscription that this user may see this data. A customer must only be able to subscribe to their own order, otherwise anyone could change the order ID and watch someone else's delivery                                |
| Cross-site WebSocket hijacking | A malicious website can open a WebSocket to your server using the visitor's cookies, so check the `Origin` header on the handshake and reject unknown origins                                                                           |
| Abuse and overload             | Limit message size, the number of connections per user and the message rate, and close connections that misbehave                                                                                                                       |
| Expired credentials            | Connections last long, so re-check or expire the session periodically, not only at connect time                                                                                                                                         |
| Untrusted input                | Validate every incoming message, as with any API                                                                                                                                                                                        |