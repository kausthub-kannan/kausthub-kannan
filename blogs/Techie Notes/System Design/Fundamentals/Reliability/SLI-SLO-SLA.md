These three terms turn the vague goal of "the system should be reliable" into something measurable, agreed on and enforceable. They sit at the centre of Site Reliability Engineering (SRE) and connect directly to observability (what you measure), resilience patterns (how you protect it) and capacity planning (how you sustain it).


|                            | SLI                                | SLO                                                     | SLA                                                                                 |
| -------------------------- | ---------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Full name**              | Service Level **Indicator**        | Service Level **Objective**                             | Service Level **Agreement**                                                         |
| **What it is**             | A measurement of service behaviour | A target for an SLI over a time window                  | A contract with consequences if the target is missed                                |
| **Nature**                 | A number (a ratio or percentile)   | An internal goal                                        | An external, usually legal or commercial, promise                                   |
| **Example**                | "Percent of requests that succeed" | "99.9 percent of requests succeed over 30 days"         | "If monthly availability drops below 99.5 percent, customers get 10 percent credit" |
| **Owned by**               | Engineering                        | Engineering and product                                 | Business, legal, sales                                                              |
| **Consequence of missing** | None by itself                     | Triggers internal action (freeze, focus on reliability) | Financial penalty, credits, contract termination                                    |

## SLI
An SLI is a **quantitative measure of some aspect of the level of service**. The most useful form is a **ratio of good events to valid events**. Expressed this way, an SLI runs from 0 to 100 percent, where higher is better. That makes SLOs, error budgets and alerts straightforward.

### Categories
|Category|Question it answers|Typical SLI|
|---|---|---|
|**Availability**|Can users get a successful response?|Successful requests / total valid requests|
|**Latency**|Is it fast enough?|Requests faster than a threshold / total requests|
|**Quality**|Is the response correct and complete (not degraded)?|Responses served without fallback or degradation / total responses|
|**Freshness**|Is the data up to date?|Records updated within X minutes / total records, or time since last successful update|
|**Throughput**|Can it handle the work?|Jobs processed per minute, batch completed on time|
|**Correctness**|Are results right?|Correct outputs / total outputs (for pipelines, financial data)|
|**Durability**|Is data retained without loss?|Objects retrievable / objects stored|
|**Coverage**|Is all the data processed?|Records processed / records received|

### SLI by System types
|System type|Primary SLIs|
|---|---|
|**Request/response service (API, web)**|Availability, latency, quality|
|**Data pipeline / batch**|Freshness, correctness, coverage, throughput|
|**Storage system**|Durability, availability, latency|
|**Streaming / queue**|Delivery latency, consumer lag, message loss|
|**Client / mobile app**|Crash-free sessions, app start time, successful actions|

### Four parts of SLI

| Part                       | Example                                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **What is a valid event?** | HTTP requests to `/api/*` from real users (exclude health checks, bots, load tests, 4xx caused by client mistakes) |
| **What is a good event?**  | Status code below 500, **and** latency under 300 ms                                                                |
| **Where is it measured?**  | At the load balancer (better than the app, because it also captures failures that never reach the app)             |
| **Over what window?**      | Rolling 28 or 30 days                                                                                              |

### Measuring SLI

|Measurement point|Pros|Cons|
|---|---|---|
|**Application server**|Easy, detailed|Misses requests that never arrive (crashes, network, overload)|
|**Load balancer / gateway**|Captures what the system actually served, including failures before the app|Less business context|
|**Client / real user monitoring**|Closest to the real experience|Noisy (client networks, devices)|
|**Synthetic probes**|Consistent, works at low traffic, catches full outages|Tests only what you script, not real user diversity|

Measuring as close to the user as is practical is usually best. The load balancer is a good default for backend services, with synthetic probes as a supplement.

Average latency hides the slow experiences. Define latency SLIs as **"the proportion of requests faster than X"** or as percentiles:

- "95 percent of requests complete in under 200 ms" (p95)
- "99 percent of requests complete in under 800 ms" (p99)

Often you use **more than one latency target** (a tight threshold for most requests and a looser one for the tail).

## SLOs
An SLO is a **target value or range for an SLI over a defined time window**.

### Components
|Component|Description|Example|
|---|---|---|
|**SLI**|What is measured|Request success ratio|
|**Target**|The objective|99.9 percent|
|**Window**|The time period|30 days, rolling|

