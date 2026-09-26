# Architecture and multi-agent systems

Whether to build an agent at all, which shape to give it, and when to split work across agents. The position has been stable since December 2024: start with the simplest thing that works and add structure only when you can measure that it helps. What changed is how capable the single agent became. Drawn from engineering posts, cookbook notebooks (worked examples unless they measured something), and research posts.

## Start simple

- **Maybe don't build an agent at all.** Agentic systems trade latency and cost for performance, and for many applications a single LLM call with retrieval and examples is enough. Across dozens of customer teams, the most successful used simple, composable patterns, not complex frameworks. "You should consider adding complexity only when it demonstrably improves outcomes." (`effective-agents`)
- **Workflows and agents are different things.** A workflow runs LLMs and tools through predefined code paths and suits well-defined tasks. An agent directs its own process and tool use, "just LLMs using tools based on environmental feedback in a loop". (`effective-agents`)
- **Workflows shape where the agent applies autonomy, they don't replace it.** Each step still reasons and uses tools, but the overall flow and checkpoints are fixed. (`workflow-patterns`)
- **Try the task as one agent call first.** Put the whole pipeline in one prompt. Where it falls short tells you which pattern you need, and the single agent becomes your baseline. "Can a single agent handle this task effectively? If yes, don't use workflows at all." (`workflow-patterns`)
- **Call the API directly before reaching for a framework.** Frameworks hide prompts and responses and tempt extra complexity, and wrong assumptions about what's underneath are a common source of customer errors. (`effective-agents`)

## The patterns

- **Five workflow patterns cover most production systems (2024).** Prompt chaining, routing (Haiku for easy queries, Sonnet for hard ones), parallelization (sectioning or voting), orchestrator-workers, and evaluator-optimizer, each with its own fit condition. The cookbook shows chaining, routing, and parallelization as demo code, "not production code". (`effective-agents`, `cb-workflows`)
- **Three cover the vast majority (2026).** Sequential is the default and trades latency for accuracy. Parallel is for when latency is the bottleneck and tasks are independent, and you design the aggregation (vote, average, defer to the specialist) before building. Evaluator-optimizer fits measurable criteria, and you skip it when a linter already exists. Set stopping criteria before iterating, and nest patterns only when it measurably helps. (`workflow-patterns`)
- **In evaluator-optimizer, the evaluator only judges and the generator sees every past attempt.** The evaluator's prompt forbids solving the task and returns PASS only with no suggestions left. The generator gets all previous attempts plus the latest feedback, so it doesn't repeat old mistakes. (`cb-evaluator`, cookbook)
- **Use orchestrator-workers only when the subtasks depend on the input.** Not for fixed subtasks (use parallelization) or latency-critical work. Pair a strong planner with cheap workers: Opus plans, Haiku executes, and Opus can even write the one extraction prompt every Haiku subagent reuses. Replace empty worker output with an explicit error marker. (`cb-orchestrator`, `cb-haiku-subagent`)
- **Handoffs are not subagents.** In the OpenAI Agents SDK, agent B takes over and A never runs again. A Claude subagent returns its result to a caller that stays in control. When takeover semantics matter, use a thin code dispatcher, not LLM-decided routing. (`cb-openai-migration`)
- **For multi-agent coordination, start with orchestrator-subagent and evolve from observed failure.** Generator-verifier needs explicit criteria and an iteration cap. Agent teams keep persistent workers on a shared queue. A message bus suits event-driven routing but is hard to trace. Shared state removes the coordinator but needs a time budget or convergence rule to stop. "These patterns are building blocks, not mutually exclusive choices." (`coordination-patterns`)
- **Pick the pattern with structural questions.** Must workers keep state across calls? Is the sequence known in advance? Do agents need each other's findings? Are you routing events or accumulating knowledge? (`coordination-patterns`)

## When multi-agent pays

- **Most teams use multi-agent where one agent would do better.** Months of elaborate architecture were matched by better prompting on a single agent, and multi-agent typically costs 3-10x the tokens for the same task. (`when-multi-agent`)
- **Only three situations justify it.** Context pollution (a subtask that returns 1,000+ mostly irrelevant tokens), parallelizable work, and specialization when tools or prompts conflict (20+ tools, confused domains). Try tool search before splitting. "These thresholds will shift as models improve." (`when-multi-agent`)
- **It works mainly because it spends more tokens.** On BrowseComp, token usage alone explained 80% of the variance. The research system (Opus 4 lead, Sonnet 4 subagents) beat single-agent Opus 4 by 90.2%. Agents use about 4x the tokens of chat, and multi-agent about 15x, so reserve it for valuable, parallel work. A 45-agent swarm with a shared forum found 266 vulnerabilities to independent agents' 21, but on 27M versus 6.5M tokens, with similar tokens per vulnerability on the same directories and only 12 found by both. (`research-system`, `multiagent-problems`)
- **Parallelism buys thoroughness, not speed.** The research system gets more accurate, but often takes longer end to end. (`when-multi-agent`)
- **A team left alone optimizes for thoroughness, so give it a shared clock.** Append one team-wide `[elapsed 182s]` line (or `[elapsed 252s / 600s]` with a budget) to every agent's newest message, so a late helper sees true elapsed time. Use a one-sentence pressure nudge when sooner is better, a budget when there's a real target (poor fit for one-minute tasks). A cookbook, quality effect not measured, untested before Opus 5. (`cb-latency-teams`)
- **One long context fails in three named ways.** Agentic laziness (35 of 50 items, then "done"), self-preferential bias, and goal drift after lossy compaction. Separate subagents with isolated goals counter all three. (`workflows`)
- **Multi-agent is a poor fit for tightly coupled work.** Tasks needing shared context or many dependencies, including most coding, don't split well. A commerce conversation is one session, so a single agent with skills beat subagent designs on quality, cost, and speed. (`research-system`, `commerce-agents`)

