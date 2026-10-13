id: learning_subagentstop_fires_for_nested_subagents_2026_10_11
type: learning
area: plugin
perspective: the-coder
created: 1791738289.748743
edges: [{"target_id": "../fabrica:domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "related"}]
cue: I am designing a role check or retro check that must hold across subagent spawn levels (a subagent spawning subagents)
---

Observed: SubagentStop fires for nested subagents too. On 2026-10-11 an Explore agent spawned by the-coder produced its own SubagentStop event with agent_type Explore and the same session_id as its parent.
Cause: The harness emits SubagentStop per subagent, regardless of who spawned it. So a hook can check every level directly.
Evidence: observed in a live session (probe transcript not kept); ai_mem/hooks/retro_check.py checks each stop directly. Consequence: the fallback planned for the check (a reviewer_records_consulted field in the-coder's retro) is not needed.
