---
type: retired-system
date: 2026-07-31
origin: memory entry bm25_hybrid_impl, exported to docs/reference/ on 2026-10-04
status: processed
---

## What the source says

BM25 Hybrid Search — implementiert 2026-04-29, Fusionsformel korrigiert 2026-07-31, BM25-Restbug gefixt 2026-07-31 (später am selben Tag)

Datei: ai_mem/infrastructure/bm25_repository.py
- BM25MemoryRepository wraps jedes MemoryRepository-kompatibles Objekt
- _BM25_FETCH=50: holt intern 50 Kandidaten statt der n_results die der Aufrufer will
- Score-Fusion: hybrid = alpha × cosine_raw + (1-alpha) × bm25_sat -- cosine ist echte Cosine-Similarity (chroma_repository.py-Fix), kein Min-Max mehr. BM25s Rohwert durchläuft _saturate() (raw/(raw+k), k=2.0, non-negativity-geclampt) statt einer Min-Max-Normalisierung.
- alpha=0.5 default, im Konstruktor konfigurierbar
- Alle anderen MemoryRepository-Methoden delegieren 1:1 an inner
- Transparent zur Application-Schicht: QueryResult.score enthält fused score, direkt für Sortierung verwendet (kein weiteres Re-Ranking)
- Details zur Herleitung von k=2.0 und dem Pol-Fix (non-negativity clamp): siehe bm25_saturating_transform_2026_07_31.

Optionale Dependency: rank_bm25>=0.7 (pip install -e '.[hybrid]')
Fallback in server.py + userprompt_hook.py: try/except ImportError → ChromaMemoryRepository direkt

Tokenisierung: doc.lower().split() — keine NLTK-Dependency

Status 2026-10-04: BM25 and hybrid fusion run only on the Chroma rollback backend; the default mem_query is a keyword overlap over record files (see docs/reference/chroma_rollback_backend.md).

## Our notes

