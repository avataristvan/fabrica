#!/usr/bin/env python3
"""ai-mem MCP server — thin adapter over the application layer."""
import asyncio
import json
import os
from pathlib import Path

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.boost_confidence import BoostConfidenceUseCase
from ai_mem.application.cleanup_memory import CleanupMemoryUseCase
from ai_mem.application.delete_memory import DeleteMemoryUseCase
from ai_mem.application.detect_split_hints import SPLIT_MIN_TEXT_CHARS, DetectSplitHintsUseCase
from ai_mem.application.dream_memory import DreamMemoryUseCase, MODES
from ai_mem.application.get_edges import GetEdgesUseCase
from ai_mem.application.get_memory import GetMemoryUseCase
from ai_mem.application.list_collections import ListCollectionsUseCase
from ai_mem.application.list_entries import ListEntriesUseCase
from ai_mem.application.list_topics import ListTopicsUseCase
from ai_mem.application.move_memory import MoveMemoryUseCase
from ai_mem.application.query_memory import QueryMemoryUseCase
from ai_mem.application.split_memory import SplitMemoryUseCase
from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.infrastructure.adr_paths import ADR_TYPES, record_collection_root, resolve_repo_root_for_collection
from ai_mem.infrastructure.repository_factory import build_repository, records_enabled
from ai_mem.repo_context import detect_repo_context

DEFAULT_COLLECTION = "workspace"

_db_path = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local" / "share" / "ai-mem"))

if records_enabled():
    # Remember where this session's collection lives, so its record files can be found later
    # from any working directory.
    _ctx = detect_repo_context()
    if _ctx.git_root or _ctx.claude_md_dir:
        record_collection_root(_db_path, _ctx.collection, _ctx.git_root or _ctx.claude_md_dir)
_repo = build_repository(_db_path)

_track_access = TrackAccessUseCase(_repo)
_add = AddMemoryUseCase(_repo)
_query = QueryMemoryUseCase(_repo, _track_access)
_list = ListCollectionsUseCase(_repo)
_delete = DeleteMemoryUseCase(_repo)
_cleanup = CleanupMemoryUseCase(_repo)
_list_entries = ListEntriesUseCase(_repo)
_list_topics = ListTopicsUseCase(_repo)
_detect_split_hints = DetectSplitHintsUseCase()
_dream = DreamMemoryUseCase(_repo)
_add_edge = AddEdgeUseCase(_repo)
_split = SplitMemoryUseCase(_repo, _add, _add_edge)
_get_edges = GetEdgesUseCase(_repo)
# track_access here means "deliberate use": explicit mem_get by id, or a positive mem_boost
# (the /reflect citation signal).
_get_memory = GetMemoryUseCase(_repo, _track_access)
_boost = BoostConfidenceUseCase(_repo, _track_access)
_move = MoveMemoryUseCase(_repo)

