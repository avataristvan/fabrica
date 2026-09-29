"""DreamMemoryUseCase — consolidate memories via Claude models."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import get_args

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.domain.memory import EdgeType, MemoryEntry, MemoryRepository

_DELETE_RE = re.compile(r"^\s*[-*•]\s+DELETE\s+(\S+)\s*:", re.MULTILINE | re.IGNORECASE)
_ADD_TARGET_RE = re.compile(
    r"^\s*[-*•]\s+ADD\s+(\S+)\s+\[target=([^\]]+)\]\s*:",
    re.MULTILINE | re.IGNORECASE,
)
_SPLIT_RE = re.compile(r"^\s*[-*•]\s+SPLIT\s+(\S+)\s*:", re.MULTILINE | re.IGNORECASE)
_MERGE_RE = re.compile(r"^\s*[-*•]\s+MERGE\s+(\S+)\s*\+\s*(\S+)\s*:", re.MULTILINE | re.IGNORECASE)
_LINK_RE = re.compile(
    r"^\s*[-*•]\s+LINK\s+(\S+)\s*->\s*(\S+)\s+\[type=([^\]]+)\]\s*:",
    re.MULTILINE | re.IGNORECASE,
)
_SUPERSEDE_RE = re.compile(r"^\s*[-*•]\s+SUPERSEDE\s+(\S+)\s*->\s*(\S+)\s*:", re.MULTILINE | re.IGNORECASE)

# LINK covers the relational edge types. Derived from EdgeType so a new type cannot drift out of
# sync; 'supersedes' has its own action (SUPERSEDE) because it also flags its target, and
# 'derived_from' is manual only (a decision's provenance is a human judgment, not a dream proposal).
_LINK_EDGE_TYPES = tuple(
    edge_type for edge_type in get_args(EdgeType) if edge_type not in ("supersedes", "derived_from")
)

MODELS = {
    "haiku": "haiku",
    "sonnet": "sonnet",
}

MODES = ("single-haiku", "single-sonnet", "hier", "team")

_TYPE_RULES = """\
TYPE RULES — apply these strictly:
- "pattern": a reusable rule or best practice. Canonical format: Rule: / When: / Why:
- "anti-pattern": a documented failure mode. Canonical format: Tried: / Failed because: / Instead:
- "domain": business/domain knowledge (why a rule exists, a domain constraint) — not a coding \
technique. Canonical format: Decision: / Why: / Scope:
- "feedback", "project", "reference", "user": descriptive entries — no fixed format.

