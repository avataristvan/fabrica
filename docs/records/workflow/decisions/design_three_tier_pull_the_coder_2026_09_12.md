id: design_three_tier_pull_the_coder_2026_09_12
type: domain
area: workflow
created: 1789229274.183399
edges: [{"target_id": "arch_decision_pretool_push_removed_2026_09_12", "edge_type": "related"}, {"target_id": "learning_gap_test_first_run_and_blindtest_2026_07_31", "edge_type": "derived_from"}]
---

Status addendum (2026-09-29): The premise of the global tier ('SessionStart's [available: global] block covers the case', decision 3) is broken -- SessionStart has been pull-based since 2026-09-16 (arch_decision_sessionstart_pull_based_2026_09_16; [available] only with session_start_verbose), and subagents receive no SessionStart output anyway. Resolved 2026-09-29: ~/.claude/agents/the-coder.md now queries global explicitly (tier 3, n_results=2).

# Three-tier pull for the-coder: agent / project / global (2026-09-12)

Follow-up question to the PreToolUse push removal (see arch_decision_pretool_push_removed_2026_09_12): how do agents (specifically the-coder, both as implementer and as chunk-plan tech-lead reviewer) deliberately use all three ai-mem tiers -- subagent.the-coder (agent), repo.<project> (project), global?

## Inventory before the change
- Agent tier: the-coder.md already had an explicit `mem_query(collection="subagent.the-coder", ...)` step at session start.
- Project tier: NO explicit query -- only SessionStart's automatic `[available]` block (fixed, high-confidence-gated cap, not task-scoped).
- Global tier: NO explicit query -- only SessionStart's `[available: global]` block (same characteristics).

## Decision
1. **The project tier gets an explicit pull** -- added in the "Session Start" section of the-coder.md, against the active collection announced by SessionStart ("Active collection: repo.<project>"), not against a guessed name. Applies identically to BOTH roles (implementer and tech-lead reviewer) -- no separate query template per role needed, because `<task summary>` differs naturally within the same template (chunk scope vs. "review this plan").
2. **The reviewer case is the real driver**: chunk-plan's tech-lead review explicitly spawns the-coder with "you have not seen the planning process -- read it cold" (see chunk-plan.md, section "Tech-Lead Review"). That is exactly the blind-test scenario from arch_decision_push_vs_pull_2026_07_31: a purely pull-less/blind agent reconstructs later refinements well from text/code, but completely misses the original, non-derivable design motivation, without any signal of incompleteness. That is why the-coder.md explicitly says: do NOT skip the project pull just because there is no code to read yet.
3. **The global tier deliberately gets NO explicit query** -- rationale: SessionStart's `[available: global]` block covers exactly the case global is meant for (curated, high-confidence, few entries); a task-scoped query would probably hit the same small pool again -- cost without real added benefit. This adheres to pattern_injection_caps_not_dumps AND to the basic idea of the push removal just completed (do not introduce new unconditional queries per call through the back door).

## Why ONE shared section in the-coder.md instead of separate templates in chunk-plan.md
Both roles run through the same `subagent_type="the-coder"` spawn -- a change to the-coder.md itself automatically reaches both call sites (implementer spawn in chunk-plan.md AND tech-lead review spawn), without duplicating the query logic in chunk-plan.md. chunk-plan.md already got its OWN project pull in the previous change -- that one is for the PLANNER (general prose agent, not the-coder), not for the tech-lead reviewer (who IS the-coder).

## Not touched
pr-review-toolkit:code-reviewer (the code-level review-loop reviewer that every the-coder calls internally against its own diff -- see dev-team.md) is not in INJECT_CONTEXT_AGENTS and still gets no ai-mem context -- it was not part of this question, but was checked as a consistency check and deliberately left unchanged.

See also: arch_decision_pretool_push_removed_2026_09_12, arch_decision_push_vs_pull_2026_07_31, hook_routing_subagent, pattern_injection_caps_not_dumps, dream_hint_the_coder.

Evidence: docs/sources/dream_hint_the_coder.md
