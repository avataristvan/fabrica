#!/usr/bin/env bash
# Fresh `claude -p` archivist run on a scratch copy built by build.py.
#   scripts/eval_archivist/run.sh <scratch-run-dir> [model]      (model: omit = the agent's default)
# Writes into <run>: stamp (taken right before the run, for the outside-scratch `find -newer`),
# transcript.jsonl (stream-json, incl. the archivist's tool calls), answer.json (the final result event),
# answer.txt (final answer), stderr.txt, real_before.sha / real_after.sha (the real record areas).
# Exit 1 when the real areas changed during the run.
set -euo pipefail
run=$(realpath "${1:?usage: run.sh <scratch-run-dir> [model]}"); model="${2:-}"
test -f "$run/workspace/ai-mem/.claude/agents/archivist.md" || { echo "no agent under test in $run; build it with build.py" >&2; exit 2; }
unset AI_MEM_WORKSPACE_ROOT AI_MEM_RECORDS_HOME
export PYENV_VERSION=3.13.11 AI_MEM_PATH="$run/db"

# `Bash(mem:*)` would also allow `mem add --area ~/workspace/...`: hash the real areas before and after.
real_hash() {
  { find "$HOME/workspace" \( -name .git -o -name node_modules -o -path '*/.claude/worktrees' \) -prune -o -path '*/docs/records/*' -type f -print 2>/dev/null || true  # unreadable docker volumes
    find "$HOME/workspace/ai-mem-records" -name .git -prune -o -type f -print; } | sort -u | xargs -r -d '\n' sha256sum 2>/dev/null || true
  # The store and the agent symlinks: listing only (name, size, mtime), never opened.
  find "$HOME/.local/share/ai-mem" "$HOME/.claude/agents" -printf '%p %s %T@ %l\n' 2>/dev/null | sort || true
}
real_hash > "$run/real_before.sha"
check_real() {
  real_hash > "$run/real_after.sha"
  if diff "$run/real_before.sha" "$run/real_after.sha"; then echo "real areas unchanged"
  else echo "REAL AREAS CHANGED during the run (see the diff above)" >&2; return 1; fi
}
# Also on a crashed or failed run: a write to real state must never go unnoticed.
trap 'rc=$?; check_real || rc=1; exit $rc' EXIT

touch "$run/stamp"
prompt="Use the archivist agent (Agent tool, subagent_type \"archivist\") to integrate the record candidates in $run/candidates.txt. Home area: ai-mem, the area of the working directory. This is an isolated test copy: every area lives under $run/workspace/ (siblings of the home area, and $run/workspace/ai-mem-records/<collection>); use only paths below $run/workspace, never ~/workspace. Tell the archivist this.${model:+ Spawn the archivist with model \"$model\" (Agent tool model parameter).} Then print its integration report verbatim as your final answer, and nothing else."
args=(-p "$prompt" --allowedTools "Read" "Grep" "Glob" "Bash(mem:*)" "Bash(mem-dream:*)" "Agent" --add-dir "$run" --add-dir "$(realpath "$(dirname "$0")/../../reference")" --output-format stream-json --verbose)
if [ -n "$model" ]; then args+=(--model "$model"); fi
(cd "$run/workspace/ai-mem" && claude "${args[@]}") > "$run/transcript.jsonl" 2> "$run/stderr.txt" || { cat "$run/stderr.txt" >&2; exit 1; }
python3 - "$run" <<'EOF'
import json, sys
run = sys.argv[1]
result = [e for e in map(json.loads, open(f"{run}/transcript.jsonl")) if e.get("type") == "result"][-1]
json.dump(result, open(f"{run}/answer.json", "w"), indent=1)
open(f"{run}/answer.txt", "w").write(result.get("result", ""))
print({k: result.get(k) for k in ("num_turns", "total_cost_usd", "duration_ms", "is_error")})
EOF
