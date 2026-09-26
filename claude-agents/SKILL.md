---
name: claude-agents
description: Building agents the way Anthropic does. Covers whether to build an agent at all, architecture and multi-agent patterns, harness design, tool and MCP design, context engineering and memory, CLAUDE.md and skills, prompt caching, cost, model and effort choice, steering long runs, evals and verification, sandboxing and containment, and production use cases like customer support, ticket routing, and moderation. Answers cite 139 Anthropic sources: every post on claude.dev, in claude.com's agents category, and on anthropic.com/engineering, plus the docs' use-case guides, the agent notebooks in claude-cookbooks, and the agent research on anthropic.com/research (Project Vend, agentic misalignment). Use for those questions or for the ideas of Anthropic's engineering blog, the Claude Code team, Thariq Shihipar, or Addy Osmani.
---

# Claude agents (Anthropic)

This skill holds what Anthropic has published about building agents: 139 sources from six places. Every post on the Claude Code team's blog at [claude.dev](https://claude.dev/), in the agents category of the [claude.com blog](https://claude.com/blog-category/agents), and on the [Anthropic engineering blog](https://www.anthropic.com/engineering), plus the docs' use-case guides, the agent notebooks in [claude-cookbooks](https://github.com/anthropics/claude-cookbooks), and the agent posts on [anthropic.com/research](https://www.anthropic.com/research). They run from 2024 to "What a task costs on Opus 5.5" (2026-09-25). Citations use short keys like (`effort`). Keys starting with `uc-` are docs guides and `cb-` are cookbooks, which are worked examples, not measurements. Each entry in `references/article-index.md` links its key to the source.

## The one-sentence thesis

> **Start with the simplest thing that works, give Claude general tools, context it loads when needed, and a way to check its own work, contain what it can break, and remove each piece of harness once the model outgrows it.**

The 14 ideas below follow from it.

## Core ideas

1. **Start simple, and check whether you need an agent at all.** One call with retrieval is often enough, and complexity gets added "only when it demonstrably improves outcomes": one agent before a workflow, a workflow before multiple agents. (`effective-agents`, `workflow-patterns`)
2. **Every harness piece encodes an assumption about what Claude can't do, and those expire.** Resets built for Sonnet 4.5's "context anxiety" became dead weight on Opus 4.5, and the team cut 80%+ of Claude Code's system prompt for Claude 5 with no eval loss. (`harness-patterns`, `managed-agents`, `ctx-eng`)
3. **Give Claude a computer and let it find its own context.** Bash, files, and code replaced separate domain agents, and Grep replaced RAG. (`agent-sdk`, `skills-for-agents`, `seeing`)
4. **Context is a finite attention budget.** Curate "the smallest set of high-signal tokens" every turn, keep CLAUDE.md short, and use compaction, notes, or sub-agents for long runs. (`effective-context`, `cc-best-practices`)
5. **Tools are the agent-computer interface.** Few tools grouped by intent, descriptions written like prompts, errors that say what to do next. On SWE-bench the team spent more time on tools than on the prompt. (`writing-tools`, `effective-agents`, `advanced-tool-use`)
6. **Caching is a prefix match.** Static first, dynamic last, updates as messages, and no tool or model changes mid-session. (`caching`, `platform-cost`)
7. **You pay per task, not per token.** A retry costs more than any saving, so start with the most intelligent model, dial effort, and move down only when your evals allow it. (`cost`, `models-explained`)
8. **Effort buys verification, not insight.** It fixes hidden edge cases (a sanitizer went from 1/5 to 5/5) but not a wrong reading of the task, so look for a check before raising it. (`effort`, `platform-cost`)
9. **Give Claude a check, and keep the checker separate from the author.** Agents praise their own mediocre work, and "the task verifier must be nearly perfect, otherwise Claude will solve the wrong problem." (`harness-design-apps`, `c-compiler`, `cc-best-practices`, `cb-outcome-grader`, `vibe-physics`)
10. **Build evals early and read the transcripts.** 20-50 tasks from real failures, graded on the outcome, not the path. The runtime is part of the test, and models can spot the eval itself. (`agent-evals`, `infra-noise`, `eval-awareness`)
11. **Multi-agent has to earn its cost.** It uses 3-10x the tokens and pays for context pollution, parallel work, or conflicting tools, split by context, not by type of work. In one conversation across several domains, a single agent with skills beat subagent designs on quality, cost, and speed. (`when-multi-agent`, `research-system`, `commerce-agents`)
12. **Skills teach how, MCP gives access.** Skills load by progressive disclosure, trigger on their description, and can improve themselves from feedback. The best agents use both. (`skills`, `skills-and-mcp`, `warp`)
13. **Contain the blast radius with deterministic boundaries.** Sandbox the filesystem and network, keep credentials out of reach, and put must-dos in the harness, because "prompts are suggestions" and people approve 93% of prompts. (`containment`, `auto-mode`, `outtake`, `trustworthy-agents`)
14. **Hand over the whole task, then steer as the human.** Write the finish line, name the stops, and own ambition and taste. Thariq has "stopped using Markdown altogether for almost everything" in favor of HTML, including as input Claude reads. (`opus-5-5`, `faster`, `html`)

Each idea is developed, with numbers and every source, in the matching reference file below.

## Reference files

- **`references/architecture-and-multi-agent.md`.** Agents vs workflows, the workflow and coordination patterns, when multi-agent pays, how to split, dynamic workflows, agent teams, failure modes between agents.
- **`references/harness-design.md`.** Harness assumptions going stale, minimal scaffolding, long-running harnesses, brain vs hands, Managed Agents, the Agent SDK and hosting.
- **`references/tool-design.md`.** Writing tools for agents, tool search, code execution with MCP, MCP servers, the think tool, computer use.
- **`references/context-engineering.md`.** Attention budget, the Claude 5 deletions, prompt altitude, just-in-time retrieval, long horizons, CLAUDE.md, compaction vs clearing vs memory.
- **`references/skills.md`.** Why skills, progressive disclosure, skills vs MCP/Projects/subagents, writing and testing, self-improving skills, governance.
- **`references/prompt-caching.md`.** Prompt order, what breaks the cache, lifetimes and prices, compaction.
- **`references/cost-and-model-choice.md`.** Per-task cost, model classes, the advisor strategy, eval-driven model search, switching models.
- **`references/effort.md`.** What effort buys, where it's wrong both ways, rules of thumb, the default-effort reversal.
- **`references/long-runs.md`.** Asking, steering, session hygiene, checking, HTML output, flagged messages.
- **`references/evals-and-verification.md`.** In-run checks, separate graders, building evals, infrastructure noise, eval awareness, postmortems.
- **`references/safety-and-containment.md`.** Blast radius, sandboxes, credentials, auto mode, injection surfaces, security programs, agentic misalignment and sabotage research.
- **`references/agents-in-production.md`.** Where to start, the docs' use-case playbooks (customer support, ticket routing, moderation, legal, commerce), Project Vend, customer lessons, how Anthropic runs its own agents.
- **`references/glossary.md`.** 189 coined terms, each with its source.
- **`references/article-index.md`.** All 139 sources with link, key, date, author, and one-line thesis, grouped by theme.

## How to answer

Walk this every time:

```
Does the question name a post, an author, or a coined term?
├── Yes → article-index.md (key → URL) or glossary.md → the theme file → answer, cite the key
└── No → Does a core idea above answer it?
    ├── Yes → answer from it; open at most one reference for the numbers
    └── No → Does a reference file cover it? (list above)
        ├── Yes → open it, answer, cite
        └── No → say "Anthropic's posts don't cover this" and stop
```

Then, before sending:

- **Does it clash with the user's own decisions, their project's CLAUDE.md or AGENTS.md, or their notes?** Theirs win. Show both positions. This skill reports what Anthropic says. It doesn't decide for them.
- **Is the position contested or did it change?** State it as the authors' position, unsoftened, with the dates. The known ones: HTML over Markdown, switching models mid-session (April: don't, September: at a break), effort first vs a stronger model first, examples in tool definitions (2025) vs interface design (Claude 5), a single agent with skills vs subagents, multi-agent cost (3-10x vs a cheaper planner-worker split), and owning your harness vs Managed Agents. In testing, the model twice added a hedge the corpus doesn't contain ("Markdown's fine for specs only Claude reads").
- **Every bullet or paragraph ends with its key(s).** Use the key printed on the reference bullet you took it from, not the name of the reference file. Give the full URL when the user wants to read the post. An uncited claim can't be checked and blurs into the model's own opinion.
- **Use their numbers instead of paraphrasing:** dollar figures, benchmark scores, token counts. Those are what the corpus adds over the model's defaults.
- **Say when a source is thin.** Several claude.com category posts are product announcements or landing pages, and the index says so. Don't present a launch post as research.
- **Never answer from outside the corpus in their voice.** Generic advice attributed to Anthropic is the one failure the user can't detect.

## Scope

Only these 139 sources, up to September 2026. Not covered: the rest of the claude.com blog, the rest of the documentation, the other research (interpretability, economics, policy), model cards, and courses or talks. Prices, model names, and defaults go out of date fast. For current API facts, the `claude-api` skill and the live docs win over this one.
