# Architecture and multi-agent systems

Whether to build an agent at all, which shape to give it, and when to split work across agents. The position has been stable since December 2024: start with the simplest thing that works and add structure only when you can measure that it helps. What changed is how capable the single agent became.

## Start simple

- **Maybe don't build an agent at all.** Agentic systems trade latency and cost for performance, and for many applications a single LLM call with retrieval and examples is enough. Across dozens of customer teams, the most successful used simple, composable patterns, not complex frameworks. "You should consider adding complexity only when it demonstrably improves outcomes." (`effective-agents`)
- **Workflows and agents are different things.** A workflow runs LLMs and tools through predefined code paths and suits well-defined tasks. An agent directs its own process and tool use, "just LLMs using tools based on environmental feedback in a loop". (`effective-agents`)
- **Workflows shape where the agent applies autonomy, they don't replace it.** Each step still reasons and uses tools, but the overall flow and checkpoints are fixed. (`workflow-patterns`)
- **Try the task as one agent call first.** Put the whole pipeline in one prompt. Where it falls short tells you which pattern you need, and the single agent becomes your baseline. "Can a single agent handle this task effectively? If yes, don't use workflows at all." (`workflow-patterns`)
- **Call the API directly before reaching for a framework.** Frameworks hide prompts and responses and tempt extra complexity, and wrong assumptions about what's underneath are a common source of customer errors. (`effective-agents`)
- **The definition got simpler over time.** By September 2025 an agent was "LLMs autonomously using tools in a loop", and the 2024 post now carries a note that its tooling has changed, pointing to Managed Agents. (`effective-context`, `effective-agents`)

## The patterns

- **Five workflow patterns cover most production systems (2024).** Prompt chaining, routing (Haiku for easy queries, Sonnet for hard ones), parallelization (sectioning or voting), orchestrator-workers, and evaluator-optimizer, each with its own fit condition. (`effective-agents`)
- **Three cover the vast majority (2026).** Sequential is the default and trades latency for accuracy. Parallel is for when latency is the bottleneck and tasks are independent, and you design the aggregation (vote, average, defer to the specialist) before building. Evaluator-optimizer fits measurable criteria, and you skip it when a linter already exists. Set stopping criteria before iterating, and nest patterns only when it measurably helps. (`workflow-patterns`)
- **For multi-agent coordination, start with orchestrator-subagent and evolve from observed failure.** Generator-verifier needs explicit criteria and an iteration cap. Agent teams keep persistent workers on a shared queue. A message bus suits event-driven routing but is hard to trace. Shared state removes the coordinator but needs a time budget or convergence rule to stop. "These patterns are building blocks, not mutually exclusive choices." (`coordination-patterns`)
- **Pick the pattern with structural questions.** Must workers keep state across calls? Is the sequence known in advance? Do agents need each other's findings? Are you routing events or accumulating knowledge? (`coordination-patterns`)

## When multi-agent pays

- **Most teams use multi-agent where one agent would do better.** Months of elaborate architecture were matched by better prompting on a single agent, and multi-agent typically costs 3-10x the tokens for the same task. (`when-multi-agent`)
- **Only three situations justify it.** Context pollution (a subtask that returns 1,000+ mostly irrelevant tokens), parallelizable work, and specialization when tools or prompts conflict (20+ tools, confused domains). Try tool search before splitting. "These thresholds will shift as models improve." (`when-multi-agent`)
- **It works mainly because it spends more tokens.** On BrowseComp, token usage alone explained 80% of the variance. The research system (Opus 4 lead, Sonnet 4 subagents) beat single-agent Opus 4 by 90.2%. Agents use about 4x the tokens of chat, and multi-agent about 15x, so reserve it for valuable, parallel work. (`research-system`)
- **Parallelism buys thoroughness, not speed.** The research system gets more accurate, but often takes longer end to end. (`when-multi-agent`)
- **One long context fails in three named ways.** Agentic laziness (35 of 50 items, then "done"), self-preferential bias, and goal drift after lossy compaction. Separate subagents with isolated goals counter all three. (`workflows`)
- **Multi-agent is a poor fit for tightly coupled work.** Tasks needing shared context or many dependencies, including most coding, don't split well. A commerce conversation is one session, so a single agent with skills beat subagent designs on quality, cost, and speed. (`research-system`, `commerce-agents`)

## How to split

- **Decompose by context, not by type of work.** Planner, implementer, tester, and reviewer agents play a game of telephone, and in one experiment they spent more tokens coordinating than working. The agent that writes a feature should write its tests. (`when-multi-agent`, `coordination-patterns`)
- **The orchestrator is an information bottleneck.** When one subagent's finding matters to another, it gets summarized away passing through the center. Writing artifacts to a filesystem and passing references avoids the telephone game. (`coordination-patterns`, `research-system`)
- **Give each subagent a full brief.** Objective, output format, tools and sources, boundaries. "Research the semiconductor shortage" produced one subagent on 2021 auto chips and two duplicating each other. Add effort-scaling rules, because early agents spawned 50 subagents for simple questions. (`research-system`)
- **Verification needs little context, so it splits well.** A verifier gets the artifact, the criteria, and tools, not the history. But verifiers declare victory early unless told exactly what to check. (`when-multi-agent`)

## Dynamic workflows and agent teams

- **Claude can write the orchestration script per task.** A JS file with `agent()`, `parallel()`, and `pipeline()`, picking each agent's model and worktree, resumable after interruption. Six patterns: classify-and-act, fan-out-and-synthesize, adversarial verification, generate-and-filter, tournament, loop until done. "Most traditional coding tasks do not need a panel of 5 reviewers." (`workflows`)
- **Use cases from the workflows post.** Migrations with one subagent per call site in its own worktree (Bun went from Zig to Rust this way). Sorting 1,000+ items as a tournament, since comparing two items beats scoring one. One verifier per CLAUDE.md rule plus a skeptic. Root causes from hypotheses built on separate evidence. Triage with quarantine, where agents that read untrusted content get no privileges. Also non-technical work: business-plan teardowns, resume ranking, naming tournaments. (`workflows`)
- **A dumb loop plus a file lock can coordinate a team.** Sixteen agents built a 100,000-line C compiler that boots Linux 6.9 in two weeks, for just under $20,000, each running `claude -p` in a loop and claiming tasks by writing a file. No orchestrator, no messaging. Parallelism only worked once GCC served as an oracle to split the monolithic kernel build into independent failures. (`c-compiler`)
- **Parallel agents allow specialized roles.** Separate agents removed duplicate code, tuned performance, and critiqued the design as a Rust developer would. (`c-compiler`)

## Key source articles
`effective-agents` · `workflow-patterns` · `when-multi-agent` · `coordination-patterns` · `research-system` · `workflows` · `c-compiler`
