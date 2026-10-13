> **Historical commands.** The runs below used the MCP server (`mcp__ai-mem__mem_*`) and the Chroma backend; both are gone (tag `v0-last-mcp`). The questions, baselines and `score.py` still apply to the librarian; replace the old allowedTools with `Read, Grep, Glob`.

# Librarian regression check

Does the librarian still answer the same way after a change to its definition? Chunk 2a
(navigation reference split out of `agents/librarian.md`) and chunk 3 (librarian
files-only) both check against the same baseline.

## Questions

Verbatim from the 2026-10-10 session in which they were first asked (plan appendix):

1. Was replacing the MCP server (ai_mem/server.py, mem_* tools) with a CLI/scripts, or
   packaging ai-mem as a Claude Code plugin, ever considered, tried or rejected? Why?
2. Does anything recorded depend on the MCP server staying — e.g. the Chroma rollback
   backend (AI_MEM_BACKEND=chroma), the daemon, the adr_collection_roots.json mapping that
   the server writes at startup, or subagents relying on mem_context?
3. Are there open todo_* entries that touch server.py, the daemon, or install.py's MCP
   registration?

`Relied on` in the original session (2026-10-10 morning, before that day's records
existed; for comparison only, the baseline below supersedes it):

- Q1: `todo_plugin_packaging`, `FOCUS.md`
- Q2: `domain_file_backend_replaces_chroma_2026_10_04`,
  `domain_librarian_replaces_experience_index_2026_10_04`, `chunk1_daemon_shipped_2026_07_31`,
  `docs/reference/chroma_rollback_backend.md`
- Q3: `todo_plugin_packaging`, `todo_drop_chromadb_dependency`, `FOCUS.md`

The records written later on 2026-10-10 (e.g. `domain_drop_mcp_server_for_cli_plugin_2026_10_10`)
change what Q1–Q3 should rely on, so the baseline was captured fresh.

## Method

Each run is a fresh process, cwd the repo, so it loads the agent definition at its own start:

```bash
claude -p 'Use the librarian agent (Agent tool, subagent_type "librarian", model "haiku") with repo <repo> (collection repo.ai-mem) and exactly this one question, verbatim: "<question>". Do not research or answer it yourself. When the librarian returns, print its reply verbatim and nothing else.' \
  --model sonnet --output-format stream-json --verbose \
  --allowedTools "Agent Read Grep Glob mcp__ai-mem__mem_list mcp__ai-mem__mem_get mcp__ai-mem__mem_edges mcp__ai-mem__mem_query" \
  --disallowedTools "Bash Write Edit NotebookEdit WebFetch WebSearch mcp__ai-mem__mem_add mcp__ai-mem__mem_link mcp__ai-mem__mem_delete mcp__ai-mem__mem_boost mcp__ai-mem__mem_move mcp__ai-mem__mem_split mcp__ai-mem__mem_dream mcp__ai-mem__mem_cleanup"
```

- Three runs per question (Haiku is not deterministic). The answer and `Relied on` are taken
  from the librarian's own handback in the stream, not from the outer session's echo.
  Reference docs are recorded by file stem (`chroma_rollback_backend`).
- A changed librarian that is not yet deployed runs from a scratch project dir holding
  `.claude/agents/librarian.md` (project agents override `~/.claude/agents/`), with the
  question still naming the repo.
- **Always with a control arm:** the unchanged librarian, run again in the baseline's setup,
  next to the arm under test.
- **Pass rule (since 2026-10-11, user decision):** core = the ids cited in at least 2 of the
  3 baseline runs. A run passes when it cites at least half of the core (rounded up) AND
  every id it cites is in the baseline union or the control arm's union. A question passes
  when at least 2 of its 3 runs pass. A fail is reported with the ids, not rerun away.
  Scoring: `python3 scripts/eval_librarian/score.py scripts/eval_librarian/baseline_2026_10_10.json <results>.json
  [--write]` (stdlib only).
- **Old rule (2026-10-10, replaced):** a run had to stay within the baseline union and cite
  the whole baseline intersection. The unchanged librarian failed it on Q1 (0/3) and Q2
  (1/3): the intersections (5 and 7 ids) were stricter than Haiku's run-to-run
  repeatability, so the rule could not tell a changed librarian from noise.

## Files

- `baseline_2026_10_10.json` — librarian at main `ca9f302`, before chunk 2a: per question
  the three runs (answer, `Relied on`), the union and the intersection.
- `post_edit_2026_10_11.json` — chunk 2a: the edited librarian (arm `edited`) and the
  control (arm `control`), scored by `score.py` (per run `core_cited`, `outside_allowed`,
  `pass`).
- `files_only_2026_10_11.json` — chunk 3: the files-only librarian (arm `files_only`, tools `Read, Grep, Glob`) plus the
  control arm copied unchanged from `post_edit_2026_10_11.json` (not rerun, budget rule), scored by `score.py`.
  The raw stream-json of the nine runs stays local (it quotes private records).
- `score.py` — the scoring above, rerunnable on any results file with a `control` arm.

## Results (chunk 2a, 2026-10-11, existing runs rescored with the new rule)

