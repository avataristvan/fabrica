id: domain_setup_applies_claude_md_changes_only_on_approval_2026_10_12
type: domain
area: plugin
perspective: user
created: 1791833919.54524
edges: [{"target_id": "domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12", "edge_type": "related"}]
cue: I am building a skill or agent that proposes edits to user-owned config files such as CLAUDE.md
---

Decision (user, 2026-10-12): the setup skill applies CLAUDE.md changes only on approval. A standing user instruction to auto-apply counts as approval and must be quoted when applying.
Why: The librarian's anchor answer surfaced a conflict between the chunk's approval gate and the user's global auto-apply rule before coding; this resolves it without silently overriding either.
Scope: skills/setup/SKILL.md "Rules"; any skill proposing edits to user-owned files.
