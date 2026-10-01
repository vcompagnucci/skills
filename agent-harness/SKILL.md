---
name: agent-harness
description: Build the harness around an AI agent: own or vendor, the loop, tools, context and memory, pausing for a human, and multi-agent. Use when choosing whether to build a harness or use one (Managed Agents, Agents API, a CX vendor), designing the loop and its failure handling, designing tools and what they return, managing context, compaction, or memory, or splitting work across agents.
---

# Agent harness

The harness is everything around the model that makes it an agent: the loop, what the model sees each turn, the tools and what they return, the state that survives a crash or a pause, and the log. Where sources disagreed, the most recent position won. Where Anthropic and OpenAI disagree with no date to settle it, both positions sit under "Where the answer depends on the case" in the reference. Report both, and never pick one from memory.

Out of scope: who may approve what and prompt injection (security), measuring the agent (agent-evals), and writing the system prompt.

## Where are you?

```
Do you have a harness yet?
├── No → references/build-or-buy.md first. A vendor may already do most of what follows.
└── Yes → What are you changing?
    ├── Turns, stopping, retries, failures, pausing for a human, a person taking over, versions → references/loop.md
    ├── Which tools, their descriptions and arguments, what they return → references/tools.md
    ├── What the model sees, compaction, memory → references/context-memory.md
    └── More than one agent → references/multi-agent.md
```

Open one reference at a time.

## Rules that hold everywhere

1. **Start with one agent, the fewest tools, and a short prompt. Add a piece only for a failure you observed and can measure.** Every piece encodes an assumption about what the model can't do, and both vendors watched pieces that helped one model become dead weight on the next (context resets, todo reminders, "be thorough"). At each model change, try removing pieces one at a time.
2. **Code holds the authority; the model proposes.** Anything that must happen every time (an identity check, a policy check, a mandatory notice, who owns the conversation after a handoff) is code around the loop or inside the tool, never an instruction. An instruction followed 99 times in 100 still fails once.
3. **Identity and scope come from the run, never from a tool argument the model fills.** The harness attaches the authenticated customer id, and anything else that sets scope (the account, the channel), to each call. A model that never supplies the id can't be talked into supplying someone else's.
4. **A tool failure goes back to the model as a result that says what to do next,** never as a crash. The model can recover from "the account is locked, ask the customer to verify identity", not from a stack trace.
5. **A failure doesn't say what already happened.** A dropped stream or a crashed turn may already have changed the account. Before retrying, read the real state and continue only the unfinished work. Never resend a task, payment, or approval automatically. Retry only transient errors, with backoff and an attempt limit. Every tool that changes state takes a dedup key, so a replay can't run it twice.
6. **Pausing for a human pauses the same run.** Save the run's state on your server with the agent version it started on, wait at zero compute, and resume where it stopped, keeping the results of tools that already finished. Starting a new conversation instead loses the pending call or runs it twice.
7. **The session log is the source of truth, not the context window.** Keep an append-only log of every message, tool call, result, and approval outside the window. Compaction and trimming are views over it, so a bad summary loses nothing permanently, and evals, debugging, and resuming read the same log.
8. **Version the whole bundle and pin it.** Prompt, model snapshot, effort level, skill versions, tools, the knowledge-base snapshot, and harness code ship together and roll back together, and a paused run resumes on the version it started on. An unpinned agent picks up edits nobody reviewed, including a help-center article someone changed this morning.

Company material (the procedures, the tool list, the backoffice endpoints) belongs in a private skill. Sources and dates: `references/sources.md`.
