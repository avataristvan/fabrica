id: pattern_doctor_exit_criterion_check_scanner_covers_destination_2026_10_12
type: pattern
area: architecture
perspective: the-coder
created: 1791786664.760172
edges: [{"target_id": "domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12", "edge_type": "related"}]
cue: Moving or restructuring docs while relying on a doctor zero-hits check as the exit criterion
---

Rule: After moving docs or changing the doc layout, verify that the scanner behind a "zero hits" exit criterion still covers the destination folders; add them if not.
When: Chunks that move docs or change the doc layout and use a `mem doctor` check as proof of done.
Why: A "zero hits" result passes trivially when the scanner does not look where the docs now live. The docs-rewrite chunk added _DOC_FOLDERS (docs/tutorial, how-to, reference, explanation) to ai_mem/doctor_sources.py so the retired-system check reads the new layout.
Evidence: ai_mem/doctor_sources.py, tests/test_doctor.py.