### Rolling vs Calendar windows
|Window|Behaviour|Good for|
|---|---|---|
|**Rolling** (for example the last 28 or 30 days)|Smooth, always shows recent reality, and a bad day fades gradually|Day-to-day operations, alerting|
|**Calendar** (month or quarter)|Resets on a fixed date, aligns with business reporting and contracts|SLAs, reporting|

Many teams use a rolling window for engineering SLOs and a calendar window for SLA reporting. 28 days is popular because it always contains the same number of weekends.

### Target of choice
|Availability|Downtime per year|Per 30-day month|Per week|
|---|---|---|---|
|90 percent ("one nine")|36.5 days|72 hours|16.8 hours|
|99 percent|3.65 days|7.2 hours|1.68 hours|
|99.5 percent|1.83 days|3.6 hours|50.4 minutes|
|99.9 percent ("three nines")|8.76 hours|43.2 minutes|10.1 minutes|
|99.95 percent|4.38 hours|21.6 minutes|5.04 minutes|
|99.99 percent ("four nines")|52.6 minutes|4.32 minutes|1.01 minutes|
|99.999 percent ("five nines")|5.26 minutes|25.9 seconds|6.05 seconds|

Each extra nine is roughly **10 times harder and more expensive**. Four nines leaves under 5 minutes of downtime a month, which is less than the time it takes a human to be paged and respond. That level generally needs full automation, redundancy and multi-region design.

- **100 percent is the wrong target.** It is impossible, extremely expensive, and leaves no room to ship changes. It also usually exceeds the reliability of the user's own device, network or ISP.
- **Start from user expectations and business need**, not from what you currently achieve. Then check against reality.
- **Be slightly worse than users would be happy with**, not as good as technically possible. Users do not notice the difference between 99.99 and 99.999 percent if their own connection is 99.9 percent.
- **Your SLO cannot exceed your dependencies.** If you depend serially on three services that are each 99.9 percent available, your ceiling is roughly `0.999^3 ≈ 99.7 percent`, unless you add redundancy, fallbacks or graceful degradation.
- **Start loose, then tighten.** It is easier to raise a target you are comfortably meeting than to walk back an unrealistic one.
- **Use different SLOs for different tiers.** Checkout and login might be 99.95 percent, internal reporting 99 percent.
- **Keep the number of SLOs small.** Typically 2 to 4 per service. More than that means nobody knows which matter.

### Composite availability
|Dependency structure|Rough combined availability|
|---|---|
|**Serial** (all must work)|Multiply: `A x B x C`|
|**Parallel / redundant** (any one works)|`1 - (1-A)(1-B)`|

For example, two independent 99 percent replicas in parallel give `1 - 0.01 x 0.01 = 99.99 percent` (in theory, assuming independent failures, which is often optimistic).

## SLA
An SLA is a **formal agreement between a provider and a customer** that defines the expected level of service and what happens if it isn't met.

|Element|Description|
|---|---|
|**Service definition**|What is covered, and what isn't (beta features, third-party integrations)|
|**Metrics and targets**|For example 99.9 percent monthly uptime|
|**Measurement method**|Who measures, from where, and how|
|**Exclusions**|Scheduled maintenance, force majeure, customer-caused issues, DDoS, outages of customer's own systems|
|**Remedies**|Service credits, refunds, termination rights|
|**Claim process**|How and by when the customer must report and request credits|
|**Support terms**|Response and resolution times by severity|
|**Reporting**|How often performance is reported|

### Example
|Monthly uptime|Service credit|
|---|---|
|Below 99.9 percent but at least 99.0 percent|10 percent of monthly fee|
|Below 99.0 percent but at least 95.0 percent|25 percent of monthly fee|
|Below 95.0 percent|50 percent of monthly fee|

- **Looser than the SLO.** If the internal SLO is 99.95 percent, the SLA might be 99.9 percent or 99.5 percent. The gap is your safety margin.
- **Consequences are financial or contractual**, so lawyers and the business are involved, not only engineers.
- **Not every service needs an SLA.** Internal services typically have SLOs only. SLAs mainly apply to paying external customers.
- **Be careful about what you promise.** Define measurement and exclusions precisely. Vague SLAs lead to disputes.
- **Related terms:** an **OLA (Operational Level Agreement)** is an internal agreement between teams that supports an SLA. Support SLAs also commonly include **response time** and **resolution time** targets.
- **Cloud provider SLAs** are worth knowing: they define the ceiling for your own design, and credits rarely cover your real losses.

## Error Budgets
The **error budget** is the amount of unreliability your SLO permits:

```
Error budget = 100 percent - SLO target
```

