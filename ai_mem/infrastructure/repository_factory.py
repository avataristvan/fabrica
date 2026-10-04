"""The one place that decides which MemoryRepository backs ai-mem.

Default since 2026-10-04: `FileMemoryRepository` -- the record files are the store and no
database is opened (domain_records_model_replaces_chroma_2026_10_04).

`AI_MEM_BACKEND=chroma` is the rollback escape hatch: the previous stack (ChromaDB, the
Markdown projection decorator unless AI_MEM_ADR_DISABLED=1, BM25 when installed). Imports
for it stay lazy so the default path never loads chromadb or an embedding model.
"""
from __future__ import annotations

import os
from pathlib import Path

from ai_mem.domain.memory import MemoryRepository

BACKEND_ENV = "AI_MEM_BACKEND"


def uses_chroma() -> bool:
    return os.environ.get(BACKEND_ENV, "files").strip().lower() == "chroma"


def records_enabled() -> bool:
    """False only with AI_MEM_ADR_DISABLED=1 (Chroma rollback without the Markdown projection)."""
    return os.environ.get("AI_MEM_ADR_DISABLED") != "1"


def build_repository(db_path: Path, with_bm25: bool = True) -> MemoryRepository:
    if not uses_chroma():
        from ai_mem.infrastructure.file_repository import FileMemoryRepository
        return FileMemoryRepository(db_path)

    from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository
    repo = ChromaMemoryRepository(db_path)
    if records_enabled():
        from ai_mem.infrastructure.markdown_adr_repository import MarkdownAdrRepository
        repo = MarkdownAdrRepository(repo, db_path)
    if with_bm25:
        try:
            from ai_mem.infrastructure.bm25_repository import BM25MemoryRepository
            repo = BM25MemoryRepository(repo)
        except ImportError:
            pass
    return repo
