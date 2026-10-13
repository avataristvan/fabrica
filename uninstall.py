#!/usr/bin/env python3
"""ai-mem uninstaller — removes the old MCP registrations, hooks, permissions, commands and links (the plugin is removed with `claude plugin uninstall`).

Intentionally does NOT remove:
  ~/.local/share/ai-mem/   — the old ChromaDB store and runtime state (user data)
  ~/.config/ai-mem/        — user config (the old agents.yaml, now unused)

Run with --dry-run to preview what would be removed without changing anything.
"""
import argparse
import json
import os
import shutil
import sys
from contextlib import suppress
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()
HOME = Path.home()
DB_PATH = Path(
    __import__("os").environ.get("AI_MEM_PATH", str(HOME / ".local" / "share" / "ai-mem"))
)


def python_exe() -> str:
    return sys.executable


# Push hooks retired in 2026-09/10 (and the SessionStart/MCP-era commands), matched by module marker.
RETIRED_HOOK_MARKERS = ("-m ai_mem.userprompt_hook", "-m ai_mem.posttool_hook", "-m ai_mem.pretool_hook")
RETIRED_HOOK_EVENTS = ("UserPromptSubmit", "PostToolUse", "PreToolUse")

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

MCP_PERMISSION_PREFIX = "mcp__ai-mem__"
OTHER_PERMISSIONS = ["Bash(mem-dream *)"]  # removed only by a full uninstall, not by the MCP removal
MCP_CONFIGS = (
    ("Claude Code", Path(".claude.json")),
    ("Gemini CLI", Path(".gemini") / "settings.json"),
    ("Cursor", Path(".cursor") / "mcp.json"),
)


