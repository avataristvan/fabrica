id: domain_fabrica_name_collision_checked_2026_10_15
type: domain
area: architecture
perspective: user
created: 1792061046.611662
edges: [{"target_id": "domain_framework_named_fabrica_2026_10_10", "edge_type": "related"}]
cue: You are asked whether the name Fabrica collides with something, or want to publish a pip package named fabrica.
---

Decision: The name Fabrica stands after a collision check (2026-10-15); no blocking collision in the same field. The user accepted that trademark registries (EUIPO, DPMA, USPTO) were not checked.
Why: PyPI `fabrica` is taken (a small agent runtime by ondrej-winter, 0 stars, since 2026-08), so a pip package of that name is not available. The near-name Fabric (danielmiessler, prompt-pattern framework, about 41k stars) is the main confusion risk in AI search. Benetton's Fabrica (creative research centre, Treviso, since 1994) is in a different field. In Portuguese and Spanish "fabrica (de software)" means software factory, the opposite of the intended fabrica ecclesiae image, so the README says so in one line. npm `fabrica` is a 2022 placeholder.
Scope: Fabrica docs, README, any package or registry naming. Closes the last point of todo_split_manifest_and_name_framework. Evidence: commit a365d9b (README), web search 2026-10-15.
