# Command-line reference

The commands ai-mem installs. `mem` is the main one: it reads and writes record files directly, standard library only, one line of output per action (`--json` for agents). For a guided first use see the [tutorial](../tutorial/first-records.md); for tasks see the [how-to guides](../how-to/).

## Area and exit codes

Every `mem` command works on one area: the nearest ancestor of the working directory that has `docs/records/` (`--area PATH` overrides). Ids are plain file stems (no `:`, separators or glob characters).

Exit codes: 0 ok, 1 conflict or not found (or lint findings remain), 2 usage or invalid input (or no area).

## `mem`

```bash
mem add --id ID --type learning --topic tools --text "..."   # or --file F, or - for stdin
mem add --id ID --cue "situation in which this helps"        # existing record: only the given fields change
mem add --id ID --perspective coder                          # whose knowledge it is
mem add --id current_focus --text "..."                      # writes FOCUS.md
mem link SOURCE TARGET --type related [--to-area PATH]       # TARGET bare, or <rel-area-path>:<id>
mem unlink SOURCE TARGET [--type T]                          # TARGET as stored; every type unless --type
mem find ID [--root DIR] [--json]                            # where an id exists (read-only); exit 1 when nowhere
mem source SLUG --status processed|unprocessed               # a source's status; only that frontmatter line changes
mem delete ID...                                             # also prints `dangling: REF --TYPE--> ID` per edge left pointing at it
mem context [PATH] [--json]                                  # area root, records dir, INDEX/FOCUS paths
mem context --map [--root DIR] [--json]                      # areas below DIR and the edges between them
mem move ID... --to-area PATH [--dry-run] [--scan-root DIR]  # move records into another area
mem move --batch FILE [--dry-run] [--scan-root DIR]          # move many records between many areas in one plan
mem move-area OLD NEW --root DIR [--dry-run] [--include-unversioned]  # rename or move an area folder, references included
mem lint [--fix] [--json]                                    # check (and normalise) the area's record files and BACKLOG.md
mem doctor [--root DIR] [--days N] [--json]                  # diagnosis of the whole practice, changes nothing
mem review [--since REF] [--json]                            # records a push would publish: added/changed/superseded, machine paths, private names, commits a squash would orphan
```

Edge types for `mem link`: `contradicts`, `fixes`, `causes`, `related`, `supersedes`, `confirms`, `derived_from`. `mem delete` changes no other record: it names each edge in the area that pointed at a deleted record (`dangling:` lines; edges from other areas are left to `mem doctor`), to be repointed with `mem link` or dropped with `mem unlink`. A link target may also be a source slug, for every edge type except `supersedes` (a source is frozen); nothing is written into the source. `mem unlink` removes an edge, also one whose target no longer exists; removing a `supersedes` edge also clears `superseded_by` and `valid_until` on the target. The format of the files these commands write: [record format](record-format.md).

### `mem find`

