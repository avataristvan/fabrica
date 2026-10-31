"""Tests for dream_memory ADD target parsing, entry formatting and area mode."""
from __future__ import annotations

import json
import time

from ai_mem.application.dream_memory import (
    _ADD_TARGET_RE,
    _TYPE_RULES,
    _format_entries,
)
from ai_mem.domain.memory import MemoryEntry


def _entry(id: str, text: str, **meta) -> MemoryEntry:
    return MemoryEntry(id=id, text=text, metadata=meta)


# ── _format_entries ───────────────────────────────────────────────────────────

class TestFormatEntries:
    def test_shows_type_metadata(self):
        e = _entry("p1", "Rule: X\nWhen: Y\nWhy: Z", type="pattern")
        out = _format_entries([e])
        assert "type=pattern" in out

    def test_decodes_edges_to_readable_form(self):
        edges = json.dumps([{"target_id": "p2", "edge_type": "contradicts"}])
        e = _entry("ap1", "anti-pattern text", type="anti-pattern", edges=edges)
        out = _format_entries([e])
        assert "p2(contradicts)" in out

    def test_shows_superseded_by_only_when_set(self):
        stale = _entry("old", "old rule", superseded_by="new")
        revived = _entry("undone", "revived rule", superseded_by="")
        out = _format_entries([stale, revived])
        assert "[old] [superseded_by=new]" in out
        assert "superseded_by" not in out.split("---")[1]

    def test_type_rules_exempt_supersedes_target_from_edge_protection(self):
        assert "'supersedes' edge marks its target as overtaken" in _TYPE_RULES

    def test_excludes_raw_timestamps(self):
        e = _entry("e1", "text", created_at=1234567890.0, last_accessed_at=9999.0)
        out = _format_entries([e])
        assert "created_at" not in out
        assert "last_accessed_at" not in out

    def test_empty_edges_field_not_shown(self):
        e = _entry("e2", "text", edges=json.dumps([]))
        out = _format_entries([e])
        assert "edges" not in out

    def test_malformed_edges_silently_skipped(self):
        e = _entry("e3", "text", edges="not-json")
        out = _format_entries([e])
        assert "edges" not in out

    def test_no_metadata_no_brackets(self):
        e = _entry("e4", "plain text")
        out = _format_entries([e])
        assert "[]" not in out
        assert "[e4]" in out

    def test_empty_list_returns_empty_marker(self):
        assert _format_entries([]) == "(empty)"


# ── _TYPE_RULES preamble presence ─────────────────────────────────────────────

class TestTypeRules:
    def test_type_rules_mentions_pattern_format(self):
        assert "Rule:" in _TYPE_RULES
        assert "When:" in _TYPE_RULES
        assert "Why:" in _TYPE_RULES

    def test_type_rules_mentions_anti_pattern_format(self):
        assert "Tried:" in _TYPE_RULES
        assert "Failed because:" in _TYPE_RULES

    def test_type_rules_warns_about_merge_constraint(self):
        assert "MERGE" in _TYPE_RULES
        assert "anti-pattern" in _TYPE_RULES


# ── _ADD_TARGET_RE ────────────────────────────────────────────────────────────

