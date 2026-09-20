"""mem_query surfaces `superseded_by` at the top level of a result; mem_link accepts 'supersedes'."""
from __future__ import annotations

import asyncio
import json
from unittest.mock import MagicMock, patch

import ai_mem.server as server_module
from ai_mem.domain.memory import QueryResult


def _call(name: str, arguments: dict, **patches):
    async def _run():
        return await server_module.call_tool(name, arguments)

    contexts = [patch.object(server_module, attr, value) for attr, value in patches.items()]
    for context in contexts:
        context.start()
    try:
        return asyncio.run(_run())
    finally:
        for context in contexts:
            context.stop()


def test_mem_query_marks_superseded_result_at_top_level_only_when_flagged():
    stale = QueryResult(rank=1, id="old", score=0.8, text="old rule", metadata={"superseded_by": "new"})
    current = QueryResult(rank=2, id="cur", score=0.5, text="current rule", metadata={})
    cleared = QueryResult(rank=3, id="undone", score=0.4, text="revived", metadata={"superseded_by": ""})
    query = MagicMock()
    query.execute.return_value = [stale, current, cleared]
    hints = MagicMock()
    hints.execute.return_value = []

    result = _call("mem_query", {"query": "rule", "collection": "col"}, _query=query, _detect_split_hints=hints)

    by_id = {r["id"]: r for r in json.loads(result[0].text)["results"]}
    assert by_id["old"]["superseded_by"] == "new"
    assert "superseded_by" not in by_id["cur"]
    assert "superseded_by" not in by_id["undone"]


def test_mem_link_passes_supersedes_to_use_case():
    add_edge = MagicMock()

    result = _call(
        "mem_link",
        {"source_id": "new", "target_id": "old", "edge_type": "supersedes", "collection": "col"},
        _add_edge=add_edge,
    )

    add_edge.execute.assert_called_once_with(
        collection="col", source_id="new", target_id="old", edge_type="supersedes"
    )
    assert "--[supersedes]-->" in result[0].text


def test_mem_link_schema_lists_supersedes():
    tools = asyncio.run(server_module.list_tools())
    link = next(tool for tool in tools if tool.name == "mem_link")
    assert "supersedes" in link.inputSchema["properties"]["edge_type"]["enum"]
