id: domain_dev_team_own_plugin_ai_mem_ships_record_parts_2026_10_12
type: domain
area: architecture
perspective: user
created: 1791788132.948062
edges: [{"target_id": "domain_review_is_skill_with_anchor_lint_agent_2026_10_12", "edge_type": "derived_from"}, {"target_id": "pattern_generic_core_selective_agent_activation", "edge_type": "related"}, {"target_id": "../ai-architecture:todo_build_dev_team_plugin_after_chunk_6a_2026_10_12", "edge_type": "related"}]
cue: I am deciding which plugin a dev-team agent, skill or command belongs in
---

Decision: dev-team becomes its own plugin (home ~/workspace/ai-architecture) with dev-team, chunk-plan, the-coder and `dev-team:review`. ai-mem ships only the record-facing parts (`ai-mem:anchor-lint`, librarian, archivist, handoff-protocol, reflect). dev-team depends on ai-mem, never the reverse. Interim: `dev-team-review` as a global user skill under ~/.claude/skills/; the plugin packaging repoints it to `ai-mem:anchor-lint`.
Why: Plugin namespaces make the split readable; ai-mem stays a generic core that names no team (pattern_generic_core_selective_agent_activation).
Scope: plugin packaging; the plugin's non-goal "general decorator mechanism" (points to ai-architecture). Interim name rests on an unverified assumption, see todo_verify_local_skills_can_have_namespace_2026_10_12.
