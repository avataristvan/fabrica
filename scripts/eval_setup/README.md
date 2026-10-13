# Setup skill exit check

Does `/ai-mem:setup` find the right boundaries, leave files alone until approval, and judge a `mem doctor` report correctly? Each run is a fresh `claude -p` process on its own fixture, so it loads the skill from the plugin directory at its own start.

```bash
python3 scripts/eval_setup/run.py --out <empty scratch dir> --model sonnet --repeats 3
python3 scripts/eval_setup/run.py --out <same dir> --model haiku --repeats 3
```

Exit code 0 when every part passes in a majority of its repeats (2 of 3) and nothing under `~/.claude` changed. Replies and checks per run land in `<out>/<model>/<part>-<n>.json`, the summary in `<out>/summary_<model>.json`.

## Setup of a run

- Real `HOME` (a temp `HOME` cannot run `claude -p`: no login), but `--setting-sources project,local`: the user's `~/.claude/CLAUDE.md` and settings are not loaded, so no standing auto-apply instruction counts as approval. `--plugin-dir` is the checkout under test, `--permission-mode acceptEdits`: the run *could* edit the fixture without asking, so an unchanged file shows the skill's own restraint.
- Fixture per run, a git repo: an existing `CLAUDE.md`; `.claude/commands/dev-team.md`, a copy of `--dev-team` (default `~/.claude/commands/dev-team.md`) with its hook-in line removed; that line must read `<boundary heading>: At this boundary follow the ai-mem handoff protocol (skill \`handoff-protocol\`).` (the script stops otherwise), and the heading is what the reply must name; `release-train.md`, a team that spawns a coder and a reviewer (a real boundary); `bookshop-copy/SKILL.md`, which names a "librarian" persona (a spurious doctor hit); `doctor_report.txt` flagging both.
- The model: the skill sets no `model:` in its frontmatter, so it runs under the session's model; `--model` sets that. (A plugin skill's `model:` *is* honored: a probe skill with `model: haiku` ran entirely on Haiku under `--model sonnet`.)

## Checks

| Part | Prompt | Checks |
|---|---|---|
| `teams` | part 1 on the team copy | the canonical line appears verbatim on a `+` line of a proposed diff; the reply names the boundary heading the removed line stood under; fixture files byte-identical |
| `claude_md` | part 2, then `both lines` via `--resume` | routing line proposed (`docs/records/` and `ai-mem:librarian` in the reply); files byte-identical before approval; after approval `git diff --numstat CLAUDE.md` shows insertions and 0 deletions |
| `doctor` | part 3 on the report, plus a `VERDICT <path> real\|spurious` line per flagged file | `commands/release-train.md` real, `skills/bookshop-copy/SKILL.md` spurious; files byte-identical |

`~/.claude` unchanged means: every file under `commands/`, `agents/`, `skills/` and `CLAUDE.md`, `settings.json`, `settings.local.json` hashes the same before and after. It detects a write, it does not prevent one, and it does not cover session state, caches or `plugins/`; edits in another live session during the check show up as a (false) failure.

The `VERDICT` line is added by the check's prompt only, to grade without reading prose; the skill itself asks for a verdict per flagged file in free form.
