id: todo_bibliothekar_haiku_retrieval_agent_2026_09_25
type: learning
area: general
created: 1790369035.889465
---

RESULT (closed 2026-09-26): 'The librarian' — originally a TODO/idea of 2026-09-25 for a lightweight, spawnable subagent (Haiku model) that independently 'rummages in memory' in the ADR file corpus (docs/decisions/, since 093dc1b docs/records/) and/or ai-mem — is implemented.

Why (original motivation, still valid): Directly addresses the actual open problem from eval_pull_gap_test_2026_09_20: the bottleneck is the retrieval trigger, not the storage format (agents almost never call mem_query proactively). A cheap, always-available librarian shifts the burden: instead of the orchestrator agent having to remember to call mem_query, asking becomes so cheap (Haiku) that it can happen much more generously. Precedent in our own code: mem_dream already uses a Haiku first pass → Sonnet synthesis (mode=hier) — the librarian is the same cost/quality pattern on the retrieval side instead of the consolidation side.

Implementation: Prototype da3f2ab (examples/agents/librarian.md, Haiku, read-only, tools mem_list/mem_get/mem_edges/mem_query + Read on docs/decisions/, as of then; today docs/records/). Measurement eval_librarian_2026_09_26 against scripts/eval_pull/: 5/6 gap cases solved (versus 2/6 with plain cosine/hybrid retrieval on the same cases), both controls correctly 'not documented', no fabrication. Fixed call points via 39a44e7: mandatory call in /chunk-plan, reference in the workspace CLAUDE.md ('Bibliothekar (Wissensabruf)' section), registered as subagent type librarian via symlink ~/.claude/agents/librarian.md. Embedded in the larger decision domain_drop_confidence_for_evidence_and_librarian_2026_09_26 (the librarian replaces confidence ranking as the trust mechanism).

Originally open design questions — answered: skill vs. registered subagent type → registered subagent type (librarian.md as agent definition, not as a skill). INDEX.md first? → yes, the instruction provides for an INDEX.md scan before reading individual files. Fire-and-forget vs. request-response → request-response (one question in, one answer out, no background run).

Still open: The librarian remains an approach on probation (domain_drop_confidence_for_evidence_and_librarian_2026_09_26) — it has to prove itself in use, measured by further gap-test runs. Follow-up: eval_librarian_2026_09_26 measured against general-purpose with the definition inserted verbatim, not against the registered subagent_type="librarian" (which did not yet exist at the time of measurement) — the gap-test arm should be repeated with the registered type to verify that the tools: restriction (only Read, mem_list, mem_get, mem_edges, mem_query) is actually enforced and not merely present as prompt text. Done 2026-09-29: re-test with the registered type, see eval_librarian_rerun_records_layout_2026_09_29 (caveat there: readable eval learnings, result possibly inflated).

Scope: repo.ai-mem. Related to todo_dream_trigger_candidates_not_count_2026_09_25 (both address the trigger aspect instead of the storage format).
