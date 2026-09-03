---
name: hi-events
description: Read and process messages addressed to the current Hirey Hi Agent through workspace_workflows. Use when the user asks whether anybody replied, what came in, or wants the Agent inbox drained.
---

# Hi Agent messages

Use the same `workspace_workflows` tool as every other Hi capability. Do not look for separate
`hi_agent_events_*` tools.

1. Call `workspace_workflows` with `action: agent_message.claim` and a payload containing a stable
   `idempotency_key` plus the supported lease arguments from `action: catalog`.
2. If no message is returned, say there is nothing new and stop.
3. Interpret only the exact claimed message data returned by Core. Show the human-relevant content
   to the user before acknowledging it.
4. Call `action: agent_message.complete` with the exact lease identifiers returned by the claim, a
   stable `idempotency_key`, and the Agent reply when one is required.
5. If processing fails, call `action: agent_message.fail` with the exact lease identifiers and a
   bounded reason so Core can release or dead-letter it according to the current contract.

Claims are leases and delivery is at least once. Never complete unseen content, invent a message,
or reuse identifiers from another session.
