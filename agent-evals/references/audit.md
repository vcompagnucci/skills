# Audit an existing eval setup

Inspect the actual artifacts: traces, judge prompts, labels, CI config, dashboards. Never answer from this list alone. Report one block per problem, most harmful to users first, and omit areas with no problem:

    ### <problem>
    Status: exists | OK | can't tell
    <one or two sentences on what you found, naming the artifact>
    Fix: <action, and the reference that covers it>

Check:

1. Failure modes came from read traces. Generic labels ("helpfulness", "hallucination score", "toxicity") mean they were brainstormed. If there's no error analysis, stop here and start with discover.md. Recommend no evaluators or dashboards before it.
2. Every judge is Pass/Fail, checks one mode, and does nothing code could check (format, schema, keywords, resulting state).
3. No similarity metric (ROUGE, BERTScore, cosine) is the main grader for answers.
4. Every judge has TPR and TNR on a held-out test split, not accuracy, percent agreement, or kappa, and its few-shot examples appear in neither dev nor test.
5. Labels come from a domain expert who saw the whole trace, rendered readably rather than as raw JSON.
6. About 100 labels per judge, at least 30 of each class.
7. Error analysis and judge validation happened after the last model, prompt, or tool change and after the last incident.
8. Production rates come from a random sample, corrected and with an interval. CI runs each case several times and gates on pass^k.
9. For customer-facing agents, escalation and actions have should-not cases, scores are reported per language, and graders judge actions on resulting state, not on the reply.
