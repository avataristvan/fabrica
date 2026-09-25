id: pattern_blindtest_methodik
type: pattern
created: 1780077541.217354
---

# Blindtest-Methodik für ai-mem Evaluation

## Was funktioniert NICHT

**Tried:** `env: {AI_MEM_PATH: /tmp/blind}` im MCP-Server-Eintrag von `~/.claude.json`
**Failed because:** Der `env`-Parameter gilt nur für den MCP-Server-Subprocess. Hooks (`ai_mem.hook`, `ai_mem.userprompt_hook`, `ai_mem.posttool_hook`) erben die Systemumgebung von Claude Code — sie lesen den echten DB-Pfad. Außerdem reused Claude Code den MCP-Server-Prozess nach Session-Restart, sodass env-Änderungen erst nach vollständigem Neustart der App greifen.

## Was funktioniert

**Option A: Hook-Commands präfixen (empfohlen)**
In `~/.claude/settings.json` alle drei Hook-Commands temporär ändern:
```
AI_MEM_PATH=/tmp/ai-mem-blind python3 -m ai_mem.hook 2>/dev/null || true
```
Damit laufen Hooks UND MCP-Server ohne echte DB. Danach zurücksetzen + Claude Code neu starten.

**Option B: DB-Verzeichnis umbenennen**
```bash
mv ~/.local/share/ai-mem ~/.local/share/ai-mem.bak
```
Risiko: wenn während des Tests etwas schreibt, verliert man nichts (leeres Verzeichnis wird neu angelegt), aber es ist destruktiver als Option A.

## Anforderungen für valide Blindtests
- Hook-Commands UND MCP-Server müssen beide auf leere/nicht-existente DB zeigen
- Claude Code nach Änderung vollständig neu starten (nicht nur neue Session)
- Test-Frage erst NACH dem Neustart stellen