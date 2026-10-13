id: pattern_reflect_between_chunks
type: pattern
area: general
perspective: user
created: 1782731914.074017
edges: [{"target_id": "todo_detect_skipped_reflect_gate_2026_10_11", "edge_type": "related"}]
---

Rule: Between chunks in a multi-chunk implementation session, always run /reflect before spawning the next coder.
When: Any task decomposed into chunks using chunk-plan or similar workflow, regardless of project or language.
Why: Each chunk completion is a natural gate — the coder's [retro] surfaces path corrections, API surprises, and scope drift before they propagate into the next chunk. Validated in another project's D-Bus chunks 1-3: caught path error (bin/model/ vs bin/), save-bug (discarded return value), and missing projectfolder.h header.
How to apply: After every the-coder completion: read [retro] → run /reflect → spawn next chunk.