server = Server("ai-mem")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="mem_add",
            description=(
                "Store or update record files (one file per id; several documents+ids in one call). "
                "Use the repo collection from session start (e.g. 'repo.ai-mem'), 'global' for knowledge that "
                "applies everywhere, or another project's collection when the user names that project. "
                "Updating an id keeps its type, area, created and edges; a text-only update needs no metadata."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "documents": {"type": "array", "items": {"type": "string"}, "description": "Text entries to store"},
                    "ids": {"type": "array", "items": {"type": "string"}, "description": "Unique ID per entry (used for updates)"},
                    "collection": {"type": "string", "description": f"Collection name (default: '{DEFAULT_COLLECTION}')"},
                    "metadatas": {"type": "array", "items": {"type": "object"}, "description": "Optional metadata per entry"},
                    "ttl_days": {"type": "number", "description": "Ignored by record files (kept for compatibility)"},
                    "type": {"type": "string", "description": "Required for a new id. 'domain': 'Decision: …\\nWhy: …\\nScope: …' (why a rule or constraint exists; store it as soon as it surfaces). 'pattern': 'Rule: …\\nWhen: …\\nWhy: …'. 'anti-pattern': 'Tried: …\\nFailed because: …\\nInstead: …'. 'learning': 'Observed: …\\nCause: …\\nEvidence: …' (a decision based on it links to it via mem_link 'derived_from'). 'todo': open work, one file per todo; close it by deleting it and writing a learning with the commit sha. 'reference': background docs (docs/reference/). The id 'current_focus' (any type) is FOCUS.md, overwritten on every update."},
                    "area": {"type": "string", "description": "Topic folder for records, ^[a-z0-9][a-z0-9_-]*$, default 'general'."},
                },
                "required": ["documents", "ids"],
            },
        ),
        types.Tool(
            name="mem_query",
            description=(
                "Keyword search over a collection's records (term overlap, not semantic). Returns 'results' and "
                "'split_hints'. Candidates only -- read and judge them; for 'why / was this tried' questions "
                "the librarian agent or INDEX.md is usually the better start."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms"},
                    "collection": {"type": "string", "description": f"Collection to search (default: '{DEFAULT_COLLECTION}')"},
                    "n_results": {"type": "integer", "default": 5, "description": "Number of results to return"},
                    "max_age_days": {"type": "number", "description": "Only return entries created within this many days"},
                    "type": {"type": "string", "description": "Only return entries of this type"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="mem_get",
            description="Fetch entries by exact id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ids": {"type": "array", "items": {"type": "string"}, "description": "Entry IDs to fetch"},
                    "collection": {"type": "string", "description": f"Collection name (default: '{DEFAULT_COLLECTION}')"},
                },
                "required": ["ids"],
            },
        ),
        types.Tool(
            name="mem_list",
            description=(
                "Without 'collection': all collections with counts. With it: every entry as {id, title}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection to list entries for (omit to list all collections)"},
                },
            },
        ),
        types.Tool(
            name="mem_context",
            description=(
                "Call this with your working directory to learn which collection to pass to mem_query/mem_add "
                "(subagents receive no SessionStart output). Git worktrees resolve to their main checkout's collection."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cwd": {"type": "string", "description": "Absolute path of your working directory"},
                },
                "required": ["cwd"],
            },
        ),
        types.Tool(
            name="mem_topics",
            description=(
                "A collection's entries as {id, title}, grouped by type."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": f"Collection to group entries for (default: '{DEFAULT_COLLECTION}')"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="mem_delete",
            description="Delete entries (their files) by id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": f"Collection name (default: '{DEFAULT_COLLECTION}')"},
                    "ids": {"type": "array", "items": {"type": "string"}, "description": "Entry IDs to delete"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="mem_move",
            description=(
                "Move entries to another collection with id, text and metadata intact. An id that exists at "
                "the target with different text is reported under 'conflicts', not overwritten. Edges pointing "
                "at a moved entry from the source collection are not updated."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ids": {"type": "array", "items": {"type": "string"}, "description": "Entry IDs to move"},
                    "collection": {"type": "string", "description": f"Source collection (default: '{DEFAULT_COLLECTION}')"},
                    "to_collection": {"type": "string", "description": "Target collection name"},
                },
                "required": ["ids", "to_collection"],
            },
        ),
        types.Tool(
            name="mem_cleanup",
            description=(
                "Legacy (TTL / last-access cleanup). Record files have neither, so this deletes nothing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection to clean (omit for all)"},
                    "stale_after_days": {
                        "type": "number",
                        "description": "Also delete entries not accessed for this many days. Omit to skip stale cleanup.",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="mem_dream",
            description=(
                "Consolidate a collection with Claude (via the claude CLI): finds contradictions, redundancies "
                "and stale entries and returns a proposal (UPDATE, MERGE, DELETE, ADD, SPLIT, LINK, SUPERSEDE). "
                "Nothing is applied unless auto_delete / auto_link / auto_supersede is set."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "Collection to consolidate (omit for all)"},
                    "mode": {
                        "type": "string",
                        "enum": list(MODES),
                        "default": "hier",
                        "description": "Consolidation mode (default: hier)",
                    },
                    "auto_delete": {
                        "type": "boolean",
                        "default": False,
                        "description": "Automatically delete entries identified as safe to remove",
                    },
                    "auto_link": {
                        "type": "boolean",
                        "default": False,
                        "description": "Automatically create the edges proposed by LINK actions",
                    },
                    "auto_supersede": {
                        "type": "boolean",
                        "default": False,
                        "description": "Automatically apply SUPERSEDE actions (old entry is flagged, not deleted)",
                    },
                    "focus_hint": {
                        "type": "string",
                        "description": "Optional instruction to steer consolidation",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="mem_split",
            description=(
                "Split a coarse entry with Claude (omit entry_id to split every hinted entry, "
                f"≥ {SPLIT_MIN_TEXT_CHARS} chars or several sections). Independent topics: 2-3 sub-entries "
                "replace the original. Observation mixed with a decision: the original id becomes the "
                "decision, '<id>_learning' is added and linked via 'derived_from'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": f"Collection to split in (default: '{DEFAULT_COLLECTION}')"},
                    "entry_id": {"type": "string", "description": "ID of a specific entry to split (omit to auto-split all hinted entries)"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="mem_link",
            description=(
                "Add a typed edge source -> target (stored in the source's file). 'supersedes': source "
                "replaces target, which stays readable but is flagged superseded_by (undo: mem_add the target "
                "with metadatas [{\"superseded_by\": \"\", \"valid_until\": \"\"}]). 'confirms': source is later "
                "evidence that target held up. 'derived_from': source decision rests on target learning. "
                "'contradicts' also links an anti-pattern to the rule it violates."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {"type": "string", "description": "ID of the source entry"},
                    "target_id": {"type": "string", "description": "ID of the target entry"},
                    "edge_type": {
                        "type": "string",
                        "enum": ["contradicts", "fixes", "causes", "related", "supersedes", "confirms", "derived_from"],
                        "description": "Relationship type from source to target",
                    },
                    "collection": {"type": "string", "description": f"Collection containing both entries (default: '{DEFAULT_COLLECTION}')"},
                },
                "required": ["source_id", "target_id", "edge_type"],
            },
        ),
        types.Tool(
            name="mem_edges",
            description="List an entry's outgoing edges.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "ID of the entry to inspect"},
                    "collection": {"type": "string", "description": f"Collection containing the entry (default: '{DEFAULT_COLLECTION}')"},
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="mem_boost",
            description=(
                "During /reflect: set an entry's cue -- one sentence naming the situation in which it helps; "
                "it is written into the record file, where the librarian finds it ('' removes it). "
                "Wrong or outdated entries get a mem_link 'contradicts'/'supersedes' instead."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ids": {"type": "array", "items": {"type": "string"}, "description": "Entry IDs to boost"},
                    "cue": {"type": "string", "description": "Situation in which this entry would have helped (one sentence, max 140 chars); empty string clears it"},
                    "collection": {"type": "string", "description": f"Collection name (default: '{DEFAULT_COLLECTION}')"},
                },
                "required": ["ids"],
            },
        ),
    ]


