id: learning_upsert_hook_command_matcher_overwrite_2026_07_31
type: learning
topic: architecture
created: 1790700223.860418
edges: [{"target_id": "fix_install_hook_registration_2026_07_31", "edge_type": "related"}]
---

Observed: install.py's `_upsert_hook_command` unconditionally overwrote `entry["matcher"]` on the retained hook group, even if that group contained a foreign user hook in the same matcher block.
Cause: `entry["matcher"] = matcher` ran regardless of whether the group contained only ai-mem's own hook. Fixed: matcher is set only if `len(entry["hooks"]) == 1` holds after the dedup stripping of this call (the group consists exclusively of ai-mem's own).
Evidence: Commit 33e0162 (formerly cited as 44f5f17), together with fix_install_hook_registration_2026_07_31; new file tests/test_install.py (plain-dict style, without mocking -- install.py can be imported as a top-level script via `import install`, since the repo root is on sys.path when `python -m pytest tests/` runs).
