"""Tests for `mem doctor` (synthetic fixtures)."""
from __future__ import annotations

import json
import os
import subprocess
import time

from ai_mem.infrastructure.areas import find_area
from ai_mem.mem_cli import main


def _area(path, records=()):
    (path / "docs" / "records").mkdir(parents=True)
    area = find_area(path)
    for entry_id, body, extra in records:
        file = area.records_dir / "general" / "learnings" / f"{entry_id}.md"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f"id: {entry_id}\ntype: learning\narea: general\ncreated: 1.0\n{extra}---\n\n{body}\n")
    if records:
        main(["lint", "--fix", "--area", str(path)])
    return area


def _doctor(root, capsys, *flags):
    capsys.readouterr()  # drop output of fixture setup
    assert main(["doctor", "--root", str(root), *flags]) == 0
    return capsys.readouterr().out


def _report(root, capsys):
    return json.loads(_doctor(root, capsys, "--json"))


def _git(path, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, env=env)


def test_clean_unversioned_area_reports_only_missing_version_control(tmp_path, capsys):
    _area(tmp_path / "a", [("learning_a", "Observed: x", "")])
    report = _report(tmp_path, capsys)
    area = report["areas"][0]
    assert area["findings"] == {} and area["versioned"] is False and not area["dead_weight"]
    assert "migration" not in report


def test_dangling_edges_bare_and_cross_area(tmp_path, capsys):
    a = _area(tmp_path / "a", [("learning_a", "Observed: x", 'edges: [{"target_id": "gone", "edge_type": "related"}, {"target_id": "../b:nope", "edge_type": "related"}, {"target_id": "../zzz:x", "edge_type": "related"}]\n')])
    _area(tmp_path / "b", [("learning_b", "Observed: y", "")])
    dangling = _report(tmp_path, capsys)["areas"][0]["dangling_edges"]
    assert len(dangling) == 3 and a.root.name == "a"


def test_hand_written_not_adopted(tmp_path, capsys):
    area = _area(tmp_path / "a", [("learning_a", "Observed: x", "")])
    (area.records_dir / "INDEX.md").write_text("| [learning_a](general/learnings/learning_a.md) |\n")
    hand = area.records_dir / "general" / "learnings" / "learning_h.md"
    hand.write_text("---\nid: learning_h\ntype: learning\n---\nObserved: h\n")
    entry = _report(tmp_path, capsys)["areas"][0]["hand_written"]
    assert entry["fix_would_change"] == ["general/learnings/learning_h.md"]
    assert entry["missing_from_index"] == ["general/learnings/learning_h.md"]
    assert entry["index_differs"] is True


def test_dead_weight_needs_no_incoming_edge_and_a_vanished_path(tmp_path, capsys):
    a = _area(tmp_path / "a", [
        ("learning_old", "Observed: see `src/gone/thing.py` and `docs/there.md`", ""),
        ("learning_kept", "Observed: see `src/gone/other.py`", ""),
        ("learning_new", "Observed: see `docs/there.md`", 'edges: [{"target_id": "learning_kept", "edge_type": "derived_from"}]\n'),
        ("learning_inline", "Observed: `a/../../etc/passwd.txt` and `read/write` and `server.py`", ""),
    ])
    (a.root / "docs" / "there.md").write_text("x")
    main(["lint", "--fix", "--area", str(a.root)])
    dead = _report(tmp_path, capsys)["areas"][0]["dead_weight"]
    assert dead == [{"file": "general/learnings/learning_old.md", "missing": ["src/gone/thing.py"]}]


def test_incoming_edge_from_another_area_keeps_a_record(tmp_path, capsys):
    _area(tmp_path / "a", [("learning_old", "Observed: see `src/gone/thing.py`", "")])
    _area(tmp_path / "b", [("learning_b", "Observed: y", 'edges: [{"target_id": "../a:learning_old", "edge_type": "derived_from"}]\n')])
    assert _report(tmp_path, capsys)["areas"][0]["dead_weight"] == []


def test_versioned_area_and_state_from_commit_times(tmp_path, capsys):
    area = _area(tmp_path / "a", [("learning_a", "Observed: x", "")])
    (area.records_dir / "FOCUS.md").write_text("focus\n")
    _git(area.root, "init", "-q")
    _git(area.root, "add", "-A")
    _git(area.root, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "one", date="2020-01-01T00:00:00")
    assert _report(tmp_path, capsys)["areas"][0]["versioned"] is True
    assert _report(tmp_path, capsys)["state"] == []
    (area.root / "x.txt").write_text("x")
    _git(area.root, "add", "-A")
    _git(area.root, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "two", date="2020-03-01T00:00:00")
    state = _report(tmp_path, capsys)["state"]
    assert [s["file"] for s in state] == ["docs/records/FOCUS.md"] and state[0]["basis"] == "last commit"


