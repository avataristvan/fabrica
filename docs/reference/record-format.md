# Record format

Reference for the on-disk format of records: directory layout, frontmatter schema, areas and cross-area references, `FOCUS.md`, `INDEX.md`, sources, and the lint codes. The reader and writer live in `ai_mem/infrastructure/adr_markdown.py`; this document is the schema they implement. Why records are files: [Organisational memory](../explanation/organisational-memory.md). History of the format: [sources/adr-migration-chunk-plan.md](../sources/adr-migration-chunk-plan.md).

Records are not limited to software architecture: a topic can just as well be `marketing`, `pricing` or `ops`. Any knowledge of an area that is worth keeping as a reviewable, versioned record fits.

**Terms.** An **area** is a folder that holds `docs/records/` (see "Areas and cross-area references" below). A **topic** is the subfolder inside `docs/records/` that a record sits in; the frontmatter key for it is `topic:`, and so is the CLI flag `--topic`. Old records may still carry the legacy key `area:` (same meaning); it is read, never written, and `mem lint --fix` renames it.

## Directory convention

- Root: `<area>/docs/records/` by default.
- Override the root via the `AI_MEM_ADR_DIR` environment variable (a path relative to the area, e.g. `AI_MEM_ADR_DIR=notes/adr`).
- Layout: `<root>/<topic>/<kind>/<id>.md`, topic first, then kind.
  - `<topic>` is the record's `topic:` field (see "Topic" below).
  - `<kind>` is derived from `type` by one fixed map: `learning` -> `learnings/`; `domain`, `pattern`, `anti-pattern` -> `decisions/`; `user` -> `user/`. There is no `todo` type: next steps live in `FOCUS.md`, the rest in `BACKLOG.md` (both plain text next to `INDEX.md`).
- Learnings (what was observed) and decisions (what was chosen because of it) are separate records in separate folders; a decision links back to the learning it rests on via a `derived_from` edge (`domain_learning_decision_split_subfolders_2026_09_29`). A type or topic change moves the file.
- Filename: `<id>.md`. Ids are unique per area and semantically named (e.g. `domain_bmad_vs_ai_mem_epistemology_2026_09_25`), so no sequence number is needed.
- `INDEX.md` and `README.md` stay central at `<root>/`, not per topic.
- There is no shared level. Every record lives in the area of its topic; cross-cutting topics get an area of their own (see [Areas and kinds](../explanation/areas-and-kinds.md)). Upgrading from the earlier collection layout: the tag `v1-last-upgrade-path`.

## Areas and cross-area references

- An area is addressed by its folder: the nearest ancestor (inclusive) of a path that has a `docs/records/` directory. A path inside `docs/records/` belongs to the folder that holds it. A CLAUDE.md is not needed, the area need not be a version-controlled repository, and worktree paths count as their main checkout (`domain_area_path_is_the_address_of_knowledge_2026_10_10`). Code: `ai_mem/infrastructure/areas.py`.
- An edge target inside the same area is a bare id. An edge target in another area is `<rel>:<id>`: `<rel>` is the POSIX path from the source area's folder to the target area's folder, and always starts with `.` or `..`:
  - `../billing:learning_x` (sibling area)
  - `..:pattern_y` (the enclosing area, e.g. the root area) and `./sub:domain_z` (nested area)
- Rejected: absolute paths, `~`, empty segments, `..` after a plain segment, `.` or `..` in the middle, backslashes, glob characters, NUL, and an id that is not a valid filename stem. Ids therefore never contain `:` (the split is at the last `:`). A reference that does not lead to a folder with `docs/records/` does not resolve.
- Cross-area edges are stored only on the source record, in the same `edges` field; nothing is written into the other area. `supersedes` across areas is refused, since it would set `superseded_by` there: use `related` or `derived_from`, and supersede inside the target area itself. Older readers see a qualified target as an id they cannot find, which breaks nothing.

## FOCUS.md

- `<root>/FOCUS.md` holds the text of the `current_focus` entry, whatever its type (one file per area; see `domain_records_model_replaces_chroma_2026_10_04`). Write it with `mem add --id current_focus --text "..."`.
- No frontmatter: the file is the plain text plus a trailing newline. It is overwritten in place and version control keeps the history.
- Not a record: never listed in `INDEX.md`, and `FOCUS` is a reserved id stem like `INDEX`/`README`. Deleting `current_focus` removes the file.

## Topic (`topic:` field)

