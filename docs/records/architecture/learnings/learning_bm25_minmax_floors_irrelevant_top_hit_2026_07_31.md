id: learning_bm25_minmax_floors_irrelevant_top_hit_2026_07_31
type: learning
area: architecture
created: 1790678547.683646
---

Observed: Empirically against the live DB (the production ai-mem store, global + repo.ai-mem, 20 query x collection pairs, 5 relevant + 5 irrelevant queries): the top BM25 candidate in the pool was mapped to exactly 1.0 under the old _normalize() in 20/20 cases, including 6 cases with raw BM25 of 0.000 (no real term overlap). At alpha=0.5, the floor of the fused score for irrelevant top hits was 0.584 vs. 0.591 for relevant ones -- a gap of 0.007, matching the documented noise ceiling (~0.60) of userprompt_hook.py.
Second finding (in code review before the merge): rank_bm25's BM25Okapi CAN return negative raw scores (floor of negative IDFs at 0.25*average_idf, itself negative for small/near-duplicate corpora -- exactly the shape of ai-mem's collections). raw/(raw+k) is not monotonic across the pole at raw=-k: the reviewer reproduced raw scores -5.05/-4.83 that saturated to 1.66/1.71 (ABOVE 1.0, full rank inversion with a realistic 2-entry pool); raw==-2.0 exactly triggered an uncaught ZeroDivisionError.
Cause: BM25's min-max normalisation always mapped the best candidate in the pool to 1.0, regardless of absolute relevance (pool-relative rescaling); the saturation formula raw/(raw+k) is safe only for non-negative raw values.
Evidence: Measurement on the live DB (20 pairs); the reviewer's reproduction; tests test_weak_pool_bm25_not_saturated_to_one, test_saturate_clamps_negative_raw_scores. Related: userprompt_hook_threshold_recalibration_2026_07_31.
