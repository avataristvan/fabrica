---
type: design-doc
date: 2026-09-25
origin: docs/adr-migration-chunk-plan.md (chunk plan of the ADR migration, in German)
status: processed
---
> Translated from the German original on 2026-10-13; content unchanged.

## What the source says

# ADR migration for ai-mem: chunk plan

Created 2026-09-25 by the `chunk-plan` skill, tech-lead review carried out, plan approved. Background and derivation: `docs/epistemology-framework.md` (section "Comparison: BMAD vs. ai-mem framework") and ai-mem entry `domain_bmad_vs_ai_mem_epistemology_2026_09_25` (collection `repo.ai-mem`).

## Tech-lead review — result

The original plan was **not** "implementable as written". 6 findings, all incorporated below:

1. `ai_mem/dream_cli.py` builds a second, independent repository stack (`_build_repo()`), which the original chunk 4 wiring overlooked — `mem-dream --auto_delete/--auto_link/--auto_supersede` would have silently bypassed the Markdown files. Now a mandatory part of chunk 4.
2. Reusing `AddMemoryUseCase` in chunk 3's `import` is correct for confidence/access_count, but would have silently discarded `created_at` in a real fresh-clone rebuild. Now: an explicit correction upsert after the `AddMemoryUseCase` call, plus a metadata equality test instead of text equality only.
3. The frontmatter field order was not specified as deterministic — it could have broken the "write only on change" diff logic (the core of the confidence-lifecycle solution) through pure dict-key-order churn. Now: fixed field order + `edges` explicitly as a single-line JSON line, with a byte-identity test.
4. The `ADR_TYPES` duplication between chunk 0/1 (deliberate, for a parallel start) had no cleanup chunk assigned — now explicitly chunk 2's scope.
5. Chunk 3 did not say which repository `import` uses — now explicit: bare `ChromaMemoryRepository`, no `MarkdownAdrRepository` wrapper (rationale added).
6. Chunk 4's smoke test would have left a real file in the real ai-mem working tree — now switched to a throwaway test directory.

**Core architecture decision:** new decorator `MarkdownAdrRepository` (`ai_mem/infrastructure/`) that fully implements the existing `MemoryRepository` protocol and sits between `ChromaMemoryRepository` and the optional `BM25MemoryRepository` — no use-case or hook file is touched.

**Confidence-lifecycle answer:** the Markdown file is a derived projection of the Chroma state minus volatile fields (`confidence`/`access_count`/`boost_count`/`last_accessed_at`/`cue` never in the file), with diff-before-write logic.

**Retrieval-trigger answer:** deliberately not solved, only mitigated to a limited extent (files are visible to grep/ls/Read, CLAUDE.md gets a discoverable pointer) — explicitly documented as open, not silently declared solved.

---

## Scope boundary / non-goals — framework vs. storage backend

ai-mem conceptually splits into two almost independent parts:

1. **Framework/specification** — when `/reflect` runs, how confidence moves (the rules, not the storage location), how collections nest (`global → workspace → repo.<name>`), skill prompts (`skills/reflect.md`), hook code (`hook.py`, `posttool_hook.py`, `userprompt_hook.py`, `pretool_hook.py`), agent conventions (orchestrator-as-sole-writer, `[retro]` blocks, expert-agent pattern).
2. **Storage backend** — currently exclusively ChromaDB.

**This migration concerns part (2) only.** It changes nothing in part (1) — no chunk in this plan may edit `skills/*.md`, `hook.py`, `posttool_hook.py`, `userprompt_hook.py`, `pretool_hook.py`, `agent_context.py` or agent-convention text. This is no coincidence, but the core of the architecture decision below: the new layer docks exactly at the `MemoryRepository` protocol boundary (`ai_mem/domain/memory.py`), precisely so that hooks, skills and use-case call signatures stay unchanged — no chunk below needs a signature change at any of these places. The only files touched outside `ai_mem/infrastructure/`/new modules are `ai_mem/server.py` (pure repository wiring — MCP adapter, not framework behaviour), `ai_mem/dream_cli.py` (the same repository wiring), `ai_mem/infrastructure/chroma_repository.py` (one line: `_PERMANENT_TYPES`), `pyproject.toml` (CLI registration), as well as `CLAUDE.md`/`docs/architecture.md`/`docs/decisions/` (documentation, no code).

If it turns out during implementation that a chunk task would after all have to touch hook or skill code, that is a sign of scope creep into the framework part — it then belongs in a separate, future task, not in this plan.

## Architecture decision up front (result of the code exploration)

**Docking point:** New decorator `MarkdownAdrRepository` in `ai_mem/infrastructure/` that fully implements the existing `MemoryRepository` protocol (`ai_mem/domain/memory.py`) and wraps an inner repository — exactly the pattern that `BM25MemoryRepository` already sets (`ai_mem/infrastructure/bm25_repository.py`: thin wrapper, delegates most methods 1:1, overrides only `query()`). No protocol contract is changed, no use-case file in `ai_mem/application/` needs to be touched — the new layer is invisible to `AddMemoryUseCase`, `AddEdgeUseCase`, `BoostConfidenceUseCase` etc., because it docks only at the repository interface.

