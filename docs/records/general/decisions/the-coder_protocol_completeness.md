id: the-coder_protocol_completeness
type: pattern
area: general
perspective: the-coder
created: 1780072547.52024
---

Rule: Protocol definitions must cover all methods that callers actually call — not just the methods of the nearest direct caller.
When: When extending a Protocol class or when adding methods to concrete implementations.
Why: If RankerRegistry.get() calls labeled_count() but TrainingBufferRepository.labeled_count() is not in the Protocol, Pyright reports no error at compile time — but mock-based tests fail and linting shows no warning. Protocol completeness is an invariant that must be enforced actively.
