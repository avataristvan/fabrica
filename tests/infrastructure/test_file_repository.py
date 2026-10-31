"""Tests for FileMemoryRepository: the MemoryRepository protocol over record files, no database."""
from __future__ import annotations

import json

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.domain.memory import MemoryEdge, MemoryEntry
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import records_dir_for_root
from ai_mem.infrastructure.areas import area_records_dir
from ai_mem.infrastructure.file_repository import FileMemoryRepository

COLLECTION = "repo.example"


@pytest.fixture
def root(tmp_path):
    path = tmp_path / "repo"
    path.mkdir()
    return path


@pytest.fixture
def repo(root):
    return FileMemoryRepository(lambda key: records_dir_for_root(root) if key == COLLECTION else None)


def _records(root):
    return root / "docs" / "records"


def _entry(entry_id, text, **metadata):
    return MemoryEntry(id=entry_id, text=text, metadata=metadata)


def test_record_round_trip_keeps_structural_metadata(repo, root):
    repo.upsert(COLLECTION, [_entry("domain_x", "Decision: X", type="domain", area="arch", created_at=12.0,
                                    cue="when X", boost_count=3)])

    [entry] = repo.get_by_ids(COLLECTION, ["domain_x"])
    assert entry.text == "Decision: X"
    assert entry.metadata == {"type": "domain", "area": "arch", "created_at": 12.0, "cue": "when X"}
    assert (_records(root) / "arch" / "decisions" / "domain_x.md").is_file()
    assert "domain_x" in (_records(root) / "INDEX.md").read_text()


def test_focus_and_reference_are_plain_files(repo, root):
    repo.upsert(COLLECTION, [_entry("current_focus", "Now: X", type="project"),
                             _entry("ref_a", "How it works", type="reference")])

    assert (_records(root) / "FOCUS.md").read_text() == "Now: X\n"
    assert (root / "docs" / "reference" / "ref_a.md").read_text() == "How it works\n"
    got = {entry.id: entry for entry in repo.get_by_ids(COLLECTION, ["current_focus", "ref_a", "missing"])}
    assert got["current_focus"].text == "Now: X" and got["ref_a"].metadata == {"type": "reference"}
    assert "missing" not in got


@pytest.mark.parametrize("bad_type", ["feedback", "project", None])
def test_unstored_types_are_rejected_before_any_write(repo, root, bad_type):
    with pytest.raises(ValueError, match="is not stored"):
        repo.upsert(COLLECTION, [_entry("ok", "fine", type="domain"), _entry("bad", "x", type=bad_type)])
    assert not _records(root).exists()


def test_unsafe_id_and_area_are_rejected(repo):
    with pytest.raises(ValueError, match="filename"):
        repo.upsert(COLLECTION, [_entry("../x", "x", type="domain")])
    with pytest.raises(ValueError, match="folder"):
        repo.upsert(COLLECTION, [_entry("x", "x", type="domain", area="Bad Area")])


def test_unknown_collection_cannot_be_written_but_reads_empty(repo):
    with pytest.raises(ValueError, match="no records directory"):
        repo.upsert("repo.unknown", [_entry("x", "x", type="domain")])
    assert repo.get_all("repo.unknown") == [] and repo.get_by_ids("repo.unknown", ["x"]) == []


def test_retype_moves_the_file_and_reference_replaces_the_record(repo, root):
    repo.upsert(COLLECTION, [_entry("e", "Observed: x", type="learning")])
    repo.upsert(COLLECTION, [_entry("e", "Rule: x", type="pattern")])
    assert [p.parent.name for p in _records(root).rglob("e.md")] == ["decisions"]

    repo.upsert(COLLECTION, [_entry("e", "now docs", type="reference")])
    assert not list(_records(root).rglob("e.md"))
    assert repo.get_by_ids(COLLECTION, ["e"])[0].metadata["type"] == "reference"


