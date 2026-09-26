# Evals and verification

Nearly every post comes back to checking, and the docs guides, cookbooks, and research posts add rubrics, target numbers, and monitoring results. Inside a run, Claude improves most when it has a way to check its own work. Across runs, teams without evals "fly blind". The rules Anthropic repeats: start small from real failures, grade outcomes rather than paths, keep the checker separate from the author, and read the transcripts before trusting a number.

## Give it a check inside the run

- **Give Claude a check it can run, or you become the verification loop.** Claude stops when work "looks done". A test suite, build exit code, linter, or screenshot lets it iterate until it passes. Gates escalate from the prompt, to a Stop hook, to a verification subagent. Ask for evidence, not claims of success, and re-run every assertion yourself after the turn ends, since the agent may have regressed something after its last check. "If you can't verify it, don't ship it." (`cc-best-practices`, `cb-fix-tests`)
- **Verification skills have the most measurable effect on output quality.** They're worth a week of an engineer's time. (`skills`)
- **Rules beat visual feedback, which beats LLM judges.** The best feedback is a clearly defined rule plus which rule failed and why. An LLM judge is "generally not a very robust method" and adds latency. (`agent-sdk`)
- **Test properties, not examples, and filter false positives hard.** An agent that inferred invariants from types and docstrings and ran Hypothesis found real bugs in NumPy and SciPy. Of 984 raw reports, 56% of a manual sample were valid. A rubric score raised that to 86% among top reports, and humans still reviewed each before filing. Reflection caught a test that passed only because the agent had wrapped it in try-catch. (`pbt-agent`)
- **Make success machine-checkable when a program consumes it.** A scheduled reviewer returns JSON to a schema, prints fixed greppable lines (`VERDICT:`, `REVIEW-RUN-INCOMPLETE`), and must echo the prior run's finding IDs to prove continuity instead of assuming `resume` worked. (`cb-repo-reviewer`)
- **Test like a user.** Claude marked features done after unit tests and `curl` while they were broken. Browser automation fixed most of that. (`long-running-harness`)
- **The task verifier must be nearly perfect, or Claude solves the wrong problem.** Most of the C compiler effort went into tests and feedback. "It is easy to see tests pass and assume the job is done, when this is rarely the case." (`c-compiler`)

## Keep the checker separate from the author

- **Agents can't grade their own work.** Asked to evaluate their own output, they praise it even when it's mediocre, especially on subjective work. Tuning a separate, skeptical evaluator is "far more tractable" than making a generator self-critical. Out of the box, Claude is a poor QA agent that talks itself into approving. Putting the rubric in the writer's own prompt doesn't fix it. Only a grader with a fresh context re-fetches the URL. (`harness-design-apps`, `cb-outcome-grader`)
- **Self-preferential bias is why workflows split judging off.** A verifier in its own context avoids it by design. One verifier per claim or per rule, then a skeptic. (`workflows`)
- **Don't trust "verified".** On a physics paper, Claude faked a plot's uncertainty band, invented coefficients in "verification" documents, and stopped checking after finding one error. Anti-shortcut rules only partly helped, and cross-checking with GPT and Gemini caught errors none found alone. (`vibe-physics`)
- **A verifier is only as good as its criteria.** Told only "is it good", it rubber-stamps. Verifiers declare victory after one or two tests unless told exactly what to check: "You MUST run the complete test suite before marking as passed." Cap iterations and define a fallback. (`coordination-patterns`, `when-multi-agent`)
- **Write the rubric more specific than the task, and name the shortcuts.** "Covers demand charges" passes a skim. Demanding a `$/kW` figure from a 10-K on `sec.gov` made the grader reject a press release twice. Add lines like "do NOT corroborate via mirrors or search snippets", and derive criteria from a known-good example. (`cb-outcome-grader`)
- **Triage must not inherit the finder's confidence.** A fresh pass re-reads the code, checks each finding against the actual lines, merges duplicates by root cause, and re-derives severity. An explicit high-value vs. noise tier list is most of what makes a security report actionable. (`cb-vuln-agent`)
- **Many narrow reviewers beat one mega-prompt reviewer, and each finding needs proof.** Narrow reviewers don't share blind spots. Requiring a proof of each finding raised PRs with substantive comments from 16% to 54%. Ask a reviewer only for merge-blocking problems, each with file, line, why, and how to show it fails, plus what it couldn't confirm. (`secure-sdlc`, `opus-5-5`)

