#!/usr/bin/env python3
"""ai-mem uninstaller — removes MCP server, hooks, permissions, commands and links (the plugin is removed with `claude plugin uninstall`).

Intentionally does NOT remove:
  ~/.local/share/ai-mem/   — ChromaDB memory data and ranker weights (user data)
  ~/.config/ai-mem/        — user config (agents.yaml, settings)

Run with --dry-run to preview what would be removed without changing anything.
"""
import argparse
import json
import os
import sys
from contextlib import suppress
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()
HOME = Path.home()
SERVER_MODULE = "ai_mem.server"
DB_PATH = Path(
    __import__("os").environ.get("AI_MEM_PATH", str(HOME / ".local" / "share" / "ai-mem"))
)


def stop_running_daemon(dry_run: bool) -> None:
    """Stop the background query daemon (ai_mem/daemon.py) and remove its socket/pid files."""
    print(f"\n  Background daemon ({DB_PATH})")
    if dry_run:
        print("    dry-run — skipping")
        return
    try:
        from ai_mem.daemon import stop_daemon
    except ImportError:
        print("    package not importable — nothing to stop")
        return
    if stop_daemon(DB_PATH):
        print("    stopped")
    else:
        print("    not running — nothing to remove")


def python_exe() -> str:
    return sys.executable


def _hook_commands() -> tuple[str, str, str]:
    py = python_exe()
    return (
        f"{py} -m ai_mem.userprompt_hook 2>/dev/null || true",
        f"{py} -m ai_mem.posttool_hook 2>/dev/null || true",
        # pretool_hook is no longer registered by install.py (2026-09-12, push→pull migration)
        # but is still removed here so pre-existing installations uninstall cleanly.
        f"{py} -m ai_mem.pretool_hook 2>/dev/null || true",
    )


# The plugin (hooks/hooks.json) now provides these; settings.json entries and links that older install.py
# versions made are matched by module marker (the interpreter path and env prefix in the command may differ).
PLUGIN_HOOK_EVENTS = ("SessionStart", "SubagentStop", "PostToolUse", "Stop")
PLUGIN_HOOK_MARKERS = ("-m ai_mem.hook ", "-m ai_mem.hooks.")

# Links older `install.py --sync-commands` made into ~/.claude (librarian: made by hand); only symlinks into this checkout are removed.
LINKED_PATHS = (
    Path(".claude") / "agents" / "librarian.md",
    Path(".claude") / "agents" / "archivist.md",
    Path(".claude") / "agents" / "anchor-lint.md",
    Path(".claude") / "ai-mem" / "navigating_records.md",
    Path(".claude") / "skills" / "handoff-protocol",
)

MCP_PERMISSIONS = [
    "mcp__ai-mem__mem_add",
    "mcp__ai-mem__mem_query",
    "mcp__ai-mem__mem_list",
    "mcp__ai-mem__mem_delete",
    "mcp__ai-mem__mem_dream",
    "mcp__ai-mem__mem_split",
    "mcp__ai-mem__mem_cleanup",
    "mcp__ai-mem__mem_train",
    "Bash(mem-dream *)",
]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_json(path: Path, data: dict, dry_run: bool) -> None:
    if dry_run:
        return
    path.write_text(json.dumps(data, indent=2) + "\n")


def _remove_hook_entries(hook_list: list, commands: set[str]) -> tuple[list, int]:
    """Remove hook entries whose command matches any of *commands*. Returns (filtered, removed_count)."""
    kept, removed = [], 0
    for entry in hook_list:
        entry_cmds = {h.get("command") for h in entry.get("hooks", [])}
        if entry_cmds & commands:
            removed += 1
        else:
            kept.append(entry)
    return kept, removed


def _points_into_checkout(link: Path) -> bool:
    """Whether the symlink's target, relative targets and `..` resolved, lies inside this checkout."""
    return Path(os.path.normpath(link.parent / link.readlink())).is_relative_to(REPO_ROOT)


# Commands older versions copied into ~/.claude/commands (/reflect is now /ai-mem:reflect, /mem-init /ai-mem:setup),
# each with the markers that tell the copy from a command the user wrote. Every shipped mem-init began with its marker line.
AI_MEM_COMMANDS = {
    "reflect.md": ("ai-mem", "archivist", "mem_add"),
    "mem-init.md": ("Initialize or update the ai-mem memory for the current project scope.",),
}


