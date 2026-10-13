id: mock-discriminate-multi-call-site-by-argument
type: pattern
area: general
perspective: the-coder
created: 1785488466.943331
---

When a test helper mocks a function with a flat return_value for ALL call sites, but production code calls that function multiple times with different arguments (e.g. one gated call plus one unconditional call to the same function with a different collection/key argument), a presence/absence assertion on the output can pass 'by accident' via the unconditional call even when the specific gated call site is broken or untested. Fix: give the mock a side_effect keyed by the differentiating argument (e.g. a dict {collection: entries}) so only the call under test can produce the observed output — the unrelated call site returns empty and can't mask the result. Applies broadly to any test asserting on merged/aggregated output of multiple calls to the same mocked dependency.