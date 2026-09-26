# Evals and verification

How OpenAI and its guest authors check agent work, both inside a single run and across versions. The sources are engineering posts about Codex and internal agents, cookbooks with worked eval loops, a few guest posts from teams using Codex, and one research-style post about a benchmark. The recurring ideas: give the agent a way to check itself using the tools humans already trust, grade the trace and not only the answer, turn every correction into a test, and remember that a score measures the whole harness, not the model alone.

## Give the agent a check inside the run

- **Plug the agent into the verification tools you already use instead of letting it invent its own.** At Skyscanner, an MCP bridge let Codex ask the IDE for file problems and run the predefined test, lint and format configurations. A wrong constructor call went from a five-step fix loop (work out how to run tests, run them, parse, fix) to three (generate, ask for problems, fix). The author stopped copy-pasting errors into chat. This is one engineer's observation, not a measurement. (`skyscanner-mcp`)
- **Let the agent see what it built.** Giving a frontend agent browser automation to render pages, test viewports and walk flows "significantly improves the likelihood" of polished, complete results, and with image understanding it can compare against a reference. (`frontends`)
- **Build instruments for work judged by feel.** For a space game, the agent got an in-page state interface (current body, flight mode, terrain readiness, draw calls), named test scenes to jump to, and browser tests that load a scene, screenshot it and check state. (`astra-games`)
- **A shortcut to the state is not a test of the path.** Separate journey tests drove the real controls and recorded positions, catching a collision surface that wasn't ready and a ship jumping between positions, which a screenshot of the landing scene would miss. (`astra-games`)
- **Measure before optimizing, change one variable, and say what the number proves.** A 90-frame timing test cut discarded terrain jobs from 6,074 to 13 in a fixed-latency simulation. The author flags that these came from headless rendering and simulations, not GPU frame rate, so human playtesting still owns look and feel. (`astra-games`)
- **Require reviewable artifacts and give the agent tools to validate them before it answers.** A diligence agent writes a memo, risk register, citations and an evidence table, and two workspace tools check that claims cite real source files and that the artifacts exist with the right shape. (`improvement-loop`)
- **Give goals the agent can verify.** "Implement the plan in this file" is weak. "Port the library, keep the API compatible, done when the original unit tests pass and differences are documented" is strong. (`codex-maxxing`)
- **Verification tooling is what makes risky self-directed work safe to accept.** When a model rewrote production GPU kernels for a 20% serving cost cut, a floating-point sanitizer was the guard on correctness. (`gpt56-efficiency`)
- **An agent that notices a suspicious intermediate result should investigate before reporting.** The data agent treats zero rows from a bad join or filter as a signal to adjust and retry, instead of handing iteration back to the user. (`data-agent`)

## Build evals for skills and agents

- **Without evals you can't tell improving a skill from just changing it.** An eval is a prompt, a captured run (trace plus artifacts), a small set of checks and a comparable score. Otherwise a regression slips in unnoticed: the skill doesn't trigger, skips a step, or leaves extra files. (`eval-skills`)
- **Define success before writing the skill, in four kinds of goal.** Outcome (did it work), process (did it follow the intended steps), style (conventions) and efficiency (no thrashing). "Without clear constraints, there's nothing concrete to evaluate." (`eval-skills`)
- **Run it by hand first, then turn every manual fix into a test.** Manual runs expose triggering, environment and execution assumptions. 10 to 20 prompts are enough for one skill if they include explicit, implicit and noisy invocations plus negative controls that should not trigger it. (`eval-skills`)
- **Grade what the agent did, not only the final output.** Deterministic checks over the event trace (did it install, which commands in what order) tell you exactly why something failed. Add a model grader for qualitative checks, forced to return structured JSON so results diff across runs, and add heavier checks (token use, smoke tests, clean git status) only where they reduce risk. (`eval-skills`)
- **Evals can be continuous unit tests against golden answers.** The data agent keeps question plus golden SQL pairs, executes the generated SQL, and grades both query and result data with a grader that tolerates syntactic variation and extra columns. "Without a tight feedback loop, regressions are inevitable and invisible." (`data-agent`)
- **Gate on quality before looking at cost.** Policy compliance, action correctness, security and escalation accuracy are hard gates, run on a stratified eval set (intent, risk, language, region, edge cases) plus a holdout. (`cost-quality`)
- **Read trajectories and calibrate the judge.** Traces reveal loops and wrong actions a polished answer hides. The judge checks grounding against recorded tool results ("your refund is on its way" fails if only a review case was opened), never overrides a deterministic failure, and is checked against a small hand-labeled sample first. (`cost-quality`)
- **Use an agent as a proxy reader to test docs coverage.** Give it only the docs, have it build a project, run a test suite on the result. If it works, coverage is adequate. The authors call this experimental. (`dagster-docs`)
- **Simulate users at volume.** Hexagon runs thousands of realistic shopping prompts a day, varying region and reasoning depth, to track how answers behave. Raindrop evaluates production agents continuously against developer-set failure conditions and traces a failure to the prompt or system change that caused it. (`responses-year`)

