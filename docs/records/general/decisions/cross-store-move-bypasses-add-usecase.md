id: cross-store-move-bypasses-add-usecase
type: anti-pattern
area: general
perspective: the-coder
created: 1783086058.384481
---

Tried: implement a cross-store 'move' operation (moving an entity between collections/tables/buckets) by reusing the existing add/upsert use case that already has metadata-preserving merge logic for updates.
Failed because: that merge logic queries the SAME destination store for prior metadata to decide what to preserve — for a same-collection update this is correct, but for a cross-collection move the 'prior metadata' lookup silently misses (entry doesn't exist there yet) or looks in the wrong place, and would reset fields like confidence/access_count instead of carrying them over.
Instead: implement move as its own use case using the repository's raw primitives directly — read from source (get_by_ids), write to target (upsert) with the entry object used verbatim/unmodified, then delete confirmed writes from source. Never route a cross-store move through an add/update use case whose merge semantics assume same-store context.