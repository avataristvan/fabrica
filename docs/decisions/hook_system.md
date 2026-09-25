id: hook_system
type: pattern
created: 1777467870.86774
edges: [{"target_id": "pattern_taxonomy_as_quality_gate", "edge_type": "related"}, {"target_id": "arch_decision_pretool_push_removed_2026_09_12", "edge_type": "related"}, {"target_id": "arch_decision_userprompt_push_removed_2026_09_13", "edge_type": "related"}]
---

ai-mem Hook System (2 hooks active, all silent on failure):
- SessionStart (hook.py): pull-based by default since 2026-09-16 -- prints only a one-line routing hint (active collection, and a registered subagent's own subagent.<name> collection). No memory content pushed: current_focus text, [available] high-confidence listing (confidence > 0.9 AND access_count ≥3 AND boost_count ≥1 -- renamed from [always-present] 2026-07-31, renders id+title only), expired-entry warnings, cross-session entry-count delta, and git commits since last session are all gated behind session_start_verbose: true in agents.yaml (opt-in, restores the old push). No CLAUDE.md seeding -- repo_seeder was removed, /mem-init is the seeding path now (see automation_repo_seeder).
- PostToolUse (posttool_hook.py): updates last_accessed_at and access_count for matched entries, but only when the caller passes min_score_for_tracking (access_count now means deliberate use, not passive surfacing -- see chunk3_access_count_semantics_shipped_2026_07_31). No training signal (ranker removed 2026-06). No output to Claude.

RETIRED -- PreToolUse (2026-07-31 to 2026-09-12) and UserPromptSubmit (project inception to 2026-09-13): both removed from install.py's registration after real cost/noise measurements showed each firing far more than its value justified; both self-heal off existing installations on install.py re-run; module files and tests for both still exist, just unwired. Full rationale for each in their own dedicated entries (see edges on this entry).

Note: stop_hook.py was never actually wired into install.py in this repo -- design notes referenced it but the module doesn't exist; /reflect Step 5 is where current_focus updates happen instead.

Hooks fire selectively by session type since 2026-05-05 -- see hook_routing_subagent for the full routing table. Non-coding subagents (Explore, Plan, reviewers) receive no context injection to conserve tokens.