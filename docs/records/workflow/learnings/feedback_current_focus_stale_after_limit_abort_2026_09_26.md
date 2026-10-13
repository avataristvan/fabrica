id: feedback_current_focus_stale_after_limit_abort_2026_09_26
type: learning
area: workflow
created: 1790440075.46643
edges: [{"target_id": "../fabrica:pattern_status_markers_rot_in_memory", "edge_type": "confirms"}]
cue: A session starts with "continue" and current_focus reports uncommitted or still-running work.
---

Observed: The session started with 'continue'; current_focus reported 'uncommitted'/'measurement may still be running', although it had long been committed.
Cause: current_focus was written at the abort caused by the usage limit and not updated.
Evidence: git log showed da3f2ab, f5d9757.

Observation 2026-09-26: The session started with 'continue' without further context. current_focus still reported 'uncommitted' and 'measurement may still be running' (written at the abort caused by the usage limit), although both had long been committed (da3f2ab, f5d9757). Only git log gave the real state. Lesson: after an abort state in current_focus, first check git log/status against the status statements before following them.
