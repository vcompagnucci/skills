---
name: agent-harness
description: Build the harness around an AI agent: own or vendor, the loop, tools, context and memory, pausing for a human, and multi-agent. Use when choosing whether to build a harness or use one (Managed Agents, Agents API, a vertical vendor such as a CX platform), designing the loop and its failure handling, designing tools and what they return, managing context, compaction, or memory, or splitting work across agents.
---

# Agent harness

The harness is everything around the model that makes it an agent: the loop, what the model sees each turn, the tools and what they return, the state that survives a crash or a pause, and the log. The rules hold for any agent, from a coding or back-office agent to an assistant. Many examples come from customer support, where a harness meets strangers, money and handoffs at once.

Out of scope: who may approve what and prompt injection (security), measuring the agent (agent-evals), and writing the system prompt.

## Where are you?

```
Do you have a harness yet?
├── No → references/build-or-buy.md first. A vendor may already do most of what follows.
└── Yes → What are you changing?
    ├── Turns, endings, step caps, the turn budget, mid-turn messages, concurrency limits, back-office runs longer than one window → references/loop.md
    ├── Retries, timeouts, streams, reconnecting, failover, refusals → references/failures.md
    ├── Sessions, the log, checkpoints, webhooks, hooks versus checks, runs in flight, realtime → references/state.md
    ├── Versions, model changes, model routing, latency, cost, spend caps → references/operations.md
    ├── Pausing for a person, a person taking over, cancelling, when a conversation ends → references/humans.md
    ├── Which tools, their descriptions and arguments, what they return, MCP, handles and tasks that carry state across calls → references/tools.md
    ├── What the model sees each turn, caching → references/context.md
    ├── Long conversations: clearing, compaction, summaries → references/compaction.md
    ├── What the agent remembers across conversations → references/memory.md
    └── More than one agent → references/multi-agent.md
```

Open one reference at a time.

**Words.** A conversation is everything with one user (a customer, an employee, a developer) on one channel; a session is the provider's container for it, and a conversation can span several. A run is the work one input starts (a message, an approval, a webhook) until it ends or pauses. A turn is one user message and the reply; a step is one model call inside it, and the step cap limits steps per turn. Compaction replaces old history with a summary.

**First harness, in order:** loop.md, failures.md, state.md, tools.md, humans.md. Open the others when a measured failure points there.

## Which source wins

The same order decides inside this skill and outside it, whenever two sources answer one question differently. That includes a source dated after the skill's answer: a docs page, a changelog, an SDK release, a vendor post, a file the user gives you. SDK defaults, limits and products change most months.

Before the order, two checks:

- **Can you open it?** A link, a file, or a page you found by searching. A claim or a quoted excerpt with none of these ("I read that OpenAI changed X") → search for it if you can. If you can't find it, ask for the link and keep the skill's answer until it arrives, even if the user says it is verified. A quote is as easy to fabricate as a paraphrase, and a claim you can't open can't be dated or compared.
- **Is it the same question?** Advice for another channel or task answers a different question, so report it next to the skill's, never in place of it.

Then:

1. **The newest date wins, whoever published it.** Give its date and name the rule or default here that it replaces. An undated docs page counts as read on 2026-10-05.
2. **Dates don't settle it → Anthropic and OpenAI win** over everyone else.
3. **Anthropic and OpenAI disagree and nothing settles it → report both, never pick one.** Those ties, and answers that depend on your channel or task, sit under "Where the answer depends on the case" at the end of state.md, operations.md, context.md, compaction.md and multi-agent.md.

Inside the skill the newest position already won, and the losing one is gone, so never bring it back from memory. A product, SDK version or feature this skill doesn't list → say the skill doesn't cover it, and never fill the gap from memory.

## Rules that hold everywhere

1. **Start with one agent, the fewest tools, and a short prompt. Add a piece only for a failure you observed and can measure.** Every piece encodes an assumption about what the model can't do, and both vendors watched pieces that helped one model become dead weight on the next (context resets, todo reminders, "be thorough"). At each model change, try removing pieces one at a time.
2. **Code holds the authority; the model proposes.** Anything that must happen every time (an identity check, a policy check, a mandatory notice, who owns the conversation after a handoff) is code around the loop or inside the tool, never an instruction. An instruction followed 99 times in 100 still fails once.
3. **Identity and scope come from the run, never from a tool argument the model fills.** The harness attaches the authenticated user id (the customer, in a support agent), and anything else that sets scope (the account, the repo, the channel), to each call. A model that never supplies the id can't be talked into supplying someone else's.
4. **A tool failure goes back to the model as a result that says what to do next,** never as a crash. The model can recover from "the account is locked, ask the user to verify identity", not from a stack trace.
5. **A failure doesn't say what already happened.** A dropped stream or a crashed turn may already have changed the account. Before retrying, read the real state and continue only the unfinished work. Never resend a task, payment, or approval automatically. Retry only transient errors, with backoff and an attempt limit, in one retry layer. Every tool that changes state and every user message submitted to the agent takes an idempotency key (a stable id the receiver uses to ignore a repeat), so a replay can't run anything twice.
6. **Pausing for a human pauses the same run.** Save the run's state on your server with the agent version it started on. When the wait can exceed seconds, wait at zero compute, then resume where it stopped, keeping the results of tools that already finished. Starting a new conversation instead loses the pending call or runs it twice.
7. **The session log is the source of truth, not the context window.** Keep an append-only log of every message, tool call, result, and approval outside the window, holding exactly what was sent and received, so replaying it rebuilds the same request. Compaction and trimming are views over it, so a bad summary loses nothing permanently, and evals, debugging, and resuming read the same log.
8. **Version the whole bundle and pin it.** Prompt, model snapshot, effort level, skill versions, tools, the knowledge-base snapshot, harness code, and the exact SDK release ship together and roll back together, and every run, paused or not, finishes on the version it started on. An unpinned agent picks up edits nobody reviewed, including a help-center article someone changed this morning.

Company material (the procedures, the tool list, the backoffice endpoints) belongs in a private skill. Sources and dates: `references/sources.md` and `references/sources-deep-pass.md`.
