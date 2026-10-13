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
import shutil

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


def _edges_of(area, entry_id):
    line = next((l for l in _record(area, entry_id).read_text().splitlines() if l.startswith("edges: ")), None)
    return json.loads(line[len("edges: "):]) if line else []


def test_unlink_removes_only_the_named_edge(env, capsys):
    _, _, proj, _ = env
    for entry_id in ("learning_a", "learning_b", "learning_c"):
        _add("--id", entry_id, "--type", "learning", "--text", entry_id)
    main(["link", "learning_a", "learning_b", "--type", "related"])
    main(["link", "learning_a", "learning_b", "--type", "causes"])
    main(["link", "learning_a", "learning_c", "--type", "related"])
    capsys.readouterr()

    assert main(["unlink", "learning_a", "learning_b", "--type", "causes"]) == 0

    assert capsys.readouterr().out == "unlinked learning_a --causes--> learning_b\n"
    assert _edges_of(proj, "learning_a") == [
        {"target_id": "learning_b", "edge_type": "related"}, {"target_id": "learning_c", "edge_type": "related"},
    ]
    assert main(["unlink", "learning_a", "learning_c"]) == 0
    assert main(["unlink", "learning_a", "learning_b"]) == 0
    assert "edges:" not in _record(proj, "learning_a").read_text()


def test_unlink_supersedes_clears_both_flags_on_the_target(env):
    _, _, proj, _ = env
    _add("--id", "learning_old", "--type", "learning", "--text", "old")
    _add("--id", "learning_new", "--type", "learning", "--text", "new")
    before = _record(proj, "learning_old").read_text()
    main(["link", "learning_new", "learning_old", "--type", "supersedes"])
    assert "superseded_by: learning_new" in _record(proj, "learning_old").read_text()

    assert main(["unlink", "learning_new", "learning_old"]) == 0

    assert _record(proj, "learning_old").read_text() == before
    assert _edges_of(proj, "learning_new") == []


def test_unlink_removes_an_edge_to_a_deleted_record(env):
    _, _, proj, _ = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--id", "todo_gone", "--type", "todo", "--text", "T.")
    main(["link", "learning_a", "todo_gone", "--type", "related"])
    main(["delete", "todo_gone"])

    assert main(["unlink", "learning_a", "todo_gone"]) == 0
    assert _edges_of(proj, "learning_a") == []


def test_unlink_conflicts_exit_1(env, capsys):
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--id", "learning_b", "--type", "learning", "--text", "B.")
    main(["link", "learning_a", "learning_b", "--type", "related"])
    capsys.readouterr()

    assert main(["unlink", "missing", "learning_b"]) == 1
    assert main(["unlink", "learning_a", "learning_b", "--type", "causes"]) == 1
    assert "has no edge of type 'causes'" in capsys.readouterr().err
    assert main(["unlink", "learning_b", "learning_a"]) == 1


def test_delete_removes_and_reports_missing(env, capsys):
    _, _, proj, _ = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    capsys.readouterr()

    assert main(["delete", "learning_a", "learning_gone"]) == 1

    assert capsys.readouterr().out.splitlines() == ["deleted learning_a", "not found learning_gone"]
    assert not list(proj.records_dir.rglob("learning_a.md"))


def test_delete_names_the_edges_it_leaves_dangling_and_unlink_clears_them(env, capsys):
    _, _, proj, _ = env
    for entry_id, entry_type in (("todo_x", "todo"), ("learning_a", "learning"), ("learning_b", "learning")):
        _add("--id", entry_id, "--type", entry_type, "--text", entry_id)
    main(["link", "learning_a", "todo_x", "--type", "related"])
    main(["link", "learning_b", "learning_a", "--type", "related"])
    capsys.readouterr()

    assert main(["delete", "todo_x"]) == 0

    assert capsys.readouterr().out.splitlines() == ["deleted todo_x", "dangling: learning_a --related--> todo_x"]
    assert "todo_x" in _record(proj, "learning_a").read_text()  # reported, never removed by the delete
    assert main(["unlink", "learning_a", "todo_x"]) == 0
    assert main(["lint"]) == 0


