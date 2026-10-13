"""Plugin hook runner: `python3 run.py <module>` runs `ai_mem.<...>` as `__main__` with the plugin root on sys.path.

Claude Code starts hooks without the package installed, so the plugin root (this file's grandparent) is
put on sys.path before the module is imported. Stdlib only. A hook must not raise or write stderr
(pattern_hooks_must_not_raise): anything that goes wrong here ends silently with exit 0.
"""
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv: list[str]) -> None:
    module = argv[1] if len(argv) == 2 else ""
    if not module.startswith("ai_mem.") or not all(part.isidentifier() for part in module.split(".")):
        return
    sys.path.insert(0, ROOT)
    runpy.run_module(module, run_name="__main__")


if __name__ == "__main__":
    try:
        main(sys.argv)
    except BaseException:  # noqa: BLE001 -- a hook must not raise, not even on SystemExit/KeyboardInterrupt
        pass
    sys.stderr = open(os.devnull, "w")  # nothing the interpreter prints at shutdown may reach stderr
    sys.exit(0)
