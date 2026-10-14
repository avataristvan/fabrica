id: domain_framework_named_fabrica_2026_10_10
type: domain
area: architecture
perspective: user
created: 1791635457.277327
edges: [{"target_id": "domain_fabrica_method_ai_mem_build_user_environment_use_2026_10_13", "edge_type": "related"}, {"target_id": "domain_fabrica_practice_not_process_pattern_language_2026_10_14", "edge_type": "related"}]
---

Decision: The framework is called Fabrica. ai-mem keeps its name and is the memory plugin that supports Fabrica. Tasklies are one ritual of Fabrica, the way a retro or a daily is a ritual of Scrum. Other rituals include the charter at a session start, the handoff at a boundary, and the review against the records. Update 2026-10-14 (user): Fabrica lives inside the ai-mem repo under docs/fabrica/. One public repo; renaming the repo to fabrica is deferred. The earlier plan of a guide.md shaped like the Scrum Guide is replaced by domain_fabrica_practice_not_process_pattern_language_2026_10_14 (core.md plus patterns/); the manifesto is folded into docs/fabrica/core.md (draft kept as docs/sources/fabrica_manifesto_draft_2026_10_10.md).
Why: The framework (conventions, roles, rituals, artifacts) is the substance, and the tool is replaceable (docs/sources/epistemology_framework.md, 'Synthesis', 2026-09-25). The name comes from the Latin fabrica ecclesiae, the institution that built and kept a cathedral across generations. That is the international form of the German Bauhütte: organisational memory, rituals and handoffs, apprentice and master learning from each other. English 'fabric' adds the image of woven knowledge. Keeping 'ai-mem' for the plugin avoids a breaking rename for installed users.
Scope: Fabrica documentation (todo_split_manifest_and_name_framework), docs and README, plugin description. Name collisions (e.g. Benetton's research centre Fabrica) were not checked and are still open.
