---
name: claude-agents
description: Designing agent tools, writing CLAUDE.md or skills, prompt caching and Claude Code costs, choosing an effort level or model (Opus 5.5, Fable 5.1, Sonnet, Haiku), steering long runs, subagents and dynamic workflows (ultracode), and verifying agent output — answered from all 10 posts on claude.dev, the Claude Code team's blog, with citations. Use for those questions or for the ideas of claude.dev / Thariq Shihipar / Addy Osmani.
---

# Claude agents (claude.dev)

This skill encodes the body of work published at [claude.dev](https://claude.dev/) by **Anthropic's Claude Code team and colleagues** (mostly Thariq Shihipar and Addy Osmani), technical writing for people building with Claude. It is distilled from all 10 posts, from "Seeing like an agent" (2026-04-10) through "What a task costs on Opus 5.5" and "Spending your effort" (2026-09-25). Citations use short post keys, e.g. (`effort`); the key → URL table heads `references/article-index.md`.

## The one-sentence thesis

> **Stop scaffolding the last model: give Claude a finish line, the right context on demand, and a way to check its own work, then measure what it actually does.**

Everything else is a corollary of this.

## The core philosophy (the load-bearing ideas)

1. **See like an agent.** Shape tools to what the current model can do, learned by reading its outputs; a tool only works if the model likes calling it. AskUserQuestion took three attempts before a dedicated tool beat a plan-tool parameter and a markdown format. (`seeing`, `references/tool-design.md`)
2. **Scaffolding expires; delete it.** TodoWrite plus reminders every 5 turns started constraining stronger models and was replaced by a shared Task tool. The team removed 80%+ of Claude Code's system prompt for Claude 5 models with no measurable eval loss: rules become judgment, examples become interface design, "think carefully" lines go. (`seeing`, `ctx-eng`, `opus-5-5`)
3. **Let Claude find context instead of handing it over.** Grep replaced RAG; skills, deferred tools, and subagents load context only when needed. A tree of files beats a monolithic CLAUDE.md, and the bar to add a tool is high. (`seeing`, `ctx-eng`, `references/context-engineering.md`)
4. **Caching is a prefix match; design everything around it.** Static first, dynamic last; updates as `<system-reminder>` messages; never add/remove tools or switch models mid-session; compaction as a cache-safe fork. The team alerts on hit rate like uptime. (`caching`, `references/prompt-caching.md`)
5. **You pay per task, not per token.** Every turn resends the conversation, so "the cheapest turn is the one you don't need", and every way to spend fewer tokens can cost you a finished task: a retry costs more than the savings. (`cost`, `references/cost-and-model-choice.md`)
6. **Give Claude a way to check its work.** Verification skills have the most measurable impact on output quality; a test through the right layer catches at medium effort what otherwise needs high. Check for checks before raising effort. (`skills`, `cost`, `references/verification.md`)
7. **Effort buys verification, not insight.** Higher effort wins on tasks with hidden edge cases (HTML sanitizer 1/5 → 5/5 as Claude fuzzed and read the parser's source) but doesn't fix a wrong approach ("picked the wrong reading" rose 25 → 47). (`effort`, `references/effort.md`)
8. **Raise effort before changing models; switch models at a break.** Opus 5.5 is the daily driver, Haiku/Sonnet for lookups, Fable 5.1 when xhigh fails twice on the same problem. (`cost`)
9. **Hand over the whole task with a finish line, then name the stops.** "Done means..." plus a CLAUDE.md rule on when to keep going and when to stop before anything destructive; read what it needs from you first. (`opus-5-5`, `references/long-runs.md`)
10. **Separate agents beat one long context, when they earn their cost.** Isolated subagents counter agentic laziness, self-preferential bias, and goal drift; Claude can now write the harness per task. But "most traditional coding tasks do not need a panel of 5 reviewers." (`workflows`, `references/multi-agent-workflows.md`)
11. **With Claude, measuring something makes it tractable.** claude.ai got ~3× faster in two weeks by finding more things to measure, proving proxies track wall-clock, and ratcheting every win in CI. (`faster`, `references/hill-climbing.md`)
12. **Humans own ambition, taste, and direction.** Claude defaults to cautious scope ("please be braver"); people rule on user-visible tradeoffs and cut complexity that isn't worth it. (`faster`)
13. **Produce output people will actually read: HTML, not Markdown.** Nobody reads a 100+ line Markdown plan; HTML with diagrams, tabs, and export buttons keeps you in the loop. Thariq has "stopped using Markdown altogether for almost everything", others on the team increasingly do the same, and the July post treats HTML artifacts as the successor to markdown specs, including as input Claude itself reads. (`html`, `references/html-outputs.md`)
14. **Skills are folders that push Claude off its defaults.** One category each, a gotchas section, scripts, progressive disclosure, and a description written for the model's trigger decision. (`skills`, `references/skills.md`)

## The claude.dev method, end to end

1. **Context** — lean CLAUDE.md (purpose, gotchas, stop rules), procedures in skills; audit old prompts with `/doctor` or `/claude-api prompt-audit`. (`ctx-eng`, `cost`)
2. **Spec** — Claude interviews you; you write the finish line. (`effort`, `opus-5-5`)
3. **Session** — pick model, effort, MCPs, and fast mode up front, then leave them. (`cost`)
4. **Check** — a test, build, or verification skill before any extra effort. (`skills`, `cost`)
5. **Run and scale** — one message, follow-ups mid-run, a checklist file; subagents or workflows only for long, parallel, or adversarial work. (`opus-5-5`, `workflows`)
6. **Verify and protect** — "needs from you" first, independent verifiers, ratchets and flags, `/usage` for your own numbers. (`opus-5-5`, `workflows`, `faster`, `cost`)

## Reference files

- **`references/tool-design.md`** — shaping tools to the model, AskUserQuestion's three attempts, TodoWrite → Task, Grep over RAG, deferred tools, the ~20-tool bar.
- **`references/context-engineering.md`** — the 80% deletion, then-vs-now rules, what goes in system prompt / CLAUDE.md / skills / references.
- **`references/skills.md`** — nine categories, gotchas, progressive disclosure, config, memory, scripts, on-demand hooks, distribution, measurement.
- **`references/prompt-caching.md`** — prefix layout, what breaks the cache, lifetimes and prices, cache-safe compaction.
- **`references/cost-and-model-choice.md`** — per-task cost math, Opus 5.5 pricing, three-model day, switching models (position changed Apr → Sep), `/usage`.
- **`references/effort.md`** — what effort is, Terminal-Bench 3.0 evidence, per-domain gains, two rules of thumb, the "one layer" sign.
- **`references/long-runs.md`** — asking, steering, checking Opus 5.5 runs; flagged messages.
- **`references/multi-agent-workflows.md`** — three failure modes, dynamic workflows, six patterns, use cases, when not to.
- **`references/verification.md`** — checks, what thorough verification looks like, separate checkers, ratchets, honest reporting.
- **`references/html-outputs.md`** — why HTML over Markdown, use cases, throwaway editors, rich references as inputs.
- **`references/hill-climbing.md`** — the claude.ai perf sprint: benchmarks, ratchets, the thread loop, what measurement found.
- **`references/glossary.md`** — 36 coined terms, each with its source.
- **`references/article-index.md`** — key → URL table, then all 10 posts with one-line thesis, grouped by theme.

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

- **Clashes with the user's own decisions, their project's CLAUDE.md/AGENTS.md, or their notes?** Theirs win; show both positions. This skill reports what claude.dev says, it doesn't decide for them.
- **Contested position (HTML over Markdown, switching models mid-session, low vs medium effort for implementation)?** State it as the authors', unsoftened, with the date when it moved. In testing, the model twice added a hedge the corpus doesn't contain ("Markdown's fine for specs only Claude reads").
- **Every bullet or paragraph ends with its key(s)** — the key printed on the reference bullet you used, not the reference file's name (`prompt-caching.md` also holds `cost` claims). Give the full URL when the user wants to read the post. An uncited claim can't be checked and blurs into the model's own opinion.
- **Their numbers, not paraphrase**: dollar figures, benchmark tasks, pass rates. Those are what the corpus adds over the model's defaults.
- **Never answer from outside the corpus in their voice.** Generic advice attributed to them is the one failure the user can't detect.

## Scope

Only the 10 claude.dev posts (Apr–Sep 2026). Not covered: API reference beyond caching and compaction, MCP server authoring, evals methodology beyond workflow-based comparisons, safety policy beyond Opus 5.5 flag handling, and non-Claude products. Prices, model names, and defaults date quickly: for current API facts the `claude-api` skill and live docs override this one.