def test_state_unversioned_uses_mtime(tmp_path, capsys):
    area = _area(tmp_path / "a", [("learning_a", "Observed: x", "")])
    focus = area.records_dir / "FOCUS.md"
    focus.write_text("focus\n")
    os.utime(focus, (1_000_000, 1_000_000))
    state = _report(tmp_path, capsys)["state"]
    assert state and state[0]["basis"] == "mtime"


def test_deterministic_and_writes_only_the_timestamp(tmp_path, monkeypatch, capsys):
    _area(tmp_path / "a", [("learning_a", "Observed: x", "")])
    db = tmp_path / "db"
    monkeypatch.setenv("AI_MEM_PATH", str(db))

    def snapshot():
        return sorted((p.relative_to(tmp_path).as_posix(), p.read_bytes()) for p in (tmp_path / "a").rglob("*") if p.is_file())

    before = snapshot()
    first = _doctor(tmp_path, capsys)
    second = _doctor(tmp_path, capsys)
    assert first == second and snapshot() == before
    assert os.listdir(db) == ["doctor_last_run"] and int((db / "doctor_last_run").read_text()) > 0


def test_default_root_is_current_area(tmp_path, monkeypatch, capsys):
    area = _area(tmp_path / "a")
    monkeypatch.chdir(area.root)
    assert main(["doctor", "--json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["areas"]) == 1


def test_invalid_root_and_no_area_are_usage_errors(tmp_path, monkeypatch):
    assert main(["doctor", "--root", str(tmp_path / "missing")]) == 2
    monkeypatch.chdir(tmp_path)
    assert main(["doctor"]) == 2


def _home(tmp_path, monkeypatch):
    home, db = tmp_path / "home", tmp_path / "db"
    (home / ".claude").mkdir(parents=True)
    db.mkdir()
    monkeypatch.setenv("AI_MEM_PATH", str(db))
    return home, db


def _doctor_json(tmp_path, home, capsys, *flags):
    (tmp_path / "a" / "docs" / "records").mkdir(parents=True, exist_ok=True)
    capsys.readouterr()
    assert main(["doctor", "--root", str(tmp_path / "a"), "--home", str(home), "--json", *flags]) == 0
    return json.loads(capsys.readouterr().out)


def test_wiring_lists_teams_without_hook_in_and_missing_hooks(tmp_path, monkeypatch, capsys):
    home, _ = _home(tmp_path, monkeypatch)
    claude = home / ".claude"
    (claude / "commands").mkdir()
    (claude / "agents").mkdir()
    (claude / "skills" / "team").mkdir(parents=True)
    (claude / "commands" / "plain.md").write_text("no agents here")
    (claude / "commands" / "bare.md").write_text('Agent(subagent_type="x")')
    (claude / "commands" / "hooked.md").write_text('Agent(...) and skill handoff-protocol')
    (claude / "agents" / "mem.md").write_text("calls mem_query")
    (claude / "skills" / "team" / "SKILL.md").write_text("ask the librarian")
    (claude / "agents" / "dangling.md").symlink_to(claude / "agents" / "missing-target.md")
    cmd = "AI_MEM_WORKSPACE_ROOT=/w /usr/bin/python3 -m ai_mem.hook 2>/dev/null || true"
    (claude / "settings.json").write_text(json.dumps({"hooks": {
        "SessionStart": [{"hooks": [{"type": "command", "command": cmd}]}],
        "Stop": [{"hooks": [{"type": "command", "command": "python -m ai_mem.hooks.reflect_reminder_x"}]}, "junk"],
        "SubagentStop": "junk"}}))
    wiring = _doctor_json(tmp_path, home, capsys)["wiring"]
    assert wiring["teams_without_hook_in"] == ["commands/bare.md", "agents/mem.md", "skills/team/SKILL.md"]
    assert wiring["teams"] == 4 and wiring["plugin_enabled"] is False
    assert wiring["hooks_registered"] == ["ai_mem.hook"]
    assert wiring["hooks_missing"] == ["ai_mem.hooks.retro_check", "ai_mem.hooks.lint_after_write", "ai_mem.hooks.reflect_reminder"]


def test_wiring_all_hooks_and_plugin(tmp_path, monkeypatch, capsys):
    home, _ = _home(tmp_path, monkeypatch)
    modules = {"SessionStart": "ai_mem.hook", "SubagentStop": "ai_mem.hooks.retro_check",
               "PostToolUse": "ai_mem.hooks.lint_after_write", "Stop": "ai_mem.hooks.reflect_reminder"}
    settings = {"hooks": {event: [{"hooks": [{"command": f"py -m {mod} 2>/dev/null || true"}]}] for event, mod in modules.items()}}
    (home / ".claude" / "settings.json").write_text(json.dumps(settings))
    assert _doctor_json(tmp_path, home, capsys)["wiring"]["hooks_missing"] == []
    (home / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {"ai-mem@fabrica": True}}))
    wiring = _doctor_json(tmp_path, home, capsys)["wiring"]
    assert wiring["plugin_enabled"] is True and wiring["teams"] == 0


