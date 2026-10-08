# Monitor production

## Measure the rate

- **Code checks on every trace, frozen per-mode judges on a random sample** sized from the interval the decision needs (Wilson sizing in statistics.md), with a cap per run for cost. Judge every trace only where each verdict triggers its own action, such as a support team's per-ticket QA review. Never use one holistic auditor. Run the same checks on the same work done by people (in support, human agents' tickets), so you compare the agent with the team and not with perfection, with the judge calibrated on each side (judges.md).
- **Estimate the failure rate only from a random sample,** then correct it for the judge's error with the Rogan-Gladen formula and bootstrap interval in statistics.md, using TPR and TNR from the frozen judge's test split. Risk groups (traces with writes, policy lookups, long conversations) are for inspection, never for the rate, because you picked them for failing more.
- **Check that the judge beats direct labeling before relying on its corrected rate** (statistics.md). An 80/80 judge never does, and a 90/90 judge only for true pass rates between 24% and 76%, while most support modes pass more often. Outside that range, have the expert label a random sample directly, report it with a Wilson interval, and keep the judge for triage, alerts, and regression gates.
- Judge the random sample and the risk groups in one pass but store them apart, and give every score a stable id so reruns don't double count. An empty window reports "no data", never a rate.
- **Fix the alert threshold before looking at results.** Alert when the lower bound of the interval crosses it, not the point estimate. A crossing starts a new round of error analysis and adds CI cases.
- **Pick risk groups from trace evidence** (a tool wrote something, the agent looked up a policy), not from what the reply says.
- **Make the out-of-scope bucket a risk group.** Review a sample of the conversations the agent labeled out of scope, unsupported, or refused, every round. Every judge scores these as polite, correct refusals, so unmet demand never shows up in a rate.
- **Reject a monitoring period whose traces came from a different model** than the one you validated the judge on.
- **Check what a managed evaluation job silently drops before reading its number.** Fail any case missing its expected answer instead of letting the grader judge without it, never take a rate from the most recent N sessions, report errored sessions and evaluators next to the average, wait for telemetry to finish ingesting, and confirm multi-agent traces are scored against the intended agent.

## Outcomes, not satisfaction

- **Measure resolution, don't assume it.** In a support agent, count customers who come back on the same issue within 7 days. A conversation that ends without a handoff isn't resolved. One team that believed it resolved 40% found 20% on full review, the rest were abandonments.
- **Never use satisfaction as a proxy for resolution** (CSAT, a "was the customer satisfied" judge, a simulated user's rating). A blind human panel rated satisfied 57.5% of conversations that had failed the task, and a transcript cut off mid-task got the highest rating of any degraded version. Gate on the verified outcome, and validate the outcome check against expert review of outcomes, never against satisfaction.
- **Measure what the automated checks miss against a golden baseline.** Every error-analysis round, have experts review, blind, a mix of runs the checks passed and work your best people did on the same kinds of cases (in support, tickets your best human agents resolved). Report the agent's acceptance as a share of the human items' acceptance: reviewers accepted only 68% of known-good human work, and normalized, accepted agent work about 24 points less often than the grader passed it.

## Monitors

- **Evaluate the monitors too.** A monitor judge (for frustration, for policy breaks) needs the same validation as any judge, with its rationale shown on every flag.
- **Matching every human report proves nothing about misses.** Estimate a monitor's recall with planted failures, and track its coverage (the share of traffic it sees), review latency, and severity tiers. A monitor that flagged every case employees reported still can't say what it misses: false negatives can't be measured without planted failures.
- **Run policy, safety, and authorization monitors on two views and alert if either flags:** one with the agent's reasoning, one with only user turns, tool calls, and tool results. Reasoning helps a monitor catch process failures, but a rationalization in it can talk the monitor out of a flag: one flagged about 1% of a harmful agent's actions because its reasoning called the environment simulated, against about 50% on the actions-only view. Red-team monitors with transcripts where the agent justifies the action ("the customer authorized this").
- **Calibrate a monitor on benign twins.** Remove the bad action from each bad transcript, set the threshold on the twins at a 1% false-positive rate, and report the catch rate per trial and as caught in any of N trials. At a 1% false-positive rate, monitors caught 0% of omissions and multi-hop reasoning, so required steps (identity verified, confirmation given) belong in code checks.

## The serving path

- **Run the frozen eval continuously on the real serving path,** on the exact build users get, and tag every request with its config and change set. Infrastructure changes degrade output with no model or prompt change, and overlapping changes on different traffic slices look like inconsistent degradation: a caching bug passed review, unit, end-to-end, and automated tests and dogfooding, and took over a week to find.
- **Ablate every system-prompt change line by line on a broad per-model suite.** A verbosity line passed weeks of internal evals, then a line-by-line ablation showed a 3% drop on two models.

## Live experiments

- **Offline evals don't replace A/B tests on live traffic.** Evals choose what enters an experiment, and the experiment confirms the effect on real outcomes.
- **Treat latency as a confounder.** If a variant changes response time as a side effect, add a third arm with its behavior at the control's latency, and check for sample-ratio mismatch before reading results. Added delays of 5 to 20 seconds alone raised resolution by up to 2 points.
- **Report policy adherence next to resolution in every experiment,** because following configured rules more faithfully can lower immediate resolution (more questions, more steps). When a component filters what the model sees (rules, tools, procedures), keep a small slice of traffic with the filter off, for unbiased labels on what it drops.