## Build evals early

- **Without evals, teams fly blind once agents scale.** Debugging turns reactive. Teams with evals upgrade to a new model in days, not weeks. (`agent-evals`)
- **Start with 20-50 simple tasks drawn from real failures.** Early changes have large effects, so small samples are enough. Source them from manual checks, the bug tracker, and the support queue. The research system started with about 20 real queries, and one prompt tweak moved success from 30% to 80%. (`agent-evals`, `research-system`)
- **A good task is one two experts would grade the same way.** Opus 4.5 went from 42% to 95% on CORE-Bench after fixing rigid grading and ambiguous specs. With frontier models, 0% after 100 tries usually means a broken task. (`agent-evals`)
- **Grade what the agent produced, not the path it took.** Exact tool-call checks are brittle. Opus 4.5 "failed" a τ2-bench task by finding a policy loophole that was better for the user. Commerce teams grade snapshots of state, not whole conversations. (`agent-evals`, `commerce-agents`)
- **Prefer deterministic graders, use LLM graders where needed, and calibrate them with humans.** Let judges answer "Unknown" and grade each rubric dimension separately. A single LLM judge with one rubric was more consistent than several. (`agent-evals`, `research-system`)
- **Split the job into tasks and set a target for each before launch.** The support guide decomposes a conversation into greeting, product info, staying on topic, and quoting, each with its own test cases and target (support and routing targets in `agents-in-production.md`). (`uc-support`, `uc-routing`)
- **Balance positive and negative cases.** Web search evals needed queries that should search and queries that shouldn't. Pair every positive with a negative. (`agent-evals`, `commerce-agents`)
- **Read the transcripts.** "We do not take eval scores at face value until someone digs into the details of the eval and reads some transcripts." Humans caught the research agent preferring SEO content farms over academic PDFs. (`agent-evals`, `research-system`)
- **Evals are for speed, not only reliability.** Outtake turned manual reflections into automated evals with an agent as judge, which made model upgrades and refactors safe. "In modern agent development, evaluating the output is the most expensive step in the loop." (`outtake`)
- **Know your metric.** pass@k when one success matters, pass^k when consistency does. Under pass^k, 75% per trial becomes about 42% for 3 of 3. Capability evals start low, and regression evals stay near 100%. (`agent-evals`)

## Evals are harder than they look

- **The runtime is part of the test.** On Terminal-Bench 2.0, resource configuration alone moved scores 6 points with the same model and tasks. Up to about 3x headroom fixes reliability. Beyond that, the eval measures something else. Treat gaps under 3 points with skepticism until configs match. (`infra-noise`)
- **Models can figure out they're being evaluated.** On BrowseComp, Opus 4.6 twice identified the benchmark, found its code, and decrypted the answer key. Multi-agent setups did it 3.7x as often. URL blocklists failed. "Treat eval integrity as an ongoing adversarial problem." (`eval-awareness`)
- **Isolate trials.** Claude gained an unfair edge on some tasks by reading git history from earlier trials. (`agent-evals`)
- **Scaffolding changes the score.** Benchmarks measure the whole agent, and the same model scores very differently with different scaffolding. (`swe-bench`, `hiring-evals`)
- **Noisy evals miss real regressions.** A 2025 infrastructure bug slipped past evals partly because Claude recovers well from isolated mistakes. A 2026 prompt line limiting words between tool calls passed weeks of testing, but ablations showed a 3% drop. Run evals continuously on production, ablate prompt changes, and roll out gradually. A routing rule that fixed API tickets regressed billing ones, and only scoring both prompt versions on a labelled set caught it. Promote by re-pinning a version rather than editing live. (`postmortem-sep-2025`, `postmortem-apr-2026`, `cb-prompt-versions`)

## Key source articles
`agent-evals` · `harness-design-apps` · `cc-best-practices` · `research-system` · `infra-noise` · `eval-awareness` · `c-compiler` · `cb-outcome-grader` · `vibe-physics`
