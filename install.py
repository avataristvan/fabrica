#!/usr/bin/env python3
"""ai-mem installer — registers the MCP server with Claude Code, Gemini CLI, and/or Cursor.

The agents, skills, hooks and `mem` commands come with the Claude Code plugin (`claude plugin install ai-mem@ai-mem`),
not from here; see UPGRADING.md.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from ai_mem import upgrade_guard

REPO_ROOT = Path(__file__).parent.resolve()
HOME = Path.home()
SERVER_MODULE = "ai_mem.server"
DB_PATH = Path(
    __import__("os").environ.get("AI_MEM_PATH", str(HOME / ".local" / "share" / "ai-mem"))
)


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
    the stale entry. Removal is per hook object, so a user-customized group that bundles an
    unrelated hook keeps that hook.
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
    """Add the ai-mem MCP server to ~/.claude.json and its permissions to ~/.claude/settings.json."""
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

    # Hooks come from the plugin (hooks/hooks.json); here only the retired legacy entries are removed.
    settings_path = HOME / ".claude" / "settings.json"

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

    print("   ✓ MCP server + permissions registered. Restart Claude Code to activate.")


def offer_plugin_switch():
    """The plugin replaces the hooks, /reflect and /mem-init commands and links older versions installed; remove them on consent."""
    import uninstall

    leftovers = uninstall.plugin_leftovers(HOME)
    if not leftovers:
        return
    print("\nThe ai-mem plugin now provides what older versions installed here:")
    for item in leftovers:
        print(f"  - {item}")
    print("Left in place they fire twice once the plugin is installed (claude plugin install ai-mem@ai-mem).")
    if input("Remove them now? [y/N]: ").strip().lower() == "y":
        uninstall.remove_plugin_provided(HOME, dry_run=False)


def run_pending_migrations():
    """Run one-time data migrations that have not yet been applied to this installation."""
    migrations_dir = upgrade_guard.migrations_dir(DB_PATH)
    sentinel = migrations_dir / "boost_count_v1.done"
    if sentinel.exists():
        return

    migration_script = REPO_ROOT / "scripts" / "migrate_boost_count.py"
    if not migration_script.exists():
        return

    if not DB_PATH.exists():
        migrations_dir.mkdir(parents=True, exist_ok=True)
        sentinel.touch()
        return

    print("\n🔄 Running one-time migration: boost_count_v1...")
    result = subprocess.run(
        [python_exe(), str(migration_script)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        migrations_dir.mkdir(parents=True, exist_ok=True)
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
    if upgrade_guard.records_v1_sentinel(DB_PATH).exists():
        return
    if not DB_PATH.exists():
        upgrade_guard.mark_records_v1_done(DB_PATH)
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
        if "Report:" in applied.stdout:
            # The files were written but the plan was not clean: records_v1 is NOT marked done, so the
            # upgrade guard stays on (SessionStart and `mem` say so) until a clean `migrate --apply`.
            print("\n".join(f"   {line}" for line in applied.stdout.splitlines() if line.startswith(("Backup", "Report"))))
            print(f"   ⚠ Migration applied, but records_v1 is NOT marked done: {applied.stderr.strip()[:200]}")
        else:
            print(f"   ⚠ Migration failed, nothing was marked done: {applied.stderr.strip()[:200]}")
        print("     The upgrade guard stays on. Re-run: mem-adr-sync migrate --apply (see UPGRADING.md).")
        return
    upgrade_guard.mark_records_v1_done(DB_PATH)
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
    parser.add_argument("--plugin-switch", action="store_true")
    args = parser.parse_args()

    if args.plugin_switch:
        offer_plugin_switch()
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

    offer_plugin_switch()

    print("\n✅ Done! Restart your AI tool(s) to start using ai-mem.")
    print(f"\n   Data will be stored at: {HOME / '.local' / 'share' / 'ai-mem'}")
    print("   Override with: AI_MEM_PATH=/your/path")
    print("\n   Quick start:")
    print("     claude plugin marketplace add " + str(REPO_ROOT) + " && claude plugin install ai-mem@ai-mem")
    print("                 — agents, /ai-mem:reflect, /ai-mem:setup, the mem command and the hooks")
    print("     /ai-mem:setup   — wire your teams and CLAUDE.md to ai-mem (proposes, applies on your approval)")
    print(f"\n   How the framework works: {REPO_ROOT / 'docs' / 'epistemology-framework.md'}")


if __name__ == "__main__":
    main()
