Agent Memory is a key concept in agentic solution development. Handling memory in the right technique based upon the approach matters; this would avoid memory overload. Memory is primarily classified as short-term and long-term.

## Short term memory
The memory of current session or conversation is called as short term memory. This often consists of thread memory, checkpoint memory. 

## Long term memory
A collective information of multiple sessions or data from different sources and databases. These are further classified as:
1. **Episodic Memory**: This type remembers specific events from the past like a user’s date of birth that was used during an earlier conversation. The agent can use this memory as context in future interactions.
2. **Semantic Memory**: This holds general knowledge about the world or things the AI has learned through past interactions. The agent can refer to this information to handle new problems effectively.
3. **Procedural Memory**: Here the agent stores “how-to” steps or rules for making decisions. For example, it might remember the process for solving a math problem and use the same steps when tackling a similar task later.

*Note: When memory sizes increases and overloads it becomes necessary to filter, trim or compress the information.* 

## Memory Management Techniques
1. **Sliding Window** — retain only the most recent _N_ tokens or turns, dropping the oldest messages once the context limit is approached.
2. **Summarization** — periodically compress older conversation turns into a rolling summary, preserving key facts while freeing up context space.
3. **Retrieval-Augmented Generation (RAG)** — instead of loading entire memory stores into context, retrieve only the most relevant chunks at query time using semantic or keyword search.
4. **Memory Tiering** — classify memory by access frequency and importance; keep hot/recent data in-context, push cold/older data to external stores (vector DB, key-value store).
5. **TTL / Forgetting Policies** — assign expiry durations to episodic entries so stale or low-value memories are automatically purged over time.
6. **Importance-based Filtering** — score and rank memories by relevance or recency before writing or retrieving, discarding low-signal entries proactively.