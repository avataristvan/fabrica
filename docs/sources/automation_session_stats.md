---
type: retired-system
date: 2026-10-04
origin: memory entry automation_session_stats, exported to docs/reference/ on 2026-10-04 (content older)
status: processed
---

## What the source says

ai-mem: Session Injection Stats (session_stats.py)
- record_injection(stats_path, scope, injected: bool): appends + trims to 20 entries
- injection_rate(stats_path, scope) → float: injected/total (0.0 if no data)
- Storage: {DB_PATH}/session_stats.json — {scope: [{ts: float, injected: bool}]}
- Recorded by: hook.py (global scope, SessionStart) — the only live call site. userprompt_hook.py also calls record_injection, but that module was unregistered from install.py on 2026-09-13 (see arch_decision_userprompt_push_removed_2026_09_13) — its call site is dead code.

## Our notes

