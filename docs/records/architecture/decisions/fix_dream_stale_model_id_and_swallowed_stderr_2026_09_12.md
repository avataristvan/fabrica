type: domain
topic: architecture
created: 1789245885.249158
cue: mem_dream aborts with "exit status 1" or a model alias/tag no longer resolves.
---

Decision (fixed 2026-09-12): (1) `MODELS` in dream_memory.py switched to unversioned aliases: `{"haiku": "haiku", "sonnet": "sonnet"}` (both aliases verified live against the real CLI, exit 0) -- eliminates the bit-rot risk permanently, no date to maintain any more. (2) `_call()`: `check=True` removed, instead manually `if result.returncode != 0: raise RuntimeError(f"claude CLI failed (model=..., exit=...): {stderr or stdout or '(no output)'}")` -- a failure now shows the real cause instead of just the exit code.
Why: For causes and observation see [learning_dream_failure_hid_cause_stale_model_tag_2026_09_12](../learnings/learning_dream_failure_hid_cause_stale_model_tag_2026_09_12.md) (outdated versioned model tag as a bit-rot risk; swallowed stderr as a diagnostic blocker).
Tests: none depended on the old MODELS values or on check=True.
See also: [arch_decision_pretool_push_removed_2026_09_12](arch_decision_pretool_push_removed_2026_09_12.md) (same session, different topic).

## Edges

- derived_from: [learning_dream_failure_hid_cause_stale_model_tag_2026_09_12](../learnings/learning_dream_failure_hid_cause_stale_model_tag_2026_09_12.md)
