# Simulate, test, and gate releases

## The test environment

- **A stateful sandbox, reset for every trial.** Writes must be real (a withdrawal changes a fake ledger), and one trial must never see another's leftovers. An agent that reads a previous run's state gets the answer for free.
- **Three layers of tests.**
  1. Pure rules as unit tests (a withdrawal limit, a KYC gate), no model involved.
  2. The agent loop with a scripted model, to prove the plumbing, such as the tool result reaching the context or an approval pause resuming the same run.
  3. End-to-end runs with the real model.
  A failure in layer 3 that layer 2 would have caught costs a model run to find.
- **Close shortcuts by rule, not by removing tools.** If the sandbox lets the agent read the answer (an already-resolved ticket, a seeded ledger note), keep the tool, state in the case what use is legitimate, and have a trace check score the run 0 when it's crossed, even if the attempt failed. Blocking tools instead turned into a 1,200-entry blocklist the agents spent 20+ turns routing around.

## Simulated customers

```
Must runs be comparable across versions? (CI, regression)
├── Yes → scripted follow-ups, written before the run, each plausible whatever the agent says
└── No → adaptive simulated user with a persona
    (capability tests, cases where the customer must act in the app, exploration)
```

**Replay real prefixes first.** For a multi-turn case, take the first N-1 turns of a real ticket and let the agent write only turn N. It tests the hard turn with real wording and no simulator drift. Use a simulated customer only when the agent's earlier turns must be allowed to vary. Prefixes are production data, so the retention rules in support-checks.md apply.

**Calibrate the simulator before trusting it.** Run the frozen judges on simulated conversations and on a random sample of real ones for the same intents. If the real pass rate falls below the simulated rate's 95% interval, the simulated customer is too easy. Make it write in fragments, leave out context, repeat itself, and give it the goals real customers bring: a refund, a human, distrust of the bot. Vary language, patience, how much they withhold, whether they start logged in, and whether they correct the agent's mistakes or retry after an error. A simulator that corrects the agent hides its failures.

**Grade the simulator before the agent.** Check each simulated turn against the case's plan and persona, and discard a run where the simulator broke them. Otherwise its mistakes count as the agent's.

**Check that the model didn't notice the test.** Models can tell a simulated run from real traffic. When OpenAI replayed 49,650 real tasks with a new model, 2.5% to 8.7% of the runs showed signs the model knew it was being tested, against 0.76% in the original traffic. Have a judge flag those signs, rerun the comparison without the flagged runs, and trust the result only if it holds.

## Runs and metrics

- 15 runs per case in CI, because a case that fails 1 run in 20 still passes 15 of 15 only 46% of the time, so it shows up instead of hiding. Gate on pass^k, where a case passes only if every run passes. pass@k (any run passes) is for exploring what the agent can do, never for gating.
- Reliability drops with repetition: 9 successes in 10 gives about a one-in-three chance of 10 clean runs. Expect the gap and design for it.
- **Estimate from n runs, don't rerun k times.** With c passes in n runs: pass@k = 1 - C(n-c, k) / C(n, k), and pass^k = C(c, k) / C(n, k). Check: 6 of 8 gives pass@2 = 0.964 and pass^4 = 0.214.
- **Rerun only infrastructure errors** (timeout, missing trace, no reward), never a failed verdict. A red regression case is evidence to read, not noise to retry. Don't classify a case from a baseline with an infrastructure error, and never change a classification to get the mix you want.
- **Tag every failed attempt** as infrastructure error, timeout, refusal, or real failure, and leave answers cut off by the token limit out of the mean. Before citing a gap between two models, set aside failures only one model triggers: they're usually harness bugs. Check that each response came from the model you requested, and fail the attempt if not.
- **Infrastructure alone moved an agent benchmark 6 points.** Fix each case's resource limits, spread runs over more than one day, and don't trust a difference under 3 points even when the noise band in improve.md is narrower.

## Red team

- **Trigger each error once before building its eval.** An eval for an attack you can't reproduce tests nothing.
- Attack through every untrusted input: retrieved articles, transaction memos, uploaded documents, other customers' data, jailbreaks, and escalation over several turns. 50+ probes per attack type.
- Sort each finding into blocked by code, newly defended, or accepted risk with a written reason. Nothing stays unsorted.
- Confirm each finding in the trace and the database, never on a scanner's verdict alone. A scanner can't see whether protected state changed. Load attack fixtures only into a throwaway copy of the data.
- Include exfiltration through retrieved content: a planted article asking the agent to add a link or image carrying customer data. Strip links and images to non-allowlisted hosts on output.

## Release gates

```
Did this case pass all 15 baseline runs?
├── Yes → regression case: must stay at 100%, any failed run blocks the release
└── No → capability case: report the score, never block
```

- **CI holds** core journeys, every past production bug, and known edge cases, with a code check for every case whose outcome is objective, plus a holdout you run but never tune against, and a rolling set of recent production failures.
- **Cadence.** Cheap checks on every change, expensive judges nightly and before each release. A capability case that starts passing every run graduates to regression. Never retire a regression case, because it's what stops an old bug from coming back.
- **Case record:** id, failure mode, input (role, user, opening message, scripted follow-ups), initial state, `checks` (code), `judges` (frozen judge and expected verdict), `assertions` (plain-language intent, never scored). Add `kind` and the baseline pass rate after the 15 baseline runs.
- **Prove every case is solvable.** Before a case enters CI, run a reference solution (a scripted run or a person using the same tools) in the reset sandbox and confirm it reaches the expected state. Store it in the case record as `reference`. If it can't reach the state, the case is broken, not the agent. A case is also broken if two domain experts would reach different verdicts on the same run, or if the grader checks something the case never asked for.
- **Quality gates come before cost.** Policy compliance, action correctness, security, and escalation accuracy must pass before you compare cost or latency. Among passed cases only, report step, tool-call, and latency ratios against an ideal run (observed divided by the fewest calls a correct run needs). Use them to compare versions that already pass. They never fail a case, because rule 5 keeps the path out of the gate. Count cost per resolved case, retries and fallbacks included: a published benchmark cost that left out fallbacks, which happened on about 40% of tasks, understated the real cost. Set the latency limit from when real users give up (the distribution of time until they abandon), not from a round number.
- **Every model change reruns a broken-tool case.** Make a tool fail and check that the agent tells the customer instead of answering as if it worked. On OpenAI's broken-search test, a small model hid the failure in 28.7% of cases and a large one in 1.5%, so the cheaper model is where to look.
- **A ship decision on a rate needs the interval, not the point.** Ship only if the upper bound of the 95% Wilson interval is below the requirement. With x of n (failures for a ship decision), p = x/n and z = 1.96: center = (p + z²/2n) / (1 + z²/n), half-width = z / (1 + z²/n) × √(p(1-p)/n + z²/4n²). Check: 16 of 20 gives 0.584 to 0.919. Size the sample first: at 3% observed against a 5% limit, 200 samples can't prove it and about 800 can. Halving the margin takes four times the samples.
- **Release one versioned bundle.** Prompt, model, tools, and the help-center snapshot ship together and roll back together. Promote by re-pinning, with the required simulations passed, a named approver from compliance or CX, and a gradual rollout.
- **Production bugs.** Reproduce with 10 runs (20 if seen once), fix, verify with the same number of runs, then add the case and a paraphrased variant to CI. One green run proves nothing for a nondeterministic bug.
