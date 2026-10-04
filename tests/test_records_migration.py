"""Tests for the records_v1 migration (ChromaDB-only store -> record files)."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from ai_mem.adr_cli import _cmd_migrate
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import read_mapping
from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository
from ai_mem.infrastructure.records_migration import (
    BACKUP_SUFFIX,
    REPORT_FILENAME,
    apply_plan,
    build_plan,
    classify,
    discover_roots,
    match_by_name,
    render_report,
)


@pytest.mark.parametrize(("entry_id", "entry_type", "text", "kind", "record_type", "auto"), [
    ("current_focus", "project", "Fokus", "focus", None, False),
    ("d1", "domain", "Decision: x", "record", "domain", False),
    ("t1", "todo", "do it", "record", "todo", False),
    ("u1", "user", "likes X", "record", "user", False),
    ("r1", "reference", "docs", "reference", None, False),
    ("f1", "feedback", "Always do X", "record", "pattern", True),
    ("f2", "feedback", "Tried: X\nFailed because: Y", "record", "anti-pattern", True),
    ("p1", "project", "Observed: it broke", "record", "learning", True),
    ("p2", "project", "Decision: we use X", "record", "domain", True),
    ("p3", "project", "# Rule: never X", "record", "pattern", True),
    ("todo_a", "project", "Open work", "record", "todo", True),
    ("todo_b", "reference", "RESULT (done): shipped", "reference", None, False),
    ("todo_c", "project", "RESULT (done): shipped", "record", "learning", True),
    ("x1", "project", "TODO: later", "record", "todo", True),
    ("x2", None, "something learned", "record", "learning", True),
])
def test_classify(entry_id, entry_type, text, kind, record_type, auto):
    placement = classify(entry_id, entry_type, text)
    assert (placement.kind, placement.type, placement.auto) == (kind, record_type, auto)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """A workspace root with two CLAUDE.md projects, one nested, wired via AI_MEM_WORKSPACE_ROOT."""
    root = tmp_path / "ws"
    for rel in ("alpha", "group/beta"):
        (root / rel).mkdir(parents=True)
        (root / rel / "CLAUDE.md").write_text("# x\n")
    (root / "group" / "legacy-name").mkdir()
    monkeypatch.setenv("AI_MEM_WORKSPACE_ROOT", str(root))
    return root


def test_discover_roots_uses_runtime_collection_names(workspace):
    assert discover_roots([workspace]) == {
        "repo.alpha": workspace / "alpha",
        "repo.group.beta": workspace / "group" / "beta",
    }


def test_match_by_name_unique_and_ambiguous(workspace):
    match, _ = match_by_name("repo.legacy-name", [workspace])
    assert match == workspace / "group" / "legacy-name"

    (workspace / "alpha" / "legacy-name").mkdir()
    match, candidates = match_by_name("repo.legacy-name", [workspace])
    assert match is None and len(candidates) == 2


@pytest.fixture
def store(tmp_path, workspace):
    db_path = tmp_path / "db"
    repo = ChromaMemoryRepository(db_path)
    add = AddMemoryUseCase(repo)
    add.execute("repo.alpha", ["Fokus A"], ["current_focus"], metadatas=[{"type": "project"}])
    add.execute("repo.alpha", ["Decision: keep X"], ["domain_x"], metadatas=[{"type": "domain", "area": "arch"}])
    add.execute("repo.alpha", ["Always check Y"], ["fb_y"], metadatas=[{"type": "feedback", "cue": "before Y"}])
    add.execute("repo.alpha", ["How the thing works"], ["ref_z"], metadatas=[{"type": "reference"}])
    add.execute("repo.alpha", ["Prefers short answers"], ["user_pref"], metadatas=[{"type": "user"}])
    add.execute("repo.group.beta", ["Open work"], ["todo_beta"], metadatas=[{"type": "project"}])
    add.execute("repo.legacy-name", ["Observed: old"], ["old_obs"], metadatas=[{"type": "project"}])
    add.execute("repo.nowhere", ["lost"], ["lost_1"], metadatas=[{"type": "domain"}])
    return argparse.Namespace(db_path=db_path, repo=repo, ws=workspace)


def test_dry_plan_writes_nothing(store):
    plan = build_plan(store.repo, store.db_path, [store.ws])

    assert len(plan.writes) == 7
    assert not (store.ws / "alpha" / "docs").exists()


def test_apply_writes_records_focus_reference_and_reports_the_rest(store):
    plan = build_plan(store.repo, store.db_path, [store.ws])
    backup = apply_plan(plan, store.repo, store.db_path)
    records = store.ws / "alpha" / "docs" / "records"

    assert (records / "FOCUS.md").read_text() == "Fokus A\n"
    assert adr_markdown.parse((records / "arch" / "decisions" / "domain_x.md").read_text()).type == "domain"
    fb = adr_markdown.parse((records / "general" / "decisions" / "fb_y.md").read_text())
    assert (fb.type, fb.cue) == ("pattern", "before Y")
    assert (store.ws / "alpha" / "docs" / "reference" / "ref_z.md").read_text() == "How the thing works\n"
    assert (records / "general" / "user" / "user_pref.md").is_file()
    assert (store.ws / "group" / "beta" / "docs" / "records" / "general" / "todos" / "todo_beta.md").exists()
    assert (store.ws / "group" / "legacy-name" / "docs" / "records" / "general" / "learnings" / "old_obs.md").exists()
    assert "fb_y" in (records / "INDEX.md").read_text()

    assert plan.unresolved == {"repo.nowhere": 1}
    assert plan.name_matched == {"repo.legacy-name"}
    report = render_report(plan)
    assert "repo.nowhere" in report and "| fb_y | feedback | pattern |" in report

    assert backup == store.db_path.with_name(store.db_path.name + BACKUP_SUFFIX) and backup.is_dir()
    assert read_mapping(store.db_path)["repo.alpha"] == str(store.ws / "alpha")
    [aligned] = store.repo.get_by_ids("repo.alpha", ["fb_y"])
    assert aligned.metadata["type"] == "pattern" and aligned.metadata["cue"] == "before Y"


def test_second_run_is_idempotent(store):
    apply_plan(build_plan(store.repo, store.db_path, [store.ws]), store.repo, store.db_path)

    again = build_plan(store.repo, store.db_path, [store.ws])

    assert again.writes == [] and again.conflicts == [] and again.already == 7


def test_existing_different_file_is_a_conflict_and_left_untouched(store):
    focus = store.ws / "alpha" / "docs" / "records" / "FOCUS.md"
    focus.parent.mkdir(parents=True)
    focus.write_text("hand-written\n")

    plan = build_plan(store.repo, store.db_path, [store.ws])
    apply_plan(plan, store.repo, store.db_path)

    assert focus.read_text() == "hand-written\n"
    assert [w.entry_id for w in plan.conflicts] == ["current_focus"]


def test_record_filed_elsewhere_is_not_duplicated(store):
    other = store.ws / "alpha" / "docs" / "records" / "general" / "learnings" / "fb_y.md"
    other.parent.mkdir(parents=True)
    other.write_text("id: fb_y\ntype: learning\narea: general\n---\n\nAlways check Y")

    plan = build_plan(store.repo, store.db_path, [store.ws])

    assert "fb_y" in [w.entry_id for w in plan.conflicts]
    assert "fb_y" not in [w.entry_id for w in plan.writes]


def test_entry_already_in_reference_or_records_is_not_duplicated(store):
    reference = store.ws / "alpha" / "docs" / "reference" / "fb_y.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("Always check Y\n")
    record = store.ws / "alpha" / "docs" / "records" / "general" / "learnings" / "ref_z.md"
    record.parent.mkdir(parents=True)
    record.write_text("id: ref_z\ntype: learning\narea: general\n---\n\nHow the thing works")

    plan = build_plan(store.repo, store.db_path, [store.ws])

    written = [w.entry_id for w in plan.writes]
    assert "fb_y" not in written and "ref_z" not in written
    assert {"fb_y", "ref_z"} <= {w.entry_id for w in plan.conflicts}


def test_cli_migrate_dry_run_then_apply(store, capsys):
    args = argparse.Namespace(db_path=str(store.db_path), apply=False, root=None, scan_root=[str(store.ws)])
    assert _cmd_migrate(args) == 0
    assert "Dry run" in capsys.readouterr().out
    assert not (store.db_path / REPORT_FILENAME).exists()

    args.apply = True
    args.root = [f"repo.nowhere={store.ws / 'alpha'}"]
    assert _cmd_migrate(args) == 0
    assert (store.db_path / REPORT_FILENAME).exists()
    assert (store.ws / "alpha" / "docs" / "records" / "general" / "decisions" / "lost_1.md").exists()


def test_cli_migrate_rejects_malformed_root(store):
    args = argparse.Namespace(db_path=str(store.db_path), apply=False, root=["no-equals-sign"], scan_root=None)
    assert _cmd_migrate(args) == 2
