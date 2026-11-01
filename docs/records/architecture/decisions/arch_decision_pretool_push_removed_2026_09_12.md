id: arch_decision_pretool_push_removed_2026_09_12
type: domain
topic: architecture
created: 1789228434.240356
edges: [{"target_id": "arch_decision_push_vs_pull_2026_07_31", "edge_type": "related"}, {"target_id": "learning_pretool_push_dominated_context_footprint_2026_09_12", "edge_type": "derived_from"}, {"target_id": "arch_redesign_sketch_pull_based_2026_07_31", "edge_type": "related"}, {"target_id": "domain_no_hardcoded_keyword_pretool_hook_recall_moment_open_2026_10_23", "edge_type": "related"}]
cue: Someone proposes that ai-mem inject something again before file edits (PreToolUse)
---

# PreToolUse push removed: return to pure pull for Edit/Write (2026-09-12)

Decision: pretool_hook.py is no longer registered in install.py (PreToolUse entry for ai_mem.pretool_hook removed, uninstall.py continues to clean it up on legacy installations). install.py additionally removes the entry self-healingly on every re-run on existing installations (see _remove_hook_command). The only remaining automatic push point is therefore SessionStart (session level, cheap) -- no more push per Edit/Write.

## Trigger
Measurement of a doctor scan (348 Edit/Write calls ~ 67.6k tokens, ~92% of ai-mem's total context footprint): see learning_pretool_push_dominated_context_footprint_2026_09_12.

## Tension with the earlier decision -- explicitly resolved, not overlooked
arch_decision_push_vs_pull_2026_07_31 (item 5) had deliberately kept PreToolUse as the 'only defensible push point' -- rationale: the trigger is a concrete action (file X is being edited), not a vague prompt string as with userprompt_hook. This rationale has not been refuted, but the new measurement is genuinely new evidence. User decision (2026-09-12, after a follow-up question including the alternatives 'shrink instead of remove' and 'measure first'): full switch to pull, explicitly on the condition 'installable and updatable' -- i.e. via install.py/uninstall.py, not by hand-editing settings.json.

## Replacement: explicit pull instead of automatic push
- chunk-plan.md (~/.claude/commands/chunk-plan.md): new section 'Memory (ai-mem)' before the Architecture-Awareness section -- an explicit `mem_query(collection="repo.<project>", query="<task>")` before decomposition.
- the-coder.md (~/.claude/agents/the-coder.md): NO change needed -- it already had an explicit `mem_query(collection="subagent.the-coder", ...)` step at session start (lines 41-49) plus a mem_add write path (lines 156-167). A proposal from a parallel session in another project for a new `agents.the-coder` collection was REJECTED -- `subagent.the-coder` is the established naming convention, already consolidated by mem-dream --expert; a parallel collection would only have fragmented it.

## What stays unchanged
SessionStart continues to inject repo.<project> [available] entries + current_focus for inject_agents (the-coder included) -- project context is not lost, it just arrives per session instead of per edit. PostToolUse/UserPromptSubmit unchanged.

Addendum 2026-09-29: This section is overtaken by arch_decision_sessionstart_pull_based_2026_09_16 -- SessionStart by default no longer injects any memory content (only a routing hint; current_focus and [available] only with session_start_verbose), and inject_agents no longer implies injection. UserPromptSubmit was also retired on 2026-09-13 (arch_decision_userprompt_push_removed_2026_09_13).

See also: arch_decision_push_vs_pull_2026_07_31, arch_critique_opus_quantified_costs_2026_07_31, hook_system, pattern_injection_caps_not_dumps.

Addendum 2026-10-04: Only the 'What stays unchanged' section is overtaken (PostToolUse retired, experience index removed); the decision itself -- no push before edits -- stands.