def test_delete_dangling_edges_in_json(env, capsys):
    _add("--id", "todo_x", "--type", "todo", "--text", "x")
    _add("--id", "learning_a", "--type", "learning", "--text", "a")
    main(["link", "learning_a", "todo_x", "--type", "fixes"])
    capsys.readouterr()

    main(["delete", "--json", "todo_x"])

    dangling = [json.loads(line) for line in capsys.readouterr().out.splitlines()][1]
    assert (dangling["action"], dangling["source"], dangling["target"], dangling["type"]) == ("dangling", "learning_a", "todo_x", "fixes")


def test_delete_of_records_pointing_at_each_other_leaves_nothing_dangling(env, capsys):
    _add("--id", "todo_x", "--type", "todo", "--text", "x")
    _add("--id", "todo_y", "--type", "todo", "--text", "y")
    main(["link", "todo_x", "todo_y", "--type", "related"])
    main(["link", "todo_y", "todo_x", "--type", "related"])
    capsys.readouterr()

    assert main(["delete", "todo_x", "todo_y"]) == 0
    assert capsys.readouterr().out.splitlines() == ["deleted todo_x", "deleted todo_y"]


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


# --- move / context --map (chunk 1b-2) ---------------------------------------------------------

def _third(tmp_path):
    return _make_area(tmp_path / "ws" / "third")


def _seed_move(proj, other, third):
    _add("--id", "learning_m", "--type", "learning", "--text", "Moved.")
    _add("--id", "learning_local", "--type", "learning", "--text", "Stays.")
    _add("--id", "learning_ref", "--type", "learning", "--text", "Refers to moved.")
    _add("--area", str(other.root), "--id", "pattern_t", "--type", "pattern", "--text", "T.")
    _add("--area", str(third.root), "--id", "learning_far", "--type", "learning", "--text", "Far.")
    main(["link", "learning_m", "learning_local", "--type", "related"])
    main(["link", "learning_m", "pattern_t", "--type", "related", "--to-area", str(other.root)])
    main(["link", "learning_ref", "learning_m", "--type", "derived_from"])
    main(["link", "learning_far", "../proj:learning_m", "--type", "related", "--area", str(third.root)])


def test_move_round_trip_requalifies_and_rewrites_source_referrers(env, tmp_path, capsys):
    _, _, proj, other = env
    third = _third(tmp_path)
    _seed_move(proj, other, third)
    far_before = _tree(third.root)

    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 0
    out = capsys.readouterr().out

    assert not list(proj.records_dir.rglob("learning_m.md"))
    text = _record(other, "learning_m").read_text()
    assert "../proj:learning_local" in text and "pattern_t" in text and "../other:pattern_t" not in text
    assert resolve_ref(other, "../proj:learning_local") == (proj, "learning_local")
    assert "../other:learning_m" in _record(proj, "learning_ref").read_text()
    assert "learning_m" not in (proj.records_dir / "INDEX.md").read_text()
    assert "learning_m" in (other.records_dir / "INDEX.md").read_text()
    assert _tree(third.root) == far_before
    assert "report (not edited)" in out and "learning_far" in out


def test_move_dry_run_changes_nothing_and_lists_everything(env, tmp_path, capsys):
    _, _, proj, other = env
    third = _third(tmp_path)
    _seed_move(proj, other, third)
    before = (_tree(proj.root), _tree(other.root), _tree(third.root))

    assert main(["move", "learning_m", "--to-area", str(other.root), "--dry-run"]) == 0
    out = capsys.readouterr().out

    assert (_tree(proj.root), _tree(other.root), _tree(third.root)) == before
    assert out.count("would write") == 2 and "would delete" in out and "would rewrite edge" in out


def test_move_conflict_leaves_both_areas_unchanged(env, capsys):
    _, _, proj, other = env
    _add("--id", "learning_m", "--type", "learning", "--text", "Mine.")
    _add("--area", str(other.root), "--id", "learning_m", "--type", "learning", "--text", "Different.")
    before = (_tree(proj.root), _tree(other.root))

    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 1
    assert (_tree(proj.root), _tree(other.root)) == before
    assert "conflict learning_m" in capsys.readouterr().out


