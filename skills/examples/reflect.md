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

Wait for the user's answer. Store each learning or blocker immediately — an observation is a `learning` (each entry becomes one record file; types without a file, like `feedback` or `project`, are rejected):

```
mem_add(
    documents=["Observed: <what happened or got in the way>\nCause: <root cause, or 'unknown'>\nEvidence: <test, commit sha or entry ids>"],
    collection=<active>,
    type="learning",
    ids=["learning_<slug>"],
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

If it is a choice or a business/domain reason (why something is the way it is), store it as a `domain` decision:

```
mem_add(
    documents=["Decision: <what was decided or is true>\nWhy: <reason>\nScope: <where it applies>"],
    collection=<active>,
    type="domain",
    area="<area, e.g. general, marketing>",   # optional, default "general"; ^[a-z0-9][a-z0-9_-]*$
    ids=["domain_<slug>"],
)
```

Every entry is a file under `docs/records/<area>/<kind>/` (`global`, `workspace` and `subagent.*` live in the records home, `ai-mem-records/<collection>/`).

If a decision (`domain`/`pattern`/`anti-pattern`) is derived from a learning, link it from the decision to the learning:

```
mem_link(source_id="<decision_id>", target_id="<learning_id>", edge_type="derived_from", collection=<active>)
```

Skip if the user has nothing to add.

---

## Step 3.1 — Citation & Cue

Schau zurück auf die Session: welche Records, die du gelesen hast (FOCUS.md, INDEX.md, eine Record-Datei, eine Antwort des Bibliothekars), waren **entscheidend** — haben eine Entscheidung verändert, einen Fehler verhindert, oder nicht-offensichtlichen Kontext geliefert? Das Vertrauenssignal ist eine nachvollziehbare Kante oder ein Cue, kein Zähler.

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

`confirms` braucht einen echten zweiten Eintrag als Beleg; wurde in dieser Session nichts Neues dazu geschrieben, reicht ein Cue (unten).

Überspring diesen Schritt still, wenn keine Records gelesen wurden oder keiner den Unterschied gemacht hat.

### Cue: in welchem Moment hätte dir das geholfen?

Der Cue steht als `cue:`-Zeile in der Record-Datei; der Bibliothekar sucht darüber nach "Situation → Eintrag". Frag dich bei jeder Erkenntnis, die du in dieser Session gewonnen oder bestätigt hast: **In welcher Situation hätte ich das gebraucht, ohne zu wissen, dass ich danach fragen muss?** Formuliere die Situation aus der Sicht dessen, der noch nichts weiß (was er gerade tut oder vorhat), nicht als Stichwort der Lösung.

```
mem_boost(
    ids=["<memory_id>"],
    collection=<active>,
    cue="bevor ein fremder Branch gemergt wird",   # ein Satz, max. 140 Zeichen
)
```

Nur was du wirklich in einer Situation wiederfinden würdest, bekommt einen Cue — ein Cue ist ein Versprechen, dass der Eintrag dann hilft. Ist ein Cue überholt oder falsch, entferne ihn mit `cue=""`.

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

Store confirmed todos — one file each under `docs/records/<area>/todos/`, several in one call:

```
mem_add(
    documents=["TODO: <first>", "TODO: <second>"],
    ids=["todo_<slug1>", "todo_<slug2>"],
    collection=<active>,
    type="todo",
)
```

A todo finished in this session is closed, not kept: `mem_delete` it and store a `learning` naming the commit sha (`Observed: … done in <sha>`).

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
    type="pattern",   # or "anti-pattern" / "learning" as appropriate
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
    type="pattern",   # or "anti-pattern" / "learning" as appropriate
    ids=["<slug>"],
)
```

Concrete signals to watch for: a fix that corrects a wrong mental model, a platform invariant, an architectural rule that held across layers.

Skip B silently if the session had no commits or was purely exploratory.

The expert collection accumulates across all projects. Over time it gives the agent genuine cross-project intuition — the same way a senior engineer recognizes patterns they've seen before, regardless of the specific codebase.

---

## Step 5 — Update current_focus

Ask: **"Was ist dein nächster Fokus?"** (or derive from the confirmed todos if obvious). It is written to `docs/records/FOCUS.md` and overwritten each time — git keeps the history, so no dates or status words that will rot.

```
mem_add(
    documents=[<focus>],
    ids=["current_focus"],
    collection=<active>,
)
```

---

## Step 6 — Einordnen (dream after every reflect) and propagation

Dream runs **after every /reflect**, scoped to the active collection — no size threshold, no trigger to detect. Whatever this session wrote, cited, linked or flagged (split hints, `contradicts`, `supersedes`) gets sorted in now, at the latest; small frequent runs instead of rare huge ones (an unscoped `hier` run once exceeded the CLI limit at 205k tokens).

```
mem_dream(
    collection=<active>,
    mode="hier",             # Haiku fast pass -> Sonnet synthesis; the heavy lifting is delegated
    auto_link=true,          # edges are additive
    auto_supersede=true,     # flags the old entry, keeps it readable
    auto_delete=false,
    focus_hint="Prioritize entries written, cited or linked in this session: <ids from Steps 3-5>. "
               "Check each against the rest: LINK (incl. confirms), SUPERSEDE, SPLIT if it carried a split hint.",
)
```

Then review only what was **not** auto-applied:
- **DELETE / MERGE** → list them compactly and ask once; apply the confirmed ones with `mem_delete` / `mem_add`. Prefer SUPERSEDE over DELETE when the old entry's reasoning is still worth reading
- **UPDATE / SPLIT** → apply after the same single confirmation; if there are several, delegate the mechanical `mem_add`/`mem_split` calls to a Haiku subagent (`Agent(model="haiku")`) with the exact actions
- Check the report's "Skipped" and "Merge Conflicts" sections
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

If the report proposes nothing beyond the auto-applied actions: skip the review silently.

---

## Close

One sentence: what was stored + what dream applied or left open + whether anything was propagated. Example: "2 Learnings, 1 Blocker, 2 Todos, current_focus aktualisiert." or "… + 1 Learning nach `global` hochgestuft." Nothing else.

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
