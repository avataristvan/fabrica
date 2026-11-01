id: domain_review_is_skill_with_anchor_lint_agent_2026_10_12
type: domain
topic: workflow
perspective: user
created: 1791788120.855459
edges: [{"target_id": "domain_librarian_at_review_handoff_2026_10_10", "edge_type": "related"}, {"target_id": "domain_agents_learn_environment_never_edit_external_2026_10_11", "edge_type": "related"}]
cue: I am designing or changing how the anchor-lint agent checks a coder against its decisions and todos
---

Decision: ai-mem ships `anchor-lint`, an own agent for the linting part of a review: one verdict per anchor (held / violated / not applicable), the anchor list copied verbatim from the caller's chunk entry. The caller passes the what; the agent fixes the how. It runs beside the standard code reviewer, which stays unchanged.
Why: The standard reviewer keeps its job and format (external agents are never edited, no foreign output format). Distance: the coder never judges the anchors itself.
Scope: the `anchor-lint` agent (agents/anchor-lint.md). It goes live once a user record gives it a yardstick for what counts as a good review. How a team's review step uses it is knowledge of the user's environment and lives outside ai-mem.
