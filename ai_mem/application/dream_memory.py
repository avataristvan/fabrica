"""DreamMemoryUseCase — consolidate the records of one area via Claude models.

The area key is the repository collection. Dream proposes and never applies: it returns a report
(the models' proposals plus propagation, split and merge-conflict sections) and writes nothing;
the archivist or the user act on it with `mem`. Model output is hostile input: ADD `target=`
area paths are validated through `AreaRefs` before they are reported as propagation candidates.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from typing import get_args

from ai_mem.domain.memory import AreaRefs, EdgeType, MemoryEntry, MemoryRepository, is_area_qualified

# An id as the model writes it, with or without Markdown code backticks around it.
_ID = r"`?([^\s`]+)`?"
_ADD_TARGET_RE = re.compile(
    r"^\s*[-*•]\s+ADD\s+" + _ID + r"\s+\[target=([^\]]+)\]\s*:",
    re.MULTILINE | re.IGNORECASE,
)
_SPLIT_RE = re.compile(r"^\s*[-*•]\s+SPLIT\s+" + _ID + r"\s*:", re.MULTILINE | re.IGNORECASE)
_MERGE_RE = re.compile(r"^\s*[-*•]\s+MERGE\s+" + _ID + r"\s*\+\s*" + _ID + r"\s*:", re.MULTILINE | re.IGNORECASE)

# The edge types the prompt offers for LINK. Derived from EdgeType so a new type cannot drift out
# of sync; 'supersedes' is proposed as its own action (SUPERSEDE) because applying it also flags
# its target, and 'derived_from' is never proposed (a decision's provenance is a human judgment).
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
stays readable as history and is flagged. Both entries must be in the same area.
- Exception: a 'supersedes' edge marks its target as overtaken (shown as superseded_by=<id> on the \
target). The edge does not protect that target from DELETE. Propose DELETE only if \
the successor already carries the full rationale; otherwise leave it as history, or propose an \
UPDATE of the successor that absorbs what is missing.
- Entries covering multiple independent concepts (multiple ## sections, multiple Tried: blocks, \
or 4+ enumerated items that don't build on each other) should be proposed for SPLIT, not MERGE. \
Each sub-entry should cover exactly one concept so queries pull in only what's relevant."""

_AREA_CONTEXT = """\
AREA UNDER REVIEW: {area}

Knowledge is addressed by the area (the folder holding docs/records/), not by collection. An \
entry that recurs across projects belongs in the area of its topic. Use the target= field on ADD \
proposals to express this. Other areas are named by their path relative to the area under review \
(e.g. ../other-area); a record there is written <relative-area-path>:<id>."""

_ACTION_FORMAT = f"""\
Format each action as:
- UPDATE <id>: <what to change>
- MERGE <id1> + <id2>: <into what>
- DELETE <id>: <reason>
- ADD <suggested-id> [target=<area-path>]: <content summary>
- SPLIT <id>: <list the sub-concept titles to split into>
- LINK <source-id> -> <target-id> [type=<edge_type>]: <reason>
  (edge_type: {" | ".join(_LINK_EDGE_TYPES)})
- SUPERSEDE <new-id> -> <old-id>: <reason>

For ADD, set target= to the area of the entry's topic, as a path relative to the area under \
review: "." if it belongs here, otherwise e.g. ../other-area. Anything outside this area is a \
propagation candidate and is written there only as a new file.

For LINK: use when two entries are related but must stay separate. <source-id> is an entry of \
this area; <target-id> may be an entry of another area, written <relative-area-path>:<id>.

For SUPERSEDE: <new-id> replaces <old-id>; both must be in this area. Never propose a SUPERSEDE \
across areas; use LINK [type=related] instead."""

