id: arch_critique_push_vs_pull_synthesis_2026_07_31
type: learning
topic: architecture
created: 1785508020.395156
---

Observed: Two independent devil's-advocate runs (Sonnet, Opus) against ai-mem's push design converged: 'Caps not dumps' limits tokens, not relevance noise; the scoring gate was ineffective (l2/min-max bug); the blind test showed neither a clear pro-push nor a clear pro-pull result.
Cause: Push without measured benefit; the judge saw only the isolated prompt string, not the task.
Evidence: pattern_gap_test_evaluation; arch_decision_push_vs_pull_2026_07_31 (decision made on it).

Status 2026-09-29: The closing recommendation 'PreToolUse remains the only push point' is superseded (arch_decision_pretool_push_removed_2026_09_12, arch_decision_userprompt_push_removed_2026_09_13). The entries named in the text, arch_critique_opus_quantified_costs_2026_07_31, todo_bm25_residual_minmax_flooring and todo_push_vs_pull_architecture_decision, no longer exist (figures: ai-mem/CLAUDE.md Critical Invariants, arch_decision_push_vs_pull_2026_07_31).

# Push-vs-pull architecture critique: synthesis (2026-07-31)

Two independent devil's-advocate runs against ai-mem's push design (Sonnet, which co-built the design; Opus, completely independent, with tool access to the live DB).

## Convergence (both found independently)
- 'Caps not dumps' limits the token count, not relevance noise -- qualitatively by Sonnet, mathematically proven by Opus (see l2/min-max scoring bug, fixed in commit 11eace0).
- The `access_count >= 3` requirement in the [always-present] gate contradicts the project's own `pattern_confidence_lifecycle` rule ('confidence, not retrieval frequency'). Opus quantifies: the access-count filter excludes only ~9% in `global` -- almost ineffective -- AND is incremented by the query process itself (self-reinforcing loop).
- Every fix in this session structurally added more push, never less (e.g. the [always-present: global] extension).
- The per-prompt query has no access to conversation history/the active task, only the raw current prompt string -- a structural weakness that no threshold tuning can fix.
- The reassurance question: does push partly serve the feeling of continuity rather than actual agent performance? Both arrived at it independently.
- Both end up at a hybrid model, not 'delete everything': PreToolUse (action-triggered) remains the only defensible push point; `mem_query` as pull already exists.

## Where Opus went clearly further (with proof, not just argument)
- Found the l2/min-max scoring bug mathematically proven (not merely suspected) -- the core of the bug fixed today (commit 11eace0).
- Found the completely dead PreToolUse hook (broken import) -- discovered independently, fixed in commit baa09db.
- Quantified the 'never measured benefit' criticism with a quote from `pattern_gap_test_evaluation` (blind test demanded since May, never run -- subsequently made up in this session, see `pattern_gap_test_evaluation`).
- Session cost simulation (30 turns, real numbers): see `arch_critique_opus_quantified_costs_2026_07_31` for details.
- More radical final recommendation: delete the `userprompt_hook` injection completely, subject to a blind test. Sonnet was more restrained (leave the question open instead of recommending a concrete deletion).

## What the blind test (see pattern_gap_test_evaluation) actually showed
Neither a clear pro-push nor a clear pro-pull result: a very thorough blind agent could reconstruct accurate, well-evidenced answers about LATER design refinements from code+docs+git, but the ORIGINAL, non-derived design motivation (only in ai-mem) remained unreachable -- without any signal of incompleteness. This supports 'ai-mem preserves deeper motivation that would otherwise be lost' more than 'push/pull is better per se'.

## Recommendation (Sonnet, after synthesis)
Neither 'rebuild everything now' nor 'ignore it, it's partly fixed now'. The BM25 residual bug (see todo_bm25_residual_minmax_flooring) is worth fixing independently of the architecture decision, because it also affects the pull path (`mem_query` via server.py, which also uses BM25MemoryRepository) -- verified: server.py ALWAYS wraps _repo with BM25MemoryRepository when rank_bm25 is installed, regardless of hook vs. MCP tool. ADSR/confidence decay (see todo_confidence_decay_adsr_design), by contrast, is architecture-dependent (depends on the future of the [always-present] gate) -- worth designing only AFTER the architecture decision, otherwise risk of wasted work.

See also: arch_critique_opus_quantified_costs_2026_07_31, arch_redesign_sketch_pull_based_2026_07_31, pattern_injection_caps_not_dumps, pattern_confidence_lifecycle, pattern_gap_test_evaluation, todo_push_vs_pull_architecture_decision.
