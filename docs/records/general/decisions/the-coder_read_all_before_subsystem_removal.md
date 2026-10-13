id: the-coder_read_all_before_subsystem_removal
type: pattern
area: general
perspective: the-coder
created: 1781380215.494617
edges: [{"target_id": "../ai-architecture:pattern_subsystem_removal_doc_hygiene", "edge_type": "related"}]
---

Rule: When removing a subsystem, read ALL affected files before writing a single line.
When: Deleting a module, protocol, or infrastructure layer that is imported across many files.
Why: Writing incrementally (delete source, then fix callers one by one) creates failing intermediate states and requires re-reading context multiple times. A single read pass reveals the full call graph; a single write pass completes the removal cleanly with one test run at the end.