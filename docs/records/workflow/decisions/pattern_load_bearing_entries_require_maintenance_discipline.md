id: pattern_load_bearing_entries_require_maintenance_discipline
type: pattern
topic: workflow
created: 1785517820.086595
cue: A change shifts thresholds or renames concepts that records describe.
---

Rule: When a change alters observable system behavior (thresholds, renamed concepts, API semantics), grep the literal old term/value across the ENTIRE collection, not just the top-N entries by access_count -- before closing the session.
When: Completing any bugfix or feature that changes something any entry describes (a threshold value, a gate name, a formula), especially a rename.
Why: Originally scoped to 'scan the top-5 by access_count' after hook_system/bm25_hybrid_impl both accumulated stale claims. Verified 2026-09-13 against the [always-present]→[available] rename (2026-07-31): ranking by access_count, the top 5 (automation_pipeline 429, developer_guide 336, collections_scoping 308, hook_system 305, antipattern_claude_dir_direct_edit 278) would have caught most of it, but mempalace_comparison (270, just below cutoff) and design_philosophy_junior_to_expert (170) and ai_mem_redesign_2026_06_13 (30, far below) all still carried the old term two months later -- the top-N heuristic under-caught by construction. Access count ranks retrieval frequency, not where stale terminology tends to hide -- comparison/philosophy/history docs are read less often precisely because they're not the daily-driver entries, which is exactly why old names linger there longest undetected. A full-collection grep is cheap (one command) compared to the cost of a stale fact surviving in ANY entry, frequently-accessed or not.