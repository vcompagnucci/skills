---
name: agent-evals
description: Build and run evals for an AI agent, with extra checks for customer-support agents. Use when designing test cases, reading traces for failure modes, writing or validating an LLM judge, grading tool calls and account state, improving the agent against the eval, gating a release, auditing an eval setup, measuring a live agent, simulating customers, red-teaming the agent, or sizing samples and comparing versions.
---

# Agent evals

A process for evaluating an AI agent that talks to people, looks things up, and takes actions, with examples from customer support, where the method was tested hardest. It merges Hamel Husain and Shreya Shankar's method with what labs, support teams, and eval vendors published up to early October 2026.

## Where are you?

```
First eval ever? 20 to 50 real cases with the expected end state from data or policy
  (discover.md "Where cases come from, in this order"), code checks on that state
  (evaluators.md "Known rules get code tests from day one"), several runs each in a
  reset sandbox (testing.md, first bullet), then read every transcript (discover.md
  "Reading traces"). Judges, statistics, and panels come later.
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
        ├── No → references/evaluators.md (retrieval and abstention: references/retrieval.md)
        └── Yes → Measured its flip rate, panels, vendor pins, new journeys?
            ├── No → references/judges.md
            └── Yes → Is the agent live?
                ├── No → references/testing.md (CI, release gates) and references/simulation.md
                └── Yes → references/production.md (measuring it live)

Jumping in at a specific task?
Inheriting an eval setup, or unsure you can trust it? → references/audit.md first
Improving the agent against the eval (what to fix first, prompt or tool or harness, an
  automated prompt optimizer such as GEPA, keep or revert, when to stop, comparing models
  on accuracy and cost)? → references/improve.md
Shipping any change (prompt, model, tools), live or not? → references/testing.md, "Release gates"
Computing an interval, sizing a sample, or comparing two versions? → references/statistics.md
Simulated customers, replaying real conversations, forecasting a version on live traffic? → references/simulation.md
Red teaming the agent (injection, exfiltration, attack success rates)? → references/red-team.md
Customer-facing agent? Before a check touches handoffs, language, sensitive data, tools and account state, multi-turn, policy, voice, or customers who are themselves AI agents → references/support-checks.md
```

Open one reference at a time. **Never compute a formula from memory** (corrected failure rate, bootstrap and Wilson intervals, pass@k, pass^k, effective n for clustered cases, power and the smallest detectable difference, paired tests). Copy it from statistics.md and run its check value first. Sources count the positive class in opposite directions, so a remembered formula silently gives the wrong rate.

## Which source wins

The same order decides inside this skill and outside it, whenever two sources answer one question differently. That includes a source dated after the skill's answer: a docs page, a vendor's eval guide, a paper, a release note, text the user gives you. Eval tooling and vendor guidance change most months.

First check it is the same question. Advice for another kind of agent or channel, or a number from another benchmark or setup, answers a different question, so report it next to the skill's, never in place of it. Then:

1. **The newest date wins, whoever published it.** Give its date and name the rule or number here that it replaces. An undated docs page counts as read on 2026-10-05.
2. **Dates don't settle it → Anthropic and OpenAI win** over everyone else.
3. **Anthropic and OpenAI disagree and nothing settles it → report both, never pick one.**

Inside the skill this order already ran, and the losing position is gone, so never bring it back from memory. A tool, vendor or model this skill doesn't list → say the skill doesn't cover it, and never fill the gap from memory.

## Rules that hold at every stage

