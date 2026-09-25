---
name: claude-agents
description: Designing agent tools, writing CLAUDE.md or skills, prompt caching and Claude Code costs, choosing an effort level or model (Opus 5.5, Fable 5.1, Sonnet, Haiku), steering long runs, subagents and dynamic workflows (ultracode), and verifying agent output. Answers come from all 10 posts on claude.dev, the Claude Code team's blog, with citations. Use for those questions or for the ideas of claude.dev, Thariq Shihipar, or Addy Osmani.
---

# Claude agents (claude.dev)

This skill holds what Anthropic's Claude Code team and colleagues published at [claude.dev](https://claude.dev/), mostly Thariq Shihipar and Addy Osmani. It covers all 10 posts, from "Seeing like an agent" (2026-04-10) to "What a task costs on Opus 5.5" and "Spending your effort" (2026-09-25). Citations use short post keys like (`effort`). The table at the top of `references/article-index.md` maps each key to its URL.

## The one-sentence thesis

> **Delete what the last model needed: give Claude a finish line, context it can load when it needs it, and a way to check its own work, then measure what it does.**

The 14 ideas below follow from it.

## Core ideas

1. **See like an agent.** Shape tools to what the current model can do, and learn that by reading its outputs. A tool only works if the model likes calling it. AskUserQuestion took three attempts: a plan-tool parameter and a markdown format both failed before a dedicated tool worked. (`seeing`, `references/tool-design.md`)
2. **What helped the last model can hold back the next one.** TodoWrite plus a reminder every 5 turns started constraining stronger models, so a shared Task tool replaced it. The team cut 80%+ of Claude Code's system prompt for Claude 5 models with no measurable eval loss. Rules became judgment, examples became interface design, and "think carefully" lines went. (`seeing`, `ctx-eng`, `opus-5-5`)
3. **Let Claude find context instead of handing it over.** Grep replaced RAG. Skills, deferred tools, and subagents load context only when needed. A tree of files beats one big CLAUDE.md, and the bar to add a tool is high. (`seeing`, `ctx-eng`, `references/context-engineering.md`)
4. **Caching is a prefix match, so design around it.** Put static content first and dynamic content last. Send updates as `<system-reminder>` messages. Never add or remove tools, or switch models, mid-session. Compact with a cache-safe fork. The team alerts on hit rate the way it alerts on uptime. (`caching`, `references/prompt-caching.md`)
5. **You pay per task, not per token.** Every turn resends the conversation, so "the cheapest turn is the one you don't need". Any way of spending fewer tokens can also cost you a finished task, and a retry costs more than the savings. (`cost`, `references/cost-and-model-choice.md`)
6. **Give Claude a way to check its work.** Verification skills have the most measurable effect on output quality. A test through the right layer catches at medium effort what would otherwise need high, so look for a check before raising effort. (`skills`, `cost`, `references/verification.md`)
7. **Effort buys verification, not insight.** Higher effort wins on tasks with hidden edge cases: an HTML sanitizer went from 1/5 to 5/5 once Claude fuzzed it and read the parser's source. It doesn't fix a wrong approach. "Picked the wrong reading" rose from 25 to 47. (`effort`, `references/effort.md`)
8. **Raise effort before changing models, and switch models at a break.** Opus 5.5 is the daily driver. Haiku or Sonnet handle lookups. Fable 5.1 comes in when xhigh fails twice on the same problem. (`cost`)
9. **Hand over the whole task with a finish line, then name the stops.** Write "Done means..." and add a CLAUDE.md rule on when to keep going and when to stop before anything destructive. When the run ends, read what it needs from you first. (`opus-5-5`, `references/long-runs.md`)
10. **Separate agents beat one long context when they earn their cost.** Isolated subagents counter agentic laziness, self-preferential bias, and goal drift, and Claude can now write the orchestration script per task. But "most traditional coding tasks do not need a panel of 5 reviewers." (`workflows`, `references/multi-agent-workflows.md`)
11. **With Claude, measuring something makes it tractable.** claude.ai got about 3× faster in two weeks. The team kept finding things to measure, proved each proxy tracked wall-clock time, and ratcheted every win in CI. (`faster`, `references/hill-climbing.md`)
12. **Humans own ambition, taste, and direction.** Claude defaults to cautious scope ("please be braver"). People rule on user-visible tradeoffs and cut complexity that isn't worth it. (`faster`)
13. **Write output people will read: HTML, not Markdown.** Nobody reads a 100+ line Markdown plan. HTML with diagrams, tabs, and export buttons keeps you in the loop. Thariq has "stopped using Markdown altogether for almost everything", others on the team are moving the same way, and the July post treats HTML artifacts as the successor to markdown specs, including as input Claude reads. (`html`, `references/html-outputs.md`)
14. **Skills are folders that push Claude off its defaults.** Each fits one category and has a gotchas section, scripts, and files it loads on demand. Its description is written for the model deciding whether to trigger it. (`skills`, `references/skills.md`)

