id: the-coder_explicit_params
type: pattern
area: general
perspective: the-coder
created: 1780049216.508159
---

Thread new parameters explicitly through function signatures instead of a module-level side effect or closure.
When: when a threshold or config value has to go deeper into a call chain.
Why: explicit parameters are testable, mockable and change behaviour only locally — module-level side effects are hard to patch and affect all callers.
