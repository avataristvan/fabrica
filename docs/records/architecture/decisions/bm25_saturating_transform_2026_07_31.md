id: bm25_saturating_transform_2026_07_31
type: domain
area: architecture
created: 1789246260.895704
edges: [{"target_id": "learning_bm25_minmax_floors_irrelevant_top_hit_2026_07_31", "edge_type": "derived_from"}]
cue: Changing or reviving score fusion of cosine and BM25 in the Chroma rollback backend
---


# BM25 residual min-max flooring: decision & final shipped state (2026-07-31)

## Decision
Chosen: a saturating transform, the same fix pattern as on the cosine side (commit 11eace0) -- an absolute, pool-independent transformation instead of pool-relative rescaling. Examined and rejected: RRF (rank-based, structurally incompatible with userprompt_hook.py's fixed absolute threshold gate), theoretical max BM25 (BM25Okapi is instantiated fresh per query over only the 50 fetched candidates -- no persistent corpus-wide IDF index against which a max could be computed), z-score/CombSUM/MNZ (the same pool-dependence flaw as min-max, or literally the existing broken pattern). k=2.0 chosen from the live-DB median of the non-zero raw BM25 (~1.6): a typical weak hit saturates at ~0.44, strong exact-phrase hits at 0.75-0.83 (k=1 too permissive: random hits reach 0.82-0.84; k=5 compresses strong hits to ~0.66).

## What shipped
bm25_repository.py's _normalize() (min-max) was deleted and replaced by:
```
_BM25_SATURATION_K = 2.0
def _saturate(scores):
    return [max(s, 0.0) / (max(s, 0.0) + _BM25_SATURATION_K) for s in scores]
```
Fusion formula unchanged: hybrid = alpha*cosine_raw + (1-alpha)*bm25_sat, only the computation of bm25_norm changed. Pole fix: clamp to max(s, 0.0) before the division (rationale and reproduction: learning_bm25_minmax_floors_irrelevant_top_hit_2026_07_31).

**Rule (generalised beyond BM25):** a saturating transform raw/(raw+k) is safe only for genuinely non-negative raw values -- if the library producing the raw signal can itself return negatives, always clamp before the transform. See pattern_saturating_transform_nonnegativity_precondition (global).

The hybrid-search page (now docs/sources/hybrid-search.md, formerly docs/hybrid-search.md) was rewritten; orphaned TorchMicroRanker pipeline reference removed; a wrongly claimed '[0,1)' output range corrected; a non-existent 'pip install -e ".[ml,hybrid]"' extra reference removed. userprompt_hook.py's CONTEXT_MIN_SCORE rationale comment received a 'STALE as of 2026-07-31' flag (recalibration separately: userprompt_hook_threshold_recalibration_2026_07_31).

Scope today: BM25 is a transparent repository wrapper that the use case never sees; fusion needs a fixed-scale cosine plus a saturating BM25 transform; over-fetch 50, then truncate. All of this describes the Chroma backend, which survives only as the rollback until chunk 7.

Tests: test_weak_pool_bm25_not_saturated_to_one, test_saturate_clamps_negative_raw_scores. Full suite green: 334/334 at the time.

Evidence: docs/sources/hybrid-search.md, docs/sources/bm25_hybrid_impl.md (formerly "bm25_hybrid_impl"; the derivation of k=2.0 and the clamp live above).

See also: arch_critique_push_vs_pull_synthesis_2026_07_31, pattern_saturating_transform_nonnegativity_precondition, userprompt_hook_threshold_recalibration_2026_07_31.
