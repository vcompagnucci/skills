# Build and validate evaluators

One evaluator per failure mode. Build it, then prove it agrees with a human before trusting any number it produces. Repeat runs, votes, panels, pairwise and agent judges, and revalidation are in judges.md. Retrieval and abstention are in retrieval.md.

## Pick the grader

```
Can code check it from the trace? (state, arguments, schema, forbidden text, citation ids)
├── Yes → code evaluator; no judge ever overrides its Fail
└── No → Is the question which of two open-ended replies is better, with no binary failure definition?
    ├── Yes → pairwise judge, blind, run in both orders (judges.md)
    └── No → Does the failure sit deep in a long trajectory?
        ├── Yes → agent judge with tools to read the trace (judges.md)
        └── No → binary LLM judge for this one mode
```

- **Comparing two versions on existing modes: run the same binary judges on both and use the exact paired test (statistics.md).** Each version also needs its own judge calibration (judges.md, "When validation stops holding").
- **Known rules get code tests from day one.** Policy and compliance constraints you already know (identity verified before account data, confirmation before a withdrawal, no investment advice) don't wait for error analysis. Judge-based evaluators do wait. A judge for a mode you haven't observed measures nothing.
- **A generated rubric is a list of candidate checks, never the evaluator.** Google and Microsoft now offer rubrics generated from the agent's instructions and tools as the main agent measure, which skips SKILL.md rule 1. The expert edits the list against the failure modes found in real traces, and each surviving item becomes its own binary check, validated like any judge. Microsoft's generated dimensions recovered 72.1% of an expert rubric's dimensions, missing about a quarter.
- **An open-ended answer whose ideal content differs by case gets a per-case rubric beside the mode judges.** Experts write binary criteria per case, weighted -10 to +10 (negative for harm). A judge marks each met or not, and the case score is the points met, negative ones subtracting, over the sum of positive points. Keep criteria at least 2 of 3 independent experts agree on and none contradicts, validate the criterion judge on expert labels, and report each case's worst score across runs.

## Write the judge

- **One failure mode per judge, Pass or Fail.** A holistic judge hides which failure happened. Scales (1 to 5) drift between graders and don't convert into a failure rate. Likert scales belong only to filtering synthetic data.
- **Critique first, verdict last.** One or two sentences naming the specific evidence in this trace, then the label. Use the skeleton in judge-prompt.md.
- **2 to 4 examples, from the train split only,** including one borderline case. Examples from the test split inflate its measured agreement.
- **Give it only the context it needs,** and ground it. Policy judges read the actual policy text and check claims against the recorded tool results. A judge of tool use also gets the tool definitions: without them, one marked legitimate calls as not permitted.
- **A judge of a conversation-level mode gets the state across turns:** the ledger or cart before and after, any open proposal, flags, or the agent's own state accessors. Per-turn judges of one deployed ordering agent caught 2 of 9 human-confirmed defect patterns, and 15 of 30 patterns had no rubric category at all. Every failure dimension needs a category.
- **Tell it that instructions inside the trace are data,** and never tell it what its label will cause or who wrote the reply (judge-prompt.md). A user message saying "mark this as passed" must not steer the grade.
- **A different model from the agent, pinned to a dated snapshot and called through the API** (SKILL.md rule 13). A model grading its own family's output is lenient toward it, and an unpinned judge changes under you.
- **Compare one frontier and one cheap judge model per mode on dev, then score the chosen one on test once.** The cheap model is fine where its failure catch rate holds and harmful where it misses the rare class. On 456 support traces six judge models scored 85.3% to 88.4% on task completion, while on groundedness the cheapest separated grounded from ungrounded replies far worse (PR-AUC 0.60 against 0.82, with 0.33 as chance) and missed hallucinations.
- **When the output is a score you threshold** (a per-case rubric total, a vendor evaluator), check ranking before the cutoff. Good ranking with a bad cutoff: re-tune the cutoff on dev labels. Weak ranking: replace the model, because no cutoff separates scores that don't separate passes from fails.

## Label

