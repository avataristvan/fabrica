id: learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12
type: learning
area: workflow
perspective: the-coder
created: 1791838321.935767
edges: [{"target_id": "anti_pattern_python_m_in_shim_puts_cwd_on_syspath_2026_10_12", "edge_type": "related"}]
cue: I am testing code in a git worktree while the main checkout is pip-installed editable and a subprocess imports ai_mem
---

Observed: Under an editable pyenv install, a `python -I` subprocess resolves `ai_mem` to the main checkout, not the worktree under test. Use `-I -S` plus `sys.path.insert(0, <worktree>)`.
Cause: The editable install puts the main checkout on the interpreter's path (site), and `-I` only drops the cwd and user site, so the worktree never wins; `-S` skips site, the explicit sys.path entry then decides.
Evidence: tests/test_stdlib_only.py (imports every ai_mem module this way; formerly tests/test_upgrade_guard.py).
