type: pattern
topic: plugin
perspective: the-coder
created: 1791745727.636475
cue: I am rewiring agents or skills from memory writes to record candidates
---

Rule: After rewiring memory writes to record candidates, grep every old collection name (global, workspace, subagent.*, repo.*) across all consumers, not only the old tool names (mem_add etc.).
When: Rewiring agents, skills or commands from direct memory writes to the handoff protocol.
Why: A consumer can keep a stale write target as prose or a path ("write to collection X") even when no tool name remains; the tool-name grep passes and the stale instruction survives. The first rewiring found exactly this: a rewired consumer kept an old collection name as a prose write target.
Evidence: the first rewiring pass (chunk 4a); the mechanism above.

## Edges

- confirms: [pattern_retirement_leaves_stale_consumers](../../../../../docs/records/general/decisions/pattern_retirement_leaves_stale_consumers.md)
