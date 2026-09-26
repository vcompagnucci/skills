# Cost and model choice

What an agent task costs and how to pick the model. Addy Osmani's September 2026 post frames it this way: you buy finished tasks, not tokens. The model-selection and platform guides add the rest, the cookbooks add measured cost passes, and the use-case docs add per-task model picks. The numbers are list prices and the posts' own examples, so they'll go out of date.

## You pay per task

- **Same price per token, different price per task.** Every turn resends the conversation, so a model that needs more turns costs more. "The cheapest turn is the one you don't need." Report pass rate and cost per task together before any optimization. (`cost`, `cb-cost`)
- **Every saving risks a retry.** Lower effort, a smaller model, or less context all save tokens, and "a retry costs more than those savings". (`cost`)
- **Four things set the cost.** Turns, cache reads, output tokens, and the model. Thinking bills as output, at 5× the input price. On Opus 5.5 an output token costs 100× a cache read, so 60K output tokens ($1.20) cost the same as 6M tokens read from cache. (`cost`)
- **The turn math.** A task whose context grows from 20K to 120K over 40 turns sends about 2.8M input tokens, around $1.62 with 90% from cache. The same task in 25 turns costs about $1.02. (`cost`)
- **Checks and batching cut turns.** A test, a build, or a script lets the model find its mistakes earlier. Gathering everything it needs in one pass means fewer resends. (`cost`)

## Opus 5.5 pricing (September 2026)

- **$4 input, $20 output, $0.20 cache read, per million tokens.** Input and output are 20% cheaper than Opus 5. Cache reads are 60% cheaper. Plan limits go about 25% further. (`cost`)
- **"40% cheaper" is an estimate for typical work, not a per-token price.** It assumes Opus 5.5 uses fewer tokens per task at its medium default. The price change alone takes the post's example session from $3.50 to $2.40, 31% less. (`cost`)
- **Well-scoped tasks get the price cut. Open-ended ones may save more,** because the model spends fewer turns on a wrong idea. (`cost`)

## Three models a day

- **Haiku or Sonnet for lookups.** Subagents that search and summarize, logs, test output, "where is this defined". This is work where a mistake is cheap to spot. A misread search result sends the main model after the wrong file, and you pay for the detour. (`cost`)
- **Opus 5.5 as the daily driver.** Supervised feature work, debugging, and review with follow-up edits. Mechanical edits across many files stay on Opus 5.5 at low effort. (`cost`)
- **Fable 5.1 when the result matters more than the price.** Long runs you won't supervise, problems with no existing pattern, large changes that coordinate many subagents. If Opus 5.5 on xhigh hits the same problem twice, switch, and switch back once it's solved. Fable 5.1 costs $10 input and $50 output, but its cache reads cost $0.25, only 1.25× Opus 5.5's, so the gap is smallest on long runs that mostly read from cache. (`cost`)
- **Raise effort before changing models.** Effort costs less than a bigger model. The sign you need it is a fix that stops at one layer (see `effort.md`). (`cost`)
- **Setting a subagent's model.** Put `model: haiku` in its definition, or set `CLAUDE_CODE_SUBAGENT_MODEL` for all of them. A subagent with no setting inherits the main model and its price. (`cost`)
- **Agent teams use about 7× the tokens** of a normal session in plan mode. Keep them small and shut teammates down when they finish. (`cost`)

## Switching models: the position changed

- **April: don't switch mid-session.** Each model has its own cache. Hand the work to a subagent instead. (`caching`, 2026-04-30)
- **September: switch at a natural break when the task is worth it.** Accept one cache write on the new model and make it smaller with `/compact` or a fresh session that starts from a short written plan. `/model` also changes the default for new sessions, so switch back afterwards. This is the later position. (`cost`, 2026-09-25)
- **Opusplan goes against the "edits stay on Opus" advice.** With it, Opus plans and Sonnet makes the edits. The post says to "measure it on your own tasks before you make it a default". (`cost`)

## The rest of the bill

- **Fast mode** runs up to 2.5× faster at 2× the price. The first request after turning it on pays full price for the whole conversation, so turn it on at the start of a session. (`cost`, `opus-5-5`)
- **Images bill by pixel area,** about one token per 28×28 patch whatever they contain. Downscale to what the task needs, and send big tables through the Files API and code execution so only the answer reaches context. (`cb-cost`)
- **Cap unattended sessions.** A Managed Agents budget caps list-price spend across every thread, subagents included. Hitting it pauses the session with files and state intact. It's checked between requests, so one request can overshoot, and it can only be set at creation. (`cb-spend-cap`)
- **The Batch API** costs half and stacks with caching, in exchange for single-shot requests within 24 hours. (`cost`, `cb-cost`)
- **Typical spend** is about $13 per developer per active day, and 90% of users stay under $30. (`cost`)

## Choosing a model class