def test_unchanged_upsert_does_not_touch_files(repo, root):
    repo.upsert(COLLECTION, [_entry("d", "Decision: d", type="domain", created_at=1.0)])
    path, index = _records(root) / "general" / "decisions" / "d.md", _records(root) / "INDEX.md"
    mtimes = (path.stat().st_mtime_ns, index.stat().st_mtime_ns)

    repo.upsert(COLLECTION, [_entry("d", "Decision: d", type="domain", created_at=1.0, boost_count=9)])

    assert (path.stat().st_mtime_ns, index.stat().st_mtime_ns) == mtimes


def test_get_all_and_list_collections(repo, root):
    repo.upsert(COLLECTION, [_entry("a", "A", type="todo"), _entry("current_focus", "F", type="project"),
                             _entry("r", "R", type="reference")])

    assert sorted(entry.id for entry in repo.get_all(COLLECTION)) == ["a", "current_focus", "r"]


def test_query_is_lexical_and_respects_type_filter(repo):
    repo.upsert(COLLECTION, [
        _entry("hook_rule", "Rule: hooks never inherit the MCP env", type="pattern"),
        _entry("other", "Observed: daemon latency", type="learning"),
    ])

    results = repo.query(COLLECTION, "why do hooks miss the env", n_results=5, max_age_days=None)
    assert [r.id for r in results] == ["hook_rule"] and results[0].rank == 1 and 0 < results[0].score <= 1
    assert repo.query(COLLECTION, "hooks env", 5, None, type_filter="learning") == []
    assert repo.query(COLLECTION, "a an", 5, None) == []


def test_edges_supersede_and_cue_through_the_use_cases(repo, root):
    add = AddMemoryUseCase(repo)
    add.execute(COLLECTION, ["Decision: old"], ["d_old"], [{"type": "domain"}])
    add.execute(COLLECTION, ["Decision: new"], ["d_new"], [{"type": "domain"}])

    AddEdgeUseCase(repo).execute(COLLECTION, "d_new", "d_old", "supersedes")
    AddEdgeUseCase(repo).execute(COLLECTION, "d_new", "d_old", "supersedes")  # idempotent
    [boosted] = repo.get_by_ids(COLLECTION, ["d_new"])
    boosted.metadata["cue"] = "when choosing"
    repo.upsert(COLLECTION, [boosted])

    assert repo.get_edges(COLLECTION, "d_new") == [MemoryEdge(target_id="d_old", edge_type="supersedes")]
    old = adr_markdown.parse((_records(root) / "general" / "decisions" / "d_old.md").read_text())
    assert old.superseded_by == "d_new"
    new = repo.get_by_ids(COLLECTION, ["d_new"])[0]
    assert new.metadata["cue"] == "when choosing" and json.loads(new.metadata["edges"])[0]["target_id"] == "d_old"
    assert "superseded" in (_records(root) / "INDEX.md").read_text()


def test_delete_removes_files_and_refuses_whole_collection(repo, root):
    repo.upsert(COLLECTION, [_entry("a", "A", type="todo"), _entry("current_focus", "F", type="project"),
                             _entry("r", "R", type="reference")])

    assert repo.delete(COLLECTION, ["a", "current_focus", "r", "missing"]) == 3
    assert repo.get_all(COLLECTION) == []
    assert "| a |" not in (_records(root) / "INDEX.md").read_text()
    with pytest.raises(ValueError, match="whole collection"):
        repo.delete(COLLECTION, None)


def test_database_only_operations_are_noops(repo):
    repo.upsert(COLLECTION, [_entry("a", "A", type="todo")])
    repo.record_access(COLLECTION, ["a"])
    assert repo.delete_expired(COLLECTION) == 0 and repo.delete_stale(COLLECTION, 0) == 0
    assert [e.id for e in repo.get_all(COLLECTION)] == ["a"]


def test_reads_existing_migrated_layout_without_writing(repo, root):
    path = _records(root) / "workflow" / "learnings" / "l1.md"
    path.parent.mkdir(parents=True)
    path.write_text(adr_markdown.serialize("l1", "learning", "Observed: y", {"created_at": 5.0, "area": "workflow"}))

    [entry] = repo.get_all(COLLECTION)
    assert (entry.id, entry.metadata["area"], entry.metadata["created_at"]) == ("l1", "workflow", 5.0)
    assert not (_records(root) / "INDEX.md").exists()


