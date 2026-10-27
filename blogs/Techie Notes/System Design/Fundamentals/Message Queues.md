A message queue is a piece of middleware that lets different applications, services or microservices communicate with each other asynchronously by passing messages. Instead of one service calling another directly and waiting for the answer, the sender puts a message into a queue and moves on, and the receiver picks the message up and processes it whenever it is ready. The queue sits in between and holds the messages safely until someone handles them. The software that runs the queue is called a message broker, and the common examples are RabbitMQ, Apache Kafka and Amazon SQS.

The easiest analogy is a post box. The sender drops a letter in and leaves, without needing the receiver to be home, and the receiver collects it later at their own pace. The two never need to be available at the same moment, and neither needs to know the other's address.

Why use queues?
1. **Decoupling:** Producers and consumers are independent, so they can be written in different languages, deployed separately and changed without breaking each other, as long as the message format stays compatible.
2. **Load Leveling:** It is where a sudden burst of traffic is stored in the queue and processed at a steady rate instead of crushing the downstream service. 
3. **Scalability:** Since adding more consumers on the same queue (competing consumers) increases processing speed without changing the producer. 
4. **Reliability:** Messages are stored until processed and failed work can be retried. 
5. **Isolation:** If the email service is down, orders are still accepted, and the emails go out when the service recovers. 
6. **Lower Latency:** Heavy tasks such as sending emails, resizing images, generating reports or processing payments can be moved out of the user's request.

## Core Components
| Component             | Role                                                                                               | Example                                    |
| --------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Producer              | The service or event source that creates a message and sends it to the broker                      | An order service publishing "order placed" |
| Message               | The data being sent: a payload (usually JSON) plus metadata such as an ID, timestamp and headers   | `{"order_id": 42, "email": "a@b.com"}`     |
| Queue                 | The buffer inside the broker where messages wait, usually read in first-in, first-out (FIFO) order | A queue named order_emails                 |
| Broker                | The server that receives, stores, routes and delivers messages                                     | RabbitMQ, Kafka, SQS                       |
| Consumer              | The service that receives a message and does the work                                              | An email service sending the confirmation  |
| Acknowledgement (ack) | The signal from the consumer that the message was processed successfully                           | `basic_ack` in RabbitMQ                    |

## Flow
The producer creates a message and sends it to the broker, which stores it in the queue, ideally on disk and replicated so it survives a crash. A consumer then receives the message, either because the broker pushes it or because the consumer pulls it. The consumer processes the message and sends an acknowledgement back. Only after the ack does the broker remove the message from the queue. If the consumer crashes or times out before acknowledging, the broker assumes the work was not done and delivers the message again, either to the same consumer or to another one. This is what makes queues reliable, since a message is not lost just because one consumer failed halfway.

## Sync vs Async Commuinication
|spect|Direct call (synchronous)|Message queue (asynchronous)|
|---|---|---|
|How it works|Service A calls Service B and waits for the response|Service A drops a message in a queue and continues|
|Coupling|Tight: A must know B and B must be running|Loose: A only knows the queue|
|If B is down|A's request fails or hangs|Messages wait in the queue until B returns|
|Traffic spikes|B is hit directly and may be overwhelmed|The queue absorbs the spike and B works at its own pace|
|Response time for the user|Includes B's processing time|Fast, since the slow work happens later|
|Getting a result|Immediately in the response|Later, through another message, a status check or a callback|
|Complexity|Simple|Extra infrastructure and eventual consistency to manage|

**Example:**
Take an online order. If the order service called the email service, the inventory service and the analytics service one after another, the customer would wait for all of them, and a failure in any one would fail the whole order. With a queue, the order service saves the order, publishes one "order placed" message and responds immediately. The email, inventory and analytics services each process that message independently. This is the same pattern as the asynchronous API, where the server returns 202 Accepted and the work continues in the background.

## Delivery Guarantees
Networks and consumers can fail at any moment, so brokers offer different promises about how many times a message is delivered.

| Guarantee     | Meaning                     | How it happens                                                       | Risk                                                        | Suitable for                                        |
| ------------- | --------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------- |
| At-most-once  | Delivered zero or one time  | The message is removed as soon as it is sent, with no retry          | Messages can be lost                                        | Metrics or logs where occasional loss is acceptable |
| At-least-once | Delivered one or more times | The message is kept until acknowledged and redelivered on failure    | Duplicates                                                  | Most business systems, and the usual default        |
| Exactly-once  | Processed exactly one time  | Needs coordination between broker and consumer, such as transactions | Complex and costly, and only true within limited boundaries | Financial processing, where supported               |