def test_move_refuses_to_overwrite_an_unreadable_target_file(env):
    _, _, proj, other = env
    _add("--id", "learning_m", "--type", "learning", "--text", "Mine.")
    broken = other.records_dir / "general" / "learnings" / "learning_m.md"
    broken.parent.mkdir(parents=True)
    broken.write_text("no frontmatter at all")
    before = (_tree(proj.root), _tree(other.root))

    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 1
    assert (_tree(proj.root), _tree(other.root)) == before


def test_move_refuses_symlinked_target_file_leaving_the_records_dir(env, tmp_path):
    _, _, proj, other = env
    _add("--id", "learning_m", "--type", "learning", "--text", "Mine.")
    outside = tmp_path / "outside.md"
    outside.write_text("untouched")
    link = other.records_dir / "general" / "learnings" / "learning_m.md"
    link.parent.mkdir(parents=True)
    link.symlink_to(outside)

    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 1
    assert _record(proj, "learning_m").is_file() and outside.read_text() == "untouched"


def test_move_together_keeps_mutual_edges_bare(env):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--id", "learning_b", "--type", "learning", "--text", "B.")
    main(["link", "learning_a", "learning_b", "--type", "related"])

    assert main(["move", "learning_a", "learning_b", "--to-area", str(other.root)]) == 0
    text = _record(other, "learning_a").read_text()
    assert "learning_b" in text and "../" not in text


def test_move_supersedes_across_areas_is_refused(env):
    _, _, proj, other = env
    _add("--id", "learning_old", "--type", "learning", "--text", "Old.")
    _add("--id", "learning_new", "--type", "learning", "--text", "New.")
    main(["link", "learning_new", "learning_old", "--type", "supersedes"])
    before = (_tree(proj.root), _tree(other.root))

    assert main(["move", "learning_new", "--to-area", str(other.root)]) == 1
    assert main(["move", "learning_old", "--to-area", str(other.root)]) == 1
    assert (_tree(proj.root), _tree(other.root)) == before


@pytest.mark.parametrize("bad", ["../x", "a/b", "*", "a:b", "current_focus"])
def test_move_hostile_ids_refused(env, bad):
    _, _, proj, other = env
    before = _tree(proj.root)
    assert main(["move", bad, "--to-area", str(other.root)]) == 2
    assert _tree(proj.root) == before


def test_move_same_area_missing_id_and_pending_guard(env):
    _, db, proj, other = env
    assert main(["move", "learning_zz", "--to-area", str(other.root)]) == 1
    assert main(["move", "learning_zz", "--to-area", str(proj.root)]) == 2
    (db / "chroma.sqlite3").write_text("")
    assert main(["move", "learning_zz", "--to-area", str(other.root)]) == 3


