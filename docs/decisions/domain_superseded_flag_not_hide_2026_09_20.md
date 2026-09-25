id: domain_superseded_flag_not_hide_2026_09_20
type: domain
created: 1789927320.601691
edges: [{"target_id": "domain_direction_judgment_over_scores_2026_09_20", "edge_type": "related"}]
---

Decision: Ein durch 'supersedes' überholter Eintrag wird beim Abruf markiert (superseded_by, valid_until) und der aktuelle Nachfolger wird angehängt — er wird nicht ausgeblendet und nicht automatisch gelöscht.
Why: Entscheidungs- und Design-Einträge tragen das Warum und die verworfenen Alternativen; das ist genau das nicht-ableitbare Wissen, das ai-mem bewahren soll. Ausblenden würde es verstecken, Löschen vernichten. Der Agent soll selbst urteilen, ob das Alte für die aktuelle Frage noch etwas hergibt (Urteil statt Score, siehe domain_direction_judgment_over_scores_2026_09_20). Gefährlich ist nicht Veraltetes an sich, sondern Veraltetes, das wie Aktuelles aussieht.
Scope: Kantentyp supersedes (Quelle = neuer Eintrag, Ziel = alter). Weil Kanten nur am Quell-Eintrag gespeichert werden und der Abruf nur ausgehenden Kanten folgt, trägt der alte Eintrag die Markierung selbst als Metadatum. Der Abruf folgt Ketten bis zum neuesten noch vorhandenen Nachfolger, dieser hat im Anhänge-Budget (2) Vorrang vor gewöhnlichen Kanten. Ein überholter Eintrag darf keinen anderen überholen (keine Zyklen). mem_dream schützt supersedes-Ziele weder per Kante noch per access_count. Rückgängig machen: mem_add mit metadatas [{"superseded_by": "", "valid_until": ""}]. Gilt nicht für Einträge, die per Konvention an Ort und Stelle überschrieben werden (current_focus).