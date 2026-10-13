"""Build the archivist acceptance run: scratch copy, candidates, expected edges, the agent definition under test.

    python scripts/eval_archivist/build.py <scratch-run-dir> [--source ~/workspace]

Writes only below <scratch-run-dir> (must not exist or be empty, and must lie outside <source>)
and, for the two fixture files, next to this script:
  candidates.json      the 18 records of the 2026-10-10 briefing session (n, real id, type, redacted body)
  expected_edges.json  the edges those records carry today + the four missed predecessors
Layout of <scratch-run-dir>: workspace/ (copy of the record areas, ai-mem without the
`_2026_10_10` records), workspace/ai-mem/.claude/agents/archivist.md (this checkout's definition: a
project agent wins over ~/.claude/agents/, whose symlink points at the main checkout),
candidates.txt (what the archivist receives, no ids), db/.migrations/records_v1.done (so the
migration guard does not trip), baseline.json (sha256 of every record file in the copy before the run).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from fixtures import REPO, Candidate, ParsedAdr, ExpectedEdge, read_record, render_candidates, save, CANDIDATES, EXPECTED_EDGES

sys.path.insert(0, str(REPO / "scripts"))

import scratch_mirror  # noqa: E402

RECORDS_HOME = scratch_mirror.RECORDS_HOME
SUFFIX = "_2026_10_10"
# The briefing-day records: architecture/ and retrieval/ topics of the ai-mem area. The remaining
# `_2026_10_10` records (plugin/, workflow/) came from later chunk work; they are dropped from the
# copy as well, but are not candidates and no expected edge touches them.
CANDIDATE_TOPICS = ("architecture", "retrieval")
# The briefing table: the new record should point at the predecessor. The fourth one is a reference doc, see README.
MISSED_EDGES = [
    ExpectedEdge("learning_context_boundary_is_read_and_write_point_2026_10_10", "related",
                 "pattern_retrieval_needs_fixed_trigger_in_role_prompt", "ai-mem-records/workspace"),
    ExpectedEdge("domain_area_path_is_the_address_of_knowledge_2026_10_10", "related",
                 "pattern_mixed_context_focus_degradation", "ai-mem-records/global"),
    ExpectedEdge("domain_hooks_enforce_that_roles_decide_how_2026_10_10", "related",
                 "pattern_convention_enforcement_gap", "ai-mem-records/global"),
    ExpectedEdge("domain_archivist_who_what_how_2026_10_10", "related",
                 "knowledge_architecture_framework", "ai-mem-records/global"),
]
# Sentences that announce a missed predecessor without naming it (candidates 14 and 17).
ANNOUNCEMENTS = ("was missed when", "predecessors in `global` and `workspace`")
DATED_ID = re.compile(r"\b[a-z][a-z0-9_]*_20\d\d_\d\d_\d\d\b")
AGENT = REPO / "agents" / "archivist.md"
# The same environment run.sh gives the archivist: no real records home, the scratch db.
UNSET = ("AI_MEM_WORKSPACE_ROOT", "AI_MEM_RECORDS_HOME")


def redact(body: str) -> str:
    """No id hints: drop sentences naming or announcing a missed predecessor, blank every other record id."""
    predecessors = [edge.target for edge in MISSED_EDGES]
    kept = []
    for line in body.split("\n"):
        sentences = re.split(r"(?<=[.:])\s+|(?<=[.:]')\s+", line)
        sentences = [s for s in sentences if not any(word in s for word in (*predecessors, *ANNOUNCEMENTS))]
        kept.append(" ".join(sentences))
    return DATED_ID.sub("an earlier record (id withheld)", "\n".join(kept))


def collect(source: Path) -> list[ParsedAdr]:
    root = source / "ai-mem" / "docs" / "records"
    paths = [path for topic in CANDIDATE_TOPICS for path in sorted((root / topic).glob(f"*/*{SUFFIX}.md"))]
    records = [read_record(path) for path in paths]
    if broken := [str(path) for path, r in zip(paths, records) if r is None]:
        raise SystemExit(f"malformed candidate records: {broken}")
    return records


def write_fixtures(source: Path) -> list[Candidate]:
    records = collect(source)
    candidates = [Candidate(f"{n:02d}", r.id, "decision" if r.type == "domain" else r.type, redact(r.text.strip()))
                  for n, r in enumerate(records, 1)]
    ids = {r.id for r in records}
    expected = [ExpectedEdge(r.id, edge["edge_type"], edge["target_id"])
                for r in records for edge in r.edges
                if edge["target_id"] in ids or not edge["target_id"].endswith(SUFFIX)]
    save(CANDIDATES, candidates)
    save(EXPECTED_EDGES, expected + MISSED_EDGES)
    return candidates


def adopt_hand_kept_areas(workspace: Path, db: Path) -> None:
    """`mem lint --fix` on the COPY of every area with a hand-kept INDEX.md, so the write guard lets the archivist add there (no-op on areas whose INDEX is already generated)."""
    env = {**{k: v for k, v in os.environ.items() if k not in UNSET}, "AI_MEM_PATH": str(db), "PYENV_VERSION": "3.13.11"}
    for index in sorted(workspace.rglob("docs/records/INDEX.md")):
        area = index.parents[2]
        if not area.resolve().is_relative_to(workspace):
            raise RuntimeError(f"refusing to lint outside the copy: {area}")
        done = subprocess.run(["mem", "lint", "--fix", "--area", str(area)], env=env, capture_output=True)
        if done.returncode not in (0, 1):  # 1 = findings left (e.g. dangling edges already in the real records)
            raise RuntimeError(f"mem lint --fix failed in {area}: {done.stderr.decode()}")
        print(f"mem lint --fix on the copy of {area.relative_to(workspace)} ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--source", type=Path, default=Path("~/workspace").expanduser())
    args = parser.parse_args(argv)
    source, run = args.source.resolve(), args.run_dir.resolve()
    if run == source or run.is_relative_to(source):
        print(f"refused: {run} lies inside the source {source}", file=sys.stderr)
        return 2
    if run.exists() and any(run.iterdir()):
        print(f"refused: {run} is not empty", file=sys.stderr)
        return 2

    workspace = run / "workspace"
    scratch_mirror.mirror(source, workspace)
    dropped, rewritten = scratch_mirror.drop_suffix(workspace, SUFFIX)
    print(f"dropped {len(dropped)} records, stripped references in {rewritten}")

    (run / "db" / ".migrations").mkdir(parents=True)
    (run / "db" / ".migrations" / "records_v1.done").write_text("")
    # reference docs of the global collection: the 4th predecessor is a docs/reference/ id, which `mem link` resolves
    reference = source / RECORDS_HOME / "global" / "docs" / "reference"
    if reference.is_dir():
        shutil.copytree(reference, workspace / RECORDS_HOME / "global" / "docs" / "reference")
    adopt_hand_kept_areas(workspace, run / "db")
    candidates = write_fixtures(source)
    (run / "candidates.txt").write_text(render_candidates(candidates))
    print(f"candidates: {len(candidates)}")
    agents = workspace / "ai-mem" / ".claude" / "agents"
    agents.mkdir(parents=True)
    # Outside a plugin ${CLAUDE_PLUGIN_ROOT} is not expanded: name this checkout instead (run.sh adds it via --add-dir).
    (agents / "archivist.md").write_text(AGENT.read_text().replace("${CLAUDE_PLUGIN_ROOT}", str(REPO)))
    print(f"agent under test: {AGENT} -> {agents / 'archivist.md'}")

    baseline = {str(p.relative_to(workspace)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(workspace.rglob("docs/records/**/*.md"))}
    (run / "baseline.json").write_text(json.dumps(baseline, indent=0))
    print(f"baseline files in copy: {len(baseline)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
