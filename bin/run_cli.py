"""Runs `python3 run_cli.py <module> [args]` as `__main__` with the plugin root first on sys.path.

Started as a script, not with `-m`: `-m` (and `-c`) put the caller's cwd on sys.path, so a foreign repo
with its own `ai_mem/` or `json.py` would run its code. A script's sys.path[0] is its own directory,
which is replaced by the plugin root here. Stdlib only.
"""
import os
import runpy
import sys

sys.path[0] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
runpy.run_module(sys.argv.pop(1), run_name="__main__", alter_sys=True)