def test_wiring_survives_garbage(tmp_path, monkeypatch, capsys):
    home, _ = _home(tmp_path, monkeypatch)
    (home / ".claude" / "settings.json").write_text("[1, 2")
    assert _doctor_json(tmp_path, home, capsys)["wiring"]["hooks_registered"] == []
    (home / ".claude" / "settings.json").write_text('{"hooks": {"Stop": [{"hooks": [1, {"command": 5}]}]}, "enabledPlugins": []}')
    assert _doctor_json(tmp_path, home, capsys)["wiring"]["hooks_missing"][-1] == "ai_mem.hooks.reflect_reminder"
    (home / ".claude" / "agents").mkdir()
    (home / ".claude" / "agents" / "bin.md").write_bytes(b"\xff\xfe Agent( \x00")
    assert _doctor_json(tmp_path, home, capsys)["wiring"]["teams_without_hook_in"] == ["agents/bin.md"]


def test_wiring_lists_external_skills_apart(tmp_path, monkeypatch, capsys):
    home, _ = _home(tmp_path, monkeypatch)
    skills = home / ".claude" / "skills"
    for name, marker in (("own", None), ("versioned", ".tool_version"), ("cloned", ".git"), ("plain", "VERSION")):
        (skills / name).mkdir(parents=True)
        (skills / name / "SKILL.md").write_text('Agent(subagent_type="x")')
        if marker:
            (skills / name / marker).mkdir() if marker == ".git" else (skills / name / marker).write_text("1")
    wiring = _doctor_json(tmp_path, home, capsys)["wiring"]
    assert wiring["teams_without_hook_in"] == ["skills/own/SKILL.md"]
    assert sorted(wiring["teams_external"]) == ["skills/cloned/SKILL.md", "skills/plain/SKILL.md", "skills/versioned/SKILL.md"]
    main(["doctor", "--root", str(tmp_path / "a"), "--home", str(home)])
    out = capsys.readouterr().out
    assert "teams without `handoff-protocol` (1 of 1 " in out and "external skills without `handoff-protocol`" in out


def _entry(agent_id, agent_type="the-coder", age_days=1, **fields):
    return {"ts": time.time() - age_days * 86400, "session_id": "s", "agent_type": agent_type, "agent_id": agent_id,
            "has_retro": True, "missing": [], "records_consulted": "none", "record_candidates": "none", "learned": None, **fields}


def test_effect_empty_or_missing_log(tmp_path, monkeypatch, capsys):
    home, db = _home(tmp_path, monkeypatch)
    assert _doctor_json(tmp_path, home, capsys)["effect"]["retro"] == {}
    capsys.readouterr()
    assert "no retro data yet" in _doctor(tmp_path / "a", capsys, "--home", str(home))
    (db / "retro_log.jsonl").write_text("")
    assert _doctor_json(tmp_path, home, capsys)["effect"]["retro"] == {}


