# Build or buy the harness

## The options

From most done for you to least:

1. **A vertical vendor** (a CX platform such as Intercom Fin or Plaude). It brings the loop, the inbox, channels, handoff to humans, and a place to write procedures.
2. **A model vendor's hosted harness** (Claude Managed Agents, OpenAI's Agents API). It hosts the loop, sessions, memory, and sandbox. You build the channel, the inbox, and the tools. Anthropic also offers a self-hosted sandbox, where the loop stays with Anthropic and the tools run inside your network.
3. **A provider SDK in your infrastructure** (Claude Agent SDK, OpenAI Agents SDK, Vercel AI SDK). The loop comes as a library, and hosting, state, retries, and integrations are yours.
4. **Your own loop on the raw API** (Messages API, Responses API). You write everything.

Visual workflow builders sit outside this list. OpenAI is shutting its own down on 2026-11-30 and moving those workflows to its SDK, because a workflow that has to keep running belongs in code.

## Choosing

```
Must the loop, memory, or data stay inside your perimeter (regulation, a contract)?
├── Yes → 3 or 4, or 2 with a self-hosted sandbox if only the tools must stay inside
└── No → Is the agent itself what your product sells?
    ├── Yes → 3: you'll need control over memory, files, and the loop
    └── No → Does a vendor already live where your conversations are (your help desk)?
        ├── Yes → shortlist 1 and 2, and run both on the same eval cases before choosing
        └── No → 2 or 3: see "Where the answer depends on the case" below
```

Run the same eval cases (agent-evals) against each candidate and let the results decide. A vendor demo shows its best conversations, not yours.

## What stays yours whatever you choose

- **The tools.** Every action is an endpoint in your systems, with its policy check inside it (SKILL.md rules 2 and 3). No vendor can write your business rules.
- **The procedures and the prompt.** A vendor gives you the place to write them, not the content.
- **The evals.** You need every conversation exported in full, with each tool call's input and output. A vendor's built-in evals can't replace yours, and OpenAI shutting down its hosted Evals platform (2026-11-30) shows why. You lose them when the vendor drops the feature.
- **Versions and rollback.** A staging copy of the agent, pinned versions, and a one-step rollback.

## Ask a vendor before signing

1. Can I export every conversation in full through an API, with tool inputs and outputs?
2. How do actions reach my backend, and does the verified customer identity travel in a field the model can't change?
3. Which model processes the data, where, for how long, and is it used for training? Get it in writing.
4. Can I pin the model and the agent's configuration, test changes on a staging copy, and roll back?
5. How does the agent hand a conversation to my team, and can it ask my team a question without handing over?
6. What do you charge for: a message, a conversation, or a resolved case? How do you define "resolved", and can I audit each charge?

## Where the answer depends on the case

- **Should most teams run a harness at all?** Anthropic (2026-04) says maintaining a harness is overhead that doesn't differentiate most products, so spend the effort on context and domain knowledge and let a hosted harness run the loop. Its hosting cookbook agrees for customer-facing chat and keeps the SDK for regulated environments and internal tools. OpenAI (2026-09) says every option trades something: frameworks underuse frontier models, provider SDKs hide the harness, and hosted harnesses limit where the agent runs and how it reaches sensitive data. Its advice is to embed a proven harness in software built around the job. Report both.