def _is_ai_mem_command(command_file: Path) -> bool:
    """Whether a command file is the one older versions copied here, not a command the user wrote."""
    try:
        text = command_file.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return False
    return any(marker in text for marker in AI_MEM_COMMANDS[command_file.name])


def _is_plugin_hook(hook: object) -> bool:
    command = hook.get("command") if isinstance(hook, dict) else None
    return isinstance(command, str) and any(marker in command for marker in PLUGIN_HOOK_MARKERS)


def _event_hooks(hooks: object, event: str) -> list:
    entries = hooks.get(event) if isinstance(hooks, dict) else None
    return entries if isinstance(entries, list) else []


def _remove_plugin_hooks(hook_list: list) -> tuple[list, int]:
    """Strip the hook objects the plugin now provides from every group, dropping groups left empty. Returns (filtered, removed_count)."""
    kept, removed = [], 0
    for entry in hook_list:
        hooks_here = entry.get("hooks", []) if isinstance(entry, dict) else None
        if not isinstance(hooks_here, list):
            kept.append(entry)
            continue
        remaining = [h for h in hooks_here if not _is_plugin_hook(h)]
        removed += len(hooks_here) - len(remaining)
        if remaining == hooks_here:
            kept.append(entry)
        elif remaining:
            kept.append({**entry, "hooks": remaining})
    return kept, removed


def _remove_links(home: Path, dry_run: bool) -> None:
    for relative in LINKED_PATHS:
        link = home / relative
        print(f"\n  Link {link}")
        if not link.is_symlink():
            print("    not a symlink — left unchanged" if link.exists() else "    not found — nothing to remove")
            continue
        if not _points_into_checkout(link):
            print("    points outside this checkout — left unchanged")
            continue
        if not dry_run:
            link.unlink()
            with suppress(OSError):  # only the ai-mem directory of the navigation reference, and only when empty
                if link.parent.name == "ai-mem":
                    link.parent.rmdir()
        print("    removed")


def plugin_leftovers(home: Path) -> list[str]:
    """What an older install.py left in `home` that the plugin now provides (hooks, /reflect and /mem-init commands, links into this checkout)."""
    found = []
    hooks = _load_json(home / ".claude" / "settings.json").get("hooks")
    for event in PLUGIN_HOOK_EVENTS:
        if _remove_plugin_hooks(_event_hooks(hooks, event))[1]:
            found.append(f"{event} hook in settings.json")
    for name in AI_MEM_COMMANDS:
        if _is_ai_mem_command(home / ".claude" / "commands" / name):
            found.append(f"command {name}")
    for relative in LINKED_PATHS:
        link = home / relative
        if link.is_symlink() and _points_into_checkout(link):
            found.append(f"link {link}")
    return found


def _strip_plugin_hooks(data: dict) -> bool:
    """Remove the plugin-provided hooks from loaded settings in place; returns whether anything changed."""
    hooks = data.get("hooks")
    changed = False
    for event in PLUGIN_HOOK_EVENTS:
        after, n = _remove_plugin_hooks(_event_hooks(hooks, event))
        if n:
            hooks[event] = after
            if not after:
                del hooks[event]
            print(f"    removed {n} {event} hook(s)")
            changed = True
    return changed


def _remove_commands(home: Path, dry_run: bool) -> None:
    for name in AI_MEM_COMMANDS:
        cmd_file = home / ".claude" / "commands" / name
        print(f"\n  Command {cmd_file}")
        if _is_ai_mem_command(cmd_file):
            if not dry_run:
                cmd_file.unlink()
            print("    removed")
        else:
            print("    not an ai-mem command — nothing to remove")


def remove_plugin_provided(home: Path, dry_run: bool) -> None:
    """Remove the hooks, /reflect and /mem-init commands and links the plugin replaces; MCP registration and permissions stay."""
    settings_path = home / ".claude" / "settings.json"
    print(f"\n  Claude Code settings ({settings_path})")
    data = _load_json(settings_path)
    if _strip_plugin_hooks(data):
        _save_json(settings_path, data, dry_run)
    else:
        print("    no ai-mem hooks to remove")
    _remove_commands(home, dry_run)
    _remove_links(home, dry_run)


# ── target: Claude Code ───────────────────────────────────────────────────────

