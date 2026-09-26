---
name: reflect
description: "Lightweight end-of-session standup. Run after completing a task or todo. Closes the Plan → Code → Reflect loop. Subagents: always append a [retro] block at the end of your response (learned: / blocked: / next:)."
---

Lightweight end-of-session standup. Run after completing a task or todo. Closes the Plan → Code → Reflect loop.

The subagent summary is already the "done" — this adds only what matters beyond the code.

Use the active collection from the session context (e.g. `repo.ai-mem`).

---

## Step 1 — Collect

Scan subagent return values for `[retro]` blocks (see convention below). Note any `learned:`, `blocked:`, and `next:` lines. No user input needed yet.

---

## Step 2 — My contributions first

Before asking the user, contribute your own observations:

- **Learned:** what was surprising, what assumption was wrong, what tool failed silently
- **Blocked:** what got in the way — missing tool, unclear requirement, wrong mental model
- **Next:** one or two todo suggestions based on what you saw

Flag each as **"Meine Beobachtung:"** so the user knows it's from the agent side.

---

## Step 3 — Two questions

Ask both questions together:

> **"Was hast du gelernt oder was hat dich überrascht?"**
> **"Was hat dich gehindert?"**

Wait for the user's answer. Store each learning or blocker immediately:

```
mem_add(
    documents=[<learning or blocker>],
    collection=<active>,
    type="feedback",
    ids=["feedback_<slug>"],
)
```

If a blocker describes a failed approach, store it as an anti-pattern instead:

```
mem_add(
    documents=["Tried: <approach>\nFailed because: <reason>\nInstead: <alternative>"],
    collection=<active>,
    type="anti-pattern",
    ids=["antipattern_<slug>"],
)
```

The `Tried:` field makes the entry self-retrieving — future queries about the same approach will surface it automatically without any special retrieval logic.

If what was learned is a generalizable rule — not tied to this project — store it as a pattern instead:

```
mem_add(
    documents=["Rule: <the rule>\nWhen: <context where it applies>\nWhy: <invariant it enforces>"],
    collection=<active>,
    type="pattern",
    ids=["pattern_<slug>"],
)
```

The `Rule:` structure makes the entry scannable during dream consolidation and prevents it from being incorrectly merged with the anti-pattern it replaces.

Skip if the user has nothing to add.

---

## Step 3.1 — Citation & Cue

Schau zurück auf die Session: welche aus dem Kontext-Hook eingespielten Memories waren **entscheidend** — haben eine Entscheidung verändert, einen Fehler verhindert, oder nicht-offensichtlichen Kontext geliefert?

Für jede entscheidende Memory (das ist das Zitier-Signal — `mem_boost` erhöht nur noch `boost_count` und setzt optional den Cue, es liest oder schreibt keine Confidence mehr):

```
mem_boost(
    ids=["<memory_id>"],
    collection=<active>,
)
```

War eine Memory falsch oder irreführend? Dann nicht decayen — das Vertrauenssignal ist eine nachvollziehbare Kante, kein Punktabzug:

```
mem_link(source_id="<neuere_id>", target_id="<memory_id>", edge_type="contradicts", collection=<active>)
```

oder, wenn eine neuere Erkenntnis sie ersetzt:

```
mem_link(source_id="<neuere_id>", target_id="<memory_id>", edge_type="supersedes", collection=<active>)
```

Hat eine in dieser Session neu gespeicherte Erkenntnis (z. B. aus Step 2 oder 3.5) eine bestehende Memory bestätigt — nicht nur benutzt, sondern nachweislich wieder zugetroffen? Dann verlinke sie mit `confirms`:

```
mem_link(source_id="<neue_id>", target_id="<memory_id>", edge_type="confirms", collection=<active>)
```

`confirms` braucht einen echten zweiten Eintrag als Beleg; wurde in dieser Session nichts Neues dazu geschrieben, reicht der Citation-Boost oben.

Die Memory-IDs stehen im `[ai-mem]`-Kontext vom Session-Start. Überspring diesen Schritt still wenn keine Memories eingespielt wurden oder keine davon den Unterschied gemacht hat.

### Cue: in welchem Moment hätte dir das geholfen?

Der Erfahrungsindex im `[ai-mem]`-Kontext ("Situation → Eintrag") besteht nur aus Einträgen mit Cue. Frag dich bei jeder Erkenntnis, die du in dieser Session gewonnen oder bestätigt hast: **In welcher Situation hätte ich das gebraucht, ohne zu wissen, dass ich danach fragen muss?** Formuliere die Situation aus der Sicht dessen, der noch nichts weiß (was er gerade tut oder vorhat), nicht als Stichwort der Lösung.

```
mem_boost(
    ids=["<memory_id>"],
    collection=<active>,
    cue="bevor ein fremder Branch gemergt wird",   # ein Satz, max. 140 Zeichen
)
```

Nur was du wirklich in einer Situation wiederfinden würdest, bekommt einen Cue: der Index hat einen festen Rahmen und lebt davon, klein zu bleiben. Ist ein Cue überholt oder falsch, entferne ihn mit `cue=""`. Überholte Einträge (`supersedes`) verschwinden von selbst aus dem Index.

---

## Step 3.5 — Feedback signal

**Outdated or misleading entries (always, no commit needed)**

