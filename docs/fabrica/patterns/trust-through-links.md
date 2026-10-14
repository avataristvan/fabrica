# Trust through links, not scores

**Status: convention**

## Problem

A confidence score claims a precision nobody has, and it hides why a record is trusted.

## Forces

- Readers want a quick verdict.
- A verdict without a reason cannot be checked, and a number cannot be argued with.

## Solution

Trust comes from links between records: a later record `confirms`, `contradicts` or `supersedes` an earlier one, or is `derived_from` it. A record that is overtaken stays readable and is marked as superseded, because the reason it was wrong is knowledge too. The links change with the work: a record matures when it is confirmed and fades when it is contradicted.

## Status

Convention. The links are implemented and in use, and the confidence score was removed. Whether the links actually make the record more trustworthy is not measured.

## Evidence

- [`domain_drop_confidence_for_evidence_and_librarian_2026_09_26`](../../records/architecture/decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md): confidence and access counts dropped; links take over.
- [`domain_direction_judgment_over_scores_2026_09_20`](../../records/architecture/decisions/domain_direction_judgment_over_scores_2026_09_20.md): judgment over scores, the direction.
- [`domain_superseded_flag_not_hide_2026_09_20`](../../records/architecture/decisions/domain_superseded_flag_not_hide_2026_09_20.md): superseded records are flagged, not hidden.
- [`domain_bmad_vs_ai_mem_epistemology_2026_09_25`](../../records/architecture/decisions/domain_bmad_vs_ai_mem_epistemology_2026_09_25.md): graphify, ADRs and BMAD deliver artifacts at a point in time; none has a lifecycle.

## Related practice

- **[graphify](https://github.com/Graphify-Labs/graphify)**: knowledge as a graph in files, every edge marked with its origin (`EXTRACTED`, `INFERRED`, `AMBIGUOUS`). Fabrica takes the links with their origin and leaves out the numeric score graphify puts on each edge. A graphify graph is a snapshot; Fabrica's links change as the work goes on.
- **Genchi genbutsu** (Toyota): go and see the source instead of trusting the summary. Related, not equivalent.