def test_context_map_aggregates_cross_area_edges_and_unresolved(env, tmp_path, capsys):
    _, _, proj, other = env
    third = _third(tmp_path)
    _seed_move(proj, other, third)
    _add("--area", str(other.root), "--id", "pattern_gone", "--type", "pattern", "--text", "G.")
    main(["link", "learning_ref", "pattern_gone", "--type", "related", "--to-area", str(other.root)])
    main(["delete", "pattern_gone", "--area", str(other.root)])
    capsys.readouterr()

    root = str(tmp_path / "ws")
    assert main(["context", "--map", "--root", root]) == 0
    out = capsys.readouterr().out
    assert "proj → other: 1 (related)" in out
    assert "third → proj: 1 (related)" in out
    assert "unresolved: proj:learning_ref --related--> ../other:pattern_gone" in out

    assert main(["context", "--map", "--root", root, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert {(e["from"], e["to"], e["count"]) for e in data["edges"]} == {
        (str(proj.root), str(other.root), 1), (str(third.root), str(proj.root), 1)}
    assert len(data["unresolved"]) == 1


def test_context_map_lists_malformed_edges_as_unresolved(env, monkeypatch, capsys):
    from ai_mem import mem_cli

    _, _, proj, _ = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    real = mem_cli._repository()

    class Corrupt:  # mock: one entry carries a stored edges field that is not valid JSON
        def get_all(self, key):
            entries = real.get_all(key)
            for entry in entries:
                entry.metadata["edges"] = "{not json"
            return entries

        def get_by_ids(self, key, ids):
            return real.get_by_ids(key, ids)

    monkeypatch.setattr(mem_cli, "_repository", lambda: Corrupt())
    assert main(["context", "--map", "--root", str(proj.root)]) == 0
    assert "<malformed edges field>" in capsys.readouterr().out


def test_move_requires_scan_root_when_areas_only_share_home_or_above(env, tmp_path, monkeypatch):
    _, _, proj, other = env
    _add("--id", "learning_m", "--type", "learning", "--text", "Mine.")
    monkeypatch.setenv("HOME", str(tmp_path / "ws"))
    before = (_tree(proj.root), _tree(other.root))

    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 2
    assert main(["move", "learning_m", "--to-area", str(other.root), "--scan-root", str(tmp_path / "ws"), "--dry-run"]) == 0
    assert (_tree(proj.root), _tree(other.root)) == before


def _hand_index(area):
    (area.records_dir / "INDEX.md").write_text("# Hand-kept\n\n- [[learning_x]] with a link\n")


@pytest.mark.parametrize("argv", [
    ["add", "--id", "learning_new", "--type", "learning", "--text", "N."],
    ["add", "--id", "learning_x", "--cue", "when"],
    ["link", "learning_x", "learning_y", "--type", "related"],
    ["delete", "learning_x"],
])
def test_hand_kept_index_refuses_every_write_and_changes_nothing(env, capsys, argv):
    tmp_path, _, proj, _ = env
    _add("--id", "learning_x", "--type", "learning", "--text", "X.")
    _add("--id", "learning_y", "--type", "learning", "--text", "Y.")
    _hand_index(proj)
    before = _tree(tmp_path)
    assert main(argv) == 1
    err = capsys.readouterr().err
    assert "hand-kept" in err and "mem lint --fix" in err
    assert _tree(tmp_path) == before


def test_missing_index_is_not_hand_kept(env):
    _, _, proj, _ = env
    assert _add("--id", "learning_x", "--type", "learning", "--text", "X.") == 0
    (proj.records_dir / "INDEX.md").unlink()
    assert _add("--id", "learning_y", "--type", "learning", "--text", "Y.") == 0


def test_current_focus_is_exempt(env):
    _, _, proj, _ = env
    _add("--id", "learning_x", "--type", "learning", "--text", "X.")
    _hand_index(proj)
    assert _add("--id", "current_focus", "--text", "Now.") == 0
    assert main(["delete", "current_focus"]) == 0
    assert (proj.records_dir / "INDEX.md").read_text().startswith("# Hand-kept")


def test_lint_fix_adopts_the_area_and_the_write_then_succeeds(env):
    _, _, proj, _ = env
    _add("--id", "learning_x", "--type", "learning", "--text", "X.")
    _hand_index(proj)
    assert _add("--id", "learning_y", "--type", "learning", "--text", "Y.") == 1
    assert main(["lint", "--fix", "--area", str(proj.root)]) == 0
    assert _add("--id", "learning_y", "--type", "learning", "--text", "Y.") == 0


def test_move_into_hand_kept_target_or_out_of_hand_kept_source_is_refused(env, capsys):
    tmp_path, _, proj, other = env
    _add("--id", "learning_m", "--type", "learning", "--text", "M.")
    _add("--area", str(other.root), "--id", "pattern_t", "--type", "pattern", "--text", "T.")
    _hand_index(other)
    before = _tree(tmp_path)
    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 1
    assert main(["move", "learning_m", "--to-area", str(other.root), "--dry-run"]) == 1
    assert "hand-kept" in capsys.readouterr().err
    assert _tree(tmp_path) == before
    (other.records_dir / "INDEX.md").unlink()
    _hand_index(proj)
    before = _tree(tmp_path)
    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 1
    assert _tree(tmp_path) == before


def test_move_ignores_a_hand_kept_third_area(env):
    tmp_path, _, proj, other = env
    third = _third(tmp_path)
    _add("--id", "learning_m", "--type", "learning", "--text", "M.")
    _add("--area", str(third.root), "--id", "learning_far", "--type", "learning", "--text", "Far.")
    _hand_index(third)
    assert main(["move", "learning_m", "--to-area", str(other.root)]) == 0
    assert (third.records_dir / "INDEX.md").read_text().startswith("# Hand-kept")


def test_pending_migration_beats_the_index_check(env):
    _, db, proj, _ = env
    (db / "chroma.sqlite3").write_bytes(b"x")
    _hand_index(proj)
    assert _add("--id", "learning_x", "--type", "learning", "--text", "X.") == 3


# --- mem find -------------------------------------------------------------------------------------------

def _write_record(area, entry_id, kind="learnings"):
    path = area.records_dir / "general" / kind / f"{entry_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nid: {entry_id}\ntype: learning\narea: general\ncreated: 2026-01-01\n---\ntext\n")
    return path


def test_find_hit_in_home_area_is_a_bare_id(env, capsys):
    _, _, proj, _ = env
    path = _write_record(proj, "x_home")
    assert main(["find", "x_home"]) == 0
    assert capsys.readouterr().out.strip() == f"x_home  {path.resolve()}"


def test_find_hit_in_ancestor_area(env, capsys):
    tmp, _, proj, _ = env
    outer = _make_area(tmp / "ws")
    path = _write_record(outer, "x_outer")
    assert main(["find", "x_outer", "--root", str(proj.root)]) == 0
    assert capsys.readouterr().out.strip() == f"..:x_outer  {path.resolve()}"


def test_find_hit_in_sibling_area(env, capsys):
    _, _, proj, other = env
    _write_record(other, "x_sib")
    assert main(["find", "x_sib"]) == 0
    assert capsys.readouterr().out.split("  ")[0] == "../other:x_sib"


def test_find_hit_in_reference_doc(env, capsys):
    _, _, proj, other = env
    doc = other.records_dir.parent / "reference" / "x_ref.md"
    doc.parent.mkdir()
    doc.write_text("plain doc\n")
    assert main(["find", "x_ref"]) == 0
    assert capsys.readouterr().out.strip() == f"../other:x_ref  {doc.resolve()}"


def test_find_lists_all_hits_home_first(env, capsys):
    _, _, proj, other = env
    _write_record(other, "x_dup")
    _write_record(proj, "x_dup")
    assert main(["find", "x_dup", "--json"]) == 0
    refs = [json.loads(line)["ref"] for line in capsys.readouterr().out.splitlines()]
    assert refs == ["x_dup", "../other:x_dup"]


def test_find_none_exits_1_and_counts_areas(env, capsys):
    assert main(["find", "x_nothing"]) == 1
    assert capsys.readouterr().out.strip() == "not found in 2 areas"


def test_find_root_comes_from_workspace_root_env(env, capsys, monkeypatch):
    tmp, _, proj, _ = env
    far = _make_area(tmp / "elsewhere" / "far")
    _write_record(far, "x_far")
    assert main(["find", "x_far"]) == 1
    capsys.readouterr()
    monkeypatch.setenv("AI_MEM_WORKSPACE_ROOT", str(tmp))
    assert main(["find", "x_far"]) == 0
    assert capsys.readouterr().out.startswith("../../elsewhere/far:x_far")


@pytest.mark.parametrize("bad", ["..", "../x", "a/b", "a:b", "x\ny", "*", "INDEX", " x"])
def test_find_refuses_hostile_ids(env, capsys, bad):
    assert main(["find", bad]) == 2
    assert capsys.readouterr().out == ""


def test_find_skips_symlink_leaving_the_records_dir_and_writes_nothing(env, capsys):
    tmp, _, proj, other = env
    secret = tmp / "secret.md"
    secret.write_text("secret\n")
    link = other.records_dir / "general" / "learnings" / "x_link.md"
    link.parent.mkdir(parents=True)
    link.symlink_to(secret)
    before = _tree(tmp)
    assert main(["find", "x_link"]) == 1
    assert _tree(tmp) == before


def test_link_error_names_where_a_missing_target_lives(env, capsys):
    _, _, proj, other = env
    _write_record(proj, "x_src")
    _write_record(other, "x_elsewhere")
    assert main(["link", "x_src", "x_elsewhere", "--type", "related"]) == 1
    err = capsys.readouterr().err
    assert "not in this area; found at ../other:x_elsewhere" in err


def test_link_error_says_found_nowhere(env, capsys):
    _, _, proj, _ = env
    _write_record(proj, "x_src")
    assert main(["link", "x_src", "x_ghost", "--type", "related"]) == 1
    assert "found nowhere" in capsys.readouterr().err


def test_find_walks_nested_areas_up_to_the_root_skipping_area_less_dirs(env, capsys):
    tmp, _, _, _ = env
    top = _make_area(tmp / "n")
    mid = _make_area(tmp / "n" / "b")
    leaf = _make_area(tmp / "n" / "b" / "plain" / "c")
    for area, entry_id in ((top, "x_top"), (mid, "x_mid")):
        _write_record(area, entry_id)
    for entry_id, ref in (("x_mid", "../..:x_mid"), ("x_top", "../../..:x_top")):
        assert main(["find", entry_id, "--area", str(leaf.root), "--root", str(top.root)]) == 0
        assert capsys.readouterr().out.startswith(ref)


def test_find_never_searches_above_the_root(env, capsys):
    tmp, _, _, _ = env
    above = _make_area(tmp / "m")
    _write_record(above, "x_above")
    root = _make_area(tmp / "m" / "r")
    leaf = _make_area(tmp / "m" / "r" / "leaf")
    assert main(["find", "x_above", "--area", str(leaf.root), "--root", str(root.root)]) == 1
    assert main(["find", "x_above", "--area", str(leaf.root), "--root", str(above.root)]) == 0
    capsys.readouterr()
    outside = _make_area(tmp / "elsewhere")
    _write_record(outside, "x_out")
    assert main(["find", "x_out", "--area", str(leaf.root), "--root", str(root.root)]) == 1


def test_find_lists_only_top_level_reference_docs(env):
    _, _, proj, other = env
    nested = other.records_dir.parent / "reference" / "sub" / "x_deep.md"
    nested.parent.mkdir(parents=True)
    nested.write_text("doc\n")
    assert main(["find", "x_deep"]) == 1


def test_link_hint_only_when_the_target_is_the_problem(env, capsys):
    _, _, proj, other = env
    _write_record(proj, "x_t")
    assert main(["link", "x_ghost_src", "x_t", "--type", "related"]) == 1
    assert "found at" not in capsys.readouterr().err


# --- move --batch (chunk 5x-a) ------------------------------------------------------------------

def _batch_file(tmp_path, *rows, name="batch.tsv"):
    path = tmp_path / name
    path.write_text("\n".join(rows) + "\n")
    return str(path)


def _row(source, entry_id, target, perspective=""):
    return "\t".join([str(source.root), entry_id, str(target.root), perspective])


def _stored_edges(area, entry_id):
    text = _record(area, entry_id).read_text()
    (line,) = [l for l in text.splitlines() if l.startswith("edges:")]
    return {(e["target_id"], e["edge_type"]) for e in json.loads(line.removeprefix("edges:").strip())}


def _seed_batch(env, tmp_path):
    """proj: a, b, user_u, stays (stays -> a); other: o (o -> ../proj:a); third: t, bystander (bystander -> ../proj:a)."""
    _, _, proj, other = env
    third, fourth = _third(tmp_path), _make_area(tmp_path / "ws" / "fourth")
    for area, entry_id, kind in ((proj, "learning_a", "learning"), (proj, "learning_b", "learning"), (proj, "user_u", "user"),
                                 (proj, "learning_stays", "learning"), (other, "learning_o", "learning"),
                                 (third, "learning_t", "learning"), (third, "learning_bystander", "learning")):
        _add("--area", str(area.root), "--id", entry_id, "--type", kind, "--text", f"{entry_id} text.")
    main(["link", "learning_a", "learning_b", "--type", "related"])
    main(["link", "learning_b", "../third:learning_t", "--type", "related"])
    main(["link", "learning_stays", "learning_a", "--type", "derived_from"])
    main(["link", "learning_o", "../proj:learning_a", "--type", "related", "--area", str(other.root)])
    main(["link", "learning_bystander", "../proj:learning_a", "--type", "related", "--area", str(third.root)])
    return third, fourth


def test_batch_moves_across_sources_and_targets_with_final_edges(env, tmp_path, capsys):
    _, _, proj, other = env
    third, fourth = _seed_batch(env, tmp_path)
    main(["link", "learning_t", "../proj:learning_b", "--type", "related", "--area", str(third.root)])
    batch = _batch_file(tmp_path, _row(proj, "learning_a", other, "tooling"), _row(proj, "learning_b", fourth),
                        _row(third, "learning_t", other), _row(proj, "user_u", other, "ignored"))
    bystander_before = _record(third, "learning_bystander").read_text()
    o_before = _record(other, "learning_o").read_text()

    assert main(["move", "--batch", batch]) == 0

    # a -> other, b -> fourth, t -> other: edges written against the final locations, in either direction
    assert _stored_edges(other, "learning_a") == {("../fourth:learning_b", "related")}
    assert _stored_edges(fourth, "learning_b") == {("../other:learning_t", "related")}
    assert _stored_edges(other, "learning_t") == {("../fourth:learning_b", "related")}
    # referrer inside a source area is rewritten to the final location
    assert _stored_edges(proj, "learning_stays") == {("../other:learning_a", "derived_from")}
    # a source area (third) is also rewritten: nothing references moved records there except t's neighbours
    assert _record(third, "learning_bystander").read_text() != bystander_before
    assert _stored_edges(third, "learning_bystander") == {("../other:learning_a", "related")}
    # a non-source, pre-existing target record is only reported
    assert _record(other, "learning_o").read_text() == o_before
    assert "perspective: tooling" in _record(other, "learning_a").read_text()
    assert "perspective: user" in _record(other, "user_u").read_text()
    for area, moved in ((proj, "learning_a"), (proj, "learning_b"), (third, "learning_t"), (proj, "user_u")):
        assert not list(area.records_dir.rglob(f"{moved}.md"))


def test_batch_reports_referrers_outside_the_source_areas_and_never_edits_them(env, tmp_path, capsys):
    _, _, proj, other = env
    third, fourth = _seed_batch(env, tmp_path)
    capsys.readouterr()
    before = {key: _tree(area.root) for key, area in (("other", other), ("third", third), ("fourth", fourth))}

    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", fourth)), "--scan-root", str(tmp_path / "ws")]) == 0

    out = capsys.readouterr().out
    assert "report (not edited) " + str(other.root) + ":learning_o" in out
    assert _tree(other.root) == before["other"]
    assert _tree(third.root) == before["third"]  # not a source area of this batch: reported only
    assert "report (not edited) " + str(third.root) + ":learning_bystander" in out


def test_batch_dry_run_changes_nothing_and_prints_the_plan(env, tmp_path, capsys):
    _, _, proj, other = env
    _seed_batch(env, tmp_path)
    before = _tree(tmp_path / "ws")
    capsys.readouterr()

    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other), _row(proj, "learning_b", other)), "--dry-run"]) == 0

    assert _tree(tmp_path / "ws") == before
    out = capsys.readouterr().out
    assert "would write" in out and "would delete" in out and "would rewrite edge" in out


