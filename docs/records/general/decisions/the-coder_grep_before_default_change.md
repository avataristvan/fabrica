id: the-coder_grep_before_default_change
type: pattern
area: general
perspective: the-coder
created: 1781380208.682191
---

Rule: When changing a default value, grep all tests that implicitly assume the old default before writing a single line.
When: Any refactor that changes a constant, default parameter, or baseline value used across multiple files.
Why: Tests that don't explicitly set the value become silent regressions — they pass before the change and fail after for reasons unrelated to what's being tested. A fast grep prevents a confusing multi-test failure cascade.