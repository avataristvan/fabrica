"""Tests for the `## Edges` section: relative links between records instead of ids in the frontmatter."""
from __future__ import annotations

import pytest

from ai_mem import records_lint
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_markdown import EdgeLink
from ai_mem.infrastructure.adr_paths import records_dir_for_root
from ai_mem.infrastructure.areas import find_area
from ai_mem.infrastructure.file_repository import FileMemoryRepository
from ai_mem.infrastructure.record_links import href_for_ref, ref_for_href


def _area(path):
    (path / "docs" / "records").mkdir(parents=True)
    return find_area(path)


def _write(area, rel, text):
    path = area.records_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _record(body="Observed: x\n", edges=""):
    return f"type: learning\ntopic: general\ncreated: 1.0\n---\n\n{body}" + (f"\n## Edges\n\n{edges}" if edges else "")


def test_section_round_trips_and_leaves_the_text():
    links = [EdgeLink("related", "../decisions/domain_b.md"), EdgeLink("superseded_by", "learning_c.md")]
    body = adr_markdown.render_edges_section("Observed: x\n", links)
    assert body == ("Observed: x\n\n## Edges\n\n- related: [domain_b](../decisions/domain_b.md)\n"
                    "- superseded_by: [learning_c](learning_c.md)\n")
    assert adr_markdown.split_edges_section(body) == ("Observed: x", links)
    assert adr_markdown.render_edges_section("Observed: x\n", []) == "Observed: x\n"
    assert adr_markdown.split_edges_section("Observed: x\n") == ("Observed: x\n", [])


def test_malformed_section_is_an_error():
    with pytest.raises(ValueError, match="Edges"):
        adr_markdown.split_edges_section("Observed: x\n\n## Edges\n\n- related: domain_b\n")


def test_parse_takes_the_id_from_the_file_name_and_edges_from_the_section():
    parsed = adr_markdown.parse(_record(edges="- related: [domain_b](../../arch/decisions/domain_b.md)\n"
                                              "- superseded_by: [learning_c](learning_c.md)\n"), entry_id="learning_a")
    assert parsed.id == "learning_a"
    assert parsed.text == "Observed: x"
    assert parsed.edges == [{"target_id": "domain_b", "edge_type": "related"}]
    assert parsed.superseded_by == "learning_c"


def test_links_resolve_within_an_area_across_areas_and_to_sources(tmp_path):
    outer = _area(tmp_path / "ws")
    inner = _area(tmp_path / "ws" / "proj")
    source = _write(inner, "general/learnings/learning_a.md", _record())
    _write(inner, "arch/decisions/domain_b.md", _record())
    _write(outer, "general/decisions/domain_up.md", _record())
    (inner.records_dir.parent / "sources").mkdir()
    (inner.records_dir.parent / "sources" / "talk.md").write_text("x")

    for ref, href in [("domain_b", "../../arch/decisions/domain_b.md"),
                      ("..:domain_up", "../../../../../docs/records/general/decisions/domain_up.md"),
                      ("talk", "../../../sources/talk.md"),
                      ("gone", "../../gone.md")]:  # dangling: a link that reads back as the same reference
        assert href_for_ref(source, inner, ref) == href
        assert ref_for_href(source, inner, href) == ref


def test_repository_reads_a_record_without_id_and_with_link_edges(tmp_path):
    area = _area(tmp_path / "repo")
    _write(area, "arch/decisions/domain_b.md", _record())
    _write(area, "general/learnings/learning_a.md", _record(edges="- confirms: [domain_b](../../arch/decisions/domain_b.md)\n"))
    repo = FileMemoryRepository(lambda key: records_dir_for_root(area.root))
    [entry] = repo.get_by_ids("k", ["learning_a"])
    assert entry.text == "Observed: x"
    assert [(e.target_id, e.edge_type) for e in repo.get_edges("k", "learning_a")] == [("domain_b", "confirms")]


def test_lint_accepts_link_edges_and_reports_dead_and_malformed_ones(tmp_path):
    area = _area(tmp_path / "a")
    _write(area, "arch/decisions/domain_b.md", _record())
    _write(area, "general/learnings/learning_a.md", _record(edges="- related: [domain_b](../../arch/decisions/domain_b.md)\n"))
    findings = {(f.file.name, f.code) for f in records_lint.lint(area)}
    assert not any(name == "learning_a.md" and code.startswith("edge") for name, code in findings)

    _write(area, "general/learnings/learning_d.md", _record(edges="- related: [nowhere](../../nowhere.md)\n"))
    _write(area, "general/learnings/learning_e.md", _record(edges="- related: nowhere\n"))
    findings = {(f.file.name, f.code) for f in records_lint.lint(area)}
    assert ("learning_d.md", "edge-dangling") in findings
    assert ("learning_e.md", "edges-section") in findings


