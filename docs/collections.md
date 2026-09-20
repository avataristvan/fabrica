# Collections and Memory Scoping

## Auto-detection

`repo_context.py` detects the correct collection from the working directory:

| Condition | Collection |
|-----------|------------|
| `CLAUDE.md` at git root | `repo.<repo-name>` |
| `CLAUDE.md` in monorepo subdir | `repo.<repo-name>.<subdir>` |
| No `CLAUDE.md` found | `workspace` |
| Cross-session general knowledge | `global` |

The collection name is derived from the git remote URL slug or directory name.

## Entry Types

The optional `type` metadata field on `mem_add` tags an entry for filtering (`mem_query(type=...)`, `mem_topics`) and for `mem-dream`'s consolidation rules. Canonical types, each with a fixed structure enforced by convention (not schema validation):

| Type | Structure | Use for |
|---|---|---|
| `pattern` | `Rule: / When: / Why:` | A reusable technique or best practice |
| `anti-pattern` | `Tried: / Failed because: / Instead:` | A documented failure mode |
| `dilemma` | `Tension: / Context A: / Context B: / Affected A: / Affected B: / Questions:` | A genuine value conflict with no single correct answer |
| `domain` | `Decision: / Why: / Scope:` | Business/domain knowledge — why a rule exists, a domain constraint — as opposed to a coding technique |
| `feedback`, `project`, `reference`, `user` | free-form | Descriptive entries, no fixed structure |

`domain` entries should be written as soon as the knowledge surfaces during coding, not deferred to an end-of-session reflection step — that kind of insight is easy to lose if it isn't captured immediately. There's no hook that forces this (recognizing a domain decision requires semantic judgment a deterministic hook can't reliably make); it's agent discipline, reinforced by the `type` description on `mem_add` itself.

`mem-dream` never merges a `pattern`/`anti-pattern` entry with a `domain` entry — technique and business rationale are different axes even when they discuss the same code.

## Special Entries

- **`current_focus`** (id `"current_focus"`) — primary context entry per collection. `SessionStart` no longer pushes its text by default (see `docs/hooks.md`) — an agent pulls it with `mem_get(ids=["current_focus"], collection=...)`, or it's shown as `[scope focus]` text when `session_start_verbose: true`.
- Nothing currently reminds the agent to update `current_focus` automatically — that reminder used to come from a `Stop` hook that was never actually wired into `install.py` (the module doesn't exist in this repo). `/reflect` Step 5 is the place this happens today.

## Collection Lifecycle

### First Session (agent-driven seeding)
Run `/mem-init` in a project to seed its `repo.*` collection: the agent explores the
codebase (not just CLAUDE.md) and writes down what actually matters, deciding entry
boundaries and types itself rather than mechanically splitting CLAUDE.md's H2 sections.
This replaced an earlier automatic seeder (`repo_seeder.py`, removed) that split
CLAUDE.md by heading once a global usage-rate threshold was crossed — agent-driven
exploration produces better-scoped entries than a fixed heading split, and doesn't
depend on an unrelated global stat to decide when to run.

### TTL Expiry
Set `ttl_days` on `mem_add` to auto-expire entries. `mem_cleanup` removes expired entries.

### Forgetting Curve
`mem_cleanup stale_after_days=N` removes entries not accessed within N days — useful for pruning outdated knowledge.

## mem_delete Semantics

- `mem_delete(collection="foo", ids=["a","b"])` — deletes specific entries, returns count
- `mem_delete(collection="foo")` — drops the entire collection, returns `-1`

## Routing at Query Time

Always pass the collection explicitly to `mem_add` and `mem_query`. The SessionStart hook prints the active collection:

```
Active collection: "repo.ai-mem". Pass collection="repo.ai-mem" to mem_add and mem_query in this session.
```

Use `global` for knowledge that should persist across all repos (user preferences, cross-project patterns).