def test_effect_rates_dedupe_window_and_malformed_lines(tmp_path, monkeypatch, capsys):
    home, db = _home(tmp_path, monkeypatch)
    lines = [
        json.dumps(_entry("a1", has_retro=False, missing=["records_consulted", "record_candidates"], records_consulted=None, record_candidates=None)),
        json.dumps(_entry("a1", records_consulted="librarian: x", record_candidates="a learning")),  # blocked, then complied: this one counts
        json.dumps(_entry("a2", missing=["record_candidates"], records_consulted="None.")),
        json.dumps(_entry("old", age_days=60, records_consulted="x")),
        json.dumps(_entry("r1", agent_type="pr-review-toolkit:code-reviewer", records_consulted="y", record_candidates="z")),
        json.dumps(_entry("", records_consulted="q")), json.dumps(_entry("", records_consulted="q")),
        "not json", "[1]", '{"ts": "x", "agent_type": "the-coder"}', '{"ts": true, "agent_type": "the-coder"}', '{"ts": 1e999}',
        json.dumps(_entry("esc", agent_type="evil\x1b[2Jtype")), "\xff",
    ]
    (db / "retro_log.jsonl").write_bytes(("\n".join(lines) + "\n").encode("latin-1", "replace"))
    retro = _doctor_json(tmp_path, home, capsys)["effect"]["retro"]
    coder = retro["the-coder"]
    assert coder["entries"] == 4 and coder["records_consulted"] == 3 and coder["record_candidates"] == 1 and coder["missing_fields"] == 1
    assert coder["records_consulted_rate"] == 0.75 and coder["missing_fields_rate"] == 0.25
    assert retro["pr-review-toolkit:code-reviewer"]["entries"] == 1
    assert "evil?[2Jtype" in retro and not any("\x1b" in name for name in retro)
    assert _doctor_json(tmp_path, home, capsys, "--days", "90")["effect"]["retro"]["the-coder"]["entries"] == 5


def test_effect_log_is_a_directory_or_unreadable(tmp_path, monkeypatch, capsys):
    home, db = _home(tmp_path, monkeypatch)
    (db / "retro_log.jsonl").mkdir()
    assert _doctor_json(tmp_path, home, capsys)["effect"]["retro"] == {}


