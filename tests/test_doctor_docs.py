"""doctor_docs: the Docs and Not-concluded sections of mem doctor."""
from __future__ import annotations

import subprocess
from pathlib import Path

from ai_mem.doctor_docs import collect_docs, render_docs, render_not_concluded
from ai_mem.infrastructure.areas import Area


def _area(tmp_path: Path) -> Area:
    (tmp_path / "docs" / "records").mkdir(parents=True)
    return Area(tmp_path, tmp_path / "docs" / "records")


def _experiment(area: Area, slug: str, status: str) -> None:
    path = area.root / "docs" / "experiments" / slug / "README.md"
    path.parent.mkdir(parents=True)
    path.write_text(f"---\nquestion: q\nstatus: {status}\ndate: 2026-11-05\nsetup: s\n---\n\n## Result\nx\n")


def test_unversioned_area_lists_loose_files_handoffs_and_old_format(tmp_path: Path) -> None:
    area = _area(tmp_path)
    (tmp_path / "docs" / "handoff-2026-11-01.md").write_text("## Charter\n")
    (tmp_path / "docs" / "dsi-test-plan-2026-10-27.md").write_text("x\n")
    (tmp_path / "docs" / "README.md").write_text("x\n")
    (tmp_path / "docs" / "notes").mkdir()
    (tmp_path / "docs" / "reference").mkdir()
    report = collect_docs(area, set(), [], {"legacy-refs": 3, "bare-id": 2, "missing-field": 1}, versioned=False, now=0)
    docs = report["docs"]
    assert docs["old_format"] == 5
    assert docs["loose_files"] == ["docs/dsi-test-plan-2026-10-27.md"]
    assert docs["folders_outside_map"] == ["docs/notes"]
    assert [h["file"] for h in docs["handoffs"]] == ["docs/handoff-2026-11-01.md"]
    lines = render_docs(".", str(tmp_path), docs)
    assert any("mem lint --fix" in line for line in lines) and any("/fabrica:tidy" in line for line in lines)


def test_project_texts_naming_records_by_bare_name(tmp_path: Path) -> None:
    area = _area(tmp_path)
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / "scout.md").write_text(
        "Mind learning_drop_drivers_2026_10_24 and [x](docs/records/a/learnings/learning_linked_2026_10_24.md).\n")
    report = collect_docs(area, {"learning_drop_drivers_2026_10_24", "learning_linked_2026_10_24"}, [], {}, versioned=False, now=0)
    texts = report["docs"]["texts_naming_records_by_id"]
    assert texts == [{"file": ".claude/agents/scout.md", "names": ["learning_drop_drivers_2026_10_24"], "count": 1}]


def test_not_concluded_lists_running_and_done_experiments_without_a_record(tmp_path: Path) -> None:
    area = _area(tmp_path)
    _experiment(area, "dsi-reenable", "done")
    _experiment(area, "emmc-speed", "done")
    _experiment(area, "suspend", "running")
    record = "Evidence: [run](../../../experiments/emmc-speed/README.md)"
    nc = collect_docs(area, set(), [record], {}, versioned=False)["not_concluded"]
    assert nc["done_without_record"] == ["docs/experiments/dsi-reenable/README.md"]
    assert [r["file"] for r in nc["running_experiments"]] == ["docs/experiments/suspend/README.md"]
    assert any("data without a conclusion" in line for line in render_not_concluded(".", nc))


def test_versioned_area_counts_commits_since_the_records_and_flags_unignored_data(tmp_path: Path) -> None:
    area = _area(tmp_path)

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "docs" / "records" / "FOCUS.md").write_text("focus\n")
    git("add", "-A"); git("commit", "-qm", "focus")
    (tmp_path / "code.py").write_text("x\n")
    git("add", "-A"); git("commit", "-qm", "code")
    (tmp_path / "data" / "runs").mkdir(parents=True)
    (tmp_path / "data" / "runs" / "log.txt").write_text("x\n")
    report = collect_docs(area, set(), [], {}, versioned=True)
    assert report["not_concluded"]["commits_since_records"] == 1
    assert report["docs"]["data_not_ignored"] is True
    (tmp_path / ".gitignore").write_text("/data/\n")
    assert collect_docs(area, set(), [], {}, versioned=True)["docs"]["data_not_ignored"] is False


def test_a_record_citing_a_longer_slug_does_not_conclude_a_shorter_one(tmp_path: Path) -> None:
    area = _area(tmp_path)
    _experiment(area, "foo", "done")
    _experiment(area, "foobar", "done")
    nc = collect_docs(area, set(), ["[r](../../../experiments/foobar/README.md)"], {}, versioned=False)["not_concluded"]
    assert nc["done_without_record"] == ["docs/experiments/foo/README.md"]
