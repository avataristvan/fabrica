---
type: retired-system
date: 2026-10-10
origin: fabrica area docs/reference/knowledge_architecture_framework.md (an MCP-era note on what goes into CLAUDE.md, MEMORY.md and ai-mem), moved into ai-mem on 2026-10-14
status: processed
---

## What the source says

# Knowledge Architecture: CLAUDE.md vs MEMORY.md vs ai-mem

**CLAUDE.md** — stable structural knowledge needed in EVERY session: dev commands, architecture overview, always-on behavioral conventions. Every byte costs tokens every session — keep short.

**MEMORY.md** — ultra-short index only (<20 entries). Pointers to local memory files or ai-mem entries. Never content directly.

**ai-mem** — dynamic, context-sensitive, evolving knowledge:
- current_focus (what's actively in progress)
- decisions with WHY context (not derivable from code)
- feedback/corrections to agent behavior
- project state that changes (bugs, deadlines, initiatives)
- reference pointers (model IDs, URLs, Linear projects)
- cross-repo implications of fixes

**Rule:** only relevant sometimes → ai-mem. Derivable from code → neither. In code but always needed → CLAUDE.md.

**Timing (added 2026-09-03):** domain/business decisions (the 'WHY context' bullet above — why a business rule exists, a domain constraint, a rationale not visible in the code itself) should be written the moment they surface during coding, not deferred to end-of-session /reflect. /reflect's Step 3 only asks the user for learnings at session end, which loses knowledge that came up mid-session and was never revisited. Use type='domain' (structure: Decision: / Why: / Scope:) for these entries specifically — distinct from type='feedback' (agent-behavior corrections, still captured at session end via /reflect) and type='pattern'/'anti-pattern' (coding technique, not business rationale). No hook enforces this; it relies on the agent noticing a domain decision and calling mem_add immediately, because judging whether something IS a domain decision requires semantic understanding a deterministic PostToolUse path-match can't provide.
