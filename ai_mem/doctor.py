"""`mem doctor` -- stub; `configure` and `run` are the contract with `mem_cli`."""
from __future__ import annotations

import argparse
import sys


def configure(parser: argparse.ArgumentParser) -> None:
    return None


def run(args: argparse.Namespace) -> int:
    print("mem doctor: not implemented yet", file=sys.stderr)
    return 2
