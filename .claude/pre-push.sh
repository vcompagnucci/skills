#!/usr/bin/env bash
# Runs before a push: format, lint and types of the files the push changes, in under 9 s. Exit 1 stops the push.
#
# Git calls it as `pre-push REMOTE URL` and writes one line per ref to stdin: `<local ref> <local sha> <remote ref>
# <remote sha>`. For each branch it reads, the files that differ between the remote sha and the local sha are checked
# as they are in the pushed commit (read with `git show` into a temp folder), never as they are in the working tree, so
# an uncommitted or untracked file cannot pass or block a push.
#   - a new branch (remote sha all zeros) is compared with its merge-base with origin/main;
#   - a deleted branch (local sha all zeros), a tag and a commit without .claude/check.sh have nothing to check.
# It does not set core.hooksPath and does not touch .git/hooks: the shared pre-push hook of the home repo calls it.
set -euo pipefail

zeros=0000000000000000000000000000000000000000
budget=9 # seconds for the whole hook; $SECONDS counts from its start

root=$(git rev-parse --show-toplevel 2>/dev/null) || root=$(cd "$(dirname "$0")/.." && pwd -P)
cd "$root"

tmp=$(mktemp -d "${TMPDIR:-/tmp}/skills-pre-push.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
trap 'exit 130' INT TERM

# Where the files that a push changes start: the merge-base with the remote sha when this clone has that commit, else the
# merge-base with the remote's main. Empty when neither exists.
base_of() {
  local sha=$1 remote_sha=$2 base="" main
  if [ "$remote_sha" != "$zeros" ] && git cat-file -e "$remote_sha^{commit}" 2>/dev/null; then
    base=$(git merge-base "$remote_sha" "$sha" 2>/dev/null || true)
  fi
  if [ -z "$base" ]; then
    for main in origin/main origin/master; do
      if git rev-parse -q --verify "$main^{commit}" >/dev/null; then
        base=$(git merge-base "$main" "$sha" 2>/dev/null || true)
        break
      fi
    done
  fi
  printf '%s' "$base"
}

status=0
while read -r local_ref local_sha _remote_ref remote_sha; do
  case $local_ref in refs/heads/*) ;; *) continue ;; esac # a tag, or the like
  [ "$local_sha" != "$zeros" ] || continue # a deleted branch
  git cat-file -e "$local_sha^{commit}" 2>/dev/null || continue
  git cat-file -e "$local_sha:.claude/check.sh" 2>/dev/null || {
    echo "pre-push: $local_ref has no .claude/check.sh, nothing to check"
    continue
  }

  # The files the push changes (added, copied, modified, renamed), as paths from the repo root.
  base=$(base_of "$local_sha" "$remote_sha")
  changed=()
  if [ -n "$base" ]; then
    while IFS= read -r -d '' f; do changed+=("$f"); done < <(git diff --name-only -z --diff-filter=ACMR "$base" "$local_sha")
  else # nothing to compare with: every file of the commit
    while IFS= read -r -d '' f; do changed+=("$f"); done < <(git ls-tree -r -z --name-only "$local_sha")
  fi

  # The pushed commit's tools, config and code (so that ty sees the modules a changed file imports), read from the commit.
  dir=$tmp/${local_sha:0:12}
  mkdir -p "$dir"
  while IFS= read -r -d '' f; do
    case $f in
      */vendor/*) ;; # third-party code, never checked
      pyproject.toml | uv.lock | package.json | bun.lock | .oxlintrc.json | .oxfmtrc.json | .claude/check.sh | .claude/run_steps.py | *.py | *.js | *.mjs)
        mkdir -p "$dir/$(dirname "$f")"
        git show "$local_sha:$f" >"$dir/$f"
        ;;
    esac
  done < <(git ls-tree -r -z --name-only "$local_sha")

  # Of the changed files, the ones check.sh looks at.
  files=()
  for f in ${changed[@]+"${changed[@]}"}; do
    case $f in
      */vendor/*) ;;
      *.py | *.js | *.mjs) [ -f "$dir/$f" ] && files+=("$f") ;;
    esac
  done
  [ ${#files[@]} -gt 0 ] || {
    echo "pre-push: $local_ref changes no Python or JavaScript file, nothing to check"
    continue
  }

  # stdin is closed for the checks, so that none of them reads the lines that git is still sending.
  (
    cd "$dir" &&
      uv sync --frozen --quiet &&
      bun install --frozen-lockfile --silent &&
      left=$((budget - SECONDS)) &&
      CHECK_STEP_BUDGET_SECONDS=5 CHECK_BUDGET_SECONDS=$((left > 2 ? left : 2)) bash .claude/check.sh "${files[@]}"
  ) </dev/null || status=1
done
exit $status
