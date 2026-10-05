# More than one agent

## Whether to split

```
Does one agent with good tools and a clear prompt fail at this?
├── No → stay with one agent
└── Yes → Is the failure one of these three?
    ├── A subtask floods the context (it returns 1,000+ mostly irrelevant tokens) → subagent that returns a summary
    ├── Independent work that can run in parallel → parallel subagents, aggregation designed first
    ├── Too many or overlapping tools, or conflicting instructions → load tools on demand and fix overlap first (tools.md), then split by domain
    └── None → fix the prompt and tools instead
```

- **Multi-agent uses 3 to 10 times the tokens of one agent for the same task,** and it works because it spends more. Billed cost can come out lower when a strong coordinator hands the reading to cheap workers, so compare at the same rigor. Better prompting on one agent matched months of elaborate architecture, per Anthropic.
- **Splitting has a ceiling.** In Google's 2026 study, splitting sequential work lost 39% to 70%, adding agents made results worse once one agent passed about 45% success, and independent agents amplified errors 17.2 times against 4.4 times under one coordinator. Stay with one agent for dependent steps, short tasks, work dominated by one slow external call, or a process that must run in a fixed order.
- **One agent keeps the customer conversation.** A single agent loading the right procedures beat subagent designs on quality, cost, and speed for commerce chat. Split the back office (a review, an investigation), not the conversation.
- **Split by context, not by type of work.** Planner, implementer, and reviewer agents play telephone and spend more tokens coordinating than working. The agent that does a piece of work also writes its checks (tests, validations), except on a large back-office task (next bullet). When a second opinion is needed, a clean-context verifier gets only the artifact, the criteria, and tools, not the history.
- **For a large back-office task, have a separate validator write the completion standard before work starts** (what must be true and how to check each part), and keep its cases hidden from the worker. The worker still writes its own unit tests, and an orchestrator decides when the work is done. One agent judging its own completion stopped at 36% on a port where the three roles reached 90% (Factory, 2026-08, not compute-matched).
- **One agent writes; others advise.** Parallel agents changing the same state conflict. Extra agents earn their place as a clean-context reviewer or a specialist the writer consults.

## Who keeps the conversation

- **A manager calls specialists as tools and keeps the customer;** use it when one voice should answer and shared checks run in one place. **A handoff gives the conversation to another agent for good;** use it when a specialist fully takes over. The question is who owns the final answer.
- **Route in code when ownership matters.** Classify the request with structured output and pick the specialist in code. A model-decided transfer can route differently on the same request, and a takeover that's wrong is hard to undo.
- **A handoff forwards the whole transcript unless you narrow it.** Decide what the receiving agent needs; what leaks through a summary is a security question.
- **An agent called as a tool starts a nested run.** Give it structured input, not a free-text string, and extract its output before the caller sees it, with a fallback when it's malformed.
- **Use an agent-to-agent protocol only across a boundary you don't own,** and keep your own subagents in-process, as production harnesses do (A2A ships in 1 of 11 studied). Over A2A, keep the server's `contextId` as the session key and reuse `messageId` on retries.
- **Backend actions stay with the main agent,** so refunds and account changes have one place to check them. OpenAI's Agents API enforces this (subagents can't call your function tools).
- **On OpenAI's Responses multi-agent, refuse state-changing calls from subagents in the handler,** because any agent in the tree can call any function tool in the request. Use the agent attribution the API returns, and confirm it reaches each function call before relying on it.
- **On OpenAI's Responses multi-agent, which accepts results one at a time, return each result when it's ready,** and send one that arrives after the response completed in a new request. Everywhere else, answer the batch in one message (tools.md).

## Briefing a subagent

- **Give a full brief:** the objective, the output format, the tools and sources it may use, and where to stop. A one-line task produced duplicated and off-target work in Anthropic's research system.
- **Pass references, not summaries.** When one agent's finding matters to another, write it to a shared store and pass the path. The orchestrator summarizes details away when they pass through it.
- **Fork or start fresh.** A fresh subagent gets only your brief and pays for its own prefix. A fork inherits the system prompt, tools, model, and history, so it starts from the parent's cache with nothing to re-explain. Fork when a fresh agent would need too much background; start fresh for a clean-context verifier. A fork copies the conversation, not the world: anything it changes outside the transcript is real for every branch.
- **Cap depth, concurrency, total count, and shared spend in code, counting the whole tree.** Platforms leave some of these open: OpenAI's Responses multi-agent runs 3 subagents at once by default, grandchildren included, with no limit on depth or total. At a limit, refuse the spawn with an error that tells the model not to retry, so it does the work itself.
- **Tell each subagent whether it may spawn agents of its own;** without a rule, recursion has no floor. Bound a clean-context grader's loop too (Anthropic's stops after 3 rounds by default).

## Failures between agents

- **Give each agent its own rate limit in code,** so one agent stuck retrying can't use up the quota the others share.
- **A subagent that ends early returns what it has, labelled partial with the reason** (step cap, rate limit, server error), so the orchestrator never mistakes it for a finished result. With no output, it returns an error, never an empty success. Resume a cut-off subagent from its own transcript instead of starting it over.

## Where the answer depends on the case

- **How readily to spawn subagents.** OpenAI's GPT-5.6 guide says spawning is steerable and to prompt for it where it helps. Codex ships both settings: one tool forbids spawning unless the user asks, while its orchestrator prefers several subagents. Anthropic warns most teams use multi-agent where one agent would do better. Decide from measured cost and quality on your own task, never by default.
