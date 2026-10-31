id: learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23
type: learning
area: records
perspective: agent
created: 1792747177.637129
edges: [{"target_id": "domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15", "edge_type": "related"}]
cue: I am moving or renaming an area folder (or the repo) and assume mem and its records keep working afterwards.
---

Observed: After ai-mem moved under ai-architecture/, 11 cross-area edges dangled (written with pre-move relative prefixes) and the pyenv editable install still mapped ai_mem to the old path, so `mem` on PATH failed with ModuleNotFoundError.
Cause: Relative area paths in edges and editable installs both encode the folder location; moving an area invalidates them silently. Incoming edges from other areas are affected too (mem move already notes this for single records).
Evidence: mem doctor 2026-10-23 (edge-dangling-xarea 6, edge-unresolved 5); __editable___ai_mem_0_1_0_finder.py MAPPING pointed to the old folder (ai-mem directly in the workspace root). After the move: run mem doctor --root <workspace root>, rewrite edges with mem unlink + mem link, reinstall the editable package.

pseudonymised for publication, 2026-10-31
