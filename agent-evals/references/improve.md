# Improve the agent against the eval

## Before the first change

**Check the eval before climbing it.** A stronger model or higher effort must score higher, and the best model at its highest effort must stay well below 100% for reasons other than broken cases. If scores don't rise with capability, ambiguous cases or a miscalibrated grader are capping them. If the current version already scores about 95% or more, there's no quality left to measure: aim at cost or latency with quality held.

- **Pick one target.** The failure mode with the highest prevalence times severity in the last error analysis that the prompt, a tool, or the harness can change, and that at least one development case scores. Write it down with three trace ids that show it. A fix aimed at no named mode can't be judged a fix. Check where it concentrates (a version, a scenario) before choosing the change.
- **Lock every model first.** Run each model you will compare on one case, replace any that can't finish it, then freeze the selection. Swapping a model after the split makes the comparison meaningless.
- **Split once, then freeze it.** Group cases by kind (regression or capability) and by whether they change data, and put about one third of each group in the test set. A group of one stays in development; a larger group keeps at least one case on each side. Assign within groups at random, never by baseline score, which builds regression to the mean into the result. Store case ids and a hash, and never recreate the split. Balanced groups make both sides score the same behaviors.
- **Set a search budget in evaluated case runs** (150 in the Cartwheel course) and charge it before each run. During search, a case that changes data runs 5 times and a read-only case once, to stretch the budget; that's a search economy, not a gate. The test batch and CI run every case 15 times, because there each case decides something. Refuse a run that would exceed the budget, and return the unused runs when one crashes.
- **Record the baseline** on development: commit, prompt hash, model, score, and the share of data-changing cases that pass all 5 runs. If time has passed or the environment changed (dependencies, model snapshot, data), run an unchanged control and compare against it, not the old baseline.

## The loop

1. **Don't choose the layer by reasoning about the failure. Probe each layer once by hand** before automating: one prompt change, one tool change (its description or its code), one harness change (retrieval, step control, context, result checks). Write the predicted effect before editing, including the mechanism you expect to see (more escalations, a tool called earlier). The layer that moves the target is where to search.
2. **One change per attempt, in one layer.** Commit it, run development, and keep it only if the score rises and the data-changing pass share doesn't drop. Otherwise revert to the last kept commit. A mean that rises while writes get less reliable is a worse agent.
3. **Log every attempt, reverts included:** candidate, layer, files, rationale, predicted effect, how often the predicted mechanism fired, score, write pass share, decision, commit, result file. A search whose failures aren't recorded can't be audited or resumed.
4. **Stop after 2 changes in a row that don't improve,** or when the budget runs out. Then stop editing and sort every remaining failure by cause. That finds broken cases and graders.
5. **Choose the method by layer.** An automated prompt optimizer (GEPA) when the fix is prompt wording; a coding agent making one allowed change at a time when it may be a tool or the harness. Never use or report an optimizer's search score: rerun its best candidate with the normal development eval and use that number. The search kept its luckiest run, so its score is biased upward.

**Never, during search:** run or read the test set, edit cases, judges, graders, tests, or the budget, raise a timeout, change a seed or sample size, or weaken an authorization check. Each one raises the score without improving the agent. If runs time out, the timeouts are failures to read and fix, not a setting to loosen.

Check first that the eval's run-to-run noise is smaller than the smallest gain you'd act on, or add cases and repetitions. A rough 95% band is ±1/√(cases × runs): 25 cases × 2 runs moves about ±14 points by chance. A gain that doesn't show the mechanism you predicted is rejected, whatever the score. When one case flipping moves the score more than the gain, rerun a promising change before keeping it. Prompts, skills, and tool descriptions are cheap to change and revert. Harness code isn't. Never paste failing transcripts into the prompt.

**Read passing runs too.** When a case or grader is new, and after each improvement round, read a sample of passes with the grader's reasoning. Look for shortcuts: extra articles cited to satisfy a citation check, an action claimed that the trace doesn't show, the answer read from the environment, a proxy met without finishing the task. A pass earned by a shortcut is a grader bug.

## Freeze, then test once

- **Pick the final candidate by the target first,** then development score, then the write pass share. A candidate that fixes the target and makes writes more reliable is worth a small drop in mean score.
- **Freeze it before any test run:** commit, prompt hash, model, development scores, and a hash of the cases and judges, verified unchanged since the split.
- **Run the test set once, as one planned batch of every configuration you compare.** Never change the agent after reading test results. Those cases are now development knowledge, and a later change needs a new test set.
- **Compare configurations so each difference has one cause.** The batch runs the starting version on each candidate model and the final version on the development model, never a comparison on development cases, which already shaped the final version. Starting versions across models show the model's effect; starting and final on the same model show your change's effect.
- **Report the frontier.** A configuration is dominated when another scores the same or higher at the same or lower cost, with at least one strictly better. The rest form the frontier, the tradeoffs worth choosing among. Price every model from one date, and count the agent's calls only, never the judges'.
- Report the final version against the baseline on the test set as the per-case difference with its interval, not two separate intervals that overlap, and don't merge a gain that sits within the noise.
