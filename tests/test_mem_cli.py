"""Tests for the `mem` CLI (synthetic fixtures only).

Coverage -- every write the consumers make today and its `mem` replacement:

| today                              | mem                                                        |
|------------------------------------|------------------------------------------------------------|
| mem_add                            | add --id ID --type T [--topic X] [--perspective P] --text  |
| mem_link                           | link SOURCE TARGET --type EDGE [--to-area PATH]            |
| mem_boost(cue=...)                 | add --id ID --cue "..." (existing record, text kept)       |
| mem_delete                         | delete ID...                                               |
| mem_move                           | move (chunk 1b-2)                                          |
| current_focus                      | add --id current_focus --text ... (writes FOCUS.md)        |
| mem_split / mem_dream              | archivist via `mem-dream`, not `mem`                       |
"""
from __future__ import annotations

import hashlib
import json

import pytest

from ai_mem.infrastructure.areas import Area, find_area, resolve_ref
from ai_mem.mem_cli import main
from ai_mem.upgrade_guard import GUARD_MESSAGE, mark_records_v1_done


def _make_area(path):
    (path / "docs" / "records").mkdir(parents=True)
    return Area(path.resolve(), (path / "docs" / "records").resolve())


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = tmp_path / "db"
    db.mkdir()
    monkeypatch.setenv("AI_MEM_PATH", str(db))
    monkeypatch.delenv("AI_MEM_RECORDS_HOME", raising=False)
    monkeypatch.delenv("AI_MEM_WORKSPACE_ROOT", raising=False)
    proj = _make_area(tmp_path / "ws" / "proj")
    other = _make_area(tmp_path / "ws" / "other")
    monkeypatch.chdir(proj.root)
    return tmp_path, db, proj, other


def _tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def _record(area, entry_id):
    (path,) = area.records_dir.rglob(f"{entry_id}.md")
    return path


def _add(*args):
    return main(["add", *args])


def test_add_creates_a_record_and_prints_one_line(env, capsys):
    _, _, proj, _ = env

    assert _add("--id", "learning_a", "--type", "learning", "--topic", "tools", "--text", "Body text.") == 0

    assert capsys.readouterr().out == "added learning_a\n"
    path = _record(proj, "learning_a")
    assert path.parent.name == "learnings" and path.parent.parent.name == "tools"
    assert "Body text." in path.read_text()


def test_add_json_output(env, capsys):
    _add("--json", "--id", "learning_a", "--type", "learning", "--text", "x")

    assert json.loads(capsys.readouterr().out)["action"] == "added"


def test_add_reads_text_from_file_and_stdin(env, tmp_path, monkeypatch):
    _, _, proj, _ = env
    source = tmp_path / "body.txt"
    source.write_text("From file.")
    assert _add("--id", "learning_f", "--type", "learning", "--file", str(source)) == 0
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("From stdin."))
    assert _add("--id", "learning_s", "--type", "learning", "-") == 0

    assert "From file." in _record(proj, "learning_f").read_text()
    assert "From stdin." in _record(proj, "learning_s").read_text()


def test_add_new_id_needs_type_and_text(env, capsys):
    assert _add("--id", "learning_a", "--text", "x") == 2
    assert _add("--id", "learning_a", "--type", "learning") == 2
    assert _add("--id", "learning_a", "--type", "learning", "--text", "x", "--file", "y") == 2


def test_add_rejects_an_untyped_taxonomy_violation(env):
    assert _add("--id", "x", "--type", "fact", "--text", "x") == 2


def test_cue_only_update_changes_only_the_cue_line(env):
    _, _, proj, _ = env
    _add("--id", "learning_a", "--type", "learning", "--topic", "tools", "--perspective", "dev", "--text", "Body.")
    _add("--id", "learning_a2", "--type", "learning", "--text", "Other.")
    assert main(["link", "learning_a", "learning_a2", "--type", "related"]) == 0
    path = _record(proj, "learning_a")
    before = path.read_text().splitlines()

    assert _add("--id", "learning_a", "--cue", "When  something\nhappens") == 0

    after = path.read_text().splitlines()
    assert [line for line in after if line not in before] == ["cue: When something happens"]
    assert [line for line in before if line not in after] == []


