---
name: agent-evals
description: Build and run evals for an AI agent, from reading the first conversations to monitoring production, with extra checks for customer-support agents. Use when designing test cases, reviewing traces for failure modes, writing or validating an LLM judge, grading tool calls and resulting state, testing escalation, multi-turn, or bilingual conversations, evaluating retrieval, gating a release, auditing an existing eval setup, or measuring a live agent. Merges Hamel Husain and Shreya Shankar's eval method with Anthropic's, OpenAI's, and support teams' lessons, conflicts resolved.
---

# Agent evals

A process for evaluating an AI agent that talks to people, looks things up, and takes actions. Examples lean on customer support, where these teams tested the method hardest. It merges the eval method of Hamel Husain and Shreya Shankar with what Anthropic, OpenAI, and support teams (Sierra, Lorikeet, Salesforce, Monzo, Block) published up to September 2026. Where they disagreed, the most recent position won and the older one is gone, so don't bring it back from memory.

## Where are you?

Inheriting an eval setup, or unsure you can trust it? → references/audit.md first. Changing the prompt, tools, harness, or model to raise a score, or comparing versions or models on accuracy and cost → references/improve.md.

```
Is there an agent yet?
├── No → references/discover.md, "Before reading anything" and "Where cases come from" only:
│   use old tickets to write the spec and the cases. Error analysis reads the
│   agent's answers, so it starts once the agent runs on those cases.
└── Yes ↓
Do you have real conversations or tickets to read?
├── No → references/discover.md (sourcing cases, synthetic data)
└── Yes → Have you read them and named the failure modes?
    ├── No → references/discover.md
    └── Yes → Does each mode have an evaluator you validated against human labels?
        ├── No → references/evaluators.md
        └── Yes → Is the agent live?
            ├── No → references/testing.md (simulation, CI, release gates)
            └── Yes → references/production.md
Customer-facing agent? Before a check touches handoffs, language, sensitive data, tools and account state, multi-turn, or policy → references/support-checks.md
```

The stages point to three tools:
- references/review-app.md, the app a human reviews traces in
- references/judge-prompt.md, the judge template
- references/retrieval.md, search and knowledge-base evals

Open one reference at a time. **Never compute a formula from memory** (corrected failure rate, bootstrap interval, pass@k, pass^k). Copy it from production.md or testing.md and run its check value first. Sources count the positive class in opposite directions, so a remembered formula silently gives the wrong rate.

## Rules that hold at every stage

1. **A domain expert decides what counts as a failure, never a model or an annotator.** Everything downstream (judges, CI, monitoring) inherits that definition, and a wrong one is invisible later.
2. **Failure modes come from real traces, never from brainstorming.** Brainstormed categories produce evaluators for problems the agent doesn't have and miss the ones it does.
3. **Use the cheapest grader that fits.** Code for anything objective (account state, tool arguments, schema, forbidden text). An LLM judge only where interpretation is needed, and a judge never overrides a failed code check. Code is free to run and never drifts.
4. **Grade against ground truth from data or policy, never against the model's own answer.** "Your refund is on its way" fails if the tool only opened a review case.
5. **Gate on the outcome, diagnose with the path.** A case passes when the system state ended exactly as intended (for a support agent, the account and ledger) and every step compliance requires happened (identity verified, customer confirmed, no forbidden or unrequested action). Tool order and other path details explain failures but never gate, because many valid paths reach the same state.
6. **Run every case more than once.** Agents are nondeterministic. Gate on pass^k (every run passes), never pass@k. At 75% per run, 3 of 3 passes only about 42% of the time.
7. **Score the held-out test set once, after freezing the final version.** Tune only on development cases. Once you read test results, those cases are development knowledge, and any later change needs a new test set.
8. **Fix the cause in the right place.** Behavior the prompt never asked for goes into the prompt. A policy, safety, or authorization rule goes into tool code with a test. Appending "never do X" to the prompt after an incident degrades the prompt and doesn't stop X.
9. **Every production failure becomes a permanent test.** Reproduce it, fix it, and keep the case in CI so it can't come back.
10. **Read transcripts before believing any number.** Broken tasks, flaky infrastructure, and miscalibrated judges all look like model failures in a score.
11. **Evals decay.** Re-run error analysis every 2 to 4 weeks on 100+ fresh traces and after every incident, and re-validate a judge after any change to its prompt or model.
12. **Before any paid batch, show the model, the number of agent runs, and the number of judge calls, and wait for approval.** Baselines and judge sweeps multiply fast.

## Numbers to use

| Question | Answer |
|---|---|
| First look after a significant change | 20 to 50 outputs, one expert, about 30 minutes |
| Traces a human reads before any agent suggests failure modes | at least 30 |
| When error analysis is done | saturation, around 100 traces |
| Human labels per judge | about 100, balanced, never under 30 Pass and 30 Fail |
| CI suite size | start at 20 to 50 cases, grow past 100 |
| Runs per CI case | 5 |
| Runs to reproduce and verify a production bug fix | 10, or 20 if it was seen once |
| Red-team probes per attack type | 50+ |

## Scope

This skill covers evaluation only. It doesn't cover how to build the agent, write its tone, or secure it, except where a check needs it. Company-specific material (the behavior spec, policies, the failure taxonomy from real conversations) belongs in a private skill, never in this one. Sources and licenses: `references/sources.md`.
