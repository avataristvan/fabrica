type: learning
topic: general
created: 1790367431.847629
---

RESULT (worked off 2026-09-26): mem_dream maintenance batch of 2026-09-25 on repo.ai-mem -- drift fixes on about 10 entries (MCP tool count, stop_hook hash, hook_system, boost_count gate, among others), [arch_decision_sessionstart_pull_based_2026_09_16](../../architecture/decisions/arch_decision_sessionstart_pull_based_2026_09_16.md) newly created, two principle patterns with cue. Commits: 82f8f68 (docs/decisions + CLAUDE.md), f7d802c (README.md in the ADR directory was treated as a broken ADR).
The decision made at the time, 'SPLIT deliberately not executed' (mem_split deleted the original ID and reset metadata), is overtaken: since b7559c8 mem_split creates learning+decision with derived_from and was used in 093dc1b for 10 splits.
Observation: the maintenance agents' mem_get counted back then as deliberate use (access_count); since b5e5d38 access_count is no longer written.
