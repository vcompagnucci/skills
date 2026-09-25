# Verification

The thread that runs through nearly every post: Claude's output improves most when it has a way to check its own work, and the check is often worth more than more thinking, more reviewers, or a bigger model.

## Give it a check

- **Verification skills have the most measurable impact on output quality.** Worth a dedicated engineer-week; use Playwright or tmux drivers, record a video of what was tested, assert state at each step. (`skills`)
- **A check cuts turns.** A test, a build, or a script calling the endpoint lets the model find mistakes earlier. (`cost`)
- **Check for checks before raising effort.** A renamed field that medium effort misses on the client fails a client-level test on the turn it's written; a test run costs one turn, more effort adds thinking to every turn. (`cost`)
- **Name the finish line.** "The tests pass" or "every endpoint is migrated" tells a long run when it's done. (`opus-5-5`)

## What thorough verification looks like

- **High effort is mostly verification.** On `html-js-filter`, xhigh adversarially reviewed its draft, read the installed parser's source, ran many identity cases, a standard XSS suite, and a random-document fuzzer. (`effort`)
- **Reproduce first; prove the test would have caught the bug.** On `mvcc-lsm-compaction`, low effort edited before running the reproducer and never checked its test against the original bug; xhigh reproduced first, used a never-compacting reference, and checked tests fail on half-finished fixes. (`effort`)
- **Use an oracle.** `cli-2ph-simplex` passed only when Claude tested its solver against a separate brute-force solver on random problems and timed larger ones. (`effort`)
- **Red then green, many times.** The layout-shift test went red 20 of 20 runs on main and green 20 of 20 on the PR. (`faster`)

## Separate the checker from the author

- **Self-preferential bias is real.** Claude prefers its own findings when judging them; a separate verifier agent in its own context structurally prevents it. (`workflows`)
- **One verifier per claim or per rule.** Deep verification spawns a checker per factual claim, optionally auditing its source; rule adherence runs one verifier per rule, then a skeptic. (`workflows`)
- **Check each subagent's evidence before accepting it.** (`opus-5-5`)
- **Adversarial review until findings degrade to nitpicks.** The `adversarial-review` skill spawns a fresh-eyes subagent and iterates. (`skills`)
- **Rubrics are references.** They let verifier agents check your taste in a field (e.g. what good API design looks like). (`ctx-eng`)

## Protect wins

- **Benchmarks that only ratchet down.** Any PR raising the instruction count fails CI; a daily job lowers the ceiling. (`faster`)
- **Tests before optimizations; flags on anything user-visible; staged rollout** (employees → 1% → everyone); automated review plus one human approval. 3,000+ changes shipped without a customer-facing incident. (`faster`)
- **Guard brittle wins with many tests.** The static composer has jsdom parity tests, 14-viewport 1px alignment tests, a keystroke-through-handoff test, and field shift reporting to a tenth of a pixel. (`faster`)

## Reporting honestly

- **Ask it to mark what it couldn't confirm and where it looked.** (`opus-5-5`)
- **Review prompt that forces evidence.** Only merge-blocking problems, each with file, line, why, and how to show it fails. (`opus-5-5`)
- **Verification agents read your HTML plan files** for broader context on what was needed. (`html`)

## Key source articles
`effort` · `skills` · `workflows` · `faster` · `cost` · `opus-5-5`