def test_lint_fix_moves_id_edges_and_superseded_by_into_links(tmp_path):
    from ai_mem.mem_cli import main
    outer = _area(tmp_path / "ws")
    area = _area(tmp_path / "ws" / "proj")
    _write(outer, "general/decisions/domain_up.md", _record())
    _write(area, "arch/decisions/domain_b.md", _record())
    _write(area, "general/learnings/learning_c.md", _record())
    legacy = ('id: learning_a\ntype: learning\ntopic: general\ncreated: 1.0\nsuperseded_by: learning_c\n'
              'edges: [{"target_id": "domain_b", "edge_type": "related"}, {"target_id": "..:domain_up", "edge_type": "derived_from"}]\n'
              'cue: when x\n---\n\nObserved: x\n')
    path = _write(area, "general/learnings/learning_a.md", legacy)
    assert ("learning_a.md", "legacy-refs") in {(f.file.name, f.code) for f in records_lint.lint(area)}

    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_text() == (
        "type: learning\ntopic: general\ncreated: 1.0\ncue: when x\n---\n\nObserved: x\n\n## Edges\n\n"
        "- related: [domain_b](../../arch/decisions/domain_b.md)\n"
        "- derived_from: [domain_up](../../../../../docs/records/general/decisions/domain_up.md)\n"
        "- superseded_by: [learning_c](learning_c.md)\n")
    assert not [f for f in records_lint.lint(area) if f.file == path]


def test_lint_fix_refuses_an_id_that_differs_from_the_file_name(tmp_path):
    from ai_mem.mem_cli import main
    area = _area(tmp_path / "a")
    text = "id: learning_other\ntype: learning\ntopic: general\ncreated: 1.0\n---\n\nObserved: x\n"
    path = _write(area, "general/learnings/learning_a.md", text)
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_text() == text


def test_a_moved_target_leaves_a_stale_link_that_fix_repairs(tmp_path):
    from ai_mem.mem_cli import main
    area = _area(tmp_path / "a")
    _write(area, "arch/decisions/domain_b.md", _record())
    path = _write(area, "general/learnings/learning_a.md",
                  _record(edges="- related: [domain_b](../../arch/decisions/domain_b.md)\n"))
    (area.records_dir / "arch/decisions/domain_b.md").rename(area.records_dir / "general/learnings/domain_b.md")
    assert ("learning_a.md", "link-stale", True) in {(f.file.name, f.code, f.fixable) for f in records_lint.lint(area)}

    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_text().endswith("- related: [domain_b](domain_b.md)\n")
    assert not [f for f in records_lint.lint(area) if f.file == path]


def test_fix_repoints_a_link_whose_target_left_for_exactly_one_other_area(tmp_path):
    from ai_mem.mem_cli import main
    area = _area(tmp_path / "ws" / "a")
    other = _area(tmp_path / "ws" / "b")
    _write(other, "general/learnings/learning_t.md", _record())
    path = _write(area, "general/learnings/learning_a.md", _record(edges="- related: [learning_t](learning_t.md)\n"))
    main(["lint", "--fix", "--area", str(area.root)])
    assert path.read_text().endswith("- related: [learning_t](../../../../../b/docs/records/general/learnings/learning_t.md)\n")


def test_retyping_a_record_relinks_its_referrers_in_the_same_area(tmp_path):
    from ai_mem.mem_cli import main
    area = _area(tmp_path / "a")
    repo = FileMemoryRepository(lambda key: records_dir_for_root(area.root))
    _write(area, "general/learnings/learning_b.md", _record())
    path = _write(area, "general/learnings/learning_a.md", _record(edges="- related: [learning_b](learning_b.md)\n"))
    [moved] = repo.get_by_ids("k", ["learning_b"])
    moved.metadata["type"] = "pattern"
    repo.upsert("k", [moved])
    assert path.read_text().endswith("- related: [learning_b](../decisions/learning_b.md)\n")
    main(["lint", "--area", str(area.root)])
    assert not [f for f in records_lint.lint(area) if f.file == path]


def test_fix_links_ids_named_in_the_text_and_leaves_code_paths_and_words(tmp_path):
    from ai_mem.mem_cli import main
    area = _area(tmp_path / "a")
    _write(area, "arch/decisions/domain_b.md", _record())
    body = ("Rests on domain_b and `domain_b`, see [domain_b](../../arch/decisions/domain_b.md).\n"
            "Kept: `mem link learning_a domain_b`, docs/records/arch/decisions/domain_b.md, domain_b.md, valid_until.\n"
            "```\ndomain_b\n```\n")
    path = _write(area, "general/learnings/learning_a.md", _record(body=body))
    assert ("learning_a.md", "bare-id") in {(f.file.name, f.code) for f in records_lint.lint(area)}

    main(["lint", "--fix", "--area", str(area.root)])
    link = "[domain_b](../../arch/decisions/domain_b.md)"
    assert path.read_text().endswith(
        f"Rests on {link} and {link}, see {link}.\n"
        "Kept: `mem link learning_a domain_b`, docs/records/arch/decisions/domain_b.md, domain_b.md, valid_until.\n"
        "```\ndomain_b\n```\n")
    assert not [f for f in records_lint.lint(area) if f.file == path]