class TestAddTargetRe:
    def test_parses_dash_bullet(self):
        text = "- ADD my_entry [target=global]: some content"
        m = _ADD_TARGET_RE.search(text)
        assert m is not None
        assert m.group(1) == "my_entry"
        assert m.group(2).strip() == "global"

    def test_parses_star_bullet(self):
        text = "* ADD my_entry [target=workspace]: some content"
        m = _ADD_TARGET_RE.search(text)
        assert m is not None
        assert m.group(2).strip() == "workspace"

    def test_parses_dot_bullet(self):
        text = "• ADD my_entry [target=repo.my-app]: some content"
        m = _ADD_TARGET_RE.search(text)
        assert m is not None
        assert m.group(2).strip() == "repo.my-app"

    def test_id_in_markdown_backticks_is_parsed_without_them(self):
        # Sonnet formats ids as `code`; the id must come out bare.
        m = _ADD_TARGET_RE.search("- ADD `my_entry` [target=../other]: some content")
        assert m is not None and m.group(1) == "my_entry"

    def test_case_insensitive(self):
        text = "- add my_entry [target=global]: some content"
        assert _ADD_TARGET_RE.search(text) is not None

    def test_no_match_without_target_field(self):
        text = "- ADD my_entry: some content without target"
        assert _ADD_TARGET_RE.search(text) is None

    def test_no_match_on_delete_line(self):
        text = "- DELETE old_entry: reason"
        assert _ADD_TARGET_RE.search(text) is None

    def test_multiline_finds_all(self):
        text = (
            "- ADD entry_a [target=global]: first\n"
            "- ADD entry_b [target=workspace]: second\n"
            "- ADD entry_c: no target\n"
        )
        matches = _ADD_TARGET_RE.findall(text)
        assert len(matches) == 2
        assert ("entry_a", "global") in matches
        assert ("entry_b", "workspace") in matches


# ── area mode: what is read, the prompt, neighbourhood, CLI dry-run ───────────

import json as _json
import sys as _sys
from unittest.mock import patch as _patch

import pytest as _pytest

from ai_mem.application.add_memory import AddMemoryUseCase as _Add
from ai_mem.application.dream_memory import DreamMemoryUseCase as _Dream, select_neighbourhood
from ai_mem.infrastructure.areas import AreaRefResolver as _Resolver, area_records_dir as _rd
from ai_mem.infrastructure.file_repository import FileMemoryRepository as _Repo


def _mk_area(root):
    (root / "docs" / "records").mkdir(parents=True)
    return str(root.resolve())


def _seed_area(repo, key, ids, edges=None):
    for entry_id in ids:
        meta = {"type": "learning"}
        if edges and entry_id in edges:
            meta["edges"] = _json.dumps([{"target_id": t, "edge_type": "related"} for t in edges[entry_id]])
        _Add(repo).execute(collection=key, documents=[f"Body {entry_id}"], ids=[entry_id], metadatas=[meta])


@_pytest.fixture
def area_setup(tmp_path):
    repo = _Repo(_rd)
    here = _mk_area(tmp_path / "ws" / "here")
    other = _mk_area(tmp_path / "ws" / "other")
    _seed_area(repo, here, ["learning_a", "learning_b", "learning_c", "learning_d"],
               edges={"learning_a": ["learning_b"], "learning_c": ["learning_a"], "learning_d": ["../other:learning_x"]})
    _seed_area(repo, other, ["learning_x"])
    return repo, here, other, tmp_path


class TestAreaMode:
    def test_reads_only_the_named_area_and_uses_the_area_prompt(self, area_setup):
        repo, here, _, _ = area_setup
        prompts = []
        with _patch("ai_mem.application.dream_memory._call", side_effect=lambda m, p: prompts.append(p) or "ok"):
            _Dream(repo, area_refs=_Resolver()).execute(here, "single-haiku")
        prompt = prompts[0]
        assert "[learning_a]" in prompt and "[learning_x]" not in prompt
        assert "the area of its topic" in prompt
        assert "[target=<area-path>]" in prompt
        assert "workspace" not in prompt.split("MEMORIES:")[0].replace("workspace/global", "")
        assert "COLLECTION HIERARCHY" not in prompt

    def test_neighbourhood_is_the_named_ids_plus_one_hop(self, area_setup):
        repo, here, _, _ = area_setup
        entries = repo.get_all(here)
        ids = {entry.id for entry in select_neighbourhood(entries, ["learning_a"])}
        assert ids == {"learning_a", "learning_b", "learning_c"}

    def test_neighbourhood_does_not_follow_qualified_edges(self, area_setup):
        repo, here, _, _ = area_setup
        ids = {entry.id for entry in select_neighbourhood(repo.get_all(here), ["learning_d"])}
        assert ids == {"learning_d"}

    @_pytest.mark.parametrize("bad", ["../other:learning_x", "learning_missing", "../x", "a*", ""])
    def test_neighbourhood_refuses_hostile_or_unknown_ids(self, area_setup, bad):
        repo, here, _, _ = area_setup
        with _pytest.raises(ValueError):
            select_neighbourhood(repo.get_all(here), [bad])

    def test_neighbourhood_limits_the_prompt(self, area_setup):
        repo, here, _, _ = area_setup
        prompts = []
        with _patch("ai_mem.application.dream_memory._call", side_effect=lambda m, p: prompts.append(p) or "ok"):
            _Dream(repo, area_refs=_Resolver()).execute(here, "single-haiku", neighbourhood=["learning_d"])
        assert "[learning_d]" in prompts[0] and "[learning_a]" not in prompts[0]


