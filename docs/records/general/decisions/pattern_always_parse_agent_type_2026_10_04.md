id: pattern_always_parse_agent_type_2026_10_04
type: pattern
topic: general
perspective: agent
created: 1791067532.967105
---

Rule: SessionStart must parse the transcript to detect agent type; never trust inherited AI_MEM_AGENT_TYPE.
When: Initializing a hook in SessionStart, especially in subagent contexts.
Why: Inherited AI_MEM_AGENT_TYPE is the parent's type, not the child's. The transcript (first ~4KB is enough) is the canonical source for determining the current session's agent type.