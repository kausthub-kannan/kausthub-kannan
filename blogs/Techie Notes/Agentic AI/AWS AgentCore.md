AWS Agent Core is service provided to build, monitor, deploy and maintain agents. It has 4 main capabilities:

**AgentCore Runtime**:
Provides low-latency serverless environments with session isolation, supporting any agent framework including popular open source frameworks, tools, and models, and handling multi-modal workloads and long-running agents. AWS It supports up to 8-hour execution windows. In nutshell:
	*It can be said as a simple wrapper around agent frameworks like LangGraph*

**AgentCore Memory**:
Includes episodic memory, enabling agents to learn and adapt from experiences, building knowledge over time to create more human-like interactions.
	*AgentCore Memory is a vital part of AgentCore which provides out of the box way to store data and manage them*

**AgentCore Gateway**:
Transforms existing APIs, databases, or services into tools that any MCP-compatible agent can use. You can deploy a gateway that wraps your Lambda functions, making your backend instantly accessible to agents without rewriting code.
	*Gateway let's interact with tools which are built in AWS services like lambdas*

**AgentCore Policy**:
Integrates with AgentCore Gateway to intercept tool calls as they happen, processing requests while maintaining operational speed. You can create policies using natural language or directly use Cedar — an open source policy language for fine-grained permissions — simplifying the process to set up, understand, and audit rules without writing custom code.
	*AgentCore Policy is a real-time guardrail that intercepts every outbound tool call from the agent to the Gateway and allows or blocks it based on Cedar rules — before the underlying Lambda or API is ever invoked.*

Apart from 4 capabilities, there two more: **AgentCore Evaluations** and **AgentCore Browser** which let agents be more observable and let them interact with web-based workflows respectively.