id: domain_direction_judgment_over_scores_2026_09_20
type: domain
created: 1789925427.11298
edges: [{"target_id": "eval_pull_gap_test_2026_09_20", "edge_type": "related"}, {"target_id": "pattern_confidence_lifecycle", "edge_type": "related"}, {"target_id": "todo_retrieval_confidence_gradient", "edge_type": "supersedes"}]
---

Decision: Richtung für ai-mem (2026-09-20): Urteil statt Score. Der epistemologische Rahmen (Taskly, /reflect, [retro], Konvention) ist der wertvollste Teil; mechanische Scores sollen ihn nicht ersetzen oder untergraben.
1. Signale, die Einträge schützen, reifen oder vergessen lassen, kommen aus Urteilen (/reflect, mem_boost, begründetes DELETE), nicht aus mechanischen Zählern. access_count aus dem PostToolUse-Dateinamen-Treffer (Cosine >= 0.5) ist Diagnose, kein Schutz- oder Reifesignal.
2. mem_dream wird als Einordnen verstanden, nicht als Aufräumen: neue Erfahrung zu bestehenden in Beziehung setzen (Kanten, Widerspruch, Verallgemeinerung, Geltungsbereich, Überholtes markieren), Ungelöstes als Spannung (dilemma) stehen lassen. Das Aktionsvokabular braucht dazu LINK und SUPERSEDE.
3. Cosine/BM25 ist Kandidatenwerkzeug, kein Relevanzmaß: keine Score-Schwelle, keine Rankingsignale aus Confidence/access_count im Abruf. Der Agent urteilt, was im aktuellen Kontext gilt.

Why:
- Nutzerprinzip: der echte Rank ist der aktuelle Kontext (was ist hier und jetzt relevant); ein kontextfreier Skalar pro Eintrag widerspricht dem. Der MLP-Ranker wurde aus demselben Grund ausgebaut.
- Nutzerbild: Ranking nach Häufigkeit/Intensität hat etwas von Trauma — was oft oder stark gefeuert hat, verfestigt sich unabhängig davon, ob es im Kontext stimmte. Mechanismus im Code (Stand 2026-09-20): der Dream-Prompt schützt access_count >= 5 als 'load-bearing' vor DELETE/MERGE; mem_cleanup löscht nach last_accessed_at; PostToolUse bumpt Einträge, deren Text dem Dateinamen der editierten Datei ähnelt (Namensnähe ist kein Nutzen).
- Nutzerbild für Dream: wie Träumen bei Lebewesen — verarbeiten und einordnen, nicht komprimieren.
- Die Framework-Doku sagt es selbst: 'Automation would give the agent more signals. Convention gives it better ones.' Das mechanische Signal widerspricht diesem Grundsatz.
- Messung (eval_pull_gap_test_2026_09_20, plus Probe an 11 Queries): Cosine ist nur bei Vokabular-Überlappung brauchbar, eine Schwelle trennt Richtiges nicht von Rauschen (0.20 für richtigen Eintrag, 0.26 für Nonsense-Query), Confidence beeinflusst die Reihenfolge ohnehin nicht. Die Scores wirken vor allem in der Pflege, also dort, wo sie Urteile ersetzen.
- Korrektur an der ursprünglichen Idee 'Agent urteilt über Kandidaten': der eigentliche Engpass ist der Auslöser, nicht das Ranking. In allen Gap-Fällen wurde 0-mal mem_query aufgerufen; erfolgreich war nur der ID-Pointer im CLAUDE.md. Ein Agent urteilt nur über Vorgelegtes.
- Aktualität schlägt Ranking: Veraltetes ist gefährlicher als schlecht Gerankstes (Beispiel: docs/friction-and-research.md markiert _ranker_signal() als Done, das es nicht mehr gibt). Cosine kann Veraltetes nicht erkennen; Einordnen (superseded markieren) kann es.

Scope: gilt für die Architektur von ai-mem (Abruf, Confidence-Lifecycle, mem_dream, mem_cleanup, PostToolUse-Tracking). Gilt nicht für die Grundstruktur (ChromaDB, typed Entries, kausale Kanten, Collections-Hierarchie), die bleibt. Umsetzung erfolgt chunkweise; der jeweilige Stand steht im Commit, nicht in diesem Eintrag. Offene Kernfrage: welcher Mechanismus löst den Abruf aus, wenn keine ID im Kontext steht (siehe eval_pull_gap_test_2026_09_20). Vor der Umsetzung prüfen: mem_cleanup-Vergessen nach last_accessed_at braucht dann ein Urteilskriterium statt Zugriffsrecency.