1. **A domain expert decides what counts as a failure, never a model or an annotator.** Everything downstream (judges, CI, monitoring) inherits that definition, and a wrong one is invisible later.
2. **Failure modes come from real traces, never from brainstorming.** Brainstormed categories produce evaluators for problems the agent doesn't have and miss the ones it does.
3. **Use the cheapest grader that fits.** Code for anything objective (account state, tool arguments, schema, forbidden text). An LLM judge only where interpretation is needed, and a judge never overrides a failed code check. Code is free to run and never drifts.
4. **Grade against ground truth from data or policy, never against the model's own answer.** "Your refund is on its way" fails if the tool only opened a review case.
5. **Gate on the outcome, diagnose with the path.** A case passes when the system state ended exactly as intended (for a support agent, the account and ledger) and every step compliance requires happened (identity verified, customer confirmed, no forbidden or unrequested action). Tool order and other path details explain failures but never gate, because many valid paths reach the same state.
6. **Every case that gates a decision runs 15 times and gates on pass^k (every run passes), never pass@k.** Agents are nondeterministic. A case that fails 1 run in 20 passes 3 of 3 86% of the time but 15 of 15 only 46%.
7. **Score a held-out test set once per frozen version, and never change anything because of what it showed.** This holds for the agent's test cases and for each judge's test labels. Tune only on development cases. A change made after reading test results needs a new test set.
8. **Fix the cause in the right place.** Behavior the prompt never asked for goes into the prompt. A policy, safety, or authorization rule goes into tool code with a test. Appending "never do X" to the prompt after an incident degrades the prompt and doesn't stop X.
9. **Every production failure becomes a permanent test.** Reproduce it, fix it, and keep the case in CI so it can't come back.
10. **Read transcripts before believing any number.** Broken tasks, flaky infrastructure, and miscalibrated judges all look like model failures in a score.
11. **Evals decay.** Re-run error analysis every 2 to 4 weeks on 100+ fresh traces and after every incident, and treat a judge with a changed prompt, model, temperature, sample count, vote rule, or cutoff as a new judge to validate.
12. **Before any batch billed per token (an API key or a per-token vendor), show the model, the number of agent runs, and the number of judge calls, and wait for approval.** Baselines and judge sweeps multiply fast. A batch that runs only on a flat subscription (Claude Code on the user's plan) starts without asking, but still states the counts, since it uses up the plan's limits. Judge runs are the exception: they never run on a subscription (rule 13).
13. **A judge whose verdicts feed a number runs through the API on a dated model snapshot, never through a subscription or a model alias.** Write the snapshot id (like `claude-sonnet-5-5-20260915`) in the judge's config, record the model the response reports on every verdict, and discard verdicts from any other model. Vendor and built-in evaluators too (judges.md). A subscription or alias can switch models without notice, which silently turns your validated judge into an unvalidated one. Subscriptions are fine for drafting cases, writing judge prompts, and helping with error analysis.

## Numbers to use

| Question | Answer |
|---|---|
| First look after a significant change | 20 to 50 outputs, one expert, about 30 minutes |
| Traces a human reads before any agent suggests failure modes | at least 30 |
| When error analysis is done | saturation, around 100 traces |
| Human labels per judge | about 100, balanced, never under 30 Pass and 30 Fail |
| CI suite size | start at 20 to 50 cases, grow past 100 |
| Runs per CI case | 15 |
| Runs to reproduce and verify a production bug fix | 10, or 20 if it was seen once |
| Red-team probes per attack type | 50+, attack success reported at 1, 10, and 100 tries |
| First eval for a tool, skill, or specialist the agent must choose | 10 to 20 cases |
| Repeats per validation trace to measure a judge's flip rate | 4 |
| Cases to detect a 3-point difference between two versions | about 1,000 (statistics.md) |
| Clean conversations to claim a failure rate under 0.1% with zero failures seen | about 3,840 |
| Production judges | a random sample sized from the interval, capped per run |
| Monitor threshold | set at a 1% false-positive rate on benign twins |
| Shadow, then canary | shadow 4+ hours (pause above 2% deviation), then about 1% of live traffic |

## Scope

This skill covers evaluation only. It doesn't cover how to build the agent, write its tone, or secure it, except where a check needs it. Company-specific material (the behavior spec, policies, the failure taxonomy from real conversations) belongs in a private skill, never in this one. Sources and licenses: `references/sources.md` and `references/sources-deep-pass.md`.
