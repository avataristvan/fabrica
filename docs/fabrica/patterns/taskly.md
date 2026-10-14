# Taskly

**Status: convention**

## Problem

What a task taught us disappears when the task ends.

## Forces

- At the end of a task, everyone wants to move on.
- Forced reflection produces noise.
- "Nothing learned" has to be an allowed answer, or people invent lessons.

## Solution

Every task ends with three questions: what did we learn, what blocked us, what comes next. Agents answer in a `[retro]` block; the human adds what they saw. Whatever is worth keeping goes to the Archivist as a record candidate, in plain text. Nobody else writes the record.

## Status

Convention. The ritual is defined and practised. Hooks check that the `[retro]` block exists, not what it says. The measurement of how often the fields are filled is unreliable at the moment, so there is no evidence yet of whether the ritual holds or erodes.

## Evidence

- [`domain_reflect_yields_handoff_and_record_candidates_2026_10_10`](../../records/architecture/decisions/domain_reflect_yields_handoff_and_record_candidates_2026_10_10.md): candidates travel from `[retro]` through `/reflect` to the Archivist.
- [`pattern_retro_learned_nothing_is_valid_2026_10_11`](../../records/plugin/decisions/pattern_retro_learned_nothing_is_valid_2026_10_11.md): "learned: nothing" is a valid answer.
- [`domain_hooks_enforce_that_roles_decide_how_2026_10_10`](../../records/architecture/decisions/domain_hooks_enforce_that_roles_decide_how_2026_10_10.md): hooks enforce that the ritual happens, not its quality.
- [`learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12`](../../records/architecture/learnings/learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12.md): the erosion signal is not evidence until verified.

## Related practice

**Hansei** (Toyota): structured reflection after a piece of work, including what went wrong.