def test_cue_empty_string_clears_the_cue(env):
    _, _, proj, _ = env
    _add("--id", "learning_a", "--type", "learning", "--text", "Body.")
    _add("--id", "learning_a", "--cue", "x")

    assert _add("--id", "learning_a", "--cue", "") == 0

    assert "cue:" not in _record(proj, "learning_a").read_text()


def test_existing_id_without_changes_is_a_usage_error(env):
    _add("--id", "learning_a", "--type", "learning", "--text", "Body.")

    assert _add("--id", "learning_a") == 2


def test_add_current_focus_writes_focus_md(env):
    _, _, proj, _ = env

    assert _add("--id", "current_focus", "--text", "Working on X.") == 0

    assert (proj.records_dir / "FOCUS.md").read_text().strip() == "Working on X."


def test_link_same_area_and_cross_area(env, capsys):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--id", "learning_b", "--type", "learning", "--text", "B.")
    _add("--area", str(other.root), "--id", "pattern_t", "--type", "pattern", "--text", "T.")

    assert main(["link", "learning_a", "learning_b", "--type", "related"]) == 0
    assert main(["link", "learning_a", "pattern_t", "--type", "related", "--to-area", str(other.root)]) == 0

    edges = _record(proj, "learning_a").read_text()
    assert "learning_b" in edges and "../other:pattern_t" in edges
    assert resolve_ref(proj, "../other:pattern_t") == (other, "pattern_t")
    assert not list(other.records_dir.rglob("learning_a.md"))


def test_link_accepts_an_already_qualified_target(env):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--area", str(other.root), "--id", "pattern_t", "--type", "pattern", "--text", "T.")

    assert main(["link", "learning_a", "../other:pattern_t", "--type", "derived_from"]) == 0


def test_link_conflicts_exit_1(env):
    _, _, _, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--area", str(other.root), "--id", "pattern_t", "--type", "pattern", "--text", "T.")

    assert main(["link", "learning_a", "missing", "--type", "related"]) == 1
    assert main(["link", "learning_a", "pattern_t", "--type", "supersedes", "--to-area", str(other.root)]) == 1


def test_delete_removes_and_reports_missing(env, capsys):
    _, _, proj, _ = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    capsys.readouterr()

    assert main(["delete", "learning_a", "learning_gone"]) == 1

    assert capsys.readouterr().out.splitlines() == ["deleted learning_a", "not found learning_gone"]
    assert not list(proj.records_dir.rglob("learning_a.md"))


def test_delete_requires_ids(env):
    with pytest.raises(SystemExit) as exc:
        main(["delete"])
    assert exc.value.code == 2


HOSTILE_IDS = ["a:b", "../x", "a/b", "..", "*", "a?", "[ab]", "/etc/passwd", "~/x", "../other:learning_x", "", "INDEX", "FOCUS", "nl\nx", "tab\tx", " lead", "trail "]


@pytest.mark.parametrize("bad", HOSTILE_IDS)
def test_hostile_ids_are_refused_before_any_write(env, bad):
    tmp_path, _, proj, other = env
    _add("--id", "learning_ok", "--type", "learning", "--text", "ok")
    before = _tree(tmp_path / "ws")

    assert _add("--id", bad, "--type", "learning", "--text", "x") == 2
    assert main(["link", bad, "learning_ok", "--type", "related"]) == 2
    assert main(["link", "learning_ok", bad, "--type", "related", "--to-area", str(other.root)]) == 2
    assert main(["delete", "learning_ok", bad]) == 2

    assert _tree(tmp_path / "ws") == before


@pytest.mark.parametrize("target", ["/etc:x", "~/x:y", "..:*", "../a:b/c", "x:"])
def test_hostile_link_targets_are_refused(env, target):
    _add("--id", "learning_ok", "--type", "learning", "--text", "ok")

    assert main(["link", "learning_ok", target, "--type", "related"]) == 2


