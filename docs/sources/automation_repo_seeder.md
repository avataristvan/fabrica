---
type: retired-system
date: 2026-10-04
origin: memory entry automation_repo_seeder, exported to docs/reference/ on 2026-10-04 (content older)
status: unprocessed
---

## What the source says

ai-mem: Repo Seeder (repo_seeder.py) -- RETIRED, module removed from the codebase (commit 1efe78a, "replace file-based seeder with agent-driven mem-init exploration"). Project seeding is /mem-init's agent-driven exploration now, not an automatic threshold-gated hook.

Historical record of how it worked while it existed:
- Gate: global injection_rate >= SEED_THRESHOLD (0.60)
- Reads CLAUDE.md from claude_md_dir, splits on '\n## ' (H2 only, H1 excluded)
- Entry IDs: seed_<slug> (lowercase, underscores, alphanumeric only)
- Metadata: {seeded_from: 'CLAUDE.md', seed_ts: <unix float>}
- Called from _try_seed when collection count == 0; always silent (try/except)

## Our notes

