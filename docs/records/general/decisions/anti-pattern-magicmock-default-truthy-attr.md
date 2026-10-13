id: anti-pattern-magicmock-default-truthy-attr
type: anti-pattern
area: general
perspective: the-coder
created: 1785488483.958318
---

Tried: replacing a `ctx.collection not in (A, B)` guard with `ctx.has_claude_md` in code, while test fixtures build `ctx = MagicMock()` without ever setting `.has_claude_md`.
Failed because: MagicMock() auto-creates any accessed attribute as a truthy MagicMock, so `ctx.has_claude_md` silently evaluates True in every existing test regardless of the scenario being simulated — old tests kept passing but for the wrong reason, and would not have caught a regression in the new condition.
Instead: when a refactor changes which attribute of a mocked object gates behavior, explicitly set that attribute (e.g. `ctx.has_claude_md = True/False`) in at least one new test per branch, rather than trusting that existing MagicMock-based tests still exercise the intended path.