_P_SINGLE = """\
You are a memory consolidation agent. The memories below come from AI assistant sessions \
(stored as text entries with metadata). Analyze them and return a structured, actionable proposal:

1. **Contradictions** — entries that conflict with each other (name entry IDs)
2. **Redundancies** — entries that overlap and could be merged
3. **Stale entries** — entries likely outdated (explain why)
4. **Missing principles** — patterns that emerge across entries but aren't yet documented
5. **Over-broad entries** — entries covering multiple independent concepts that should be split so queries pull in only the relevant piece

{action_format}

{area_context}

MEMORIES:
{memories}"""

_P_HAIKU = """\
You are doing a fast first-pass memory consolidation. Focus on what's obvious:
- Direct contradictions between entries
- Clear redundancies (same fact stated in multiple entries)
- Entries with explicit dates or version references that are likely stale
- Entries whose topic belongs in another area

Be concise. Reference entry IDs explicitly. \
A more capable model will review your output.

{area_context}

MEMORIES:
{memories}"""

_P_SONNET_HIER = """\
You are reviewing a fast first-pass memory consolidation. Deepen and validate it.

- Confirm or correct the first-pass findings
- Add what it missed (subtle contradictions, cross-entry patterns)
- Identify emergent principles across entries not yet documented
- Identify cross-project patterns that belong in another area

{action_format}

{area_context}

MEMORIES:
{memories}

FIRST-PASS ANALYSIS:
{haiku_pass}"""

_P_SONNET_CRITIQUE = """\
You are the second voice in a memory consolidation debate. A faster model gave an initial analysis.
Challenge it: what did it miss? Where is it wrong? What subtle patterns does it overlook?
Also add your own findings. Be direct.

{area_context}

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

{area_context}

INITIAL ANALYSIS:
{haiku_analysis}

CRITIQUE:
{sonnet_critique}

REBUTTAL:
{haiku_rebuttal}"""


def _format_entries(entries: list[MemoryEntry]) -> str:
    parts = []
    for entry in entries:
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
        parts.append(f"[{entry.id}]{meta_str}\n{entry.text}")
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
        "These entries cover multiple independent concepts — consider splitting with `mem_split` (it separates an observation from a decision into learning + decision when the entry mixes both):\n\n"
        + "\n".join(lines)
    )


def select_neighbourhood(entries: list[MemoryEntry], ids: list[str]) -> list[MemoryEntry]:
    """The named entries plus the same-area entries they link to or are linked from (one hop).

    Ids are plain ids of the area: a qualified id (`:`) or an id that is not loaded is refused,
    so a hostile `--neighbourhood` value never reaches a path. Qualified edge targets lead into
    other areas and are not followed.
    """
    by_id = {entry.id: entry for entry in entries}
    for entry_id in ids:
        if is_area_qualified(entry_id):
            raise ValueError(f"--neighbourhood takes plain ids of the area, got {entry_id!r}")
        if entry_id not in by_id:
            raise ValueError(f"--neighbourhood id {entry_id!r} is not a record of this area")
    seeds = set(ids)
    wanted = set(seeds)
    for entry in entries:
        for edge in _edge_targets(entry):
            if entry.id in seeds and edge in by_id:
                wanted.add(edge)
            if edge in seeds:
                wanted.add(entry.id)
    return [entry for entry in entries if entry.id in wanted]


def _edge_targets(entry: MemoryEntry) -> list[str]:
    try:
        return [edge["target_id"] for edge in json.loads(entry.metadata.get("edges") or "[]")]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def _area_add_targets(
    synthesis: str, area_key: str, area_refs: AreaRefs,
) -> tuple[list[tuple[str, str, str]], list[tuple[str, str]]]:
    """Split ADD proposals into (id, target as written, resolved area key) for other existing areas
    and (id, target as written) for targets that are invalid or not an area. The own area is dropped."""
    accepted: list[tuple[str, str, str]] = []
    rejected: list[tuple[str, str]] = []
    for match in _ADD_TARGET_RE.finditer(synthesis):
        entry_id, target = match.group(1), match.group(2).strip()
        resolved = area_refs.resolve_area(area_key, target)
        if resolved is None:
            rejected.append((entry_id, target))
        elif resolved != area_key:
            accepted.append((entry_id, target, resolved))
    return accepted, rejected


