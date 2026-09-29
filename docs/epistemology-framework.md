# The Epistemology Framework

ai-mem is a memory tool, but memory alone does not produce knowledge. What turns stored entries into genuine agent expertise is the methodology around it. Together they form an **epistemology framework** — a system that determines how an agent comes to know things, not just how it stores them.

> **Implementation note:** This document distinguishes between what is code-backed and what is convention. Sections marked *[convention]* describe workflow patterns enforced by agent prompts and Skill definitions, not by code constraints. Sections marked *[planned]* describe intended capabilities not yet implemented.

---

## Foundational Premise: Agents Do Not Know Where They Are

A Claude agent has no intrinsic awareness of its own position in a multi-agent hierarchy. It does not know whether it is the top-level Orchestrator, a subagent spawned for a subtask, or a temporarily embedded Expert. Without explicit context, it will not behave accordingly.

`agent_context.py` detects hierarchy position at the **hook level** — via depth counters and signature matching — and uses this to gate context injection. But this is external detection, not agent self-awareness. The agent reasoning inside Claude never receives "you are the Orchestrator" as a ground truth — it receives it only if the prompt says so.

This gap is the origin of the framework. Every convention in the system — the Orchestrator-as-central-writer pattern, `[retro]` blocks, collection routing, the `/reflect` ritual — exists to **provide hierarchy context explicitly** rather than assuming the agent will derive it on its own.

**Practical implication:** The convention layer is not optional workflow polish. It is structural scaffolding that gives agents a role, a scope, and a persistent identity they would otherwise lack. Removing or weakening the conventions does not simplify the system — it removes the only mechanism by which agents know who they are.

### Transparency as a Feature

The convention-based approach has a benefit that full automation cannot offer: **mutual visibility**.

When the `/reflect` ritual surfaces agent observations, subagent `[retro]` blocks, and user feedback in a shared exchange, both sides learn from the other in that moment. The agent sees what the user considers important; the user sees what the agent noticed that they missed. This bilateral exchange is not overhead — it is a second learning signal on top of what gets stored in ai-mem.

A fully automated system (hooks firing silently, labels assigned without confirmation, dream running in the background) would close the feedback loop technically but break this exchange. The agent would learn from patterns; the user would not learn from the agent.

The deliberate pace of the convention layer is therefore not a limitation of the current implementation — it is a design choice that keeps the human in the loop as an active participant, not just a source of ground-truth labels.

> **The core trade-off:** Automation would give the agent more signals. Convention gives it better ones. The framework optimizes for accuracy, not efficiency.

---

## The Three Pillars

### 1. Empirical Methodology — the Taskly *[convention]*

After every task, the agent runs `/reflect` (the Taskly ritual). It is structured self-observation modeled after Agile retrospectives:

- Subagents append a `[retro]` block (`learned:`, `blocked:`, `next:`) at the end of their response
- The orchestrating agent contributes its own observations first
- The user adds ground-truth feedback
- The agent writing the reflect output stores results via `mem_add`

This is the input side. Raw experience becomes structured entries.

**What the code does:** The `/reflect` Skill (`skills/reflect.md`) defines this ritual as a five-step prompt sequence. `[retro]` blocks are read and interpreted by the LLM at runtime — there is no code parser. The convention that the Orchestrator (and not individual subagents) is the sole writer to `mem_add` is a workflow rule, not a technical constraint.

### 2. Deterministic Persistence — ai-mem

The tool provides reliable storage and retrieval:

- **ChromaDB** for semantic vector search
- **BM25 hybrid layer** (optional) — fuses cosine + BM25 scores
- **Evidence edges instead of a score** — trust in an entry is shown by traceable edges, not a number: `confirms` (a later record bears out an earlier one), `supersedes`, `contradicts`. `/reflect` records a citation with `mem_boost` (`boost_count` + optional `cue`), which carries no score. The earlier `confidence`/`access_count` lifecycle was dropped 2026-09-26 (`domain_drop_confidence_for_evidence_and_librarian_2026_09_26`) because the number converged on popularity, not relevance, and could not say *why* to trust an entry
- **TTL + forgetting curve** — `mem_cleanup` with `stale_after_days` removes entries not accessed within a window
- **Typed entries** (`feedback`, `project`, `reference`, `user`, `pattern`, `anti-pattern`, `dilemma`, `domain`) for filtered retrieval
- **Typed causal edges** — directional relationships between entries (`contradicts`, `fixes`, `causes`, `related`, `supersedes`, `confirms` — `supersedes` marks an entry as overtaken without deleting it; retrieval flags it and appends the successor)

