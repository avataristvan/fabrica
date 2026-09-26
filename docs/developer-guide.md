# Developer Guide

## Adding a Use Case

1. Create `ai_mem/application/<domain>.py` with a class named `<Action>UseCase`
2. `__init__` accepts only injected dependencies (repositories, other use cases)
3. Single public method: `execute(self, ...)` — no side effects via globals
4. Wire it up in `server.py` at module load (not inside request handlers)
5. Add MCP tool declaration in `list_tools()` and handler branch in `call_tool()`

Example skeleton:
```python
from ai_mem.domain.memory import MemoryRepository

class MyUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(self, collection: str, ...) -> ...:
        ...
```

## Adding Infrastructure

Add a concrete implementation of a domain Protocol in `ai_mem/infrastructure/`. Never import from `application/` or other infrastructure modules (no cross-infrastructure deps).

## Running Tests

```bash
python -m pytest tests/ -v           # all tests
python -m pytest tests/test_session_stats.py -v  # single file
```

Test fixtures are in `tests/conftest.py`. Infrastructure tests use a real ChromaDB instance in a temp directory.

Run the count yourself rather than trusting a number here — it drifts with every change: `python -m pytest tests/ -q | tail -1`.

## Working with Typed Edges

Link two entries with a typed causal edge:
```
mem_link(source_id="abc", target_id="xyz", edge_type="contradicts", collection="repo.my-project")
```

Available edge types: `contradicts`, `fixes`, `causes`, `related`, `supersedes`, `confirms`.

Query edges for an entry:
```
mem_edges(entry_id="abc", collection="repo.my-project")
```

During `mem_query`, matched entries automatically surface their linked targets (1-hop, budget: 2 entries). Appended entries have `via_edge` and `via_source` in their metadata.

**Primary use case:** link `type=anti-pattern` entries to the `type=pattern` they contradict. When the pattern is retrieved, the anti-pattern is surfaced alongside it.

## Conventions

- All timestamps stored as Unix float in ChromaDB metadata: `created_at`, `expires_at`, `last_accessed_at`. `access_count` (and `confidence`) may still appear as legacy metadata on older entries but are no longer written or read (dropped 2026-09-26 — see CLAUDE.md)
- `mem_delete` with no `ids` returns `-1` (signals full collection drop, not count)
- `QueryMemoryUseCase` returns results in ChromaDB's native cosine order — no re-ranking step, no over-fetch
- Edges are stored as JSON-string in ChromaDB metadata (`edges` field). `_parse_edges()` in `chroma_repository.py` always returns `[]` on parse error.

No ML ranker remains in the codebase (removed 2026-06) — no `RankingFeatures`, `RankerScope`, `NullRanker`, or ranker config file.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_MEM_PATH` | `~/.local/share/ai-mem` | Database location |

## Install / Registration

```bash
python3 install.py          # registers MCP server + hooks in ~/.claude/settings.json
pip install -e .            # editable install (no BM25 hybrid search)
pip install -e ".[hybrid]"  # with BM25 hybrid search (rank_bm25)
pip install -e ".[config]"  # with pyyaml for agents.yaml support
```

## Module Entry Points

```bash
python3 -m ai_mem.server          # MCP server (stdio)
python3 -m ai_mem.hook            # SessionStart hook
python3 -m ai_mem.posttool_hook   # PostToolUse hook (pipe JSON payload on stdin)
```

`userprompt_hook.py` and `pretool_hook.py` still exist and remain directly runnable
(`python3 -m ai_mem.userprompt_hook` / `.pretool_hook`), but `install.py` no longer
registers either — see `docs/hooks.md` for why. There is no `stop_hook.py` module.
