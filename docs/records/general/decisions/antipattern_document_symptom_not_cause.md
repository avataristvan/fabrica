id: antipattern_document_symptom_not_cause
type: anti-pattern
topic: general
perspective: agent
created: 1779056766.200665
---

Tried: documenting only the symptom of a hook/component failure (e.g. 'Stop hook was replaced') without capturing the underlying structural principle.
Failed because: the same failure recurs under a different hook name — the structural principle (every broadly-firing hook triggers for all agents including subagents, creating chain risk) was never recognised from the symptom alone.
Instead: when documenting a fix or workaround, also record WHY the previous approach broke at the structural level. The principle — not the instance — prevents future recurrence. (The original instance, antipattern_stop_hook_agent_spawn, is a record of the workspace root area.)
