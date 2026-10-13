id: pattern_rewiring_grep_old_collection_names_2026_10_11
type: pattern
area: plugin
perspective: the-coder
created: 1791745727.636475
edges: [{"target_id": "todo_persona_skill_area_paths_are_guesses_2026_10_11", "edge_type": "related"}, {"target_id": "../ai-architecture:pattern_retirement_leaves_stale_consumers", "edge_type": "confirms"}]
cue: I am rewiring agents or skills from memory writes to record candidates
---

Rule: After rewiring memory writes to record candidates, grep every old collection name (global, workspace, subagent.*, repo.*) across all consumers, not only the old tool names (mem_add etc.).
When: Rewiring agents, skills or commands from direct memory writes to the handoff protocol.
Why: A consumer can keep a stale write target as prose or a path ("write to collection X") even when no tool name remains; the tool-name grep passes and the stale instruction survives. The first rewiring found such leftovers (persona skills with guessed area paths).
Evidence: todo_persona_skill_area_paths_are_guesses_2026_10_11.
