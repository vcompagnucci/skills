---
name: claude-agents
description: Building agents the way Anthropic does. Covers whether to build an agent at all, agent architecture and multi-agent patterns, harness design, tool and MCP design, context engineering, CLAUDE.md and skills, prompt caching, cost, model and effort choice, steering long runs, evals and verification, sandboxing and containment, and deploying agents in production. Answers come from all 73 posts Anthropic published on this, with citations: 10 on claude.dev, 38 in claude.com's agents category, and 25 on anthropic.com/engineering. Use for those questions or for the ideas of Anthropic's engineering blog, the Claude Code team, Thariq Shihipar, or Addy Osmani.
---

# Claude agents (Anthropic)

This skill holds what Anthropic has published about building agents: the Claude Code team's blog at [claude.dev](https://claude.dev/), the agents category of the [claude.com blog](https://claude.com/blog-category/agents), and the [Anthropic engineering blog](https://www.anthropic.com/engineering). It covers all 73 posts, from "Contextual Retrieval" (2024-09-19) and "Building Effective AI Agents" (2024-12-19) to "What a task costs on Opus 5.5" (2026-09-25). Citations use short post keys like (`effort`). Each entry in `references/article-index.md` links its key to the post.

## The one-sentence thesis

> **Start with the simplest thing that works, give Claude general tools, context it loads when needed, and a way to check its own work, contain what it can break, and remove each piece of harness once the model outgrows it.**

The 14 ideas below follow from it.

## Core ideas

1. **Start simple, and maybe don't build an agent.** A single call with retrieval is often enough, workflows fix the flow while agents direct their own, and the most successful teams used simple, composable patterns. Try the task as one agent before adding a workflow, and add complexity "only when it demonstrably improves outcomes". (`effective-agents`, `workflow-patterns`, `references/architecture-and-multi-agent.md`)
2. **Every harness piece encodes an assumption about what Claude can't do, and those expire.** Context resets built for Sonnet 4.5's "context anxiety" became dead weight on Opus 4.5. The team cut 80%+ of Claude Code's system prompt for Claude 5 with no eval loss. Remove one component at a time and measure. (`harness-patterns`, `managed-agents`, `harness-design-apps`, `ctx-eng`, `references/harness-design.md`)
3. **Give Claude a computer and let it find its own context.** Bash, a filesystem, and code are enough for most agents: one general agent that works through code replaced separate domain agents. Grep replaced RAG, and agents load data just in time through references. (`agent-sdk`, `skills-for-agents`, `seeing`, `effective-context`)
4. **Context is a finite attention budget.** Recall falls as tokens grow, so curate "the smallest set of high-signal tokens" every turn. Keep CLAUDE.md short (bloat makes Claude ignore real rules), write prompts at the right altitude, and use compaction, notes, or sub-agents for long runs. (`effective-context`, `cc-best-practices`, `references/context-engineering.md`)
5. **Tools are the agent-computer interface, so design them for agents.** Few consolidated tools grouped by intent, descriptions written like prompts, high-signal responses, and errors that say what to do next. On SWE-bench the team spent more time on tools than on the prompt. Load definitions on demand and let code do multi-step orchestration. (`writing-tools`, `effective-agents`, `advanced-tool-use`, `mcp-code-exec`, `references/tool-design.md`)
6. **Caching is a prefix match, so design around it.** Static first, dynamic last. Send updates as messages. Never add or remove tools, or switch models, mid-session. Compact with a cache-safe fork. Claude Code alerts on its hit rate like uptime. (`caching`, `platform-cost`, `references/prompt-caching.md`)
7. **You pay per task, not per token.** Every turn resends the conversation, and a retry costs more than any saving. Start with the most intelligent model and dial effort, move down only when your own evals say a cheaper model clears the bar, and measure with `/usage`. (`cost`, `models-explained`, `references/cost-and-model-choice.md`)
8. **Effort buys verification, not insight.** Higher effort wins on hidden edge cases (an HTML sanitizer went from 1/5 to 5/5) but doesn't fix a wrong reading of the task, and too much just over-thinks. Look for a check before raising effort. (`effort`, `platform-cost`, `references/effort.md`)
9. **Give Claude a check, and keep the checker separate from the author.** Without a check you become the verification loop. Agents praise their own mediocre work, so tune a separate, skeptical grader with explicit criteria. "The task verifier must be nearly perfect, otherwise Claude will solve the wrong problem." (`cc-best-practices`, `harness-design-apps`, `c-compiler`, `references/evals-and-verification.md`)
10. **Build evals early and read the transcripts.** Start with 20-50 tasks from real failures, grade the outcome rather than the path, calibrate LLM judges with humans, and don't trust a score until someone reads transcripts. The runtime is part of the test, and models can spot the eval itself. With Claude, measuring something makes it tractable. (`agent-evals`, `infra-noise`, `eval-awareness`, `faster`)
11. **Multi-agent has to earn its cost.** It uses 3-10x the tokens and works mainly because it spends more of them. It pays for context pollution, parallel work, and conflicting tools. Split by context, not by type of work, and give each subagent a full brief. When the work is one conversation, like a customer-facing agent across several domains, a single agent with skills beat subagent designs on quality, cost, and speed. (`when-multi-agent`, `research-system`, `coordination-patterns`, `workflows`, `commerce-agents`)
12. **Skills teach how, MCP gives access.** Skills are folders loaded by progressive disclosure, triggered by their description, carrying gotchas and scripts. They can improve themselves from feedback captured where people work. MCP connects, and the best agents use both. (`skills`, `agent-skills`, `skills-and-mcp`, `warp`, `references/skills.md`)
13. **Contain the blast radius with deterministic boundaries.** Failure gets less likely while what an agent could break keeps growing. Sandboxes need filesystem and network isolation, credentials stay out of reach, and must-dos go in the harness because "prompts are suggestions". Approvals decay into rubber-stamping (93% accepted). (`containment`, `sandboxing`, `auto-mode`, `outtake`, `references/safety-and-containment.md`)
14. **Hand over the whole task, then steer as the human.** Write the finish line, name the stops in CLAUDE.md, and read what it needs from you first. People own ambition ("please be braver"), taste, and direction, and should get output they'll read: Thariq has "stopped using Markdown altogether for almost everything" in favor of HTML, including as input Claude reads. (`opus-5-5`, `faster`, `html`, `references/long-runs.md`)

