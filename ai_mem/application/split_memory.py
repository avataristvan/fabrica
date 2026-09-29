"""SplitMemoryUseCase — break coarse entries into focused sub-entries via Claude."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.detect_split_hints import SPLIT_MIN_TEXT_CHARS
from ai_mem.domain.memory import MemoryEntry, MemoryRepository

_MODEL = "claude-haiku-4-5-20251001"
_SKIP_REASON_MAX = 200  # truncation limit for CalledProcessError messages

_DECISION_TYPES = ("domain", "pattern", "anti-pattern")

_SPLIT_PROMPT = """\
Analyse the following memory entry and choose exactly one of two splits.

A) LEARNING + DECISION -- use this only if the entry mixes an observation (what was seen, measured or
found, and why) with a decision (what to do or not do because of it). Produce exactly one part of
kind "learning" and exactly one part of kind "decision":
  - "learning": text in the form "Observed: ... Cause: ... Evidence: ..." (only facts, no directive).
  - "decision": the rewritten directive in the form "Decision: ... Why: ... Scope: ...", where Why
    summarises the learning. Its "type" is one of "domain", "pattern", "anti-pattern".
  - The decision part's id MUST be exactly the original ID. The learning id is "<original_id>_learning".

B) TOPICS -- otherwise, split into 2-3 focused sub-entries, each covering a distinct, independent
sub-topic. Every part has kind "topic". Derive sub-IDs from the original ID
("<original_id>_1", "<original_id>_2", ...).

Keep each part self-contained and concise. Return valid JSON only -- no prose, no markdown fences.
Format:
[
  {{"kind": "learning" | "decision" | "topic", "id": "...", "text": "...", "type": "<decision only>"}}
]

Entry ID: {id}
Entry text:
{text}"""


@dataclass
class SplitResult:
    original_id: str
    new_ids: list[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""


class SplitMemoryUseCase:
    def __init__(
        self,
        repo: MemoryRepository,
        add_uc: AddMemoryUseCase,
        add_edge_uc: AddEdgeUseCase,
        model: str = _MODEL,
    ) -> None:
        self._repo = repo
        self._add_uc = add_uc
        self._add_edge_uc = add_edge_uc
        self._model = model

    def execute(self, collection: str, entry_id: str | None = None) -> list[SplitResult]:
        """Split one entry by ID, or all hinted entries in the collection when entry_id is None."""
        if entry_id:
            entries = self._repo.get_by_ids(collection, [entry_id])
        else:
            entries = [
                entry for entry in self._repo.get_all(collection)
                if len(entry.text) >= SPLIT_MIN_TEXT_CHARS
            ]

        return [self._split_one(collection, entry) for entry in entries]

    def _split_one(self, collection: str, entry: MemoryEntry) -> SplitResult:
        prompt = _SPLIT_PROMPT.format(id=entry.id, text=entry.text)
        try:
            raw = subprocess.run(
                ["claude", "--print", "--model", self._model],
                input=prompt,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except subprocess.CalledProcessError as exc:
            return SplitResult(
                original_id=entry.id,
                skipped=True,
                skip_reason=f"claude CLI error (exit {exc.returncode}): {exc.stderr.strip()[:_SKIP_REASON_MAX]}",
            )
        except FileNotFoundError:
            return SplitResult(
                original_id=entry.id,
                skipped=True,
                skip_reason="claude CLI not found — ensure claude is on PATH",
            )

        try:
            sub_entries = _parse_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            return SplitResult(
                original_id=entry.id,
                skipped=True,
                skip_reason=f"JSON parse error: {exc}",
            )

        kinds = {item.get("kind", "topic") for item in sub_entries}
        if kinds <= {"topic"}:
            return self._split_topics(collection, entry, sub_entries)
        return self._split_learning_decision(collection, entry, sub_entries)

    def _split_topics(self, collection: str, entry: MemoryEntry, sub_entries: list[dict]) -> SplitResult:
        self._repo.delete(collection, [entry.id])
        new_ids = [item["id"] for item in sub_entries]
        self._add_uc.execute(
            collection=collection,
            documents=[item["text"] for item in sub_entries],
            ids=new_ids,
        )
        return SplitResult(original_id=entry.id, new_ids=new_ids)

    def _split_learning_decision(
        self, collection: str, entry: MemoryEntry, parts: list[dict],
    ) -> SplitResult:
        """The original id stays the decision (rewritten, metadata and edges kept); it is never deleted."""
        decisions = [p for p in parts if p.get("kind") == "decision"]
        learnings = [p for p in parts if p.get("kind") == "learning"]
        if len(decisions) != 1 or not learnings or len(decisions) + len(learnings) != len(parts):
            return _skipped(entry, "learning/decision split needs exactly one decision and at least one learning")

        learning_ids = [p["id"] for p in learnings]
        if entry.id in learning_ids or len(set(learning_ids)) != len(learning_ids):
            return _skipped(entry, f"invalid learning ids: {learning_ids}")
        taken = [existing.id for existing in self._repo.get_by_ids(collection, learning_ids)]
        if taken:
            return _skipped(entry, f"learning id(s) already exist, refusing to overwrite: {taken}")

        decision = decisions[0]
        decision_type = entry.metadata.get("type")
        if decision_type not in _DECISION_TYPES:
            decision_type = decision.get("type") if decision.get("type") in _DECISION_TYPES else "domain"

        learning_meta = {"type": "learning"}
        if "area" in entry.metadata:
            learning_meta["area"] = entry.metadata["area"]

        # Learnings first: if anything fails, the original is untouched and the new learnings are rolled back.
        try:
            self._add_uc.execute(
                collection=collection,
                documents=[p["text"] for p in learnings],
                ids=learning_ids,
                metadatas=[dict(learning_meta) for _ in learnings],
            )
            self._add_uc.execute(
                collection=collection,
                documents=[decision["text"]],
                ids=[entry.id],
                metadatas=[{"type": decision_type}],
            )
            for learning_id in learning_ids:
                self._add_edge_uc.execute(collection, entry.id, learning_id, "derived_from")
        except ValueError as exc:
            self._repo.delete(collection, learning_ids)
            self._add_uc.execute(
                collection=collection, documents=[entry.text], ids=[entry.id], metadatas=[entry.metadata],
            )
            return _skipped(entry, f"learning/decision split failed, rolled back: {exc}")
        return SplitResult(original_id=entry.id, new_ids=learning_ids)


def _skipped(entry: MemoryEntry, reason: str) -> SplitResult:
    return SplitResult(original_id=entry.id, skipped=True, skip_reason=reason)


def _parse_json(raw: str) -> list[dict]:
    """Parse a JSON array from raw text; falls back to extracting between [ and ]."""
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise
        result = json.loads(raw[start : end + 1])
    if not isinstance(result, list):
        raise ValueError(f"expected a JSON array, got {type(result).__name__}")
    for item in result:
        if not isinstance(item, dict) or "id" not in item or "text" not in item:
            raise ValueError(f"each item must have 'id' and 'text' keys, got {item!r}")
    return result