An earlier version of this pillar included an adaptive MLP re-ranker that learned from access patterns; it was removed in 2026-06 (see CLAUDE.md's Critical Invariants) in favor of ChromaDB's native cosine ordering (the confidence lifecycle that briefly replaced it is itself gone since 2026-09-26) — simpler, no training step, no PyTorch dependency.

**Split-hint detection** is also code-backed: entries with `text ≥ 500 chars` (or carrying structural markers — multiple headers, multiple `Tried:` blocks, a long numbered list) are flagged in every `mem_query` response as candidates for splitting.

#### Lean Context by Design — Pull, Not Push

Context bloat is the primary failure mode for memory-augmented agents: dumping the full collection into every prompt drowns the signal in noise. ai-mem's answer to this changed shape over time.

An earlier version solved it at the hook level: a `UserPromptSubmit` hook queried the active collection against every incoming prompt and injected the top-3 relevant entries, gated by a ranker-confidence threshold. That hook (and a `PreToolUse` counterpart that did the same before every file edit) was retired in 2026-09 — see `docs/hooks.md` — because firing on every message or every edit meant the token cost scaled with conversation length or edit count, not with actual relevance, regardless of how tight the per-call selection was.

The current answer is pull, not push: `SessionStart` announces which collection to use (a one-line routing hint, no content), and the agent decides when to query it — `mem_query` for a semantic search, `mem_get` for a known id. The selection discipline (top-k, never the full collection) still applies to every `mem_query` call; what changed is *who decides to call it*, not how tightly the results are scoped once called.

#### Typed Causal Edges — Knowledge as a Graph

Raw memory entries store facts in isolation. Typed edges model *relationships* between knowledge — which patterns contradict each other, which fixes address which bugs, which anti-patterns follow from which choices.

Both entry types have canonical formats that make them self-retrieving and scannable during dream consolidation:

| Type | Format |
|---|---|
| `pattern` | `Rule: <rule>\nWhen: <context>\nWhy: <invariant>` |
| `anti-pattern` | `Tried: <approach>\nFailed because: <reason>\nInstead: <alternative>` |
| `dilemma` | `Tension: <value A> vs. <value B>\nContext A: <when/why>\nContext B: <when/why>\nAffected A: <who, how>\nAffected B: <who, how>\nQuestions: <what to ask to determine which context applies>` |

The leading keyword (`Rule:`, `Tried:`) is the self-retrieving hook — a future query about the same approach will surface the entry without special retrieval logic.

**Values extension:** When an anti-pattern involves human stakeholders — people treated as instrumental variables, trust broken, autonomy overridden — add an `Affected:` field:

```
Tried: <approach>
Failed because: <causal reason — including why it is wrong, not just that it failed>
Affected: <who was affected and how — models the other perspective explicitly>
Instead: <alternative>
```

This field forces the system to store *why it matters for others*, not just the pragmatic outcome. The distinction between knowledge-as-power and knowledge-as-wisdom lives here: a rule says "don't do X"; an `Affected:` entry says "when you do X, this is what happens to [person] and why that is wrong." The causal account generalizes to new situations no rule anticipates.

```
# After storing a best-practice pattern (canonical format):
mem_add(documents=["Rule: Use AddMemoryUseCase in tests, not repo.upsert() directly.\nWhen: Writing tests that insert memory entries.\nWhy: AddMemoryUseCase injects required timestamps; ChromaDB rejects empty metadata dicts."],
        ids=["pattern_add_via_use_case"], type="pattern", collection="repo.ai-mem")

# After storing the matching anti-pattern (canonical format):
mem_add(documents=["Tried: calling repo.upsert() directly in tests\nFailed because: ChromaDB rejects empty metadata dicts\nInstead: use AddMemoryUseCase which always injects timestamps"],
        ids=["antipattern_direct_upsert"], type="anti-pattern", collection="repo.ai-mem")

# Link them:
mem_link(source_id="antipattern_direct_upsert", target_id="pattern_add_via_use_case",
         edge_type="contradicts", collection="repo.ai-mem")
```

Now when `mem_query` retrieves the pattern, the anti-pattern surfaces automatically alongside it (and vice versa). Budget: 2 linked entries per query. Linked entries are tagged `via_edge` and `via_source` in their metadata.

This is the difference between *storing facts* and *storing a knowledge graph*. A senior engineer does not just know what the best practice is — they know what mistake it replaces and why. The edge makes that relationship retrievable, not just inferrable.

### 3. Dreaming Agent — consolidation

Periodically (currently triggered manually by the Navigator), the Dreaming Agent (`mem_dream`) runs. It calls a Claude model to produce a structured proposal:

- **UPDATE** — rewrite an entry for clarity
- **MERGE** — combine two related entries
- **DELETE** — remove redundant or stale entries (auto-applied when `auto_delete=true`)
- **ADD** — propose a new generalized entry
- **LINK** — document a relationship between two entries that must stay separate (`contradicts`, `fixes`, `causes`, `related`); applied when `auto_link=true`
- **SUPERSEDE** — mark an entry as overtaken by a newer one instead of deleting it (the old entry stays readable and is flagged); applied when `auto_supersede=true`

Actions that cannot be applied (unknown ids, ids in different collections, invalid edge types) are listed with their reason rather than dropped. MERGE proposals that conflict with an existing `contradicts` or `supersedes` edge are flagged in the report.

`mem_dream` operates within a single collection or across all collections (`mode=hier`). It also supports a `team` mode for cross-agent consolidation.

**What `mem_dream` does not do automatically:**

- It does not split large entries — splitting is a separate tool (`mem_split`) triggered independently

**Trigger placement:** `mem_dream` is invoked as part of the `/reflect` ritual (convention), not via a hook. Hook-based auto-triggering would fire for every subagent session, not just the orchestrator — the same class of problem that got the `UserPromptSubmit`/`PreToolUse` push hooks retired (see `docs/hooks.md`). Keeping the trigger in `/reflect` ensures it runs exactly once per task cycle, always at the orchestrator level, always deliberately. Since 2026-09-26 it runs after **every** `/reflect`, scoped to the active collection (no entry-count threshold — a project collection legitimately stays large), so whatever a session wrote or flagged is sorted in at the latest then; LINK and SUPERSEDE are auto-applied, DELETE/MERGE need confirmation.

**Upward propagation** is handled during the same Step 6 of `/reflect`. ADD proposals that target a higher-level collection than their source (e.g. a `repo.*` pattern proposed for `workspace`) are surfaced as propagation candidates. The Orchestrator confirms; `mem_add` copies the entry into the target collection. The source entry is kept — propagation copies upward, it does not move. This keeps the decision in the agent's judgment rather than in code, consistent with the rest of the convention layer.

**Splitting** uses `SplitMemoryUseCase`: deletes the original entry and replaces it with 2–3 focused sub-entries via a Claude call. Split-hints from `mem_query` indicate when an entry is a candidate.

The Dreaming Agent is the bridge between raw empiricism and structured knowledge — analogous to sleep-based memory consolidation. The automatic, threshold-triggered version of this loop is in active development.

---

## The Knowledge Hierarchy

Collections are organized by scope. Two levels are auto-detected from the working directory:

```
global                   ← cross-project, manually managed
  └── workspace          ← fallback when no git repo is found
        └── repo.<name>  ← auto-detected from CLAUDE.md + git remote
```

The full intended hierarchy (partially implemented):

```
global
  └── workspace          (team / department)
        ├── repo.<name>   (project — auto-detected)
        │     └── subagent  (individual agent — convention only, not auto-detected)
        └── [expert agents]  (cross-project — convention only, no schema enforcement)
```

The `subagent` level and `expert.*` collections can be created manually by naming them accordingly. The `SessionStart` hook (`hook.py`) names the active repo collection (and a registered subagent's own collection); by default it does not push `current_focus` text — an agent pulls it with `mem_get`. It also detects whether it is running inside a subagent via `agent_context.py`, but does not automatically create a separate subagent-scoped collection.

A learning starts at the level where it was experienced. Upward propagation — from `repo.*` to `workspace` to `global` — is a design goal; the Dreaming Agent currently identifies candidates but does not execute the cross-collection move.

---

## The Junior → Senior Effect

This is the central claim of the framework:

> An agent that runs Tasklies accumulates structured experience faster than any individual can consciously track. Over time it becomes more competent in its domain — not because it runs a larger model, but because it has better-organized knowledge.

The progression:

| Stage | What the agent has |
|---|---|
| Junior | Large model, no domain memory |
| Mid-level | Memory of what was done |
| Senior | Memory of what worked, what failed, and in which context — organized by the Dreaming Agent |

The key distinction from simple retrieval systems: a senior does not just remember more — they remember *better organized* knowledge. Evidence edges (`confirms`/`contradicts`/`supersedes`) + the Dreaming Agent provide that organization over time.

---

## Agent Teams *[convention]*

The framework extends to multi-agent teams. These patterns are enforced by agent prompts and Orchestrator conventions, not by code.

### Team composition

Each agent has three knowledge layers:
- **Team knowledge** — shared expertise of the group (`workspace` collection)
- **Project knowledge** — context for the current engagement (`repo.<name>` collection)
- **Personal knowledge** — individual profile: role, personality, accumulated experience (named by convention, e.g. `subagent.<role>`)

### Expert agents

Expert agents are specialists with their own cross-project collections. They accumulate expertise across every team they join.

When called into a team:
1. They receive full context: team knowledge + project knowledge + task
2. They work as a full team member for the duration
3. Their `[retro]` feedback flows to the Orchestrator
4. The Orchestrator writes relevant learnings into both the team collection and the expert's own collection
5. The expert leaves with new experience; the team retains what the expert contributed

This is the **guest professor model**: the expert teaches while learning, and both sides are stronger after the engagement. Collection naming and routing are enforced by the Orchestrator prompt, not by code.

### The Orchestrator

By convention, the Orchestrator is the central writer to `mem_add`. Individual subagents surface learnings via `[retro]` blocks; the Orchestrator decides what gets stored where.

```
All agents → [retro] → Orchestrator
                           ↓
                     evaluates + routes
                           ↓
              mem_add (team / expert / project)
```

---

## The Full Loop

```
Task
  ├── subagents produce [retro] blocks     [convention]
  └── /reflect (Taskly)                   [convention]
          ↓
     Orchestrator aggregates               [convention]
          ↓
       mem_add
     (feedback / antipattern / project / current_focus)
          ↓
     PostToolUse records last_accessed_at  [code, implicit]
          ↓
   /reflect Step 3.1/3.5: evidence check   [convention]
     → mem_boost (citation + cue), mem_link confirms/contradicts/supersedes
          ↓
   /reflect Step 6: mem_dream (every run)  [convention]
     → compresses, merges, deletes
     → ADD proposals with higher target    → propagation candidates
          ↓
     Orchestrator confirms propagation     [convention]
          ↓
     mem_add to workspace / global         [code]
          ↓
   global / workspace / repo.<name>
```

---

## Comparison: The Broader Field

A full competitive analysis (MemPalace, claude-mem, mcp-memory-service, OB1) is maintained in [docs/ai-mem-vs-memPalace.md](ai-mem-vs-memPalace.md).

## Comparison: OB1 + OpenClaw vs. ai-mem framework

| Dimension | OB1 + OpenClaw | ai-mem framework |
|---|---|---|
| Who drives memory? | The user (weekly review, manual capture) | The agent (Taskly after every task) |
| Feedback loop | None — capture only | Evidence edges + Taskly (explicit) |
| Consolidation | None | Dreaming Agent (manual trigger today, auto-trigger planned) |
| Knowledge hierarchy | Flat collections | global → workspace → repo (subagent: convention) |
| Expert agents | Not modeled | Convention-based pattern, no code schema |
| Junior → Senior effect | Not achievable structurally | Built into the loop (evidence edges + dream) |

OB1 is a **capture tool**. The ai-mem framework is a **learning system**. The difference is not the storage backend — it is whether there is a feedback loop that closes.

## Comparison: BMAD vs. ai-mem framework

[BMAD](https://github.com/bmad-code-org/BMAD-METHOD) (Breakthrough Method for Agile AI-Driven Development) structures a role pipeline: an Analyst/PM/Architect agent produces a PRD and Architecture doc, a Scrum-Master agent shards these into Story files with fully embedded context, and a Dev agent implements from a story. This is strong context engineering *within* a single delivery pipeline — the Dev agent never needs to know the whole project, only its story.

| Dimension | BMAD | ai-mem framework |
|---|---|---|
| Unit of memory | Story file (generated once, complete, linear handoff) | Knowledge graph (cumulative, cross-session) |
| Update mechanism | Fixed role/template per pipeline stage | Judgment during `/reflect` (cite/confirm/contradict/supersede) |
| Maturity/trust signal | None — a doc is current or replaced (versioning) | Evidence edges (`confirms`, `contradicts`, `supersedes`) — a reader can check *why* to trust an entry; no score |
| Contradiction/staleness | Not modeled | `supersedes` edge — old entry stays readable, flagged, not deleted |
| Scope solved | Context loss *within* one pipeline run | Continuity of judgment *across* tasks and sessions (Junior → Senior effect) |
| Team distribution | Git-native — files travel with any clone/pull, no extra infrastructure | Local-only per machine (`AI_MEM_PATH`, default `~/.local/share/ai-mem`); `workspace`/`subagent.*` collections are logical namespaces inside one local DB, not physically shared |

BMAD is a **delivery framework** with good per-task context engineering. The ai-mem framework is a **learning system** that accumulates organized experience across tasks — the same distinction drawn against OB1 above, on a different axis (task handoff vs. temporal continuity).

**Why continuity is not just nice-to-have:** BMAD's context engineering solves context loss by front-loading everything a story needs into that story's own document — but "everything" has to be re-derived and re-written by the PM/Architect/SM agents every time, since nothing persists past the story boundary. A convention, a past incident, a domain constraint that doesn't change often still gets re-authored into each new story at full token cost. A persistent, judgment-curated substrate (ai-mem) lets that knowledge be written once and pulled by id or query when relevant, instead of re-derived per story. This is also *where* the Junior → Senior effect has to live: BMAD's role personas are static templates that don't accumulate project-specific competence between stories — a story file has no lifecycle once it closes. The two are complementary rather than substitutable: BMAD can supply the structured pipeline while its agents write cross-story lessons into ai-mem at story close, so the next story (or another project, via `workspace`/`global`) inherits them instead of re-deriving them.

**Devil's advocate — this is a bet, not a guaranteed win:**
1. *The token saving is conditional on retrieval actually firing.* `eval_pull_gap_test_2026_09_20` found `mem_query` called 0 times across every gap case — only a direct id pointer in CLAUDE.md worked. If the retrieval trigger problem (still an open question in that entry) isn't solved, ai-mem pays write/maintenance cost (`/reflect`, `mem_dream`) and never cashes in the retrieval saving — pure overhead relative to BMAD's redundancy.
2. *BMAD's redundancy is a freshness guarantee, not just waste.* Re-deriving each story's context from the current PRD/Architecture doc means it cannot go stale. A persisted ai-mem entry can (`domain_direction_judgment_over_scores_2026_09_20`: "staleness beats bad ranking as a danger — cosine can't detect staleness, only judgment/supersede can"). The token saving is bought with the risk of an agent acting on an outdated entry that hasn't been flagged `supersedes` yet — a risk BMAD's re-derive approach structurally does not have.

The continuity argument only cashes out if (a) the retrieval trigger fires reliably and (b) curation discipline (dream/supersede) keeps pace with accumulation — both open, not solved, per the entries cited above.

**Team-scale gap — not a bet, a missing capability:** ai-mem's persistence lives at `AI_MEM_PATH` (`~/.local/share/ai-mem` by default — see README.md), per user, per machine, outside the repo. The `workspace`/`subagent.*`/expert-agent collections described under "Agent Teams" above are logical namespaces inside that one local database; they are *[convention]*, not a physically shared store — there is no sync/server component and no export/import command today. BMAD's artifacts (PRD, Architecture doc, Story files) are ordinary repo files: git-native distribution to every team member on clone/pull, no extra infrastructure required.

The naive fix — committing the ChromaDB directory into the repo — would trade this gap for a worse one. ChromaDB persists as SQLite plus binary vector-index segments, not text: committing it means no diff, no merge, and no PR-reviewable content (a reviewer can read a new `pattern:` line in a Markdown story; not a binary blob diff), plus repo bloat as the index rewrites on every embedding update. The correct fix would be a text-export layer — canonical entries serialized as JSON/Markdown into the repo (git-diffable and reviewable, like BMAD's own docs), with each local ai-mem instance rebuilding its vector index as a reproducible derivative on pull, since the index is a cache, not the source of truth. This layer does not exist yet.

Until it does, ai-mem's continuity benefit is scoped to the single developer running it locally, not the team. BMAD's plain-file approach already clears the team-distribution bar today, without further engineering.

**Precedent for the missing layer: `graphify`.** The text-export layer above is not hypothetical — a sibling tool in this same toolchain already builds it, for a different purpose. `graphify` (`~/.claude/skills/graphify/SKILL.md`) persists its knowledge graph entirely as text/JSON in a folder: `graphify-out/graph.json` (nodes/edges as plain JSON), `graphify-out/GRAPH_REPORT.md` (a Markdown audit report), and optionally `graphify-out/obsidian/` (one Markdown file per node — maximally git-diffable). Retrieval is graph traversal (BFS/DFS via `graphify query`), not cosine similarity — no vector index sits between the text and the answer. This confirms the file/folder pattern is buildable and already production-proven in the same ecosystem, not a design fantasy.

It is not, however, a substitute for ai-mem — it solves a different problem. `graphify` extracts a graph *from an existing corpus* (code, docs, papers) under an explicit honesty rule ("never invent an edge"): it can only represent what is already written somewhere and re-derives it on `--update` when the corpus changes — structurally closer to BMAD's "re-derive fresh from the source" philosophy than to ai-mem's "accumulate judgment that isn't written anywhere else." `graphify` has no confidence lifecycle, no boost/decay, no `/reflect` ritual, and no supersede-by-agent-judgment — an agent's lesson from a failed approach, or a `/reflect` outcome, exists nowhere in the corpus for it to extract. The right conclusion is not "graphify replaces ai-mem" but "ai-mem's storage layer should move from ChromaDB to a graphify-like text/JSON format, while the epistemic layer (confidence, reflect, judgment-driven supersede) stays on top — no extraction tool can supply that layer, because its content doesn't exist as text until an agent writes it."

**A closer precedent: ADRs.** Architecture Decision Records are an even tighter structural match than graphify, because they capture the same *content* ai-mem's `domain` type does, not just a different storage shape for corpus facts. An ADR's Status/Context/Decision/Consequences maps almost directly onto `domain`'s `Decision: / Why: / Scope:`; one Markdown file per decision, sequentially numbered, git-versioned, PR-reviewable; a "superseded by ADR-0034" note in an old file is the same concept as ai-mem's `supersedes` edge, just expressed as prose instead of a typed edge. The gap between an ADR and an ai-mem `domain` entry is the storage medium, not the semantics. This suggests a concrete shape for the missing layer, tighter than a generic text/JSON export: persist `domain` (and plausibly `pattern`/`anti-pattern`) entries as ADR-style Markdown files in the repo, with ChromaDB reduced to a locally-regenerable semantic index built over those files rather than the source of truth.

Caveat (this is still an architecture proposal, not a working system): moving storage format does not by itself fix the retrieval-trigger problem (`eval_pull_gap_test_2026_09_20` — `mem_query` called zero times in every gap case; only a direct id pointer worked), and the confidence lifecycle sits awkwardly on top of ADRs — ADRs are effectively immutable once accepted (superseded by a new one), while `mem_boost` mutates confidence/`access_count` far more often (`current_focus` alone: `access_count` 183) than a sane git-commit cadence would tolerate. Team here means both human collaborators (potentially on separate machines) and the agent team on a single machine — with humans in the mix, the local-storage gap is real, not hypothetical, which is why this migration is worth doing despite the two open problems above, not because they're solved.

## Synthesis: three layers, not one framework

The comparison converges on a three-layer picture rather than a single winning framework:

1. **Planning artifacts** (BMAD's PRD/Architecture/Story, or spec-driven development's spec-first flow) — git-native, team-visible, regenerated fresh per delivery cycle. Spec-driven development belongs in this same family as BMAD, not a separate axis: spec-first, code kept in sync with the spec, plain text, reviewable.
2. **Decision records** (ADR-style Markdown for what ai-mem calls `domain`, and plausibly `pattern`/`anti-pattern`) — git-native, one file per decision, superseded rather than edited.
3. **The epistemic mechanism** (`/reflect`/Taskly + records + evidence edges + a librarian agent on probation; replaced the confidence lifecycle 2026-09-26) — what actually produces a **"Projektbegleitender Entwickler"**: an agent whose judgment about layers 1 and 2 matures over time (linked `confirms` when borne out, `contradicts` when wrong, `supersedes` when overtaken), rather than a fresh agent re-deriving everything each cycle.

None of the three substitutes for another. Layers 1 and 2 can be produced by BMAD, spec-driven development, or plain ADR practice — all convention, all git-native, all already proven outside ai-mem. Layer 3 is what none of them supply: a lifecycle mechanism that operates independently of any single artifact's text. That is ai-mem's one irreplaceable contribution — but it is also the layer that most depends on layers 1 and 2 being durable and team-visible, since a judgment about a document nobody else can read does not accumulate into shared expertise.

**What "ai-mem" actually is, restated (user observation, 2026-09-25):** this whole comparison points at a reframing of ai-mem itself, not just of what it competes with. The project's real substance is the framework/specification — when `/reflect` runs, how confidence moves, how collections nest, when `mem_dream` links vs. supersedes — and that specification already lives almost entirely as text: Skill prompts (`skills/reflect.md`), hook code (`hook.py`, `posttool_hook.py`), agent conventions (Orchestrator-as-writer, `[retro]` blocks). ChromaDB is the swappable part — today's storage backend for whatever the framework decides to write, not the framework itself. The "Projektbegleitender Entwickler" from the synthesis above is the personification of the framework (layer 3), not of the database. The database was never the interesting part; it is just the most concrete, most visibly bounded artifact (local, binary, not team-shareable) — which is exactly why this whole discussion kept circling it, while the framework stayed comparatively invisible despite being the actual value. This reframes the ADR migration itself: it changes nothing about the framework's conventions, only what the framework writes to.

---

## What This Is Not

- Not a model fine-tuning approach — the model weights do not change
- Not a RAG system — there is no document corpus, only structured experience entries
- Not a rule engine — rules emerge from reflection, they are not hand-coded

The framework is epistemological: it concerns how knowledge is acquired and structured, not what the knowledge is about. It applies equally to coding agents, writing teams, marketing teams, and executive decision-making groups.

---

## Implementation Status Summary

| Feature | Status |
|---|---|
| ChromaDB storage, TTL, typed entries | Implemented |
| BM25 hybrid retrieval | Implemented |
| Adaptive MLP re-ranker (`[10→32→16→1]`) | Removed 2026-06 |
| Confidence lifecycle (`confidence`/`access_count`) | Removed 2026-09-26 — replaced by evidence edges (`confirms`) + librarian |
| `mem_boost` (citation + `cue`), `[available]` gate (`boost_count ≥ 1`) | Implemented |
| Typed causal edges (`mem_link`, `mem_edges`) | Implemented |
| Librarian retrieval agent (`examples/agents/librarian.md`) | Prototype on probation — measured 5/6 on the gap-test cases, no fixed call point yet (`eval_librarian_2026_09_26`) |
| PostToolUse passive `last_accessed_at` timestamp | Implemented |
| `SessionStart` push (focus text, `[available]`, deltas, git commits) | Opt-in (`session_start_verbose: true`) — routing-only by default since 2026-09-16 |
| `UserPromptSubmit` / `PreToolUse` push hooks | Removed 2026-09 — see `docs/hooks.md` |
| Split-hint detection | Implemented |
| `mem_split` (manual) | Implemented |
| `mem_dream` (manual trigger) | Implemented |
| Outcome signal via `/reflect` Step 3.1 | Convention — `mem_boost` citation + `mem_link confirms` on entries borne out |
| `mem_dream` trigger via `/reflect` ritual | Convention — after every `/reflect`, scoped to the active collection (by design — hook placement causes subagent chain problem) |
| Upward propagation via `/reflect` Step 6 | Convention — `mem_dream hier` surfaces candidates, Orchestrator confirms |
| `/reflect` Taskly ritual | Convention (Skill prompt) |
| `[retro]` block parsing | Convention (LLM reasoning) |
| Orchestrator-only write constraint | Convention |
| Expert-agent collection schema, wiring | Convention — see `examples/agents/` for a starting template |
| `subagent.*` auto-detection | Not implemented (transcript-signature matching via `agents.yaml` gets a custom agent type recognized, not the collection itself) |
