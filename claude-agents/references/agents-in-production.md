# Agents in production

What Anthropic and its customers learned putting agents into real work: where to start, where the agent should live, and how Anthropic runs its own. Many of these posts are customer stories or product pages, so the positions are thinner than in the engineering posts, and the numbers are self-reported. The docs use-case guides add recommended processes and target metrics, the cookbooks add worked examples, and the research posts add usage data and field experiments.

## Where to start

- **Start with one simple, high-impact, low-risk task where oversight already exists.** In finance: support triage, knowledge retrieval, flagging unusual transactions. In healthcare: documentation first, then low-risk diagnostic support like abnormal lab flags. Early deployments are where teams learn the agent's limits cheaply. (`finance-agents`, `healthcare-agents`)
- **Not every workflow needs an agent.** Some organizations get better returns from simpler automation. (`healthcare-agents`)
- **Agents solve the "process completion problem".** Regulated work needs actions across several systems, not just information: the agent coordinates and drafts, and "the analyst makes the final decision". (`finance-agents`, `healthcare-agents`)
- **Build compliance, audit trails, and a safe failure state in from day one.** Decide up front which actions need human sign-off, and design the system to "fail in a known safe state". Healthcare teams that skip compliance "will be forced to rebuild sooner rather than later". (`finance-agents`, `healthcare-agents`)
- **Become the expert before building the agent.** Outtake's engineers ran real cyber investigations themselves to define what good evidence looks like, then prototyped in Claude Code and moved to the Agent SDK. They hardcoded what must always happen and left judgment free: "a filesystem and bash is all you need". (`outtake`)

## Put the agent where the work happens

- **Bolting AI features onto a product hits a ceiling.** monday.com's "AI month" features drew excitement but no sustained use. They rebuilt so agents are teammates with names and permissions, assigned work on the board, and customers logged 5M+ agent interactions. "Adopting AI features is not the same as becoming an AI company." (`monday`)
- **Chain narrow agents and leave one human decision at the end.** A strategist agent, a page builder, and a brand reviewer prepare a campaign, and the manager decides. Adoption depends on trust (governance, permissions, transparency) as much as capability. (`monday`)
- **Keep the agent in shared channels, not DMs.** Threads become a reviewable record. In one channel Claude Tag answered over 75% of questions within a minute or two. Map one thread to one session, `ack()` within Slack's 3-second window and do the work in the background, and persist the thread-to-session map. (`slack-analytics`, `cb-slack-bot`)
- **Put the approval where on-call already works.** The agent diagnoses, opens a PR, and calls a custom tool that posts an Approve button to the on-call channel. Custom tools are what pause the session for a human, and the session log is the audit trail with no extra instrumentation. (`cb-sre-responder`)
- **One agent can cover a whole customer journey.** The commerce shopping agent searches, plans multi-item carts, and handles orders and returns instead of sending people to a support page. Guardrails keep prices and products tied to the real catalog, and merchant changes need human approval. (`commerce-launch`)
- **Measure cost per completed task, and when close, choose intelligence.** Outcome quality moves business metrics more than marginal latency. Cut latency with fewer turns, eager tool dispatch, and streamed UI, not by using a weaker model. (`commerce-agents`)
- **Frame the agent as a supervised teammate in high-stakes work.** Millennium's risk analyst logs its reasoning, tests actions in sandboxes, and needs human approval. (`millennium`)
- **Ground agents in data the team already trusts.** Finance plugins connect FactSet, MSCI, S&P, and LSEG, "proprietary data and specialized platforms that no general-purpose plugin can replicate". (`cowork-finance`)

## Collaboration, not delegation

- **Engineers shift from writing code to coordinating agents, but they can fully delegate little.** Developers use AI in about 60% of their work but fully delegate only 0-20% of tasks. "The organizations pulling ahead aren't removing engineers from the loop." (`eight-trends`, `work-at-anthropic`)
- **People delegate what is verifiable and self-contained, and keep taste.** Anthropic's own survey (132 engineers, 200,000 transcripts) found 27% of Claude-assisted work wouldn't have happened otherwise. Its warning is the "paradox of supervision": supervising Claude needs the skills that over-delegation erodes. (`work-at-anthropic`)
- **People plan, Claude executes, and domain expertise predicts success.** Across ~400,000 Claude Code sessions, people made ~70% of planning decisions and ~20% of execution ones. Verified success went from 15% for novices to 28-33% for experts, and software occupations barely beat others (34% vs 29%). (`cc-in-practice`)
- **Oversight moves from approving to monitoring.** With experience, full auto-approve rises from ~20% to over 40% of sessions while interrupts rise from ~5% to ~9%. Claude stops to ask more than humans interrupt it. The study advises post-deployment monitoring over mandated per-action approval. (`agent-autonomy`)
- **An agent acting for you is capped by how well it understood you.** In a 201-person book market, imprecise preference intake caused ~85% of the shortfall. A stronger model moved outcomes ~0.08-0.12, while "ruthless" vs "prosocial" instructions moved them ~0.02. (`project-swap`)
- **Leaders encode institutional knowledge into systems that compound.** Adoption doubled from 2023, and the open question is whether gains compound or plateau. (`enterprise-agents`)
- **Humans steer, and the agent is multi-player.** On-call fixes arrive as PRs a named human reviews and merges, and teammates add hypotheses in real time. (`ci-first-responder`)

