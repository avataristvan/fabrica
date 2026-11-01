id: pattern_knowledge_distribution_rule_2026_10_04
type: pattern
topic: general
perspective: user
created: 1791067532.967105
edges: [{"target_id": "domain_archivist_write_threshold_2026_10_19", "edge_type": "related"}]
---

Rule: Distribute knowledge by relevance and derivability.
When: Deciding where to store information (CLAUDE.md, MEMORY.md, or ai-mem).
Why: CLAUDE.md costs tokens every session (keep short, only always-needed structural knowledge); ai-mem stores dynamic, context-sensitive knowledge; MEMORY.md is ultra-short pointers only. Only relevant sometimes → ai-mem. Derivable from code → neither. In code but always needed → CLAUDE.md.
Evidence: docs/sources/knowledge_architecture_framework.md (the MCP-era note stating this split); docs/sources/automation_memory_demotion.md (retired MEMORY.md auto-demotion, same concern: keep MEMORY.md short; loose fit)