_PATTERN_LINK_THRESHOLD = 0.4
_PATTERN_LINK_MAX = 2
CONTRADICTION_THRESHOLD = 0.75
_CONTRADICTION_UPPER = 0.97  # near-identical embeddings are format artifacts, not semantic contradictions
_CONTRADICTION_MAX = 3


def _suggest_pattern_links(collection: str, documents: list[str], stored_ids: list[str]) -> str:
    """Return a suggestion block for linking anti-pattern entries to related patterns.

    Queries for type=pattern entries similar to each stored document. Returns an
    empty string when no matches exceed the threshold or when the query fails.
    """
    try:
        lines: list[str] = []
        seen_pairs: set[tuple[str, str]] = set()
        for doc, source_id in zip(documents, stored_ids):
            results = _query.execute(
                collection=collection,
                query=doc,
                n_results=_PATTERN_LINK_MAX,
                type_filter="pattern",
            )
            for result in results:
                if result.score < _PATTERN_LINK_THRESHOLD:
                    continue
                pair = (source_id, result.id)
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                preview = result.text[:60].replace("\n", " ")
                lines.append(
                    f'  mem_link(source_id="{source_id}", target_id="{result.id}",'
                    f' edge_type="contradicts", collection="{collection}")'
                )
                lines.append(f"  # {preview}")
        if not lines:
            return ""
        return "💡 Related patterns found — consider linking:\n" + "\n".join(lines)
    except Exception:
        return ""


