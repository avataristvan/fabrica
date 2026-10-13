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
| MCP server -> plugin | The MCP server is replaced by a Claude Code plugin (part 1: install the plugin; part 2: remove the server) | released |

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

ChromaDB stays on disk as it is. The Chroma backend itself (`AI_MEM_BACKEND=chroma`, the MCP server, the daemon) no longer exists in the code; a human who needs it checks out the tag `v0-last-mcp` (the last commit that had it). The migration above stays and needs no extra package.

## Collections -> areas

The records that lived in collection folders (`ai-mem-records/<collection>/`) belong in the area of the topic they describe. Where each record goes is a judgment about your projects: the agent never decides it automatically. If you are an agent following this section, stop here and ask the human for the placement of every record.

1. Check that the source areas are under git and committed, and `mem doctor --root <workspace>` is clean enough to compare against later. Save its output and checksums of the existing records in the target areas.
2. Agree a placement table with the human: one row per record (`source_area<TAB>id<TAB>target_area<TAB>perspective`, paths relative to the file or absolute, `#` comments). Hand-kept INDEX.md files in a target area stop `mem move`; adopt them first with `mem lint --fix` in that area.
3. Dry run: `mem move --batch <table.tsv> --dry-run --scan-root <workspace>`. It lists every write, delete and edge rewrite and stops on conflicts (same id with different content in the target, supersede pairs that would cross areas). Resolve conflicts first.
4. Apply: `mem move --batch <table.tsv> --scan-root <workspace>`. A rerun after an interruption continues where it stopped.
5. `mem doctor --root <workspace>`: no records left under collection names, no new dangling edges compared with step 1. Reference docs (`docs/reference/`) are not records: copy them by hand and remove the original afterwards.

## MCP server -> plugin

Two parts, in this order. Part 1 installs the plugin next to the still-registered MCP server. Part 2 removes the server's registration and permissions; the server's code is gone from this checkout once you have pulled.

### Part 1: install the plugin

Skip steps 2 to 5 if `claude plugin list` already shows `ai-mem@ai-mem` as enabled. Run from the ai-mem checkout.

1. Preconditions of this document hold, and records_v1 is done: `$STORE/.migrations/records_v1.done` exists, or `$STORE/chroma.sqlite3` does not. Otherwise: **STOP** (finish that section first).
2. `claude --version` exits 0. Otherwise: **STOP** (no Claude Code CLI on the PATH).
3. `command -v python3` prints a path. The plugin's hooks and its `mem` command call `python3` and need nothing else installed. Otherwise: **STOP**.
4. `claude plugin validate "$PWD"` exits 0 (warnings are fine). Otherwise: **STOP**; do not edit the manifest.
5. Install: `claude plugin marketplace add "$PWD"`, then `claude plugin install ai-mem@ai-mem`. Non-zero exit, a prompt, or an error that the name is taken by another marketplace: **STOP**.
6. **Hand over to a human** (do not do these yourself; the first edits `~/.claude`):
   - `python3 install.py --plugin-switch` lists the hooks in `~/.claude/settings.json`, the `~/.claude/commands/reflect.md` and `~/.claude/commands/mem-init.md` commands (only the copies ai-mem installed; a command the user wrote under the same name is not listed and stays) and the symlinks (`~/.claude/agents/{librarian,archivist,anchor-lint}.md`, `~/.claude/skills/handoff-protocol`, `~/.claude/ai-mem/`) that the plugin now provides, and removes them on `y`. Until then every hook fires twice, and a bare `librarian` or `archivist` agent from the old links shadows the plugin's.
   - Optionally set the plugin's options with `/plugin configure ai-mem@ai-mem` in Claude Code; while they are unset the hooks use their defaults (`retro_roles` includes `ai-mem:anchor-lint`).
   - Restart Claude Code (all sessions). `/reflect` is now `/ai-mem:reflect`; agents are called `ai-mem:librarian`, `ai-mem:archivist`, `ai-mem:anchor-lint`; the skill is `ai-mem:handoff-protocol`. Team files that name the bare ones (the one-line hook-in, `Agent(subagent_type="librarian")`) need the prefix: `mem doctor` (Wiring) lists teams that lack the hook-in.
   - In a new session inside an area: the SessionStart output has an `Area:` line, `mem context` works from Bash, and `mem doctor` (Wiring) shows the plugin enabled and no duplicate hooks.
   - `/mem-init` is replaced by `/ai-mem:setup`. Run it in a session to get the hook-in proposals for the teams `mem doctor` lists and the CLAUDE.md lines; it changes the user's files only on approval, so an unattended agent does not run it ([how-to](docs/how-to/set-up.md)).

Do not remove the `ai-mem` MCP registration or the `mcp__ai-mem__*` permissions in part 1; the server keeps running until part 2. Do not call `mem_*` MCP tools to check the plugin.

