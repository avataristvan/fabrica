id: the-coder_return_type_naming
type: pattern
area: general
perspective: the-coder
created: 1780072547.52024
---

Rule: Functions that change their return type (e.g. class → tuple) need a name that signals the new type — otherwise a silent contract break for all callers.
When: When refactoring helper functions that have to return several values.
Why: _resolve_ranker_class() returning a tuple (class, bool) violates the principle of least surprise. Callers that expect only the class break silently. Better: _resolve_ranker_stack() or two separate functions with explicit names.
