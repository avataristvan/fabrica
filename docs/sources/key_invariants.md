---
type: retired-system
date: 2026-10-04
origin: memory entry key_invariants (the ChromaDB-era invariants list), exported to docs/reference/ on 2026-10-04
status: processed
---

## What the source says

ai-mem Key Invariants and Gotchas:

1. cosine_similarity = 1 - (ChromaDB distance / 2). Collections use l2 (squared-L2) space, not cosine space -- verified live via col.configuration_json. For normalized embeddings, squared-L2 dist = 2 - 2*cos_sim, so cos_sim = 1 - dist/2. The old '1 - dist' formula was wrong (fixed 2026-07-31) and combined with BM25's min-max normalization made CONTEXT_MIN_SCORE etc. structurally unable to reject a top hit.
2. The hybrid repository used by the server (BM25MemoryRepository) over-fetches 50 candidates (_BM25_FETCH=50) from ChromaDB, fuses cosine with a saturated BM25 score, then slices to n_results. Plain ChromaMemoryRepository returns ChromaDB's native cosine order. QueryMemoryUseCase itself adds no re-ranking.
3. mem_delete with no ids drops the entire collection; repo signals this by returning -1.
4. current_focus (id "current_focus") is the primary context entry per collection.
5. [available] gate (renamed 2026-07-31 from [always-present]): boost_count >= 1 (history: until 2026-09-26 it also required confidence > 0.9 AND access_count >= 3, dropped in favor of evidence edges -- see domain_drop_confidence_for_evidence_and_librarian_2026_09_26). Entries without an explicit /reflect boost never qualify. Runs unconditionally against GLOBAL_COLLECTION too (separate, smaller cap) -- see [available: global] in hook.py. Both gate blocks render id+title only (mem_get for full body), not a text dump, and render only under session_start_verbose: true in agents.yaml (SessionStart is pull-based by default since 2026-09-16, arch_decision_sessionstart_pull_based_2026_09_16).
6. confidence and access_count are no longer written or read (dropped 2026-09-26, commit b5e5d38). mem_boost is now purely a /reflect citation: it increments boost_count and, optionally, sets the entry's experience-index cue -- no delta, no confidence math. Legacy confidence/access_count values from before the drop stay in stored metadata untouched, never migrated away, and play no role in gating, ranking, or dream.
7. last_accessed_at means deliberate use (an explicit min_score_for_tracking query, a mem_get by id, or a mem_boost) -- not passive query surfacing; a plain mem_query with no threshold tracks nothing. (History: access_count meant the same thing from 2026-07-31, chunk 3, commit be41add, until it was dropped entirely 2026-09-26.)

Note: Items previously referencing ML ranker (TrainRankerUseCase, RankerRegistry, RankerScope, TrainingExample, mem_train, hybrid scope keys) are removed -- ranker fully deleted in 2026-06 (commit a7110da). Items about _try_seed / repo_seeder.py section splitting were dropped 2026-09-20: the seeder module no longer exists (see automation_repo_seeder).

Status 2026-10-04: The items on cosine/BM25, the -1 whole-collection delete, [available] and the access counters apply only to the Chroma rollback backend (see docs/reference/chroma_rollback_backend.md). Current invariants: the Gotchas section of ai-mem's CLAUDE.md.

## Our notes

