type: pattern
topic: general
perspective: the-coder
created: 1791758033.771845
cue: Writing a hook or module whose test must redirect a path that is derived from another module-level path
---

Rule: Do not compute a second module-level constant from a path constant (`X = DB_PATH / "..."`); compute the path inside the function that uses it, so the name is looked up at run time.
When: Writing hooks or modules whose tests redirect storage with `patch.object(module, "DB_PATH", tmp_path)`.
Why: The patch only affects code that looks the name up at call time; a constant derived at import time keeps the old value, so tests write to the real location. `_STATS_PATH` in userprompt_hook.py had this bug (fix fddfa9d). Complements [the-coder_python_patchability](the-coder_python_patchability.md) (import names at module level).
Evidence: docs/sources/pull_through_measurement_impl_2026_07_31.md (section "Gotcha beim Bauen"); commits b13d4d0, fddfa9d.

## Edges

- related: [the-coder_python_patchability](the-coder_python_patchability.md)
