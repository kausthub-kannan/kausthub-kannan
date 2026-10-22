Graph defines a structure of agentic or multi-agentic flow. These can be visualised as workflows quite similar to AWS Step function but focused on LLM-based decision making and more flexible.

**Nodes & Edges**:
Agentic  Workflows consists of two main components; Nodes and Edges. Nodes represent certain action to be executed. These can be LLM calls, Human-In-The-Loop (HITL), Tool Call and others. LangGraph defines the start of a graph as a **Start Node** and the terminal node as **End**. On code Nodes are python functions.

Edges connect these Nodes making graphs. Edges are of two basic type:
1. **Normal**: These connect nodes directly creating a sequential network
2. **Conditional**: Conditional graphs allow dynamic routing. Using decision making techniques, edges can direct connect to multiple nodes and can route based on the condition. When parallel execution occurs and need to converge *Reducers* need to be used.
   Note: Conditional Nodes enable **Map Reduce**. When rather than condition based routing, same node is called multiple times concurrently via a loop creating a *Map*. Using *Reducers* the outputs are combined. *The calling of same nodes concurrently can be done using LangGraph Send API.*

LangGraph introduces a powerful API called *Command*. This removes the necessities of creating edges .i.e conditional edges separate from the node. Command can update the State and dynamically call the next node (or graph/agent). This makes all routing to be done by nodes and removes the concept of edges on code. This also allows HITL to exist within the node.

**States**:
States define the input to be sent to a node (and can also be used for output of a graph). They play a vital role in handling memory of the graph. States define schema of *keys* (variables) which are used in the agent graph. These variables can also be defined with *reducers*.

*Note: Agents have parallel and sequential execution. If seen as a binary tree concept each level is called as a super-state. Every sequential node is a different super-state but where as every parallel executing nodes of same level is consider in the same super-state.*

**Reducers**:
When nodes run parallel or to the same state variable the data needs to be appended (such as messages), *Reducers* help in using in-built or custom functions to handle such data. They can be further used for trimming, filtering etc.

*Note: LangGraph provides a pre-built `add_messages` reducer and a ready-to-use `MessageState` that manages message history out of the box, with support for custom keys alongside the default `messages` key.*

**Tools**:
Tools are useful to perform certain activity based on LLM decision taken such as calling external API.  The LLM when given with tools, returns the arguments and tool name, which then can be sent to a tool call node.

*Understanding them all together*
Graphs accept inputs — including messages managed via reducer functions — as States. Nodes are functions that take these States and perform actions, with Chat Models, Tools, and other components as part of their logic. Edges connect nodes and handle routing: rule-based or conditional decision-making that determines the next step, including whether to invoke a tool or not

# Agent Memory

Memory is useful to retain the input or output from previous execution of the graph. 
LangGraph does this with *checkpointers* and *threads*. The state of every super-state can be saved in memory as a **checkpoint** identified with a *checkpoint id*. The information of an end-to-end invoke (all the super-states) is saved as a **thread** identified with a *thread id*. When a new invocation is performed the previous invoke data can be passed using the thread id.

Threads and checkpoints come under *Short-term memory*. But when memory needs to be taken from different places, facts (from VectorDB, SQL, etc.). This is termed as *Long-term memory*. Checkpoints can be saved in databases to extend data. 

![Simple Agent flow](../../assets/excalidraw/Agentic AI/Simple Agent flow.excalidraw){ width="800" }

**Memory handling**:
With increased number of invokes and runs, memory size increases and becomes not scale-able to use all of it. Both memories require selective consideration of required data. This is done using *filtering* and *trimming*. For filtering simple techniques such as summarization, semantic search and others. Trimming is token based approach of handling data. These approaches can be selected intuitively based on use cases.

# HITL and ReAct

**ReAct**:
It is a pattern where the output of a model or tool is fed back into the model as input — for example, the output of a tool node is returned to the calling node for further reasoning. **Re**ason (interpret the output and decide the next step) + **Act** (execute and observe the result). This pattern is particularly useful when the same or similar tools are called repeatedly, such as tools that interact with a database.

![ReAct](../../assets/excalidraw/Agentic AI/ReAct.excalidraw){ width="100" }

**Human-In-The-Loop (HITL)**:
Human-in-the-Loop (HITL) ensures that major decisions made by models or agents are verified and approved before proceeding to the next node or agent, reducing security risks and preventing cascading failures.

Breakpoints are used to introduce HITL — either between a model output and a tool call, or at higher-level agentic decision points such as altering database data or schema. These breakpoints pause execution and require explicit approval before continuing.

In LangGraph, this is achieved through controlled streaming. Streaming enables node-by-node execution, and by introducing `interrupt` at specific nodes, the stream pauses at that point and can be resumed from the same state later. Interrupts can additionally be made conditional, triggering only when certain state conditions are met.

*Note: Replaying vs Re-Executing:*
Along with HITL, streams allow restarting a workflow. While doing so, if the checkpoint is not updated; the workflow uses the previous execution output of the states and post that step performs execution. This is called *Replaying*. But when the any checkpoint is updated, the updated state is executed again before proceeding to execute other succeeding nodes, it is called as *Re-executing*. The process of updating a checkpoint is called *forking*. 