## The method, in order

1. **Decide the shape.** One agent call first, then a workflow, then an agent, then multiple agents, each only if measured. (`workflow-patterns`, `when-multi-agent`)
2. **Build on general tools.** Bash, files, code, a few intent-level tools, MCP for access, skills for procedure. (`agent-sdk`, `writing-tools`, `skills-and-mcp`)
3. **Curate context.** Short CLAUDE.md with gotchas and stop rules, cache-friendly order, just-in-time loading. (`effective-context`, `ctx-eng`, `caching`)
4. **Contain before you trust.** Sandbox, credentials out of reach, must-dos in the harness. (`containment`, `outtake`)
5. **Give it a check and an eval set.** Tests, a separate grader, 20-50 real failures. (`cc-best-practices`, `agent-evals`)
6. **Run and steer.** Finish line, the right model and effort, subagents only where they earn it. (`opus-5-5`, `models-explained`, `effort`)
7. **Read, measure, prune.** Transcripts, `/usage`, ratchets, and remove what the model no longer needs. (`agent-evals`, `cost`, `faster`, `harness-patterns`)

## Reference files

- **`references/architecture-and-multi-agent.md`.** Agents vs workflows, the workflow and coordination patterns, when multi-agent pays, how to split, dynamic workflows, agent teams.
- **`references/harness-design.md`.** Harness assumptions going stale, minimal scaffolding, long-running harnesses, brain vs hands, Managed Agents.
- **`references/tool-design.md`.** Writing tools for agents, tool search, code execution with MCP, MCP servers, the think tool, computer use.
- **`references/context-engineering.md`.** Attention budget, the Claude 5 deletions, prompt altitude, just-in-time retrieval, long horizons, CLAUDE.md.
- **`references/skills.md`.** Why skills, progressive disclosure, skills vs MCP/Projects/subagents, writing and testing, self-improving skills, governance.
- **`references/prompt-caching.md`.** Prompt order, what breaks the cache, lifetimes and prices, compaction.
- **`references/cost-and-model-choice.md`.** Per-task cost, model classes, the advisor strategy, eval-driven model search, switching models.
- **`references/effort.md`.** What effort buys, where it's wrong both ways, rules of thumb, the default-effort reversal.
- **`references/long-runs.md`.** Asking, steering, session hygiene, checking, HTML output, flagged messages.
- **`references/evals-and-verification.md`.** In-run checks, separate graders, building evals, infrastructure noise, eval awareness, postmortems.
- **`references/safety-and-containment.md`.** Blast radius, sandboxes, credentials, auto mode, injection surfaces, security programs.
- **`references/agents-in-production.md`.** Where to start, agents inside the workflow, customer lessons, how Anthropic runs its own agents.
- **`references/glossary.md`.** 163 coined terms, each with its source.
- **`references/article-index.md`.** All 73 posts with link, key, date, author, and one-line thesis, grouped by theme.

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
- **Is the position contested or did it change?** State it as the authors' position, unsoftened, with the dates. The known ones: HTML over Markdown, switching models mid-session (April: don't, September: at a break), effort first vs a stronger model first, examples in tool definitions (2025) vs interface design (Claude 5), a single agent with skills vs subagents, and owning your harness vs Managed Agents. In testing, the model twice added a hedge the corpus doesn't contain ("Markdown's fine for specs only Claude reads").
- **Every bullet or paragraph ends with its key(s).** Use the key printed on the reference bullet you took it from, not the name of the reference file. Give the full URL when the user wants to read the post. An uncited claim can't be checked and blurs into the model's own opinion.
- **Use their numbers instead of paraphrasing:** dollar figures, benchmark scores, token counts. Those are what the corpus adds over the model's defaults.
- **Say when a source is thin.** Several claude.com category posts are product announcements or landing pages, and the index says so. Don't present a launch post as research.
- **Never answer from outside the corpus in their voice.** Generic advice attributed to Anthropic is the one failure the user can't detect.

## Scope

Only these 73 posts, September 2024 to September 2026. Not covered: the rest of the claude.com blog, the documentation, research papers, model cards, and policy. Prices, model names, and defaults go out of date fast. For current API facts, the `claude-api` skill and the live docs win over this one.