## Handling Failures
When a consumer fails to process a message, the broker retries it. A visibility timeout, used by SQS, hides the message from other consumers for a set time while one consumer works on it, and the message reappears if the consumer does not finish or acknowledge in time. Retries should use exponential backoff, which means waiting longer between each attempt, so a struggling service is not overwhelmed.

Some messages can never succeed, such as a message with corrupt data, and are called poison messages. If they are retried forever, they block the queue and waste resources. The standard solution is a dead letter queue (DLQ): after a configured number of failed attempts, the message is moved to a separate queue where it can be inspected, fixed and replayed manually. Monitoring the DLQ is an important operational task, since messages sitting there mean something is wrong.

## Ordering
A queue is described as FIFO, meaning first in, first out, but strict ordering is more complicated than it sounds. A single queue with a single consumer preserves order. As soon as several consumers read the same queue in parallel, messages are processed at the same time and may finish in a different order, and retries put old messages back behind newer ones. Standard SQS queues therefore give best-effort ordering only, while SQS FIFO queues guarantee order within a message group. Kafka guarantees order within a partition, not across the whole topic. The usual design is to keep related messages together, for example all events for one order or one user, by giving them the same key so that they land in the same partition or group and are handled in order, while unrelated messages are processed in parallel.

## Queue vs Publish
| Aspect       | Point-to-point (queue)                            | Publish/subscribe (topic)                                                  |
| ------------ | ------------------------------------------------- | -------------------------------------------------------------------------- |
| Delivery     | Each message goes to exactly one consumer         | Each message goes to every subscriber                                      |
| Typical goal | Distribute work among workers                     | Broadcast an event to many interested services                             |
| Consumers    | Compete for messages from the same queue (random) | Each subscriber gets its own copy (predefined)                             |
| Example      | A pool of workers resizing uploaded images        | "Order placed" received by email, inventory and analytics services         |
| Tools        | SQS, RabbitMQ queues                              | SNS, Google Pub/Sub, RabbitMQ exchanges, Kafka topics with consumer groups |

## Message Queue vs Event Streaming
| Aspect              | Traditional queue (RabbitMQ, SQS)                         | Event streaming (Kafka)                                                                        |
| ------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Model               | Broker holds messages until consumers process them        | An append-only log of events that is retained                                                  |
| After consumption   | Message is deleted once acknowledged                      | Message stays until the retention period ends, such as seven days                              |
| Replay old messages | Not possible once deleted                                 | Yes, a consumer can rewind and reread the log                                                  |
| Who tracks progress | Broker tracks what each message's state is                | Each consumer group tracks its own position (offset)                                           |
| Ordering            | Per queue, weakened by parallel consumers                 | Per partition, strong                                                                          |
| Scaling             | Add more consumers to a queue                             | Add partitions, with consumers spread across them                                              |
| Throughput          | Moderate to high                                          | Very high, millions of events per second                                                       |
| Routing             | Rich, with exchanges and routing rules in RabbitMQ        | Simple, by topic and partition key                                                             |
| Best for            | Task distribution, background jobs, reliable one-off work | Event streams, analytics, data pipelines, event sourcing, many consumers needing the same data |

### Types of Message Brokers
| Tool                              | Type               | Key characteristics                                                                                                                               |
| --------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| RabbitMQ                          | Traditional broker | Supports the AMQP protocol, flexible routing with exchanges, push-based delivery, good for complex routing and task queues                        |
| Apache Kafka                      | Distributed log    | Very high throughput, retained and replayable events, partitioned and replicated, used for streaming and pipelines                                |
| Amazon SQS                        | Managed queue      | Fully managed and nearly unlimited scaling, standard queues (at-least-once, best-effort order) and FIFO queues (ordered, exactly-once processing) |
| Amazon SNS                        | Managed pub/sub    | Fans out a message to many subscribers, often combined with SQS                                                                                   |
| Google Pub/Sub, Azure Service Bus | Managed messaging  | Cloud equivalents with pub/sub and queue features                                                                                                 |
| Redis Streams                     | In-memory stream   | Lightweight and fast, useful when Redis is already in use, with less durability than dedicated brokers                                            |

## Messaging Patterns
| Pattern                   | Description                                                                                             | Example                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Work queue                | Tasks are spread across a pool of workers                                                               | Image resizing, report generation                            |
| Publish/subscribe         | One event is delivered to many subscribers                                                              | "User signed up" triggering email, analytics and CRM updates |
| Request/reply             | The requester sends a message and waits for the reply on a response queue                               | Asynchronous calls where a result is needed                  |
| Saga                      | A long business transaction is broken into steps, with compensating messages for failures               | Booking flight, hotel and car, with undo steps if one fails  |
| Outbox                    | Messages are saved in the same database transaction as the data, then published, to avoid losing events | Saving an order and publishing its event reliably            |
