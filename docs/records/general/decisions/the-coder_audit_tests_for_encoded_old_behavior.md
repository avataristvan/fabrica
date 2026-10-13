id: the-coder_audit_tests_for_encoded_old_behavior
type: pattern
area: general
perspective: the-coder
created: 1785505717.204282
---

Rule: When fixing a scoring/behavior bug, explicitly audit existing tests for ones that silently assert the OLD (buggy) behavior as an invariant -- they won't fail until the bug is fixed, so 'no test broke' is not sufficient confirmation of a safe fix.
When: Any bugfix to a scoring, ranking, or threshold-based mechanism with pre-existing test coverage.
Why: A test asserting a tight bound or specific range that only made sense under the old (buggy) formula will pass silently right up until the fix lands, then break -- or worse, stay green if the new behavior happens to still satisfy a loose assertion, masking that the fix changed semantics the test was supposed to guard.