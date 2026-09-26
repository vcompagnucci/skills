# Agents in production

What Anthropic and its customers learned putting agents into real work: where to start, where the agent should live, and what the docs use-case guides recommend. Many of these posts are customer stories, so the numbers are self-reported. The docs use-case guides add recommended processes and target metrics, and the cookbooks add worked examples.

## Where to start

- **Start with one simple, high-impact, low-risk task where oversight already exists.** In finance: support triage, knowledge retrieval, flagging unusual transactions. In healthcare: documentation first, then low-risk diagnostic support like abnormal lab flags. Early deployments are where teams learn the agent's limits cheaply. (`finance-agents`, `healthcare-agents`)
- **Not every workflow needs an agent.** Some organizations get better returns from simpler automation. (`healthcare-agents`)
- **Agents solve the "process completion problem".** Regulated work needs actions across several systems, not just information: the agent coordinates and drafts, and "the analyst makes the final decision". (`finance-agents`, `healthcare-agents`)
- **Build compliance, audit trails, and a safe failure state in from day one.** Decide up front which actions need human sign-off, and design the system to "fail in a known safe state". Healthcare teams that skip compliance "will be forced to rebuild sooner rather than later". (`finance-agents`, `healthcare-agents`)
- **Become the expert before building the agent.** Outtake's engineers ran real cyber investigations themselves to define what good evidence looks like, then prototyped in Claude Code and moved to the Agent SDK. They hardcoded what must always happen and left judgment free: "a filesystem and bash is all you need". (`outtake`)
- **An agent acting for you is capped by how well it understood you.** In a 201-person book market, imprecise preference intake caused ~85% of the shortfall. A stronger model moved outcomes ~0.08-0.12, while "ruthless" vs "prosocial" instructions moved them ~0.02. (`project-swap`)

## Put the agent where the work happens

- **Keep the agent in shared channels, not DMs.** Threads become a reviewable record. In one channel Claude Tag answered over 75% of questions within a minute or two. Map one thread to one session, `ack()` within Slack's 3-second window and do the work in the background, and persist the thread-to-session map. (`slack-analytics`, `cb-slack-bot`)
- **Put the approval where on-call already works.** The agent diagnoses, opens a PR, and calls a custom tool that posts an Approve button to the on-call channel. Custom tools are what pause the session for a human, and the session log is the audit trail with no extra instrumentation. (`cb-sre-responder`)
- **For a data bot in Slack, deployment is a separate problem from accuracy.** Serve skills fresh, add an internal knowledge index for the "why", scope the bot's service account because "everyone who can mention the bot has the bot's data access", and instrument every answer. Order: permissions, distribution, telemetry, knowledge index, analytics skills. (`slack-analytics`)

## What the docs use-case guides recommend

- **Support: write the ideal conversation, then split it into testable tasks.** Script a real example turn by turn in the actual words, to fix tone, length, and detail. Then decompose it (car insurance: greeting and guidance, product info, staying on topic, quote generation), each with its own prompt section and test cases. Put the bulk of the prompt in the first User turn and only the role in the system prompt. (`uc-support`)
- **Support targets.** 95%+ query comprehension, 90%+ response relevance, 100% on static company and product info, 80%+ relevant citations, 95%+ topic adherence and escalation accuracy. Business side: 70-80% deflection and CSAT of 4/5 or better. (`uc-support`)
- **Support: add RAG, tools, and a router only when you need them.** RAG handles large static context, tools are required for live data (balances, orders), and a separate intent classifier routing to specialized sub-conversations costs one extra call per turn. Opus 5 for long multi-step reasoning, Haiku 4.5 once latency binds. (`uc-support`)
- **Routing: accuracy follows the taxonomy.** Define intents and subcategories first, output `<reasoning>` before `<intent>`, default to Haiku 4.5. Past 20 categories, cascade classifiers. Retrieved similar tickets as few-shot examples lifted accuracy from 71% to 93%. Tell it to "ignore emotion, focus on intent". Targets: 95%+ consistency, 80%+ on edge cases, and 90%+ accuracy within 50-100 samples of a new category. (`uc-routing`)
- **Moderation: keep the verdict out of the model.** Claude compiles the policy into rules and extracts fields, and a model-free engine decides, returning `needs_review` when a field is unknown, so identical inputs get identical, auditable decisions. A plain classification prompt is kept for policies that don't change (`cb-moderation`). At volume, 1B posts a month costs ~$36,100 on Haiku 4.5 vs ~$180,500 on Opus 5 (`uc-moderation`).
- **Legal: say which details to extract, since there is no single correct summary.** Tagged sections per requested detail, chunk-then-combine meta-summarization for long documents, Opus 5 by default ($438.75 vs $87.75 on Haiku for 1,000 subleases), and a disclaimer that a lawyer must review. (`uc-legal`)
- **Commerce: two agents, and neither acts on its own.** Shopping and merchant agents reach business systems only through a backend interface, and no shopping method can place an order or move money (approval design in `safety-and-containment.md`). (`uc-commerce`)

## Key source articles
`uc-support` · `uc-routing` · `uc-moderation` · `slack-analytics` · `cb-slack-bot` · `cb-sre-responder` · `outtake` · `project-swap` · `finance-agents` · `healthcare-agents`
