"""Tests for ai_mem.infrastructure.adr_index.regenerate_index: pure Markdown table generation."""
from __future__ import annotations

import pytest

from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import regenerate_index


def _write_adr(adr_dir, entry_id, entry_type, text, metadata=None):
    metadata = metadata or {}
    kind = "learnings" if entry_type == "learning" else "decisions"
    target_dir = adr_dir / metadata.get("area", "general") / kind
    target_dir.mkdir(parents=True, exist_ok=True)
    content = adr_markdown.serialize(entry_id, entry_type, text, metadata)
    (target_dir / f"{entry_id}.md").write_text(content)


def test_regenerate_index_lists_entries_sorted_by_id_with_status(tmp_path):
    adr_dir = tmp_path / "decisions"
    _write_adr(adr_dir, "domain_zebra", "domain", "Decision: last alphabetically.\nWhy: z.\nScope: s.")
    _write_adr(adr_dir, "domain_alpha", "domain", "Decision: first alphabetically.\nWhy: a.\nScope: s.")
    _write_adr(
        adr_dir,
        "domain_old",
        "domain",
        "Decision: outdated.\nWhy: o.\nScope: s.",
        metadata={"superseded_by": "domain_alpha"},
    )

    regenerate_index(adr_dir)

    content = (adr_dir / "INDEX.md").read_text()
    lines = content.splitlines()
    assert lines[0] == "# Decision Records Index"
    header_idx = lines.index("| id | area | type | title | status |")
    rows = lines[header_idx + 2:]
    assert rows == [
        "| domain_alpha | general | domain | Decision: first alphabetically. | active |",
        "| domain_old | general | domain | Decision: outdated. | superseded_by: domain_alpha |",
        "| domain_zebra | general | domain | Decision: last alphabetically. | active |",
    ]


def test_regenerate_index_skips_malformed_file_and_reports_it(tmp_path, capsys):
    adr_dir = tmp_path / "decisions"
    _write_adr(adr_dir, "domain_good", "domain", "Decision: fine.\nWhy: y.\nScope: s.")
    (adr_dir / "general" / "decisions" / "domain_broken.md").write_text("not valid frontmatter at all")

    regenerate_index(adr_dir)

    err = capsys.readouterr().err
    assert "domain_broken.md" in err

    content = (adr_dir / "INDEX.md").read_text()
    assert "domain_good" in content
    assert "domain_broken" not in content


def test_regenerate_index_excludes_itself_from_the_table(tmp_path):
    adr_dir = tmp_path / "decisions"
    _write_adr(adr_dir, "domain_good", "domain", "Decision: fine.\nWhy: y.\nScope: s.")

    regenerate_index(adr_dir)
    regenerate_index(adr_dir)

    content = (adr_dir / "INDEX.md").read_text()
    assert content.count("domain_good") == 1


def test_regenerate_index_is_byte_identical_across_repeated_runs(tmp_path):
    adr_dir = tmp_path / "decisions"
    _write_adr(adr_dir, "domain_a", "domain", "Decision: a.\nWhy: y.\nScope: s.")
    _write_adr(adr_dir, "domain_b", "domain", "Decision: b.\nWhy: y.\nScope: s.", metadata={"superseded_by": "domain_a"})

    regenerate_index(adr_dir)
    first = (adr_dir / "INDEX.md").read_bytes()

    regenerate_index(adr_dir)
    second = (adr_dir / "INDEX.md").read_bytes()

    assert first == second


def test_regenerate_index_ignores_readme_silently(tmp_path, capsys):
    adr_dir = tmp_path / "decisions"
    _write_adr(adr_dir, "domain_a", "domain", "Decision: a.")
    (adr_dir / "README.md").write_text("# Decision records\n\nHandwritten, no frontmatter.\n")

    regenerate_index(adr_dir)

    assert "README" not in capsys.readouterr().err
    assert "README" not in (adr_dir / "INDEX.md").read_text()


def test_regenerate_index_covers_areas_and_kinds_recursively(tmp_path):
    adr_dir = tmp_path / "records"
    _write_adr(adr_dir, "domain_a", "domain", "Decision: a.", metadata={"area": "hooks"})
    _write_adr(adr_dir, "learning_b", "learning", "Observed: b.\nCause: unknown\nEvidence: c", metadata={"area": "search"})
    _write_adr(adr_dir, "pattern_c", "pattern", "Decision: c.")

    regenerate_index(adr_dir)

    rows = (adr_dir / "INDEX.md").read_text().splitlines()[4:]
    assert rows == [
        "| domain_a | hooks | domain | Decision: a. | active |",
        "| learning_b | search | learning | Observed: b. | active |",
        "| pattern_c | general | pattern | Decision: c. | active |",
    ]


def test_regenerate_index_skips_only_top_level_index_and_readme(tmp_path):
    adr_dir = tmp_path / "records"
    _write_adr(adr_dir, "domain_a", "domain", "Decision: a.")
    (adr_dir / "README.md").write_text("handwritten")
    nested = adr_dir / "general" / "decisions"
    (nested / "README.md").write_text(adr_markdown.serialize("README", "domain", "Decision: nested.", {}))

    regenerate_index(adr_dir)

    content = (adr_dir / "INDEX.md").read_text()
    assert "| README | general | domain | Decision: nested. |" in content
    assert "handwritten" not in content


def test_regenerate_index_leaves_no_temp_files(tmp_path):
    adr_dir = tmp_path / "records"
    adr_dir.mkdir()
    regenerate_index(adr_dir)
    regenerate_index(adr_dir)

    assert [p.name for p in adr_dir.iterdir()] == ["INDEX.md"]


def test_regenerate_index_failed_write_keeps_old_index_and_cleans_up(tmp_path, monkeypatch):
    import os

    adr_dir = tmp_path / "records"
    adr_dir.mkdir()
    regenerate_index(adr_dir)
    old = (adr_dir / "INDEX.md").read_bytes()

    def boom(*_args):
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        regenerate_index(adr_dir)

    assert (adr_dir / "INDEX.md").read_bytes() == old
    assert [p.name for p in adr_dir.iterdir()] == ["INDEX.md"]
