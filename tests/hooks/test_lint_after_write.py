"""lint_after_write: PostToolUse lint of the one record that was just written."""
from __future__ import annotations

import os
from pathlib import Path

from ai_mem.hooks import lint_after_write
from ai_mem.infrastructure.adr_index import regenerate_index

GOOD = """id: learning_good
type: learning
topic: general
created: 1791630404.0
---

Observed: x
Cause: y
Evidence: z
"""


def _area(tmp_path: Path) -> Path:
    (tmp_path / "area" / "docs" / "records" / "general" / "learnings").mkdir(parents=True)
    return tmp_path / "area"


def _event(path: Path | str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": str(path)}}


def test_malformed_record_yields_a_block_reason(tmp_path: Path) -> None:
    area = _area(tmp_path)
    bad = area / "docs" / "records" / "general" / "learnings" / "learning_bad.md"
    bad.write_text("no frontmatter at all\n")
    out = lint_after_write.handle(_event(bad))
    assert out["decision"] == "block" and "learning_bad.md" in out["reason"]
    assert bad.read_text() == "no frontmatter at all\n"  # never --fix


def test_clean_record_with_current_index_is_silent(tmp_path: Path) -> None:
    area = _area(tmp_path)
    good = area / "docs" / "records" / "general" / "learnings" / "learning_good.md"
    good.write_text(GOOD)
    regenerate_index(area / "docs" / "records")
    assert lint_after_write.handle(_event(good)) is None


def test_file_outside_records_is_ignored(tmp_path: Path) -> None:
    area = _area(tmp_path)
    other = area / "README.md"
    other.write_text("# x\n")
    assert lint_after_write.handle(_event(other)) is None


def test_top_level_index_and_focus_are_not_records(tmp_path: Path) -> None:
    area = _area(tmp_path)
    focus = area / "docs" / "records" / "FOCUS.md"
    focus.write_text("focus\n")
    assert lint_after_write.handle(_event(focus)) is None


def test_relative_and_non_markdown_paths_are_ignored(tmp_path: Path) -> None:
    area = _area(tmp_path)
    assert lint_after_write.handle(_event("docs/records/general/learnings/x.md")) is None
    assert lint_after_write.handle(_event(area / "docs" / "records" / "x.txt")) is None
    assert lint_after_write.handle({"tool_input": {"file_path": 5}}) is None


def test_dotdot_path_is_normalised_before_the_area_walk(tmp_path: Path) -> None:
    area = _area(tmp_path)
    bad = area / "docs" / "records" / "general" / "learnings" / "learning_bad.md"
    bad.write_text("broken\n")
    sneaky = area / "docs" / "records" / "general" / ".." / "general" / "learnings" / "learning_bad.md"
    assert lint_after_write.handle(_event(sneaky))["decision"] == "block"
    escape = area / "docs" / "records" / ".." / ".." / "README.md"
    (area / "README.md").write_text("x\n")
    assert lint_after_write.handle(_event(escape)) is None


def test_symlinked_record_is_reported_not_followed(tmp_path: Path) -> None:
    area = _area(tmp_path)
    secret = tmp_path / "secret.md"
    secret.write_text("id: x\n---\nTOP SECRET BODY\n")
    link = area / "docs" / "records" / "general" / "learnings" / "learning_link.md"
    os.symlink(secret, link)
    out = lint_after_write.handle(_event(link))
    assert out["decision"] == "block" and "TOP SECRET" not in out["reason"]


def test_many_findings_are_capped(tmp_path: Path) -> None:
    area = _area(tmp_path)
    bad = area / "docs" / "records" / "general" / "learnings" / "learning_bad.md"
    bad.write_text("---\n---\n" + "x" * 10)
    out = lint_after_write.handle(_event(bad))
    assert len(out["reason"]) <= 800


def test_symlinked_records_directory_is_not_followed(tmp_path: Path) -> None:
    outside = tmp_path / "outside" / "general" / "learnings"
    outside.mkdir(parents=True)
    (outside / "learning_x.md").write_text("broken\n")
    (tmp_path / "proj" / "docs").mkdir(parents=True)
    os.symlink(tmp_path / "outside", tmp_path / "proj" / "docs" / "records")
    assert lint_after_write.handle(_event(tmp_path / "proj" / "docs" / "records" / "general" / "learnings" / "learning_x.md")) is None


def test_reason_carries_codes_not_record_text(tmp_path: Path) -> None:
    area = _area(tmp_path)
    bad = area / "docs" / "records" / "general" / "learnings" / "learning_bad.md"
    bad.write_text("id: learning_bad\ntype: learning\ntopic: general\nedges: [{\"target_id\": \"SECRETTEXT\", \"edge_type\": \"related\"}]\n---\nbody\n")
    out = lint_after_write.handle(_event(bad))
    assert out and "SECRETTEXT" not in out["reason"]