def _detect_contradictions(collection: str, type_tag: str, documents: list[str]) -> list[dict]:
    """Query the opposite type to find possible contradictions above the threshold.

    Returns a list of {id, score, preview} dicts for hits at or above
    CONTRADICTION_THRESHOLD. Returns an empty list when the query fails.
    """
    opposite = "anti-pattern" if type_tag == "pattern" else "pattern"
    hits: list[dict] = []
    try:
        for doc in documents:
            results = _query.execute(
                collection=collection,
                query=doc,
                n_results=_CONTRADICTION_MAX,
                type_filter=opposite,
            )
            seen_ids = {hit["id"] for hit in hits}
            for result in results:
                if CONTRADICTION_THRESHOLD <= (result.score or 0.0) < _CONTRADICTION_UPPER and result.id not in seen_ids:
                    hits.append({"id": result.id, "score": round(result.score, 2), "preview": result.text[:120]})
    except Exception:
        pass
    return hits


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    collection = arguments.get("collection") or DEFAULT_COLLECTION

    if name == "mem_add":
        metadatas = arguments.get("metadatas")
        type_tag = arguments.get("type")
        area = arguments.get("area")
        if type_tag is not None or area is not None:
            count = len(arguments["documents"])
            if metadatas is None:
                metadatas = [{} for _ in range(count)]
            for meta_entry in metadatas:
                if type_tag is not None:
                    meta_entry.setdefault("type", type_tag)
                if area is not None:
                    meta_entry.setdefault("area", area)
        try:
            count = _add.execute(
                collection=collection,
                documents=arguments["documents"],
                ids=arguments["ids"],
                metadatas=metadatas,
                ttl_days=arguments.get("ttl_days"),
            )
        except ValueError as exc:
            return [types.TextContent(type="text", text=f"Error: {exc}")]
        base_text = f"Stored {count} entry/entries in '{collection}'."

        if type_tag in ADR_TYPES and resolve_repo_root_for_collection(_db_path, collection) is None:
            base_text = (
                f"{base_text}\n\nnote: not persisted as a Markdown file — "
                f"could not resolve a repo root for collection '{collection}' yet."
            )

        if type_tag == "anti-pattern":
            suggestion = _suggest_pattern_links(
                collection=collection,
                documents=arguments["documents"],
                stored_ids=arguments["ids"],
            )
            if suggestion:
                base_text = f"{base_text}\n\n{suggestion}"

        if type_tag in ("pattern", "anti-pattern"):
            contradictions = _detect_contradictions(
                collection=collection,
                type_tag=type_tag,
                documents=arguments["documents"],
            )
            if contradictions:
                base_text = (
                    f"{base_text}\n\npossible_contradictions: "
                    + json.dumps(contradictions, ensure_ascii=False)
                )

        return [types.TextContent(type="text", text=base_text)]

    if name == "mem_query":
        results = _query.execute(
            collection=collection,
            query=arguments["query"],
            n_results=arguments.get("n_results", 5),
            max_age_days=arguments.get("max_age_days"),
            type_filter=arguments.get("type"),
        )
        split_hints = _detect_split_hints.execute(results)
        out = {
            "results": [
                {
                    "rank": result.rank,
                    "id": result.id,
                    "score": result.score,
                    # Top-level so a superseded (stale) hit cannot be mistaken for a current one.
                    **({"superseded_by": result.metadata["superseded_by"]} if result.metadata.get("superseded_by") else {}),
                    "metadata": result.metadata,
                    "text": result.text,
                }
                for result in results
            ],
            "split_hints": [
                {"id": hint.id, "text_preview": hint.text_preview}
                for hint in split_hints
            ],
        }
        return [types.TextContent(type="text", text=json.dumps(out, indent=2, ensure_ascii=False))]

    if name == "mem_get":
        entries = _get_memory.execute(collection, arguments["ids"])
        out = [{"id": entry.id, "text": entry.text, "metadata": entry.metadata} for entry in entries]
        return [types.TextContent(type="text", text=json.dumps(out, indent=2, ensure_ascii=False))]

    if name == "mem_list":
        col_arg = arguments.get("collection")
        if col_arg:
            entries = _list_entries.execute(col_arg)
            return [types.TextContent(type="text", text=json.dumps(entries, indent=2, ensure_ascii=False))]
        cols = _list.execute()
        return [types.TextContent(type="text", text=json.dumps([{"name": col_info.name, "count": col_info.count} for col_info in cols], indent=2))]

    if name == "mem_context":
        cwd = Path(arguments.get("cwd") or "")
        if not cwd.is_absolute() or not cwd.is_dir():
            return [types.TextContent(type="text", text=f"Error: cwd must be an absolute path to an existing directory, got {arguments.get('cwd')!r}")]
        ctx = detect_repo_context(cwd)
        result = {
            "collection": ctx.collection,
            "match": ctx.source,
            "claude_md_dir": str(ctx.claude_md_dir) if ctx.claude_md_dir else None,
            "git_root": str(ctx.git_root) if ctx.git_root else None,
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    if name == "mem_topics":
        topics = _list_topics.execute(collection)
        return [types.TextContent(type="text", text=json.dumps(topics, indent=2, ensure_ascii=False))]

    if name == "mem_delete":
        try:
            affected = _delete.execute(collection=collection, ids=arguments.get("ids"))
        except ValueError as exc:
            return [types.TextContent(type="text", text=f"Error: {exc}")]
        if affected == -1:
            return [types.TextContent(type="text", text=f"Dropped collection '{collection}'.")]
        return [types.TextContent(type="text", text=f"Deleted {affected} entry/entries from '{collection}'.")]

    if name == "mem_move":
        to_collection = arguments["to_collection"]
        try:
            result = _move.execute(from_collection=collection, to_collection=to_collection, ids=arguments["ids"])
        except ValueError as exc:
            return [types.TextContent(type="text", text=f"Error: {exc}")]
        lines = [f"Moved {len(result.moved_ids)} entry/entries from '{collection}' to '{to_collection}'."]
        if result.not_found_ids:
            lines.append(f"not_found: {result.not_found_ids}")
        if result.conflicts:
            lines.append("conflicts: " + json.dumps(
                [{"id": c.id, "existing_text_preview": c.existing_text_preview, "source_text_preview": c.source_text_preview} for c in result.conflicts],
                ensure_ascii=False,
            ))
        return [types.TextContent(type="text", text="\n".join(lines))]

    if name == "mem_cleanup":
        col_arg = arguments.get("collection")
        result = _cleanup.execute(col_arg, stale_after_days=arguments.get("stale_after_days"))
        detail = json.dumps(
            {col_name: {"expired": col_stats.expired, "stale": col_stats.stale} for col_name, col_stats in result.collections.items()},
            indent=2,
        )
        return [types.TextContent(type="text", text=f"Cleaned up {result.total} entry/entries.\n{detail}")]

    if name == "mem_dream":
        mode = arguments.get("mode") or "hier"
        col_arg = arguments.get("collection") or None
        auto_delete = bool(arguments.get("auto_delete", False))
        focus_hint = arguments.get("focus_hint") or None
        result = await asyncio.to_thread(
            _dream.execute, col_arg, mode, auto_delete, focus_hint,
            auto_link=bool(arguments.get("auto_link", False)),
            auto_supersede=bool(arguments.get("auto_supersede", False)),
        )
        return [types.TextContent(type="text", text=result)]

    if name == "mem_split":
        entry_id = arguments.get("entry_id") or None
        results = await asyncio.to_thread(_split.execute, collection, entry_id)
        out = [
            {
                "original_id": result.original_id,
                "new_ids": result.new_ids,
                "skipped": result.skipped,
                **({"skip_reason": result.skip_reason} if result.skipped else {}),
            }
            for result in results
        ]
        total = len(results)
        succeeded = sum(1 for result in results if not result.skipped)
        summary = f"Split {succeeded}/{total} entries."
        return [types.TextContent(type="text", text=f"{summary}\n{json.dumps(out, indent=2)}")]

    if name == "mem_link":
        try:
            _add_edge.execute(
                collection=collection,
                source_id=arguments["source_id"],
                target_id=arguments["target_id"],
                edge_type=arguments["edge_type"],
            )
            return [types.TextContent(
                type="text",
                text=f"Linked '{arguments['source_id']}' --[{arguments['edge_type']}]--> '{arguments['target_id']}' in '{collection}'.",
            )]
        except ValueError as exc:
            return [types.TextContent(type="text", text=f"Error: {exc}")]

    if name == "mem_edges":
        edges = _get_edges.execute(
            collection=collection,
            entry_id=arguments["entry_id"],
        )
        out = [{"target_id": edge.target_id, "edge_type": edge.edge_type} for edge in edges]
        return [types.TextContent(type="text", text=json.dumps(out, indent=2))]

    if name == "mem_boost":
        col = arguments.get("collection") or DEFAULT_COLLECTION
        ids = arguments["ids"]
        # 'delta' is no longer read: dropped from the schema, but a caller/skill still sending
        # it (backward compat) is silently ignored rather than rejected.
        try:
            boosted = _boost.execute(col, ids, cue=arguments.get("cue"))
        except ValueError as exc:
            return [types.TextContent(type="text", text=f"Error: {exc}")]
        return [types.TextContent(type="text", text=f"Boosted {boosted} entr{'y' if boosted == 1 else 'ies'} in '{col}'.")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
