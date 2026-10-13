#!/usr/bin/env bash
# Acceptance run for UPGRADING.md (records_v1), on copies only. See README.md next to this file.
#
#   scripts/upgrade_acceptance/run.sh <scratch-dir> [--skip-agents]
#
# Env overrides: SRC (code under test, default: this checkout), STORE_SRC (store to copy,
# default ~/.local/share/ai-mem.bak-2026-10-04), WORKSPACE (default ~/workspace),
# BASE_PY (interpreter for the venvs, default python3), CLAUDE_BIN (default claude).
set -uo pipefail

SCRATCH=${1:?usage: run.sh <scratch-dir> [--skip-agents]}
SKIP_AGENTS=${2:-}
HERE=$(cd "$(dirname "$0")" && pwd -P)
SRC=${SRC:-$(cd "$HERE/../.." && pwd -P)}
STORE_SRC=${STORE_SRC:-$HOME/.local/share/ai-mem.bak-2026-10-04}
WORKSPACE=${WORKSPACE:-$HOME/workspace}
BASE_PY=${BASE_PY:-python3}
CLAUDE_BIN=${CLAUDE_BIN:-claude}
REAL_STORE=$HOME/.local/share/ai-mem

mkdir -p "$SCRATCH"
SCRATCH=$(cd "$SCRATCH" && pwd -P)
if [ -n "$(ls -A "$SCRATCH")" ]; then echo "scratch dir must be empty: $SCRATCH" >&2; exit 2; fi
case "$SCRATCH" in "$REAL_STORE"*|"$WORKSPACE"/*|"$HOME/.local/share"/*) echo "scratch dir must not be inside real data" >&2; exit 2;; esac

FAILED=0
check() {  # check <name> <command...>
  local name=$1; shift
  if "$@"; then echo "PASS  $name"; else echo "FAIL  $name"; FAILED=1; fi
}
log() { echo "---- $*"; }
git_q() { git -c user.name=acceptance -c user.email=acceptance@localhost -c commit.gpgsign=false "$@"; }

real_checksums() {
  {
    find "$REAL_STORE" "$STORE_SRC" -type f -exec sha256sum {} + 2>/dev/null
    for d in "$WORKSPACE"/*/docs/records "$WORKSPACE/ai-mem-records"; do
      [ -d "$d" ] && find "$d" -type f -exec sha256sum {} +
    done
  } | sort -k2
}

log "real-data checksums (before)"
real_checksums > "$SCRATCH/real-before.sha"

log "store copies (mapping file and sentinel removed)"
for X in A B C; do
  mkdir -p "$SCRATCH/$X"
  cp -a "$STORE_SRC" "$SCRATCH/$X/db"
  rm -f "$SCRATCH/$X/db/adr_collection_roots.json" "$SCRATCH/$X/db/.migrations/records_v1.done"
done

log "scratch workspaces (CLAUDE.md copies, git init where the real dir is a repo)"
(cd "$WORKSPACE" && find . -maxdepth 6 \( -name '.*' ! -name . -o -name node_modules -o -name build \
    -o -name .gradle -o -name __pycache__ -o -name venv \) -prune -o -name CLAUDE.md -type f -print) \
  | sed 's|^\./||' | sort > "$SCRATCH/claude_md.list"
for X in A B C; do
  WS=$SCRATCH/$X/ws
  mkdir -p "$WS/ai-mem-records"
  while read -r rel; do
    dir=$(dirname "$rel")
    mkdir -p "$WS/$dir"
    cp "$WORKSPACE/$rel" "$WS/$rel"
    if [ "$dir" != "." ] && [ -e "$WORKSPACE/$dir/.git" ] && [ ! -e "$WS/$dir/.git" ]; then
      git_q init -q "$WS/$dir"
    fi
  done < "$SCRATCH/claude_md.list"
done

log "code under test: bare remote + clones"
mkdir -p "$SCRATCH/remote-src"
(cd "$SRC" && git ls-files -co --exclude-standard -z | xargs -0 cp --parents -t "$SCRATCH/remote-src")
git_q -C "$SCRATCH/remote-src" init -q -b main
git_q -C "$SCRATCH/remote-src" add -A
git_q -C "$SCRATCH/remote-src" commit -q -m "code under test"
git_q clone -q --bare "$SCRATCH/remote-src" "$SCRATCH/remote.git"
for X in B C; do git_q clone -q "$SCRATCH/remote.git" "$SCRATCH/$X/checkout"; done
echo "pulled by the upgrade" > "$SCRATCH/remote-src/UPGRADE_ACCEPTANCE_MARKER"
git_q -C "$SCRATCH/remote-src" add UPGRADE_ACCEPTANCE_MARKER
git_q -C "$SCRATCH/remote-src" commit -q -m "trivial commit for git pull --ff-only"
git_q -C "$SCRATCH/remote-src" push -q "$SCRATCH/remote.git" main
echo "local edit" > "$SCRATCH/C/checkout/UPGRADE_ACCEPTANCE_MARKER"
git_q -C "$SCRATCH/C/checkout" add UPGRADE_ACCEPTANCE_MARKER
git_q -C "$SCRATCH/C/checkout" commit -q -m "local commit that diverges from the remote"
C_HEAD_BEFORE=$(git -C "$SCRATCH/C/checkout" rev-parse HEAD)