## How Anthropic runs its own agents

- **Speed: measuring made it tractable.** claude.ai got about 3x faster in two weeks, with 3,000+ changes and no customer incident. Claude picked four journeys from usage data, built deterministic benchmarks, proved they tracked wall-clock time, and ratcheted each win in CI. Each thread ran the same loop: benchmark, risk-sized PRs behind flags, watch the field data, ratchet or roll back. It found 6,900 hooks re-rendering per keystroke, and em dashes forcing slow UTF-16 regex paths. People pushed ambition ("please be braver") and ruled on taste. (`faster`)
- **CI on-call: the agent is the first responder.** Claude Tag has memory, its own service account, scheduled routines, and instructions as skills in a repo. Alerting stays deterministic. Investigation runs as an orchestrator with parallel executors, with a first grounded analysis in a median 14 minutes. "The only way to keep up with agentic coding is agentic CI." (`ci-first-responder`)
- **Data questions in Slack: deployment is a separate problem from accuracy.** Serve skills fresh, add an internal knowledge index for the "why", scope the bot's service account because "everyone who can mention the bot has the bot's data access", and instrument every answer. Order: permissions, distribution, telemetry, knowledge index, analytics skills. (`slack-analytics`)
- **Security review at agent speed.** Narrow review agents, shift-left rules in CLAUDE.md, and hard boundaries on what agents can reach (see `safety-and-containment.md`). (`secure-sdlc`)
- **Project Vend: scaffolding fixed honest mistakes, not manipulation.** Claudius (Sonnet 3.7) lost money running an office shop: it hallucinated a Venmo account and was talked into discounts. In phase two a CRM, costs shown in inventory, and forced price research before quoting helped ("bureaucracy matters"), a separate merch agent with a clear role did well, but staff still fooled it. (`vend-1`, `vend-2`)
- **PMs build against the spec instead of reviewing it in a doc.** Sketching an agent against pre-production API specs reshaped the Managed Agents API several times, and one bespoke agent per job automates the operational long tail. (`product-dev`)

## What the docs use-case guides recommend

- **Support: write the ideal conversation, then split it into testable tasks.** Script a real example turn by turn in the actual words, to fix tone, length, and detail. Then decompose it (car insurance: greeting and guidance, product info, staying on topic, quote generation), each with its own prompt section and test cases. Put the bulk of the prompt in the first User turn and only the role in the system prompt. (`uc-support`)
- **Support targets.** 95%+ query comprehension, 90%+ response relevance, 100% on static company and product info, 80%+ relevant citations, 95%+ topic adherence and escalation accuracy. Business side: 70-80% deflection and CSAT of 4/5 or better. (`uc-support`)
- **Support: add RAG, tools, and a router only when you need them.** RAG handles large static context, tools are required for live data (balances, orders), and a separate intent classifier routing to specialized sub-conversations costs one extra call per turn. Opus 5 for long multi-step reasoning, Haiku 4.5 once latency binds. (`uc-support`)
- **Routing: accuracy follows the taxonomy.** Define intents and subcategories first, output `<reasoning>` before `<intent>`, default to Haiku 4.5. Past 20 categories, cascade classifiers. Retrieved similar tickets as few-shot examples lifted accuracy from 71% to 93%. Tell it to "ignore emotion, focus on intent". Targets: 95%+ consistency, 80%+ on edge cases. (`uc-routing`)
- **Moderation: score risk, define categories, and weigh keeping the model out of the verdict.** A 0-3 risk scale lets high risk auto-block and medium go to humans, and a written definition of each category catches what labels miss. 1B posts a month costs ~$36,100 on Haiku 4.5 vs ~$180,500 on Opus 5. The cookbook alternative has Claude compile policy into rules and extract fields, and a model-free engine returns `needs_review` when a field is unknown. (`uc-moderation`, `cb-moderation`)
- **Legal: say which details to extract, since there is no single correct summary.** Tagged sections per requested detail, chunk-then-combine meta-summarization for long documents, Opus 5 by default ($438.75 vs $87.75 on Haiku for 1,000 subleases), and a disclaimer that a lawyer must review. (`uc-legal`)
- **Commerce: two agents, and neither acts on its own.** Shopping and merchant agents reach business systems only through a backend interface. No shopping method can place an order or move money, and every merchant write is staged for human approval (see `safety-and-containment.md`). (`uc-commerce`)

## Where the posts disagree

- **Should the model decide a moderation verdict?** The docs guide (`uc-moderation`, undated) has Claude classify and score risk directly. The cookbook (`cb-moderation`, 2026-08-13) keeps every verdict in a model-free rule engine so identical inputs get identical, auditable decisions, and reserves a plain classification prompt for policies that don't change.

## Key source articles
`faster` · `ci-first-responder` · `slack-analytics` · `outtake` · `monday` · `commerce-agents` · `finance-agents` · `eight-trends` · `uc-support` · `cc-in-practice`
