"""Tests for `mem lint` (synthetic fixtures; one per drift kind, plus the preservation guarantees)."""
from __future__ import annotations

import json

import pytest

from ai_mem import records_lint
from ai_mem.infrastructure.areas import find_area
from ai_mem.mem_cli import main


def _area(path):
    (path / "docs" / "records").mkdir(parents=True)
    return find_area(path)


def _write(area, rel, text):
    path = area.records_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _record(entry_id="learning_a", entry_type="learning", topic="general", extra="", body="Observed: x\n"):
    return f"id: {entry_id}\ntype: {entry_type}\ntopic: {topic}\ncreated: 1.0\n{extra}---\n\n{body}"


def _codes(area):
    return sorted({f.code for f in records_lint.lint(area)})


def _clean_area(tmp_path):
    area = _area(tmp_path / "a")
    _write(area, "general/learnings/learning_a.md", _record())
    main(["lint", "--fix", "--area", str(area.root)])
    assert records_lint.lint(area) == []
    return area


def test_clean_area_has_no_findings(tmp_path):
    _clean_area(tmp_path)


@pytest.mark.parametrize("text,code", [
    ("no frontmatter at all\n", "unparsable"),
    ("id: x\nthis line has no colon\n---\n\nbody\n", "unparsable"),
    ("id: x\nid: y\n---\n\nbody\n", "unparsable"),
    ("**id:** learning_a\n---\n\nbody\n", "unparsable"),
])
def test_unparsable_frontmatter(tmp_path, text, code):
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_b.md", text)
    assert code in _codes(area)


