---
type: retired-system
date: 2026-10-04
origin: memory entry automation_memory_demotion, exported to docs/reference/ on 2026-10-04 (content older)
status: unprocessed
---

## What the source says

ai-mem: MEMORY.md Auto-Demotion (memory_index.py) — built but currently undeployed; no trigger wired.
- Threshold: 180 lines → demote until 160 lines
- Sort: project (0) → reference (1) → user (2) → feedback (3); within type: oldest mtime first
- Routing: type=project → project_collection; all others → global
- Dangling entries (file missing): removed from index without add to ai-mem
- On add failure: entry stays in index (no data loss)
- find_memory_dir(): resolves ~/.claude/projects/<encoded-cwd>/memory/

## Our notes