What changed, for the record: hooks moved from `~/.claude/settings.json` into the plugin's `hooks/hooks.json`; `AI_MEM_WORKSPACE_ROOT` is no longer put in the hook commands (the area is found by walking up from the working directory, the collection routing line keeps using the environment of the session); agents and skills moved from `examples/agents/` and `skills/examples/` to `agents/` and `skills/reflect/`; `/mem-init` became the plugin skill `/ai-mem:setup`, and `install.py --sync-commands` is gone (`install.py` now refuses the flag with exit code 2 instead of starting the interactive install).

### Part 2: remove the server

The code no longer contains the MCP server (`ai_mem.server`), the query daemon, the Chroma/BM25 backend, the push hooks and the collection routing line. What is left to do is on the user's machine: the MCP registration in `~/.claude.json` (and `~/.gemini/settings.json`, `~/.cursor/mcp.json` if the user registered it there), the `mcp__ai-mem__*` permissions and old push hooks in `~/.claude/settings.json`. Those files belong to the user and to a running Claude Code, so an agent never edits them: `install.py` does it, with the user's consent, and only a human runs `install.py`.

Run from the ai-mem checkout, after part 1 and records_v1 are done.

1. Preconditions of this document hold (re-read this file after the pull in step 2: part 2 may have changed), `claude plugin list` shows `ai-mem@ai-mem` as enabled, and `$STORE/.migrations/records_v1.done` exists or `$STORE/chroma.sqlite3` does not. Otherwise: **STOP** (finish the earlier parts first).
2. Update the code: `git pull --ff-only`. Non-zero exit, diverged branches, or a prompt: **STOP**.
3. Reinstall the package: `"$PY" -m pip install -e .` (no extras; ai-mem has no runtime dependencies now). Non-zero exit: **STOP**.
4. Check the commands the plugin uses: `(cd "$PWD" && "$PY" -m ai_mem.mem_cli context)` exits 0 (this checkout has a `docs/records/`), and `"$PY" -m ai_mem.adr_cli --help` exits 0. Otherwise: **STOP**.
5. Look, do not touch: `grep -c 'mcp__ai-mem__' ~/.claude/settings.json` and `grep -c '"ai-mem"' ~/.claude.json` (a missing file counts as 0). Report both numbers to the human. They count lines, so they also match unrelated text and miss registrations in other scopes (`projects.<path>.mcpServers`, a project `.mcp.json`, `settings.local.json`, `~/.gemini`, `~/.cursor`): treat them as a hint. The real check is `claude mcp list` in step 7; do not run it earlier (it creates `.claude` state in the directory it runs in).
6. **Hand over to a human** (do not do these yourself):
   - Close all Claude Code sessions, then run `python3 install.py --plugin-switch`. It lists the leftovers of the MCP era (the `mcpServers["ai-mem"]` entries, the `mcp__ai-mem__*` permissions, retired push hooks) and removes them on `y`; the user's other servers, permissions and hooks stay. Closing the sessions first matters: a running Claude Code rewrites `~/.claude.json` when it exits.
   - If `AI_MEM_BACKEND` or `AI_MEM_ADR_DISABLED` is set in a shell profile, remove it: nothing reads it any more.
   - Restart Claude Code. The `mem_*` tools are gone; agents read through the librarian and write through the archivist (`/ai-mem:reflect`).
7. **Verify only after the human has told you the hand-over is done.** Until then **STOP** here and report what you did and the step-5 numbers; do not run this step on your own. Afterwards: `claude mcp list` does not show `ai-mem`, and the step-5 numbers are 0 (or the human explains the remainder). The `Area:` line in a new session is for the human to confirm; you cannot open one. Otherwise: **STOP** and report which one failed.

Rollback is the tag `v0-last-mcp`: a human checks it out in the checkout, installs that version's dependencies (`pip install -e . chromadb`) and re-registers the server with that version's `install.py`. The Chroma store on disk and `$STORE.bak-*` are never touched by any step here.

What changed, for the record: `ai_mem/server.py`, `daemon*.py`, `_hook_deps.py`, the PreToolUse/UserPromptSubmit/PostToolUse push modules, `infrastructure/{chroma,bm25,markdown_adr}_repository.py`, `repository_factory.py`, `agent_context.py`, `session_stats.py`, `injection_log.py` and the use cases only the server called are gone; `mem-adr-sync export`/`import` (the Chroma round trip) and `mem-dream --collection`/`--expert` are gone (`mem-dream --area` stays); SessionStart prints `Area:` and `Records:` lines (and the upgrade/doctor pointers) instead of `Active collection:`; `pyproject.toml` has `dependencies = []` and one extra, `dev`.
