"""Path arithmetic and checks for relocating an area folder (`mem move-area`). Stdlib only.

Every area at or below `old` moves with it (nested areas included). A reference is rewritten when it resolves,
before the move, to an area that moves or is written in one; a reference in record text only when the record it
names exists, so prose like `./x:y` that names nothing is left alone. The machine-level state a move also breaks
(worktrees, editable installs, Claude Code config and auto-memory) is only reported, never touched.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from ai_mem.infrastructure.adr_paths import entry_files
from ai_mem.infrastructure.areas import Area, area_for_key, git, qualify, resolve_ref

# `./x:id`, `../x/y:id`, `..:id` -- a relative area path then an id; never preceded by a path or word character.
_TEXT_REF = re.compile(r"(?<![\w./-])(\.\.?(?:/[\w.-]+)*:[A-Za-z0-9][\w-]*)")
_CONFIG_NAMES = ("CLAUDE.md", "CLAUDE.local.md", ".mcp.json")
_CONFIG_IN_DOT_CLAUDE = ("settings.json", "settings.local.json")


@dataclass(frozen=True)
class AreaRelocation:
    old: Path
    new: Path

    def moves(self, path: Path) -> bool:
        return path == self.old or path.is_relative_to(self.old)

    def after(self, path: Path) -> Path:
        return self.new / path.relative_to(self.old) if self.moves(path) else path

    def _moved_area(self, area: Area) -> Area:
        root = self.after(area.root)
        return Area(root, root / area.records_dir.relative_to(area.root))

    def _resolve(self, from_key: str, ref: str) -> tuple[Area, Area, str] | None:
        from_area = area_for_key(from_key)
        if from_area is None or ":" not in ref:
            return None
        hit = resolve_ref(from_area, ref)
        return (from_area, *hit) if hit is not None else None

    def _relocate(self, resolved: tuple[Area, Area, str], ref: str) -> str | None:
        from_area, to_area, entry_id = resolved
        if not (self.moves(from_area.root) or self.moves(to_area.root)):
            return None
        new = qualify(self._moved_area(from_area), self._moved_area(to_area), entry_id)
        return new if new != ref else None

    def relocated_ref(self, from_key: str, ref: str) -> str | None:
        resolved = self._resolve(from_key, ref)
        return self._relocate(resolved, ref) if resolved is not None else None

    def relocated_text(self, from_key: str, text: str) -> tuple[str, list[tuple[str, str]]]:
        pairs: list[tuple[str, str]] = []

        def replace(match: re.Match) -> str:
            ref = match.group(1)
            resolved = self._resolve(from_key, ref)
            new = self._relocate(resolved, ref) if resolved is not None else None
            # Prose may look like a reference; only one that names an existing file is one.
            if new is None or not entry_files(resolved[1].records_dir, resolved[2]):
                return ref
            pairs.append((ref, new))
            return new

        return _TEXT_REF.sub(replace, text), pairs

    def preflight(self) -> str | None:
        """Why the folder cannot be renamed, or None."""
        if not self.old.is_dir() or self.old.is_symlink():
            return f"{self.old} is not a directory"
        if self.new.exists() or self.new.is_symlink():
            return f"{self.new} already exists"
        if self.moves(self.new):
            return f"{self.new} is inside {self.old}"
        if not self.new.parent.is_dir():
            return f"{self.new.parent} does not exist"
        if os.stat(self.old).st_dev != os.stat(self.new.parent).st_dev:
            return f"{self.new.parent} is on another filesystem; the rename would not be atomic"
        return None

    def rename(self) -> None:
        os.rename(self.old, self.new)


def is_versioned(area: Area) -> bool:
    return bool(git(area.root, "rev-parse", "--show-toplevel"))


def machine_state(old: Path, new: Path, root: Path, areas: list[Area]) -> list[str]:
    """What else still names `old` and is left to the user: one line each, nothing changed."""
    lines = []
    toplevels = {Path(top) for area in areas if (top := git(area.root, "rev-parse", "--show-toplevel"))}
    for toplevel in sorted(top for top in toplevels if top == old or top.is_relative_to(old)):
        listing = git(toplevel, "worktree", "list", "--porcelain")
        linked = [line[len("worktree "):] for line in listing.splitlines() if line.startswith("worktree ")][1:]
        if linked:
            lines.append(f"{len(linked)} linked worktree(s) of {toplevel}: after the move run "
                         f"`git -C {new / toplevel.relative_to(old)} worktree repair <their paths>` ({', '.join(linked)})")
    for entry in map(Path, sys.path):
        try:
            hooks = [p for p in entry.glob("__editable__*") if old.as_posix() in p.read_text(errors="replace")] if entry.is_dir() else []
        except OSError:
            hooks = []
        lines += [f"editable install still maps to {old}: {p} (reinstall with `pip install -e {new}`)" for p in hooks]
    memory = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", old.as_posix())
    if memory.is_dir():
        lines.append(f"Claude Code project memory for {old}: {memory} (move it to the new path's folder by hand)")
    candidates = [Path.home() / ".claude" / name for name in ("CLAUDE.md", *_CONFIG_IN_DOT_CLAUDE)]
    candidates.append(Path.home() / ".claude" / "plugins" / "known_marketplaces.json")
    for directory in {root, *(area.root for area in areas)}:
        candidates += [directory / name for name in _CONFIG_NAMES]
        candidates += [directory / ".claude" / name for name in _CONFIG_IN_DOT_CLAUDE]
    needles = [old.as_posix()]
    if old.is_relative_to(Path.home()):
        needles.append(f"~/{old.relative_to(Path.home()).as_posix()}")
    for path in sorted(set(candidates)):
        try:
            text = path.read_text(errors="replace") if path.is_file() else ""
        except OSError:
            continue
        if any(needle in text for needle in needles):
            lines.append(f"names the old path: {path}")
    return lines