|SLO|Error budget|In a 30-day month (time)|In 10 million requests|
|---|---|---|---|
|99 percent|1 percent|7.2 hours|100,000 failed requests|
|99.9 percent|0.1 percent|43.2 minutes|10,000 failed requests|
|99.99 percent|0.01 percent|4.32 minutes|1,000 failed requests|

Error budgets turn the tension between **shipping features** (which risks breakage) and **reliability** (which slows change) into a shared, objective rule:

- **Budget remaining:** you can ship, experiment, run risky migrations and chaos tests.
- **Budget nearly spent:** slow down, add safeguards, prioritise reliability work.
- **Budget exhausted:** freeze non-essential releases until reliability is restored.

This removes arguments between "dev wants to ship" and "ops wants stability", because both agree on the budget in advance.

### Error budget policy
|Budget state|Action|
|---|---|
|**More than 50 percent remaining**|Normal development and releases|
|**Between 10 and 50 percent remaining**|Extra review for risky changes, prioritise reliability fixes in planning|
|**Under 10 percent remaining**|Only critical fixes and reliability work, release approvals required|
|**Exhausted**|Feature freeze, postmortem actions take priority until back within SLO|
|**Single incident consumed more than 20 percent**|A postmortem is required with follow-up actions|

The policy needs **agreement from product, engineering and leadership**. Without that buy-in, nobody honours the freeze.

### Budget consumption
- Outages and incidents
- Bad deployments and failed rollouts
- Planned maintenance and risky migrations
- Experiments and chaos engineering
- Dependency failures
- Slow degradation (latency creeping over the threshold)

## Burn Rate alerting
**Burn rate** is how fast you're consuming the error budget relative to the rate that would use it up exactly at the end of the window.

```
Burn rate = (observed error rate) / (error rate allowed by the SLO)
```

- Burn rate **1** means the budget runs out exactly at the end of the window (sustainable).
- Burn rate **10** means the budget runs out in 1/10 of the window.
- For a 99.9 percent SLO over 30 days, the allowed error rate is 0.1 percent. If the current error rate is 1.44 percent, burn rate is `1.44 / 0.1 = 14.4`, and the whole month's budget is gone in about 2 days.

A fixed threshold such as "error rate over 1 percent" either pages for tiny blips that don't matter or misses slow leaks that quietly consume the budget. Burn-rate alerts are tied directly to **user impact against the objective**.

### Multi-window, multi-burn-rate alerts
Use a long window to confirm the problem is real and a short window to confirm it is **still happening** (so alerts reset quickly once fixed). Example for a 30-day SLO (from the Google SRE Workbook):

|Severity|Burn rate|Long window|Short window|Budget consumed if sustained|Response|
|---|---|---|---|---|---|
|**Page**|14.4|1 hour|5 minutes|2 percent in 1 hour|Immediate|
|**Page**|6|6 hours|30 minutes|5 percent in 6 hours|Immediate|
|**Ticket**|3|1 day|2 hours|10 percent in 1 day|Working hours|
|**Ticket**|1|3 days|6 hours|10 percent in 3 days|Working hours|

An alert fires only when **both** windows exceed the burn-rate threshold.

## Best way to choose SLIs and SLOs
Start with **what users do and care about**, not what is easy to measure.
1. List the **critical user journeys** (log in, search, add to cart, pay, upload).
2. For each, decide what "working well" means (success, speed, correctness).
3. Choose SLIs that capture it, measured as close to the user as practical.
4. Set a target and window, and check it against historical data.
5. Review with product and stakeholders.
6. **Fewer, meaningful SLOs** beat dozens of narrow ones.
7. Make SLIs **simple enough that everyone can explain them**.
8. **Exclude** traffic that isn't real user demand (health checks, bots, load tests), and client errors that aren't your fault.
9. Count **degraded responses** (served from a fallback) in a **quality** SLI. Otherwise graceful degradation hides real problems.
10. **Review SLOs regularly** (quarterly): are they too tight, too loose, still matching user needs?

|Poor SLI|Why it's poor|Better|
|---|---|---|
|CPU utilisation|A cause, not user experience|Request success and latency|
|Server uptime|The server can be up while the service is broken|Successful requests / valid requests|
|Average latency|Hides slow tail|Proportion of requests faster than threshold|
|Number of errors logged|Depends on logging habits, not user impact|Ratio of failed to valid requests|
|Queue depth|A symptom|Age of oldest message, or end-to-end processing time within target|
|Health check passes|Shallow, doesn't reflect real use|Real or synthetic journey success|