def _load_json(path: Path) -> dict:
    """The JSON object in `path`; {} when the file is missing, unreadable or not an object (see `_unreadable`)."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _unreadable(path: Path) -> bool:
    """A file that exists but is not a JSON object: reported and left unchanged, never rewritten."""
    if not path.exists():
        return False
    try:
        return not isinstance(json.loads(path.read_text()), dict)
    except Exception:
        return True


_backed_up: set[Path] = set()


def _save_json(path: Path, data: dict, dry_run: bool) -> None:
    """Atomic rewrite (temp file + replace); the content before this run is kept next to it as `<name>.ai-mem.bak`.

    A run may save the same file twice (uninstall: MCP removal, then plugin hooks); only the first save
    backs up, so the backup holds the original. `~/.claude.json` holds credentials: the temp file is created
    owner-only and gets the original's mode (copy2 does the same for the backup), so permissions never widen.
    """
    if dry_run:
        return
    mode = 0o600
    if path.exists():
        mode = path.stat().st_mode & 0o777
        if path not in _backed_up:
            shutil.copy2(path, path.with_name(path.name + ".ai-mem.bak"))
            _backed_up.add(path)
    tmp = path.with_name(path.name + ".ai-mem.tmp")
    with suppress(FileNotFoundError):
        tmp.unlink()
    with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as f:
        f.write(json.dumps(data, indent=2) + "\n")
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def _allow_list(data: dict) -> list:
    permissions = data.get("permissions")
    allow = permissions.get("allow") if isinstance(permissions, dict) else None
    return allow if isinstance(allow, list) else []


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


def _hook_has_marker(hook: object, markers: tuple[str, ...]) -> bool:
    command = hook.get("command") if isinstance(hook, dict) else None
    return isinstance(command, str) and any(marker in command for marker in markers)


def _is_plugin_hook(hook: object) -> bool:
    return _hook_has_marker(hook, PLUGIN_HOOK_MARKERS)


def _event_hooks(hooks: object, event: str) -> list:
    entries = hooks.get(event) if isinstance(hooks, dict) else None
    return entries if isinstance(entries, list) else []


def _filter_hooks(hook_list: list, is_target) -> tuple[list, int]:
    """Strip the matching hook objects from every group, dropping groups left empty. Returns (filtered, removed_count)."""
    kept, removed = [], 0
    for entry in hook_list:
        hooks_here = entry.get("hooks", []) if isinstance(entry, dict) else None
        if not isinstance(hooks_here, list):
            kept.append(entry)
            continue
        remaining = [h for h in hooks_here if not is_target(h)]
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
        if _filter_hooks(_event_hooks(hooks, event), _is_plugin_hook)[1]:
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
    n = _strip_hooks(data, PLUGIN_HOOK_EVENTS, _is_plugin_hook)
    if n:
        print(f"    removed {n} ai-mem hook(s)")
    return bool(n)


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


# ── the old MCP registration, retired push hooks and permissions ────────────────

def _is_mcp_permission(perm: object) -> bool:
    return isinstance(perm, str) and perm.startswith(MCP_PERMISSION_PREFIX)


def _is_retired_hook(hook: object) -> bool:
    return _hook_has_marker(hook, RETIRED_HOOK_MARKERS)


def _mcp_servers(data: dict) -> dict:
    servers = data.get("mcpServers")
    return servers if isinstance(servers, dict) else {}


def _strip_hooks(data: dict, events: tuple[str, ...], is_target) -> int:
    """Remove the matching hooks from loaded settings in place; returns how many were removed."""
    hooks = data.get("hooks")
    total = 0
    for event in events:
        kept, removed = _filter_hooks(_event_hooks(hooks, event), is_target)
        if removed:
            hooks[event] = kept
            if not kept:
                del hooks[event]
            total += removed
    return total


def mcp_leftovers(home: Path) -> list[str]:
    """Where the removed MCP server is still registered in `home`: mcpServers entries, mcp__ai-mem__* permissions, retired push hooks."""
    found = [f"mcpServers[\"ai-mem\"] in {home / rel}" for _, rel in MCP_CONFIGS if "ai-mem" in _mcp_servers(_load_json(home / rel))]
    settings = _load_json(home / ".claude" / "settings.json")
    if any(_is_mcp_permission(p) for p in _allow_list(settings)):
        found.append("mcp__ai-mem__* permissions in settings.json")
    if any(_filter_hooks(_event_hooks(settings.get("hooks"), e), _is_retired_hook)[1] for e in RETIRED_HOOK_EVENTS):
        found.append("retired push hooks (userprompt/pretool/posttool) in settings.json")
    return found


def remove_mcp_registration(home: Path, dry_run: bool) -> None:
    """Remove the MCP registrations, `mcp__ai-mem__*` permissions and retired push hooks; the plugin's hooks and other permissions stay."""
    for label, rel in MCP_CONFIGS:
        path = home / rel
        print(f"\n  {label} MCP ({path})")
        if _unreadable(path):
            print("    not a readable JSON object — left unchanged")
            continue
        data = _load_json(path)
        if "ai-mem" in _mcp_servers(data):
            del data["mcpServers"]["ai-mem"]
            _save_json(path, data, dry_run)
            print("    removed mcpServers[\"ai-mem\"]")
        else:
            print("    not registered — nothing to remove")

    settings_path = home / ".claude" / "settings.json"
    print(f"\n  Claude Code settings ({settings_path})")
    if _unreadable(settings_path):
        print("    not a readable JSON object — left unchanged")
        return
    data = _load_json(settings_path)
    changed = False
    n = _strip_hooks(data, RETIRED_HOOK_EVENTS, _is_retired_hook)
    if n:
        print(f"    removed {n} retired push hook(s)")
        changed = True
    allow = _allow_list(data)
    mcp_perms = [p for p in allow if _is_mcp_permission(p)]
    if mcp_perms:
        data["permissions"]["allow"] = [p for p in allow if not _is_mcp_permission(p)]
        print(f"    removed {len(mcp_perms)} mcp__ai-mem__* permission(s)")
        changed = True
    if changed:
        _save_json(settings_path, data, dry_run)
    else:
        print("    nothing to remove")


def unregister_claude(home: Path, dry_run: bool) -> None:
    remove_mcp_registration(home, dry_run)
    settings_path = home / ".claude" / "settings.json"
    data = _load_json(settings_path)
    changed = _strip_plugin_hooks(data)
    allow = _allow_list(data)
    if any(p in OTHER_PERMISSIONS for p in allow):
        data["permissions"]["allow"] = [p for p in allow if p not in OTHER_PERMISSIONS]
        print("    removed Bash(mem-dream *) permission")
        changed = True
    if changed:
        _save_json(settings_path, data, dry_run)
    _remove_commands(home, dry_run)
    _remove_links(home, dry_run)


# ── UI ────────────────────────────────────────────────────────────────────────

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
        f"    {HOME / '.local' / 'share' / 'ai-mem'}  (the old ChromaDB store + runtime state)\n"
        f"    {HOME / '.config' / 'ai-mem'}           (user config)\n"
        "  Delete these manually if you want a full wipe."
    )

    try:
        unregister_claude(HOME, args.dry_run)
    except Exception as e:
        print(f"  Error: {e}")

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
