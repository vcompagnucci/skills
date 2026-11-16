#!/usr/bin/env bash
# Runs before a commit: formats the staged files and stages them again, then lints them with warnings as errors. Exit 1
# stops the commit. The same checks as CI (.claude/check.sh) with the same pins, in two steps that stop at the first
# failure:
#   1. Format: ruff format for the Python, bun fmt for the JavaScript, JSON, YAML and CSS (the Markdown is the content of
#      the skills, so it is never touched). A file that is staged whole is formatted and staged again. A file that is
#      staged in part (git diff lists it too) is never formatted and added, because that would commit hunks that were left
#      out: it is only checked, and the commit stops with the name when it is not formatted.
#   2. Lint: ruff check and oxlint --deny-warnings, on the staged content (the index), never on unstaged edits.
# A commit with no Python, JavaScript, JSON, YAML or CSS file staged exits 0 before it looks for a tool. A tool that is
# missing, is the wrong bun, or fails stops the commit with the reason: it never passes a file as "formatted".
# `git commit --no-verify` skips it. It does not set core.hooksPath and does not touch .git/hooks: the shared pre-commit
# hook of the home repo calls it. Tools: `uv sync --frozen && bun install --frozen-lockfile`, as for check.sh.
set -uo pipefail
export GIT_LITERAL_PATHSPECS=1 # a file name with [ or * is a name, not a pattern

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 1
cd "$root" || exit 1

tmp=$(mktemp -d "${TMPDIR:-/tmp}/skills-pre-commit.XXXXXX") || { echo "pre-commit: cannot make a temporary folder" >&2; exit 1; }
trap 'rm -rf "$tmp"' EXIT
trap 'exit 130' INT TERM
fail() { echo "pre-commit: $*" >&2; exit 1; }

# The staged files (added, copied, modified, renamed) and the ones with unstaged changes, as paths from the repo root.
# Each list goes through a file first: a git that fails must stop the commit, not read as "no files".
git diff --cached --name-only -z --diff-filter=ACMR >"$tmp/staged" || fail "git diff --cached failed, so nothing was checked"
git diff --name-only -z >"$tmp/unstaged" || fail "git diff failed, so nothing was checked"

python=() fmt=() js=() partly=()
while IFS= read -r -d '' f; do
  case $f in
    */vendor/*) continue ;; # third-party code, copied in as it was published
    *.py) python+=("$f") ;;
    *.js | *.mjs) js+=("$f"); fmt+=("$f") ;;
    *.json | *.yml | *.yaml | *.css) fmt+=("$f") ;;
    *) continue ;;
  esac
  grep -qxFz -- "$f" "$tmp/unstaged" && partly+=("$f")
done <"$tmp/staged"
[ $((${#python[@]} + ${#fmt[@]})) -gt 0 ] || exit 0

ruff=$root/.venv/bin/ruff oxlint=$root/node_modules/.bin/oxlint
if [ ${#python[@]} -gt 0 ] && [ ! -x "$ruff" ]; then fail "$ruff is missing: run 'uv sync --frozen && bun install --frozen-lockfile'"; fi
if [ ${#js[@]} -gt 0 ] && [ ! -x "$oxlint" ]; then fail "$oxlint is missing: run 'uv sync --frozen && bun install --frozen-lockfile'"; fi
if [ ${#fmt[@]} -gt 0 ]; then
  want=$(tr -d '[:space:]' <.bun-version) have=$(bun --version 2>/dev/null || true)
  [ "$have" = "$want" ] || fail "bun $want is needed for bun fmt (.bun-version), and this is ${have:-no bun}"
fi

# 1. Format.
in_list() { # in_list FILE LIST...
  local f=$1 g
  shift
  for g in "$@"; do [ "$g" = "$f" ] && return 0; done
  return 1
}
format_stdin() { # format_stdin FILE: the formatter's output for the staged content of FILE, on stdout
  case $1 in
    *.py) git show ":$1" | "$ruff" format --no-cache --stdin-filename "$1" - ;;
    *) git show ":$1" | bun fmt --no-script --stdin-filepath "$1" ;;
  esac
}
whole_py=() whole_fmt=() unformatted=()
for f in ${python[@]+"${python[@]}"} ${fmt[@]+"${fmt[@]}"}; do
  if in_list "$f" ${partly[@]+"${partly[@]}"}; then
    git show ":$f" >"$tmp/before" || fail "cannot read $f from the index"
    format_stdin "$f" >"$tmp/after" || fail "the formatter failed on $f, so it was not checked"
    cmp -s "$tmp/before" "$tmp/after" || unformatted+=("$f")
  else
    case $f in *.py) whole_py+=("$f") ;; *) whole_fmt+=("$f") ;; esac
  fi
done
if [ ${#unformatted[@]} -gt 0 ]; then
  for f in "${unformatted[@]}"; do echo "pre-commit: $f is staged in part and not formatted: format $f or stage all of it" >&2; done
  exit 1
fi
[ ${#whole_py[@]} -eq 0 ] || "$ruff" format --no-cache --quiet -- "${whole_py[@]}" || fail "ruff format failed"
[ ${#whole_fmt[@]} -eq 0 ] || bun fmt --no-script --log-level=error -- "${whole_fmt[@]}" || fail "bun fmt failed"
changed=()
for f in ${whole_py[@]+"${whole_py[@]}"} ${whole_fmt[@]+"${whole_fmt[@]}"}; do
  git diff --quiet -- "$f" || changed+=("$f")
done
if [ ${#changed[@]} -gt 0 ]; then
  git add -- "${changed[@]}" || fail "git add failed, so the formatted files are not staged"
  echo "pre-commit: formatted and staged again: ${changed[*]}"
fi

# 2. Lint the staged content: the index goes to a folder with the configs, as pre-push does with a pushed commit.
git ls-files -z --cached -- pyproject.toml .oxlintrc.json .oxfmtrc.json "${python[@]+"${python[@]}"}" "${js[@]+"${js[@]}"}" >"$tmp/export" ||
  fail "git ls-files failed, so nothing was linted"
mkdir "$tmp/index"
# The file modes come from the index too: ruff fails a script that has a shebang and is not executable.
git checkout-index -z --stdin --prefix="$tmp/index/" <"$tmp/export" || fail "cannot read the staged files out of the index"
if [ ${#python[@]} -gt 0 ]; then
  (cd "$tmp/index" && "$ruff" check --quiet --no-cache --output-format concise -- "${python[@]}") || exit 1
fi
if [ ${#js[@]} -gt 0 ]; then
  (cd "$tmp/index" && "$oxlint" --deny-warnings -- "${js[@]}") || exit 1
fi
