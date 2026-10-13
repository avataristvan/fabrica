id: pattern_knowledge_distribution_rule_2026_10_04
type: pattern
area: general
perspective: user
created: 1791067532.967105
---

Rule: Distribute knowledge by relevance and derivability.
When: Deciding where to store information (CLAUDE.md, MEMORY.md, or ai-mem).
Why: CLAUDE.md costs tokens every session (keep short, only always-needed structural knowledge); ai-mem stores dynamic, context-sensitive knowledge; MEMORY.md is ultra-short pointers only. Only relevant sometimes → ai-mem. Derivable from code → neither. In code but always needed → CLAUDE.md.