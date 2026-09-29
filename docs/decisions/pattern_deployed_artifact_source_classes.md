id: pattern_deployed_artifact_source_classes
type: pattern
created: 1790440791.965188
---

Rule: Vor dem Editieren einer ausgerollten Datei (Skill, Command, Agent) ihre Quellklasse bestimmen: (1) Repo-Quelle plus installierte Kopie (z. B. ~/.claude/commands/reflect.md aus skills/examples/reflect.md): die Quelle editieren, dann synchronisieren (install_reflect_command()); (2) Symlink (z. B. ~/.claude/agents/librarian.md -> examples/agents/librarian.md): die Repo-Datei editieren; Agent-Definitionen werden erst nach einem Neustart von Claude Code neu gelesen; (3) rein global, ohne Repo-Quelle (~/.claude/commands/chunk-plan.md, dev-team.md): direkt an Ort und Stelle editieren.
When: Eine Datei unter ~/.claude/ soll geändert werden.
Why: Alle drei Fälle kamen am 2026-09-26 vor. Eine direkte Änderung an einer Kopie aus Klasse (1) driftet still und wird beim nächsten install überschrieben; bei Klasse (3) gibt es keine Quelle, die man stattdessen editieren könnte.