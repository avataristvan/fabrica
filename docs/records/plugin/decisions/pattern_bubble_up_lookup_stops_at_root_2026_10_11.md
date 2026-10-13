id: pattern_bubble_up_lookup_stops_at_root_2026_10_11
type: pattern
area: plugin
perspective: the-coder
created: 1791745726.71139
edges: [{"target_id": "../fabrica:domain_area_path_is_the_address_of_knowledge_2026_10_10", "edge_type": "related"}]
cue: I am writing a lookup that walks up the ancestor folders (area lookup, config search)
---

Rule: A bubble-up (ancestor-walk) search names its stop explicitly (the root) and is split into one function per stage, e.g. areas.ancestor_areas for the walk and areas.search_order for the order of stages.
When: Writing any lookup that walks from a path up through its ancestors.
Why: An implicit end of the walk lets the search leak above the intended root or stop short; one function per stage keeps each stage testable and the stop visible. The area lookup now ends at the workspace root (domain_area_path_is_the_address_of_knowledge_2026_10_10).
Evidence: ai_mem/infrastructure/areas.py.
