type: anti-pattern
topic: general
perspective: the-coder
created: 1785488483.958318
---

Tried: removing an unused import (e.g. WORKSPACE_COLLECTION) from a module after refactoring a conditional to no longer reference it.
Failed because: existing tests used unittest.mock.patch.object(module, "WORKSPACE_COLLECTION", ...) to stub that name — patch.object requires the target attribute to already exist on the object unless create=True is passed, so removing the import broke those tests with AttributeError even though the import was genuinely dead code in the source module.
Instead: when removing an import/name that's dead in the source, grep the test suite for patch.object(module, "<name>", ...) referencing it too, and remove those patch calls in the same change — 'still used elsewhere' must include test-side patch.object targets, not just references within the source file itself.

## Edges

- contradicts: [the-coder_python_patchability](the-coder_python_patchability.md)
