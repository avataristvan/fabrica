type: domain
topic: evaluation
perspective: user
created: 1791925100.251217
cue: Someone asks whether the archivist was ever accepted, or wants to rerun scripts/eval_archivist.
---

Decision: The archivist acceptance (scripts/eval_archivist/; pass rule >= 80% of 33 hand-set edges, 4/4 predecessors across areas, the duplicate flagged, all back-references) is closed as FAIL and not rerun. The archivist is accepted on real use instead. Last run (run 3, sonnet, reworked definition): 11/33 edges, 0/4 predecessors, duplicate not flagged, back-references 26/26, nothing written outside the scratch tree.
Why: The fixture no longer fits the records. Since the redistribution 12 of the 18 candidates live in fabrica, and build.py drops them only from the ai-mem copy, so a rerun would find them already present; the blueprint pass of 2026-10-13 also changed edges and deleted records, so the expected edges no longer match. Part of the 11/33 is the scoring itself: compare.py counts direction, and the archivist often linked sibling candidates the reverse way. Real use carries the acceptance: the blueprint pass over ~245 records, the translation of cues, the close-todo rule with repointing via mem delete's dangling report, all on 2026-10-13, lint clean each time.
Scope: scripts/eval_archivist/ (result.md, README.md as evidence). Open levers from the run: todo_archivist_report_names_searched_areas_2026_10_11, todo_archivist_flag_cross_area_duplicates_2026_10_13.

## Edges

- related: [domain_archivist_who_what_how_2026_10_10](../../architecture/decisions/domain_archivist_who_what_how_2026_10_10.md)
