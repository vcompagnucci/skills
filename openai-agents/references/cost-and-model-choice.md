# Cost and model choice

Picking a model and a reasoning effort per step, and cutting cost without losing quality. Draws on OpenAI's builder guide and efficiency post for GPT-5.6, its 2025 practical guide to agents, a support-agent cost cookbook (a simulation), frontend, benchmark, long-run and chain-of-thought monitoring posts, and the model-migration guide shipped in the Codex repo.

## Pick the model

- **Prototype with the most capable model everywhere, then swap in smaller ones.** Set a baseline with evals and hit the accuracy target first. Then cut cost and latency where smaller models still pass. This shows where they fail instead of limiting the agent early. (`practical-guide`)
- **Small models now handle steps that used to need the flagship.** On a search benchmark, the small model at its highest effort matched the older flagship (84.04% vs 84.36%) at about 1/25th of the cost. Use them for high-volume, latency-sensitive or repeated steps, like extraction before the agentic analysis in a legal workflow. (`gpt56-guide`)
- **Route per step, not per system.** Smallest model for classification and tags, a mid model for routine resolution, the largest for high-risk cases like account access and refund disputes, with deterministic authorization checks and human review kept in place. (`cost-quality`)
- **A newer model can be cheaper per task.** Fewer retries, tool calls or escalations can outweigh a higher rate. (`cost-quality`)
- **Distill once the task is proven.** Validate it on a larger model, then distill into a smaller, cheaper one. (`devs-2025`)

## Switch models as a migration

- **Swapping a model is a behavior change, not a string replace.** The upgrade guide shipped in the Codex repo (`references/upgrading-to-gpt-6-astra.md`) first preserves each call site's behavior, latency class, cost class, reasoning level, tool semantics, cache behavior and output contract, then makes "the smallest safe migration". Routers and fallbacks are mapped by role (flagship, balanced, fast) instead of all moving to the flagship. When intent is unclear, leave the site unchanged and list it. New features only for a measured problem. (`repo-prompting`)
- **Validate with a ladder, one change per rung.** Old model and prompt, then the new model with the same prompt and effort, then one level lower effort, then the smallest fix for a measured failure, then each optional feature alone. Track task success, tool choice, loop count, latency, tokens including cached, and total cost per successful task. Never fix failures by weakening schemas or dropping tools. (`repo-prompting`)

## Set reasoning effort

- **Reasoning became a dial, not a separate model family.** By late 2025 it merged into one model line, so choosing a model became a cost, latency and quality tradeoff. (`devs-2025`)
- **Re-test the effort you default to.** With the harness held constant, the new flagship at low effort beat the previous one at high effort on an agent benchmark, and startups cut costs by lowering effort from their old defaults. (`gpt56-guide`)
- **More reasoning isn't always better.** For simpler sites, low and medium effort "often lead to stronger front-end results" because the model stays focused and overthinks less. Raise it for ambitious designs. (`frontends`)
- **Try one level lower on each step.** Keep it if quality gates still pass. Codex's migration ladder has the same rung. (`cost-quality`, `repo-prompting`)
- **Effort can also buy oversight.** Across 13 evaluations, a smaller model at higher effort reached capability comparable to a larger one at low effort, and its longer reasoning was easier to monitor. The price is more inference compute, which OpenAI calls a "monitorability tax". One training run per model size, and wall-clock time wasn't studied. (`cot-monitorability`)
- **On a latency-critical path, tune effort with everything else.** GPT-Live tuned the delegated model's effort, output limits, tool schemas and model-tool round trips together for faster useful answers. (`gpt-live`)

## Cost comes from architecture

- **Context bloat costs money and triggers needless reasoning.** It also distracts the model. Codex caps tool output and surfaces tools and skills only when needed. (`gpt56-efficiency`)
- **Reuse work already done.** Keeping reasoning across turns and compacting instead of truncating made the agent both better and cheaper, with about 6x fewer output tokens on ARC-AGI-3 (numbers in `context-engineering.md`). (`arc-agi-3`, `gpt56-guide`)
- **Move work that doesn't change the outcome off the user's path.** Classification, lookups, the decision and the reply stay synchronous. QA, tags, summaries, audits and reporting go async or to batch. (`cost-quality`)
- **Efficiency can also be trained in.** GPT-5.6 was trained on task success and efficiency together, to take a more direct path. OpenAI's claim about its own model. (`gpt56-efficiency`)

## Cut cost without cutting quality

- **Most waste comes from doing too much in one path.** The cookbook built a deliberately bad support agent: every tool exposed, oversized payloads, high reasoning and the biggest model everywhere, QA and tagging before replying. In its simulation (modeled, not a benchmark), the first round of prompt and output controls took quality from 0.51 to 0.98, policy compliance from 10% to 100%, tokens from about 11,900 to 1,400 and cost down 87%. (`cost-quality`)
- **Apply the levers in a safe order.** Baseline, prompt and output controls, tool control, context hygiene, model routing, caching, cache-aware context, split workflow, processing tier. Tool outputs "can dominate input tokens", so slim payloads to the fields a decision needs. (`cost-quality`)
- **Measure cost per verified success, including failures.** A cheaper agent that resolves half its tickets can cost more per success than a pricier one that resolves 90%. Count spend on failed attempts, track autonomous and human-assisted resolutions apart, and never count an escalation as a resolution. Codex's migration guide uses the same metric, total cost per successful task. (`cost-quality`, `repo-prompting`)

## Scale of spend on long runs

- **Big autonomous runs use a lot of tokens.** One 25-hour Codex run at the highest reasoning setting used about 13M tokens for about 30k lines of code. Four engineers building Sora for Android over 28 days used about 5 billion. Treat these as reference points, not targets. (`long-horizon`, `sora-android`)

## Where the posts disagree

- **Start big, or start low?** The practical guide (2025-04-17) says prototype with the most capable model everywhere and swap down. The frontend post (2026-03-20) says start with low effort, and the GPT-5.6 guide (2026-08-13) says re-test defaults because newer models do more at lower effort. The first is about finding the ceiling. The later ones are about defaults once models got stronger. (`practical-guide`, `frontends`, `gpt56-guide`)
- **Maximum effort for hard work?** The 25-hour run (2026-02-23) used the highest reasoning setting. The frontend post finds low and medium often better for simpler sites. Codex's own code-review skill (repo, 2026-09-26) runs every review sub-agent at the highest effort. Task size and stakes likely decide. (`long-horizon`, `frontends`, `repo-review`)

## Key source articles
`cost-quality` · `gpt56-guide` · `gpt56-efficiency` · `repo-prompting` · `practical-guide` · `frontends` · `devs-2025` · `arc-agi-3` · `cot-monitorability`