def test_days_must_be_positive(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    _area(tmp_path / "a")
    assert main(["doctor", "--root", str(tmp_path / "a"), "--days", "0"]) == 2


def test_three_confirms_across_areas_flag_cue_sharpening(tmp_path, capsys):
    def confirm(target):
        return f'edges: [{{"target_id": "{target}", "edge_type": "confirms"}}]\n'
    _area(tmp_path / "a", [("learning_t", "Observed: t", ""), ("learning_u", "Observed: u", ""),
                           ("learning_c1", "Observed: c1", confirm("learning_t")), ("learning_c2", "Observed: c2", confirm("learning_t")),
                           ("learning_c3", "Observed: c3", confirm("learning_u")), ("learning_bad", "Observed: b", "edges: nope\n")])
    _area(tmp_path / "b", [("learning_c4", "Observed: c4", confirm("../a:learning_t")), ("learning_c5", "Observed: c5", confirm("../a:learning_u"))])
    effect = json.loads(_doctor(tmp_path, capsys, "--json"))["effect"]
    assert [(c["id"], c["confirms"]) for c in effect["cue_sharpening"]] == [("learning_t", 3)]
    assert "learning_t (3)" in _doctor(tmp_path, capsys)


def test_hostile_inputs_never_crash(tmp_path, monkeypatch, capsys):
    home, db = _home(tmp_path, monkeypatch)
    (home / ".claude" / "settings.json").write_text("[" * 200_000)
    (db / "retro_log.jsonl").write_text("[" * 100_000 + "\n" + json.dumps(_entry("x", ts=1e999)) + "\n")
    area = _area(tmp_path / "a", [("learning_t", "Observed: t", "")])
    deep = area.records_dir / "general" / "learnings" / "learning_deep.md"
    deep.write_text("---\nid: learning_deep\ntype: learning\nedges: " + "[" * 50_000 + "\n---\nObserved: d\n")
    (home / ".claude" / "agents").mkdir()
    (home / ".claude" / "agents" / "evil\x1b[31m.md").write_text("Agent(")
    capsys.readouterr()
    assert main(["doctor", "--root", str(area.root), "--home", str(home), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["effect"]["retro"] == {} and "\x1b" not in report["wiring"]["teams_without_hook_in"][0]
    assert main(["doctor", "--root", str(area.root), "--days", "10" + "0" * 400]) == 2
    assert main(["doctor", "--root", str(area.root), "--home", "~nosuchuser_zz"]) == 2


def test_fifo_log_is_skipped(tmp_path, monkeypatch, capsys):
    home, db = _home(tmp_path, monkeypatch)
    os.mkfifo(db / "retro_log.jsonl")
    assert _doctor_json(tmp_path, home, capsys)["effect"]["retro"] == {}


def test_repeated_confirms_from_one_record_and_dangling_targets_do_not_count(tmp_path, capsys):
    three = 'edges: [' + ", ".join(['{"target_id": "learning_t", "edge_type": "confirms"}'] * 3) + ']\n'
    gone = 'edges: [' + ", ".join(['{"target_id": "learning_gone", "edge_type": "confirms"}'] * 3) + ']\n'
    _area(tmp_path / "a", [("learning_t", "Observed: t", ""), ("learning_c", "Observed: c", three), ("learning_d", "Observed: d", gone),
                           ("learning_e", "Observed: e", gone), ("learning_f", "Observed: f", gone)])
    assert json.loads(_doctor(tmp_path, capsys, "--json"))["effect"]["cue_sharpening"] == []


def _source(area, slug, status="unprocessed", extra=""):
    path = area.root / "docs" / "sources" / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntype: measurement\ndate: 2026-01-01\norigin: test\nstatus: {status}\n{extra}---\n\n## What the source says\n\nx\n\n## Our notes\n\n")


def test_sources_unprocessed_is_accepted_and_processed_needs_a_pointer(tmp_path, capsys):
    area = _area(tmp_path / "a", [("learning_a", "Observed: x\nEvidence: docs/sources/cited.md", "")])
    _source(area, "fresh")
    _source(area, "cited", "processed")
    _source(area, "orphan", "processed")
    sources = _report(tmp_path, capsys)["areas"][0]["sources"]
    assert sources["total"] == 3
    assert sources["unprocessed"] == ["docs/sources/fresh.md"]
    assert sources["unpointed"] == ["docs/sources/orphan.md"]
    assert sources["malformed"] == []


def test_sources_edge_counts_as_pointer_and_lint_accepts_it(tmp_path, capsys):
    area = _area(tmp_path / "a")
    _source(area, "measured", "processed")
    _area(tmp_path / "b", [("learning_b", "Observed: y", 'edges: [{"target_id": "../a:measured", "edge_type": "derived_from"}]\n')])
    report = _report(tmp_path, capsys)
    assert report["areas"][0]["sources"]["unpointed"] == []
    assert not report["areas"][1]["dangling_edges"]


def test_sources_malformed_frontmatter_and_unknown_status(tmp_path, capsys):
    area = _area(tmp_path / "a")
    _source(area, "weird", "maybe")
    (area.root / "docs" / "sources" / "bare.md").write_text("# no frontmatter\n")
    (area.root / "docs" / "sources" / "partial.md").write_text("---\ntype: x\nstatus: unprocessed\n---\n")
    problems = {m["file"]: m["problem"] for m in _report(tmp_path, capsys)["areas"][0]["sources"]["malformed"]}
    assert "not one of" in problems["docs/sources/weird.md"]
    assert problems["docs/sources/bare.md"] == "no frontmatter"
    assert problems["docs/sources/partial.md"] == "missing date, origin"


def test_retired_system_in_current_doc_unless_marked_historical(tmp_path, capsys):
    area = _area(tmp_path / "a")
    docs = area.root / "docs"
    (docs / "current.md").write_text("# Arch\n\nThe MCP server stores entries in ChromaDB.\n")
    (docs / "banner.md").write_text("> **Superseded.** old text\n\nThe MCP server.\n")
    (docs / "fm.md").write_text("---\nstatus: historical\n---\nBM25 and the daemon.\n")
    (docs / "handoff-2026-01-01.md").write_text("ChromaDB daemon\n")
    (docs / "clean.md").write_text("# Records\n")
    found = _report(tmp_path, capsys)["areas"][0]["sources"]["retired_in_current"]
    assert found == [{"file": "docs/current.md", "keywords": ["ChromaDB", "MCP server"]}]
    assert "docs/current.md: ChromaDB, MCP server" in _doctor(tmp_path, capsys)


def test_retired_system_found_in_diataxis_folders(tmp_path, capsys):
    area = _area(tmp_path / "a")
    for folder in ("tutorial", "how-to", "reference", "explanation"):
        (area.root / "docs" / folder).mkdir()
        (area.root / "docs" / folder / "page.md").write_text("The daemon answers queries.\n")
    (area.root / "docs" / "sources").mkdir(exist_ok=True)
    (area.root / "docs" / "sources" / "old.md").write_text("The daemon.\n")
    found = _report(tmp_path, capsys)["areas"][0]["sources"]["retired_in_current"]
    assert sorted(f["file"] for f in found) == [f"docs/{d}/page.md" for d in ("explanation", "how-to", "reference", "tutorial")]


def test_sources_section_renders_without_docs(tmp_path, capsys):
    _area(tmp_path / "a")
    assert "no sources and no docs to check" in _doctor(tmp_path, capsys)