@pytest.mark.parametrize("pattern", ["*", "d?", "[d]0", "**", "d0\x00"])
def test_glob_like_ids_never_select_other_records(repo, root, pattern):
    repo.upsert(COLLECTION, [_entry(f"d{i}", "Decision: x", type="domain") for i in range(3)])

    assert repo.delete(COLLECTION, [pattern]) == 0
    assert repo.get_by_ids(COLLECTION, [pattern]) == []
    assert len(repo.get_all(COLLECTION)) == 3
    with pytest.raises(ValueError, match="filename"):
        repo.upsert(COLLECTION, [_entry(pattern, "x", type="domain")])


def test_perspective_and_unknown_keys_survive_a_rewrite_through_the_repository(repo, root):
    path = _records(root) / "arch" / "decisions" / "domain_x.md"
    path.parent.mkdir(parents=True)
    original = ("id: domain_x\ntype: domain\narea: arch\nperspective: user\ncreated: 1.0\n"
                "status: accepted\nowner: team-a\ncue: when x\n---\n\nDecision: X")
    path.write_text(original)

    [entry] = repo.get_by_ids(COLLECTION, ["domain_x"])
    assert entry.metadata["perspective"] == "user"
    assert entry.metadata["extra_frontmatter"] == {"status": "accepted", "owner": "team-a"}
    repo.upsert(COLLECTION, [entry])
    assert path.read_text() == original

    repo.upsert(COLLECTION, [_entry("domain_y", "Decision: Y", type="domain", area="arch")])
    AddEdgeUseCase(repo).execute(COLLECTION, "domain_x", "domain_y", "related")
    text = path.read_text()
    assert "perspective: user\n" in text and "status: accepted\nowner: team-a\ncue: when x\n---" in text


def test_invalid_perspective_and_extra_keys_are_rejected_before_writing(repo, root):
    with pytest.raises(ValueError, match="perspective"):
        repo.upsert(COLLECTION, [_entry("d", "x", type="domain", perspective="../User")])
    with pytest.raises(ValueError, match="frontmatter key"):
        repo.upsert(COLLECTION, [_entry("d", "x", type="domain", extra_frontmatter={"cue": "x"})])
    assert not _records(root).exists()


@pytest.fixture
def area_repo():
    return FileMemoryRepository(area_records_dir)


def _area_key(path):
    (path / "docs" / "records").mkdir(parents=True)
    return str(path.resolve())


def test_area_repository_writes_records_focus_and_references(tmp_path, area_repo, monkeypatch):
    repo = area_repo
    key = _area_key(tmp_path / "proj")
    monkeypatch.chdir(tmp_path / "proj")

    repo.upsert(key, [_entry("domain_x", "Decision: X", type="domain", area="arch"),
                      _entry("current_focus", "Now: X", type="project"),
                      _entry("ref_a", "How it works", type="reference")])

    records = tmp_path / "proj" / "docs" / "records"
    assert (records / "arch" / "decisions" / "domain_x.md").is_file()
    assert (records / "FOCUS.md").read_text() == "Now: X\n"
    assert (tmp_path / "proj" / "docs" / "reference" / "ref_a.md").is_file()
    assert {e.id for e in repo.get_all(key)} == {"domain_x", "current_focus", "ref_a"}
    assert [(c.name, c.count) for c in repo.list_collections()] == [(key, 3)]
    assert repo.delete(key, ["current_focus", "domain_x"]) == 2


def test_area_repository_ignores_collection_names(tmp_path, area_repo, root, monkeypatch):
    repo = area_repo
    monkeypatch.chdir(tmp_path)

    assert repo.get_all(COLLECTION) == [] and repo.list_collections() == []
    with pytest.raises(ValueError, match="no records directory for area"):
        repo.upsert(COLLECTION, [_entry("d", "x", type="domain")])
    assert not _records(root).exists()


def test_qualified_ids_are_never_looked_up_locally(tmp_path, area_repo):
    repo = area_repo
    key = _area_key(tmp_path / "proj")
    repo.upsert(key, [_entry("domain_x", "Decision: X", type="domain")])

    assert repo.get_by_ids(key, ["../proj:domain_x", "./x:domain_x", "/etc:passwd"]) == []
