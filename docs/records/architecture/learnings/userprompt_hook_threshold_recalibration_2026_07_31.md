id: userprompt_hook_threshold_recalibration_2026_07_31
type: learning
topic: architecture
created: 1785504672.145765
---

Observed: Off-topic prompts reached 0.45-0.60 as top hits against global/repo.ai-mem; relevant queries 0.58 to 0.71-0.78.
Cause: BM25 min-max always gave the best of the pool bm25_norm 1.0 (residual bug, later fixed in bm25_saturating_transform).
Evidence: Commit 11eace0; live-DB measurement.

Fix (2026-07-31, commit 11eace0, part of the cosine/BM25 scoring-fix work; the access_count semantics change is a separate step, see chunk3_access_count_semantics_shipped_2026_07_31): Recalibrated userprompt_hook.py thresholds after the scoring fixes, measured empirically against the live DB via _build_query_uc(with_bm25=True). CONTEXT_MIN_SCORE 0.3→0.62, ANTIPATTERN_MIN_SCORE/DILEMMA_MIN_SCORE 0.4→0.58. Key finding: even after the cosine fix, off-topic prompts ('weather in Paris', 'pizza dough hydration', 'quantum entanglement') still scored 0.45-0.60 as top hits against `global` and `repo.ai-mem` -- because BM25MemoryRepository's min-max normalization (bm25_repository.py::_normalize) still gives the best-in-pool BM25 candidate a bm25_norm of 1.0 regardless of absolute relevance, so hybrid = alpha*cosine + (1-alpha)*1.0 puts an artificial floor under even irrelevant top hits. This is a distinct, un-fixed residual of the same 'min-max always inflates the top hit' bug pattern that was fixed for cosine -- just one layer up, in BM25's half of the fusion -- and was out of scope here (bm25_repository.py untouched; later fixed in bm25_saturating_transform_2026_07_31). Relevant-query floor measured at ~0.58 (noisy multi-project `global`) to ~0.71-0.78 (`repo.ai-mem`). New thresholds set just above the measured irrelevant ceiling per collection type (context: 0.62 vs ~0.60 ceiling; antipattern/dilemma type-filtered pool: 0.58 vs ~0.555 ceiling), erring toward precision over recall. No dilemma entries exist in any collection currently, so DILEMMA_MIN_SCORE was set by structural analogy to ANTIPATTERN_MIN_SCORE, not direct measurement. Added 2 regression tests in tests/test_userprompt_hook.py using these measured values as mocked scores.

Retired 2026-09-13: userprompt_hook.py itself was fully unwired (arch_decision_userprompt_push_removed_2026_09_13) -- these threshold values no longer execute anywhere. Kept as the historical record of the BM25 residual-flooring bug's discovery.
