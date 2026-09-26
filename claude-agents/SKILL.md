---
name: claude-agents
description: Building your own agent the Anthropic way (Messages API, Agent SDK, Managed Agents). Covers whether to build one, multi-agent patterns, harness and long runs, tools and MCP, context and memory, skills, prompt caching, cost, model and effort, evals, security and sandboxing, and use cases like customer support. Cites 120 sources: Anthropic's engineering blog, claude.dev, claude.com, docs guides, cookbooks, and research.
---

# Claude agents (Anthropic)

This skill holds what Anthropic has published that helps you build your own agent: 120 sources from six places. Posts on the Claude Code team's blog at [claude.dev](https://claude.dev/), in the agents category of the [claude.com blog](https://claude.com/blog-category/agents), and on the [Anthropic engineering blog](https://www.anthropic.com/engineering), plus the docs' use-case guides, the agent notebooks in [claude-cookbooks](https://github.com/anthropics/claude-cookbooks), and agent posts on [anthropic.com/research](https://www.anthropic.com/research), from 2024 to September 2026. Citations use short keys like (`cost`). Keys starting with `uc-` are docs guides and `cb-` are cookbooks, which are worked examples, not measurements. Each entry in `references/article-index.md` links its key to the source.

## The one-sentence thesis

> **Start with the simplest thing that works, give Claude general tools, context it loads when needed, and a way to check its own work, contain what it can break, and remove each piece of harness once the model outgrows it.**

The 14 ideas below follow from it.

## Core ideas

1. **Start simple, and check whether you need an agent at all.** One call with retrieval is often enough, and complexity gets added "only when it demonstrably improves outcomes": one agent before a workflow, a workflow before multiple agents. (`effective-agents`, `workflow-patterns`)
2. **Every harness piece encodes an assumption about what Claude can't do, and those expire.** Resets built for Sonnet 4.5's "context anxiety" became dead weight on Opus 4.5, and the team cut 80%+ of Claude Code's system prompt for Claude 5 with no eval loss. (`harness-patterns`, `managed-agents`, `ctx-eng`)
3. **Give Claude a computer and let it find its own context.** Bash, files, and code replaced separate domain agents, and Grep replaced RAG. (`agent-sdk`, `skills-for-agents`, `seeing`)
4. **Context is a finite attention budget.** Curate "the smallest set of high-signal tokens" every turn, keep the system prompt lean, and pick compaction, tool-result clearing, or memory by the problem you have. (`effective-context`, `ctx-eng`, `cb-ctx-tools`)
5. **Tools are the agent-computer interface.** Few tools grouped by intent, descriptions written like prompts, errors that say what to do next. On SWE-bench the team spent more time on tools than on the prompt. (`writing-tools`, `effective-agents`, `advanced-tool-use`)
6. **Caching is a prefix match.** Static first, dynamic last, updates as messages, and no tool or model changes mid-session. (`caching`, `platform-cost`)
7. **You pay per task, not per token.** A retry costs more than any saving, so start with the most intelligent model, dial effort, and move down only when your evals allow it. (`cost`, `models-explained`)
8. **Effort buys verification, not insight.** It fixes hidden edge cases (a sanitizer went from 1/5 to 5/5) but not a wrong reading of the task, so look for a check before raising it. (`effort`, `platform-cost`)
9. **Give Claude a check, and keep the checker separate from the author.** Agents praise their own mediocre work, and "the task verifier must be nearly perfect, otherwise Claude will solve the wrong problem." (`harness-design-apps`, `c-compiler`, `cb-outcome-grader`, `vibe-physics`)
10. **Build evals early and read the transcripts.** 20-50 tasks from real failures, graded on the outcome, not the path. The runtime is part of the test, and models can spot the eval itself. (`agent-evals`, `infra-noise`, `eval-awareness`)
11. **Multi-agent has to earn its cost.** It uses 3-10x the tokens and pays for context pollution, parallel work, or conflicting tools, split by context, not by type of work. In one conversation across several domains, a single agent with skills beat subagent designs on quality, cost, and speed. (`when-multi-agent`, `research-system`, `commerce-agents`)
12. **Skills teach how, MCP gives access.** Skills load by progressive disclosure, trigger on their description, and can improve themselves from feedback. The best agents use both. (`skills`, `skills-and-mcp`, `warp`)
13. **Contain the blast radius with deterministic boundaries.** Sandbox the filesystem and network, keep credentials out of reach, and put must-dos in the harness, because "prompts are suggestions" and people approve 93% of prompts. (`containment`, `auto-mode`, `outtake`, `trustworthy-agents`)
14. **Long runs need state outside the context window.** A durable session log, a progress file that records failed approaches, a test oracle, a commit per unit of work, and a loop that challenges "done", because models find excuses to stop early. (`long-running-harness`, `managed-agents`, `long-running-science`)

Each idea is developed, with numbers and every source, in the matching reference file below.

## Reference files

- **`references/architecture-and-multi-agent.md`.** Agents vs workflows, the workflow and coordination patterns, when multi-agent pays, how to split, dynamic workflows, agent teams, failure modes between agents.
- **`references/harness-design.md`.** Harness assumptions going stale, minimal scaffolding, long-running and multi-day runs, brain vs hands, the three build paths (Messages API, Agent SDK, Managed Agents), hosting, sessions, prompt versioning.
- **`references/tool-design.md`.** Writing tools for agents, tool search, code execution with MCP, MCP servers, the think tool, computer use.
- **`references/context-engineering.md`.** Attention budget, the Claude 5 deletions, prompt altitude, just-in-time retrieval, compaction vs clearing vs memory, instruction files.
- **`references/skills.md`.** Why skills, progressive disclosure, skills vs MCP, writing and testing, self-improving skills, versioning.
- **`references/prompt-caching.md`.** Prompt order, what breaks the cache, lifetimes and prices, compaction.
- **`references/cost-and-model-choice.md`.** Per-task cost, model classes, the advisor and planner-worker splits, eval-driven model search, the cost lever order, effort.
- **`references/evals-and-verification.md`.** In-run checks, separate graders, building evals, infrastructure noise, eval awareness, postmortems.
- **`references/safety-and-containment.md`.** Blast radius, sandboxes, credentials, approvals, auto mode, injection surfaces, agentic misalignment and sabotage research.
- **`references/agents-in-production.md`.** Where to start, deployment patterns (Slack, on-call), and the docs' use-case playbooks: customer support, ticket routing, moderation, legal, commerce.
- **`references/glossary.md`.** 170 coined terms, each with its source.
- **`references/article-index.md`.** All 120 sources with link, key, date, author, and one-line thesis, grouped by theme.

## How to answer

Walk this every time:

```
Does the question name a post, an author, or a coined term?
├── Yes → Grep article-index.md or glossary.md for the key, title, or term (never read them whole) → the theme file → answer, cite the key
└── No → Does a core idea above answer it?
    ├── Yes → answer from it; open at most one reference for the numbers
    └── No → Does a reference file cover it? (list above)
        ├── Yes → open it, answer, cite
        └── No → say "Anthropic's posts don't cover this" and stop
```

Then, before sending:

- **Does it clash with the user's own decisions, their project's CLAUDE.md or AGENTS.md, or their notes?** Theirs win. Show both positions. This skill reports what Anthropic says. It doesn't decide for them.
- **Did the advice change, or does it depend on the case?** Where Anthropic changed its advice, the skill keeps only the latest, so give that one with its date and don't bring older advice back from memory. Where posts answer the same question for different cases, the reference file lists them under "Where the answer depends on the case": give each post's case as its authors put it. Don't close with your own rule of thumb.
- **Every bullet or paragraph ends with its key(s).** Use the key printed on the reference bullet you took it from, not the name of the reference file. Give the full URL when the user wants to read the post. An uncited claim can't be checked and blurs into the model's own opinion.
- **Use their numbers instead of paraphrasing:** dollar figures, benchmark scores, token counts. Those are what the corpus adds over the model's defaults.
- **Say when a source is thin.** Several claude.com category posts are product announcements or landing pages, and the index says so. Don't present a launch post as research.
- **Never answer from outside the corpus in their voice.** Generic advice attributed to Anthropic is the one failure the user can't detect.

## Scope

Only these 120 sources, up to September 2026, chosen for building an agent. Not covered: using Claude Code day to day, output formats for people, enterprise adoption stories, the rest of the claude.com blog and the docs, research outside agents, model cards, and courses or talks. Prices, model names, and defaults go out of date fast. For current API facts, the `claude-api` skill and the live docs win over this one.
