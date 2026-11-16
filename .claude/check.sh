#!/usr/bin/env bash
# The repo's checks, side by side: ruff and ty for the Python, oxlint for the JavaScript, and bun fmt for the JavaScript,
# JSON, YAML and CSS (not the Markdown: it is the content of the skills). Exit 1 if any fails.
#   bash .claude/check.sh           every tracked file (what CI runs)
#   bash .claude/check.sh FILE...   only these files, as paths from the repo root
# Needs the tools installed first: `uv sync --frozen && bun install --frozen-lockfile` (their versions are pinned in
# pyproject.toml, package.json and the two lock files), and bun at the version in .bun-version, which is also what CI installs. The steps run through .claude/run_steps.py, which fails a step
# that goes over CHECK_STEP_BUDGET_SECONDS and the whole run over CHECK_BUDGET_SECONDS, and names it.
set -euo pipefail
cd "$(dirname "$0")/.."

ruff=.venv/bin/ruff ty=.venv/bin/ty oxlint=node_modules/.bin/oxlint
for tool in "$ruff" "$ty" "$oxlint"; do
  [ -x "$tool" ] || { echo "$tool is missing: run 'uv sync --frozen && bun install --frozen-lockfile'" >&2; exit 1; }
done
# bun fmt is part of bun, and its output changes between versions: a different bun would format differently from CI.
want=$(tr -d '[:space:]' <.bun-version)
have=$(bun --version 2>/dev/null || true)
[ "$have" = "$want" ] || { echo "bun $want is needed for bun fmt (.bun-version), and this is ${have:-no bun}" >&2; exit 1; }

files=()
if [ $# -gt 0 ]; then
  files=("$@")
else
  while IFS= read -r f; do files+=("$f"); done < <(git ls-files)
fi

# ty cannot see the folders that the scripts put on sys.path, so each template folder gets its own run with its recipe/
# folder as a search path (pipeline/ and portrait-qa/ have modules of the same name, so they cannot share a run).
pipeline=() portrait=() scripts=() python=() js=() fmt=()
for f in ${files[@]+"${files[@]}"}; do
  case $f in
    */vendor/*) ;;  # third-party code, copied in as it was published
    *.py) python+=("$f")
      case $f in
        photo-retouch/templates/pipeline/*) pipeline+=("$f") ;;
        photo-retouch/templates/portrait-qa/*) portrait+=("$f") ;;
        *) scripts+=("$f") ;;
      esac ;;
    *.js | *.mjs) js+=("$f"); fmt+=("$f") ;;
    *.json | *.yml | *.yaml | *.css) fmt+=("$f") ;;
  esac
done

# One shell-quoted command line: the tool, then its arguments.
line() { printf '%q ' "$@"; }

steps=()
if [ ${#python[@]} -gt 0 ]; then
  steps+=("ruff check::$(line "$ruff" check --no-cache --output-format concise "${python[@]}")")
  steps+=("ruff format::$(line "$ruff" format --check --no-cache "${python[@]}")")
fi
templates=photo-retouch/templates
if [ ${#pipeline[@]} -gt 0 ]; then
  steps+=("ty pipeline::$(line "$ty" check --error-on-warning --output-format concise --extra-search-path "$templates/pipeline/recipe" "${pipeline[@]}")")
fi
if [ ${#portrait[@]} -gt 0 ]; then
  steps+=("ty portrait-qa::$(line "$ty" check --error-on-warning --output-format concise --extra-search-path "$templates/portrait-qa/recipe" "${portrait[@]}")")
fi
if [ ${#scripts[@]} -gt 0 ]; then
  steps+=("ty scripts::$(line "$ty" check --error-on-warning --output-format concise "${scripts[@]}")")
fi
if [ ${#js[@]} -gt 0 ]; then
  steps+=("oxlint::$(line "$oxlint" --deny-warnings "${js[@]}")")
fi
if [ ${#fmt[@]} -gt 0 ]; then
  steps+=("bun fmt::$(line bun fmt --no-script --check -- "${fmt[@]}")")
fi

if [ ${#steps[@]} -eq 0 ]; then
  echo "nothing to check: no Python, JavaScript, JSON, YAML or CSS file in the list"
  exit 0
fi
exec python3 -I .claude/run_steps.py "${steps[@]}"
