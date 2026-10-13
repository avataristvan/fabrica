id: pattern_attribute_records_by_created_timestamp_2026_10_12
type: pattern
area: records
perspective: archivist
created: 1791756536.500039
cue: I must assign an old the-coder record to a project but its text does not say which one
---

Rule: To attribute a the-coder record to its project when the text does not say, match its `created` timestamp against the commit days of the candidate projects.
When: redistributing records of the former `subagent.the-coder` collection.
Why: The-coder works in every project, so its records carry no project; the creation day usually coincides with commits of exactly one. Treat a day with commits in several projects as unresolved and ask.
