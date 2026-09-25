"""Tests for ai_mem.infrastructure.adr_index.regenerate_index: pure Markdown table generation."""
from __future__ import annotations

from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import regenerate_index


def _write_adr(adr_dir, entry_id, entry_type, text, metadata=None):
    adr_dir.mkdir(parents=True, exist_ok=True)
    content = adr_markdown.serialize(entry_id, entry_type, text, metadata or {})
    (adr_dir / f"{entry_id}.md").write_text(content)


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
    header_idx = lines.index("| id | title | status |")
    rows = lines[header_idx + 2:]
    assert rows == [
        "| domain_alpha | Decision: first alphabetically. | active |",
        "| domain_old | Decision: outdated. | superseded_by: domain_alpha |",
        "| domain_zebra | Decision: last alphabetically. | active |",
    ]


def test_regenerate_index_skips_malformed_file_and_reports_it(tmp_path, capsys):
    adr_dir = tmp_path / "decisions"
    _write_adr(adr_dir, "domain_good", "domain", "Decision: fine.\nWhy: y.\nScope: s.")
    (adr_dir / "domain_broken.md").write_text("not valid frontmatter at all")

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
