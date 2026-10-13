id: learning_config_rewrite_keeps_file_mode_and_backs_up_once_2026_10_12
type: learning
area: plugin
perspective: agent
created: 1791838324.015333
cue: I am writing an installer or uninstaller that rewrites a user config file such as ~/.claude.json
---

Observed: Rewriting `~/.claude.json` (mode 0600, holds credentials) via `write_text` + `os.replace` leaves it at the umask default (0644). Create the temp file owner-only (os.open 0600, O_EXCL) and chmod it to the original's mode; copy2 keeps the backup's mode. A run that saves the same file twice (uninstall: MCP removal, then plugin hooks) must back up only on the first save, otherwise the backup holds already-modified content. The security-review hook and /simplify found it; the in-chunk sonnet reviewer did not.
Cause: os.replace swaps in a new inode that carries the temp file's mode, not the original's; a per-save backup overwrites the pristine copy on the second save.
Evidence: uninstall.py `_save_json`, tests/test_uninstall.py.
