id: domain_chunk_plan_carries_all_boundary_anchors_2026_10_12
type: domain
area: workflow
perspective: user
created: 1791788120.578081
edges: [{"target_id": "arch_decision_pretool_push_removed_2026_09_12", "edge_type": "related"}, {"target_id": "../fabrica:domain_why_travels_with_chunk_spec_2026_10_10", "edge_type": "related"}, {"target_id": "learning_large_chunk_plan_held_over_one_weekend_2026_10_12", "edge_type": "related"}]
cue: I am writing a chunk-plan entry and listing which decisions or todos the coder must respect
---

Decision: Chunk-plan entries carry every anchor that draws a boundary for the chunk (decisions, restricting todos, patterns that apply while working), gathered from the librarian at planning time. At agent level records act like a linter: deterministic, fire on a concrete violation, never push content.
Why: An agent in a fresh session is blind; everything happens for the first time. In one chunk the plan's "Decisions:" line missed the anchors that actually guided the coder; only the orchestrator's librarian call supplied them. This is distinct from the retired content push (arch_decision_pretool_push_removed_2026_09_12): the anchors travel in the plan, nothing is injected at tool time.
Scope: /chunk-plan (spec lists all anchors, not only decisions), the-coder chunk start, and the anchor list the reviewer checks (domain_review_is_skill_with_anchor_lint_agent_2026_10_12). Extends ../fabrica:domain_why_travels_with_chunk_spec_2026_10_10 from decisions to all anchors.
