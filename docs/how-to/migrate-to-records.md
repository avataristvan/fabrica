# How to migrate an old installation to record files (records_v1)

Until 2026-10-04 ai-mem kept memory in a vector database store (`~/.local/share/ai-mem/chroma.sqlite3`). From then on it keeps memory as Markdown files in each area (`domain_records_model_replaces_chroma_2026_10_04`), and an existing installation is migrated once. Skip this page if you have no `chroma.sqlite3` or if `~/.local/share/ai-mem/.migrations/records_v1.done` exists. Why the move happened: [Organisational memory](../explanation/organisational-memory.md) and the retired-system evidence under [sources/](../sources/).

An agent that updates ai-mem unattended follows [`UPGRADING.md`](../../UPGRADING.md) instead of this page: it lists the exact commands and the conditions under which to stop and ask. The later upgrade steps (collections to areas, tool server to plugin) are listed there too.

## The short way

```bash
cd ai-mem && git pull
python3 install.py
```

After the package update, `install.py` asks for your workspace root (the directory that contains your projects). It then shows a dry run (which files would go into which repo) and writes only if you answer `y`. Answering `n` changes nothing; the next `install.py` run asks again.

## By hand

```bash
export AI_MEM_WORKSPACE_ROOT=~/workspace            # wherever your projects live
mem-adr-sync migrate                                 # dry run: shows the plan
mem-adr-sync migrate --apply                         # writes the files
mem-adr-sync migrate --apply --root repo.foo=~/code/foo   # place a collection the scan missed
```

## What happens

| Entry | Becomes |
|---|---|
| `domain`, `pattern`, `anti-pattern`, `learning`, `todo`, `user` | `<repo>/docs/records/<area>/<kind>/<id>.md` (as is) |
| `current_focus` | `<repo>/docs/records/FOCUS.md` |
| `reference` | `<repo>/docs/reference/<id>.md` (plain text) |
| `feedback`, `project`, `fact`, untyped | classified by rule (see below) and listed in the report |

The rule for untyped and legacy types: a text starting with `Tried:` or `Anti-pattern` becomes an `anti-pattern`, `Decision:` a `domain`, `Observed:` a `learning`, `Rule:` a `pattern`; otherwise `feedback` becomes `pattern`, a `todo_*` id or a `TODO` text becomes `todo` (a `RESULT` text, i.e. closed work, becomes `learning`), and everything else `learning`. Measured against a hand-sorted store this matched in 79% of the auto-classified cases, so **read the "Auto-classified" table in the report** and retype what is wrong (`mem add --id ID --type TYPE` on the written record).

Which directory a collection belongs to is derived exactly as the old runtime did: every `CLAUDE.md` directory below the workspace root is resolved to its collection name. Collections named by older rules are matched by a unique directory name (reported as such); anything left over is listed under "Collections without a directory": place it with `--root`. `global`, `workspace` and `subagent.*` go to `$AI_MEM_WORKSPACE_ROOT/ai-mem-records/<collection>/` when that directory exists (`install.py` offers to create it). The next upgrade step redistributes those into areas by topic (`UPGRADING.md`, "Collections -> areas").

## Safety

- The store is opened read-only with Python's own `sqlite3` (no extra package needed) and is never written or deleted from; it is copied to `~/.local/share/ai-mem.bak-records-v1` first.
- `--apply` marks the migration done (`~/.local/share/ai-mem/.migrations/records_v1.done`) only when nothing was left over: no collection without a directory, no conflict, no id that cannot be a filename. Otherwise it writes what it can, says why, and exits 1; place the rest with `--root` and run it again. Until it is marked done, SessionStart prints an "ai-mem upgrade pending" line.
- Some leftovers cannot be fixed by a re-run: an id that cannot be a filename stays in the store (which the migration never writes), and a collection may belong to a project that no longer exists. After reading those sections of the report, a human (never an unattended agent) may accept them as skipped: `touch ~/.local/share/ai-mem/.migrations/records_v1.done`.
- Existing files are never overwritten. A different file at the target, or the same id filed in another folder, is reported as a conflict and left alone.
- The run is idempotent: a second run writes nothing new.

## Afterwards

1. Read `~/.local/share/ai-mem/records-migration-report.md`.
2. Run `mem lint` in each area and read the findings (`mem lint --fix` repairs what is fixable).
3. Commit `docs/records/` (and `docs/reference/`) in each project; commit `ai-mem-records/` if you created it.
4. Restart Claude Code. SessionStart now only points at `docs/records/` and the librarian agent; it no longer pushes memory content.
5. Run `mem doctor` once to see what else needs attention.