log "throwaway venvs (no extras, so no chromadb)"
for X in B C; do
  "$BASE_PY" -m venv "$SCRATCH/$X/venv"
  "$SCRATCH/$X/venv/bin/python" -m pip install -q -e "$SCRATCH/$X/checkout" > "$SCRATCH/$X/pip.log" 2>&1 \
    || { echo "pip install failed for $X, see $SCRATCH/$X/pip.log" >&2; exit 1; }
done
check "venv B has no chromadb" bash -c "! '$SCRATCH/B/venv/bin/python' -c 'import chromadb' 2>/dev/null"

env_for() { echo "AI_MEM_PATH=$SCRATCH/$1/db AI_MEM_WORKSPACE_ROOT=$SCRATCH/$1/ws PATH=$SCRATCH/$1/venv/bin:$PATH"; }
A_ENV="AI_MEM_PATH=$SCRATCH/A/db AI_MEM_WORKSPACE_ROOT=$SCRATCH/A/ws"
MIGRATE="$SCRATCH/B/venv/bin/mem-adr-sync migrate"

log "dry run on A: collections the scan cannot place, or places by name only"
env $A_ENV $MIGRATE > "$SCRATCH/A/dry-run.txt" 2>&1
cat "$SCRATCH/A/dry-run.txt"
# UPGRADING.md stops on both, and the B agent may not use --root. A real installation has
# these placements recorded in adr_collection_roots.json, so the harness records them there
# too (relative to each workspace): name-matched ones where the scan found them, unplaced
# repo.a.b under ws/a/b. Identical in A, B and C.
"$BASE_PY" - "$SCRATCH" "$SCRATCH/A/dry-run.txt" <<'PY' || FAILED=1
import json, os, re, sys
scratch, dry = sys.argv[1], open(sys.argv[2]).read()
rel = {}
m = re.search(r"^\d+ collections placed by directory name only: (.*)$", dry, re.M)
for pair in (m.group(1).split(", ") if m else []):
    name, path = pair.split(" -> ")
    rel[name] = os.path.relpath(path, f"{scratch}/A/ws")
m = re.search(r"^\d+ collections without a directory \(skipped\): (.*)$", dry, re.M)
for item in (m.group(1).split(", ") if m else []):
    name = re.sub(r" \(\d+\)$", "", item)
    if not name.startswith("repo."):
        sys.exit(f"cannot place non-repo collection {name} -- fix the harness inputs")
    rel[name] = name.removeprefix("repo.").replace(".", "/")
for x in "ABC":
    mapping = {name: f"{scratch}/{x}/ws/{path}" for name, path in rel.items()}
    for path in mapping.values():
        os.makedirs(path, exist_ok=True)
    with open(f"{scratch}/{x}/db/adr_collection_roots.json", "w") as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
for name, path in sorted(rel.items()):
    print(f"recorded {name} -> ws/{path}")
PY
env $A_ENV $MIGRATE > "$SCRATCH/A/dry-run-2.txt" 2>&1
cat "$SCRATCH/A/dry-run-2.txt"
check "A dry run places nothing by name only" bash -c "! grep -q 'placed by directory name only' '$SCRATCH/A/dry-run-2.txt'"
check "A dry run is clean" bash -c "! grep -q '^NOT CLEAN' '$SCRATCH/A/dry-run-2.txt'"
check "dry run wrote nothing into A/ws" bash -c "[ -z \"\$(find '$SCRATCH/A/ws' -path '*/docs/*' -print -quit)\" ]"

log "A: migrate --apply directly"
env $A_ENV $MIGRATE --apply > "$SCRATCH/A/apply.txt" 2>&1; A_RC=$?
cat "$SCRATCH/A/apply.txt"
check "A apply exit 0" test "$A_RC" -eq 0
check "A sentinel exists" test -f "$SCRATCH/A/db/.migrations/records_v1.done"

log "hook guard line on a copy without the sentinel"
cp -a "$SCRATCH/A/db" "$SCRATCH/hookcheck-db"
rm -f "$SCRATCH/hookcheck-db/.migrations/records_v1.done"
(cd "$SCRATCH" && echo '{}' | env AI_MEM_PATH="$SCRATCH/hookcheck-db" "$SCRATCH/B/venv/bin/python" -m ai_mem.hook \
  > "$SCRATCH/hookcheck.out" 2> "$SCRATCH/hookcheck.err")
