id: domain_librarian_at_review_handoff_2026_10_10
type: domain
area: retrieval
created: 1791588269.857843
edges: [{"target_id": "domain_user_records_as_role_perspective_2026_10_04", "edge_type": "related"}, {"target_id": "domain_librarian_replaces_experience_index_2026_10_04", "edge_type": "related"}, {"target_id": "domain_review_is_skill_with_anchor_lint_agent_2026_10_12", "edge_type": "related"}, {"target_id": "eval_pull_gap_test_2026_09_20", "edge_type": "derived_from"}, {"target_id": "learning_pull_needs_situation_triggers_2026_10_04", "edge_type": "derived_from"}, {"target_id": "../..:domain_dev_team_stops_on_contradiction_blocked_2026_10_19", "edge_type": "related"}]
---

Decision: The librarian is firmly integrated at handoff points of the dev team instead of being called situationally by agents. In /dev-team the reviewer asks it at the code → review handoff with the changed paths against decisions/learnings (in addition to /chunk-plan as the preventive point). The reviewer also reports record_candidates; the reflect gate takes them as the first source for new records, ahead of the coder's learned:.
Why: An agent has no cheap recognition ('I know this') and only asks when an id is already in the context (eval_pull_gap_test_2026_09_20). The ranker and autoinject fired without reference to the situation. At handoffs the context is fresh and concrete (at review: a diff), so the role fixes the situation instead of a hunch. The reviewer has distance from the implementation and can better judge what a record is worth.
Scope: ~/.claude/commands/dev-team.md (reviewer template, [retro] block, reflect gate). Measure: records_consulted. If it stays 'none' over many chunks, the step is ritual and must be reviewed. Open: whether a reviewer spawn can still start an agent (third level); as a fallback the coder asks before the reviewer spawn.
