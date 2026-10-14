id: domain_user_records_as_role_perspective_2026_10_04
type: domain
area: architecture
created: 1791133727.801265
edges: [{"target_id": "domain_records_model_replaces_chroma_2026_10_04", "edge_type": "related"}, {"target_id": "pattern_triggers_beat_storage_and_ranking", "edge_type": "related"}, {"target_id": "domain_plugin_target_picture_implemented_and_closed_2026_10_15", "edge_type": "related"}]
---

Decision: 'user' stays a record type (docs/records/<area>/user/). Two kinds of user knowledge are kept apart: what must act in every session (tone, way of working) goes into CLAUDE.md, which is loaded automatically; the user's perspective as a yardstick for a role (what they value, what bothers them, what 'good' means to them) is a user record that the role pulls on a fixed trigger -- first the reviewer: dev-team.md's reviewer prompt template tells it to read the user records before reviewing. mem-adr-sync migrate writes user entries like any other record.
Why: The user proposed it (2026-10-04): a reviewer should partly adopt the user's view. A pull with a fixed trigger in the role's prompt is the pattern that measurably works (pattern_triggers_beat_storage_and_ranking); whether subagents see CLAUDE.md at all is unverified, so the explicit pointer in the role prompt is the robust path.
Scope: Narrows domain_records_model_replaces_chroma_2026_10_04's clause 'user preferences do not belong in records' to always-on preferences. Closes todo_user_record_type.