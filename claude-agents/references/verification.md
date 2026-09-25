# Verification

Nearly every post comes back to this. Claude's output improves most when it has a way to check its own work, and a check is often worth more than extra thinking, extra reviewers, or a bigger model.

## Give it a check

- **Verification skills have the most measurable effect on output quality.** They're worth a week of an engineer's time. Drive the product with Playwright or tmux, record a video of what was tested, and assert state at each step. (`skills`)
- **A check cuts turns.** A test, a build, or a script that calls the endpoint lets the model find its mistakes earlier. (`cost`)
- **Look for a check before raising effort.** When a field is renamed, medium effort can miss the client. A test that goes through the client fails on the turn the bug is written. Running a test costs one turn. More effort adds thinking to every turn. (`cost`)
- **Name the finish line.** "The tests pass" or "every endpoint is migrated" tells a long run when it's done. (`opus-5-5`)

## What thorough verification looks like

- **High effort is mostly verification.** On `html-js-filter`, xhigh reviewed its own draft adversarially, read the installed parser's source, ran many clean pages that should pass through unchanged, ran a standard XSS suite, and wrote a random-document fuzzer. (`effort`)
- **Reproduce the bug first, and prove the test would have caught it.** On `mvcc-lsm-compaction`, low effort edited the code before running the reproducer and never checked its test against the original bug. Xhigh reproduced the crash first, compared against a reference that never compacts, and checked that its tests failed on half-finished fixes. (`effort`)
- **Test against an oracle.** `cli-2ph-simplex` only passed when Claude checked its solver against a separate brute-force solver on random problems and timed larger ones. (`effort`)
- **Red, then green, many times.** The layout-shift test failed 20 of 20 runs on main and passed 20 of 20 on the PR. (`faster`)

## Keep the checker separate from the author

- **Self-preferential bias is real.** Claude favors its own findings when it judges them. A verifier agent with its own context avoids that by design. (`workflows`)
- **One verifier per claim, or per rule.** Deep verification gives each factual claim its own checker, which can also audit the source. Rule checks run one verifier per rule, then a skeptic agent. (`workflows`)
- **Check each subagent's evidence before accepting it.** (`opus-5-5`)
- **Review adversarially until only nitpicks are left.** The `adversarial-review` skill starts a fresh subagent to critique the work, fixes what it finds, and repeats. (`skills`)
- **Rubrics count as references.** A rubric lets verifier agents check your taste in a field, such as what good API design looks like. (`ctx-eng`)

## Protect wins

- **Benchmarks that only go down.** A PR that raises the instruction count fails CI, and a daily job lowers the ceiling. (`faster`)
- **Tests before optimizations, flags on anything users can see, staged rollouts.** Rollouts went to employees, then 1% of users, then everyone. Every PR got automated review plus one human approval. The team shipped more than 3,000 changes with no incident reaching customers. (`faster`)
- **Protect fragile wins with many tests.** The static composer has tests that it matches the real React component, 1px alignment tests at 14 viewport sizes, a test that types through the handoff, and field reports of any shift down to a tenth of a pixel. (`faster`)

## Reporting honestly

- **Ask it to mark what it couldn't confirm, and where it looked.** (`opus-5-5`)
- **Use a review prompt that demands evidence.** Only problems that would block the merge, each with file, line, why it's wrong, and how to show it fails. (`opus-5-5`)
- **Let the verification agent read your HTML plan files,** so it knows what was intended. (`html`)

## Key source articles
`effort` · `skills` · `workflows` · `faster` · `cost` · `opus-5-5`
