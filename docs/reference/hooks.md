# Hooks

Reference for the Claude Code lifecycle hooks ai-mem registers: the SessionStart routing hook and three enforcing hooks (SubagentStop, PostToolUse, Stop). All are silent on failure (wrapped in try/except, exit 0, nothing on stderr) so they never interrupt a session. None of them injects record content: they route, check, or remind. Why: [Organisational memory](../explanation/organisational-memory.md), "Pull, not push".

## SessionStart (`ai_mem/hook.py`)

Fires at the start of every Claude Code session.

1. Detects the area: the nearest ancestor of the cwd with `docs/records/` (a worktree maps to its main checkout) and prints `Area: <path>`.
2. Prints one `Records:` line pointing at `FOCUS.md` and `INDEX.md` of the area and at the librarian agent.  Outside any area, no `Area:` line is printed.
3. When the session is inside an area and `$AI_MEM_PATH/doctor_last_run` (epoch seconds, written by `mem doctor`) is missing or older than 14 days, adds one pointer line: `Run mem doctor (last run N days ago).` or `Run mem doctor (not run yet).` A pointer, never findings.

Nothing from the records is pushed, and the hook never opens a database. The agent pulls on purpose: it reads the record files, or asks the librarian agent, which reads them (including each record's `cue:` line) by judgment.

```
[ai-mem]
Area: <area folder>
Records: <area>/docs/records (FOCUS.md = current focus, INDEX.md = catalogue of decisions, learnings, todos). Read them on demand; for "why is it like this / was this tried before?" ask the librarian agent.
```

If no part is generated, the hook exits silently.

## Enforcing hooks (`ai_mem/hooks/`)

Hooks enforce THAT a ritual happens; roles decide HOW (`domain_hooks_enforce_that_roles_decide_how_2026_10_10`). Each module is a `python -m ai_mem.hooks.<name>` entry point, stdlib only, exit 0 and no stderr on any stdin. Ids and paths from stdin are untrusted: session ids are accepted only as `[A-Za-z0-9_-]{1,128}` before they become a file name, paths are normalised before the area walk, and a transcript that is not a regular file is never opened.

| Event | Module | Does |
|---|---|---|
| `SubagentStop` | `retro_check` | For listed roles only: is there a `[retro]` block with non-empty `records_consulted` and `record_candidates` (`none` counts)? First miss: `{"decision":"block","reason":...}` once; with `stop_hook_active` it only logs, so it cannot loop. |
| `PostToolUse` (`Write\|Edit\|MultiEdit`) | `lint_after_write` | When `tool_input.file_path` is a record file under some area's `docs/records/`, runs `records_lint` on that one record plus INDEX.md; findings come back as a `block` reason (the tool already ran), clean files produce nothing. Never `--fix`. |
| `Stop` | `reflect_reminder` | When the transcript shows a Write/Edit/MultiEdit and no `/reflect`, returns a user-visible `systemMessage` once per session (marker `$AI_MEM_PATH/reminded/<session_id>`). Never `block`. |

`SubagentStop` also fires for subagents spawned by subagents (verified 2026-10-11: an `Explore` started by `the-coder` produced its own event), so a reviewer inside the-coder is checked directly.

### Retro roles

The roles come from the plugin option `retro_roles`, else `$AI_MEM_PATH/retro_roles.json` (a JSON list of agent types); both missing or malformed means the default `["ai-mem:anchor-lint"]`: the plugin enforces only the agents it ships; your own teams (e.g. `the-coder`) are added through the option. Other agent types produce no output and no log line.

### Retro log (`$AI_MEM_PATH/retro_log.jsonl`)

One JSON object per checked stop (the contract with `mem doctor`):

```json
{"ts": 1791736395.48, "session_id": "...", "agent_type": "the-coder", "agent_id": "...", "has_retro": false,
 "missing": ["records_consulted", "record_candidates"], "records_consulted": null, "record_candidates": null, "learned": null}
```

`has_retro` is whether a `[retro]` marker was found; `missing` lists the required fields that are absent or empty; the three text fields hold the raw field text (`"none"` stays `"none"`, absent or empty is `null`), capped at 2000 characters. An agent that was blocked and then complied appears twice with the same `agent_id`: first with the miss, then with the complete block.

### Registration

The plugin registers all four hooks in its own `hooks/hooks.json`, each as `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/run.py" <module>` (timeout 10). `run.py` puts the plugin root on `sys.path`, runs the module as `__main__` and always exits 0 with nothing on stderr, so a hook needs neither an installed package nor `|| true`. The modules use only the standard library, so the system `python3` suffices.

Two plugin options reach the hooks as environment variables, `CLAUDE_PLUGIN_OPTION_RETRO_ROLES` (comma-separated agent types, read by `retro_check`) and `CLAUDE_PLUGIN_OPTION_DOCTOR_CADENCE_DAYS` (read by SessionStart). A variable that is unset or blank means the file or default named above; Claude Code exports an option only once a value is set. Runtime state stays in `$AI_MEM_PATH` (default `~/.local/share/ai-mem`), not in `${CLAUDE_PLUGIN_DATA}`: that variable is not in the Bash tool's environment, so `mem doctor` run by an agent could not find it.

The hooks of the plugin and the entries older `install.py` versions wrote into `~/.claude/settings.json` would both fire. Remove the old entries from `settings.json` by hand, or check out the tag `v1-last-upgrade-path`, whose `install.py --plugin-switch` removes them.

## Retired hooks

Earlier versions also registered `UserPromptSubmit` and `PreToolUse` hooks that injected search results into the prompt, and a `PostToolUse` hook that counted accesses. They were retired in September and October 2026 because pushed content scaled with conversation length and edit count, not with relevance. Their measurements and reasoning: [sources/automation.md](../sources/automation.md), [sources/pull_through_measurement_impl_2026_07_31.md](../sources/pull_through_measurement_impl_2026_07_31.md), [sources/hook_routing_subagent.md](../sources/hook_routing_subagent.md). The modules were removed at the plugin cutover (tag `v0-last-mcp`); existing installs remove their hook entries as described under Registration.
