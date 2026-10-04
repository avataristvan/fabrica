# Migrating from ChromaDB to record files (records_v1)

From 2026-10-04 on, ai-mem keeps memory as git-native Markdown files in each project
instead of in ChromaDB (`domain_records_model_replaces_chroma_2026_10_04`). An existing
installation is migrated once.

## The short way

```bash
cd ai-mem && git pull
python3 install.py
```

After the package update, `install.py` asks for your workspace root (the directory that
contains your projects). It then shows a dry run (which files would go into which repo)
and writes only if you answer `y`. Answering `n` changes nothing; the next `install.py`
run asks again.

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

The rule for untyped/legacy types: a text starting with `Tried:` or `Anti-pattern` becomes an
`anti-pattern`, `Decision:` a `domain`, `Observed:` a `learning`, `Rule:` a `pattern`;
otherwise `feedback` becomes `pattern`, a `todo_*` id or a `TODO` text becomes `todo`
(a `RESULT` text, i.e. closed work, becomes `learning`), and everything else `learning`.
Measured against a hand-sorted store this matched in 79% of the auto-classified cases, so
**read the "Auto-classified" table in the report** and retype what is wrong
(`mem_add` with the same id and the right `type`).

Which directory a collection belongs to is derived exactly like at runtime: every
`CLAUDE.md` directory below the workspace root is resolved to its collection name.
Collections named by older rules are matched by a unique directory name (reported as
such); anything left over is listed under "Collections without a directory" -- place it
with `--root`. `global`, `workspace` and `subagent.*` go to
`$AI_MEM_WORKSPACE_ROOT/ai-mem-records/<collection>/` when that directory exists
(`install.py` offers to create it).

## Safety

- ChromaDB is copied to `~/.local/share/ai-mem.bak-records-v1` first and is never deleted
  from. Only the `type`/`area` metadata of auto-classified entries is aligned with their new
  files, so a later `mem_add` keeps the file.
- Existing files are never overwritten. A different file at the target, or the same id
  filed in another folder, is reported as a conflict and left alone.
- The run is idempotent: a second run writes nothing new.

## Afterwards

1. Read `~/.local/share/ai-mem/records-migration-report.md`.
2. Commit `docs/records/` (and `docs/reference/`) in each project; commit `ai-mem-records/`
   if you created it.
3. Restart Claude Code. SessionStart now only points at `docs/records/` and the librarian
   agent; it no longer pushes memory content.