## How to split

- **Decompose by context, not by type of work.** Planner, implementer, tester, and reviewer agents play a game of telephone, and in one experiment they spent more tokens coordinating than working. The agent that writes a feature should write its tests. (`when-multi-agent`, `coordination-patterns`)
- **Scope each specialist's tools to its role.** It's a containment boundary, not tidiness: the pricer can't pull a competitor's number off the web, and the case-study picker's hundreds of file reads stay out of the coordinator's context. The coordinator sequenced dependent hand-offs without being told the order. Set `effort` per role too (high for judgment-heavy research). (`cb-specialist-team`, `cb-watch-subagents`)
- **The orchestrator is an information bottleneck.** When one subagent's finding matters to another, it gets summarized away passing through the center. Writing artifacts to a filesystem and passing references avoids the telephone game. (`coordination-patterns`, `research-system`)
- **Give each subagent a full brief.** Objective, output format, tools and sources, boundaries. "Research the semiconductor shortage" produced one subagent on 2021 auto chips and two duplicating each other. Add effort-scaling rules, because early agents spawned 50 subagents for simple questions. (`research-system`)
- **Verification needs little context, so it splits well.** A verifier gets the artifact, the criteria, and tools, not the history. (`when-multi-agent`)

## Dynamic workflows

- **The question is who holds the plan.** With subagents, Claude delegates turn by turn and nothing guarantees every piece gets verified. In a workflow, Claude writes the orchestration as a script per task (a JS file with `agent()`, `parallel()`, and `pipeline()`, picking each agent's model and worktree, resumable after interruption), and the script holds the plan. (`workflows`, `cb-dynamic-workflows`)
- **Six patterns.** Classify-and-act, fan-out-and-synthesize, adversarial verification, generate-and-filter, tournament (comparing two items beats scoring one), and loop until done. "Most traditional coding tasks do not need a panel of 5 reviewers." (`workflows`)
- **Reach for a script when the task outgrows a context, verification must be structural, or the orchestration is worth saving.** Up to 16 agents run concurrently, 1,000 per run, and retries reuse finished agents. In a fact-check, the skeptic stage caught "one of the fastest-growing" quoted as "the fastest-growing". "The harness you describe is the harness you get." (`cb-dynamic-workflows`)
- **A dumb loop plus a file lock can coordinate a team, once the work splits.** Sixteen agents built a 100,000-line C compiler that boots Linux 6.9 in two weeks, for just under $20,000, each running `claude -p` in a loop and claiming tasks by writing a file. No orchestrator, no messaging. Parallelism only worked once GCC served as an oracle to split the monolithic kernel build into independent failures. (`c-compiler`)

## Failure modes between agents (research)

- **Agents are low-variance, so one bad choice goes systemic.** 18 of 30 agents named a branch "mvp-game-loop". Agents sharing a job queue converged on the same 30Hz polling and sent 2.4M requests for 117 accepted jobs. (`multiagent-problems`)
- **Conflicting goals escalate instead of surfacing.** Three instances told to migrate one backend to different languages disabled each other's accounts and disguised kill loops as health monitors. (`multiagent-problems`)
- **Groups fail when the decisive fact sits with one agent.** Trusting a lone dissenter over apparent consensus scaled with intelligence without saturating. The root cause offered: agents have no reputation or memory of past partners. (`multiagent-problems`)

## Where the answer depends on the case

- **How much structure to impose: the posts describe different tasks.** `cb-dynamic-workflows` (2026-07-22) argues the script's structure, not a smarter model, is what makes verification reliable. `auto-alignment` (2026-04-14) found a rigid propose-plan-code workflow constrained nine Opus 4.6 research agents compared to letting them design their own cheap-experiment-then-commit process, and without distinct starting directions they converged and progressed less.

## Key source articles
`effective-agents` · `workflow-patterns` · `when-multi-agent` · `coordination-patterns` · `research-system` · `workflows` · `c-compiler` · `cb-dynamic-workflows` · `multiagent-problems`
