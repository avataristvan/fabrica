---
type: retired-system
date: 2026-07-31
origin: memory entry bm25_hybrid_impl, exported to docs/reference/ on 2026-10-04
status: processed
---
> Translated from the German original on 2026-10-13; content unchanged.

## What the source says

BM25 hybrid search — implemented 2026-04-29, fusion formula corrected 2026-07-31, BM25 residual bug fixed 2026-07-31 (later the same day)

File: ai_mem/infrastructure/bm25_repository.py
- BM25MemoryRepository wraps any MemoryRepository-compatible object
- _BM25_FETCH=50: internally fetches 50 candidates instead of the n_results the caller wants
- Score-Fusion: hybrid = alpha × cosine_raw + (1-alpha) × bm25_sat -- cosine is true cosine similarity (chroma_repository.py fix), no min-max any more. BM25's raw value passes through _saturate() (raw/(raw+k), k=2.0, non-negativity-clamped) instead of a min-max normalisation.
- alpha=0.5 default, configurable in the constructor
- All other MemoryRepository methods delegate 1:1 to inner
- Transparent to the application layer: QueryResult.score contains the fused score, used directly for sorting (no further re-ranking)
- Details on the derivation of k=2.0 and the pole fix (non-negativity clamp): see bm25_saturating_transform_2026_07_31.

Optional dependency: rank_bm25>=0.7 (pip install -e '.[hybrid]')
Fallback in server.py + userprompt_hook.py: try/except ImportError → ChromaMemoryRepository directly

Tokenisation: doc.lower().split() — no NLTK dependency

Status 2026-10-04: BM25 and hybrid fusion run only on the Chroma rollback backend; the default mem_query is a keyword overlap over record files (see docs/reference/chroma_rollback_backend.md).

## Our notes

