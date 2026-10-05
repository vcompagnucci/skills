# Build or buy the harness

## The options

From most done for you to least:

1. **A vertical vendor** (a CX platform such as Intercom Fin or Plaude). It brings the loop, the inbox, channels, handoff to humans, and a place to write procedures.
2. **A model vendor's hosted harness** (Claude Managed Agents, OpenAI's Agents API). It hosts the loop, sessions, memory, and sandbox. You build the channel, the inbox, and the tools. Both vendors also offer a self-hosted sandbox, where the loop stays with the vendor and the tools run inside your network. That keeps tools and files inside, never the conversation: OpenAI stores Agents API sessions itself, in the US only, and offers no zero data retention even when the sandbox is yours.
3. **A provider SDK in your infrastructure** (Claude Agent SDK, OpenAI Agents SDK, Vercel AI SDK). The loop comes as a library, and hosting, state, retries, and integrations are yours. OpenAI's docs place the SDK beside its hosted Agents API: the SDK when deployment, storage, and approvals stay in your application, the API for long-running tasks OpenAI manages.
   - **3b. The SDK's loop inside a durable workflow engine** (Temporal, Restate). The engine records each model call and tool call, and a run starts from a message, an approval, a timer, or a webhook. Cursor moved its agent loop onto Temporal and went from 90% to over 99% reliability.
4. **Your own loop on the raw API** (Messages API, Responses API). You write everything.

Visual workflow builders sit outside this list. OpenAI is shutting its own down on 2026-11-30 and moving those workflows to its SDK, because a workflow that has to keep running belongs in code.

## Choosing

```
Must the loop, memory, or data stay inside your perimeter (regulation, a contract)?
├── Yes → 3 or 4, or 2 with a self-hosted sandbox if only the tools and files must stay inside (the conversation still leaves)
└── No → Is the agent itself what your product sells?
    ├── Yes → 3: you'll need control over memory, files, and the loop
    └── No → Does a vendor already live where your conversations are (your help desk)?
        ├── Yes → shortlist 1 and 2
        └── No → 2
```

Run the same eval cases (agent-evals) against each candidate and let the results decide. A vendor demo shows its best conversations, not yours.

## What stays yours whatever you choose

- **The tools.** Every action is an endpoint in your systems, with its policy check inside it (SKILL.md rules 2 and 3). No vendor can write your business rules.
- **The procedures and the prompt.** A vendor gives you the place to write them, not the content.
- **The evals.** You need every conversation exported in full, with each tool call's input and output, so your evals don't depend on a vendor feature that can disappear.
- **Versions and rollback.** A staging copy of the agent, pinned versions, and a one-step rollback.
- **Cost accounting.** A hosted harness's usage numbers are not a bill: OpenAI's Agents API reports them best effort, they can be null rather than zero or change later, an agent's span (its trace record) leaves out its subagents, and there's no cache-write count. Keep your own per-call accounting, or reserve against the worst case before each call (operations.md).

## Ask a vendor before signing

1. Can I export every conversation in full through an API, with tool inputs and outputs?
2. How do actions reach my backend, and does the verified customer identity travel in a field the model can't change?
3. Which model processes the data, where, for how long, and is it used for training? Get it in writing.
4. Can I pin the model and the agent's configuration, test changes on a staging copy, send a small share of new conversations to a new version, and roll back? Some hosts serve one version per endpoint with no traffic split (Microsoft Foundry's hosted agents).
5. How does the agent hand a conversation to my team, and can it ask my team a question without handing over?
6. Can I export the agent's definition (procedures, prompts, tool definitions) as files I can diff, and ship changes on my own schedule?
7. What do you charge for: a message, a conversation, or a resolved case? How do you define "resolved", and can I audit each charge?
8. How long does an idle or paused session survive before it's deleted? A paused run must outlive your longest wait for a person (Gemini Managed Agents delete an environment after 7 idle days; Foundry deletes sessions after 30).

## How the vendors' positions converged

OpenAI (2026-04-15) warned that hosted harnesses limit where the agent runs and how it reaches sensitive data; Anthropic (2026-06-10) called maintaining a harness overhead that doesn't differentiate most products. OpenAI's hosted Agents API (2026-09-10) joined Anthropic, keeping its SDK for agents whose deployment, storage, and approvals stay in your application. Hosted is the default, unless data or the loop must stay inside your perimeter.
