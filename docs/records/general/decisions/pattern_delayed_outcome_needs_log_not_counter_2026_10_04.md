type: pattern
topic: general
perspective: agent
created: 1791067532.967105
cue: Designing a live counter for whether a pushed item was later used
---

Rule: A live rolling counter cannot measure a result whose outcome is still unknown at the time of the triggering action (e.g. 'was this pushed item later pulled?', 'did this request end up succeeding?'). A counter can only record hits that are already settled at the time of the increment -- it cannot represent the non-occurrence of a later event, because it is evaluated too early. Use logged events plus a later report instead.
When: When designing a metric for delayed/asynchronous outcomes -- 'was X later Y', not 'is X currently Y'; measuring deferred effects in systems with passive tracking.
Why: Prevents a metric that can structurally only show 100% or close to 100%, because the non-occurrence of the later event is never counted. Keep an event log of the triggering action (with timestamp), and reconcile the balance later via a report against the actual later state (e.g. against a timestamp such as last_accessed_at).
Evidence: docs/sources/pull_through_measurement_impl_2026_07_31.md (the measurement log joined to later access; its infrastructure died with userprompt_hook, 281 push events, frozen 2026-09-13).
