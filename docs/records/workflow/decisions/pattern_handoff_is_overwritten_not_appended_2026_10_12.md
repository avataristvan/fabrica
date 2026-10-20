id: pattern_handoff_is_overwritten_not_appended_2026_10_12
type: pattern
area: workflow
perspective: agent
created: 1791821372.671895
edges: [{"target_id": "domain_handoff_points_instead_of_copying_2026_10_19", "edge_type": "related"}]
cue: I am updating a docs/handoff file at the end of a session
---

Rule: Overwrite the handoff with the current state each time; never only append.
When: Writing or updating docs/handoff-<date>.md.
Why: An append-only handoff rots: the 2026-10-10 handoff grew to 40 KB and predicted that doctor would report plugin hooks as missing, already outdated when read. History lives in git and records.
