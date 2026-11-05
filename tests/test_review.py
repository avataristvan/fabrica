"""mem review: the records a push would publish, with what should not leave the machine."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_mem import review

RECORD = "type: learning\ntopic: general\ncreated: 1791630404.0\n---\n\n{body}\n"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("AI_MEM_PATH", str(tmp_path / "state"))
    root = tmp_path / "area"
    (root / "docs" / "records" / "general" / "learnings").mkdir(parents=True)
    _git(root, "init", "-q")
    (root / "docs" / "records" / "FOCUS.md").write_text("focus\n")
    _git(root, "add", "-A"); _git(root, "commit", "-qm", "base")
    _git(root, "tag", "base")
    return root


def _record(root: Path, name: str, body: str) -> None:
    (root / "docs" / "records" / "general" / "learnings" / f"{name}.md").write_text(RECORD.format(body=body))


def test_lists_added_records_with_title_and_skips_state_files(repo: Path) -> None:
    _record(repo, "learning_a", "Observed: a thing")
    (repo / "docs" / "records" / "FOCUS.md").write_text("new focus\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-qm", "a")
    items = review.collect(repo, repo / "docs" / "records", "base")
    assert [(i["change"], i["file"], i["title"], i["flags"]) for i in items] == [
        ("added", "docs/records/general/learnings/learning_a.md", "Observed: a thing", [])]


def test_flags_machine_paths_private_names_and_unpushed_commits(repo: Path, tmp_path: Path) -> None:
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "private_names").write_text("# names\nKaustabh\n")
    _record(repo, "learning_b", "x")
    _git(repo, "add", "-A"); _git(repo, "commit", "-qm", "b")
    local = _git(repo, "rev-parse", "--short=7", "HEAD")
    _record(repo, "learning_b", f"Evidence: /home/someone/x.log, commit {local}, reported to kaustabh.")
    _git(repo, "add", "-A"); _git(repo, "commit", "-qm", "b2")
    flags = review.collect(repo, repo / "docs" / "records", "base")[0]["flags"]
    assert "machine path /home/someone/" in flags
    assert "private name 'Kaustabh'" in flags
    assert any(local in f and "squash at the push would orphan it" in f for f in flags)


def test_a_commit_off_this_branch_is_flagged(repo: Path) -> None:
    _git(repo, "checkout", "-qb", "side")
    (repo / "x.txt").write_text("x\n")
    _git(repo, "add", "-A"); _git(repo, "commit", "-qm", "side")
    side = _git(repo, "rev-parse", "--short=7", "HEAD")
    _git(repo, "checkout", "-q", "-")
    _record(repo, "learning_c", f"Evidence: commit {side}")
    _git(repo, "add", "-A"); _git(repo, "commit", "-qm", "c")
    flags = review.collect(repo, repo / "docs" / "records", "base")[0]["flags"]
    assert any("not on this branch" in f for f in flags)


def test_unknown_base_is_an_error(repo: Path) -> None:
    with pytest.raises(ValueError):
        review.collect(repo, repo / "docs" / "records", "@{upstream}")
