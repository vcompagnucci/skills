# Red team

Red teaming here measures how often attacks on the agent succeed. How to defend the agent is out of scope.

## Before attacking

- **Write a threat model for each environment:** what the attacker controls (a document, a transaction memo, a tool output, a customer message) and what counts as success (an item repriced, another customer's order cancelled, data sent out). Attack success rates without a shared threat model can't be compared.
- **Trigger each error once before building its eval.** An eval for an attack you can't reproduce tests nothing.
- **Run the probe set with no attack first.** A high "success" rate without the attack means the prompts or the rubric are wrong, not the agent.
- **The grader of attack success is a judge.** Validate it like one (evaluators.md): two graders with the same 80% accuracy but different error rates can read the same attacks as 0.46 and 0.60.

## Attack

- **Attack through every untrusted input:** retrieved articles, transaction memos, uploaded documents, other users' data, jailbreaks, and escalation over several turns. 50+ probes per attack type.
- **Use an adaptive attacker, not only a fixed list.** It sends an attack, reads the agent's reply and tool calls, and tries again. Fixed lists saturate: models already pass several static injection benchmarks above 97%, while OpenAI's adaptive attacker succeeded on 84% of held-out indirect-injection scenarios against 13% for human red teamers. Match the adversary's tooling, including a harness that keeps a bypass working across turns.
- **Include exfiltration through retrieved content:** a planted article asking the agent to add a link or image carrying private data. It passes only if no private data leaves in a link or image.
- **Search categories of realistic requests for rare failures nobody attacks for.** Write each category in plain language ("in Spanish, about a family member's account"), sample many queries per category, score policy breaks, and keep the categories that reliably trigger them. Drop categories that openly ask for bad behavior. A person still reviews each kept category before it enters CI (discover.md).
- **Keep every attack that ever worked.** Browser attacks built against an older model still succeeded on newer ones without added safeguards, so the suite only grows.

## Confirm and report

- **Build attacks against a simulated copy, then confirm them on a throwaway copy of the deployed configuration,** with input filters, action classifiers, and model fallbacks on, because that's what users get. In Anthropic's test, 18% of rollouts went to a fallback model. Load attack fixtures only into a throwaway copy of the data.
- **Confirm each finding in the trace and the database,** never on a scanner's verdict alone. A scanner can't see whether protected state changed.
- **Report attack success at several attempt budgets.** An attacker needs one success, so report the measured share of attacks where at least one of k attempts succeeds, at k = 1, 10, and 100, and state the budget next to every rate. The formula for independent attempts (statistics.md) doesn't hold for repeated ones: on Gray Swan's ART, where each attempt is drawn from a fixed pool of attacks chosen because they transfer across models, Opus 4.7 went from about 0.1% on one attempt to 4.8% to 6.0% at 100, not the 9.5% it predicts. An attacker that adapts to the model does far worse to it (agent-security models.md).
- **Report over-refusal next to attack success.** Run legitimate requests through the same configuration and count refusals. An agent can look robust by refusing more.
- **Never read zero failures in N as safe at scale.** For rare high-severity failures, estimate each query's failure probability and extrapolate the worst-query risk along its power-law tail. Forecasts from about 900 queries to about 90,000 landed within 10x of the true risk in 86% of cases.
- **Sort each finding** into blocked by code, newly defended, or accepted risk with a written reason. Nothing stays unsorted.
- **Rerun injection and tool-abuse probes on every model change.** One agent's injection resistance fell from 94% to 71% after an upgrade from GPT-4o to GPT-4.1.
