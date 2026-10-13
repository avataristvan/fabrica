id: the-coder_investigation_first
type: pattern
area: general
perspective: the-coder
created: 1780049216.508159
---

Investigation before implementation: if the analysis shows that the existing design is correct, 'no fix' is the right answer.
When: before any bug fix or feature implementation — first understand, then decide.
Why: a premature change can destroy working invariants (e.g. overwriting the is_never_accessed flag with the access_count prior). Verification first saves regressions.