- Frontmatter key `topic`, set with `mem add --topic`. It names the topic folder, not the area.
- Legacy key `area:` (the old name): read as `topic:`. If both keys are present and differ, `lint` reports `topic-conflict`; the reader then uses `topic:`.
- Default when missing: `general`. Legacy files without the field parse as `general`.
- Must match `^[a-z0-9][a-z0-9_-]*$`. An invalid topic makes the write fail (like an unsafe id).
- `serialize` always writes the `topic` line (`general` when there is none). A parse/serialize round trip is byte-identical for files that use `topic:`; a file with the legacy `area:` comes back with `topic:` until `mem lint --fix` has renamed it.

## Frontmatter schema

Fields are written in a fixed, literal order (`id, type, area, perspective, created, superseded_by, valid_until, edges, <other keys>, cue`). The determinism lets a rewrite be skipped when nothing changed, so history stays free of churn.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Record id, matches the filename stem. |
| `type` | yes | One of `domain`, `pattern`, `anti-pattern`, `learning`, `user` (kinds `decisions`, `learnings`, `user`). Any other type is rejected by `mem add`; the retired `todo` with a pointer to `FOCUS.md`/`BACKLOG.md`, and `mem lint` flags a leftover todo file the same way. |
| `topic` | yes | Topic folder, matches `^[a-z0-9][a-z0-9_-]*$`; `general` when the record has none. Written directly after `type`. |
| `perspective` | no | Whose knowledge or experience it is: `user`, `agent`, or a role such as `coder` or `reviewer` (`domain_perspective_is_a_lens_not_a_location_2026_10_10`). Same pattern as `topic`; written after it. A lens, not a location: it never changes where the file lives. Records of kind `user` keep their kind and also carry `perspective: user`. |
| `created` | yes | ISO-ish timestamp the record was first created. |
| `superseded_by` | no | Id of the record that supersedes this one, if any. |
| `valid_until` | no | Timestamp after which this record is considered stale, if set. |
| `edges` | no | Single-line embedded JSON array of `{"target_id": ..., "edge_type": ...}` objects, not multi-line YAML. Edge types: `contradicts`, `fixes`, `causes`, `related`, `supersedes`, `confirms` (later record -> earlier one it bears out), `derived_from` (a decision points at the learning it rests on). A target in another area is area-qualified (`../<area>:<id>`, see above). |
| other keys | no | Any other `key: value` line (e.g. from a hand-written record) is kept as is, in its original order, after `edges` and before `cue`. Normalising a record never drops it. Keys must not contain `:` and values must fit on one line. |
| `cue` | no | One line: the situation in which this record helps. It is the recognition trigger the librarian matches against. Set with `mem add --cue`. Written last; a cue change rewrites the file but never INDEX.md. |

After the frontmatter, the record's raw text body follows unchanged. The body shapes by type are a convention, not a schema:

| Type | Body |
|---|---|
| `domain` | `Decision: / Why: / Scope:` |
| `pattern` | `Rule: / When: / Why:` |
| `anti-pattern` | `Tried: / Failed because: / Instead:` |
| `learning` | `Observed: <fact or measurement>`, `Cause: <root cause, or 'unknown'>`, `Evidence: <test, commit sha, record ids or a source path>`, one per line. `Observed:` holds only what was seen; an attributed cause goes into `Cause:` with its origin and status (open or backed) (`pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24`). |

**Superseding.** `mem link NEW OLD --type supersedes` marks `OLD` as overtaken instead of deleting it: it keeps its reasoning and is flagged with `superseded_by`. A superseded record cannot itself supersede another, which rules out cycles.

## INDEX.md

`<root>/INDEX.md` is generated from a recursive scan of all record files by `mem lint --fix` (and kept in step by `mem add`, `mem link`, `mem delete` and `mem move`). Columns: `id | topic | type | title | status`. Do not edit it by hand: a hand-kept or stale INDEX.md makes the write commands refuse until `mem lint --fix` has adopted the area.

## Fields that are not stored

Earlier versions kept operational counters and trust signals next to a record. They are neither written nor read any more: `confidence`, `access_count` (dropped 2026-09-26, `domain_drop_confidence_for_evidence_and_librarian_2026_09_26`), `boost_count`, `last_accessed_at`, `expires_at`. Unknown extra keys in a hand-written record are kept as they are (see "other keys" above). The reasoning behind the retired counters: [sources/adr-migration-chunk-plan.md](../sources/adr-migration-chunk-plan.md).

## Sources

A source is dated evidence that never changes: a talk or paper, a measurement, a past design doc, the documentation of a retired system (`domain_docs_split_into_documentation_and_sources_2026_10_10`). It lives at `docs/sources/<slug>.md` of the area; large raw material (a transcript) lies next to it in `docs/sources/<slug>/`. Its claims are frozen. Only pseudonymising for publication may change the text, deliberately and noted in a record.