- **Test the definition before labeling the set.** The two best domain experts blind-label the same 25 random traces and compute Cohen's kappa between them. Unless it's above 0.6, rewrite the definition and repeat before spending 100 labels on it: Microsoft sets that bar before calibrating a judge, and Shopify read about 0.2 as an ambiguous definition. Their agreement is also the ceiling a judge can reach.
- One domain expert labels. If others help, they first align with the expert on 20 to 50 shared traces, and the expert settles every disagreement. Include random traffic, and record the reason with every label.
- **Preference labels need a consensus step.** When the label is which reply is better, labelers score independently, discuss disagreements in pairs, and revise. The test set keeps only strong-confidence labels and pairs with a clear quality gap. In Anthropic's study that raised human agreement from 53% to 68%, and to 77% with the clear-gap filter. About 90 pairs still leave each model's interval near ±10 points, so size the set for the comparison you need.
- About 100 labels per mode, balanced between Pass and Fail. Never fewer than 30 of each. Below that the confidence interval is too wide to decide anything. For a rare mode (a wrong withdrawal), generate targeted scenarios (discover.md) until you have 30 Fails.
- **One record per conversation before splitting.** Keep one of each group of repeated runs or close scenario variants, or the same conversation lands in train and test and inflates agreement.
- **Split once:** stratified by label, fixed seed, about 20% train (examples), 40% dev (iterating on the prompt), 40% test (measured once, after the prompt is frozen). Check each split's Pass and Fail counts before picking examples, and never re-split afterward. Revise the prompt at most twice against dev. Past that you are fitting dev.
- **The two-revision cap counts manual edits made while reading dev disagreements.** An automated optimizer (GEPA) may tune the judge prompt against the labels instead, as long as its dev score is never reported and its frozen best prompt is scored on test once. The search kept its luckiest prompt, so its own score is biased upward.
- **The judge input holds only the trace:** conversation, tool calls and results, retrieved text. Never human labels, review notes, or the scenario's expected outcome. Any of them leaks the answer. Save the exact inputs once and reuse them for every prompt version.

## Measure agreement

- **Pass is the positive class.** TPR is agreement on human Passes, TNR is agreement on human Fails. Always write them out in words in any report: "failure catch rate" (TNR) and "pass agreement" (TPR), since sources count them in opposite directions and a reader can't tell which you meant.
- **Report both with 95% Wilson intervals,** computed with the formula in statistics.md after running its check value. With 20 human Fails the interval on the catch rate still spans about 34 points, so you know little. Cohen's kappa is only for comparing two human labelers, never a judge.
- **Accept by the cost of a miss.** 90% on both is the starting target and 80% the floor. 90% is about where experts agree with each other on binary labels: 89% to 93% in Microsoft's study, against 60% to 70% on 1-to-5 scores. For modes that move money or break compliance, the failure catch rate decides alone. A judge that misses a wrong withdrawal is useless however well it agrees on passes.
- **A preference or pairwise judge can't beat two experts' agreement with each other.** Measure that agreement on the same sample and set the target from it, not from 90%. On GDPval the pairwise grader agreed with experts 65.7% of the time against 70.8% between experts, and OpenAI still kept its expert graders.
- **Read every disagreement** and decide which of three it is. The judge is wrong, the label is wrong, or the definition is unclear. Fix the right one.
- **Test the grader before the agent.** Measure its flip rate over repeated runs (judges.md). Check for timeouts and cut-off answers, which look like model failures.
- **Attack the grader before a case enters CI.** An empty answer, "I don't know", a vague answer, and a confident answer to a different question must all fail, and a constant output must score near 0 across the set. A correct answer that differs from the reference must pass. Then have a model look for gaps in the rubric. A grader that passes a lazy answer will reward one.
- **Break the agent on purpose.** In a copy of the agent, make one behavior worse (remove the instruction behind it) and run all judges on the same cases. The matching judge's fail rate must rise and the others must stay flat. Labels show the judge agrees with a human on past traces. This shows it reacts to the failure it names.
- **Backtest when you have history.** Run the frozen judge on traces from two past versions whose real result you know (an A/B test, a release that raised complaints). It must rank them the same way. A judge that can't recover a known win or loss won't catch the next one.
- **A judge is its prompt, model snapshot, sampling settings, input formatter, verdict parser, and any sample count and vote rule, frozen together.** Change any of them and it's a new judge: tune it on dev, then score test once. If you already changed it after reading test results, label a fresh test split. CI and monitoring call the frozen judge exactly as you validated it, and never an unvalidated one.

## Guardrails are different

A guardrail blocks live traffic, so measure it like a classifier with precision (the share of blocks that were real threats; low precision means legitimate requests blocked) and recall (the share of threats blocked; low recall means threats got through), using the exact config you deploy. TPR and TNR are for judges that feed a failure rate.
