id: learning_deleting_a_removed_modules_test_file_loses_tests_of_moved_functions_2026_10_31
type: learning
topic: workflow
perspective: the-coder
created: 1793471377.227264
edges: [{"target_id": "pattern_stale_by_neighbouring_retirement", "edge_type": "related"}]
cue: I am deleting the test file of a module that a chunk removes, while some of its functions moved to another module.
---

Observed: When the test file of a removed module was deleted (tests/test_repo_context.py), `_to_main_checkout`, which had moved to another module rather than been removed, lost its worktree tests. The reviewer caught it; a7ba267 restored them in tests/infrastructure/test_areas.py.
Cause: The test file was judged by the removed module's name, not by what its tests covered; a function that survives the retirement keeps its need for tests.
Evidence: commits fe8403f and a7ba267 (pushed); tests/infrastructure/test_areas.py. Same family as pattern_stale_by_neighbouring_retirement (a retirement leaves neighbours behind), here for tests.