Core sizes: Q1 7 ids (need 4), Q2 9 (need 5), Q3 4 (need 2).

| Question | edited | control (unchanged librarian) |
|---|---|---|
| Q1 | 1/3 — FAIL | 2/3 — pass |
| Q2 | 1/3 — FAIL | 3/3 — pass |
| Q3 | 2/3 — pass | 3/3 — pass |

Every edited run cites enough of the core. All edited fails come from ids outside
baseline ∪ control:
- Q1 run 1: `antipattern_ai_mem_path_via_mcp_env_misses_hooks`; run 3:
  `domain_dream_after_every_reflect_2026_09_26`.
- Q2 run 1: `arch_overview`; run 3: `arch_overview`,
  `learning_e2e_file_backend_after_restart_2026_10_04`.
- Q3 run 3 (question still passes): `todo_ai_mem_violates_link_type`,
  `todo_frontmatter_value_injection`, `todo_symlink_following_delete`, three todos the other
  runs name as unrelated.

The control's only failing run is Q1 run 2 (2 of the 4 needed core ids).

Reading: the edited librarian finds the same core but cites more records outside it.
`arch_overview` (`docs/reference/`) appears in edited Q2 runs 1 and 3 and in no baseline or
control run, a weak sign that the edited librarian reaches for background docs more often.
All edited runs read the navigation reference first and kept the `Answer:` / `Relied on:` shape.

Limits of the edited arm:
- It changes two things at once against baseline and control: the definition text, and the
  setup (project agent in a scratch dir instead of the user-level agent in the repo).
- The reference path was substituted: the edited copy named the worktree's absolute
  `reference/navigating_records.md`, not the shipped `~/.claude/ai-mem/navigating_records.md`.
  A separate probe (one Haiku subagent, `tools: Read`, told to read `~/.claude/agents/<file>`)
  expanded `~` itself and read the file, so the shipped path should work; the deployed
  librarian itself is still to be run once after `install.py --sync-commands`.
- This check does not establish that the answers are unchanged; it reports the rule's
  result with ids.

## Results (chunk 3, librarian files-only, 2026-10-11)

Arm under test: `agents/librarian.md` with `tools: Read, Grep, Glob` and every `mem_*` mention
removed, as a project agent in a scratch dir (`PYENV_VERSION=3.13.11`, `--allowedTools "Agent Read Grep Glob"`,
`--add-dir` for the repo and `~/.claude`), reference read through the shipped `~/.claude/ai-mem/` path,
repo = the main checkout (the worktree has no `docs/records/`). Control: the 2a control arm, not rerun.
In all nine runs the librarian used only Read/Grep/Glob.

| Question | files_only | control (unchanged librarian) |
|---|---|---|
| Q1 | 2/3 — pass | 2/3 — pass |
| Q2 | 0/3 — FAIL | 3/3 — pass |
| Q3 | 3/3 — pass | 3/3 — pass |

Fails (all Q2; core need 5):
- Run 1: the handback has no `Relied on:` line (format break), scored as empty. Its prose names
  `todo_plugin_packaging`, `todo_drop_chromadb_dependency`, `pattern_persistence_migration_bypasses_mcp`,
  `learning_subagents_no_sessionstart_output_2026_10_04`, `arch_decision_pretool_push_removed_2026_09_12`.
- Run 2: core 6/5, but outside `domain_records_model_replaces_chroma_2026_10_04`, `plan_plugin_chunks`,
  `adr-migration-chunk-plan` (the last two are non-record docs under `docs/`).
- Run 3: core 8/5, but outside `arch_overview`, `domain_records_model_replaces_chroma_2026_10_04`.
Q1 run 3 (core 6/4) fails on ids outside the allowed set: `FOCUS.md`,
`learning_hooks_do_not_inherit_mcp_env_2026_07_03` (the control's Q1 run 2 fails on core 2/4).

Reading: every Q2 run that has a `Relied on:` line cites enough core; the fails are ids outside
baseline ∪ control (`arch_overview` again, as in the 2a edited arm) and one dropped `Relied on:` line. No fail
involves a `mem_*` call, so removing the tools does not explain them; the same pattern appeared with the 2a
edit. Limits as for 2a: scratch-dir project agent versus user-level control; `domain_records_model_replaces_chroma_2026_10_04`
is named in the definition's own description and exists in the records, so citing it is plausible.

Reviewer additions (chunk 3):
- Scope drift: in the raw runs the files-only librarian Grepped the whole `docs/` tree (all Q1/Q2 runs) and q2-2 read
  `docs/plan_plugin_chunks.md`, outside the definition's `docs/records|reference|sources` scope; the scope rule is
  prompt-only (Read/Grep/Glob accept any path). Without the `mem_*` tools the Haiku librarian may widen its search,
  which is a plausible cause of the outside ids in Q2.
- `relied_on` extraction (no script committed): take the handback's `Relied on:` line only, promote a
  `(plus non-record docs: ...)` list, drop other parentheticals, basename of paths, strip `.md`, `FOCUS` -> `FOCUS.md`;
  reference docs by stem.
- Removed fallback: a collection with no record files (an unmigrated Chroma-only installation) now yields "Not documented".
