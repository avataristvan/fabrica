# ADR Markdown Format

Part of the ADR migration (see `docs/adr-migration-chunk-plan.md`). This document
specifies the on-disk frontmatter schema and directory convention for `domain`/
`pattern`/`anti-pattern` entries persisted as Markdown files alongside ChromaDB.
The serializer/parser themselves live in `ai_mem/infrastructure/adr_markdown.py`
(a later chunk); this document is the schema they implement against.

## Directory convention

- Location: `<repo_root>/docs/decisions/` by default.
- Override the subdirectory via the `AI_MEM_ADR_DIR` environment variable
  (a path relative to the repo root, e.g. `AI_MEM_ADR_DIR=notes/adr`).
- Flat directory, no per-type subfolder — `type` lives in the frontmatter instead,
  so a later type change on an entry never requires moving its file.
- Filename: `<ai-mem-entry-id>.md`. ai-mem entry IDs are already unique per
  collection and semantically named (e.g. `domain_bmad_vs_ai_mem_epistemology_2026_09_25`),
  so no additional sequence number is needed.
- `global` and `workspace` collections have no 1:1 repo root and are never
  backed by files — they remain ChromaDB-only. This is a deliberate scope
  boundary of the migration, not a gap.

## Frontmatter schema

Only structural, ADR-relevant fields are persisted. They are written in a fixed,
literal order — never by iterating a Python `metadata` dict's own key order,
since that order can vary across code paths that merge dicts. This determinism
is what lets a decorator skip rewriting a file when only volatile fields changed
(see below).

| Field | Required | Notes |
|---|---|---|
| `id` | yes | ai-mem entry ID, matches the filename stem. |
| `type` | yes | One of `domain`, `pattern`, `anti-pattern`. |
| `created` | yes | ISO-ish timestamp the entry was first created. |
| `superseded_by` | no | Entry ID of the entry that supersedes this one, if any. |
| `valid_until` | no | Timestamp after which this entry is considered stale, if set. |
| `edges` | no | Single-line embedded JSON array of `{"target_id": ..., "edge_type": ...}` objects — not multi-line YAML. |

After the frontmatter, the entry's raw text body follows unchanged (its existing
`Decision:/Why:/Scope:`, `Rule:/When:/Why:`, or `Tried:/Failed because:/Instead:`
shape is not reformatted into a different ADR prose style).

## Fields that are never persisted to the file

These fields are ChromaDB-only, volatile operational telemetry — they are never
written to the Markdown frontmatter even if present in the input metadata dict:

- `confidence`
- `access_count`
- `boost_count`
- `last_accessed_at`
- `cue`

Rationale: the Markdown file is a derived projection of the current ChromaDB
state *minus* these volatile fields. A `mem_boost` or `record_access` call
mutates confidence/access_count but must never cause a file rewrite — see the
"Confidence-Lifecycle" section of `docs/adr-migration-chunk-plan.md` for the
full reasoning and the diff-before-write requirement this implies for the
repository decorator that writes these files.
