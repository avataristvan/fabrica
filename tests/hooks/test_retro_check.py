"""retro_check: SubagentStop contract (D14) and the retro log schema shared with `mem doctor`."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_mem.hooks import retro_check

FULL = """Work done.

[retro]
learned: nothing new
blocked: none
next: chunk 4c
records_consulted: none
record_candidates: none
"""


@pytest.fixture(autouse=True)
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("AI_MEM_PATH", str(tmp_path))
    return tmp_path


def _event(message: str | None, agent_type: str = "ai-mem:anchor-lint", **extra) -> dict:
    return {"session_id": "s1", "agent_id": "a1", "agent_type": agent_type, "last_assistant_message": message, **extra}


def _log(state: Path) -> list[dict]:
    path = state / "retro_log.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def test_complete_retro_passes_and_logs_the_schema(state: Path) -> None:
    assert retro_check.handle(_event(FULL)) is None
    (entry,) = _log(state)
    assert set(entry) == {"ts", "session_id", "agent_type", "agent_id", "has_retro", "missing",
                          "records_consulted", "record_candidates", "learned"}
    assert entry["has_retro"] is True and entry["missing"] == []
    assert entry["records_consulted"] == "none" and entry["record_candidates"] == "none"
    assert entry["learned"] == "nothing new" and isinstance(entry["ts"], float)


def test_missing_retro_blocks_once_and_logs(state: Path) -> None:
    out = retro_check.handle(_event("Done, no retro."))
    assert out["decision"] == "block"
    assert "records_consulted" in out["reason"] and "record_candidates" in out["reason"]
    (entry,) = _log(state)
    assert entry["has_retro"] is False and entry["missing"] == ["records_consulted", "record_candidates"]
    assert entry["records_consulted"] is None


def test_stop_hook_active_logs_without_blocking(state: Path) -> None:
    assert retro_check.handle(_event("still no retro", stop_hook_active=True)) is None
    assert _log(state)[0]["has_retro"] is False


def test_partial_retro_names_only_the_missing_field(state: Path) -> None:
    out = retro_check.handle(_event("[retro]\nlearned: x\nrecords_consulted: id_a, id_b\n"))
    assert "record_candidates" in out["reason"] and "records_consulted" not in out["reason"]
    entry = _log(state)[0]
    assert entry["has_retro"] is True and entry["missing"] == ["record_candidates"]
    assert entry["records_consulted"] == "id_a, id_b"


def test_multiline_candidates_and_markdown_keys() -> None:
    fields = retro_check.parse_retro("[retro]\n- **learned:** a\n- **records_consulted:** none\n- **record_candidates:**\n  first line\n  second line\n")
    assert fields["record_candidates"] == "first line second line"
    assert fields["records_consulted"] == "none"


def test_empty_field_counts_as_missing() -> None:
    out = retro_check.handle(_event("[retro]\nrecords_consulted:\nrecord_candidates: none\n"))
    assert "records_consulted" in out["reason"]


def test_unlisted_role_produces_no_output_and_no_log(state: Path) -> None:
    assert retro_check.handle(_event("no retro", agent_type="Explore")) is None
    assert _log(state) == []


def test_roles_come_from_the_config_file(state: Path) -> None:
    (state / "retro_roles.json").write_text('["Explore"]')
    assert retro_check.handle(_event("no retro", agent_type="Explore"))["decision"] == "block"
    assert retro_check.handle(_event("no retro", agent_type="the-coder")) is None


def test_malformed_roles_file_falls_back_to_default(state: Path) -> None:
    (state / "retro_roles.json").write_text("{not json")
    assert retro_check.handle(_event("no retro"))["decision"] == "block"


def test_log_values_are_capped(state: Path) -> None:
    retro_check.handle(_event("[retro]\nrecords_consulted: " + "x" * 5000 + "\nrecord_candidates: none\n", agent_id="i" * 500))
    entry = _log(state)[0]
    assert len(entry["records_consulted"]) == 2000 and len(entry["agent_id"]) == 200


def test_unwritable_log_still_blocks(state: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    blocker = state / "file"
    blocker.write_text("x")
    monkeypatch.setenv("AI_MEM_PATH", str(blocker))
    assert retro_check.handle(_event("no retro"))["decision"] == "block"


def test_anchor_lint_is_a_default_retro_role(state: Path) -> None:
    assert "ai-mem:anchor-lint" in retro_check.DEFAULT_ROLES
    assert retro_check.handle(_event("no retro", agent_type="ai-mem:anchor-lint"))["decision"] == "block"


def test_plugin_option_beats_the_config_file(state: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (state / "retro_roles.json").write_text('["the-coder"]')
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_RETRO_ROLES", "Explore, ai-mem:anchor-lint")
    assert retro_check.handle(_event("no retro", agent_type="Explore"))["decision"] == "block"
    assert retro_check.handle(_event("no retro", agent_type="the-coder")) is None


def test_blank_plugin_option_falls_back_to_the_config_file(state: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (state / "retro_roles.json").write_text('["Explore"]')
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_RETRO_ROLES", " , ")
    assert retro_check.handle(_event("no retro", agent_type="Explore"))["decision"] == "block"
