# Organisational memory

Why ai-mem is built the way it is. This page explains; for exact formats see the [reference](../reference/), for tasks the [how-to guides](../how-to/).

## The problem

An agent starts every session cold. It does not know where it is, what was decided last week, or what was already tried and failed, and it has no cheap signal of the form "I know this". Two obvious answers both fail:

- **Push** everything that might be relevant into every prompt. It costs tokens on every message, fires regardless of the situation, and buries the one decision that matters under unrelated ones. ai-mem tried this (injected focus text, ranked search results per prompt and per edit) and measured it; the push hooks were retired. The measurements are kept as sources: [automation](../sources/automation.md), [pull-through measurement](../sources/pull_through_measurement_impl_2026_07_31.md).
- **Trust the agent to query** a memory when it needs to. A gap test showed that agents did not query unless something in their context named the memory (recorded as `eval_pull_gap_test_2026_09_20`; the earlier pull redesign is kept as the source [pull-based redesign sketch](../sources/arch_redesign_sketch_pull_based_2026_07_31.md)).

What worked is **pull at fixed points by a role with judgment**: a moment where a question is asked, and a reader who decides by understanding which records apply, not by a similarity score.

## An organisation's memory, not a person's

ai-mem remembers like an organisation does: through rituals at boundaries (decision reviews, handoffs, retrospectives), as domain-driven design's context maps and Team Topologies describe. The value lies in the practice, not the tool:

- **Record files in each area.** Decisions, learnings and user-held yardsticks are Markdown files, reviewable and greppable without any tooling and versioned with the work.
- **Fixed call points at context boundaries.** A session start, a chunk handoff and a review are where knowledge is read in and written out.
- **Judgment instead of scores.** A librarian agent reads the catalogue and the `cue:` of each record and decides what applies. Nothing is ranked by a number.

It is the reference implementation of [Fabrica](../fabrica/core.md), the practice that lets humans and agents learn from their own work. Fabrica's values are practices over tools, judgment over scores, knowledge at the right moment over knowledge at every moment, reasons over rules, mutual learning over silent automation, and superseding over forgetting. The first, longer account of the method is kept as the source [epistemology framework](../sources/epistemology_framework.md); it predates the file-based model.

## Roles

| Role | Does | Writes? |
|---|---|---|
| **Librarian** | Answers one to three questions by judgment over the record files. Read-only, runs on a small model, so any boundary can call it without risk. | no |
| **Archivist** | The default writer. Takes plain-text record candidates and integrates them: new, update, supersede, confirm or contradict; area by topic; `perspective:`, `cue:`, causal edges. Adopts hand-written records. Never edits evidence. | yes, via the `mem` CLI |
| **Orchestrator** | The main session. Runs `/reflect` at a boundary: writes the handoff, hands candidates to the archivist. | state only |
| **Everyone else** | Asks the librarian at a boundary; delivers `record_candidates` in the `[retro]` block. | no |

Librarian and archivist stay separate: permissions (reading is safe, writing should be rare), cost (reading is frequent and cheap, the harder supersede-or-confirm judgment is not) and timing (the librarian is asked before an action, the archivist after it). Both share one navigation reference so they judge alike.

Hand-written records stay allowed. Records must remain readable and writable without tooling; the archivist adopts them.

## Context boundaries: read in, write out

Every boundary has a read side and a write side. The read side is a question to the librarian carrying the situation: scope, terminology, mode, the files about to be touched. The write side is `/reflect`, which yields a handoff (state: charter, conclusions, open points, no history) and record candidates for the archivist. The contract for the read side is the skill `handoff-protocol`; see [wire skills and agents](../how-to/wire-skills-and-agents.md).

## Hooks enforce that, roles decide how

A ritual that nothing enforces erodes. So a few hooks check that the ritual happened (a `[retro]` block with `records_consulted` and `record_candidates`, a lint pass after a record is written, a `/reflect` reminder) without ever deciding what goes into a record. `mem doctor` is the other half: a read-only diagnosis of whether the practice is still alive, from the records, the wiring and the retro log. Details: [hooks](../reference/hooks.md), [command-line reference](../reference/cli.md).

## Three kinds of knowledge

They age differently and are never mixed. See [areas and kinds](areas-and-kinds.md).

## What was left behind

The first versions were a semantic store behind a tool server: vector search, hybrid ranking, confidence scores, automatic injection. Most of that was measured, found to push noise or to need maintenance nobody did, and replaced by files and judgment. The evidence stays, frozen, in [`docs/sources/`](../sources/) so that a conclusion can be checked and a retired idea is not rediscovered; an old installation upgrades via the tag `v1-last-upgrade-path`.