class DreamMemoryUseCase:
    def __init__(self, repo: MemoryRepository, area_refs: AreaRefs) -> None:
        self._repo = repo
        self._area_refs = area_refs

    def execute(
        self,
        area: str,
        mode: str,
        neighbourhood: list[str] | None = None,
    ) -> str:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")

        all_entries = self._repo.get_all(area)
        if neighbourhood:
            all_entries = select_neighbourhood(all_entries, neighbourhood)

        if not all_entries:
            return "No memories found."

        memories = _TYPE_RULES + "\n\n---\n\n" + _format_entries(all_entries)
        area_ctx = _AREA_CONTEXT.format(area=area)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        if mode in ("single-haiku", "single-sonnet"):
            synthesis, report = self._run_single(mode.split("-", 1)[1], ts, memories, area_ctx)
        elif mode == "hier":
            synthesis, report = self._run_hier(ts, memories, area_ctx)
        else:
            synthesis, report = self._run_team(ts, memories, area_ctx)

        report += self._area_propagation_report(synthesis, area)

        split_report = _split_candidates(synthesis, all_entries)
        if split_report:
            report += split_report

        conflicts = _check_merge_conflicts(synthesis, _build_edge_index(all_entries))
        if conflicts:
            report += "\n\n---\n\n## ⚠ Merge Conflicts\n\n" + "\n".join(conflicts)

        return report

    def _area_propagation_report(self, synthesis: str, area_key: str) -> str:
        accepted, rejected = _area_add_targets(synthesis, area_key, self._area_refs)
        report = ""
        if accepted:
            lines = "\n".join(f"- `{eid}` → **{target}** (`{key}`)" for eid, target, key in accepted)
            report += (
                "\n\n---\n\n## Propagation Candidates\n\n"
                "These ADD proposals target another area (not applied: write each as a new file "
                "there, e.g. with `mem add`, if confirmed):\n\n" + lines
            )
        if rejected:
            lines = "\n".join(f"- `{eid}` [target={target}]" for eid, target in rejected)
            report += (
                "\n\n---\n\n## Rejected ADD Targets\n\n"
                "These targets are not an existing area path relative to the area under review:\n\n" + lines
            )
        return report

    def _run_single(self, model_key: str, ts: str, memories: str, area_ctx: str) -> tuple[str, str]:
        result = _call(model_key, _P_SINGLE.format(
            memories=memories, area_context=area_ctx, action_format=_ACTION_FORMAT,
        ))
        return result, f"# Dream Log — {ts} — single:{model_key}\n\n{result}"

    def _run_hier(self, ts: str, memories: str, area_ctx: str) -> tuple[str, str]:
        haiku_pass = _call("haiku", _P_HAIKU.format(memories=memories, area_context=area_ctx))
        sonnet_synthesis = _call("sonnet", _P_SONNET_HIER.format(
            memories=memories, area_context=area_ctx, action_format=_ACTION_FORMAT, haiku_pass=haiku_pass,
        ))
        report = (
            f"# Dream Log — {ts} — hier\n\n"
            f"## Haiku: First Pass\n\n{haiku_pass}\n\n---\n\n"
            f"## Sonnet: Synthesis\n\n{sonnet_synthesis}"
        )
        return sonnet_synthesis, report

    def _run_team(self, ts: str, memories: str, area_ctx: str) -> tuple[str, str]:
        haiku_analysis = _call("haiku", _P_HAIKU.format(memories=memories, area_context=area_ctx))
        sonnet_critique = _call("sonnet", _P_SONNET_CRITIQUE.format(
            memories=memories, area_context=area_ctx, haiku_analysis=haiku_analysis,
        ))
        haiku_rebuttal = _call("haiku", _P_HAIKU_REBUTTAL.format(haiku_analysis=haiku_analysis, sonnet_critique=sonnet_critique))
        sonnet_final = _call("sonnet", _P_SONNET_FINAL.format(
            area_context=area_ctx, action_format=_ACTION_FORMAT,
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
