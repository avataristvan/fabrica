# Seniority lives in the record

**Status: hypothesis**

## Problem

Agents start every session as juniors. Experience does not build up in them.

## Forces

- Seniority is usually tied to a person, and an agent has no person behind it between sessions.
- A record that only holds decisions explains the past to someone who already has judgment; it does not give judgment to someone who has none.

## Solution

Seniority is placed in what the agent inherits: the record, carried from session to session like the lodge book of a cathedral workshop from one generation of builders to the next. Because the agent brings no experience of its own, the record has to carry more than decisions: learnings, dead ends, and the situation in which a record applies. The better the record, the more senior the next session starts.

## Status

Hypothesis. A preregistered measurement (2026-10-16/17, 96 runs) gave the same tasks to agents without the record, with decisions only, and with the whole record. It did not reach probation: the whole record did not beat decisions alone, and agents that read the reason for a rejected design often built it anyway. The plan forbids a second version of this measurement; the result and its lessons are in [What we measured](../../explanation/what-we-measured.md#5-seniority-lives-in-the-record-not-confirmed).

## Evidence

- [`domain_fabrica_seniority_from_the_record_2026_10_14`](../../records/architecture/decisions/domain_fabrica_seniority_from_the_record_2026_10_14.md): the decision, marked unmeasured.
- [`eval_seniority_main_run_result_2026_10_18`](../../records/evaluation/learnings/eval_seniority_main_run_result_2026_10_18.md): the measurement, not confirmed; plan in [`plan_seniority_measurement.md`](../../plan_seniority_measurement.md).
- [`learning_knowledge_loses_against_the_order_2026_10_18`](../../records/evaluation/learnings/learning_knowledge_loses_against_the_order_2026_10_18.md): where the record was read, the agent often built the rejected thing anyway.
- [`domain_bmad_vs_ai_mem_epistemology_2026_09_25`](../../records/architecture/decisions/domain_bmad_vs_ai_mem_epistemology_2026_09_25.md): ADRs, graphify and BMAD deliver artifacts at a point in time; the contribution is judgment that matures instead of arising anew in every cycle.
- [`epistemology_framework.md`](../../sources/epistemology_framework.md), section "The Junior → Senior Effect": the first account of the claim.

## Related practice

**[Architecture Decision Records](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)** (Nygard; Fowler's bliki entry, 2026): one file per decision, kept in the repo, superseded and never reopened, so that people "months or years later" understand why the system is built the way it is. ADRs explain past decisions to readers who bring their own experience. An agent brings none, so the record must carry more.
