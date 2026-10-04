#!/usr/bin/env python3
"""ai-mem installer — registers the MCP server with Claude Code, Gemini CLI, and/or Cursor."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()
HOME = Path.home()
SERVER_MODULE = "ai_mem.server"
DB_PATH = Path(
    __import__("os").environ.get("AI_MEM_PATH", str(HOME / ".local" / "share" / "ai-mem"))
)
MIGRATIONS_DIR = DB_PATH / ".migrations"


# ── helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], check=True):
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def patch_json(path: Path, updater):
    """Read JSON, apply updater(dict) → dict, write back."""
    data = json.loads(path.read_text()) if path.exists() else {}
    data = updater(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def python_exe() -> str:
    return sys.executable


def _remove_hook_command(entries: list[dict], module: str) -> None:
    """Strip any hook entry invoking `module` from `entries`, dropping groups left empty.

    Used to retire a hook install.py no longer registers (PreToolUse push→pull migration,
    2026-09-12) — re-running install.py on an existing installation self-heals by removing
    the stale entry, same surgical per-hook-object removal as _upsert_hook_command's own
    dedup path, so a user-customized group that bundles an unrelated hook keeps that hook.
    """
    marker = f"-m {module} "
    for entry in list(entries):
        hooks_list = entry.get("hooks", [])
        if not any(marker in h.get("command", "") for h in hooks_list):
            continue
        entry["hooks"] = [h for h in hooks_list if marker not in h.get("command", "")]
        if not entry["hooks"]:
            entries[:] = [e for e in entries if e is not entry]


def _existing_workspace_root(settings_path: Path, module: str) -> str:
    """Recover an already-installed AI_MEM_WORKSPACE_ROOT prefix from `module`'s current hook command.

    register_claude() re-prompts for the workspace root on every run. If a later run's prompt is
    left blank (e.g. reinstalling for an unrelated fix), the hook command must not silently
    regress to git-based detection just because that answer was empty this time -- update_mcp()
    already protects the MCP server's own env block the same way when workspace_root is falsy.
    """
    if not settings_path.exists():
        return ""
    try:
        data = json.loads(settings_path.read_text())
    except (json.JSONDecodeError, OSError):
        return ""
    marker = f"-m {module} "
    for group in data.get("hooks", {}).get("SessionStart", []):
        for hook in group.get("hooks", []):
            command = hook.get("command", "")
            if marker not in command:
                continue
            match = re.match(r"AI_MEM_WORKSPACE_ROOT=(\S+) ", command)
            if match:
                return match.group(1)
    return ""


def _upsert_hook_command(entries: list[dict], module: str, command: str, timeout: int, matcher: str | None = None) -> None:
    """Update the existing hook entry that invokes `module`, or append a new one.

    Matches by module name (`-m <module>`) rather than exact command string, so re-running
    install.py with a different env prefix (e.g. AI_MEM_WORKSPACE_ROOT changing) updates the
    existing entry in place instead of appending a duplicate that fires alongside the old one.

    Self-healing: if more than one hook entry already matches `module` (e.g. left over from
    installs predating this dedup logic, or from install.py having been invoked once via
    `python` and once via `python3`), the extras are removed here too — every install run
    sanitizes the file down to exactly one entry per module instead of only preventing new
    duplicates from being added. Removal is surgical: only the matching hook object is
    stripped out of a group's `hooks` list, and the group itself is dropped only if that
    leaves it empty — a user-customized group that bundles an unrelated hook alongside an
    old ai-mem duplicate keeps its unrelated hook intact.
    """
    marker = f"-m {module} "
    kept: dict | None = None
    for entry in list(entries):
        hooks_list = entry.get("hooks", [])
        matching = [h for h in hooks_list if marker in h.get("command", "")]
        if not matching:
            continue
        if kept is None:
            kept = matching[0]
            # drop any further duplicates that happen to sit in this same group too
            entry["hooks"] = [h for h in hooks_list if h is kept or marker not in h.get("command", "")]
            # only claim the matcher if the group is exclusively ours now — a group that
            # still holds an unrelated user hook keeps its own matcher untouched
            if matcher is not None and len(entry["hooks"]) == 1:
                entry["matcher"] = matcher
        else:
            entry["hooks"] = [h for h in hooks_list if marker not in h.get("command", "")]
            if not entry["hooks"]:
                # remove by identity, not value-equality — two unrelated emptied/empty
                # groups can be dict-equal and list.remove would drop the wrong one
                entries[:] = [e for e in entries if e is not entry]
    if kept is not None:
        kept["command"] = command
        kept["timeout"] = timeout
        return
    new_entry = {"hooks": [{"type": "command", "command": command, "timeout": timeout}]}
    if matcher is not None:
        new_entry["matcher"] = matcher
    entries.append(new_entry)


# ── installation steps ────────────────────────────────────────────────────────

def install_package():
    print("\n📦 Installing ai-mem package...")
    run([python_exe(), "-m", "pip", "install", "-e", str(REPO_ROOT), "--quiet"])
    stop_running_daemon()


def stop_running_daemon():
    """Stop any already-running background query daemon.

    The daemon (ai_mem/daemon.py) is a long-lived process hooks spawn lazily to stay warm
    across hook invocations — it does not hot-reload when its source changes. Without this
    step, a daemon started before this install/update keeps serving old code indefinitely;
    hooks will lazily respawn a fresh one (picking up whatever was just installed) on their
    next cache miss.
    """
    try:
        from ai_mem.daemon import stop_daemon
    except ImportError:
        return  # nothing installed yet to have started a daemon in the first place
    if stop_daemon(DB_PATH):
        print("   ✓ Stopped running background daemon (will restart with updated code).")


def prompt_workspace_root() -> str:
    """Ask the user for their workspace root directory. Returns empty string if skipped."""
    print("\nWorkspace root (optional but recommended):")
    print("  ai-mem uses this to name collections by folder structure instead of git remotes.")
    print("  Example: ~/workspace → acme-project/filming → repo.acme-project.filming")
    print("  Leave blank to use git-based detection instead.")
    raw = input("\nWorkspace root [default: skip]: ").strip()
    if not raw:
        return ""
    expanded = str(Path(raw).expanduser().resolve())
    if not Path(expanded).is_dir():
        print(f"  ⚠ '{expanded}' does not exist — skipping workspace root.")
        return ""
    print(f"  ✓ Workspace root: {expanded}")
    return expanded


def register_claude(workspace_root: str = ""):
    """Add ai-mem MCP server + SessionStart hook to ~/.claude.json and ~/.claude/settings.json."""
    # MCP server → ~/.claude.json
    mcp_path = HOME / ".claude.json"
    print(f"\n🤖 Registering with Claude Code ({mcp_path})...")

    INSTRUCTIONS = (
        "ai-mem keeps an agent's experience as git-native record files: each project's docs/records/ "
        "(decisions/, learnings/, todos/ per area, INDEX.md as catalogue, FOCUS.md for the current focus) and "
        "docs/reference/ for background docs; 'global' holds what applies everywhere. Nothing is pushed into "
        "your context -- pull on purpose: read INDEX.md / FOCUS.md or grep the files, and ask the librarian agent "
        "for 'why is it like this / was this tried before?'.\n\n"
        "Write as soon as knowledge surfaces (mem_add, one concept per id): domain = Decision/Why/Scope, "
        "pattern = Rule/When/Why, anti-pattern = Tried/Failed because/Instead, learning = Observed/Cause/Evidence, "
        "todo = open work (close it by deleting it and writing a learning with the commit sha). Link with mem_link "
        "(supersedes, confirms, contradicts, derived_from, causes, fixes, related). Keep FOCUS.md current "
        "(mem_add id='current_focus'); run /reflect after a task to do this as a ritual."
    )

    def update_mcp(data: dict) -> dict:
        entry: dict = {
            "type": "stdio",
            "command": python_exe(),
            "args": ["-m", SERVER_MODULE],
            "instructions": INSTRUCTIONS,
        }
        if workspace_root:
            entry["env"] = {"AI_MEM_WORKSPACE_ROOT": workspace_root}
        else:
            # Preserve an existing env block (e.g. AI_MEM_PATH), just don't add workspace root
            existing_env = data.get("mcpServers", {}).get("ai-mem", {}).get("env", {})
            if existing_env:
                entry["env"] = existing_env
        data.setdefault("mcpServers", {})["ai-mem"] = entry
        return data

    patch_json(mcp_path, update_mcp)

    # SessionStart + PostToolUse hooks + permissions → ~/.claude/settings.json
    # PreToolUse's automatic push (pretool_hook.py) was retired 2026-09-12 in favor of explicit
    # pull (mem_query) from role-scoped collections in agent/command prompts.
    # UserPromptSubmit's automatic push (userprompt_hook.py) was retired 2026-09-13 for the same
    # reason: it fired on every single message (not just once per session like SessionStart),
    # doing up to 4 parallel semantic queries each time.
    settings_path = HOME / ".claude" / "settings.json"
    # Hooks run as separate subprocesses spawned by Claude Code directly — they do NOT inherit
    # the "env" block set on the MCP server entry above (that only applies to the MCP server's own
    # subprocess). So workspace_root must be threaded into the hook commands themselves, or hooks
    # keep using git-based detection while mem_add/mem_query use workspace-root-based naming —
    # the same failure mode already documented for AI_MEM_PATH in ai-mem's own memory.
    if not workspace_root:
        workspace_root = _existing_workspace_root(settings_path, "ai_mem.hook")
    env_prefix = f"AI_MEM_WORKSPACE_ROOT={workspace_root} " if workspace_root else ""
    hook_cmd = f"{env_prefix}{python_exe()} -m ai_mem.hook 2>/dev/null || true"

    MCP_PERMISSIONS = [
        "mcp__ai-mem__mem_add",
        "mcp__ai-mem__mem_query",
        "mcp__ai-mem__mem_list",
        "mcp__ai-mem__mem_delete",
        "mcp__ai-mem__mem_move",
        "mcp__ai-mem__mem_dream",
        "mcp__ai-mem__mem_split",
        "mcp__ai-mem__mem_cleanup",
        "Bash(mem-dream *)",
    ]

    def update_settings(data: dict) -> dict:
        hooks = data.setdefault("hooks", {})

        session_hooks = hooks.setdefault("SessionStart", [])
        _upsert_hook_command(session_hooks, "ai_mem.hook", hook_cmd, timeout=10)

        if "UserPromptSubmit" in hooks:
            _remove_hook_command(hooks["UserPromptSubmit"], "ai_mem.userprompt_hook")
            if not hooks["UserPromptSubmit"]:
                del hooks["UserPromptSubmit"]

        if "PreToolUse" in hooks:
            _remove_hook_command(hooks["PreToolUse"], "ai_mem.pretool_hook")
            if not hooks["PreToolUse"]:
                del hooks["PreToolUse"]

        # PostToolUse only bumped last_accessed_at after every Write/Edit; with record files there
        # is no access counter left to bump (2026-10-04), so it is retired like the two above.
        if "PostToolUse" in hooks:
            _remove_hook_command(hooks["PostToolUse"], "ai_mem.posttool_hook")
            if not hooks["PostToolUse"]:
                del hooks["PostToolUse"]

        allow = data.setdefault("permissions", {}).setdefault("allow", [])
        for perm in MCP_PERMISSIONS:
            if perm not in allow:
                allow.append(perm)

        return data

    patch_json(settings_path, update_settings)

    install_mem_init_command()
    install_reflect_command()
    print("   ✓ MCP server + hooks + permissions registered. Restart Claude Code to activate.")


_MEM_INIT_CONTENT = """\
Initialize or update the ai-mem memory for the current project scope.

