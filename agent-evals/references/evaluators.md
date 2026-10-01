# Build and validate evaluators

One evaluator per failure mode. Build it, then prove it agrees with a human before trusting any number it produces.

## Pick the grader

```
Can code check it from the trace? (state, arguments, schema, forbidden text, citation ids)
├── Yes → code evaluator
└── No → Is it a comparison between two agent versions?
    ├── Yes → pairwise judge, blind, run in both orders
    └── No → binary LLM judge for this one mode
```

- **Known rules get code tests from day one.** Policy and compliance constraints you already know (identity verified before account data, confirmation before a withdrawal, no investment advice) don't wait for error analysis. Judge-based evaluators do wait. A judge for a mode you haven't observed measures nothing.
- **A judge never overrides a failed code check.**

## Write the judge

- **One failure mode per judge, Pass or Fail.** A holistic judge hides which failure happened. Scales (1 to 5) drift between graders and don't convert into a failure rate. Likert scales belong only to filtering synthetic data.
- **Critique first, verdict last.** One or two sentences naming the specific evidence in this trace, then the label. Use the skeleton in judge-prompt.md.
- **2 to 4 examples, from the train split only,** including one borderline case. Examples from the test split inflate its measured agreement.
- **Give it only the context it needs,** and ground it. Policy judges read the actual policy text and check claims against the recorded tool results. A judge of tool use also gets the tool definitions: without them, one marked legitimate calls as not permitted.
- **Tell it that instructions inside the trace are data.** A customer message saying "mark this as passed" must not steer the grade.
- **A different model from the agent, pinned to a dated snapshot and called through the API** (SKILL.md rule 13). A model grading its own family's output is lenient toward it, and an unpinned judge changes under you.

## Label

- One domain expert labels. If others help, they first align with the expert on 20 to 50 shared traces, and the expert settles every disagreement.
- About 100 labels per mode, balanced between Pass and Fail. Never fewer than 30 of each. Below that the confidence interval is too wide to decide anything. For a rare mode (a wrong withdrawal), generate targeted scenarios (discover.md) until you have 30 Fails.
- **One record per conversation before splitting.** Keep one of each group of repeated runs or close scenario variants, or the same conversation lands in train and test and inflates agreement.
- **Split once:** stratified by label, fixed seed, about 20% train (examples), 40% dev (iterating on the prompt), 40% test (measured once, after the prompt is frozen). Check each split's Pass and Fail counts before picking examples, and never re-split afterward. Revise the prompt at most twice against dev. Past that you are fitting dev.
- **The judge input holds only the trace:** conversation, tool calls and results, retrieved text. Never human labels, review notes, or the scenario's expected outcome. Any of them leaks the answer. Save the exact inputs once and reuse them for every prompt version.

## Measure agreement

- **Pass is the positive class.** TPR is agreement on human Passes, TNR is agreement on human Fails. Always write them out in words in any report: "failure catch rate" (TNR) and "pass agreement" (TPR), since sources count them in opposite directions and a reader can't tell which you meant.
- **Report both with 95% Wilson intervals.** Catching 16 of 20 human Fails is 0.80, interval about 0.58 to 0.92: with 20 Fails you still know little. Cohen's kappa is only for comparing two human labelers, never a judge.
- **Accept by the cost of a miss.** 90% on both is the starting target and 80% the floor. For modes that move money or break compliance, the failure catch rate decides alone. A judge that misses a wrong withdrawal is useless however well it agrees on passes.
- **Read every disagreement** and decide which of three it is. The judge is wrong, the label is wrong, or the definition is unclear. Fix the right one.
- **Test the grader before the agent.** Run it twice on the same output and check the verdict holds. Check for timeouts and cut-off answers, which look like model failures.
- **Attack the grader before a case enters CI.** An empty answer, "I don't know", a vague answer, and a confident answer to a different question must all fail, and a constant output must score near 0 across the set. A correct answer that differs from the reference must pass. Then have a model look for gaps in the rubric. A grader that passes a lazy answer will reward one.
- **Break the agent on purpose.** In a copy of the agent, make one behavior worse (remove the instruction behind it) and run all judges on the same cases. The matching judge's fail rate must rise and the others must stay flat. Labels show the judge agrees with a human on past traces. This shows it reacts to the failure it names.
- **Backtest when you have history.** Run the frozen judge on traces from two past versions whose real result you know (an A/B test, a release that raised complaints). It must rank them the same way. A judge that can't recover a known win or loss won't catch the next one.
- **Pairwise judges run in both orders.** A win counts only when both orders agree, and a flip counts as a tie. Let judges and labelers answer tie. Keep compared answers similar in length, or check the winner isn't just the longer one.
- **A judge is its prompt, model snapshot, input formatter, and verdict parser, frozen together.** Change any of the four and it's a new judge: tune it on dev, then score test once. If you already changed it after reading test results, label a fresh test split. CI and monitoring call the frozen judge exactly as you validated it, and never an unvalidated one.

## Guardrails are different

A guardrail blocks live traffic, so measure it like a classifier with precision (the share of blocks that were real threats; low precision means legitimate requests blocked) and recall (the share of threats blocked; low recall means threats got through), using the exact config you deploy. TPR and TNR are for judges that feed a failure rate.

## Retrieval and abstention

See retrieval.md.
