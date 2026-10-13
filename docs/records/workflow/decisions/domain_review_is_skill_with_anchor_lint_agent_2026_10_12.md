id: domain_review_is_skill_with_anchor_lint_agent_2026_10_12
type: domain
area: workflow
perspective: user
created: 1791788120.855459
edges: [{"target_id": "domain_chunk_plan_carries_all_boundary_anchors_2026_10_12", "edge_type": "derived_from"}, {"target_id": "domain_librarian_at_review_handoff_2026_10_10", "edge_type": "related"}, {"target_id": "domain_agents_learn_environment_never_edit_external_2026_10_11", "edge_type": "related"}]
cue: I am designing or changing how a chunk review checks the coder against its decisions and todos
---

Decision: The reviewer checks every anchor the coder had. Review is a skill, not one agent: it spawns the standard code reviewer unchanged and, in parallel, an own `anchor-lint` agent for the linting part (one verdict per anchor: held / violated / not applicable; anchor list copied verbatim from the chunk entry). The caller passes the what; skill and agent fix the how.
Why: The standard reviewer keeps its job and format (external agents are never edited, no foreign output format). Distance: the coder never judges the anchors itself. Spawn depth stays 2 because the caller asks the librarian first (a third-level spawn is unverified).
Scope: review step of /dev-team, the `anchor-lint` agent (agents/anchor-lint.md). Goes live once todo_user_record_review_values gives it a user yardstick.
