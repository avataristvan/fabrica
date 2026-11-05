type: domain
topic: architecture
perspective: user
created: 1791788132.948062
cue: I am deciding which plugin an agent, skill or command belongs in, ai-mem or a team plugin
---

Decision: ai-mem ships only the record-facing parts (`ai-mem:anchor-lint`, librarian, archivist, handoff-protocol, reflect) and names no team. A team plugin depends on ai-mem, never the reverse.
Why: Plugin namespaces make the split readable; ai-mem stays a generic core that names no team ([pattern_generic_core_selective_agent_activation](pattern_generic_core_selective_agent_activation.md)).
Scope: packaging of ai-mem's own plugin. How a team plugin is packaged is knowledge of the user's environment and lives outside ai-mem.

## Edges

- derived_from: [domain_review_is_skill_with_anchor_lint_agent_2026_10_12](../../workflow/decisions/domain_review_is_skill_with_anchor_lint_agent_2026_10_12.md)
- related: [pattern_generic_core_selective_agent_activation](pattern_generic_core_selective_agent_activation.md)
- related: [domain_dev_team_requires_fabrica_no_reduced_team_2026_11_01](../../../../../docs/records/workflow/decisions/domain_dev_team_requires_fabrica_no_reduced_team_2026_11_01.md)