def test_well_formed_but_unresolvable_target_is_a_conflict(env):
    _add("--id", "learning_ok", "--type", "learning", "--text", "ok")

    assert main(["link", "learning_ok", "../../..:x", "--type", "related"]) == 1


def test_to_area_must_be_an_area(env, tmp_path):
    _add("--id", "learning_ok", "--type", "learning", "--text", "ok")
    plain = tmp_path / "plain"
    plain.mkdir()

    assert main(["link", "learning_ok", "x", "--type", "related", "--to-area", str(plain)]) == 2


def test_no_area_exits_2(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AI_MEM_PATH", str(tmp_path))
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)

    assert _add("--id", "learning_a", "--type", "learning", "--text", "x") == 2
    assert "no area" in capsys.readouterr().err
    assert main(["context"]) == 2


def test_area_flag_selects_the_area(env, tmp_path):
    _, _, proj, other = env

    assert _add("--area", str(other.records_dir), "--id", "learning_a", "--type", "learning", "--text", "x") == 0

    assert list(other.records_dir.rglob("learning_a.md")) and not list(proj.records_dir.rglob("learning_a.md"))


def test_pending_migration_blocks_every_write(env, capsys):
    tmp_path, db, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--id", "learning_b", "--type", "learning", "--text", "B.")
    (db / "chroma.sqlite3").write_bytes(b"")
    before = _tree(tmp_path)

    codes = [
        _add("--id", "learning_c", "--type", "learning", "--text", "C."),
        _add("--id", "learning_a", "--cue", "x"),
        _add("--id", "current_focus", "--text", "f"),
        main(["link", "learning_a", "learning_b", "--type", "related"]),
        main(["delete", "learning_a"]),
    ]

    assert codes == [3] * 5
    assert GUARD_MESSAGE in capsys.readouterr().err
    assert _tree(tmp_path) == before


def test_guard_lifts_with_the_sentinel(env):
    _, db, _, _ = env
    (db / "chroma.sqlite3").write_bytes(b"")
    mark_records_v1_done(db)

    assert _add("--id", "learning_a", "--type", "learning", "--text", "A.") == 0


def test_context_reports_paths_and_legacy_collection(env, tmp_path, monkeypatch, capsys):
    _, _, proj, _ = env
    home = tmp_path / "ai-mem-records"
    coll = _make_area(home / "workspace")
    monkeypatch.setenv("AI_MEM_RECORDS_HOME", str(home))

    assert main(["context", "--json"]) == 0
    info = json.loads(capsys.readouterr().out)
    assert info["area_root"] == str(proj.root) and info["legacy_collection"] is None
    assert info["index"].endswith("docs/records/INDEX.md") and info["focus"].endswith("docs/records/FOCUS.md")

    assert main(["context", str(coll.records_dir)]) == 0
    assert "legacy_collection: workspace" in capsys.readouterr().out
    assert find_area(coll.root) == coll


def test_stubs_exit_2(env, capsys):
    assert main(["lint"]) == 2
    assert main(["doctor"]) == 2
    assert "not implemented yet" in capsys.readouterr().err


def test_importing_the_cli_loads_no_third_party_module():
    import subprocess
    import sys

    code = "import sys, ai_mem.mem_cli as m; bad=[n for n in ('chromadb','mcp','rank_bm25','yaml') if n in sys.modules]; print(bad); m.main(['--help'])"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)

    assert result.returncode == 0 and result.stdout.startswith("[]")


def test_add_refuses_to_overwrite_an_unreadable_record(env):
    _, _, proj, _ = env
    broken = proj.records_dir / "learnings" / "hw.md"
    broken.parent.mkdir(parents=True)
    broken.write_text("---\nid: hw\ntype: learning\nedges: related:t1\n---\nHand-written body.\n")
    before = broken.read_text()

    assert _add("--id", "hw", "--type", "learning", "--text", "clobber") == 1

    assert broken.read_text() == before
