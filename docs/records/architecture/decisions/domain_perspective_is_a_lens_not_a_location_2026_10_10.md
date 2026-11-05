type: domain
topic: architecture
perspective: user
created: 1791634114.755075
---

Decision: Every record can carry a `perspective:` field naming whose knowledge or experience it is: `user`, `agent`, or a role such as `the-coder` or `reviewer`. Location follows topic (area), never party. The librarian uses perspective as a lens, not a filter. It structures answers by party ('decided X because ...' / 'the coder experienced ...'). A contradiction between perspectives becomes visible (`contradicts` edge). The reviewer's user yardstick becomes a perspective filter. `global` dissolves by topic, like `workspace` and `subagent.*`: AI-work practice and the Navigator's interaction style go to the ai-architecture area, records about a project go to it, and machine and tooling facts go to a small environment area. There is no personal area.
Why: The collections mixed two axes. `subagent.the-coder` used the party as a location, so 179 project-specific records sat outside their projects. `user` is a kind although it is a party. `global` was the location for 'topic unknown'. Keeping the party inside the record lets the librarian deliver both perspectives on one question (the Navigator's idea, 2026-10-10). That mirrors the evidence/inference split the Navigator applies to sources: who claims something belongs to the claim.
Scope: the record format (optional `perspective:`), navigation reference, archivist (sets perspective), librarian (answers by perspective). Open for the planner: whether the `user` kind folds into `perspective: user` or stays as a kind.

pseudonymised for publication, 2026-10-11

## Edges

- related: [domain_area_path_is_the_address_of_knowledge_2026_10_10](domain_area_path_is_the_address_of_knowledge_2026_10_10.md)
- related: [domain_user_records_as_role_perspective_2026_10_04](domain_user_records_as_role_perspective_2026_10_04.md)
