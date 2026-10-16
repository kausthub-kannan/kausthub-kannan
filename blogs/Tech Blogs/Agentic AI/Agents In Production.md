## Reliability & Error Handling
When agents need to be pushed for production, the durable nature matters making reliable. The approach and design of safely and intelligently handling errors, failures and retries makes the solution robust.

**Retry Logic**:
Agents can fail due to LLM calls failing or tools failing. Hence it is necessary to handle them properly. Below are few methods which can be adopted:
1. Simple Retry Logic:
   Using a fixed *wait time* the agents retries the tool call or LLM call again. This is useful when the system is small and there are less frequent retries. On larger systems multiple retries are occurring at the same time can cause retry storm using this approach. 
   
2. Exponential Back-off Logic:
   To avoid retry storms the fixed wait time becomes dynamic. Every time the failure happens again the wait time increases by a multiple of *e*. This can be further modified by adding a random number within a range called *jitter*.

3. Fallback and HITL:
   For LLM failures fallback models can be used and if the failures are critical then this could be escalated to human

4. Prompt Feedback and Circuit break:
   Agents can wander off due to hallucination, prompt feedback helps in delegating such issues. Improvising the root cause (via HITL or automated critic) Agents perform better. This approach simplified can be used to break Tool call circuits. This is when the tool keeps failing and agent keeps calling it; prompt could be injected to move on from that tool when possible.

*Integration of Temporal in Agent workflows*:
Temporal is an open-source framework making Agentic AI solution production ready by increasing reliability. When an agentic workflow crashes mid-way rather than retrying the whole workflow, temporal replays the history and restores still where it was left. This ensures no data-loss.

The workflow code is called as *Worker*. When a client hits the server with the input, Temporal puts the input into history. Worker pics up the input from the history starting the workflow. The workflow contains certain *Activities*. Activities are the dynamic part of the workflow which can fail (such as LLM calls, API calls, DB actions, etc). When activity completes the actions the results are stored in history. When the worker dies, a new worker spins up and rather than re-executing everything it replays the history and continues post that. 

*Note: Temporal is a an workflow orchestration framework similar to LangGraph. Though it is not as powerful for AI as LangGraph, it is more durable for critical applications. If used with LangGraph I should be used with high-level abstraction (an agent itself becomes and activity). Such cases it turns out be overkill and needs to be used only with necessity.*

## Safety
As agents rely on LLMs for decisions and tool calls. In such cases a layer to tackle the safety of LLM responses matters. This could either verifying approvals or preventing the response to provide sensitive data such as PHI/PII. 

**HITL**:
Human-In-The-Loop is a must inclusive technique which required to be added in Agentic workflows, especially when the agent is trying to take some critical decisions. Agents can never be hold accountable for actions as end of the day they are machines. HITL ensures that these steps are made more reliable and accountable.

**Guardrails**:
Responses from LLMs are in-deterministic. Even with modern LLMs, the generated texts can contain sensitive, unwanted data and others. Guardrails ensure that such issues can be handled easily reducing risks.

*Note: Guardrails are one of the most useful tools for agents. These ensure to tackle one of the major security issue called a prompt injection. Prompt injection occurs when LLMs are unable to enforce policy over input (which would have sensitive or malicious data) hence performing forbidden tasks*