# Discover failures

The goal of this stage is a short list of named, binary failure modes that come from real conversations. No judge or dashboard gets built before it. Code tests for rules you already know are the exception (evaluators.md).

## Before reading anything

- **Check the trace is complete.** Each one holds the whole conversation, the model id, every tool call with its arguments and result, what retrieval returned, and a session id. Group multi-turn conversations by session. A trace missing tool results can't tell a wrong answer from a wrong lookup. Each trace also carries the case id and a hash of the system prompt, so you can group runs by version.
- **List which tools record their call and result.** Provider-run tools (built-in web search, grounding, code execution, hosted retrieval) often never appear in the trace, so tool-use and trajectory judges false-fail them and groundedness judges can't see the source. Leave those tools out of tool-call checks and grade the final answer and its claims instead. Google documents that its multi-turn tool-use judge always fails a search-only agent for this reason.
- **Write the behavior spec as testable requirements with ids.** For each main journey (a failed deposit, a KYC rejection, a withdrawal question), write the ideal conversation in real words, then split it into parts you can test. Link every failure mode you find to a requirement id. When a failure has no requirement, fix the spec before building an evaluator. You can't grade a behavior nobody defined.

## Where cases come from, in this order

1. Real tickets and production transcripts, after checking retention rules and who may see sensitive data (see support-checks.md).
2. Bug reports and escalations.
3. 5 to 10 cases written by hand for journeys you know matter.
4. Synthetic cases anchored in real ones, only to fill what the first three don't cover. Pure synthetic only for a flow with no ticket history.

Real tickets come first because synthetic users are more cooperative and articulate than real customers, and a suite built on them skews easy. User traffic alone also skews easy, so add hard cases a person picked.

**Pick hard cases because a person judged them hard, never because today's model fails them.** A set built from one model's failures measures that model's weak spots, and it stops meaning anything when the model changes. A failure found by search can enter the suite only after a human reviews it and rewrites it as the general case it stands for.

**Pair every should-do case with a should-not case.** Escalate and don't escalate, act and don't act, answer and abstain. Without the negatives, an agent that escalates everything scores perfectly on escalation.

**A tool, skill, or specialist the agent must choose starts with 10 to 20 cases** covering explicit requests, implicit ones, ones that depend on context, and negative controls: adjacent requests that must not trigger it. Log each run as structured events and check the choice in code over those events before adding any judge.

**Keep a coverage pool and a challenge pool, reported separately.** Routine successes in the same average hide how the agent does on edge cases.

## Reading traces

0. **First look after every significant change.** One domain expert reads 20 to 50 outputs in about 30 minutes before any coding round. It's the cheapest check that a prompt, model, or tool change broke nothing obvious.
1. **Open coding.** One expert reads each trace in the review app (review-app.md) and writes a free-text note on the first failure only, then moves on. The first failure is the earliest step that breaks a requirement or makes a later failure materially more likely. A trace with none gets the note "no failure observed", so a reviewed trace is never mistaken for an unreviewed one. No predefined labels, because they make you see what you expected. Note problems that aren't the model's fault too (missing article, broken tool).
2. **Sample a mix.** Random, plus representatives of clusters, plus a product dimension (language, intent), plus outliers, plus traces with customer feedback. Never only the traces a model or heuristic predicts will fail.
3. **Let an agent help only after 30 human-read traces.** Its suggestions before that replace your judgment instead of informing it. The human accepts or dismisses every suggestion, and re-reads earlier traces when the criteria shift.
4. **Check an assisting agent's work mechanically.** Count the share of traces it actually coded (agents stop early and declare done), the share of codes used only once (paraphrase instead of grouping), whether its code count tracks trace length, and whether it re-applied your feedback to earlier traces. Reject categories no fix could be tested against, and review its output in rounds of about 10 items. On 451 items agents coded 6% to 68% of them, and 93.8% to 100% of their codes were used once.
5. **Axial coding.** Group the notes into 5 to 8 binary failure modes. Merge two notes when one product change would fix both, and split a mode when its examples need different fixes. Each mode needs at least 3 clear examples and 3 close non-examples, and records: a snake_case name, a binary definition another reviewer can apply, the notes it came from, its boundary with the nearest mode, the likely grader (code or judge), and the requirement id.
6. **Stop at saturation,** around 100 traces. A final batch of 15 that adds no new mode confirms it.
7. **Label every trace against every final mode.** Go back and record Pass or Fail for each trace and mode. A trace can fail several. You validate judges against these labels. Report counts as sample fractions, never as prevalence. Clustering and targeted searches enrich the sample on purpose. Prevalence comes only from a random sample (production.md).

## Synthetic scenarios

- Define dimensions tied to a failure hypothesis (intent, customer state, language, how much the customer withholds), have a human approve the combinations, then generate in two steps, the combination first and the conversation second.
- Record the expected outcome from the database or the policy, with the source it came from, and keep those facts out of what the simulated customer is told. Otherwise the customer leaks the answer.
- Generate each conversation in its own model call, several in parallel. One call for the whole set repeats structure and phrasing. Give the generator the role, goal, style, facts the customer would know, and turn count. Never ids, exact dates, internal rules, or the expected outcome.
- Run an independent critic on each conversation that flags four things: invented ids, amounts, or dates, follow-ups that assume the agent's reply, shared openings, and customers quoting internal policy names. Hand-check 10 of the critic's flags before trusting it.
- Scenarios that write (a withdrawal, a refund) each use a different record, so one run's side effect can't change another's expected outcome.
- **Rates from generated scenarios or an eliciting simulator are comparisons, never prevalence.** Compare versions only under the same generator config, seed, and grader, and cite that config with every number. In Anthropic's tests absolute rates moved with generator settings while model rankings held, and a simulator that pushes for failures gave rates "likely higher than a fixed environment would produce".
- **Pilot before the full set.** Reset state, run about 30 scenarios on the model you'll use, and review at least 10. A failure counts only when the scenario is valid and the behavior contradicts its recorded expectation or a requirement, with the evidence named. Require at least 5 valid failures before generating the rest. If there are fewer, add challenge scenarios a person judges hard. Never swap the model under test to produce failures, and never copy the requests that happened to fail.

## Before building an evaluator

Fix what's cheap first. If the prompt never asked for the behavior, add the instruction and re-check. If the failure breaks a policy, safety, or authorization rule, move the rule into tool code with a test. Build evaluators only for the failures that survive.