- **Start with the most intelligent available model and dial effort.** Cost per task is often lower on smarter models, even at a higher price per token, because they take fewer turns. Starting small also makes it harder to tell model failures from setup failures. The guide documents the opposite approach (start cheapest, move up) as an alternative. (`models-explained`)
- **Classes differ in how hard a problem they can carry, not in domain.** There's no finance model and science model. Decide on task difficulty, latency, access, and unit economics. Mythos and Fable handle frontier and long-running work, Opus reasoning-heavy enterprise work, Sonnet everyday tasks and high-volume subagents, Haiku the lowest cost and latency. (`models-explained`)
- **Move up to Fable only when your evals show Opus struggling.** If Opus clears the bar, its speed and price may win. (`models-explained`, `cost`)
- **The advisor strategy mixes models.** A cheap executor calls a smarter model only to check its plan and work. Sonnet 5 with a Fable 5 advisor landed within 10% of Fable 5 on SWE-bench Pro at 63% of the price. Executors forget the advisor exists, so nudge them every ~20 turns. It works best gated on a cheap external signal (a payout threshold), since asking a weak driver to spot hard cases needs the judgment it lacks. In Managed Agents each consult is its own priced thread, with no per-consult cap. (`models-explained`, `computer-use`, `cb-cost`, `cb-advisor`)
- **Planning big and executing small pays on coverage work.** A frontier coordinator that never reads raw pages, with cheap workers reading in parallel, billed 84-98% of team input tokens at the worker rate (measured). The gap narrows on discovery tasks, where frontier search intuition matters, and splitting into more, narrower briefs raised the bill: each worker has a setup cost. (`cb-plan-big`)
- **Compare arms at the same rigor.** A solo frontier agent left to its judgment read one source per fact and came in cheap, but that's a lower-rigor product. Both arms also built their list from model memory and misranked one item: verification covered the facts, not the question's premise. (`cb-plan-big`)
- **Split by mechanical versus reasoning work.** For computer use, Sonnet 4.6 clicks more precisely and Opus reasons better, and an orchestrator with a clicking sub-agent handles advanced flows. (`computer-use`)
- **Benchmarks saturate at the top, so decide with your own evals.** Use a curated set of production problems with your team's success criteria. `/claude-api hillclimb` searched model, effort, and prompt against a train/test split: going from Opus 4.8 at high effort to Sonnet 5 at low effort plus routing rules raised held-out accuracy from 78.6% to 90.5% at about a fifth of the cost. (`models-explained`, `platform-cost`)
- **Profile spend first, then apply ranked levers.** `/claude-api cost-optimize` ranks caching, trimming, bounded output, and batching: LegalBench about 67% cheaper, tau2-bench retail about 73%, with no significant score change. (`platform-cost`)
- **Change the model last.** The cost cookbook's order: caching, input trimming, loop efficiency, output, Batch API, then model and effort, because only the model caps intelligence. On a ten-claim insurance eval, Sonnet at medium plus one system-prompt breakpoint was 13× cheaper than Opus at high with no caching ($0.29 a task), still 10/10. Tool search, context editing, and compaction didn't help there: the workload was too small. (`cb-cost`)
- **"Cheap and slightly wrong is still not an optimization."** Haiku subagents plus one Sonnet decider cut cost about 90% but missed a case, because condensing the manual into a rule card dropped a nested exception. (`cb-cost`)
- **Use-case docs pick by task (undated, older models).** Haiku 4.5 is the default for routing and volume moderation: 1B posts a month cost about $36,100 on Haiku 4.5 against $180,500 on Opus 5. Legal summaries default to Opus 5 for accuracy ($438.75 against $87.75 for 1,000 leases). Support uses Opus for long reasoning and Haiku once RAG and tools make latency bind. (`uc-routing`, `uc-moderation`, `uc-legal`, `uc-support`)

## Where the posts pull in different directions

- **Effort first, or a stronger model first?** The cost post says to raise effort before moving to a bigger model, because effort costs less (`cost`). The model and platform guides say a stronger model at low effort can be cheaper than a weaker model at high effort: Fable 5.1 at low matched Fable 5 at high on CursorBench 3.2 at a third of the cost (`models-explained`, `platform-cost`). The first is about getting unstuck on one task, the second about picking a default.
- **Multi-agent costs tokens.** Agents use about 4x the tokens of chat and multi-agent systems about 15x, and multi-agent typically costs 3-10x more than one agent for the same task (`research-system`, 2025-06-13, `when-multi-agent`, 2026-01-23). A later cookbook finds a frontier coordinator with cheap workers bills most of its reading at the worker rate, so at matched rigor the split can cost less than one frontier agent. It also finds a solo agent left to its own rigor is cheaper (`cb-plan-big`, 2026-07-02). Tokens and bill are different questions.

## Measure it yourself

- **Check three things in `/usage`.** A low cache share points to a long pause, a model switch, or an MCP change. A lot of output on a small change means effort is too high or the model retried. Total input many times the size of the conversation means the session looped, and it's worth reading where. (`cost`)
- **Run the same real task on both models three or four times before you decide.** "Your own numbers are the ones to trust." (`cost`)

## Key source articles
`cost` · `models-explained` · `platform-cost` · `caching` · `opus-5-5` · `cb-cost` · `cb-plan-big`