class TestDreamCliArea:
    def _run(self, argv, tmp_path, monkeypatch):
        import ai_mem.dream_cli as cli
        monkeypatch.setattr(_sys, "argv", ["mem-dream", *argv])
        cli.main()

    def test_dry_run_lists_what_it_would_read_without_calling_claude(self, area_setup, monkeypatch, capsys):
        _, here, _, tmp = area_setup
        with _patch("ai_mem.application.dream_memory._call", side_effect=AssertionError("API call")):
            self._run(["--area", str(tmp / "ws" / "here" / "docs"), "--dry-run"], tmp, monkeypatch)
        out = capsys.readouterr().out
        assert f"area {here}: 4 entries" in out and "learning_a" in out and "learning_x" not in out

    def test_dry_run_with_neighbourhood(self, area_setup, monkeypatch, capsys):
        _, here, _, tmp = area_setup
        self._run(["--area", here, "--neighbourhood", "learning_d", "--dry-run"], tmp, monkeypatch)
        assert f"area {here}: 1 entries" in capsys.readouterr().out

    def test_unknown_neighbourhood_id_exits_1(self, area_setup, monkeypatch):
        _, here, _, tmp = area_setup
        with _pytest.raises(SystemExit) as exc:
            self._run(["--area", here, "--neighbourhood", "nope", "--dry-run"], tmp, monkeypatch)
        assert exc.value.code == 1

    def test_path_without_area_exits_1(self, area_setup, monkeypatch):
        _, _, _, tmp = area_setup
        with _pytest.raises(SystemExit) as exc:
            self._run(["--area", str(tmp / "db"), "--dry-run"], tmp, monkeypatch)
        assert exc.value.code == 1

    def test_area_excludes_collection_and_expert(self, area_setup, monkeypatch):
        _, here, _, tmp = area_setup
        for extra in (["--collection", "x"], ["--expert"]):
            with _pytest.raises(SystemExit) as exc:
                self._run(["--area", here, *extra], tmp, monkeypatch)
            assert exc.value.code == 2

    def test_neighbourhood_needs_area(self, area_setup, monkeypatch):
        _, _, _, tmp = area_setup
        with _pytest.raises(SystemExit) as exc:
            self._run(["--neighbourhood", "x"], tmp, monkeypatch)
        assert exc.value.code == 2

    def test_run_prints_report_and_no_save(self, area_setup, monkeypatch, capsys):
        _, here, _, tmp = area_setup
        with _patch("ai_mem.application.dream_memory._call", return_value="synthesis ok"):
            self._run(["--area", here, "--mode", "single-haiku", "--no-save"], tmp, monkeypatch)
        assert "synthesis ok" in capsys.readouterr().out


def test_call_uses_bare_model_alias_and_surfaces_stderr():
    from ai_mem.application.dream_memory import _call
    done = type("R", (), {"returncode": 1, "stdout": "", "stderr": "boom"})()
    with _patch("ai_mem.application.dream_memory.subprocess.run", return_value=done) as run:
        with _pytest.raises(RuntimeError, match="boom"):
            _call("haiku", "p")
    assert run.call_args.args[0] == ["claude", "--print", "--model", "haiku"]