Review the conversation: were any retrieved memories outdated, misleading, or contradicted by reality?

For each: reform in place as anti-pattern — the content change is the signal, no ranker label needed:

```
mem_add(
    documents=["Tried: <original claim>\nOutdated/wrong because: <reason>\nInstead: <what is true now>"],
    ids=[<original_id>],
    collection=<active>,
    type="anti-pattern",
)
```

Completely wrong with no useful lesson → `mem_delete` instead.

Skip silently if nothing was outdated.

---

## Step 4 — Next todos

Aggregate next-todo suggestions:
- Your own (from Step 2)
- Any `next:` lines from `[retro]` blocks
- The user's ideas (if any from Step 3)

Present them as a short list. Do not store automatically — ask which ones to keep:

> **"Welche davon sind relevant?"**

Store confirmed todos:

```
mem_add(
    documents=[<todo>],
    collection=<active>,
    type="project",
    ttl_days=14,   # optional, adjust per todo
)
```

---

## Step 4.5 — Expert propagation

**A: Subagent retros** (only if `[retro]` blocks were found in Step 1)

For each subagent that contributed a `learned:` line, decide: is this learning about **how to approach a problem** (technique, process, pattern) — or about **what was done in this project** (specific decision, project fact)?

- Process/technique → candidate for the expert collection
- Project-specific → stays in the project collection only

Ask for each candidate:

> **"Soll dieses Learning für `<agent-type>` cross-projekt gespeichert werden?"**

If yes:

```
mem_add(
    documents=[<learning text>],
    collection="subagent.<agent-type>",   # e.g. "subagent.the-coder"
    type="feedback",
    ids=["<agent-type>_<slug>"],
)
```

**B: Direct coding by orchestrator** (only if commits were found in Step 3.5 and no coding subagent was used)

Ask:

> **"Gab es in dieser Session transferierbare Coding-Grundsätze — Muster die in jedem Projekt gelten würden, nicht nur hier?"**

If the user names one or more, store each in the appropriate collection — `global` for universal principles, or a `subagent.*` collection if a coding agent exists in this setup:

```
mem_add(
    documents=[<principle>],
    collection=<global or subagent.*>,
    type="feedback",   # or "anti-pattern" / "pattern" as appropriate
    ids=["<slug>"],
)
```

Concrete signals to watch for: a fix that corrects a wrong mental model, a platform invariant, an architectural rule that held across layers.

Skip B silently if the session had no commits or was purely exploratory.

The expert collection accumulates across all projects. Over time it gives the agent genuine cross-project intuition — the same way a senior engineer recognizes patterns they've seen before, regardless of the specific codebase.

---

## Step 5 — Update current_focus

Ask: **"Was ist dein nächster Fokus?"** (or derive from the confirmed todos if obvious).

```
mem_add(
    documents=[<focus>],
    ids=["current_focus"],
    collection=<active>,
)
```

---

## Step 6 — Consolidation and propagation

After storing, silently run `mem_list` on the active collection and count entries.

**Consolidation:** If entry count **> 30**, or if `mem_query` returned split-hint warnings in this session:

> **"Die Collection hat X Einträge — soll ich das Gedächtnis konsolidieren? (`mem_dream`)"**

If yes, run dream in `hier` mode to see across all collections at once:

```
mem_dream(mode="hier", auto_delete=false)
```

Review the proposal with the user:
- DELETE / UPDATE / MERGE proposals → apply to the source collection with `mem_add` / `mem_delete`
- **LINK / SUPERSEDE proposals** → apply with `mem_link` (`related` / `contradicts` / `fixes` / `causes`, or `supersedes` with the newer entry as source), or let `mem_dream` do it via `auto_link=true` / `auto_supersede=true`. Prefer SUPERSEDE over DELETE when the old entry's reasoning is still worth reading; check the "Skipped" and "Merge Conflicts" sections of the report
- **ADD proposals where `target_collection` is higher than the source** (e.g. `workspace` or `global`) → these are **propagation candidates**: a pattern that proved universal across projects

For each propagation candidate, ask:

> **"Dieses Learning taucht in mehreren Projekten auf — soll es nach `[target_collection]` hochgestuft werden?"**

If yes:

```
mem_add(
    documents=[<entry text>],
    collection=<target_collection>,   # e.g. "workspace" or "global"
    type=<same type as source>,
)
```

The entry stays in the source collection too — propagation copies upward, it does not move.

If count ≤ 30 and no split hints: skip silently.

---

## Close

One sentence: what was stored + whether dream ran + whether anything was propagated. Example: "2 Learnings, 1 Blocker, 2 Todos, current_focus aktualisiert." or "… + 1 Learning nach `global` hochgestuft." Nothing else.

---

## [retro] convention for subagents

When spawning subagents for non-trivial tasks, add this to the end of their prompt:

> Am Ende deiner Antwort füge einen `[retro]`-Block hinzu:
> ```
> [retro]
> learned: <was überraschend war oder nicht funktioniert hat — oder "nothing">
> blocked: <was dich gehindert hat — oder "nothing">
> next: <Vorschlag für ein nächstes Todo — oder "nothing">
> ```

The main agent reads this block in Step 1 and surfaces it in Step 4. This makes subagent observations (silent fallbacks, tool failures, dead ends) visible without requiring transcript review.