## Corrections become evals

- **Optimize the harness, not just the prompt.** The harness (instructions, tools, routing, output requirements, validation) is an explicit, versioned config. Traces show what happened, feedback says what mattered, evals make it reusable, and a coding agent turns the evidence into a ranked change set. (`improvement-loop`)
- **Seed test data with deliberate conflicts.** A synthetic dataroom mixed exports with narratives that disagree ("SOC 2 complete" when only Type I exists, a management estimate that contradicts finance data) to surface real failure modes. (`improvement-loop`)
- **Keep expert feedback and model feedback separate, and have humans vet generated evals.** Model feedback widens coverage and expert feedback carries domain judgment. Generated evals mix literal assertions with a rubric judge, and people check they measure what matters before they join the suite. (`improvement-loop`)
- **A passing gate is not the end.** All 5 generated evals passed, yet the diagnosis found validators could pass while citation problems remained in the actual artifacts. (`improvement-loop`)
- **Move the human gate as trust grows.** Start with the system proposing a diff that a developer approves, then close the loop once the eval gate earns trust. Gates can sit at trace review, eval refinement, PR, merge or deploy. (`improvement-loop`)
- **Turn expert corrections into eval targets in three steps.** Capture the diff between what the agent proposed and what the expert filed, group related failures to separate recurring product bugs from noise, and promote repeated patterns to targets. (`tax-agents`)
- **Hand the coding agent a scoped task, not an alert.** Its environment splits a writable worktree (product code, targeted and regression evals, skills) from read-only production evidence (trace, source documents, prediction, final return). It diagnoses, fixes, reruns evals and proposes a PR for review. Returns reaching 75% correct field completion went from about a quarter at launch to 86% in six weeks. (`tax-agents`)
- **Quality is a loop: eval, improve, re-eval.** Programmable graders make it repeatable, and a task validated on a large model can then be distilled into a cheaper one. (`devs-2025`)

## Review agents

- **Written review rules measurably raise recall of team-specific bugs.** On a suite of known violations plus safe counterexamples, rule-guided review recovered 98% of required custom findings versus 58.3% for the baseline. Some bugs are invisible in the diff, like renaming an event that compiles but breaks a downstream consumer. (`review-rules`)
- **Score a reviewer on four axes, not just recall.** Coverage (finds violations in busy diffs), restraint (no finding on clean changes and valid exceptions), retention (still catches ordinary bugs), actionability (each finding names guidance, location, priority). (`review-rules`)
- **Test each rule with three cases.** One change that should trigger it, one safe counterexample, one unrelated change. Rules complement CI, linters and required approvals, they don't replace them. (`review-rules`)

## Evals measure harnesses

- **A benchmark scores a bundle of harness, settings and prompting.** On ARC-AGI-3, keeping past reasoning and compacting instead of truncating took the same model from 13.3% to 38.3% with about 6x fewer output tokens. OpenAI had been surprised before by low scores from eval runners that dropped reasoning. (`arc-agi-3`, `codex-platform`)

## Where the posts disagree

- **Should instructions tell the agent to run checks?** The Skyscanner post (`skyscanner-mcp`, 2026-01-11) credits an instruction to check problems, format and lint after every edit. The Astra post (`astra-skills`, 2026-09-11) says instructions to run tests now cause unnecessary testing because the stronger model already checks its work.
- **Fixed assertions or model judgment?** `eval-skills` (2026-01-22) starts with deterministic trace checks and adds a model grader only for qualitative checks, and `cost-quality` (2026-09-14) never lets the judge override a deterministic failure. `skills-oss` (2026-03-09) found model comparison against intent more accurate than fixed assertions for code that calls real APIs.

## Key source articles
`eval-skills` · `improvement-loop` · `tax-agents` · `review-rules` · `cost-quality` · `astra-games` · `skyscanner-mcp` · `data-agent` · `arc-agi-3`
