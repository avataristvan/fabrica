# Both sides learn

**Status: convention**

## Problem

If only the agent learns, the human's context is missing. If only the human learns, the agent's observations are lost: silent fallbacks, wrong assumptions, tools that failed without saying so.

## Forces

- The human has the context; the agent has the details.
- Each side's knowledge is valid from its own point of view, and neither view is the whole.

## Solution

At a reflection, the agent speaks first ("my observation:"), then the human adds theirs. Every record says whose view it holds (`perspective:`). The record does not decide whose view is right; it keeps both, and a later record can confirm or contradict either.

## Status

Convention. The `perspective:` field exists and is used. So far the records mostly hold agent roles and user decisions; the two-sided exchange is practised but not yet visible in the data.

## Evidence

- [`domain_perspective_is_a_lens_not_a_location_2026_10_10`](../../records/architecture/decisions/domain_perspective_is_a_lens_not_a_location_2026_10_10.md): whose view a record holds is a lens, not a place.
- [`learning_organizational_not_personal_memory_2026_10_10`](../../records/architecture/learnings/learning_organizational_not_personal_memory_2026_10_10.md): the memory belongs to the workshop, not to one party.

## Related practice

**Respect for people** (Toyota), the second pillar next to continuous improvement: the people who do the work are the ones who improve it. Related, not equivalent: Toyota's pillar has no agents in it.
