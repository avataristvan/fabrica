"""Shared pytest fixtures for ai-mem tests."""
from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Modules like server.py build their repository stack at import time from AI_MEM_PATH.
# Point it at a throwaway dir before any test module imports them, so a test that forgets
# to mock _add/_query can't write into the real ~/.local/share/ai-mem. ADR persistence is
# off for the same reason: the collection -> repo-root mapping resolves via cwd, so an
# unmocked domain/pattern write would otherwise land in this repo's real docs/decisions/.
# Tests of the ADR layer construct MarkdownAdrRepository directly and are unaffected.
_TEST_DB_PATH = tempfile.mkdtemp(prefix="ai-mem-test-")
atexit.register(shutil.rmtree, _TEST_DB_PATH, ignore_errors=True)
os.environ["AI_MEM_PATH"] = _TEST_DB_PATH
os.environ["AI_MEM_ADR_DISABLED"] = "1"

from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository


@pytest.fixture
def tmp_repo(tmp_path: Path) -> ChromaMemoryRepository:
    """A fresh ChromaMemoryRepository backed by a temp directory."""
    return ChromaMemoryRepository(tmp_path / "chroma")


@pytest.fixture
def track_access(tmp_repo) -> TrackAccessUseCase:
    return TrackAccessUseCase(tmp_repo)
