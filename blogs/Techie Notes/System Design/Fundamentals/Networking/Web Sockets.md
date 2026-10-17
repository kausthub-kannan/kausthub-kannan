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

|Code|Meaning|
|---|---|
|1000|Normal closure|
|1001|Going away, for example the server is shutting down or the user left the page|
|1008|Policy violation, for example failed authorization|
|1011|The server hit an unexpected error|
|1006|Abnormal closure, reported locally when the connection dropped without a close frame|

## Loadbalancing in Websockets
Unlike ordinary HTTP requests, which can be routed independently to any server, a WebSocket connection stays attached to the gateway (server) that accepted it, for as long as it lasts. This changes how load balancing works. The load balancer must support WebSocket upgrades and allow connections that last for a long time, so idle timeouts need to be raised, and requests need to be passed on with the upgrade headers. For nginx, that looks like this.

```
location /ws {
    proxy_pass http://websocket_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}
```

If the gateway fails, all its connections are lost, and clients must reconnect to another gateway, which is another reason for the reconnect logic above. For balancing the load, "least connections" tends to work better than round robin, since connections last very different amounts of time and the number currently open is what really matters.

Sticky sessions can help when an application requires a client's repeated connections to reach the same instance, for example when reconnecting to resume a session. But they do not solve message distribution across multiple instances, which is the bigger problem, covered next.

## Scaling
uppose a customer is connected to gateway 1, watching their delivery, and the driver's location update arrives at gateway 2. Gateway 2 has no connection to that customer, so how does the update reach them?

The standard answer is a publish/subscribe backplane. Every gateway subscribes to a shared message system, such as Redis Pub/Sub, Kafka or NATS, for the topics its connected clients care about. When a location update comes in, it is published once to a topic such as `order:42`, and every gateway that holds a subscriber for that order receives it and pushes it down the right socket.

```
 Driver app --> Location service --publish--> [ Redis / Kafka topic: order:42 ]
                                                    |               |
                                          subscribed by      subscribed by
                                            Gateway 1          Gateway 3
                                                |                  
                                          pushes to customer's socket
```

This keeps the gateways thin and interchangeable: they only hold open connections and forward messages, while the real state lives elsewhere, such as the latest driver location in Redis, so a client that reconnects can immediately get the current state. This approach ties back to the message queue and scaling notes, and it follows the same rule as stateless services: keep as little state as possible in the server process.

The number of connections one server can hold is limited by memory (each connection takes some tens of kilobytes or more) and by operating system limits such as the number of open file descriptors. A well-tuned server can hold tens or hundreds of thousands of idle connections, but the real limit depends on how much traffic each one carries, so capacity should be tested and the number of gateways scaled out as connections grow. Autoscaling is usually based on the number of open connections, not on CPU alone.

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