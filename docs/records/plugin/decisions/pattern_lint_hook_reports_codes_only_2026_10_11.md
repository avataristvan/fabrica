id: pattern_lint_hook_reports_codes_only_2026_10_11
type: pattern
area: plugin
perspective: the-coder
created: 1791738296.180107
edges: [{"target_id": "../fabrica:domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "related"}, {"target_id": "..:pattern_hooks_must_not_raise", "edge_type": "related"}]
cue: I am letting a hook surface findings about record files to the model, or checking that a path stays inside docs/records
---

Rule: A hook's block reason about record lint carries finding codes only, never the lint message. Containment checks on docs/records use is_contained(..., allow_symlink=False).
When: A hook reports findings about record files to the model (lint_after_write).
Why: records_lint messages embed raw record values; passing them on would inject record content, which the hooks must never do. A containment check that resolves both sides lets a symlinked docs/records pass.
Evidence: ai_mem/hooks/lint_after_write.py; found by the-coder and reviewer.
