"""Integration: the real server-side stack (Chroma -> MarkdownAdrRepository -> BM25).

test_markdown_adr_repository.py covers the decorator against a fake; this checks that
the volatile-field (boost_count/cue) diff-before-write boundary also holds when the real
use cases drive the real stack.
"""
from __future__ import annotations

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.boost_confidence import BoostConfidenceUseCase
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import record_collection_root
from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository
from ai_mem.infrastructure.markdown_adr_repository import MarkdownAdrRepository

COLLECTION = "repo.integration"


@pytest.fixture
def stack(tmp_path):
    db_path = tmp_path / "db"
    repo_root = tmp_path / "repo"
    record_collection_root(db_path, COLLECTION, repo_root)
    repo = MarkdownAdrRepository(ChromaMemoryRepository(db_path), db_path)
    try:
        from ai_mem.infrastructure.bm25_repository import BM25MemoryRepository
        repo = BM25MemoryRepository(repo)
    except ImportError:
        pass
    return repo, repo_root / "docs" / "records" / "general" / "decisions"


def test_boost_and_cue_do_not_touch_the_file(stack):
    repo, adr_dir = stack
    AddMemoryUseCase(repo).execute(COLLECTION, ["Decision: A\nWhy: B\nScope: C"], ["domain_a"], [{"type": "domain"}])
    file_path = adr_dir / "domain_a.md"
    content, mtime_ns = file_path.read_text(), file_path.stat().st_mtime_ns

    BoostConfidenceUseCase(repo).execute(COLLECTION, ["domain_a"], cue="when deciding A")
    BoostConfidenceUseCase(repo).execute(COLLECTION, ["domain_a"])

    assert file_path.read_text() == content
    assert file_path.stat().st_mtime_ns == mtime_ns
    assert repo.get_by_ids(COLLECTION, ["domain_a"])[0].metadata["boost_count"] == 2


def test_supersede_then_clear_leaves_parseable_files(stack):
    repo, adr_dir = stack
    add = AddMemoryUseCase(repo)
    add.execute(COLLECTION, ["Decision: old"], ["domain_old"], [{"type": "domain"}])
    add.execute(COLLECTION, ["Decision: new"], ["domain_new"], [{"type": "domain"}])

    AddEdgeUseCase(repo).execute(COLLECTION, "domain_new", "domain_old", "supersedes")
    assert adr_markdown.parse((adr_dir / "domain_old.md").read_text()).superseded_by == "domain_new"

    add.execute(COLLECTION, ["Decision: old"], ["domain_old"], [{"superseded_by": "", "valid_until": ""}])

    parsed = adr_markdown.parse((adr_dir / "domain_old.md").read_text())
    assert parsed.superseded_by is None
    assert parsed.valid_until is None