**Wrapping order in `server.py`:**
```python
_inner_repo = ChromaMemoryRepository(_db_path)
_adr_repo = MarkdownAdrRepository(_inner_repo)   # NEW
_repo = BM25MemoryRepository(_adr_repo)  # if available, otherwise _adr_repo directly
```
Rationale: BM25 reads only `query()`/`get_by_ids()` etc. and passes `upsert`/`delete`/`add_edge` through unchanged (verified in `bm25_repository.py` lines 90-119) — so it does not matter for BM25's correctness, but `MarkdownAdrRepository` must sit closer to Chroma so that its `upsert()`/`delete()`/`add_edge()` see the actual write operations before BM25 reshapes them (read-only).

**Which repository methods get file I/O, which stay pure passthrough:**

| Method | Behaviour |
|---|---|
| `upsert()` | Delegates to inner first. For every entry with `metadata["type"] in {"domain","pattern","anti-pattern"}` and a resolvable repo root: write/update the Markdown file. |
| `delete(ids=[...])` | Query the type of the IDs from inner **before** deleting (not possible afterwards), delete in inner, then remove the associated Markdown files of the ADR types. |
| `delete(ids=None)` | **Deletes NO Markdown files** (explicit safety decision — an accidental `mem_delete()` without `ids` must not recursively clear out git-tracked ADR files). Only the Chroma cache is dropped. |
| `add_edge()` | Delegates to inner, then re-reads the source entry (`inner.get_by_ids`) and resyncs its file if it is an ADR type (for the `edges:` frontmatter line). Updating the target file on `supersedes` happens automatically **via the upsert() call** that `AddEdgeUseCase` itself makes separately on the target (see below) — no special case needed. |
| `query()`, `get_by_ids()`, `list_collections()`, `delete_expired()`, `record_access()`, `get_all()`, `delete_stale()`, `get_edges()` | Pure passthrough to inner, **no** file I/O. This is the concrete implementation of the confidence-lifecycle decision (see below) — `mem_boost`/`record_access` never touch the files. |

**Evidence for the `supersedes` automation:** `AddEdgeUseCase.execute()` (`ai_mem/application/add_edge.py:43-51`) calls `self._repo.add_edge(...)` (source) AND separately `self._repo.upsert(collection, [target])` (target, with `superseded_by`/`valid_until` in `target.metadata`). Since `MarkdownAdrRepository.upsert()` re-serialises from the current metadata on every call, the target file is updated automatically with `superseded_by: <id>`, without `add_edge()` having to touch the target itself.

## Explicit answer to problem (b) — confidence-lifecycle mismatch

**Decision:** The Markdown file is a **derived projection of the current Chroma state, minus volatile fields**. The following metadata fields are **never** written to the file (they stay Chroma-only, not git-versioned): `confidence`, `access_count`, `boost_count`, `last_accessed_at`, `cue`.

The following fields **are** written to the frontmatter (structural, ADR-relevant): `id`, `type`, `created_at`, `superseded_by` (if present), `valid_until` (if present), `edges` (if present, from `get_edges()`/`metadata["edges"]`).

Consequence: `mem_boost` (no matter how often — `current_focus` has `access_count` 183) never touches a file, because `record_access()` and the pure confidence path in `boost_confidence.py` do run through `upsert()` — **here `MarkdownAdrRepository.upsert()` must additionally check whether anything other than the volatile fields changed before it rewrites the file** (diff against the last written file content, not just "type matches"), otherwise every `mem_boost` would touch the file after all. The coder spec for chunk 2 therefore explicitly demands: **before writing, compare the target file content with the newly computed one; write only on an actual content change.** That is the concrete, verifiable criterion, not just a field exclusion list.

In addition: `chroma_repository.py`'s `_PERMANENT_TYPES = {"pattern", "anti-pattern"}` (line 16) does **not** include `domain` — `domain` entries could today be deleted automatically by `mem_cleanup`'s forgetting curve (`delete_stale`). That contradicts the ADR philosophy (decision records are long-lived, replaced by `supersedes`, not discarded through inactivity). **Chunk 2 extends `_PERMANENT_TYPES` by `"domain"`.**

## Explicit answer to problem (a) — retrieval trigger

**Not solved by this migration, deliberately treated that way:** `eval_pull_gap_test_2026_09_20` shows `mem_query` 0 calls in all gap cases; only a CLAUDE.md ID pointer worked. Changing the storage format changes nothing about whether an agent looks things up on its own.

**Deliberately limited mitigation that this plan delivers (no full fix):** ADR files are ordinary repo files under `docs/decisions/*.md` — an agent that searches the repo with `grep`/`ls`/`Read` (the channel that actually worked in the gap test: CLAUDE.md scan, repo grep) comes across them **without** calling `mem_query`. Chunk 5 makes this explicitly usable: a new section in CLAUDE.md points to `docs/decisions/` as a path (analogous to the ID-pointer pattern that demonstrably works), AND it is explicitly documented that the general `mem_query` trigger problem is **not** solved by this. That is the required deliberate chunk decision, not an overlooked point.

