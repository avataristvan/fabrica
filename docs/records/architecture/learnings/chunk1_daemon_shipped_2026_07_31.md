type: learning
topic: architecture
created: 1785509735.991885
---

Observed: A Unix-socket daemon (ai_mem/daemon.py) keeps a warm ChromaMemoryRepository across hook calls. Measured on the real production DB (2026-07-31): cold hook call 2.817s, warm 1.476s, third call 1.326s -- roughly 45-55% less.
Cause: Every hook event starts a fresh Python process, ~1.1s of chromadb import + PersistentClient init + ONNX model load were lost every time. The remaining ~1.3s were 4 sequential semantic queries (global/repo/antipattern/dilemma) at ~0.27-0.4s ONNX inference each -- not cacheable, because every query is new text (load of the meanwhile removed userprompt_hook).
Evidence: commit 4ebef7f (bundled with the [available] format and mem_topics, see [arch_decision_push_vs_pull_2026_07_31](../decisions/arch_decision_push_vs_pull_2026_07_31.md)); tests/test_daemon.py, tests/test_daemon_client.py (real daemon in a thread, real socket protocol, only _spawn_daemon/stop_daemon mocked).

Design: Self-bootstrapping without systemd -- daemon_client.py pings the socket (150ms timeout); on a miss it starts `python -m ai_mem.daemon` detached and the current hook call falls back to the cold in-process path (never blocks), only the next one uses the daemon. Idle timeout 30 min; protocol version in the ping forces a respawn on an outdated daemon; install.py/uninstall.py call stop_running_daemon() (socket shutdown, PID kill as fallback) so that a `git pull` does not leave behind a daemon with old code. _hook_deps.py::_build_query_uc tries the daemon first. User constraint: installable/updatable via install.py, no manually maintained background process.
