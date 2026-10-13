# Archivist acceptance run (chunks 2v, 2a-2)

Does the archivist, given the 18 record candidates of the 2026-10-10 briefing session as plain text and a copy of the
records without them, reproduce the hand-set edges, find the four predecessors missed on that day, flag the
`istvan_interaction_style` duplicate, and write a back-reference on every existing record it links to? Pass: >= 80%
of the 33 hand-set edges, 4/4 predecessors linked across areas, duplicate flagged, every edge to an existing record
has its back-reference (since 2a-2), nothing written outside the scratch tree.

    PYENV_VERSION=3.13.11 python scripts/eval_archivist/build.py <scratch>/runN      # copy + fixtures + agent + baseline.json
    scripts/eval_archivist/run.sh <scratch>/runN [model]                              # fresh `claude -p` (never edit while it runs)
    python scripts/eval_archivist/compare.py <scratch>/runN --report <scratch>/runN/answer.txt
    find ~/workspace -newer <scratch>/runN/stamp -path '*docs/records*' -not -path '*/.claude/worktrees/*'   # must be empty
    find ~/workspace/ai-mem-records -newer <scratch>/runN/stamp                                              # must be empty

Files: `candidates.json` (18 candidates: number, real id, type, redacted body; the archivist gets `<run>/candidates.txt`
without ids), `expected_edges.json` (33 hand-set edges from the real frontmatter, `predecessor_area: null`, + 4
missed predecessors with the area they live in), `fixtures.py` (both types and the record reader), `results/`,
`result.md`. Copy the raw outputs of a run into `results/runN_<model>/` right away: /tmp is lost on reboot.

## Design notes

- Copy: `scripts/scratch_mirror.py` (from the real areas) + `--drop-suffix _2026_10_10` (26 records dropped: the 18
  candidates plus 8 later plugin/workflow records), INDEX regenerated, edges to dropped ids stripped.
- `mem lint --fix` was run on the COPY of every area (the hand-kept ones: ai-architecture,
  ai-architecture/software-architecture-gathering, interview-notes; a no-op elsewhere) so the hand-kept-INDEX
  guard does not refuse the archivist's writes. Exit 1 (findings left, e.g. old dangling edges) is accepted.
- Redactions (no id hints): sentences naming a missed predecessor (candidate 17 named three of them in its own body)
  or announcing one ("was missed when ...", candidate 14) are removed; every other dated record id became
  "an earlier record (id withheld)".
- The scratch db dir carries `.migrations/records_v1.done`; `AI_MEM_WORKSPACE_ROOT`/`AI_MEM_RECORDS_HOME` are unset;
  `--allowedTools Read Grep Glob Bash(mem:*) Bash(mem-dream:*) Agent`. Containment of `mem --area <path>` rests on the
  prompt (all areas are under `<run>/workspace`) plus the outside-scratch check.
- The prompt tells the archivist it works on an isolated copy and to use only paths below it (a mild hint).
- Comparison: candidate -> written record by body similarity (greedy one-to-one, threshold 0.15, because the archivist
  rewrote some bodies); an edge counts when the mapped source carries it to the target (related <-> derived_from
  interchangeable; other type differences listed as "pair only"). A predecessor counts only as the expected
  (source record -> predecessor) edge, area-qualified, to the expected area.
- Run 1 (sonnet): the copy lacked `docs/reference/`, so predecessor 4 (a reference id) was impossible there. A probe
  showed `mem link` resolves reference ids once `docs/reference/` is in the copy; `build.py` now copies
  `ai-mem-records/global/docs/reference/`. Run 2 (opus) had it.
- The machine rebooted at 09:20 and wiped /tmp: run 1's raw outputs are gone (its numbers are from the run report);
  run 2's outputs are kept in `results/run2_opus/`.
- Chunk 2a-2: candidate 17 still announced the predecessors ("predecessors in `global` and `workspace` were found only
  hours later ...") although their ids were already cut; that sentence is now redacted too (`ANNOUNCEMENTS`).
- The definition under test: `~/.claude/agents/archivist.md` is a symlink into the MAIN checkout, so a run from a
  worktree would use the old definition. `build.py` copies this checkout's `agents/archivist.md` to
  `<run>/workspace/ai-mem/.claude/agents/`; a project agent wins over a user agent. `transcript.jsonl` (stream-json)
  shows the archivist's tool calls, so it can be checked that the new procedure ran.
- Back-references: for every edge from a new record to a baseline record, compare.py looks for any edge on that record
  pointing back at the new one (or `superseded_by` naming it); the edge type is not checked, and `docs/reference/`
  targets are not records and need none. Run 2 (its scratch tree survived the reboot) scores 6/37: 37 edges from its
  new records to baseline records, 6 with a back-reference.
- `run.sh` hashes every file under the real `docs/records/` trees and `ai-mem-records/` before and after the run and
  exits 1 on a difference: `Bash(mem:*)` would permit `mem add --area ~/workspace/...`. A write to real state by
  someone else during the run (the orchestrator's FOCUS.md) shows up there too.
