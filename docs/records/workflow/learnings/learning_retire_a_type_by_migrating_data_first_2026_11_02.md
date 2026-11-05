type: learning
topic: workflow
perspective: user
created: 1793657747.814631
cue: I plan to retire a record type or format and weigh a compatibility layer against migrating the data first.
---

Observed: After the 98 todo records in 14 areas were migrated into BACKLOG.md files, retiring type todo in code needed no compatibility path (no legacy reader, no doctor finding for leftovers). The planned "read old, reject new" design became a plain removal with a lint hint: 56 insertions, 97 deletions in ai_mem+tests.
Cause: With no old data left, nothing had to be read, so no compatibility code was needed (user's judgment from the work).
Evidence: fabrica a51e451; migration commits ai-architecture ec84bb3, galaxy-tab-a-2016 592f1b2, ExoDeck b7c44bd, WokTuna 44d491c; decision [domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02](../decisions/domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02.md).

## Edges

- related: [domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02](../decisions/domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02.md)
