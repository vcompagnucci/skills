# More than one agent

## Whether to split

```
Does one agent with good tools and a clear prompt fail at this?
├── No → stay with one agent
└── Yes → Is the failure one of these three?
    ├── A subtask floods the context (it returns 1,000+ mostly irrelevant tokens) → subagent that returns a summary
    ├── Independent work that can run in parallel → parallel subagents, aggregation designed first
    ├── 20+ tools or conflicting instructions confuse it → try loading tools on demand first, then split by domain
    └── None → fix the prompt and tools instead
```

- **Multi-agent costs 3 to 10 times the tokens of one agent for the same task,** and it works mainly because it spends more. Better prompting on one agent matched months of multi-agent architecture in Anthropic's customer work.
- **A conversation with a customer is one session.** A single agent loading the right procedures beat subagent designs on quality, cost, and speed for commerce chat. Split the back office (a review, an investigation), not the conversation.
- **Split by context, not by type of work.** Planner, implementer, and reviewer agents play telephone and spend more tokens coordinating than working. The agent that does a piece of work also checks its own result. A separate verifier only needs the artifact, the criteria, and tools, not the history.
- **One agent writes; others advise.** Parallel agents changing the same state conflict. Extra agents earn their place as a clean-context reviewer or a specialist the writer consults.

## Who keeps the conversation

- **A manager calls specialists as tools and keeps the customer;** use it when one voice should answer and shared checks run in one place. **A handoff gives the conversation to another agent for good;** use it when a specialist fully takes over. The question is who owns the final answer.
- **Route in code when ownership matters.** Classify the request with structured output and pick the specialist in code. A model-decided transfer can route differently on the same request, and a takeover that's wrong is hard to undo.
- **A handoff forwards the whole transcript unless you narrow it, and narrowing is not redaction.** Tool arguments and results survive inside a generated summary. Treat the receiving agent and its model provider as recipients of everything forwarded.
- **An agent called as a tool starts a nested run.** Give it structured input, not a free-text string, and extract its output before the caller sees it, with a fallback when it's malformed.
- **Backend actions stay with the main agent.** In OpenAI's Agents API, subagents can't call your function tools at all, and keeping refunds and account changes in one agent keeps one place to check them.

## Briefing a subagent

- **Give a full brief:** the objective, the output format, the tools and sources it may use, and where to stop. A one-line task produced duplicated and off-target work in Anthropic's research system.
- **Pass references, not summaries.** When one agent's finding matters to another, write it to a shared store and pass the path. The orchestrator summarizes details away when they pass through it.
- **Tell it whether it may spawn agents of its own.** Without a rule, recursion has no floor.

## Failures between agents

- **Agents make the same choice the same way, so one bad default spreads.** Agents sharing a job queue converged on the same polling rate and sent 2.4 million requests for 117 jobs. Give each agent its own limits.
- **Interactive supervision tops out at 3 to 5 parallel sessions** per person. Past that, the bottleneck is human attention, not the agents.

## Where the answer depends on the case

- **How readily to spawn subagents.** OpenAI's GPT-5.6 guide says spawning is steerable and to prompt for it where it helps. Codex ships both settings: one tool forbids spawning unless the user asks, while its orchestrator prefers several subagents. Anthropic warns most teams use multi-agent where one agent would do better. Decide from measured cost and quality on your own task, never by default.
