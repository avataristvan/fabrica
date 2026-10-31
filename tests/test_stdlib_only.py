"""dependencies = [] is a promise: every runtime module imports without third-party packages."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_every_runtime_module_imports_with_the_stdlib_only():
    """With site-packages disabled (-S) every ai_mem module still imports."""
    code = (
        "import importlib, pkgutil, sys; sys.path.insert(0, %r); import ai_mem; "
        "names = [m.name for m in pkgutil.walk_packages(ai_mem.__path__, 'ai_mem.')]; "
        "[importlib.import_module(n) for n in names]; "
        "import ai_mem.hook as h; assert h.find_area is not None; "
        "assert len(names) > 20, names"
    ) % str(REPO_ROOT)
    result = subprocess.run([sys.executable, "-I", "-S", "-c", code], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
