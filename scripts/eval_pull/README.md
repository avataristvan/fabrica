# Pull gap-test

Question: when an agent gets a task-like question and is not told that memory exists, does the pull path
reach knowledge that lives only in ai-mem? Method: knowledge exists only in memory, a fresh agent gets the
question without a hint, and a memory arm is compared against a no-memory arm. Cases and answer keys are in
`cases.json`.

`gold_ids` refer to entries in the maintainer's own memory collection. To reuse the harness, replace the
cases with questions whose answers live only in your own entries.

## Stage A — agent runs (costs tokens; not automated)

Per case, two fresh sessions/subagents with the same repo and CLAUDE.md, nothing else:

- **mem arm**: only the question, plus "List every tool call you made at the end, with exact arguments."
  Do not mention memory or ai-mem in the prompt.
- **nomem arm**: same, plus "Do not use any mem_* tools."

Record per run: final answer, every `mem_*` call (query text, ids fetched), and the outcome from
`cases.json -> scoring`. The gap is real only if the nomem arm scores `fail`/`neighbour`/`neutral`
and the mem arm scores `ok`. Cases where nomem already answers correctly are not gaps — drop them.

Measures: (1) did the agent call `mem_query` at all (trigger), (2) did its own query reach the gold
entry (retrieval), (3) did it use the entry (judgment), (4) controls: does it say "not documented".

## Stage B — replay (cheap, deterministic)

```bash
python3 scripts/eval_pull/replay.py                      # questions verbatim
python3 scripts/eval_pull/replay.py --queries q.json     # + agent-written queries from stage A
```

`q.json`: `{"g1_pretool_numbers": ["query the agent actually wrote", ...]}`. Compares cosine vs the
hybrid the server uses; shows the top-1 score on controls.

## Caveats

- Do NOT tell agents to avoid "writing/saving anything": `mem_get` bumps `access_count`, and two agents skipped memory entirely because of that wording. Say "Make no changes to files." only.
- If project instructions (CLAUDE.md / CLAUDE.local.md) name entry ids, agents that see an id fetch it directly with `mem_get` (no similarity search). Cases with such a pointer test the pointer, not retrieval.
- Move `scripts/eval_pull/` out of the repo tree while agents run; `cases.json` contains the answer keys.

- Questions were written by an agent that had read the entries; vocabulary overlap is minimised, not zero.
  Replace or add questions from real sessions where possible.
- `vetted_absent` terms were checked against repo files, git log/diffs, project instructions and the
  auto-memory dir on 2026-09-20; re-check after docs change.
- Agent tool logs are self-reported.
