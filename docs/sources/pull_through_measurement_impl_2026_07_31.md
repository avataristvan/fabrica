---
type: measurement
date: 2026-07-31
origin: memory entry pull_through_measurement_impl_2026_07_31, exported to docs/reference/ on 2026-10-04
status: processed
---

## What the source says

# Pull-Through-Messung implementiert (2026-07-31)

Umsetzung des Datenerhebungsschritts aus arch_decision_push_vs_pull_2026_07_31, Punkt 6 (Schicksal von userprompt_hook wird erst nach echten Nutzungsdaten entschieden, nicht geraten). Committed als b13d4d0 (Hauptimplementierung) + fddfa9d (Fix: session_stats.json-Pfad war ebenfalls von der im Gotcha unten beschriebenen Bugklasse betroffen, im selben Zug korrigiert).

## Mechanik
- Neues Modul `ai_mem/injection_log.py`: `record_pushed(log_path, collection, ids)` loggt jede von userprompt_hook gepushte ID pro Collection ({DB_PATH}/injection_log.json, JSON {id, ts}, capped 500/Collection).
- `userprompt_hook.py` ruft record_pushed für alle drei Blöcke auf (dilemmas, warnings, available) -- collection-Zuordnung folgt der bestehenden coll-Variable pro Ergebnis.
- `dream_memory._pull_through_report(entries, log_path)`: gleicht das Log gegen `last_accessed_at` jedes Entries ab -- pulled = last_accessed_at > push_ts. Gelöschte Entries (nicht mehr auflösbar) werden aus Zähler UND Nenner ausgeschlossen, nicht als 'nicht gepullt' gewertet -- das Log kann 'nie genutzt' nicht von 'nicht mehr feststellbar' unterscheiden.
- Gerendert als eigener Report-Abschnitt in mem-dream (analog zu _confidence_report), aktiviert via `DreamMemoryUseCase(repo, injection_log_path=...)` in dream_cli.py.

## Warum kein Live-Zähler
Erste Idee war ein Rolling-Counter analog zu session_stats.py, der bei jedem track_access-Ereignis hochzählt. Verworfen: das Ergebnis eines Push-Events ('wurde später gepullt') ist zum Push-Zeitpunkt noch nicht bekannt -- ein Live-Zähler kann nur True-Treffer festhalten, nie das Ausbleiben. Also: Log der Push-Events + Report, der später (bei jedem mem-dream-Lauf) gegen last_accessed_at abgleicht, statt Instrumentierung an den drei TrackAccessUseCase-Konstruktionsstellen (server.py, daemon.py, _hook_deps.py). Generalisiert als pattern_delayed_outcome_needs_log_not_counter in global.

## Gotcha beim Bauen
Modul-Level-Konstante `X = DB_PATH / "..."` in einem Hook lässt sich in Tests nicht patchen -- `patch.object(hook, "DB_PATH", tmp_path)` wirkt nur auf Code, der den Namen DB_PATH zur Laufzeit nachschlägt, nicht auf eine beim Import bereits berechnete separate Konstante. Fix: Pfad inline in main() berechnen, nicht als Modul-Konstante hochziehen. `_STATS_PATH` in userprompt_hook.py hatte denselben Bug -- im selben PR (fddfa9d) mitgefixt.

## Status (final, 2026-09-13) -- Infrastruktur ist jetzt TOT
Log blieb bei 281 Push-Events über 5 Collections eingefroren (global:184, repo.ai-mem:30, repo.project-a:7, repo.workspace:17, repo.project-b:43) -- und wird nicht mehr wachsen: record_pushed's einziger Aufrufer war userprompt_hook.py, das am 2026-09-13 komplett entfernt wurde (arch_decision_userprompt_push_removed_2026_09_13). Die geplante Pull-Through-Raten-Auswertung (arch_decision_push_vs_pull_2026_07_31 Punkt 6) wurde NIE durchgeführt -- die Frage, die diese Infrastruktur beantworten sollte, wurde stattdessen durch einen unabhängigen Vorfall aufgelöst (userprompt_hook einfach komplett entfernt, aus einem anderen Grund). `injection_log.py`, `_pull_through_report` und dieses Modul bleiben im Code, sind aber jetzt tote Infrastruktur, die eine Frage beantwortet, die niemand mehr stellt.

## Our notes

