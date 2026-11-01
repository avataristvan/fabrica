id: domain_dev_team_own_plugin_ai_mem_ships_record_parts_2026_10_12
type: domain
topic: architecture
perspective: user
created: 1791788132.948062
edges: [{"target_id": "domain_review_is_skill_with_anchor_lint_agent_2026_10_12", "edge_type": "derived_from"}, {"target_id": "pattern_generic_core_selective_agent_activation", "edge_type": "related"}, {"target_id": "..:todo_build_dev_team_plugin_after_chunk_6a_2026_10_12", "edge_type": "related"}]
cue: I am deciding which plugin an agent, skill or command belongs in, ai-mem or a team plugin
---

Decision: ai-mem ships only the record-facing parts (`ai-mem:anchor-lint`, librarian, archivist, handoff-protocol, reflect) and names no team. A team plugin depends on ai-mem, never the reverse.
Why: Plugin namespaces make the split readable; ai-mem stays a generic core that names no team (pattern_generic_core_selective_agent_activation).
Scope: packaging of ai-mem's own plugin. How a team plugin is packaged is knowledge of the user's environment and lives outside ai-mem.
