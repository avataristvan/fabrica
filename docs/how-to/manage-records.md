# How to manage records

Everyday tasks with the `mem` CLI. Every command acts on the nearest area of the working directory (`--area PATH` overrides). Flags: [command-line reference](../reference/cli.md).

## Supersede an outdated record

Write the new record, then mark the old one as overtaken instead of deleting it:

```bash
mem add --id domain_new_choice_2026_10_12 --type domain --topic data --text "Decision: ..."
mem link domain_new_choice_2026_10_12 domain_old_choice_2026_09_01 --type supersedes
```

The old record keeps its reasoning and is flagged with `superseded_by`. Supersede inside one area: `supersedes` across areas is refused, so supersede in the target area's own session.

## Confirm or contradict

When a later record bears out an earlier one, link `--type confirms` (later -> earlier). Three incoming confirms make the earlier record a candidate for a sharper `cue`, which `mem doctor` shows. A record that argues against another uses `--type contradicts`; link an anti-pattern to the pattern it contradicts, and the librarian surfaces both together.

## Link across areas

```bash
mem find some_id --root ~/workspace                  # where does the id exist?
mem link my_record some_id --type related --to-area ../other-area
```

`mem find` prints the reference `mem link` accepts (`<relative-area-path>:<id>`); `mem link` never qualifies a target for you.

## Move records to the area where they belong

```bash
mem move id1 id2 --to-area ../other-area --dry-run   # read the plan
mem move id1 id2 --to-area ../other-area
```

Edges are re-qualified and referrers in the source area rewritten; referrers elsewhere are only reported. Many records between many areas: `mem move --batch plan.tsv --dry-run`. Run moves only on versioned areas.

## Adopt hand-written records

Records may be written by hand or by another tool. To bring an area into the canonical form:

```bash
mem lint            # read the findings
mem lint --fix      # normalise frontmatter and regenerate INDEX.md
```

`--fix` never touches a body, and refuses a file when its preservation guard cannot prove nothing is lost. While an area's `INDEX.md` is hand-kept or stale, `mem add`, `link`, `delete` and `move` refuse until you have run `mem lint --fix`.

## Attach evidence

Put dated evidence in `docs/sources/<slug>.md` (format: [record format](../reference/record-format.md#sources)), then name it in the learning:

```bash
mem add --id learning_x --type learning --topic tools \
  --text $'Observed: ...\nCause: unknown\nEvidence: docs/sources/<slug>.md'
```

Never edit the body of a source afterwards. `mem doctor` lists sources that no record points to.

## Delete a record

```bash
mem delete ID...
```

Ids are required; a delete without ids is refused. Prefer superseding to deleting: a wrong decision keeps its reason.

## Review the whole practice

```bash
mem doctor --root ~/workspace      # every area below the root
```

Read the Records, Sources, State, Wiring and Effect sections; each names what to do. The SessionStart hook reminds you when the last run is older than 14 days.