## File layout

- Directory: `<repo_root>/docs/decisions/` (default), override via `AI_MEM_ADR_DIR` (repo-root-relative path).
- File name: `<id>.md` — ai-mem IDs are already unique per collection and semantically named (e.g. `domain_bmad_vs_ai_mem_epistemology_2026_09_25`), no additional sequential numbering needed.
- Flat, no subfolder per type (the type is in the frontmatter — simpler, no move handling should `type` ever change).
- `global` and `workspace` collections get **no** file backing (no 1:1 repo root resolvable) — they stay Chroma-only. An explicitly documented scope boundary of this migration, not a gap that arises by accident.

## Explicit answer: where do edges between ADR files live

**Decision: option A — frontmatter edges in every ADR file.** Typed edges (`contradicts`/`fixes`/`causes`/`related`/`supersedes`) are written as a structural field in the frontmatter of every file (`edges`, single-line embedded JSON — see chunk 1, step 3), not as a separate graph index (option B, rejected — drift risk, conceptually a poor fit, because `supersedes`/`contradicts` are deliberate judgments, not facts extractable from text as with graphify's code edges) and not as plain prose (option C, rejected — not machine-queryable).

**Most important clarification:** the frontmatter `edges` line is a **git-durable projection**, not the graph queried at runtime — `mem_query`'s edge traversal continues to read directly from Chroma via `MarkdownAdrRepository`'s pure passthrough; the runtime semantics of `mem_link`/`mem_query` do not change through the migration. The file is only a transport route (git clone/pull) and a fresh-clone recovery source (`mem-adr-sync import` calls `repo.add_edge()` per parsed edge, chunk 3).

**Two follow-up problems, explicitly addressed rather than skipped:**

1. **`mem_dream`'s `auto_link`/`auto_supersede` become file mutations:** they deliberately remain automatically applicable, without new approval logic in the code — the review step already exists for free through the existing git workflow (no step in this plan commits automatically; a file write remains a visible uncommitted change until it is committed under the existing "no `git commit` without an explicit request" convention). Mandatory sentence on this in chunk 4's CLAUDE.md edit.
2. **Backlink integrity on `mem_split`/rename:** explicitly named as a pre-existing gap not newly caused by this migration (CLAUDE.md already documents the same dangling-edge weakness for `mem_move`) — deliberately outside the scope of this migration, anchored as an explicit "also open" sentence in chunk 5's CLAUDE.md section, analogous to the retrieval-trigger non-fix.

The "elegant side effect" (storing meaningful judgments vs. operational telemetry differently) is not a new category, but already covered by the problem-(b) answer above: edges are "rare, deliberate judgments" and thus fall into the same category as text/`superseded_by` (file), not into the telemetry category (Chroma-only).

## Repo-root resolution per collection

`ai_mem/infrastructure/adr_paths.py` (chunk 0) holds a persisted mapping file `<AI_MEM_PATH>/adr_collection_roots.json` (`{"repo.<name>": "/abs/path", ...}`), self-populating: on every server start (`server.py`, chunk 4) `detect_repo_context(Path.cwd())` is called once and its own collection→root assignment is recorded. For `mem_add` calls that explicitly address a **different** project collection, the file is written as soon as any session has already run in that target repo; before that, the write attempt is skipped and `mem_add`'s response text gets an explicit note ("not persisted as file — repo root for 'repo.my-app' not yet known"), so that this is not silent data loss.

---

### Chunk 0: Architecture Prep — repo-root resolution & path conventions

**Scope:** New: `ai_mem/infrastructure/adr_paths.py`, `tests/infrastructure/test_adr_paths.py`, `docs/adr-format.md` (new, documents the frontmatter schema + directory convention).

**Depends on:** none
**Parallelizable with:** Chunk 1

**Implementation steps:**
1. `ADR_TYPES = frozenset({"domain", "pattern", "anti-pattern"})` (single source of truth, imported by chunks 1/2/4, not duplicated).
2. `resolve_repo_root_for_collection(collection: str) -> Path | None`:
   - `collection in ("global", "workspace")` → `None`.
   - Otherwise: read the mapping file `<db_path>/adr_collection_roots.json` (path parameter `db_path: Path`, passed in by the caller — **no** import of `server.py`'s `AI_MEM_PATH` logic, to avoid circular imports; the `adr_paths` functions take `db_path` explicitly). Hit → return it.
   - Otherwise: `from ai_mem.repo_context import detect_repo_context`; call `detect_repo_context(Path.cwd())`; if `.collection == collection` and `.git_root` or `.claude_md_dir` is set (git_root preferred, otherwise claude_md_dir) → return the root AND persist it via `record_collection_root()`.
   - Otherwise `None`.
3. `record_collection_root(db_path: Path, collection: str, root: Path) -> None` — reads/merges/writes the JSON mapping file atomically (write-to-temp-then-rename).
4. `adr_dir_for(db_path: Path, collection: str) -> Path | None` = `resolve_repo_root_for_collection(...) / os.environ.get("AI_MEM_ADR_DIR", "docs/decisions")`, or `None`.
5. `adr_file_path(db_path: Path, collection: str, entry_id: str) -> Path | None`.
6. `docs/adr-format.md`: documents the frontmatter keys (id, type, created, superseded_by, valid_until, edges), the file name convention, the directory override via `AI_MEM_ADR_DIR`, and the explicit list of the volatile fields NOT persisted (confidence/access_count/boost_count/last_accessed_at/cue) with a reference to the confidence-lifecycle section above.
7. Tests: mapping file round trip (write, reload), `global`/`workspace` → always `None`, cache hit vs. fallback via `detect_repo_context` (mocked), missing mapping file → no crash, but `None`/empty dict.

**Exit criterion:** `pytest tests/infrastructure/test_adr_paths.py -v` green; `python -c "from ai_mem.infrastructure.adr_paths import ADR_TYPES, resolve_repo_root_for_collection, record_collection_root, adr_dir_for, adr_file_path"` runs without error.

**Coder prompt core:** This is Chunk 0 of a pre-approved plan. Implement exactly the scope above: a new pure-logic module `ai_mem/infrastructure/adr_paths.py` that resolves a filesystem root for a given ai-mem collection name (for `repo.<name>` collections only; `global`/`workspace` always resolve to `None`), using a self-populating JSON mapping file plus `ai_mem.repo_context.detect_repo_context()` as fallback, and write `docs/adr-format.md` documenting the frontmatter schema. Do not touch any other file, do not implement markdown serialization (that's Chunk 1) or the repository decorator (Chunk 2). Do not replan or expand scope.

---

### Chunk 1: ADR Markdown Serialization (pure text transform)

**Scope:** New: `ai_mem/infrastructure/adr_markdown.py`, `tests/infrastructure/test_adr_markdown.py`.

**Depends on:** none
**Parallelizable with:** Chunk 0

**Implementation steps:**
1. Import `ADR_TYPES` from `ai_mem.infrastructure.adr_paths` (loose coupling — if chunk 0 is not yet merged, define `frozenset({"domain", "pattern", "anti-pattern"})` locally and switch to the shared import in chunk 2; **no blocker for the parallel start**).
2. `@dataclass ParsedAdr: id: str; type: str; text: str; created_at: float | None; superseded_by: str | None; valid_until: float | None; edges: list[dict]`.
3. `serialize(entry_id: str, entry_type: str, text: str, metadata: dict) -> str` — renders frontmatter (only the structural fields from the list above, volatile fields are ignored if passed by accident) + `\n---\n\n` + the raw `text` (the existing `Decision:/Why:/Scope:` resp. `Rule:/When:/Why:` resp. `Tried:/Failed because:/Instead:` format stays unchanged in the body, no reformatting into ADR language).
   **Determinism is a hard must, not just a style hint:** the frontmatter fields are written in a hard-wired, literal order — `id, type, created, superseded_by (if present), valid_until (if present), edges (if present)` — **never** by iterating over the keys of the `metadata` dict (whose order can vary through `{**prior_meta, **user_meta}` merges elsewhere in the code). Without this fixed order the "write only on content change" logic from chunk 2 would be triggered by pure key-order churn although nothing changed semantically.
   `edges` is written as a **single-line embedded JSON** line (`edges: [{"target_id": "...", "edge_type": "..."}]`), exactly as `chroma_repository.py`'s `edges` metadata field is already a JSON string today — **no** multi-line YAML list format.
4. `parse(markdown_text: str) -> ParsedAdr` — robust frontmatter parsing (no full YAML needed, simple `key: value` line parsing is enough, because `edges` is a single-line JSON line). The `edges` value is decoded with `json.loads()`, analogous to `_parse_edges` in `chroma_repository.py`. On parse errors (broken frontmatter, invalid JSON in `edges`) raise a `ValueError` with a clear message, since a broken ADR file should be a team-visible error, not a silent carry-on.
5. Round-trip test: `parse(serialize(id, type, text, metadata))` returns `id`/`type`/`text` identically; `superseded_by`/`edges` survive the round trip.
6. Test: `serialize()` with `metadata` containing `confidence`/`access_count` → these keys do NOT appear in the output.
7. Test: two `serialize()` calls with identical `metadata` content but different Python dict insertion order yield **byte-identical** output.
8. Test: `metadata` with `edges` as a list of `{"target_id": ..., "edge_type": ...}` dicts → the frontmatter contains a single-line JSON line; `parse()` decodes it back into the same list.

**Exit criterion:** `pytest tests/infrastructure/test_adr_markdown.py -v` green, including the test that excludes volatile fields.

**Coder prompt core:** This is Chunk 1 of a pre-approved plan. Implement exactly the scope above: a new pure module `ai_mem/infrastructure/adr_markdown.py` with `serialize()`/`parse()` functions that convert between a `MemoryEntry`'s (id, type, text, metadata) and an ADR-style Markdown file (frontmatter with only structural fields — id/type/created_at/superseded_by/valid_until/edges — followed by the raw entry text unchanged). Volatile fields (confidence, access_count, boost_count, last_accessed_at, cue) must never appear in the frontmatter, even if present in the input metadata dict — verify with a dedicated test. Frontmatter fields MUST be emitted in a fixed literal order (id, type, created, superseded_by, valid_until, edges), never by iterating the metadata dict's own key order — verify with a byte-identical-output test across two differently-ordered input dicts. `edges` is a single embedded JSON line, not multi-line YAML. Do not touch server.py, chroma_repository.py, or any other file. Do not replan or expand scope.

---

### Chunk 2: MarkdownAdrRepository decorator + `_PERMANENT_TYPES` extension

**Scope:** New: `ai_mem/infrastructure/markdown_adr_repository.py`, `tests/infrastructure/test_markdown_adr_repository.py`. Edit: `ai_mem/infrastructure/chroma_repository.py` (line 16: `_PERMANENT_TYPES = {"pattern", "anti-pattern"}` → `{"pattern", "anti-pattern", "domain"}`). Edit (small, explicitly allowed): `ai_mem/infrastructure/adr_markdown.py` — replace the `ADR_TYPES` constant defined locally there as a stopgap in chunk 1 with an import from `ai_mem.infrastructure.adr_paths`.

**Depends on:** Chunk 0, Chunk 1
**Parallelizable with:** Chunk 3

**Implementation steps:**
1. `class MarkdownAdrRepository:` constructor `__init__(self, inner: MemoryRepository, db_path: Path)`.
2. `_sync_file(self, collection, entry) -> None`: resolves the path via `adr_paths.adr_file_path()`; if `None` (type not ADR-relevant or root not resolvable) → no-op. Otherwise: compute the new content via `adr_markdown.serialize()`; **if the file exists, read the current content and compare — write only on a difference**. Create the directory with `parents=True, exist_ok=True`.
3. `upsert()`: `self._inner.upsert(collection, entries)`, then for every entry with `entry.metadata.get("type") in ADR_TYPES`: `_sync_file(collection, entry)`.
4. `delete(collection, ids)`: if `ids` is set: **before** deleting call `self._inner.get_by_ids(collection, ids)`, note the ADR-type entries; `affected = self._inner.delete(collection, ids)`; afterwards delete the file for the noted entries (if present, `missing_ok=True`); return `affected`. If `ids is None`: only `self._inner.delete(collection, None)` — **no file deletion**.
5. `add_edge()`: `self._inner.add_edge(collection, source_id, edge)`, then `entries = self._inner.get_by_ids(collection, [source_id])`; if ADR type → `_sync_file(collection, entries[0])`.
6. Remaining protocol methods: 1-line passthrough to `self._inner`, exactly in the style of `bm25_repository.py` lines 93-118 — **no** file I/O in these methods.
7. Adjust `chroma_repository.py` line 16: add `domain` to `_PERMANENT_TYPES`.
8. Tests (with a simple in-memory fake for `inner: MemoryRepository`, `tmp_path` as `db_path`): `upsert()` with `type="domain"` writes a file; `upsert()` with `type="feedback"` writes no file; two `upsert()` calls with only a changed `confidence` → file content/mtime unchanged; `delete(ids=[...])` removes the file; `delete(ids=None)` leaves files untouched; `add_edge(edge_type="supersedes")` simulation updates the target file; a `chroma_repository.py` test confirms `domain` in `_PERMANENT_TYPES`.

**Exit criterion:** `pytest tests/infrastructure/ -v` fully green, including the new file and the extension in `test_chroma_repository.py`.

**Coder prompt core:** This is Chunk 2 of a pre-approved plan. Implement exactly the scope above: a new `MarkdownAdrRepository` class in `ai_mem/infrastructure/markdown_adr_repository.py` implementing the full `MemoryRepository` Protocol by wrapping an inner repository, in the same thin-decorator style as `ai_mem/infrastructure/bm25_repository.py`. Only `upsert`, `delete`, and `add_edge` get real logic; every other Protocol method is a one-line passthrough with zero file I/O. Critical constraint: before writing a file, compare its would-be new content against the existing file content and skip the write if unchanged, so that confidence/access_count-only mutations never touch the file — this only works because Chunk 1's `serialize()` emits frontmatter fields in a fixed deterministic order. Also change `chroma_repository.py` line 16's `_PERMANENT_TYPES` to include `"domain"`, AND replace `adr_markdown.py`'s temporary local `ADR_TYPES` with an import from `adr_paths`. Do not touch `server.py` (Chunk 4) or `ai_mem/adr_cli.py` (Chunk 3, parallel). Do not replan or expand scope.

---

### Chunk 3: `mem-adr-sync` CLI (export/import round trip)

**Scope:** New: `ai_mem/adr_cli.py`, `tests/test_adr_cli.py`. Edit: `pyproject.toml` (`[project.scripts]`).

**Depends on:** Chunk 0, Chunk 1
**Parallelizable with:** Chunk 2

**Implementation steps:**
1. `argparse`-based CLI with two subcommands, analogous to the structure of `dream_cli.py`:
   - `mem-adr-sync export --collection repo.ai-mem [--db-path ...]`: instantiates `ChromaMemoryRepository` directly (pure read operation), `repo.get_all(collection)`, filters `ADR_TYPES`, writes a file for each entry via `adr_markdown.serialize()` + `adr_paths.adr_dir_for()`. Without `--collection`: iterates over `repo.list_collections()`, exports every `repo.*` collection with a resolvable root, skips `global`/`workspace` (with a notice, no silent skip).
   - `mem-adr-sync import --collection repo.ai-mem [--db-path ...]`: instantiates a **bare `ChromaMemoryRepository`** (no `MarkdownAdrRepository` wrapper). Reads all `*.md` under `adr_paths.adr_dir_for(...)`, parses each file via `adr_markdown.parse()`. **Error handling:** `ValueError` → skip the file, print name+error, continue with the rest, exit code ≠ 0 if anything was skipped.
     For every successfully parsed file: `AddMemoryUseCase.execute()` (from `ai_mem.application.add_memory`) with `metadatas` from `type`/`superseded_by`/`valid_until` (NOT `created_at`). Afterwards separately `repo.add_edge()` for every parsed edge.
     **`created_at` correction:** `AddMemoryUseCase.execute()` reads `created_at` exclusively from metadata already present in Chroma — after the call, if the file carries a `created_at`, fetch the entry again via `get_by_ids()`, set `created_at` to the parsed value, and correct with a second `repo.upsert()`.
2. `main()` entry point, `pyproject.toml`: `mem-adr-sync = "ai_mem.adr_cli:main"`.
3. Tests: `export` after `mem_add` → file with correct content; `import` into a fresh instance → identical text AND `created_at`; round trip export→delete→import restores the entry; a second `import` after `mem_boost` does not overwrite confidence; broken `.md` file next to valid ones → valid ones are imported, broken one reported, exit code ≠ 0.

**Exit criterion:** `pytest tests/test_adr_cli.py -v` green; `mem-adr-sync --help` shows both subcommands.

**Coder prompt core:** This is Chunk 3 of a pre-approved plan. Implement a new CLI `ai_mem/adr_cli.py` with `export` and `import` subcommands, using `adr_paths` and `adr_markdown` (Chunks 0/1 — read both first). Both operate on a bare `ChromaMemoryRepository` — never `MarkdownAdrRepository` (Chunk 2, parallel, do not create/import it). `import` MUST reuse `AddMemoryUseCase.execute()` for confidence/access_count, but that path discards `created_at` from the file — re-fetch and correct it with a follow-up `upsert()`. On a malformed file, skip, report, continue, exit non-zero if anything skipped. Register `mem-adr-sync` in `pyproject.toml`. Do not touch `server.py` (Chunk 4). Do not replan or expand scope.

---

### Chunk 3b: `docs/decisions/INDEX.md` — compact index against retrieval noise

**Why this chunk exists (user addition):** once `docs/decisions/` has many files, an agent should not have to read/grep N individual ADR files to see what exists — a compact index file with one line per decision lowers the context noise. It belongs in this plan because it belongs directly to the retrieval-trigger mitigation from chunk 5 (an agent reads one file instead of many).

**Deliberately NOT part of this plan, with rationale (user question "librarian" subagent):** the index generation is pure, deterministic file I/O + string formatting — there is no judgment to make that would need an LLM. A fire-and-forget subagent would be slower, non-deterministic and more expensive than a Python function that does the same in milliseconds — and would moreover be a new skill/agent concept, not a repository/infrastructure layer, hence outside the "scope boundary" above anyway. Recommendation: the index file itself belongs in this plan (this chunk), the "librarian" subagent concept is a separate, later todo (`todo_bibliothekar_haiku_retrieval_agent_2026_09_25`) — and only for a task that actually needs judgment, not for what INDEX.md does today.

**Scope:** New: `ai_mem/infrastructure/adr_index.py`, `tests/infrastructure/test_adr_index.py`. Edit (small): `ai_mem/adr_cli.py` — new subcommand `reindex`, plus a call to `regenerate_index()` as the last step of `export` (chunk 3). **Storage-layer only**.

**Depends on:** Chunk 1 (`adr_markdown.parse()`), Chunk 3 (`adr_cli.py` must exist)
**Parallelizable with:** Chunk 4 (completely disjoint files)

**Implementation steps:**
1. `regenerate_index(adr_dir: Path) -> None` in `ai_mem/infrastructure/adr_index.py`: lists all `*.md` files in `adr_dir` except `INDEX.md` itself, parses each via `adr_markdown.parse()`, extracts the title by reusing `title_of()` from `ai_mem.application.list_entries` (do not reimplement; `infrastructure → application → domain` is the permitted import direction according to `docs/architecture.md`). Status column: `active`, or `superseded_by: <id>` if set.
2. Output format — Markdown table, sorted by `id` (determinism as in chunk 1):
   ```markdown
   # Decision Records Index

   | id | title | status |
   |---|---|---|
   | domain_bmad_vs_ai_mem_epistemology_2026_09_25 | Decision: The comparison BMAD vs. ai-mem... | active |
   | domain_some_old_entry | ... | superseded_by: domain_newer_entry |
   ```
   Broken `.md` file: skip, report the file name, continue with the rest (like chunk 3's `import`).
3. `ai_mem/adr_cli.py`: new subcommand `mem-adr-sync reindex --collection ... [--db-path ...]`; `export` additionally calls `regenerate_index()` as the last step. No automatic updating on individual `mem_add` calls via `MarkdownAdrRepository` (chunk 2) — deliberately a periodically regenerated artifact (like `mem_dream`), not an overlooked gap: freshness between two `export`/`reindex` runs is an accepted, documented limitation, not a live update, to avoid a read-modify-write race on a shared file.
4. Tests: 3 ADR files (one with `superseded_by`) → sorted, correct `INDEX.md`; a broken file in between is skipped and reported; two runs without source changes → byte-identical `INDEX.md`.

**Exit criterion:** `pytest tests/infrastructure/test_adr_index.py -v` green; `mem-adr-sync reindex --help` works; after `mem-adr-sync export`, `docs/decisions/INDEX.md` exists with one line per exported file.

**Coder prompt core:** This is Chunk 3b of a pre-approved plan, parallel to Chunk 4 (built by another coder — do not touch `server.py`, `dream_cli.py`, `docs/architecture.md`, or `CLAUDE.md`). Implement exactly the scope above: a new pure function `regenerate_index()` in `ai_mem/infrastructure/adr_index.py` that scans `docs/decisions/*.md`, parses each via `ai_mem.infrastructure.adr_markdown.parse()` (Chunk 1, read it first), and writes a single sorted-by-id Markdown table `INDEX.md` with columns id/title/status — reuse `title_of()` from `ai_mem.application.list_entries` rather than reimplementing title extraction (this infrastructure→application import is explicitly allowed per `docs/architecture.md`). Add a `reindex` subcommand to `ai_mem/adr_cli.py` (Chunk 3, read it first) that calls this function, and make `export` call it automatically as its final step. A malformed `.md` file must be skipped and reported by name, never crash the run. Output must be byte-identical across repeated runs with unchanged sources — verify with a test. Do not wire index regeneration into `MarkdownAdrRepository` (Chunk 2) or any per-`mem_add` write path. Do not replan or expand scope.

---

### Chunk 4: Server wiring + self-population of the root mapping

**Scope:** Edit: `ai_mem/server.py`, `ai_mem/dream_cli.py`, `docs/architecture.md`, `CLAUDE.md`. **Storage-layer only.**

**Important finding from the tech-lead review:** `ai_mem/dream_cli.py` builds in `_build_repo()` a **second, independent** repository stack for the `mem-dream` terminal command. `DreamMemoryUseCase` mutates real data through this stack for exactly the types migrated here. Without adjustment, `mem-dream --auto_delete` would orphan a `domain` file on disk, and `--auto_link`/`--auto_supersede` would change Chroma's `edges`/`superseded_by` without updating the `.md` file. Therefore: **`dream_cli.py`'s `_build_repo()` is wired exactly like `server.py`'s repository stack** — a mandatory part of this chunk.

**Depends on:** Chunk 2, Chunk 3
**Parallelizable with:** nothing

**Implementation steps:**
1. In `server.py`, after `_inner_repo = ChromaMemoryRepository(_db_path)`:
   ```python
   from ai_mem.infrastructure.markdown_adr_repository import MarkdownAdrRepository
   from ai_mem.infrastructure.adr_paths import record_collection_root
   from ai_mem.repo_context import detect_repo_context

   _adr_repo = MarkdownAdrRepository(_inner_repo, _db_path)
   ctx = detect_repo_context()
   if ctx.git_root or ctx.claude_md_dir:
       record_collection_root(_db_path, ctx.collection, ctx.git_root or ctx.claude_md_dir)
   ```
   Then `BM25MemoryRepository(_adr_repo)` instead of `BM25MemoryRepository(_inner_repo)`, and the `except ImportError` fallback to `_repo = _adr_repo`. Opt-out via `AI_MEM_ADR_DISABLED=1` (then `_repo = _inner_repo` directly).
2. `ai_mem/dream_cli.py` gets the same wiring in `_build_repo()`, including the same opt-out check.
3. In the `mem_add` handler: if `type_tag in ADR_TYPES` and the root is not resolvable: append a note to `base_text` ("not persisted as a Markdown file — could not resolve a repo root..."), otherwise optionally name the path written.
4. `docs/architecture.md`: new row in the infrastructure table for `MarkdownAdrRepository`.
5. `CLAUDE.md` Critical Invariants: new item on the confidence-lifecycle boundary.
6. Full test run (`pytest tests/ -v`) — existing server tests must not break through the changed wiring.

**Exit criterion:** `pytest tests/ -v` fully green; manual smoke test in a **throwaway test directory** (e.g. `/tmp/adr-smoketest`), not in the real ai-mem repo.

**Coder prompt core:** This is Chunk 4 of a pre-approved plan. Wire `MarkdownAdrRepository` (Chunk 2) into `server.py`'s repository construction between `ChromaMemoryRepository` and the optional BM25 wrapper. Add repo-root self-population at startup. Apply the exact same wiring to `dream_cli.py`'s `_build_repo()` — required, not optional: `mem-dream`'s auto_delete/auto_link/auto_supersede flags mutate the migrated entry types. Add a note to `mem_add`'s response when a file couldn't be written. Update `docs/architecture.md` and `CLAUDE.md`. Run the full test suite and fix breakage via mocks/fixtures, not weakened assertions. Smoke-test only in a throwaway temp directory. Do not replan or expand scope beyond server.py + dream_cli.py wiring + the two doc files.

---

### Chunk 5: Backfill of existing entries + retrieval-trigger mitigation (docs)

**Scope:** New: `docs/decisions/README.md`, generated files under `docs/decisions/*.md` (via CLI). Edit: `CLAUDE.md` (new section "Decision Records"). **Storage-layer + docs only.**

**Depends on:** Chunk 4, Chunk 3, and Chunk 3b (export also creates INDEX.md automatically)
**Parallelizable with:** nothing

**Implementation steps:**
1. `mem-adr-sync export --collection repo.ai-mem` as a one-time operational step (calls the CLI, which thanks to chunk 3b also automatically creates `docs/decisions/INDEX.md` at the end), to backfill existing entries, among others `domain_bmad_vs_ai_mem_epistemology_2026_09_25`.
2. `docs/decisions/README.md`: explain the convention (one file per decision, file name = ai-mem ID, frontmatter schema reference to `docs/adr-format.md`, "superseded by" as a frontmatter field instead of deletion).
3. `CLAUDE.md`, new standalone section "Decision Records":
   ```markdown
   ## Decision Records

   `domain`/`pattern`/`anti-pattern` knowledge lives git-natively under `docs/decisions/` (one
   Markdown file per decision, file name = ai-mem entry ID) — directly searchable with
   grep/ls/Read, without ai-mem tools. ChromaDB is a locally regenerable semantic index
   on top of it (`mem-adr-sync import` rebuilds it from the files), not the source of truth.

   **Open, NOT solved by this migration:** the general mem_query retrieval-trigger
   problem (`eval_pull_gap_test_2026_09_20`, collection `repo.ai-mem`) — an agent that has a
   question does not call mem_query on its own in most cases. This section
   only makes `docs/decisions/` discoverable via the channel that demonstrably
   worked in the gap test (CLAUDE.md reference + repo grep), but does not solve the trigger problem for
   ai-mem's own query tools.

   `docs/decisions/INDEX.md` lists all decisions compactly (id + title + status) —
   with many files, read this one file first instead of grepping individually;
   `mem-adr-sync reindex`/`export` keeps it current.
   ```
4. Verification: `mem-adr-sync import` against a fresh test Chroma instance returns an entry identical to the original (manual diff check).

**Exit criterion:** `docs/decisions/domain_bmad_vs_ai_mem_epistemology_2026_09_25.md` exists with the full original text; `docs/decisions/INDEX.md` exists and lists this entry; `docs/decisions/README.md` exists; `CLAUDE.md` contains the new section including the explicit "not solved" sentence.

**Coder prompt core:** This is Chunk 5 of a pre-approved plan — the final chunk. Run `mem-adr-sync export --collection repo.ai-mem` to backfill existing entries into `docs/decisions/*.md`. Write `docs/decisions/README.md`. Add a "Decision Records" section to `CLAUDE.md` (standalone, not under "Critical Invariants") pointing at `docs/decisions/`, including — hard requirement — an explicit sentence that the general `mem_query` retrieval-trigger problem is NOT solved by this migration. Verify the backfilled file for `domain_bmad_vs_ai_mem_epistemology_2026_09_25`. Do not replan or expand scope.

---

## Spawn Order

Sequential (dependencies):
- Chunk 0 + Chunk 1 (parallel) → /reflect → Chunk 2 + Chunk 3 (parallel) → /reflect → Chunk 3b + Chunk 4 (parallel) → /reflect → Chunk 5 → the-coder → /reflect

Parallel possible:
- **Chunk 0 + Chunk 1 simultaneously** (fully disjoint files) → spawn two `Agent` calls in the same message with `subagent_type="the-coder"`
- **Chunk 2 + Chunk 3 simultaneously**, after Chunk 0 + Chunk 1 have landed and reflected (disjoint files, both only read Chunk 0/1's modules) → spawn two `Agent` calls in the same message with `subagent_type="the-coder"`
- **Chunk 3b + Chunk 4 simultaneously**, after Chunk 2 + Chunk 3 have landed and reflected (disjoint files: `adr_index.py`+`adr_cli.py` addition vs. `server.py`+`dream_cli.py`+the two doc files) → spawn two `Agent` calls in the same message with `subagent_type="the-coder"`
- Chunk 5 is strictly sequential after both Chunk 3b and Chunk 4.

**Reflect gate:** Run /reflect between every chunk (or every parallel pair). The coder's `[retro]` surfaces path corrections, API surprises, and scope drift before they propagate into the next chunk — particularly important here because Chunk 2/3 both depend on Chunk 0/1's exact function signatures, Chunk 3b depends on Chunk 1's and Chunk 3's exact shape, and Chunk 4 depends on Chunk 2/3's exact class/CLI shape.

## Our notes

