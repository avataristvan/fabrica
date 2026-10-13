id: decision_hybrid_fusion_cosine_saturated_bm25_2026_10_04
type: domain
area: general
created: 1791067532.967105
superseded_by: domain_file_backend_replaces_chroma_2026_10_04
valid_until: 1791139067.668012
---

Decision: BM25 hybrid score = alpha x cosine_raw + (1-alpha) x bm25_sat, with cosine_raw true cosine similarity (no min-max) and BM25 raw passed through _saturate() (raw/(raw+k), k=2.0, clamped non-negative); alpha=0.5 default, configurable in constructor
Why: fusion formula was corrected 2026-07-31 (replacing min-max normalization); derivation of k=2.0 and the non-negativity clamp is in bm25_saturating_transform_2026_07_31
Scope: ai_mem/infrastructure/bm25_repository.py