"""docs_lint: experiments, handoff shape, records that cite a handoff (the documentation map)."""
from __future__ import annotations

from pathlib import Path

from ai_mem import docs_lint, records_lint
from ai_mem.hooks import lint_after_write
from ai_mem.infrastructure.areas import Area


def _area(tmp_path: Path) -> Area:
    records = tmp_path / "docs" / "records"
    records.mkdir(parents=True)
    return Area(tmp_path, records)


def _experiment(area: Area, slug: str, text: str) -> Path:
    path = area.root / "docs" / "experiments" / slug / "README.md"
    path.parent.mkdir(parents=True)
    path.write_text(text)
    return path


def _codes(findings) -> list[str]:
    return [code for code, _ in findings]


def test_planned_experiment_needs_question_status_date(tmp_path: Path) -> None:
    area = _area(tmp_path)
    good = _experiment(area, "a", "---\nquestion: q\nstatus: planned\ndate: 2026-11-05\n---\n\n## Hypotheses\n")
    assert docs_lint.check_experiment(good) == []
    no_date = _experiment(area, "b", "---\nquestion: q\nstatus: planned\n---\n")
    assert _codes(docs_lint.check_experiment(no_date)) == [docs_lint.EXPERIMENT_FRONTMATTER]


def test_running_needs_setup_and_done_needs_a_result(tmp_path: Path) -> None:
    area = _area(tmp_path)
    running = _experiment(area, "a", "---\nquestion: q\nstatus: running\ndate: 2026-11-05\n---\n")
    assert "setup" in docs_lint.check_experiment(running)[0][1]
    done = _experiment(area, "b", "---\nquestion: q\nstatus: done\ndate: 2026-11-05\nsetup: r19\n---\n\n## Runs\n")
    assert "Result" in docs_lint.check_experiment(done)[0][1]
    done_ok = _experiment(area, "c", "---\nquestion: q\nstatus: done\ndate: 2026-11-05\nsetup: r19\n---\n\n## Result\nH2 held.\n")
    assert docs_lint.check_experiment(done_ok) == []


def test_unknown_status_and_missing_frontmatter(tmp_path: Path) -> None:
    area = _area(tmp_path)
    assert _codes(docs_lint.check_experiment(_experiment(area, "a", "---\nstatus: wip\n---\n"))) == [docs_lint.EXPERIMENT_STATUS]
    assert _codes(docs_lint.check_experiment(_experiment(area, "b", "# notes\n"))) == [docs_lint.EXPERIMENT_FRONTMATTER]


def test_handoff_keeps_four_sections_and_no_dated_updates_or_tables(tmp_path: Path) -> None:
    area = _area(tmp_path)
    good = area.root / "docs" / "handoff-2026-11-05.md"
    good.write_text("# Handoff\n\n## Charter\nx\n\n## Conclusions (what holds now)\ny\n\n## Open points\nz\n\n## Start with\n/plan\n")
    assert docs_lint.check_handoff(good) == []
    bad = area.root / "docs" / "handoff-2026-11-06.md"
    bad.write_text("## Charter\n\n## Update 2026-11-06 evening\n\n## Build\n\n| # | change | result |\n|---|---|---|\n")
    messages = [message for _, message in docs_lint.check_handoff(bad)]
    assert any("dated section" in m for m in messages)
    assert any("'Build'" in m for m in messages)
    assert any("table" in m for m in messages)


def test_record_citing_a_handoff_is_found_but_a_commit_reference_is_not() -> None:
    assert docs_lint.handoff_citations("Evidence: docs/handoff-2026-10-23.md, the update.") == ["handoff-2026-10-23.md"]
    assert docs_lint.handoff_citations("Evidence: [h](../../../handoff-2026-10-23.md)") == ["handoff-2026-10-23.md"]
    assert docs_lint.handoff_citations("Evidence: `3353e4d:docs/handoff-2026-10-23.md`") == []
    assert docs_lint.handoff_citations("Evidence: docs/sources/handoff_2026_10_13.md") == []


def test_mem_lint_reports_experiments_and_handoffs(tmp_path: Path) -> None:
    area = _area(tmp_path)
    _experiment(area, "a", "# no frontmatter\n")
    (area.root / "docs" / "handoff-2026-11-05.md").write_text("## Status 2026-11-05 night\n")
    codes = {f.code for f in records_lint.lint(area)}
    assert {docs_lint.EXPERIMENT_FRONTMATTER, docs_lint.HANDOFF_SHAPE} <= codes


def test_hook_checks_an_experiment_and_a_handoff_it_just_wrote(tmp_path: Path) -> None:
    area = _area(tmp_path)
    experiment = _experiment(area, "a", "---\nstatus: running\n---\n")
    out = lint_after_write.handle({"tool_input": {"file_path": str(experiment)}})
    assert out["decision"] == "block" and docs_lint.EXPERIMENT_FRONTMATTER in out["reason"]
    handoff = area.root / "docs" / "handoff-2026-11-05.md"
    handoff.write_text("## Charter\n\n## Conclusions\n")
    assert lint_after_write.handle({"tool_input": {"file_path": str(handoff)}}) is None
    other = area.root / "docs" / "notes.md"
    other.write_text("## Anything 2026-11-05\n")
    assert lint_after_write.handle({"tool_input": {"file_path": str(other)}}) is None
