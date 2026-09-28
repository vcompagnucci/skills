# Simulate, test, and gate releases

## The test environment

- **A stateful sandbox, reset for every trial.** Writes must be real (a withdrawal changes a fake ledger), and one trial must never see another's leftovers: an agent that reads a previous run's state gets the answer for free.
- **Three layers of tests.**
  1. Pure rules as unit tests (a withdrawal limit, a KYC gate), no model involved.
  2. The agent loop with a scripted model, to prove the plumbing: the tool result reaches the context, an approval pause resumes the same run.
  3. End-to-end runs with the real model.
  A failure in layer 3 that layer 2 would have caught costs a model run to find.

## Simulated customers

```
Must runs be comparable across versions? (CI, regression)
├── Yes → scripted follow-ups, written before the run, each plausible whatever the agent says
└── No → adaptive simulated user with a persona
    (capability tests, cases where the customer must act in the app, exploration)
```

Check adaptive users against real tickets for realism. Vary language, patience, how much they withhold, and whether they start logged in.

## Runs and metrics

- 5 runs per case in CI. Gate on pass^k: a case passes only if every run passes. pass@k (any run passes) is for exploring what the agent can do, never for gating.
- Reliability drops with repetition: 9 successes in 10 gives about a one-in-three chance of 10 clean runs. Expect the gap and design for it.

## Red team

- **Trigger each error once before building its eval.** An eval for an attack you can't reproduce tests nothing.
- Attack through every untrusted input: retrieved articles, transaction memos, uploaded documents, other customers' data, jailbreaks, and escalation over several turns. 50+ probes per attack type.
- Sort each finding into blocked by code, newly defended, or accepted risk with a written reason. Nothing stays unsorted.

## Improving against the eval

Change one thing at a time and keep it only if the held-out set improves too. First check that the eval's run-to-run noise is smaller than the smallest gain you'd act on, or add cases and repetitions. Prompts, skills, and tool descriptions are cheap to change and revert. Harness code isn't. Never paste failing transcripts into the prompt. When the score stalls for 2 or 3 rounds, stop editing and sort every remaining failure by cause: that finds broken cases and graders.

## Release gates

```
Did this case pass all 5 baseline runs?
├── Yes → regression case: must stay at 100%, any failed run blocks the release
└── No → capability case: report the score, never block
```

- **CI holds** core journeys, every past production bug, and known edge cases, with a code check for every case whose outcome is objective, plus an untouched holdout and a rolling set of recent production failures.
- **Cadence.** Cheap checks on every change, expensive judges nightly and before each release. Retire or harden cases that always pass: they cost time and catch nothing.
- **Quality gates come before cost.** Policy compliance, action correctness, security, and escalation accuracy must pass before cost or latency is compared.
- **Release one versioned bundle.** Prompt, model, tools, and the help-center snapshot ship together and roll back together. Promote by re-pinning, with the required simulations passed, a named approver from compliance or CX, and a gradual rollout.
- **Production bugs.** Reproduce with 10 runs (20 if seen once), fix, verify with the same number of runs, then add the case and a paraphrased variant to CI. One green run proves nothing for a nondeterministic bug.
