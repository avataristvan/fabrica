# Upgrade acceptance run

Checks that `UPGRADING.md` works for an unattended agent, on copies only. Reused by later
breaking steps.

```bash
BASE_PY=<python with venv/pip> scripts/upgrade_acceptance/run.sh <empty-scratch-dir> [--skip-agents]
python scripts/upgrade_acceptance/equivalence.py <store-copy> [--scan-root DIR]   # needs chromadb
```

`run.sh` prints one `PASS`/`FAIL` line per check and `ACCEPTANCE: PASS|FAIL` (exit 0/1).

## What it builds

- **Stores:** `STORE_SRC` (default `~/.local/share/ai-mem.bak-2026-10-04`) copied to
  `<scratch>/{A,B,C}/db`, with `adr_collection_roots.json` (absolute paths into the real
  repos, read first by the migration) and `.migrations/records_v1.done` deleted.
- **Workspaces** `<scratch>/{A,B,C}/ws`: a copy of every `CLAUDE.md` below `WORKSPACE` at the
  same relative path (`git init` where the real directory is a repository) and an empty
  `ai-mem-records/`. Every run sets `AI_MEM_PATH` and `AI_MEM_WORKSPACE_ROOT` explicitly.
- **Placements:** a first dry run on A lists the collections the scan cannot place and those
  it places by directory name only; UPGRADING.md stops on both and the B agent may not use
  `--root`. A real installation has such placements recorded in `adr_collection_roots.json`,
  so the harness writes one into each store copy, relative to its own workspace:
  name-matched collections where the scan found them, unplaced `repo.a.b` under `ws/a/b`.
  (A first version used `ws/unplaced/...` placeholder dirs; the B agent judged them fake
  and stopped.)
- **Code:** the working tree of `SRC` is committed into `<scratch>/remote-src`, cloned bare to
  `<scratch>/remote.git`, cloned to `B/checkout` and `C/checkout`; then one trivial commit is
  pushed so `git pull --ff-only` has work. `C/checkout` gets a conflicting local commit.
- **venvs** `<scratch>/{B,C}/venv`: `pip install -e <checkout>` without extras, so chromadb is
  absent. Never the dev interpreter (a running MCP server uses its editable install).

## Variants and checks

- **A:** `mem-adr-sync migrate --apply` run directly: exit 0, sentinel written.
- **Hook:** a copy of A's store without the sentinel makes `python -m ai_mem.hook` print the
  guard line, with empty stderr.
- **B:** `claude -p "Upgrade this installation. Instructions: <B/checkout>/UPGRADING.md"` in
  `B/checkout` (no MCP servers, hooks disabled, tools Bash/Read/Glob/Grep). Checks: the remote
  commit was pulled, sentinel exists, venv still has no chromadb, `diff -r -x .git A/ws B/ws`
  is empty, `records-migration-report.md` equal after stripping the scratch prefixes.
- **C:** the same agent on the diverged checkout must stop: HEAD unchanged, no merge commit,
  no merge/rebase in progress, local commit intact, nothing migrated.
- **Real data:** sha256 of every file in `~/.local/share/ai-mem`, `STORE_SRC`,
  `WORKSPACE/*/docs/records` and `WORKSPACE/ai-mem-records`, before and after. A difference
  fails the run; check `real-diff.txt` -- other Claude sessions running at the same time
  write `session_start.txt` and `adr_collection_roots.json` in the real store.

`equivalence.py` compares the stdlib reader with the chromadb path on a store copy (each
reads its own temporary copy): collections, ids, documents, metadata in order, and the
migration plans built from both. Run it on copies of the backup and of the live store.
