---
name: openai-agents
description: Building your own agent the way OpenAI describes it, as concepts that work on any stack. Covers whether to build one, single vs multi-agent, the harness and long runs, tools and MCP, context and memory, skills, prompt caching, cost and reasoning effort, evals, and security and sandboxing. Cites 82 OpenAI sources: developers.openai.com/blog, openai.com engineering and security posts, the practical guide to building agents, Agents SDK docs, cookbook articles, and the open-source Codex harness (its system prompts, compaction, approvals, memory, and tools).
---

# OpenAI agents

This skill holds what OpenAI has published that helps you build your own agent: 82 sources from the [developer blog](https://developers.openai.com/blog), the [Engineering category](https://openai.com/news/engineering/) of openai.com, 17 agent posts from other openai.com categories (including the Agents API launch), *A practical guide to building agents* (2025), 7 concept pages from the Agents SDK and API docs, 9 [cookbook](https://developers.openai.com/cookbook/topic/agents/) articles, two Codex guides, and the open-source [Codex harness](https://github.com/openai/codex), from April 2025 to September 2026. Keys starting with `repo-` cite the harness's own prompts and tool descriptions: what OpenAI ships, not what it argues. It keeps the concepts and drops OpenAI platform specifics. Citations use short keys like (`harness-eng`), and `references/article-index.md` links each key to its source.

## The one-sentence thesis

> **The harness is the product: give the model a computer, a map instead of a manual, and checks it can run, keep humans on the decisions and the irreversible steps, and answer every failure by improving the environment, not the prompt.**

The 14 ideas below follow from it.

## Core ideas

1. **Build an agent only where deterministic code fails, and max out one agent first.** Agents fit nuanced judgment, tangled rules, and unstructured data. Split into several only when branches or overlapping tools demand it, and try better tool names first. (`practical-guide`)
2. **The harness is the product.** Keeping reasoning and compacting instead of truncating took ARC-AGI-3 from 13.3% to 38.3% with the same model. Embed a proven loop in software built for the job instead of moving the job into a chat window. (`arc-agi-3`, `codex-platform`)
3. **Give the model a computer, stage data on disk, and keep the harness outside it.** A shell, files, and a database the model queries beat packing inputs into the prompt: "Tools write to disk, models reason over disk." (`computer-env`, `skills-shell`) Running the harness apart from the compute that executes model-written code keeps credentials out of reach and lets a run survive a lost container. (`agents-sdk-evolution`)
4. **Context is a map, not a manual.** A ~100-line entry file pointing into structured docs beat one giant instruction file, and "if the agent can't see it, it doesn't exist". Ground domain agents in layers, including the code that produces the data. (`harness-eng`, `data-agent`)
5. **Tools: few, distinct, in distribution, with capped output.** Overlap hurts more than count, formats the model was trained on work best, and output is truncated at about 10,000 tokens keeping head and tail. (`practical-guide`, `codex-prompting`, `gpt56-efficiency`)
6. **A skill's description is its routing logic.** Say exactly when to use it and when not. Scripts do the mechanics and the model does the judgment, and an instruction file makes the right skill mandatory at the right moment. (`skills-shell`, `skills-oss`, `astra-skills`)
7. **Treat history as append-only so the prefix caches.** The loop resends a growing prompt, and cache hits make sampling "linear rather than quadratic". Changes go in as new messages, tools stay in a fixed order. (`agent-loop`, `gpt56-efficiency`, `repo-agents-md`)
8. **Pay per verified success, and cost comes from architecture.** A cheaper agent that resolves half its tickets can cost more per success. Right-size model and effort per step, and re-test effort defaults with each new model. (`cost-quality`, `gpt56-guide`)
9. **Long runs live in files, not in the prompt.** A 25-hour run held together with a spec, a milestone plan with validation commands, a runbook, and a status log, fixing each failed milestone before the next. (`long-horizon`, `exec-plans`) A goal is a completion contract that only evidence can close, and running out of budget is not done. (`codex-goals`)
10. **Grade the trace, and turn every correction into an eval.** Define done before writing the skill, check the event trace deterministically, and promote repeated expert corrections to eval targets a coding agent climbs. (`eval-skills`, `tax-agents`, `improvement-loop`)
11. **Stronger models need less scaffolding.** Recipes, "run the tests" reminders, and "ask first" language written for weaker models now slow a stronger one down. Re-audit instructions and skills at every model change. Codex's own shipped prompts show it: the prompts for harness-trained models run about 80 lines against 280 to 330 for general ones,. (`astra-skills`, `data-agent`, `repo-system-prompts`)
12. **Constrain what a fooled agent can do.** Injection now looks like social engineering, so cap the damage with OS-level sandboxing, no open-ended network, and checks on every source-to-sink path, not with input filters alone. Codex ships a separate reviewer model that decides approvals from a fixed risk table. (`injection-design`, `windows-sandbox`, `codex-safely`, `repo-approvals`)
13. **Monitor real sessions, because misbehavior shows up there.** A strong model reading full transcripts caught every case employees escalated and many they missed. The usual failure is overeagerness, not hidden motives, and reading the reasoning catches far more than reading actions alone. (`agent-monitoring`, `cot-monitorability`)
14. **Human attention is the bottleneck.** "Humans steer. Agents execute." Interactive supervision tops out at three to five sessions, so let the task tracker drive agents and fix the system when one misses. (`harness-eng`, `symphony`)

Each idea is developed, with numbers and every source, in the matching reference file below.

## Reference files

- **`references/architecture-and-multi-agent.md`.** When to build an agent, model plus tools plus instructions, single agent first, manager vs handoff, parallel agents, the tracker as control plane.
- **`references/harness-design.md`.** The harness as product, the loop and its turns, serving one harness to many surfaces, the execution environment, loop latency, long-horizon runs.
- **`references/tool-design.md`.** Which tools to give, naming and describing them, staying in distribution, tool count, output limits, computer and browser tools, MCP.
- **`references/context-engineering.md`.** Context layers, instruction files as a map, the repo as system of record, memory, compaction and retained reasoning, prompting habits.
- **`references/skills.md`.** What a skill is, descriptions as routing, repo-local and mandatory skills, scripts vs judgment, keeping skills lean.
- **`references/prompt-caching.md`.** Why the loop depends on caching, assembly order, what breaks it, when it doesn't pay.
- **`references/cost-and-model-choice.md`.** Picking the model, reasoning effort, cost from architecture, the cost lever order, spend on long runs.
- **`references/evals-and-verification.md`.** In-run checks, evals for skills and agents, corrections becoming evals, review agents, evals measuring harnesses.
- **`references/safety-and-containment.md`.** Prompt injection, guardrails, sandboxes, network and secrets, approvals, monitoring agents.
- **`references/agents-in-production.md`.** Case studies with a build lesson, humans working with agents, voice agents, escalation.
- **`references/glossary.md`.** 129 coined terms, each with its source.
- **`references/article-index.md`.** All 82 sources with link, key, date, author, and one-line thesis, grouped by theme. Repo entries list the folders they draw on.

## How to answer

Walk this every time:

```
Does the question name a post, an author, or a coined term?
├── Yes → Grep article-index.md or glossary.md for the key, title, or term (never read them whole) → the theme file → answer, cite the key
└── No → Does a core idea above answer it?
    ├── Yes → answer from it; open at most one reference for the numbers
    └── No → Does a reference file cover it? (list above)
        ├── Yes → open it, answer, cite
        └── No → say "OpenAI's posts don't cover this" and stop
```

Then, before sending:

- **Does it clash with the user's own decisions, their project's CLAUDE.md or AGENTS.md, or their notes?** Theirs win. Show both positions. This skill reports what OpenAI says. It doesn't decide for them.
- **Did the advice change, or does it depend on the case?** Where OpenAI changed its advice, the skill keeps only the latest, so give that one with its date and don't bring older advice back from memory. Where posts answer the same question for different cases, the reference file lists them under "Where the answer depends on the case": give each post's case as its authors put it. Don't close with your own rule of thumb: a verdict the posts never gave reads as OpenAI's.
- **Every bullet or paragraph ends with its key(s).** Use the key printed on the reference bullet you took it from. Give the full URL when the user wants to read the source. An uncited claim can't be checked and blurs into the model's own opinion.
- **Use their numbers instead of paraphrasing.** They're what the corpus adds over the model's defaults.
- **Separate what OpenAI argues from what it ships.** Say whether a claim comes from a post or from the Codex repo (`repo-*`), and name the file when it matters. Where the two differ, show both, since practice is the stronger evidence.
- **Say when a source is thin.** Guest posts (Dagster, Skyscanner, Alpic, Perplexity) are one team's experience and the cost cookbook (`cost-quality`) is a simulation. The reference bullets mark both, so carry the caveat into the answer.
- **Never answer from outside the corpus in their voice.** Generic advice attributed to OpenAI is the one failure the user can't detect. If the user wants Anthropic's view too, use the `claude-agents` skill for that side and keep the two apart.

## Scope

Only these 82 sources, up to September 2026, chosen for building an agent. Not covered: OpenAI API and product specifics (endpoints, parameters, Codex settings, pricing), launches, customer stories without a build lesson, OpenAI's infrastructure posts, and videos or talks. For current OpenAI API facts, use their live docs.