1. Detect the active scope:
   - Find the nearest CLAUDE.md (or agent.md) walking up from the current directory

   If AI_MEM_WORKSPACE_ROOT is set (recommended):
   - Compute the CLAUDE.md directory path relative to the workspace root
   - Each path component becomes a dot-separated scope segment
   - Sanitize each part: replace characters outside [a-zA-Z0-9._-] with underscore, strip leading/trailing ._-
   - Collection name: `repo.<scope>` (e.g. `repo.acme-project.filming`)
   - If CLAUDE.md is at the workspace root itself: falls back to `workspace`

   If AI_MEM_WORKSPACE_ROOT is not set (git-based fallback):
   - From the CLAUDE.md directory run: `git rev-parse --show-toplevel`
   - Try: `git remote get-url origin` and extract the trailing path component (strip .git suffix)
   - Fall back to the basename of the git root if no remote
   - If CLAUDE.md is not at the git root, append the relative subpath (dot-separated)
   - Collection name: `repo.<scope>` (e.g. `repo.ai-mem`, `repo.mymonorepo.backend`)

2. Tell the user: "Initializing ai-mem for scope '<scope>' using collection 'repo.<scope>'."

3. Ask: "What are you currently working on in this scope? (This becomes current_focus.)"

4. Call mem_add:
   - documents: [<user's answer>]
   - ids: ["current_focus"]
   - collection: "repo.<scope>"

5. Seed the collection by exploring the repo with your tools (Read, Bash, Grep).
   Answer each question below and store the answer with a separate mem_add call.
   Skip a question if the repo is too new or empty to answer it meaningfully.

   a. What is this project?
      Read README, pyproject.toml, package.json, or equivalent to find out.
      mem_add(ids=["seed_project"], collection="repo.<scope>",
              documents=[<answer>], metadatas=[{"type": "reference", "seeded_by": "mem-init"}])

   b. What are the non-obvious architectural decisions — things not immediately visible from the directory structure?
      mem_add(ids=["seed_architecture"], collection="repo.<scope>",
              documents=[<answer>], metadatas=[{"type": "pattern", "seeded_by": "mem-init"}])

   c. What conventions or gotchas would surprise a new contributor?
      mem_add(ids=["seed_conventions"], collection="repo.<scope>",
              documents=[<answer>], metadatas=[{"type": "pattern", "seeded_by": "mem-init"}])

   Each answer becomes a file: seed_project in docs/reference/, the patterns in docs/records/general/decisions/.
   Re-running /mem-init updates these files in place (same ids = upsert).

6. Confirm: "Done. Memory initialized for 'repo.<scope>'. Re-run /mem-init after major structural changes."

7. Close with this reminder:
   "One more thing: run /reflect after every task you complete. That closes the
   Plan → Code → Reflect loop and is the actual core of ai-mem — without it,
   ai-mem is just a database. With /reflect, the agent accumulates structured
   experience across sessions and builds progressively better context."

current_focus is written to docs/records/FOCUS.md. A focus that spans all repos goes into
collection="global" (its FOCUS.md lives in the records home, ai-mem-records/global/).
"""


def install_mem_init_command():
    commands_dir = HOME / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    target = commands_dir / "mem-init.md"
    target.write_text(_MEM_INIT_CONTENT)
    print(f"   ✓ /mem-init command installed at {target}")


def install_reflect_command():
    source = REPO_ROOT / "skills" / "examples" / "reflect.md"
    if not source.exists():
        print("   ⚠ skills/reflect.md not found, skipping /reflect install.")
        return
    commands_dir = HOME / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    target = commands_dir / "reflect.md"
    target.write_text(source.read_text())
    print(f"   ✓ /reflect command installed at {target}")


def run_pending_migrations():
    """Run one-time data migrations that have not yet been applied to this installation."""
    sentinel = MIGRATIONS_DIR / "boost_count_v1.done"
    if sentinel.exists():
        return

    migration_script = REPO_ROOT / "scripts" / "migrate_boost_count.py"
    if not migration_script.exists():
        return

    if not DB_PATH.exists():
        MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
        sentinel.touch()
        return

    print("\n🔄 Running one-time migration: boost_count_v1...")
    result = subprocess.run(
        [python_exe(), str(migration_script)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
        sentinel.touch()
        summary = [l for l in result.stdout.splitlines() if l.strip() and not l.startswith("  ")]
        print(f"   ✓ {summary[-1] if summary else 'Done.'}")
    else:
        print(f"   ⚠ Migration failed (non-fatal): {result.stderr.strip()[:120]}")


def run_records_migration(workspace_root: str = ""):
    """records_v1: move a ChromaDB-only store to git-native record files, once, with consent.

    Writes into the user's project repos, so it always shows a dry run first and only applies
    on an explicit yes. Declining leaves no sentinel: the next install.py run asks again.
    """
    sentinel = MIGRATIONS_DIR / "records_v1.done"
    if sentinel.exists():
        return
    if not DB_PATH.exists():
        MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
        sentinel.touch()
        return

    root = workspace_root or _existing_workspace_root(HOME / ".claude" / "settings.json", "ai_mem.hook")
    print("\n🔄 One-time migration: records_v1 (ChromaDB -> Markdown record files)")
    print("   Memory moves into each project's docs/records/ (decisions, learnings, todos, FOCUS.md)")
    print("   and docs/reference/. ChromaDB is kept as a backup; nothing is deleted.")
    if not root:
        root = input("   Directory that contains your projects [default: skip]: ").strip()
    env = dict(__import__("os").environ)
    cmd = [python_exe(), "-m", "ai_mem.adr_cli", "migrate", "--db-path", str(DB_PATH)]
    if root:
        root_path = Path(root).expanduser()
        env["AI_MEM_WORKSPACE_ROOT"] = str(root_path)
        cmd += ["--scan-root", str(root_path)]
        records_home = root_path / "ai-mem-records"
        if not records_home.exists() and input(
            f"   Create {records_home} for the global/workspace/subagent collections? [y/N]: "
        ).strip().lower() == "y":
            records_home.mkdir(parents=True)
    else:
        print("   Without a directory only collections with a recorded location can be placed.")

    dry = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if dry.returncode != 0:
        print(f"   ⚠ Migration dry run failed (non-fatal): {dry.stderr.strip()[:200]}")
        return
    print("\n" + "\n".join(f"   {line}" for line in dry.stdout.splitlines()))
    if input("\n   Write these files into your project repos now? [y/N]: ").strip().lower() != "y":
        print("   Skipped. Run it later with: mem-adr-sync migrate --apply (asked again on the next install).")
        return

    applied = subprocess.run(cmd + ["--apply"], capture_output=True, text=True, env=env)
    if applied.returncode != 0:
        print(f"   ⚠ Migration failed (non-fatal): {applied.stderr.strip()[:200]}")
        return
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)
    sentinel.touch()
    print("\n".join(f"   {line}" for line in applied.stdout.splitlines() if line.startswith(("Backup", "Report"))))
    print("   ✓ Done. Review the report, then commit docs/records/ (and docs/reference/) in each repo.")


def register_gemini():
    """Add ai-mem to ~/.gemini/settings.json mcpServers."""
    config_path = HOME / ".gemini" / "settings.json"
    print(f"\n♊ Registering with Gemini CLI ({config_path})...")

    def update(data: dict) -> dict:
        data.setdefault("mcpServers", {})["ai-mem"] = {
            "command": python_exe(),
            "args": ["-m", SERVER_MODULE],
        }
        return data

    patch_json(config_path, update)
    print("   ✓ Registered. Restart Gemini CLI to activate.")


def register_cursor():
    """Add ai-mem to Cursor's MCP settings."""
    # Cursor stores MCP config at ~/.cursor/mcp.json (all platforms)
    config_path = HOME / ".cursor" / "mcp.json"
    print(f"\n🖱  Registering with Cursor ({config_path})...")

    def update(data: dict) -> dict:
        data.setdefault("mcpServers", {})["ai-mem"] = {
            "command": python_exe(),
            "args": ["-m", SERVER_MODULE],
        }
        return data

    patch_json(config_path, update)
    print("   ✓ Registered. Restart Cursor to activate.")


# ── UI ────────────────────────────────────────────────────────────────────────

TARGETS = {
    "1": ("Claude Code", register_claude),
    "2": ("Gemini CLI",  register_gemini),
    "3": ("Cursor",      register_cursor),
}


def prompt_targets() -> list:
    print("\nSelect AI tools to configure:")
    for key, (label, _) in TARGETS.items():
        print(f"  {key}) {label}")
    print("  a) All  [default]")
    choice = input("\nChoice [1/2/3/a]: ").strip().lower() or "a"

    if choice == "a":
        return list(TARGETS.values())
    selected = []
    for ch in choice:
        if ch in TARGETS:
            selected.append(TARGETS[ch])
        else:
            print(f"  ⚠ Unknown option '{ch}', skipping.")
    return selected


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--sync-commands", action="store_true")
    args, _ = parser.parse_known_args()

    if args.sync_commands:
        install_mem_init_command()
        install_reflect_command()
        print("\n✅ Commands synced.")
        return

    print("=" * 50)
    print("  ai-mem installer")
    print("=" * 50)

    install_package()
    run_pending_migrations()

    workspace_root = prompt_workspace_root()
    run_records_migration(workspace_root)

    targets = prompt_targets()
    for label, register_fn in targets:
        try:
            if register_fn is register_claude:
                register_fn(workspace_root)
            else:
                register_fn()
        except Exception as e:
            print(f"   ✗ {label} registration failed: {e}")

    print("\n✅ Done! Restart your AI tool(s) to start using ai-mem.")
    print(f"\n   Data will be stored at: {HOME / '.local' / 'share' / 'ai-mem'}")
    print("   Override with: AI_MEM_PATH=/your/path")
    print("\n   Quick start:")
    print("     /mem-init   — initialize memory for your current project")
    print("     /reflect    — run after every task to close the learning loop")
    print("     python3 install.py --sync-commands   — sync only the /mem-init and /reflect commands")
    print(f"\n   How the framework works: {REPO_ROOT / 'docs' / 'epistemology-framework.md'}")


if __name__ == "__main__":
    main()
