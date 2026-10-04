# ADR Markdown Format

Part of the ADR migration (see `docs/adr-migration-chunk-plan.md`). This document
specifies the on-disk frontmatter schema and directory convention for `domain`/
`pattern`/`anti-pattern`/`learning` entries persisted as Markdown files alongside
ChromaDB. The serializer/parser live in `ai_mem/infrastructure/adr_markdown.py`;
this document is the schema they implement against.

Records are not limited to software architecture: an area can just as well be
`marketing`, `pricing` or `ops`. Any repo-scoped knowledge worth keeping as a
reviewable, git-native record fits.

## Directory convention

- Root: `<repo_root>/docs/records/` by default.
- Override the root via the `AI_MEM_ADR_DIR` environment variable
  (a path relative to the repo root, e.g. `AI_MEM_ADR_DIR=notes/adr`).
- Layout: `<root>/<area>/<kind>/<id>.md`, area first, then kind.
  - `<area>` is the entry's `area` metadata (see below).
  - `<kind>` is derived from `type` by one fixed map: `learning` -> `learnings/`;
    `domain`, `pattern`, `anti-pattern` -> `decisions/`.
- Learnings (what was observed) and decisions (what was chosen because of it)
  are separate entries with separate folders; a decision links back to the
  learning it rests on via a `derived_from` edge. See ai-mem entry
  `domain_learning_decision_split_subfolders_2026_09_29` in `repo.ai-mem`.
- This overturns the earlier single-flat-directory rule. That
  rule assumed a type change should never move a file; the types are now stable,
  and the split is what makes the folder browsable. The cost is accepted: a type
  or area change moves the file, and the repository removes the old location
  (including legacy flat files) on the next upsert.
- Filename: `<ai-mem-entry-id>.md`. Entry IDs are unique per collection and
  semantically named (e.g. `domain_bmad_vs_ai_mem_epistemology_2026_09_25`), so
  no sequence number is needed.
- `INDEX.md` and `README.md` stay central at `<root>/`, not per area.
- `global`, `workspace` and `subagent.*` collections have no 1:1 repo root. They are
  backed by files below a separate private records repo: `$AI_MEM_RECORDS_HOME`, else
  `$AI_MEM_WORKSPACE_ROOT/ai-mem-records`, as `<collection>/docs/records/…`. Opt-in:
  while that directory does not exist they remain ChromaDB-only (extended 2026-10-03;
  supersedes the earlier "deliberate scope boundary").

## FOCUS.md

- `<root>/FOCUS.md` holds the text of the `current_focus` entry, whatever its type
  (one file per collection, replaces the old ChromaDB-only focus; see
  `domain_records_model_replaces_chroma_2026_10_04`).
- No frontmatter: the file is the plain text plus a trailing newline. It is
  overwritten in place and git keeps the history. A boost-only upsert leaves it untouched.
- Not a record: never listed in `INDEX.md`, and `FOCUS` is a reserved id stem like
  `INDEX`/`README`. Deleting `current_focus` removes the file.
- `mem-adr-sync export` writes it; `import` restores `current_focus` from it
  (type `project` on a fresh rebuild).

## Area

- Free-form Chroma metadata key `area`, set via the optional `area` parameter of
  `mem_add`.
- Default when missing: `general`. Legacy files without the field parse as `general`.
- Must match `^[a-z0-9][a-z0-9_-]*$`. For ADR-typed entries an invalid area makes
  `upsert` raise `ValueError` before ChromaDB is written (like an unsafe id).
  Non-ADR entries are never checked.
- `serialize` always writes the `area` line (`general` when the metadata has
  none), so a parse/serialize round trip is byte-identical.

## Frontmatter schema

Only structural, ADR-relevant fields are persisted. They are written in a fixed,
literal order (`id, type, area, created, superseded_by, valid_until, edges, cue`) — never by iterating a Python `metadata` dict's own key order,
since that order can vary across code paths that merge dicts. This determinism
is what lets a decorator skip rewriting a file when only volatile fields changed
(see below).

| Field | Required | Notes |
|---|---|---|
| `id` | yes | ai-mem entry ID, matches the filename stem. |
| `type` | yes | One of `domain`, `pattern`, `anti-pattern`, `learning`, `todo`, `user` (kinds `decisions`, `learnings`, `todos`, `user`; `todo`/`user` added 2026-10-04). Entries of any other type are never file-backed. |
| `area` | yes | Topic area, matches `^[a-z0-9][a-z0-9_-]*$`; `general` when the entry has none. Written directly after `type`. |
| `created` | yes | ISO-ish timestamp the entry was first created. |
| `superseded_by` | no | Entry ID of the entry that supersedes this one, if any. |
| `valid_until` | no | Timestamp after which this entry is considered stale, if set. |
| `edges` | no | Single-line embedded JSON array of `{"target_id": ..., "edge_type": ...}` objects — not multi-line YAML. A decision that rests on a learning carries `derived_from` (source = decision, target = learning), stored outgoing on the decision. |
| `cue` | no | One-line experience-index cue (the situation in which this entry would have helped), set via `mem_boost(cue=...)`. Written last. Persisted since 2026-10-04 so the experience index survives without ChromaDB; a cue change rewrites the file but never INDEX.md. |

After the frontmatter, the entry's raw text body follows unchanged (its existing
`Decision:/Why:/Scope:`, `Rule:/When:/Why:`, or `Tried:/Failed because:/Instead:`
shape is not reformatted into a different ADR prose style). A `learning` body has
the shape `Observed: <fact or measurement>`, `Cause: <root cause, or 'unknown'>`,
`Evidence: <test, commit sha or entry ids>`, one per line.

## INDEX.md

`<root>/INDEX.md` is regenerated by `mem-adr-sync reindex`/`export` from a
recursive scan of all record files. Columns: `id | area | type | title | status`.

## Fields that are never persisted to the file

These fields are ChromaDB-only, volatile operational telemetry — they are never
written to the Markdown frontmatter even if present in the input metadata dict:

- `confidence` (legacy metadata only — no longer written or read anywhere; dropped 2026-09-26, see CLAUDE.md)
- `access_count` (legacy metadata only — no longer written or read anywhere; dropped 2026-09-26, see CLAUDE.md)
- `boost_count`
- `last_accessed_at`

(`cue` was on this list until 2026-10-04 and is now a frontmatter field, see above.)

Rationale: the Markdown file is a derived projection of the current ChromaDB
state *minus* these volatile fields. A `mem_boost` call mutates `boost_count`
(and `last_accessed_at`) and a `record_access` call mutates `last_accessed_at`,
but neither must ever cause a file rewrite; only a `mem_boost` that sets or
clears a `cue` does — see the
"Confidence-Lifecycle" section of `docs/adr-migration-chunk-plan.md` for the
original reasoning (historical: predates the 2026-09-26 confidence/access_count
removal) and the diff-before-write requirement this implies for the
repository decorator that writes these files.