def test_batch_supersede_pair_moves_together_but_never_split(env, tmp_path, capsys):
    _, _, proj, other = env
    third, _ = _seed_batch(env, tmp_path)
    main(["link", "learning_a", "learning_b", "--type", "supersedes"])
    before = _tree(tmp_path / "ws")

    # one end only, or the two ends to different targets: refused, nothing changes
    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other))]) == 1
    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other), _row(proj, "learning_b", third))]) == 1
    assert _tree(tmp_path / "ws") == before

    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other), _row(proj, "learning_b", other))]) == 0
    assert ("learning_b", "supersedes") in _stored_edges(other, "learning_a")


def test_batch_refuses_reference_docs_and_a_differing_record_in_the_target(env, tmp_path, capsys):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--area", str(other.root), "--id", "learning_a", "--type", "learning", "--text", "Different.")
    ref = proj.root / "docs" / "reference"
    ref.mkdir()
    (ref / "ref_doc.md").write_text("---\ntype: reference\n---\nA reference doc.\n")
    before = _tree(tmp_path / "ws")

    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other))]) == 1
    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "ref_doc", other))]) == 1
    assert _tree(tmp_path / "ws") == before
    assert "not records" in capsys.readouterr().out


def test_batch_rerun_is_idempotent_and_resumes_an_interrupted_run(env, tmp_path, capsys):
    _, _, proj, other = env
    third, _ = _seed_batch(env, tmp_path)
    batch = _batch_file(tmp_path, _row(proj, "learning_a", other, "tooling"), _row(proj, "learning_b", third))

    # interrupted run: the arrivals landed in the targets, the source rewrites and deletes did not
    backup = tmp_path / "proj-before"
    shutil.copytree(proj.records_dir, backup)
    assert main(["move", "--batch", batch]) == 0
    expected = _tree(tmp_path / "ws")
    shutil.rmtree(proj.records_dir)
    shutil.copytree(backup, proj.records_dir)
    assert main(["move", "--batch", batch]) == 0
    assert _tree(tmp_path / "ws") == expected
    assert not list(proj.records_dir.rglob("learning_a.md"))

    # a finished batch run again: all rows are done, nothing changes
    capsys.readouterr()
    snapshot = _tree(tmp_path / "ws")
    assert main(["move", "--batch", batch]) == 0
    assert _tree(tmp_path / "ws") == snapshot
    assert capsys.readouterr().out.count("done learning_") == 2