def unregister_claude(dry_run: bool) -> None:
    hook_commands = set(_hook_commands())

    # MCP server — ~/.claude.json
    mcp_path = HOME / ".claude.json"
    print(f"\n  Claude Code MCP ({mcp_path})")
    data = _load_json(mcp_path)
    if "ai-mem" in data.get("mcpServers", {}):
        del data["mcpServers"]["ai-mem"]
        _save_json(mcp_path, data, dry_run)
        print("    removed mcpServers[\"ai-mem\"]")
    else:
        print("    not registered — nothing to remove")

    # Hooks + permissions — ~/.claude/settings.json
    settings_path = HOME / ".claude" / "settings.json"
    print(f"\n  Claude Code settings ({settings_path})")
    data = _load_json(settings_path)
    changed = False

    hooks = data.get("hooks", {})
    for event in ("UserPromptSubmit", "PostToolUse", "PreToolUse"):
        before = hooks.get(event, [])
        after, n = _remove_hook_entries(before, hook_commands)
        if n:
            hooks[event] = after
            print(f"    removed {n} {event} hook(s)")
            changed = True
    changed |= _strip_plugin_hooks(data)

    allow = data.get("permissions", {}).get("allow", [])
    removed_perms = [p for p in MCP_PERMISSIONS if p in allow]
    if removed_perms:
        data["permissions"]["allow"] = [p for p in allow if p not in MCP_PERMISSIONS]
        print(f"    removed {len(removed_perms)} permission(s)")
        changed = True

    if changed:
        _save_json(settings_path, data, dry_run)
    else:
        print("    nothing to remove")

    _remove_commands(HOME, dry_run)
    _remove_links(HOME, dry_run)


# ── target: Gemini CLI ────────────────────────────────────────────────────────

def unregister_gemini(dry_run: bool) -> None:
    config_path = HOME / ".gemini" / "settings.json"
    print(f"\n  Gemini CLI ({config_path})")
    data = _load_json(config_path)
    if "ai-mem" in data.get("mcpServers", {}):
        del data["mcpServers"]["ai-mem"]
        _save_json(config_path, data, dry_run)
        print("    removed mcpServers[\"ai-mem\"]")
    else:
        print("    not registered — nothing to remove")


# ── target: Cursor ────────────────────────────────────────────────────────────

def unregister_cursor(dry_run: bool) -> None:
    config_path = HOME / ".cursor" / "mcp.json"
    print(f"\n  Cursor ({config_path})")
    data = _load_json(config_path)
    if "ai-mem" in data.get("mcpServers", {}):
        del data["mcpServers"]["ai-mem"]
        _save_json(config_path, data, dry_run)
        print("    removed mcpServers[\"ai-mem\"]")
    else:
        print("    not registered — nothing to remove")


# ── UI ────────────────────────────────────────────────────────────────────────

TARGETS = {
    "1": ("Claude Code", unregister_claude),
    "2": ("Gemini CLI",  unregister_gemini),
    "3": ("Cursor",      unregister_cursor),
}


def prompt_targets() -> list:
    print("\nSelect AI tools to unregister:")
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
            print(f"  Unknown option '{ch}', skipping.")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Uninstall ai-mem integration artifacts.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview removals without writing any files")
    args = parser.parse_args()

    print("=" * 50)
    print("  ai-mem uninstaller")
    if args.dry_run:
        print("  DRY RUN — no files will be modified")
    print("=" * 50)
    print(
        "\n  Memory data is preserved:\n"
        f"    {HOME / '.local' / 'share' / 'ai-mem'}  (ChromaDB + ranker weights)\n"
        f"    {HOME / '.config' / 'ai-mem'}           (user config)\n"
        "  Delete these manually if you want a full wipe."
    )

    targets = prompt_targets()
    for label, fn in targets:
        print(f"\n── {label} ──")
        try:
            fn(args.dry_run)
        except Exception as e:
            print(f"  Error: {e}")

    stop_running_daemon(args.dry_run)

    pip_answer = input("\nRemove the ai-mem Python package? [y/N] ").strip().lower()
    if pip_answer == "y":
        import subprocess
        cmd = [sys.executable, "-m", "pip", "uninstall", "ai-mem", "-y"]
        print(f"  $ {' '.join(cmd)}")
        if not args.dry_run:
            subprocess.run(cmd, check=False)
    else:
        print("  Package kept.")

    print("\nDone. Restart your AI tool(s) to apply changes.")


if __name__ == "__main__":
    main()
