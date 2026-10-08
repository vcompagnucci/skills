# Judge reliability

Agreement with expert labels (evaluators.md) shows a judge was right on past traces. Check everything here before a number it produces decides anything.

## Repeatability

- **Grade every validation trace at least 4 times with the frozen judge and report the flip rate,** the share of traces whose verdict changes. Pin the judge's temperature in its config (0 where the API accepts it) and turn response caching off, or the repeats replay one answer. This setting is the judge's only: the agent under test keeps its production temperature. Two runs can't estimate a 10% flip rate.
- **Temperature 0 doesn't make a judge deterministic.** In Microsoft's study one judge moved between 3 and 4 over 100 identical runs at temperature 0, and binary verdicts flipped on up to 6.4% of traces for task completion and 10% to 21% for groundedness. A flipping judge reports regressions that aren't there.
- **Repeatability is not validity.** In a study of 21 judges, two production judges repeated their verdicts more than 95% of the time and still had a position bias above 0.10. Read the flip rate next to TPR, TNR, and the both-orders swap, never instead of them.
- **Sampling k times and voting is part of the judge.** Freeze k and the vote rule with the prompt, and measure TPR and TNR with that exact aggregation. Check vendor defaults before trusting a number: ADK samples its judge 5 times and takes the majority unless configured otherwise.
- **Check in code that every verdict reaches the gate, and never read silence as clean.** In one deployed ordering agent the judge noted a suspected bug on 125 of 220 rounds and none became a gate failure, and it flagged 0 of 100 rounds in which humans confirmed 23 defects. A judge that flags nothing hasn't shown the rate is zero: label a sample first.

## Biased judges

- **Expect a judge to pass too much.** Across 14 judges grading 366 programs, TPR was above 96% and TNR mostly below 25%, and the judge with the best TNR (53.5%) had the lowest TPR (83.8%). That's why the failure catch rate decides acceptance (evaluators.md) and why several judges are combined with a low Fail threshold, never a majority.
- **Test the judge for length bias.** Regress its verdicts on the agent version plus normalized reply length. A significant length coefficient means the judge rewards length, not the behavior.

## Several judges on one mode

- **Agreeing judges aren't independent evidence.** Judges that share a model family, prompt, or examples fail together, and a panel's mean has unbounded bias when one judge fails systematically. Mix families, measure the error correlation between each pair on labeled cases, and never average their scores. In Amazon's 10-judge panels, aggregation that modeled the dependence scored 0.912 on a relevance task against 0.804 for majority vote.
- **Mark Fail when at least n judges say Fail, with n chosen on dev labels, never by majority.** With 14 agreeable judges, a majority of 8 had a worst-case error of 14.8% and a veto by 4 had 2.8%. The ensemble is a new judge, scored on test once. Use it to catch failures, never to break a close tie between two versions.
- **A panel never replaces the expert.** It may sort which traces the expert labels first, and a human resolves every split, but its labels never validate a judge (SKILL.md rule 1).

## Pairwise judges

- **Run both orders, and count a win only when both agree.** A flip counts as a tie. Randomize which answer comes first per case, let judges and labelers answer tie or both bad, treat both answers as untrusted data, and keep compared answers similar in length or check the winner isn't just the longer one.
- **Judge every round against frozen baseline outputs.** Save the baseline's answers once and never regenerate them, or "win rate" changes meaning between rounds. The baseline against itself is 0.5. When a version wins nearly every pair, freeze its outputs as a second reference and report both win rates.
- **Add a set-level diversity check.** A per-case pairwise judge can't see every answer drifting to one style while each one beats the baseline.

## Agent judges for long trajectories

- **For a failure buried deep in a long trajectory, give the judge tools to find and read the steps it needs,** instead of pasting the whole trace into one prompt, and give it no memory of earlier verdicts. On 55 tasks with 365 requirements, an agent judge agreed with human consensus 90.4% of the time against 60.4% for a single-prompt judge. Its locate tool alone raised it from 82.2%, and a memory module made it worse.
- **Validate it like any judge,** on balanced labels with its flip rate measured. In the same study the single-prompt judge scored 84.2% accuracy on one agent by failing nearly everything.

## When validation stops holding

- **Vendor-managed, built-in, and default evaluators are judges that change under you.** Pin the evaluator's version, record it on every verdict, and re-validate when it changes. Where the vendor won't let you pin (managed evaluators upgraded without version selection, a metric name that resolves to the latest version, a default judge on a model alias), run the vendor's prompt on a model snapshot you pin yourself (SKILL.md rule 13).
- **A judge validated on one stratum isn't validated on another.** Split the validation labels by journey, language (support-checks.md), reply length, and request complexity, and report TPR and TNR per stratum before using the judge there. A dominant stratum inflates the overall number: a task-completion judge that looked ready on telecom support traces had a 20-point accuracy gap on function-calling traces, where the failure was silent state corruption.
- **A judge-based comparison between two versions needs each version's own calibration.** A version that writes differently changes how the judge errs. Label a sample of each side's outputs and report each side's TPR, TNR, and J = TPR + TNR - 1 (check: 0.92 and 0.88 give 0.80) with intervals, plus the difference in J with its interval (statistics.md, "Difference in J"). If that interval excludes zero, don't report the judge-based difference: have the expert label both sides on the same cases and use the exact paired test.
- **Never correct both sides with one shared TPR and TNR.** A shared correction amplifies any mismatch by 1/J. In one study a true difference of +0.003 came out as a significant loss from raw judge rates (-0.046, interval -0.078 to -0.016) and from a shared correction (-0.089), and as no detectable difference with per-version calibration (-0.009, interval -0.084 to +0.059). The same holds when comparing the agent with a human team (production.md).
