# Discover failures

The goal of this stage is a short list of named, binary failure modes that come from real conversations. Nothing gets built before it.

## Before reading anything

- **Check the trace is complete.** Each one holds the whole conversation, the model id, every tool call with its arguments and result, what retrieval returned, and a session id. Group multi-turn conversations by session. A trace missing tool results can't tell a wrong answer from a wrong lookup. Each trace also carries the case id and a hash of the system prompt, so you can group runs by version.
- **Write the behavior spec as testable requirements with ids.** For each main journey (a failed deposit, a KYC rejection, a withdrawal question), write the ideal conversation in real words, then split it into parts you can test. Link every failure mode you find to a requirement id. When a failure has no requirement, fix the spec before building an evaluator. You can't grade a behavior nobody defined.

## Where cases come from, in this order

1. Real tickets and production transcripts, after checking retention rules and who may see sensitive data (see support-checks.md).
2. Bug reports and escalations.
3. 5 to 10 cases written by hand for journeys you know matter.
4. Synthetic cases anchored in real ones, only to fill what the first three don't cover. Pure synthetic only for a flow with no ticket history.

Real tickets come first because synthetic users are more cooperative and articulate than real customers, and a suite built on them skews easy. User traffic alone also skews easy, so add hard cases a person picked.

**Pick hard cases because a person judged them hard, never because today's model fails them.** A set built from one model's failures measures that model's weak spots, and it stops meaning anything when the model changes. A failure found by search can enter the suite only after a human reviews it and rewrites it as the general case it stands for.

**Pair every should-do case with a should-not case.** Escalate and don't escalate, act and don't act, answer and abstain. Without the negatives, an agent that escalates everything scores perfectly on escalation.

**Keep a coverage pool and a challenge pool, reported separately.** Routine successes in the same average hide how the agent does on edge cases.

## Synthetic scenarios

- Define dimensions tied to a failure hypothesis (intent, customer state, language, how much the customer withholds), have a human approve the combinations, then generate in two steps, the combination first and the conversation second.
- Record the expected outcome from the database or the policy, with the source it came from, and keep those facts out of what the simulated customer is told. Otherwise the customer leaks the answer.
- Generate each conversation in its own model call, several in parallel. One call for the whole set repeats structure and phrasing. Give the generator the role, goal, style, facts the customer would know, and turn count. Never ids, exact dates, internal rules, or the expected outcome.
- Run an independent critic on each conversation that flags four things: invented ids, amounts, or dates, follow-ups that assume the agent's reply, shared openings, and customers quoting internal policy names.
- Scenarios that write (a withdrawal, a refund) each use a different record, so one run's side effect can't change another's expected outcome.
- **Pilot before the full set.** Reset state, run about 30 scenarios on the model you'll use, and review at least 10. A failure counts only when the scenario is valid and the behavior contradicts its recorded expectation or a requirement, with the evidence named. Require at least 5 before generating the rest. If there are fewer, add challenge scenarios from the hard dimensions or use a weaker model from the same provider. Never copy the requests that happened to fail.

## Reading traces

1. **Open coding.** One expert reads each trace in the review app (review-app.md) and writes a free-text note on the first failure only, then moves on. The first failure is the earliest step that breaks a requirement or makes a later failure materially more likely. A trace with none gets the note "no failure observed", so a reviewed trace is never mistaken for an unreviewed one. No predefined labels, because they make you see what you expected. Note problems that aren't the model's fault too (missing article, broken tool).
2. **Sample a mix.** Random, plus representatives of clusters, plus a product dimension (language, intent), plus outliers, plus traces with customer feedback. Never only the traces a model or heuristic predicts will fail.
3. **Let an agent help only after 30 human-read traces.** Its suggestions before that replace your judgment instead of informing it. The human accepts or dismisses every suggestion, and re-reads earlier traces when the criteria shift.
4. **Axial coding.** Group the notes into 5 to 8 binary failure modes. Merge two notes when one product change would fix both, and split a mode when its examples need different fixes. Each mode needs at least 3 clear examples and 3 close non-examples, and records: a snake_case name, a binary definition another reviewer can apply, the notes it came from, its boundary with the nearest mode, the likely grader (code or judge), and the requirement id.
5. **Stop at saturation,** around 100 traces. A final batch of 15 that adds no new mode confirms it.
6. **Label every trace against every final mode.** Go back and record Pass or Fail for each trace and mode. A trace can fail several. You validate judges against these labels. Report counts as sample fractions, never as prevalence. Clustering and targeted searches enrich the sample on purpose. Prevalence comes only from a random sample (production.md).

## Before building an evaluator

Fix what's cheap first. If the prompt never asked for the behavior, add the instruction and re-check. If the failure breaks a policy, safety, or authorization rule, move the rule into tool code with a test. Build evaluators only for the failures that survive.
