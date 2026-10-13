#!/usr/bin/env python3
"""ai-mem installer — installs the Python package, runs the records_v1 migration, and offers to remove what older versions left.

The agents, skills, hooks and `mem` commands come with the Claude Code plugin (`claude plugin install ai-mem@ai-mem`),
not from here; see UPGRADING.md. There is no MCP server any more: `--plugin-switch` offers to remove the old MCP
registration and `mcp__ai-mem__*` permissions together with the other leftovers.
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
DB_PATH = Path(
    __import__("os").environ.get("AI_MEM_PATH", str(HOME / ".local" / "share" / "ai-mem"))
)


# ── helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], check=True):
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def python_exe() -> str:
    return sys.executable


def _existing_workspace_root(settings_path: Path, module: str) -> str:
    """Recover an already-installed AI_MEM_WORKSPACE_ROOT prefix from `module`'s current hook command.

    The migration needs the directory that holds the projects; a blank answer must not lose the one an
    older install recorded in its SessionStart hook command.
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


def prompt_workspace_root() -> str:
    """Ask the user for their workspace root directory. Returns empty string if skipped."""
    print("\nWorkspace root (optional but recommended):")
    print("  The records_v1 migration scans it for CLAUDE.md directories to place old ChromaDB collections.")
    print("  Leave blank to skip (only collections with a recorded location can then be placed).")
    raw = input("\nWorkspace root [default: skip]: ").strip()
    if not raw:
        return ""
    expanded = str(Path(raw).expanduser().resolve())
    if not Path(expanded).is_dir():
        print(f"  ⚠ '{expanded}' does not exist — skipping workspace root.")
        return ""
    print(f"  ✓ Workspace root: {expanded}")
    return expanded


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


def offer_mcp_removal():
    """The MCP server is gone; remove its registration and permissions (and retired push hooks) on consent."""
    import uninstall

    leftovers = uninstall.mcp_leftovers(HOME)
    if not leftovers:
        return
    print("\nThe ai-mem MCP server no longer exists; these registrations point at it:")
    for item in leftovers:
        print(f"  - {item}")
    print("Close running Claude Code sessions first: a running session rewrites ~/.claude.json on exit.")
    if input("Remove them now? [y/N]: ").strip().lower() == "y":
        uninstall.remove_mcp_registration(HOME, dry_run=False)


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


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--plugin-switch", action="store_true")
    args = parser.parse_args()

    if args.plugin_switch:
        offer_plugin_switch()
        offer_mcp_removal()
        return

    print("=" * 50)
    print("  ai-mem installer")
    print("=" * 50)

    install_package()

    workspace_root = prompt_workspace_root()
    run_records_migration(workspace_root)

    offer_plugin_switch()
    offer_mcp_removal()

    print("\n✅ Done! Restart Claude Code to start using ai-mem.")
    print(f"\n   Data will be stored at: {HOME / '.local' / 'share' / 'ai-mem'}")
    print("   Override with: AI_MEM_PATH=/your/path")
    print("\n   Quick start:")
    print("     claude plugin marketplace add " + str(REPO_ROOT) + " && claude plugin install ai-mem@ai-mem")
    print("                 — agents, /ai-mem:reflect, /ai-mem:setup, the mem command and the hooks")
    print("     /ai-mem:setup   — wire your teams and CLAUDE.md to ai-mem (proposes, applies on your approval)")
    print(f"\n   How the framework works: {REPO_ROOT / 'docs' / 'epistemology-framework.md'}")


if __name__ == "__main__":
    main()