Consolidation constraints:
- NEVER propose MERGE between a "pattern" and an "anti-pattern". They contradict by design. \
If they share an edge (shown in metadata), verify the relationship is accurate — do not collapse it.
- NEVER propose MERGE between a "domain" entry and a "pattern"/"anti-pattern" entry — domain \
knowledge and coding technique are different axes even when they discuss the same code.
- If two entries share an edge, the edge makes both necessary. \
Verify the relationship before proposing structural changes.
- If two related entries have no edge yet, propose LINK to document the relationship explicitly \
instead of leaving it implicit. Prefer LINK over MERGE when the entries have different types or \
already share an edge.
- When an entry has been overtaken by a newer entry that exists on its own (a decision reversed, a \
fact replaced), propose SUPERSEDE <new-id> -> <old-id> instead of DELETE or MERGE: the old entry \
stays readable as history and is flagged. Both entries must be in the same collection.
- Exception: a 'supersedes' edge marks its target as overtaken (shown as superseded_by=<id> on the \
target). The edge does not protect that target from DELETE. Propose DELETE only if \
the successor already carries the full rationale; otherwise leave it as history, or propose an \
UPDATE of the successor that absorbs what is missing.
- Entries covering multiple independent concepts (multiple ## sections, multiple Tried: blocks, \
or 4+ enumerated items that don't build on each other) should be proposed for SPLIT, not MERGE. \
Each sub-entry should cover exactly one concept so queries pull in only what's relevant."""

_COLLECTION_CONTEXT = """\
COLLECTIONS PRESENT:
{collections}

COLLECTION HIERARCHY (lower → higher scope):
  repo.<name>  →  workspace  →  global

A pattern documented in a repo collection that recurs across multiple projects belongs \
in a higher-level collection. Use the target= field on ADD proposals to express this."""

_ACTION_FORMAT = f"""\
Format each action as:
- UPDATE <id>: <what to change>
- MERGE <id1> + <id2>: <into what>
- DELETE <id>: <reason>
- ADD <suggested-id> [target=<collection>]: <content summary>
- SPLIT <id>: <list the sub-concept titles to split into>
- LINK <source-id> -> <target-id> [type=<edge_type>]: <reason>
  (edge_type: {" | ".join(_LINK_EDGE_TYPES)})
- SUPERSEDE <new-id> -> <old-id>: <reason>

For ADD, set target= to the collection where the entry belongs:
  - Same collection as the source entry if it is project-specific.
  - A higher-level collection (workspace or global) if the pattern applies broadly \
across multiple projects — this flags it as a propagation candidate.

For LINK: use when two entries are related but must stay separate (e.g. an anti-pattern \
contradicting a pattern, a fix addressing a cause). Source and target must be in the same collection.

For SUPERSEDE: <new-id> replaces <old-id>; use it when the old entry is overtaken but its \
reasoning is still worth reading. Both ids must be in the same collection."""

_P_SINGLE = """\
You are a memory consolidation agent. The memories below come from AI assistant sessions \
(stored as text entries with metadata). Analyze them and return a structured, actionable proposal:

1. **Contradictions** — entries that conflict with each other (name entry IDs)
2. **Redundancies** — entries that overlap and could be merged
3. **Stale entries** — entries likely outdated (explain why)
4. **Missing principles** — patterns that emerge across entries but aren't yet documented
5. **Over-broad entries** — entries covering multiple independent concepts that should be split so queries pull in only the relevant piece

{action_format}

{collection_context}

MEMORIES:
{memories}"""

_P_HAIKU = """\
You are doing a fast first-pass memory consolidation. Focus on what's obvious:
- Direct contradictions between entries
- Clear redundancies (same fact stated in multiple entries)
- Entries with explicit dates or version references that are likely stale
- Patterns that recur across repo collections and belong in a higher-level collection

Be concise. Reference entry IDs and source collections explicitly. \
A more capable model will review your output.

{collection_context}

MEMORIES:
{memories}"""

_P_SONNET_HIER = """\
You are reviewing a fast first-pass memory consolidation. Deepen and validate it.

- Confirm or correct the first-pass findings
- Add what it missed (subtle contradictions, cross-entry patterns)
- Identify emergent principles across entries not yet documented
- Identify cross-project patterns that should propagate to workspace or global

{action_format}

{collection_context}

MEMORIES:
{memories}

FIRST-PASS ANALYSIS:
{haiku_pass}"""

_P_SONNET_CRITIQUE = """\
You are the second voice in a memory consolidation debate. A faster model gave an initial analysis.
Challenge it: what did it miss? Where is it wrong? What subtle patterns does it overlook?
Also add your own findings. Be direct.

{collection_context}

MEMORIES:
{memories}

INITIAL ANALYSIS:
{haiku_analysis}"""

_P_HAIKU_REBUTTAL = """\
You gave an initial memory analysis. A more capable model critiqued it. Respond:
- Defend what you got right
- Concede where the critique is valid
- Add anything this exchange surfaced

YOUR INITIAL ANALYSIS:
{haiku_analysis}

CRITIQUE:
{sonnet_critique}"""

_P_SONNET_FINAL = """\
Synthesize the best insights from this full debate into one clean, actionable proposal.

{action_format}

{collection_context}

INITIAL ANALYSIS:
{haiku_analysis}

CRITIQUE:
{sonnet_critique}

REBUTTAL:
{haiku_rebuttal}"""


def _format_entries(entries: list[MemoryEntry]) -> str:
    parts = []
    for entry in entries:
        col = entry.metadata.get("_collection", "?")
        shown: dict[str, object] = {}
        if entry_type := entry.metadata.get("type"):
            shown["type"] = entry_type
        if raw_edges := entry.metadata.get("edges"):
            try:
                edges = json.loads(raw_edges)
                if edges:
                    shown["edges"] = [f"{ed['target_id']}({ed['edge_type']})" for ed in edges]
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        if superseded_by := entry.metadata.get("superseded_by"):
            shown["superseded_by"] = superseded_by
        meta_str = (
            " [" + ", ".join(f"{key}={val}" for key, val in shown.items()) + "]"
            if shown else ""
        )
        parts.append(f"[{entry.id}] (collection: {col}){meta_str}\n{entry.text}")
    return "\n\n---\n\n".join(parts) if parts else "(empty)"


def _build_edge_index(entries: list[MemoryEntry]) -> dict[tuple[str, str], str]:
    """Return {(source_id, target_id): edge_type} from the loaded entries' metadata.

    A `superseded_by` flag also yields a (successor, entry) 'supersedes' pair, so the merge guard
    still sees a supersession whose edge was never written (e.g. flagged by hand).
    """
    index: dict[tuple[str, str], str] = {}
    for entry in entries:
        try:
            for edge in json.loads(entry.metadata.get("edges", "[]")):
                index[(entry.id, edge["target_id"])] = edge["edge_type"]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        if successor := entry.metadata.get("superseded_by"):
            index[(successor, entry.id)] = "supersedes"
    return index


def _check_merge_conflicts(synthesis: str, edge_index: dict[tuple[str, str], str]) -> list[str]:
    """Warn about MERGE proposals whose two entries share a `contradicts` or `supersedes` edge."""
    warnings = []
    for match in _MERGE_RE.finditer(synthesis):
        first, second = match.group(1), match.group(2)
        edge_types = {edge_index.get((first, second)), edge_index.get((second, first))}
        if "contradicts" in edge_types:
            warnings.append(
                f"⚠ MERGE {first} + {second} conflicts with an existing `contradicts` edge — "
                f"use LINK to document the relationship instead."
            )
        elif "supersedes" in edge_types:
            warnings.append(
                f"⚠ MERGE {first} + {second}: one entry supersedes the other — merging would erase the "
                f"history. Keep the old entry as flagged history, or DELETE it once the successor "
                f"carries the full rationale."
            )
    return warnings


def _parse_link_proposals(synthesis: str) -> list[tuple[str, str, str]]:
    """Return (source_id, target_id, edge_type) for each LINK proposal in the synthesis."""
    return [(m.group(1), m.group(2), m.group(3).strip()) for m in _LINK_RE.finditer(synthesis)]


def _parse_supersede_proposals(synthesis: str) -> list[tuple[str, str]]:
    """Return (new_id, old_id) for each SUPERSEDE proposal in the synthesis."""
    return [(m.group(1), m.group(2)) for m in _SUPERSEDE_RE.finditer(synthesis)]


def _shared_collection(id_to_cols: dict[str, set[str]], source_id: str, target_id: str) -> tuple[str | None, str]:
    """Return (collection, "") when both ids live in exactly one common collection, else
    (None, reason). Edges are stored per collection, so a link across collections cannot exist."""
    if source_id not in id_to_cols:
        return None, f"unknown id '{source_id}'"
    if target_id not in id_to_cols:
        return None, f"unknown id '{target_id}'"
    shared = id_to_cols[source_id] & id_to_cols[target_id]
    if not shared:
        return None, "the entries are in different collections (edges cannot span collections)"
    if len(shared) > 1:
        return None, f"both ids exist in several collections ({', '.join(sorted(shared))}) — ambiguous"
    return next(iter(shared)), ""


def _call(model_key: str, prompt: str) -> str:
    result = subprocess.run(
        ["claude", "--print", "--model", MODELS[model_key]],
        input=prompt,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "(no output on stdout/stderr)"
        raise RuntimeError(
            f"claude CLI failed (model={MODELS[model_key]!r}, exit={result.returncode}): {detail}"
        )
    return result.stdout.strip()


def _collection_context(collections: list[str]) -> str:
    return _COLLECTION_CONTEXT.format(collections="\n".join(f"  - {col_name}" for col_name in collections))


def _pull_through_report(entries: list[MemoryEntry], log_path: Path) -> str:
    """Return a markdown report of what fraction of pushed (userprompt_hook-injected) ids were
    later deliberately used, per collection (the data that decides whether a push hook is worth keeping).

    "Deliberately used" means last_accessed_at (bumped only by mem_get, a positive mem_boost, or
    a strong PostToolUse match) moved past the push
    timestamp. Entries deleted since their push, or never accessed at all, count as not pulled.
    Returns an empty string if no push events are logged for any collection in `entries`.
    """
    from ai_mem.injection_log import load_events

    by_key: dict[tuple[str, str], MemoryEntry] = {}
    collections: set[str] = set()
    for entry in entries:
        col = entry.metadata.get("_collection")
        if col:
            by_key[(col, entry.id)] = entry
            collections.add(col)

    rows: list[tuple[str, int, int]] = []  # (collection, pulled, total)
    for col in sorted(collections):
        events = load_events(log_path, col)
        if not events:
            continue
        pulled = 0
        total = 0
        for event in events:
            entry = by_key.get((col, event.get("id")))
            if entry is None:
                continue  # deleted since the push -- unresolvable, excluded from both counts
            total += 1
            last_accessed = float(entry.metadata.get("last_accessed_at", 0) or 0)
            if last_accessed > event.get("ts", 0):
                pulled += 1
        if total == 0:
            continue
        rows.append((col, pulled, total))

    if not rows:
        return ""

    sections = [
        "---",
        "",
        "## Pull-Through Report",
        "",
        "Of the ids userprompt_hook pushed into context, the fraction later deliberately used "
        "(mem_get, positive mem_boost, or a strong PostToolUse match):",
        "",
    ]
    for col, pulled, total in rows:
        pct = 100.0 * pulled / total
        sections.append(f"- `{col}`: {pulled}/{total} pushed ids later pulled ({pct:.1f}%)")
    return "\n".join(sections)


def _split_candidates(synthesis: str, all_entries: list[MemoryEntry]) -> str:
    """Return a formatted section listing SPLIT proposals from the synthesis, or empty string."""
    id_to_preview: dict[str, str] = {entry.id: entry.text[:60].replace("\n", " ") for entry in all_entries}
    found = _SPLIT_RE.findall(synthesis)
    if not found:
        return ""
    lines = []
    for eid in found:
        preview = id_to_preview.get(eid, "")
        preview_str = f" — {preview}…" if preview else ""
        lines.append(f"- `{eid}`{preview_str}")
    return (
        "\n\n---\n\n## Split Candidates\n\n"
        "These entries cover multiple independent concepts — consider splitting with `mem_split`:\n\n"
        + "\n".join(lines)
    )


def _propagation_candidates(synthesis: str, source_collections: set[str]) -> list[tuple[str, str]]:
    """Return (entry_id, target_collection) pairs where target differs from all source collections."""
    candidates = []
    for match in _ADD_TARGET_RE.finditer(synthesis):
        entry_id, target = match.group(1), match.group(2).strip()
        if target not in source_collections:
            candidates.append((entry_id, target))
    return candidates


class DreamMemoryUseCase:
    def __init__(self, repo: MemoryRepository, injection_log_path: Path | None = None) -> None:
        self._repo = repo
        self._injection_log_path = injection_log_path

    def execute(
        self,
        collection: str | None,
        mode: str,
        auto_delete: bool = False,
        focus_hint: str | None = None,
        collections_filter: list[str] | None = None,
        auto_link: bool = False,
        auto_supersede: bool = False,
    ) -> str:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")

        if collections_filter is not None:
            collections = collections_filter
        elif collection:
            collections = [collection]
        else:
            collections = [col_info.name for col_info in self._repo.list_collections()]

        all_entries = []
        for col in collections:
            entries = self._repo.get_all(col)
            for entry in entries:
                entry.metadata["_collection"] = col
            all_entries.extend(entries)

        if not all_entries:
            return "No memories found."

        preamble_parts = [_TYPE_RULES]
        if focus_hint:
            preamble_parts.append(f"FOCUS:\n{focus_hint}")
        memories = "\n\n".join(preamble_parts) + "\n\n---\n\n" + _format_entries(all_entries)
        col_ctx = _collection_context(collections)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        if mode in ("single-haiku", "single-sonnet"):
            synthesis, report = self._run_single(mode.split("-", 1)[1], ts, memories, col_ctx)
        elif mode == "hier":
            synthesis, report = self._run_hier(ts, memories, col_ctx)
        else:
            synthesis, report = self._run_team(ts, memories, col_ctx)

        propagation = _propagation_candidates(synthesis, set(collections))
        if propagation:
            lines = "\n".join(f"- `{eid}` → **{target}**" for eid, target in propagation)
            report += (
                "\n\n---\n\n## Propagation Candidates\n\n"
                "These ADD proposals target a higher-level collection "
                "(review and apply with `mem_add` if confirmed):\n\n" + lines
            )

        split_report = _split_candidates(synthesis, all_entries)
        if split_report:
            report += split_report

        if self._injection_log_path is not None:
            pull_report = _pull_through_report(all_entries, self._injection_log_path)
            if pull_report:
                report += "\n\n" + pull_report

        conflicts = _check_merge_conflicts(synthesis, _build_edge_index(all_entries))
        if conflicts:
            report += "\n\n---\n\n## ⚠ Merge Conflicts\n\n" + "\n".join(conflicts)

        if auto_link:
            proposals = _parse_link_proposals(synthesis)
            report += self._edge_report("Links", "LINK", proposals, all_entries, allowed_types=_LINK_EDGE_TYPES)

        if auto_supersede:
            proposals = [(new_id, old_id, "supersedes") for new_id, old_id in _parse_supersede_proposals(synthesis)]
            report += self._edge_report("Supersessions", "SUPERSEDE", proposals, all_entries)

        if auto_delete:
            deleted = self._auto_apply_deletes(synthesis, all_entries)
            if deleted:
                report += "\n\n---\n\n## Auto-Applied Deletions\n\n" + "\n".join(
                    f"- Deleted `{deleted_id}`" for deleted_id in deleted
                )
            else:
                report += "\n\n---\n\n## Auto-Applied Deletions\n\nNone (no high-confidence DELETE actions found)."

        return report

    def _run_single(self, model_key: str, ts: str, memories: str, col_ctx: str) -> tuple[str, str]:
        result = _call(model_key, _P_SINGLE.format(
            memories=memories, collection_context=col_ctx, action_format=_ACTION_FORMAT,
        ))
        return result, f"# Dream Log — {ts} — single:{model_key}\n\n{result}"

    def _run_hier(self, ts: str, memories: str, col_ctx: str) -> tuple[str, str]:
        haiku_pass = _call("haiku", _P_HAIKU.format(memories=memories, collection_context=col_ctx))
        sonnet_synthesis = _call("sonnet", _P_SONNET_HIER.format(
            memories=memories, collection_context=col_ctx, action_format=_ACTION_FORMAT, haiku_pass=haiku_pass,
        ))
        report = (
            f"# Dream Log — {ts} — hier\n\n"
            f"## Haiku: First Pass\n\n{haiku_pass}\n\n---\n\n"
            f"## Sonnet: Synthesis\n\n{sonnet_synthesis}"
        )
        return sonnet_synthesis, report

    def _run_team(self, ts: str, memories: str, col_ctx: str) -> tuple[str, str]:
        haiku_analysis = _call("haiku", _P_HAIKU.format(memories=memories, collection_context=col_ctx))
        sonnet_critique = _call("sonnet", _P_SONNET_CRITIQUE.format(
            memories=memories, collection_context=col_ctx, haiku_analysis=haiku_analysis,
        ))
        haiku_rebuttal = _call("haiku", _P_HAIKU_REBUTTAL.format(haiku_analysis=haiku_analysis, sonnet_critique=sonnet_critique))
        sonnet_final = _call("sonnet", _P_SONNET_FINAL.format(
            collection_context=col_ctx, action_format=_ACTION_FORMAT,
            haiku_analysis=haiku_analysis, sonnet_critique=sonnet_critique, haiku_rebuttal=haiku_rebuttal,
        ))
        report = (
            f"# Dream Log — {ts} — team\n\n"
            f"## Haiku: Initial Analysis\n\n{haiku_analysis}\n\n---\n\n"
            f"## Sonnet: Critique\n\n{sonnet_critique}\n\n---\n\n"
            f"## Haiku: Rebuttal\n\n{haiku_rebuttal}\n\n---\n\n"
            f"## Sonnet: Final Synthesis\n\n{sonnet_final}"
        )
        return sonnet_final, report

    def _edge_report(self, title: str, action: str, proposals: list[tuple[str, str, str]],
                     all_entries: list[MemoryEntry], allowed_types: tuple[str, ...] | None = None) -> str:
        """Apply (source, target, edge_type) proposals via AddEdgeUseCase and render a report section.

        Nothing is dropped silently: every proposal that could not be applied is listed with its
        reason (invalid type, unknown id, ids in different collections, or the use case's own error).
        """
        id_to_cols: dict[str, set[str]] = {}
        for entry in all_entries:
            id_to_cols.setdefault(entry.id, set()).add(entry.metadata["_collection"])

        applied: list[str] = []
        skipped: list[str] = []
        for source_id, target_id, edge_type in proposals:
            label = f"`{source_id} -> {target_id}`" + ("" if edge_type == "supersedes" else f" [{edge_type}]")
            if allowed_types is not None and edge_type not in allowed_types:
                skipped.append(f"- {label}: invalid edge type (expected one of {', '.join(allowed_types)})")
                continue
            collection, reason = _shared_collection(id_to_cols, source_id, target_id)
            if collection is None:
                skipped.append(f"- {label}: {reason}")
                continue
            try:
                AddEdgeUseCase(self._repo).execute(collection, source_id, target_id, edge_type)
            except Exception as exc:  # ValueError from the use case, or a repository failure
                skipped.append(f"- {label}: {exc}")
                continue
            applied.append(f"- Applied {label} in `{collection}`")

        if not proposals:
            return f"\n\n---\n\n## Auto-Applied {title}\n\nNone (no {action} actions found)."
        section = f"\n\n---\n\n## Auto-Applied {title}\n\n" + ("\n".join(applied) if applied else "None applied.")
        if skipped:
            section += f"\n\n### Skipped {title}\n\n" + "\n".join(skipped)
        return section

    def _auto_apply_deletes(self, synthesis: str, all_entries: list[MemoryEntry]) -> list[str]:
        """Parse DELETE <id>: lines from synthesis and delete matching entries."""
        id_to_col = {entry.id: entry.metadata["_collection"] for entry in all_entries}
        found_ids = _DELETE_RE.findall(synthesis)
        deleted = []
        for id_ in found_ids:
            col = id_to_col.get(id_)
            if col is None:
                continue
            try:
                self._repo.delete(col, [id_])
                deleted.append(id_)
            except Exception:
                pass
        return deleted
