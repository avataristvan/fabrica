type: pattern
topic: general
perspective: the-coder
created: 1779142854.871379
---

Rule: In Python, import module-level names at the top of the file — never inside a function — when you need `unittest.mock.patch.object(module, ...)` to work in tests.
When: Writing Claude Code hooks, callbacks, or any module where tests need to patch collaborators via `patch.object(hook_module, 'collab')`.
Why: `from x import y` inside a function creates a local binding at call time. `patch.object(module, 'y')` patches the module attribute, which never gets set if the import was lazy. Module-level imports bind the name at import time, making it patchable.

## Edges

- related: [pattern_runtime_lookup_for_patchable_path_constants_2026_10_12](pattern_runtime_lookup_for_patchable_path_constants_2026_10_12.md)
