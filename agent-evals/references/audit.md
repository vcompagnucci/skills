# Audit an existing eval setup

Inspect the actual artifacts: traces, judge prompts, labels, CI config, dashboards. Never answer from this list alone. Report one block per problem, most harmful to users first, and omit areas with no problem:

    ### <problem>
    Status: exists | OK | can't tell
    <one or two sentences on what you found, naming the artifact>
    Fix: <action, and the reference that covers it>

Check:

1. Failure modes came from read traces. Generic labels ("helpfulness", "hallucination score", "toxicity") mean they were brainstormed. If there's no error analysis, stop here and start with discover.md. Recommend no judges or dashboards before it, only code tests for rules already known.
2. Every judge is Pass/Fail, checks one mode, and does nothing code could check (format, schema, keywords, resulting state).
3. No similarity metric (ROUGE, BERTScore, cosine) is the main grader for answers.
4. Every judge has TPR and TNR on a held-out test split, not accuracy, percent agreement, or kappa, and its few-shot examples appear in neither dev nor test.
5. Labels come from a domain expert who saw the whole trace, rendered readably rather than as raw JSON.
6. About 100 labels per judge, at least 30 of each class.
7. Error analysis and judge validation happened after the last model, prompt, or tool change and after the last incident.
8. Production rates come from a random sample, corrected and with an interval. CI runs each gating case 15 times and gates on pass^k.
9. Actions have should-not cases, and graders judge actions on resulting state, not on the reply. For customer-facing agents, escalation has should-not cases too and scores are reported per language.
10. The case set itself was audited: code checks on every case, a person reading a stratified 20 to 50, and an LLM auditor per case given the prompt, log, submission, and expected answer but not the pass result, its flags reviewed per item 13. Each human reviewer reached a verdict before reading any agent's analysis. Each expected answer records where it came from, and none was copied from the current model's output.
11. The audit started where broken cases concentrate: cases the best configuration fails in every run, and cases stronger agents fail more often than weaker ones. Of 138 SWE-bench Verified tasks o3 failed in all 64 runs, 59.4% were broken. On τ-bench Airline 25 of 50 tasks were, and excluding them doubled mean pass^k from 20.8% to 40.0%.
12. Each broken case was named by kind: a grader stricter than the task, a requirement the grader enforces that the task never states, a grader lenient enough to pass incomplete work, a task that points at the wrong behavior, and in support simulators an expected action that contradicts the policy, ambiguous customer instructions, or a database or grading error.
13. A person reviewed the cases an auditing agent approved, and the flags humans dismissed, with evidence required to dismiss one. Agent auditors found about half the lenient graders humans found (4.1% of tasks against 9.4%), and Anthropic's reviewers had dismissed some true flags as false positives.
14. Sweeps over many transcripts (an audit, an incident, a risk group) ran a cheap high-recall filter over every transcript, then had a model review what it flagged, never an agent searching through them. An agentic search over about 141,000 transcripts missed an incident that a two-stage scan found.
15. Every run reports how many passes were disqualified and the score before and after, from a sampled review for reward hacking, contamination, broken cases, and signs the model knew it was tested or underperformed on purpose. Refusals that hide the behavior count as compromised, never as passes. One model's measured time horizon fell from about 13 hours to about 6 once reward-hacked successes were removed.
16. Evaluators a coding agent wrote each map to a named failure mode, their code does what their plan says (no keyword count where the plan promised a semantic judge), and each ran end to end once before anyone trusted a number. Without eval guidance, coding agents wrote 12 or more metrics per agent, favoring latency and tokens over task success, in code 2 to 3 times longer, and only 30% of it ran.