```
---
type: <retired-system | design-doc | research | measurement | origin | config-note | talk | paper | ...>
date: <YYYY-MM-DD the evidence dates from, not the day it was moved>
origin: <where it came from: former path, memory entry, URL>
status: <unprocessed | processed>
---

## What the source says

<the original text, unchanged>

## Our notes

<ours, dated; the only part that may grow>
```

`status: unprocessed` means the archivist has not yet derived what still holds from it. `processed` means every conclusion that still holds exists as a record. A learning or decision that rests on a source names it in its `Evidence:` line by path (`Evidence: docs/sources/<slug>.md`), or has an edge to `<slug>` (`mem link <record> <slug> --type derived_from`; lint accepts source slugs as edge targets). `mem source <slug> --status processed` sets the status; it is the only change `mem` makes to a source.

`mem doctor` (section Sources) lists sources that are `processed` yet pointed to by no record, and sources with a missing field or an unknown status. Sources with private matter stay out of version control (`.gitignore`) until the user releases them.

## Lint and normalisation

`mem lint [--area PATH] [--fix] [--json]` checks one area's record files and reads them as plain files (not through the repository, which silently skips records it cannot parse). Exit 0 clean, 1 findings remain, 2 no area. `mem doctor` runs the same checks over every area below `--root` and adds state checks; it changes nothing except `$AI_MEM_PATH/doctor_last_run`.

| Code | Meaning | Fixable |
|---|---|---|
| `unparsable` | frontmatter cannot be read: no `---` separator, a line that is not `key: value` (e.g. bold labels), a duplicate key, a symlink or a file resolving outside the records directory | no |
| `frontmatter-shape` | leading `---` fence, or no blank line after the closing `---` | yes |
| `frontmatter-format` | field order or spacing differs from the canonical form | yes |
| `missing-field` | `id`/`type` missing (no), `topic:`/`created:` missing (yes) | partly |
| `legacy-topic-key` | the legacy key `area:` instead of `topic:` (`--fix` renames it in place and changes nothing else; if `topic:` is also present and equal, the `area:` line is dropped) | yes |
| `topic-conflict` | `topic:` and the legacy `area:` are both present and differ | no |
| `bad-number` | `created` or `valid_until` is not a number | no |
| `value-chars` | a frontmatter value contains control or line-break characters | no |
| `id-stem`, `id-colon`, `id-chars`, `id-unsafe` | id differs from the file name, contains `:`, contains control characters, or is not a safe file stem | no |
| `type-invalid`, `type-folder`, `topic-folder`, `layout` | type not a record type; file not in the kind folder of its type; `topic:` differs from the topic folder; file not at `<topic>/<kind>/<id>.md` | no |
| `perspective-user` | a `user` record without `perspective: user` (a different non-empty value is reported, not overwritten) | yes, when empty |
| `edges-json`, `edge-type`, `edge-target-invalid` | `edges` is not a JSON list of `{target_id, edge_type}`; unknown edge type; target not a valid id or `<area-path>:<id>` | no |
| `edge-dangling`, `edge-unresolved`, `edge-dangling-xarea` | bare target absent from the area; qualified target points at no area; qualified target absent from the area it points at | by `--fix` when the id lives in exactly one area (flag stays `false`: lint does not scan other areas) |
| `index-missing`, `index-stale` | INDEX.md absent, or different from what the generator writes (hand-written tables with links count) | yes |
| `backlog-format` | BACKLOG.md items numbered (`1.`, `1)`), marked `*`/`+`, or separated by blank lines; the canonical form is the header paragraph, one blank line, then one unnumbered `- ` line per item, the line order being the order of work | yes (the order is kept) |
| `backlog-line` | a BACKLOG.md line after the header that is no item: a heading, a section, a continuation line | no |

`--fix` writes only inside the given area and prints one line per change. It rewrites a file's frontmatter into the canonical form (drops a leading `---` fence, inserts the missing blank line, renames a legacy `area:` to `topic:`, fills `topic:` from the topic folder, fills `created:` from the file's first commit time, else its mtime, sets `perspective: user` on user records, orders the known keys canonically, keeps unknown keys in their order before `cue`) and then regenerates INDEX.md. It also repoints a lost edge target (an area moved, so the prefix went stale) when its id exists in exactly one area below the search root (`$AI_MEM_WORKSPACE_ROOT`, else the outermost area above, else the parent folder); an id found in no area or in several stays as it is and is still reported. Only the source record in the given area is rewritten. This is no judgment, unlike repointing an edge to a deleted record (`domain_mem_delete_names_dangling_edges_2026_10_13`): there is one place the id can mean. The body is never touched. Before writing, a preservation guard re-reads the new text and requires the body to be identical, every original non-empty frontmatter value to be present (the `edges` value may differ only in targets, with the same edge types in the same order), and the result to parse with the normal reader; otherwise the file is reported as not fixable and left as it is. Symlinked records are never read or written.