def test_batch_row_validation(env, tmp_path, capsys):
    _, _, proj, other = env
    _seed_batch(env, tmp_path)
    before = _tree(tmp_path / "ws")
    bad_rows = {
        "too few columns": f"{proj.root}\tlearning_a",
        "too many columns": _row(proj, "learning_a", other, "x") + "\textra",
        "empty id": _row(proj, "", other),
        "hostile id": _row(proj, "../../x", other),
        "qualified id": _row(proj, "a:b", other),
        "same area": _row(proj, "learning_a", proj),
        "not an area": f"{tmp_path}\tlearning_a\t{other.root}",
        "bad perspective": _row(proj, "learning_a", other, "Not Safe"),
        "focus": _row(proj, "current_focus", other),
    }
    for name, row in bad_rows.items():
        assert main(["move", "--batch", _batch_file(tmp_path, row)]) == 2, name
    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other), _row(proj, "learning_a", other))]) == 2
    third = tmp_path / "ws" / "third"
    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other), f"{third}\tlearning_a\t{other.root}")]) == 2
    assert main(["move", "--batch", _batch_file(tmp_path, "# only a comment", "")]) == 2
    assert main(["move", "--batch", str(tmp_path / "missing.tsv")]) == 2
    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other)), "learning_b"]) == 2
    assert _tree(tmp_path / "ws") == before


def test_batch_comments_blank_lines_and_relative_paths(env, tmp_path):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")

    batch = tmp_path / "ws" / "batch.tsv"
    batch.write_text("# header\n\nproj\tlearning_a\tother\n")

    assert main(["move", "--batch", str(batch)]) == 0
    assert _record(other, "learning_a")


def test_batch_unknown_id_aborts_before_anything_is_written(env, tmp_path, capsys):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    before = _tree(tmp_path / "ws")

    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other), _row(proj, "learning_zz", other))]) == 1

    assert _tree(tmp_path / "ws") == before
    assert "not found learning_zz" in capsys.readouterr().out


def test_batch_into_hand_kept_target_is_refused(env, tmp_path, capsys):
    _, _, proj, other = env
    _add("--id", "learning_a", "--type", "learning", "--text", "A.")
    _add("--area", str(other.root), "--id", "pattern_t", "--type", "pattern", "--text", "T.")
    _hand_index(other)
    before = _tree(tmp_path / "ws")

    assert main(["move", "--batch", _batch_file(tmp_path, _row(proj, "learning_a", other)), "--dry-run"]) == 1

    assert "hand-kept" in capsys.readouterr().err
    assert _tree(tmp_path / "ws") == before