## The method, in order

1. **Context.** Keep CLAUDE.md to purpose, gotchas, and stop rules. Put procedures in skills. Audit old prompts with `/doctor` or `/claude-api prompt-audit`. (`ctx-eng`, `cost`)
2. **Spec.** Claude interviews you, then you write the finish line. (`effort`, `opus-5-5`)
3. **Session.** Pick model, effort, MCPs, and fast mode up front, then leave them alone. (`cost`)
4. **Check.** Add a test, build, or verification skill before paying for more effort. (`skills`, `cost`)
5. **Run and scale.** Send one message, add follow-ups mid-run, keep a checklist file. Use subagents or workflows only for long, parallel, or adversarial work. (`opus-5-5`, `workflows`)
6. **Verify and protect.** Read what it needs from you first, use independent verifiers, lock wins with ratchets and flags, and check `/usage` for your own numbers. (`opus-5-5`, `workflows`, `faster`, `cost`)

## Reference files

- **`references/tool-design.md`.** Shaping tools to the model, AskUserQuestion's three attempts, TodoWrite to Task, Grep over RAG, deferred tools, the ~20-tool bar.
- **`references/context-engineering.md`.** The 80% cut, old rules versus new, what goes in the system prompt, CLAUDE.md, skills, and references.
- **`references/skills.md`.** Nine categories, gotchas, loading files on demand, config, memory, scripts, on-demand hooks, distribution, measurement.
- **`references/prompt-caching.md`.** Prompt order, what breaks the cache, lifetimes and prices, cache-safe compaction.
- **`references/cost-and-model-choice.md`.** Per-task cost math, Opus 5.5 pricing, the three-model day, switching models (the position changed between April and September), `/usage`.
- **`references/effort.md`.** What effort is, Terminal-Bench 3.0 evidence, gains per domain, two rules of thumb, the "one layer" sign.
- **`references/long-runs.md`.** Asking, steering, and checking Opus 5.5 runs. Flagged messages.
- **`references/multi-agent-workflows.md`.** Three failure modes, dynamic workflows, six patterns, use cases, when not to.
- **`references/verification.md`.** Checks, what thorough verification looks like, separate checkers, ratchets, honest reporting.
- **`references/html-outputs.md`.** Why HTML over Markdown, use cases, throwaway editors, rich references as inputs.
- **`references/hill-climbing.md`.** The claude.ai performance sprint: benchmarks, ratchets, the thread loop, what measurement found.
- **`references/glossary.md`.** 36 coined terms, each with its source.
- **`references/article-index.md`.** The key-to-URL table, then all 10 posts with a one-line thesis, grouped by theme.

## How to answer

Walk this every time:

```
Does the question name a post, an author, or a coined term?
├── Yes → article-index.md (key → URL) or glossary.md → the theme file → answer, cite the key
└── No → Does a core idea above answer it?
    ├── Yes → answer from it; open at most one reference for the numbers
    └── No → Does a reference file cover it? (list above)
        ├── Yes → open it, answer, cite
        └── No → say "claude.dev doesn't cover this" and stop
```

Then, before sending:

- **Does it clash with the user's own decisions, their project's CLAUDE.md or AGENTS.md, or their notes?** Theirs win. Show both positions. This skill reports what claude.dev says. It doesn't decide for them.
- **Is the position contested (HTML over Markdown, switching models mid-session, low vs medium effort for implementation)?** State it as the authors' position, unsoftened, with the date when it changed. In testing, the model twice added a hedge the corpus doesn't contain ("Markdown's fine for specs only Claude reads").
- **Every bullet or paragraph ends with its key(s).** Use the key printed on the reference bullet you took it from, not the name of the reference file (`prompt-caching.md` also holds `cost` claims). Give the full URL when the user wants to read the post. An uncited claim can't be checked and blurs into the model's own opinion.
- **Use their numbers instead of paraphrasing:** dollar figures, benchmark tasks, pass rates. Those are what the corpus adds over the model's defaults.
- **Never answer from outside the corpus in their voice.** Generic advice attributed to them is the one failure the user can't detect.

## Scope

Only the 10 claude.dev posts, April to September 2026. Not covered: API reference beyond caching and compaction, MCP server authoring, evals beyond comparisons run as workflows, safety policy beyond how Opus 5.5 handles flagged messages, and products other than Claude. Prices, model names, and defaults go out of date fast. For current API facts, the `claude-api` skill and the live docs win over this one.