Searches the home area, its ancestor areas (nearest first), then every other area below `--root` (default `$AI_MEM_WORKSPACE_ROOT`, else the home area's parent); records, `docs/reference/` docs and sources (`docs/sources/<slug>.md`) count. Each hit is printed as the reference `mem link` accepts from the home area (bare id, else `<rel-area-path>:<id>`) plus the file path. `mem link` with a bare target missing in the home area still fails, but its error names where `mem find` would find it; it never qualifies for you.

### `mem move-area`

Renames or moves a folder that is an area or holds areas, together with every reference the move would break. Cross-area references are relative paths, so a move breaks them in both directions: from the moved areas outwards and from every other area into them. `mem move-area` scans every area below `--root` (the workspace), rewrites each edge that resolves into or out of a moved area, and does the same for references in record text (`../x:<id>`, `./x:<id>`) when the record they name exists. Areas nested in the folder move with it; edges between them stay as they are. Then it renames the folder.

It refuses before writing anything when the target exists, lies inside the folder or on another filesystem, when a record's edges field is malformed, when an area it would write has a hand-kept INDEX.md, or when such an area is not under git (no undo; `--include-unversioned` allows it). With `--dry-run` it prints every rewrite, the rename, what blocks it and what is left to you, and changes nothing. Records are rewritten before the folder is renamed, so an interrupted run can be started again.

What a move also breaks outside the records is reported as `left to you:` and never touched: linked git worktrees (with the `git worktree repair` command), an editable install that still maps to the old path (only when you develop the plugin itself), the Claude Code project memory folder of the old path, and config files (`CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `.claude/settings*.json` in the workspace and its areas, `~/.claude/` files) that name the old path.

### `mem move`

Copies each record into the same topic/kind folder of the target area and deletes it at the source. Its outgoing edges are re-qualified (a bare edge points back into the source area, a qualified edge is re-based); referrers inside the source area are rewritten to the qualified reference; referrers in any other area under `--scan-root` (default: the common parent of both areas; required when that is `$HOME` or above) are only reported, never edited. A different record with the same id at the target, an unreadable target file, a symlink leaving a records directory, or a `supersedes`/`superseded_by` pair that the move would split is a conflict (exit 1, nothing changed); move both ends of a supersede pair together. `--dry-run` prints every planned write, edge rewrite and delete.

`mem move --batch FILE` takes a TSV, one row per record: `source_area<TAB>id<TAB>target_area[<TAB>perspective]` (paths absolute or relative to the file; blank lines and `#` comments allowed; each area must be an area root). It builds one plan for the whole batch, independent of row order: every moved record's edges are written against the final location of what they point at, including records moving in the same batch to another target. Referrers are rewritten only in the batch's source areas; referrers anywhere else are reported, never edited. A supersede pair moves only together into the same target; reference docs are refused; a different record with the same id in the target, a malformed row, an id listed twice for one source, two rows landing one id in one target, an id that is not found, or a hand-kept INDEX.md in any source or target area stops the batch before anything is written. `perspective` is set on the written copy (kind `user` always gets `user`). Arrivals are written and confirmed in every target first, then referrers are rewritten, then the originals deleted; rerun the same file after an interruption: a row whose record is already in the target and gone from the source is reported as `done` (an INDEX.md left stale by the interruption needs `mem lint --fix` first). Referrer rewrites edit files in the source areas, so run a batch only on versioned areas.

### Refusals

`add`, `link`, `unlink`, `delete` and `move` refuse (exit 1, nothing written) while an affected area's INDEX.md exists and differs from the generated one: it is hand-kept, or merely stale because a record file was added by hand. Adopt the area with `mem lint --fix` from inside it (or with `--area`) first. `current_focus` is exempt; `move` checks source and target. `mem delete` without ids is a usage error (exit 2).

### `mem lint` and `mem doctor`

`mem lint` checks one area; the codes are in [record format](record-format.md#lint-and-normalisation). `mem doctor` runs the same checks over every area below `--root` and adds the Sources, Docs, Not concluded, State, Wiring and Effect sections described in [architecture](architecture.md#doctor-ai_memdoctorpy). It changes nothing except `$AI_MEM_PATH/doctor_last_run`.

## `mem-dream`

Consolidates an area's records with the `claude` CLI: contradictions, redundancy, stale records. It is the archivist's tool, not a routine step.

```bash
mem-dream --area PATH [--neighbourhood ID...] --dry-run   # preview what it would read, no API calls
mem-dream --area PATH --neighbourhood ID...               # only these records and their one-hop links
```

Modes: `--mode single-haiku | single-sonnet | hier | team` (default `hier`). It calls the `claude` CLI with bare model aliases (`sonnet`, `haiku`), never versioned tags, and prints the CLI's stderr on failure. Results go to `dream-log/` unless `--no-save`.

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `AI_MEM_PATH` | `~/.local/share/ai-mem` | runtime state: retro log, doctor timestamp, retro roles |
| `AI_MEM_WORKSPACE_ROOT` | unset | the directory that contains your areas; default root for `mem find` |
| `AI_MEM_ADR_DIR` | `docs/records` | records directory relative to the area |

