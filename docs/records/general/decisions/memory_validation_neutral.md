id: memory_validation_neutral
type: pattern
area: general
perspective: agent
created: 1785497100.714465
---

Memory validation is neutral — neither code nor memory is authoritative. Code can be missing a fix that memory documents as done; memory can be stale if code changed afterward. Always cross-check: treat memory entries as a checklist against the actual code, not as ground truth, and treat the code as a candidate, not as the final word. Report discrepancies instead of silently resolving them in either direction.