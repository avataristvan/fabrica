id: ddd-usecase-preserved-field-needs-followup-upsert-on-fresh-insert
type: pattern
area: general
perspective: the-coder
created: 1790370317.478376
---

Rule: When a use-case (e.g. AddMemoryUseCase) deliberately preserves a field only from prior-existing storage state and never from caller-supplied input (protecting history like created_at across re-adds), an import/rebuild path that must restore that exact historical value on a FRESH insert (id not yet present) needs a two-step write: call the use case first (gets confidence/access_count lifecycle right), then re-fetch the just-written entry and issue a second, direct repository upsert to correct the one field the use case couldn't have known about.
When: Building a file<->DB sync/import CLI on top of an existing use-case layer that has its own field-preservation rules.
Why: Passing the value through the use case's normal argument won't work by construction — it's ignored for existing ids and would be silently stamped with 'now' for new ones, since the use case's whole point is to not trust caller input for that field.