check "hook prints the guard line" grep -q "ai-mem upgrade pending" "$SCRATCH/hookcheck.out"
check "hook writes no stderr" test ! -s "$SCRATCH/hookcheck.err"

run_agent() {  # run_agent <X>
  local X=$1
  # cwd is <scratch>/X, not the checkout: the sandbox masks protected paths (.bashrc, .claude/, ...)
  # in its cwd with /dev/null mounts, which would show up as untracked files in the checkout.
  (cd "$SCRATCH/$X" && env $(env_for "$X") "$CLAUDE_BIN" -p \
      "Upgrade the ai-mem installation in $SCRATCH/$X/checkout. Instructions: $SCRATCH/$X/checkout/UPGRADING.md" \
      --output-format json --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
      --settings '{"disableAllHooks": true, "sandbox": {"enabled": true, "failIfUnavailable": true, "allowUnsandboxedCommands": false, "network": {"allowedDomains": ["pypi.org", "files.pythonhosted.org"]}}}' \
      --allowedTools "Bash Read Glob Grep" \
      --add-dir "$SCRATCH/$X" > "$SCRATCH/$X/agent.json" 2> "$SCRATCH/$X/agent.err")
  echo "agent $X exit $?"
  "$BASE_PY" -c "import json,sys; print(json.load(open(sys.argv[1])).get('result',''))" "$SCRATCH/$X/agent.json" \
    > "$SCRATCH/$X/agent.txt" 2>/dev/null || cp "$SCRATCH/$X/agent.json" "$SCRATCH/$X/agent.txt"
  echo "agent $X said:"; sed 's/^/    /' "$SCRATCH/$X/agent.txt"
}

if [ "$SKIP_AGENTS" != "--skip-agents" ]; then
  log "B: fresh claude -p agent follows UPGRADING.md"
  run_agent B
  check "B pulled the remote commit" test -f "$SCRATCH/B/checkout/UPGRADE_ACCEPTANCE_MARKER"
  check "B sentinel exists" test -f "$SCRATCH/B/db/.migrations/records_v1.done"
  check "B venv still has no chromadb" bash -c "! '$SCRATCH/B/venv/bin/python' -c 'import chromadb' 2>/dev/null"
  check "diff -r A/ws B/ws is empty (without .git)" diff -r -x .git "$SCRATCH/A/ws" "$SCRATCH/B/ws"
  check "reports equal after stripping scratch prefixes" bash -c \
    "diff <(sed 's#$SCRATCH/A/#<X>/#g' '$SCRATCH/A/db/records-migration-report.md') \
          <(sed 's#$SCRATCH/B/#<X>/#g' '$SCRATCH/B/db/records-migration-report.md')"

  log "C: diverged checkout -- the agent must stop without merge/reset"
  run_agent C
  check "C HEAD unchanged" test "$(git -C "$SCRATCH/C/checkout" rev-parse HEAD)" = "$C_HEAD_BEFORE"
  check "C has no merge commit" test -z "$(git -C "$SCRATCH/C/checkout" log --merges --oneline)"
  check "C has no merge/rebase in progress" bash -c \
    "[ ! -e '$SCRATCH/C/checkout/.git/MERGE_HEAD' ] && [ ! -d '$SCRATCH/C/checkout/.git/rebase-merge' ] && [ ! -d '$SCRATCH/C/checkout/.git/rebase-apply' ]"
  check "C local commit still there" test "$(cat "$SCRATCH/C/checkout/UPGRADE_ACCEPTANCE_MARKER")" = "local edit"
  check "C migrated nothing" bash -c "[ ! -e '$SCRATCH/C/db/.migrations/records_v1.done' ] && [ -z \"\$(find '$SCRATCH/C/ws' -path '*/docs/*' -print -quit)\" ]"
else
  echo "SKIP  agent runs B and C (--skip-agents)"
fi

log "real-data checksums (after)"
real_checksums > "$SCRATCH/real-after.sha"
if diff "$SCRATCH/real-before.sha" "$SCRATCH/real-after.sha" > "$SCRATCH/real-diff.txt"; then
  echo "PASS  real-data checksums identical"
else
  echo "FAIL  real-data checksums differ (see $SCRATCH/real-diff.txt):"; sed 's/^/    /' "$SCRATCH/real-diff.txt"
  FAILED=1
fi

echo; [ "$FAILED" -eq 0 ] && echo "ACCEPTANCE: PASS" || echo "ACCEPTANCE: FAIL"
exit "$FAILED"
