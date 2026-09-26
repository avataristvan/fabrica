id: pattern_triggers_beat_storage_and_ranking
type: pattern
created: 1790409909.376447
edges: [{"target_id": "eval_pull_gap_test_2026_09_20", "edge_type": "related"}, {"target_id": "eval_experience_index_ab_2026_09_21", "edge_type": "related"}, {"target_id": "domain_direction_judgment_over_scores_2026_09_20", "edge_type": "related"}]
---

Rule: Was einen Agenten zum Memory-Zugriff bewegt, ist ein ID-Pointer oder eine Situations-Cue im Kontext — nicht besserer Speicher oder besseres Ranking (Cosine, Hybrid, Confidence-Gewichtung).
When: Bevor Zeit in Retrieval-Verbesserung (Similarity-Formel, Hybrid-Search, Confidence-gewichtetes Ranking) statt in Auslöser-Mechanismen (CLAUDE.md-Pointer, Experience-Index/cue) investiert wird.
Why: eval_pull_gap_test_2026_09_20 fand in allen 7 Gap-Fällen 0 mem_query-Aufrufe; die 3 gelösten Fälle liefen ausschließlich über mem_get auf eine im CLAUDE.md genannte Entry-ID, nicht über Similarity-Suche (Cosine hit@1 nur 3/7 im Replay, und eine Score-Schwelle trennt Richtiges nicht von Rauschen — richtiger Treffer bei 0.20, Nonsense-Query bei 0.26). eval_experience_index_ab_2026_09_21 bestätigt die Richtung: mit einem SessionStart-Cue-Block griffen 3/3 vormals ungelöste Fälle (g2, g5, g6) direkt auf den Gold-Eintrag zu, gegenüber 1/3 in der Baseline ohne Index. domain_direction_judgment_over_scores_2026_09_20 zieht daraus die Architekturkonsequenz: Urteil (Boost/Cue/Supersede) statt mechanischer Score als Schutz- oder Reifesignal, weil der eigentliche Engpass der Auslöser ist, nicht das Ranking der Kandidaten.
Grenzen der Evidenz: n=1 pro Zelle, ein Modell, Selbstauskunft der Tool-Calls statt Instrumentierung, Cues wurden von demselben Agenten geschrieben, der die Testfragen kannte — das ist eine Richtungsaussage, keine belastbare Rate.