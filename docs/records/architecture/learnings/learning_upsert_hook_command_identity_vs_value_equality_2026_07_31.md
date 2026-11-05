type: learning
topic: architecture
created: 1790700224.170705
---

Observed: `entries.remove(entry)` in install.py's `_upsert_hook_command` deleted by dict value equality instead of by identity -- two independent empty or emptied `{"hooks": []}` groups further up the list could cause the wrong group to be removed.
Cause: list.remove() compares by ==, not by identity. Fixed with `entries[:] = [e for e in entries if e is not entry]`.
Evidence: Commit 33e0162 (formerly cited as 44f5f17), together with [fix_install_hook_registration_2026_07_31](fix_install_hook_registration_2026_07_31.md); tests/test_install.py.

## Edges

- related: [fix_install_hook_registration_2026_07_31](fix_install_hook_registration_2026_07_31.md)
