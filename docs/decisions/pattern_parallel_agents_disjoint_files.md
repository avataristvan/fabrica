id: pattern_parallel_agents_disjoint_files
type: pattern
created: 1790440075.46643
edges: [{"target_id": "feedback_test_daemon_flaky", "edge_type": "related"}]
---

Rule: Parallele Coding-Subagenten im selben Worktree bekommen fest getrennte Dateimengen (explizite Verbotsliste der Dateien des anderen) und jeweils eigene Test-Aufrufe (--ignore auf die Tests des anderen); der Orchestrator fährt die volle Suite erst, wenn beide fertig sind.
When: Eine größere Änderung lässt sich entlang von Dateigrenzen in zwei unabhängige Teile schneiden.
Why: Ohne Trennung sehen beide Agenten die halbfertigen Edits des anderen als rote Tests und reparieren fremde Baustellen. 2026-09-26 (confidence-Streichung, Hook/Dream vs. Boost/Tracking/Server) lief so ohne einen Konflikt.