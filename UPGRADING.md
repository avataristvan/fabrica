# Upgrading an ai-mem installation

Written for an agent that updates ai-mem unattended. Follow the steps in order, run each
command exactly as written, and **stop at every "STOP" condition**: report what you saw to a
human and wait. Never improvise around a STOP: no merge, rebase, reset, stash, checkout,
`git clean`, no `--force`, no deleting or editing files by hand, no `install.py` (it is
interactive and meant for a human).

Breaking steps, oldest first:

| Step | What changes | Status |
|---|---|---|
| records_v1 | Memory moves out of ChromaDB into Markdown record files in each project | released |
| Collections -> areas | Collection folders are redistributed into areas | not yet released |
| MCP server -> plugin | The MCP server is replaced by a Claude Code plugin | not yet released |

## Preconditions

Run these from the ai-mem checkout (the directory that contains this file).

1. `git status --porcelain` prints nothing. Otherwise: **STOP** (local changes).
2. The interpreter: `PY=$(command -v python3)`, then
   `"$PY" -c "import ai_mem, pathlib; print(pathlib.Path(ai_mem.__file__).resolve().parent.parent)"`
   must print this checkout's absolute path (`pwd -P`). If it fails or prints another path:
   **STOP** (unknown installation). Use `"$PY"` for every command below.
3. The store: `AI_MEM_PATH` if set, else `~/.local/share/ai-mem`. Call it `$STORE`. Work
   only with `$STORE`; other directories that look like ai-mem stores are not yours to read.
4. Do not call any ai-mem MCP tool (`mem_add`, `mem_query`, ...) during the upgrade: an MCP
   server that is already running keeps its old code and may still write to ChromaDB.
5. The workspace: `AI_MEM_WORKSPACE_ROOT` must be set to the directory that contains the
   user's projects. If it is not set: **STOP** (ask which directory holds the projects).

## records_v1: ChromaDB -> record files

Skip this section if `$STORE/chroma.sqlite3` does not exist, or if
`$STORE/.migrations/records_v1.done` exists. Otherwise (a SessionStart line saying
"ai-mem upgrade pending" means exactly this):

1. **Update the code:** `git pull --ff-only`.
   If it exits non-zero, says the branches diverged, or asks for anything: **STOP**. Do not
   merge, rebase, reset or retry with other flags.
2. **Install:** `"$PY" -m pip install -e .` (no extras; chromadb is not needed).
   Non-zero exit: **STOP**.
3. **Dry run:** `"$PY" -m ai_mem.adr_cli migrate`
   It reads the store read-only and writes nothing. Keep its output. **STOP** if any of:
   - the exit code is not 0, or there is a traceback / error message;
   - a line starts with `NOT CLEAN`;
   - the summary mentions `collections without a directory`, `placed by directory name only`,
     `conflicts`, or `ids cannot be filenames`.
   Do not try to fix these yourself (no `--root`, no creating directories, no editing
   `adr_collection_roots.json`); a human decides where those entries belong.
   If none of these appear, the placement is decided: do not second-guess the directories
   in the summary, go on to step 4.
4. **Apply:** `"$PY" -m ai_mem.adr_cli migrate --apply`
   It copies the store to `<store>.bak-records-v1` first and never changes the store itself.
   Exit code 1 (or anything not 0): **STOP** -- it applied what it could but did not mark the
   migration done; the reason is on stderr and in `$STORE/records-migration-report.md`.
5. **Verify:**
   - `$STORE/.migrations/records_v1.done` exists.
   - The apply printed the same summary as the dry run in step 3.
   - Re-run the dry run (`"$PY" -m ai_mem.adr_cli migrate`): it must report `0 files to write`
     and no `NOT CLEAN` line. Otherwise: **STOP**.
   - For each row of the "Collections" table in `$STORE/records-migration-report.md` whose
     directory contains `docs/records/`:
     `"$PY" -m ai_mem.adr_cli reindex --collection <collection>` exits 0. Otherwise: **STOP**.
6. **Hand over to a human** (do not do these yourself): read the report, especially the
   "Auto-classified" table; commit `docs/records/` (and `docs/reference/`) in each project
   and `ai-mem-records/` if present; restart Claude Code (all sessions). After the restart,
   run the dry run once more: anything other than `0 files to write` was written to ChromaDB
   by a session that still ran the old server during the upgrade -- `migrate --apply` again
   picks it up.

ChromaDB stays on disk as it is. `AI_MEM_BACKEND=chroma` (the rollback to the old store)
needs the extra: `"$PY" -m pip install -e '.[chroma]'`.

## Collections -> areas

Not yet released -- stop here.

## MCP server -> plugin

Not yet released -- stop here.
