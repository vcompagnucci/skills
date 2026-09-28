---
name: support-evals
description: Build and run evals for a customer-support agent, from reading the first tickets to monitoring production. Use when designing test cases, writing or validating an LLM judge, grading tool calls and account changes, testing escalation, multi-turn, or bilingual conversations, gating a release, or measuring a live agent. Merges Hamel Husain and Shreya Shankar's eval method with Anthropic's, OpenAI's, and support vendors' lessons, conflicts resolved.
---

# Support evals

A process for evaluating a customer-support agent that reads tickets, answers from a help center, and takes actions on customer accounts. It merges the eval method of Hamel Husain and Shreya Shankar with what Anthropic, OpenAI, and support teams (Sierra, Lorikeet, Salesforce, Monzo, Block) published up to September 2026. Where they disagreed, the most recent position won and the older one was deleted, so don't bring it back from memory.

## Where are you?

```
Do you have real conversations or tickets to read?
├── No → references/discover.md (sourcing cases, synthetic data)
└── Yes → Have you read them and named the failure modes?
    ├── No → references/discover.md
    └── Yes → Does each mode have an evaluator you validated against human labels?
        ├── No → references/evaluators.md
        └── Yes → Is the agent live?
            ├── No → references/testing.md (simulation, CI, release gates)
            └── Yes → references/production.md
Whatever the stage, before a check touches handoffs, language, sensitive data,
tools and account state, multi-turn, or policy → references/support-checks.md
```

Open one reference at a time. Each is under 60 lines.

## Rules that hold at every stage

1. **A domain expert decides what counts as a failure, never a model or an annotator.** Everything downstream (judges, CI, monitoring) inherits that definition, and a wrong one is invisible later.
2. **Failure modes are observed in real traces, not brainstormed.** Brainstormed categories produce evaluators for problems the agent doesn't have and miss the ones it does.
3. **Use the cheapest grader that fits.** Code for anything objective (account state, tool arguments, schema, forbidden text). An LLM judge only where interpretation is needed, and a judge never overrides a failed code check. Code is free to run and never drifts.
4. **Grade against ground truth from data or policy, never against the model's own answer.** "Your refund is on its way" fails if the tool only opened a review case.
5. **Gate on the outcome, diagnose with the path.** A case passes when the account and ledger ended exactly as intended and every step compliance requires happened (identity verified, customer confirmed, no forbidden or unrequested action). Tool order and other path details explain failures but never gate, because many valid paths reach the same state.
6. **Run every case more than once.** Agents are nondeterministic. Gate on pass^k (every run passes), never pass@k. At 75% per run, 3 of 3 passes only about 42% of the time.
7. **Keep a held-out set you never tune against.** If train scores rise while held-out stays flat, you are fitting the eval, not improving the agent.
8. **Fix the cause in the right place.** Behavior the prompt never asked for goes into the prompt. A policy, safety, or authorization rule goes into tool code with a test. Appending "never do X" to the prompt after an incident degrades the prompt and doesn't stop X.
9. **Every production failure becomes a permanent test.** Reproduce it, fix it, and keep the case in CI so it can't come back.
10. **Read transcripts before believing any number.** Broken tasks, flaky infrastructure, and miscalibrated judges all look like model failures in a score.
11. **Evals decay.** Re-run error analysis every 2 to 4 weeks on 100+ fresh traces and after every incident, and re-validate a judge after any change to its prompt or model.

## Numbers to use

| Question | Answer |
|---|---|
| First look after a significant change | 20 to 50 outputs, one expert, about 30 minutes |
| Traces a human reads before any agent suggests failure modes | at least 30 |
| When error analysis is done | saturation, around 100 traces |
| Human labels per judge | about 100, balanced; floor 30 Pass and 30 Fail |
| CI suite size | start at 20 to 50 cases, grow past 100 |
| Runs per CI case | 5 |
| Runs to reproduce and verify a production bug fix | 10, or 20 if it was seen once |
| Red-team probes per attack type | 50+ |

## Scope

This skill covers evaluation only. It doesn't cover how to build the agent, write its tone, or secure it, except where a check needs it. Company-specific material (the behavior spec, policies, the failure taxonomy from real tickets) belongs in a private file next to this skill, not in it. Sources and licenses: `references/sources.md`.
