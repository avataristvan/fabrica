# Tutorial: your first records

You will create an area, write a decision and the learning it rests on, link them, set a focus, and check the result with `mem lint` and `mem doctor`. It takes about ten minutes and needs only `mem` on your path (see the install section of the [README](../../README.md)). Nothing here touches a project you care about: use a scratch folder.

## 1. Make an area

An area is any folder that has `docs/records/`.

```bash
mkdir -p demo/docs/records && cd demo
mem context
```

`mem context` prints the area root, the records directory and the paths of `INDEX.md` and `FOCUS.md`. Every `mem` command from here on works on this area, because it is the nearest ancestor of your working directory with `docs/records/`.

## 2. Write a decision

```bash
mem add --id domain_use_postgres_2026_10_12 --type domain --topic data \
  --text "Decision: use Postgres. Why: the team knows it. Scope: the backend."
```

`mem` prints `added domain_use_postgres_2026_10_12`. Look at what it wrote:

```bash
find docs -type f
cat docs/records/data/decisions/domain_use_postgres_2026_10_12.md
```

The record is a Markdown file at `<topic>/<kind>/<id>.md`: the topic `data` you gave it, the kind `decisions` that the type `domain` maps to. You could have created that file by hand; `mem` just keeps the format right ([record format](../reference/record-format.md)).

## 3. Say when it helps

A `cue` is the situation in which the record would help. The librarian agent matches against it.

```bash
mem add --id domain_use_postgres_2026_10_12 --cue "choosing a database for a new service"
```

Because the id exists, only the field you gave changes.

## 4. Write the learning it rests on, and link them

```bash
mem add --id learning_pg_pool_2026_10_12 --type learning --topic data \
  --text $'Observed: 20 connections were exhausted under load.\nCause: no connection pooler.\nEvidence: load test of 2026-10-12'

mem link domain_use_postgres_2026_10_12 learning_pg_pool_2026_10_12 --type derived_from
```

A decision points at the learning it rests on with a `derived_from` edge, stored on the decision.

## 5. Set the focus

```bash
mem add --id current_focus --text "Setting up the backend."
cat docs/records/FOCUS.md
```

`FOCUS.md` is state, not a record: plain text that is overwritten in place.

## 6. Check it

```bash
mem lint       # checks the area's record files; prints "clean" and exits 0
mem doctor     # diagnosis of the whole practice; changes nothing
```

`docs/records/INDEX.md` was generated for you: a catalogue the librarian reads first. `mem doctor` will also tell you that the area is not under version control, and which of your agents and skills do not yet ask the librarian.

## Where next

- Let an agent read these records at the right moment: [wire skills and agents](../how-to/wire-skills-and-agents.md).
- Everyday tasks (supersede, move, adopt hand-written records): [manage records](../how-to/manage-records.md).
- Why it works this way: [Organisational memory](../explanation/organisational-memory.md).
- Every command and flag: [command-line reference](../reference/cli.md).
