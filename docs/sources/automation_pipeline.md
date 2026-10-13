---
type: retired-system
date: 2026-10-04
origin: memory entry automation_pipeline, exported to docs/reference/ on 2026-10-04 (content older)
status: processed
---

## What the source says

ai-mem Automation Pipeline — threshold-driven: each active subsystem fires once its own fixed threshold is crossed, with no judgment step in the firing path itself (a description of the current mechanism, not a design ideal — see domain_direction_judgment_over_scores_2026_09_20 for why judgment-over-scores is the current direction elsewhere in ai-mem).

Two active subsystems, two retired:
1. automation_memory_demotion — MEMORY.md auto-demotion (memory_index.py, 180→160 line threshold; currently undeployed, no trigger wired)
2. automation_session_stats — Session injection tracking (session_stats.py, 20-entry rolling window)
3. automation_repo_seeder — RETIRED, see that entry (was: CLAUDE.md seeding, repo_seeder.py, injection_rate ≥ 0.60 gate; module removed from the codebase, replaced by /mem-init's agent-driven exploration)
4. automation_userprompt_injection — RETIRED 2026-09-13 (was: UserPromptSubmit context injection, three independent paths) -- see arch_decision_userprompt_push_removed_2026_09_13

Common invariant (for the two still-active subsystems): each fires independently on its own threshold — no manual trigger needed.

Status 2026-10-04: The threshold-driven subsystems described here (session_stats gate, cleanup by access) are dormant or no-ops on the record-file backend (see docs/reference/chroma_rollback_backend.md).

## Our notes

