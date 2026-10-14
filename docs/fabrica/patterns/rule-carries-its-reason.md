# A rule carries its reason

**Status: convention**

## Problem

A rule without a reason is followed blindly or broken blindly. Nobody can tell when it stops applying.

## Forces

- Short rules are easier to read.
- Reasons cost time to write, and the writer already knows them.

## Solution

Every record has a fixed shape with the reason in it: Decision / Why / Scope, Rule / When / Why, Tried / Failed because / Instead, Observed / Cause / Evidence. "Cause: unknown" is allowed. A missing reason is not. A record that others derive from is never deleted, because it carries their reason.

## Status

Convention. The format asks for the reason; lint does not check it, and hand-written records drift from the shape.

## Evidence

- [Record format](../../reference/record-format.md): the shapes per kind of record.
- [`domain_clear_dead_weight_keep_reasons_2026_10_10`](../../records/architecture/decisions/domain_clear_dead_weight_keep_reasons_2026_10_10.md): dead weight goes, reasons stay.
- [`learning_handwritten_records_drift_from_format_2026_10_10`](../../records/architecture/learnings/learning_handwritten_records_drift_from_format_2026_10_10.md): hand-written records follow the shape loosely.

## Related practice

- **A3 report** (Toyota): problem, cause and countermeasure on one page.
- **5 Whys**: to the cause, not the symptom.
- "Where there is no standard, there can be no kaizen" (attributed to Taiichi Ohno): a standard with its reason is what can be improved.
