# Agents in production

What Anthropic and its customers learned putting agents into real work: where to start, where the agent should live, and how Anthropic runs its own. Many of these posts are customer stories or product pages, so the positions are thinner than in the engineering posts, and the numbers are self-reported.

## Where to start

- **Start with one simple, high-impact, low-risk task where oversight already exists.** In finance: support triage, knowledge retrieval, flagging unusual transactions. In healthcare: documentation first, then low-risk diagnostic support like abnormal lab flags. Early deployments are where teams learn the agent's limits cheaply. (`finance-agents`, `healthcare-agents`)
- **Not every workflow needs an agent.** Some organizations get better returns from simpler automation. (`healthcare-agents`)
- **Agents solve the "process completion problem".** Regulated work needs actions across several systems, not just information: the agent coordinates and drafts, and "the analyst makes the final decision". (`finance-agents`, `healthcare-agents`)
- **Build compliance, audit trails, and a safe failure state in from day one.** Decide up front which actions need human sign-off, and design the system to "fail in a known safe state". Healthcare teams that skip compliance "will be forced to rebuild sooner rather than later". (`finance-agents`, `healthcare-agents`)
- **Become the expert before building the agent.** Outtake's engineers ran real cyber investigations themselves to define what good evidence looks like, then prototyped in Claude Code and moved to the Agent SDK. They hardcoded what must always happen and left judgment free: "a filesystem and bash is all you need". (`outtake`)

## Put the agent where the work happens

- **Bolting AI features onto a product hits a ceiling.** monday.com's "AI month" features drew excitement but no sustained use. They rebuilt so agents are teammates with names and permissions, assigned work on the board, and customers logged 5M+ agent interactions. "Adopting AI features is not the same as becoming an AI company." (`monday`)
- **Chain narrow agents and leave one human decision at the end.** A strategist agent, a page builder, and a brand reviewer prepare a campaign, and the manager decides. Adoption depends on trust (governance, permissions, transparency) as much as capability. (`monday`)
- **Keep the agent in shared channels, not DMs.** Threads become a reviewable record. In one channel Claude Tag answered over 75% of questions within a minute or two. (`slack-analytics`)
- **One agent can cover a whole customer journey.** The commerce shopping agent searches, plans multi-item carts, and handles orders and returns instead of sending people to a support page. Guardrails keep prices and products tied to the real catalog, and merchant changes need human approval. (`commerce-launch`)
- **Measure cost per completed task, and when close, choose intelligence.** Outcome quality moves business metrics more than marginal latency. Cut latency with fewer turns, eager tool dispatch, and streamed UI, not by using a weaker model. (`commerce-agents`)
- **Frame the agent as a supervised teammate in high-stakes work.** Millennium's risk analyst logs its reasoning, tests actions in sandboxes, and needs human approval. (`millennium`)
- **Ground agents in data the team already trusts.** Finance plugins connect FactSet, MSCI, S&P, and LSEG, "proprietary data and specialized platforms that no general-purpose plugin can replicate". (`cowork-finance`)

## Collaboration, not delegation

- **Engineers shift from writing code to coordinating agents, but they can fully delegate little.** Developers use AI in about 60% of their work but fully delegate only 0-20% of tasks. "The organizations pulling ahead aren't removing engineers from the loop." (`eight-trends`)
- **Leaders encode institutional knowledge into systems that compound.** Adoption doubled from 2023, and the open question is whether gains compound or plateau. (`enterprise-agents`)
- **Humans steer, and the agent is multi-player.** On-call fixes arrive as PRs a named human reviews and merges, and teammates add hypotheses in real time. (`ci-first-responder`)

## How Anthropic runs its own agents

- **Speed: measuring made it tractable.** claude.ai got about 3x faster in two weeks, with 3,000+ changes and no customer incident. Claude picked four journeys from usage data, built deterministic benchmarks, proved they tracked wall-clock time, and ratcheted each win in CI. Each thread ran the same loop: benchmark, risk-sized PRs behind flags, watch the field data, ratchet or roll back. It found 6,900 hooks re-rendering per keystroke, and em dashes forcing slow UTF-16 regex paths. People pushed ambition ("please be braver") and ruled on taste. (`faster`)
- **CI on-call: the agent is the first responder.** Claude Tag has memory, its own service account, scheduled routines, and instructions as skills in a repo. Alerting stays deterministic. Investigation runs as an orchestrator with parallel executors, with a first grounded analysis in a median 14 minutes. "The only way to keep up with agentic coding is agentic CI." (`ci-first-responder`)
- **Data questions in Slack: deployment is a separate problem from accuracy.** Serve skills fresh, add an internal knowledge index for the "why", scope the bot's service account because "everyone who can mention the bot has the bot's data access", and instrument every answer. Order: permissions, distribution, telemetry, knowledge index, analytics skills. (`slack-analytics`)
- **Security review at agent speed.** Narrow review agents, shift-left rules in CLAUDE.md, and hard boundaries on what agents can reach (see `safety-and-containment.md`). (`secure-sdlc`)
- **PMs build against the spec instead of reviewing it in a doc.** Sketching an agent against pre-production API specs reshaped the Managed Agents API several times, and one bespoke agent per job automates the operational long tail. (`product-dev`)

## Key source articles
`faster` · `ci-first-responder` · `slack-analytics` · `outtake` · `monday` · `commerce-agents` · `finance-agents` · `eight-trends`