def test_missing_required_fields_and_fixability(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_b.md", "id: learning_b\ntype: learning\n---\n\nObserved: x\n")
    _write(area, "general/learnings/learning_c.md", "type: learning\ntopic: general\ncreated: 1.0\n---\n\nObserved: x\n")
    by_file = {(f.file.name, f.message): f.fixable for f in records_lint.lint(area) if f.code == "missing-field"}
    assert by_file[("learning_b.md", "required field 'topic' is missing")] is True
    assert by_file[("learning_b.md", "required field 'created' is missing")] is True
    assert by_file[("learning_c.md", "required field 'id' is missing")] is False


def test_id_stem_colon_and_control_characters(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_b.md", _record("learning_other"))
    _write(area, "general/learnings/learning_c:d.md", _record("learning_c:d"))
    _write(area, "general/learnings/learning_e\nf.md", _record("learning_e"))
    codes = _codes(area)
    assert {"id-stem", "id-colon", "id-chars"} <= set(codes)


def test_value_with_control_character_is_flagged_and_never_fixed(tmp_path):
    area = _clean_area(tmp_path)
    path = _write(area, "general/learnings/learning_b.md", _record("learning_b", extra="note: a\x0bb\n"))
    assert "value-chars" in _codes(area)
    before = path.read_bytes()
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_bytes() == before


def test_type_and_folder_mismatches(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_b.md", _record("learning_b", "domain"))
    _write(area, "general/learnings/learning_c.md", _record("learning_c", topic="other"))
    _write(area, "general/learnings/learning_d.md", _record("learning_d", "bogus"))
    _write(area, "learning_e.md", _record("learning_e"))
    assert {"type-folder", "topic-folder", "type-invalid", "layout"} <= set(_codes(area))


def test_retired_todo_type_points_to_focus_and_backlog(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/todos/todo_x.md", _record("todo_x", "todo"))
    assert "type-invalid" in _codes(area)


def test_bad_number(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_b.md", _record("learning_b").replace("created: 1.0", "created: 2026-10-10"))
    assert "bad-number" in _codes(area)


def test_edges_checks(tmp_path):
    area = _clean_area(tmp_path)
    other = _area(tmp_path / "other")
    _write(other, "general/learnings/learning_o.md", _record("learning_o"))
    main(["lint", "--fix", "--area", str(other.root)])
    edges = [
        {"target_id": "learning_a", "edge_type": "related"},
        {"target_id": "learning_missing", "edge_type": "related"},
        {"target_id": "learning_a", "edge_type": "bogus"},
        {"target_id": "../other:learning_o", "edge_type": "related"},
        {"target_id": "../other:learning_gone", "edge_type": "related"},
        {"target_id": "../nowhere:learning_o", "edge_type": "related"},
        {"target_id": "/abs/other:learning_o", "edge_type": "related"},
        {"target_id": "~/x:learning_o", "edge_type": "related"},
    ]
    _write(area, "general/learnings/learning_b.md", _record("learning_b", extra=f"edges: {json.dumps(edges)}\n"))
    _write(area, "general/learnings/learning_c.md", _record("learning_c", extra="edges: not json\n"))
    messages = {f.code: f.message for f in records_lint.lint(area)}
    assert {"edge-dangling", "edge-type", "edge-dangling-xarea", "edge-unresolved", "edge-target-invalid", "edges-json"} <= set(messages)
    findings = [f for f in records_lint.lint(area) if f.file.name == "learning_b.md"]
    assert not any("learning_o'" in f.message and f.code == "edge-dangling-xarea" and "gone" not in f.message for f in findings)


def test_fix_repoints_edges_whose_id_lives_in_exactly_one_area(tmp_path):
    area = _clean_area(tmp_path)
    for name, ids in (("moved/deeper", ["learning_m"]), ("one", ["learning_twice"]), ("two", ["learning_twice"])):
        other = _area(tmp_path / name)
        for entry_id in ids:
            _write(other, f"general/learnings/{entry_id}.md", _record(entry_id))
        main(["lint", "--fix", "--area", str(other.root)])
    edges = [
        {"target_id": "../moved:learning_m", "edge_type": "confirms"},      # area moved one level down
        {"target_id": "learning_m", "edge_type": "related"},                # bare id, lives elsewhere
        {"target_id": "../one:learning_a", "edge_type": "derived_from"},    # lives in this very area
        {"target_id": "../x:learning_twice", "edge_type": "related"},       # ambiguous: two areas
        {"target_id": "learning_nowhere", "edge_type": "related"},          # in no area
    ]
    path = _write(area, "general/learnings/learning_b.md", _record("learning_b", extra=f"edges: {json.dumps(edges)}\n", body="Body\n"))
    main(["lint", "--fix", "--area", str(area.root)])
    text = path.read_text()
    assert [e["target_id"] for e in json.loads(text.split("edges: ", 1)[1].split("\n", 1)[0])] == [
        "../moved/deeper:learning_m", "../moved/deeper:learning_m", "learning_a", "../x:learning_twice", "learning_nowhere"]
    assert [e["edge_type"] for e in json.loads(text.split("edges: ", 1)[1].split("\n", 1)[0])] == [e["edge_type"] for e in edges]
    assert text.endswith("---\n\nBody\n")
    assert sorted(f.message for f in records_lint.lint(area) if f.code.startswith("edge")) == [
        "edge target '../x:learning_twice' points at no area", "edge target 'learning_nowhere' does not exist in this area"]


def test_user_record_needs_perspective_user(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/user/user_a.md", _record("user_a", "user"))
    _write(area, "general/user/user_b.md", _record("user_b", "user", extra="perspective: agent\n"))
    flagged = {f.file.name: f.fixable for f in records_lint.lint(area) if f.code == "perspective-user"}
    assert flagged == {"user_a.md": True, "user_b.md": False}


def test_index_missing_and_stale_are_fixable(tmp_path):
    area = _clean_area(tmp_path)
    index = area.records_dir / "INDEX.md"
    index.write_text("# Records Index\n\n| [learning_a](x.md) | hand written |\n")
    assert [(f.code, f.fixable) for f in records_lint.lint(area)] == [("index-stale", True)]
    index.unlink()
    assert [(f.code, f.fixable) for f in records_lint.lint(area)] == [("index-missing", True)]
    assert main(["lint", "--fix", "--area", str(area.root)]) == 0
    assert records_lint.lint(area) == []


def test_symlinked_record_is_reported_not_read_or_written(tmp_path):
    area = _clean_area(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("---\nid: learning_x\ntype: learning\n---\nOutside\n")
    link = area.records_dir / "general" / "learnings" / "learning_x.md"
    link.symlink_to(outside)
    assert "unparsable" in _codes(area)
    main(["lint", "--fix", "--area", str(area.root)])
    assert outside.read_text() == "---\nid: learning_x\ntype: learning\n---\nOutside\n"
    assert link.is_symlink()


DRIFTED = "---\nlearning: yes\ntype: learning\nid: learning_b\nnote: keep me\n---\nObserved: **bold** label\n\n---\nstill body\n"


def test_fix_normalises_shape_and_preserves_everything(tmp_path):
    area = _clean_area(tmp_path)
    path = _write(area, "general/learnings/learning_b.md", DRIFTED)
    assert {"frontmatter-shape", "missing-field"} <= set(_codes(area))
    assert main(["lint", "--fix", "--area", str(area.root)]) == 0
    fixed = path.read_text()
    body = "Observed: **bold** label\n\n---\nstill body\n"
    assert fixed.endswith("---\n\n" + body)
    fields = dict(line.partition(": ")[::2] for line in fixed.split("\n---\n\n")[0].splitlines())
    assert fields["learning"] == "yes" and fields["note"] == "keep me"
    assert fields["topic"] == "general" and float(fields["created"]) > 0
    assert list(fields)[:3] == ["id", "type", "topic"]
    assert list(fields)[-2:] == ["learning", "note"]


def test_fix_is_idempotent_and_prints_each_change(tmp_path, capsys):
    area = _clean_area(tmp_path)
    path = _write(area, "general/learnings/learning_b.md", DRIFTED)
    capsys.readouterr()
    main(["lint", "--fix", "--area", str(area.root)])
    out = capsys.readouterr().out
    assert "fixed docs/records/general/learnings/learning_b.md" in out and "regenerated" in out
    first = path.read_text()
    main(["lint", "--fix", "--area", str(area.root)])
    assert "fixed" not in capsys.readouterr().out
    assert path.read_text() == first


def test_fix_fills_user_perspective_and_keeps_cue_last(tmp_path):
    area = _clean_area(tmp_path)
    path = _write(area, "general/user/user_a.md", _record("user_a", "user", extra="cue: when x\nextra: 1\n"))
    main(["lint", "--fix", "--area", str(area.root)])
    lines = path.read_text().split("\n---\n\n")[0].splitlines()
    assert "perspective: user" in lines and lines[-1] == "cue: when x" and lines[-2] == "extra: 1"


def test_preservation_guard_refuses_unsafe_rewrite(tmp_path, monkeypatch):
    area = _clean_area(tmp_path)
    path = _write(area, "general/learnings/learning_b.md", DRIFTED)
    before = path.read_bytes()
    monkeypatch.setattr(records_lint, "_canonical", lambda *args: "id: learning_b\ntype: learning\n---\n\nlost\n")
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_bytes() == before


def test_fix_does_not_write_outside_the_area(tmp_path):
    area = _clean_area(tmp_path)
    other = _area(tmp_path / "other")
    foreign = _write(other, "general/learnings/learning_f.md", DRIFTED)
    before = foreign.read_bytes()
    main(["lint", "--fix", "--area", str(area.root)])
    assert foreign.read_bytes() == before


def test_no_area_is_a_usage_error(tmp_path, capsys):
    assert main(["lint", "--area", str(tmp_path)]) == 2


def test_fix_keeps_crlf_and_lone_cr_body_bytes(tmp_path):
    area = _clean_area(tmp_path)
    path = area.records_dir / "general" / "learnings" / "learning_b.md"
    body = b"line1\r\nline2\rlone\r\n"
    path.write_bytes(b"---\r\nid: learning_b\r\ntype: learning\r\nfoo: bar\r\n---\r\n" + body)
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_bytes().endswith(b"---\n\n\r\nline1\r\nline2\rlone\r\n") or path.read_bytes().endswith(b"---\n\n" + body)
    assert body in path.read_bytes()


def test_zero_width_joiner_in_value_is_not_a_control_character(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_b.md", _record("learning_b", extra="note: a‍b\n"))
    assert "value-chars" not in _codes(area)


def test_key_order_matches_what_serialize_writes():
    from ai_mem.infrastructure import adr_markdown
    metadata = {"area": "general", "perspective": "user", "created_at": 1.0, "superseded_by": "x", "valid_until": 2.0,
                "edges": [{"target_id": "t", "edge_type": "related"}], "cue": "c"}
    text = adr_markdown.serialize("i", "user", "body", metadata)
    keys = [line.partition(":")[0] for line in text.split("\n---\n\n")[0].splitlines()]
    assert tuple(keys[:-1]) == adr_markdown.KEY_ORDER and keys[-1] == "cue"


def test_render_index_equals_what_regenerate_index_writes(tmp_path):
    from ai_mem.infrastructure.adr_index import regenerate_index, render_index
    area = _clean_area(tmp_path)
    _write(area, "general/learnings/learning_bad.md", "garbage")
    regenerate_index(area.records_dir)
    assert render_index(area.records_dir, report_skipped=False) == (area.records_dir / "INDEX.md").read_text()


def test_edge_to_a_reference_doc_is_not_dangling(tmp_path):
    area = _clean_area(tmp_path)
    (area.records_dir.parent / "reference").mkdir()
    (area.records_dir.parent / "reference" / "key_invariants.md").write_text("# Key invariants\n", encoding="utf-8")
    edges = [{"target_id": "key_invariants", "edge_type": "related"}]
    _write(area, "general/learnings/learning_b.md", _record("learning_b", extra=f"edges: {json.dumps(edges)}\n"))
    assert "edge-dangling" not in {f.code for f in records_lint.lint(area)}


def test_edge_to_a_source_is_not_dangling(tmp_path):
    area = _clean_area(tmp_path)
    (area.records_dir.parent / "sources").mkdir()
    (area.records_dir.parent / "sources" / "measured.md").write_text("---\nstatus: unprocessed\n---\n", encoding="utf-8")
    edges = [{"target_id": "measured", "edge_type": "derived_from"}]
    _write(area, "general/learnings/learning_b.md", _record("learning_b", extra=f"edges: {json.dumps(edges)}\n"))
    assert "edge-dangling" not in {f.code for f in records_lint.lint(area)}


LEGACY = "id: learning_b\ntype: learning\narea: general\ncreated: 1.0\nedges: []\n---\n\nObserved: x\r\nCause: y\n"


def test_legacy_area_key_is_a_fixable_finding_and_fix_changes_only_the_key(tmp_path):
    area = _clean_area(tmp_path)
    path = _write(area, "general/learnings/learning_b.md", LEGACY)
    findings = [f for f in records_lint.lint(area) if f.file == path]
    assert [(f.code, f.fixable) for f in findings] == [("legacy-topic-key", True)]
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_bytes() == LEGACY.replace("area: general", "topic: general").encode()
    assert records_lint.lint(area) == []


def test_legacy_key_with_equal_topic_drops_the_old_line(tmp_path):
    area = _clean_area(tmp_path)
    text = "id: learning_b\ntype: learning\ntopic: general\narea: general\ncreated: 1.0\n---\n\nObserved: x\n"
    path = _write(area, "general/learnings/learning_b.md", text)
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_text() == text.replace("area: general\n", "")


def test_conflicting_topic_and_area_is_a_finding_that_fix_refuses(tmp_path):
    area = _clean_area(tmp_path)
    text = "id: learning_b\ntype: learning\ntopic: general\narea: other\ncreated: 1.0\n---\n\nObserved: x\n"
    path = _write(area, "general/learnings/learning_b.md", text)
    assert "topic-conflict" in {f.code for f in records_lint.lint(area) if f.file == path}
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_text() == text


def test_backlog_numbering_and_blank_lines_are_fixed_in_order(tmp_path):
    area = _clean_area(tmp_path)
    backlog = _write(area, "BACKLOG.md", "Ordered.\nSecond header line.\n\n1. first (todo_a)\n\n2) second\n* third\n-   fourth\n")
    assert _codes(area) == ["backlog-format"]
    main(["lint", "--fix", "--area", str(area.root)])
    assert backlog.read_text() == "Ordered.\nSecond header line.\n\n- first (todo_a)\n- second\n- third\n- fourth\n"
    assert records_lint.lint(area) == []


def test_backlog_without_header_and_canonical_backlog_are_clean(tmp_path):
    area = _clean_area(tmp_path)
    _write(area, "BACKLOG.md", "- first\n- second\n")
    assert records_lint.lint(area) == []


def test_backlog_section_heading_is_reported_not_fixed(tmp_path):
    area = _clean_area(tmp_path)
    backlog = _write(area, "BACKLOG.md", "Header.\n\n- first\n## Out of scope\n- second\n")
    findings = records_lint.lint(area)
    assert [(f.code, f.fixable) for f in findings] == [("backlog-line", False)]
    assert "line 4" in findings[0].message
    main(["lint", "--fix", "--area", str(area.root)])
    assert backlog.read_text() == "Header.\n\n- first\n## Out of scope\n- second\n"
