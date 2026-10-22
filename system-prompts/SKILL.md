---
name: system-prompts
description: Write, review or migrate the instructions an AI agent runs on: a system prompt, developer message, Agents SDK instructions, AGENTS.md or CLAUDE.md. Use for what the prompt holds, wording rules, procedures and escalation, few-shot examples, tool use and autonomy, progress and stopping, tone, formatting, reply language and voice agents, grounding, prompt layout, operator vs user authority, per-model differences, subagent briefs, and improving or versioning a prompt.
---

# System prompts

How to write the instructions an agent runs on, for any agent. Most examples come from customer support, where one prompt meets strangers, policy and handoffs at once. It distills 329 sources read in October 2026: Anthropic and OpenAI first, then other labs, the published prompts of open-source agents (Codex first), support vendors and research. Every claim cites its source as (`slug`), listed in `references/article-index.md`. Quoted text followed by a slug is that source's wording. Quoted text without one is an example.

> A prompt holds what the model can't know and the few places its default is wrong; every other line costs attention, and each new model makes more of them wrong.

## What every prompt gets right

Ten points to hold whatever the job. The steps below apply them, and each reference holds the evidence.

1. **Write only what the model can't know or gets wrong by default.** Treat it as a brilliant new employee who lacks your norms, and show the prompt to a colleague with minimal context: if they'd be confused, the model will be too. Assume it is already very smart, because every line competes with the conversation for attention. (`anthropic-prompting-best-practices`, `anthropic-skill-authoring-best-practices`)
2. **Cut before you add, one group at a time, re-running the same evals after each cut.** On GPT-5.6, leaner system prompts scored 10-15% higher (OpenAI's rough figure) on a sample of OpenAI's internal coding-agent evals with 41-66% fewer tokens and 33-67% less cost, ranges OpenAI calls directional. Anthropic removed over 80% of Claude Code's system prompt for Opus 5 and Fable 5 with no measurable loss on its coding evals (2026-07-24). (`openai-gpt-5-6-prompt-guidance`, `anthropic-new-rules-context-engineering-claude-5`)
3. **Write at the right altitude: the destination, the bar and the few decision points.** Hard-coded if-else logic breaks on the first case it didn't foresee, and vague guidance gives the model nothing to check. OpenAI's support example: "Resolve the customer's issue end to end." (`anthropic-effective-context-engineering`, `openai-gpt-5-6-prompt-guidance`)
4. **Give each rule its reason, its positive target and, where it sets a limit, a number.** The model generalizes from the reason, and a count lets it check its own draft (instructions.md). (`anthropic-prompting-best-practices`)
5. **Add a line only for a failure you saw, and keep that requirement in the eval set.** Lines written for imagined failures pile up into conflicts; a gotchas section built from real failures is the highest-signal part of a prompt. (`anthropic-effective-context-engineering`, `anthropic-how-we-use-skills`)
6. **Keep capitals and absolute words for the one or two true invariants, and back each invariant with a check in code.** On 2024-era models the system rule won only 9.6-45.8% of conflicts on average (Control Illusion, 2025-02), so the role split alone guarantees nothing (authority.md). (`zendesk-generative-procedures-best-practices`, `geng-control-illusion-instruction-hierarchy`)
7. **Treat the rule count as a budget.** At 40 simultaneous rules, a threshold Eliav gives as rough, restructure instead of rewording: by 80 no tested model produced a perfect response (rule-sets.md). (`eliav-prompt-design-at-scale`)
8. **Prompt per model family, set the API's settings before the wording, and re-check the prompt at every model change.** The same line helps one family and hurts another, and reasoning effort, verbosity and structured outputs do what prose does less reliably (models.md). (`anthropic-effort`, `openai-using-gpt-5-5`)
9. **Give the agent an honest exit for every gap: the exact sentence for "I don't know", for out of scope, and for a tool that failed or returned nothing.** Without one the model fills the gap with a plausible answer (grounding.md). (`anthropic-reduce-hallucinations`, `google-dialogflow-cx-playbook-best-practices`)
10. **Put procedures, examples and reference material where they load when needed, and keep the always-on prompt to what a third or more of traffic needs.** (`anthropic-new-rules-context-engineering-claude-5`, `openai-skills-shell-compaction-tips`)

## Steps

Pick the job, open the files it names in order, and stop only at its completion check.

**Write a prompt from scratch.**
1. Write the success criteria as checkable numbers, then run the task with no prompt (iterate.md, "Before the first draft"). Done when you hold a list of what the model gets wrong by default. If you can't run the model yourself, put the criteria and the no-prompt run first in your answer, as the test the user runs before adopting the draft.
2. Draft from the skeleton: identity line, goal and finish line, deployment context (anatomy.md). Add a rule only for a gap from step 1, worded per instructions.md. Done when every line answers a listed gap or states a fact the model can't know.
3. Write one procedure per frequent request type, each with a trigger, steps and an exit, and escalation as countable triggers plus the words to say (procedures.md).
4. Set the policies the agent applies on every turn, opening only the files this agent needs. Always: what it says when it doesn't know (grounding.md). When it calls tools or works over several steps: tool use and asking (tools-and-autonomy.md), updates and stopping (progress-and-stopping.md). Tone, length and format: voice-and-output.md for a text surface, voice-agents.md for a spoken one (not voice-and-output.md). Reply language: language.md, only when the task names more than one language or a market where users write in another; otherwise skip it.
5. Check the draft against the target model's section in models.md and the rule budget in rule-sets.md (one rule per separate demand; say how you counted when you report a count). Done when every rule carries its reason, every limit a number (a number from a source copied with its slug; a number you chose labeled as a starting value to tune right where it appears, in the prompt as well as in your notes), every branch an exit, every conflict a stated winner, every rule that must never break a named code check behind it, and absolute words (never, always, must), not only capitals, appear only on the one or two invariants: count the lines that use them, and rewrite all but those. The uppercase WHEN, IF and THEN of a procedure's layout (procedures.md) are structure, not emphasis, and don't count.

**Review an existing prompt.**
1. Give every line one verdict: keep, rewrite, move (to a procedure, a skill, a tool definition, config or code) or delete. Open common-lines.md first and match each line against it. Open another reference only for a line it doesn't cover: iterate.md "Auditing an existing prompt", instructions.md "Delete lines that change nothing", and rule-sets.md for conflicts.
2. A line common-lines.md matches is done: its "Evidence:" pointer is for checking a verdict you doubt, not further reading. Open authority.md, grounding.md or models.md only for a line it doesn't cover about user trust, sources or a model family.
3. Count the lines that use capitals or absolute words (NEVER, ALWAYS, IMPORTANT, MUST) and say which one or two, if any, stay as invariants.
4. Report each problem as the quoted line, what goes wrong, the rewrite and the source slug. Quote marks go only around the prompt's or a source's exact words; a rewrite adapted from a source goes unquoted, followed by its slug. A number you put inside a rewrite is either a source's, with its slug, or labeled as a starting value to tune. If you advise testing the rewrite, use the sizes in iterate.md "Before the first draft" (three scenarios, `anthropic-skill-authoring-best-practices`) or label your own as a starting value. Any count or tally you add comes from the per-line verdicts, with a conditional verdict counted as its own kind. Done when no line of the prompt is left without a verdict.

**Move a prompt to a new model.** Follow models.md "Settings before wording" and then "Migrating to a new model", in that order, starting with the target model's newest prompting guide and the model switched with the prompt unchanged. Done when the evals match or beat the old model, the prompt is no longer than it was, and each model-specific line left names the defect it covers (iterate.md, "Versions and rollout").

**Write an instruction file** (AGENTS.md, CLAUDE.md, rules files): instruction-files.md. Done when every line is a command, convention, gotcha or pointer the agent can't find by looking, the critical lines sit at the top, and the files fit the harness's cap.

**Brief a subagent or write an orchestrator prompt**: multi-agent.md. Done when a fresh agent holding only the brief could do the job: objective, context, boundaries against the other subagents (what they cover), output format, tools, stop condition or effort budget, and report shape. Without boundaries, subagents duplicate each other's work (`anthropic-research-system`).

## Where to look

```
What are you working on?
├── What the prompt holds and in what order: skeleton, identity, deployment context, date,
│   what stays out, length → anatomy.md
├── Wording one instruction: why, positive phrasing, specificity, scope, emphasis, refusals,
│   lines that change nothing → instructions.md
├── Many rules in one prompt: conflicts, how many a model keeps, repeating a rule,
│   order in a list → rule-sets.md
├── A procedure: steps, triggers, branches, escalation and retries, done conditions,
│   prompt vs skill → procedures.md
├── A line from a real prompt and whether to keep it → common-lines.md
├── Few-shot examples: how many, what they contain, where they go → examples.md
├── Acting vs advising, what needs approval, asking vs assuming, calling tools → tools-and-autonomy.md
├── Progress updates, plans on long runs, persistence, when to stop, checks before "done"
│   → progress-and-stopping.md
├── The agent stops too often, asks permission for small things, or ends its turn early
│   → tools-and-autonomy.md "Ask or assume", then progress-and-stopping.md "When to stop"
├── Tone, persona, length, formatting per surface, words to ban, the last message,
│   in a text channel → voice-and-output.md
├── Which language to answer in, switching, register, translation → language.md
├── A spoken agent, or moving a chat agent to the phone: sentence caps, turn-taking, numbers
│   read aloud, preambles, barge-in → voice-agents.md, then language.md "Language on a voice channel"
│   (voice-and-output.md is for text channels)
├── Answering only from sources, citations, "I don't know", reports on its own work → grounding.md
├── The prompt's own layout: roles, sections and delimiters, long documents, templates
│   and variables, injected text, mid-conversation changes → structure.md
├── What an operator's prompt can and can't change, user trust, injected text's rank → authority.md
├── One model family, reasoning effort vs wording, migrating to a new model → models.md
├── A subagent brief, routing descriptions, handoffs, the orchestrator, reviewers → multi-agent.md
├── AGENTS.md, CLAUDE.md, rules files for coding agents → instruction-files.md
├── Improving a prompt: audits, metaprompting, optimizers, versions and rollout → iterate.md
└── How published production prompts (Codex, the Claude apps, Gemini CLI, ...) are built → worked-examples.md
A coined term you don't recognize → grep glossary.md for it; a source by slug → grep article-index.md
```

Open one reference at a time. **Never quote a number or a prompt line from memory.** Copy it from the reference with its model, date and who measured or wrote it.

## Which source wins

The same order decides inside this skill and outside it, whenever two sources answer one question differently. That includes a source dated after the skill's answer: a prompting guide, a model's release notes, a published system prompt, a file the user gives you. Vendors rewrite their prompting guides with each model generation, so the model-specific advice here goes stale first.

Before the order, two checks:

- **Can you open it?** A link, a file, or a page you found by searching. A claim with none of these ("OpenAI now says X", from memory) → search for it if you can. If you can't find it, ask for the link and keep the skill's answer until it arrives. A claim you can't open can't be dated or compared.
- **Is it the same question?** Same means the same instruction, for the same kind of model. Advice for another model family answers a different question, so report it next to the skill's, never in place of it.

Then:

1. **The newest date wins, whoever published it.** Give its date and name the rule here that it replaces. An undated docs page counts as read on 2026-10-22.
2. **Dates don't settle it → Anthropic and OpenAI win** over everyone else.
3. **Anthropic and OpenAI disagree and nothing settles it → report both, never pick one.** The skill's own ties sit in the section titled Where the answer depends on the case, in the files that have one.

Inside the skill this order already ran, and the losing position is gone, so never bring it back from memory. A model this skill doesn't list → say the skill doesn't cover it, and read the vendor's newest prompting guide if you can search.

## Numbers to use

| What | Number | Source |
|---|---|---|
| Leaner system prompts, GPT-5.6 | evals +10-15% (rough figure), tokens -41-66%, cost -33-67% (OpenAI's internal coding-agent sample, directional) | `openai-gpt-5-6-prompt-guidance` |
| Claude Code prompt for Opus 5 and Fable 5 | over 80% removed, no measurable loss on coding evals (2026-07-24) | `anthropic-new-rules-context-engineering-claude-5` |
| Simultaneous rules | restructure at 40 (Eliav's rough threshold); perfect-response rate zero by 80 for every model tested (2026-07-21) | `eliav-prompt-design-at-scale` |
| 500 keyword instructions at once | best of 20 models 68%, o3 62.8%, claude-opus-4 44.6% (IFScale, 2025-07) | `distyl-ifscale-instruction-density` |
| Reasoning-trace demos on reasoning models | AIME'25 -6-16% with one demo (the authors' rough range), up to -35% with three (Qwen3, R1 distills, 2025-09-27) | `wang-harm-to-help-reasoning-demos` |
| Few-shot examples | 3 to 5, diverse, in `<example>` tags (Anthropic, read 2026-10-22); on reasoning models no worked-reasoning demos (row above); many-shot, hundreds of cached examples, gained comparably to fine-tuning (DeepMind, 2024-10-17). This skill's default: start at 3 to 5 and try many-shot only after a handful fails (examples.md, end of file) | `anthropic-prompting-best-practices`, `deepmind-many-shot-in-context-learning` |
| Instruction hierarchy attacks, GPT-6 family | defender success 99.99% Astra, 99.97% Sol and Luna (2026-09-03) | `openai-gpt-6-astra-system-card` |
| AGENTS.md and CLAUDE.md size | Codex stops at 32 KiB combined; Devin auto-loads the first 16 KiB per file; Claude Code's docs give a target of under 200 lines per CLAUDE.md (read 2026-10-22) | `openai-codex-agents-md-guide`, `devin-agents-md`, `anthropic-claude-code-memory` |

## Scope

This skill covers the content and wording of an agent's instructions. agent-harness owns how the context is assembled and delivered: layers, cache order, loading on demand, compaction, state, tool design and tool descriptions. agent-security owns prompt injection, system-prompt extraction, manipulation by the person in the chat, and guardrails. agent-evals owns measuring the agent, judge prompts and simulated users. A company's own voice, policies and tool list belong in a private skill, never in this one, and they override this skill where they disagree. How the claims were chosen is in `references/sources.md`, and every source is in `references/article-index.md`.
