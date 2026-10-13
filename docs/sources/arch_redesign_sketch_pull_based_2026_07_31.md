---
type: design-doc
date: 2026-07-31
origin: memory entry arch_redesign_sketch_pull_based_2026_07_31, exported to docs/reference/ on 2026-10-04
status: processed
---

## What the source says

Status-Nachtrag (2026-09-29): Zwei Aussagen im Status-Block unten wurden später umgekehrt -- Punkt 1 (userprompt_hook löschen), hier als ABGELEHNT vermerkt, wurde am 2026-09-13 doch umgesetzt (arch_decision_userprompt_push_removed_2026_09_13); Punkt 5 (PreToolUse behalten) wurde am 2026-09-12 verworfen, PreToolUse komplett entfernt (arch_decision_pretool_push_removed_2026_09_12). Punkte 2-4 und 6 bleiben gültig. chunk2_available_format_mem_topics_shipped_2026_07_31 ist in arch_decision_push_vs_pull_2026_07_31 aufgegangen.

# Konkreter Pull-basierter Redesign-Vorschlag (Opus, 2026-07-31) -- Referenz, Entscheidung bereits getroffen

Ausgangspunkt: die Pull-Leiter existiert in server.py bereits (mem_list -> Collections+Counts, mem_list(collection) -> {id,title}-Paare, mem_get(ids) -> voller Text ohne Ranking) -- analog zu einem bestehenden MCP-Muster (list_tool_categories -> list_tools_in_category -> get_tool_signature). Push wurde AUF ein bereits funktionierendes Pull-System draufgebaut, nicht statt eines fehlenden.

## Vorschlag (7 Punkte, unverändert aus dem Original-Report)
1. `userprompt_hook`-Injection komplett löschen (nicht nur tunen) -- Begründung: der Richter (isolierter Prompt-String ohne Task-Kontext) ist strukturell schlechter informiert als der Agent selbst, und das Scoring-Gate war beweisbar wirkungslos (siehe l2/BM25-Bug, jetzt gefixt).
2. SessionStart behalten, aber auf einen Index verkleinern, nicht Inhalt -- current_focus + Git-Commits + Collection-Namen + Titel-Index, nicht Entry-Bodies.
3. `[always-present]` durch `[available]` ersetzen -- nur Titel+IDs zeigen, `mem_get` ist einen billigen Call entfernt falls gebraucht.
4. `mem_topics(collection)` ergänzen -- die fehlende `list_tools_in_category`-Sprosse; Titel clustern/taggen, damit auch eine 300-Einträge-Collection browsable bleibt.
5. PreToolUse behalten, aber fixen und als einzigen aktions-getriggerten Push-Punkt begründen -- Trigger ist eine konkrete Handlung (Datei X wird editiert), nicht ein vager Prompt-String.
6. Scoring unabhängig von der Architektur-Entscheidung fixen (l2/cosine, BM25-Restbug).
7. `access_count` entweder bedeutsam machen (nur hochzählen wenn Agent bewusst per ID `mem_get`-t oder in /reflect zitiert) oder fallen lassen.

## Sonnets Vorbehalt zu diesem Vorschlag
Nicht 1:1 übernehmen ohne Blindtest-Ergebnis einzubeziehen (siehe pattern_gap_test_evaluation) -- der Blindtest zeigte ein nuancierteres Bild als 'Pull schlägt Push immer'. Empfehlung: schrittweise umsetzen, nicht als ein großer Rewrite.

## Status (2026-07-31, Ende der Session)
Die Entscheidung ist getroffen (siehe arch_decision_push_vs_pull_2026_07_31): Punkte 2-6 wurden übernommen und sind umgesetzt (chunk1_daemon_shipped_2026_07_31, chunk2_available_format_mem_topics_shipped_2026_07_31, chunk3_access_count_semantics_shipped_2026_07_31, bm25_saturating_transform_final_2026_07_31). Punkt 1 (userprompt_hook komplett löschen) wurde ABGELEHNT -- der Blindtest sprach dagegen. Dieser Eintrag ist historische Referenz für Opus' Originalvorschlag, kein offener Arbeitsposten mehr.

## Our notes

