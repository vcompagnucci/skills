---
name: system-prompts
description: Write, review or migrate the instructions an AI agent runs on: a system prompt, developer message, Agents SDK instructions, AGENTS.md or CLAUDE.md. Use for what the prompt holds, wording rules, procedures and escalation, few-shot examples, tool use and autonomy, progress and stopping, tone, formatting, reply language and voice agents, grounding, prompt layout, operator vs user authority, per-model differences, subagent briefs, and improving or versioning a prompt.
---

# System prompts

How to write the instructions an agent runs on, for any agent. Most examples come from customer support, where one prompt meets strangers, policy and handoffs at once. Every claim cites its source as (`slug`); to look one up, grep `references/article-index.md`. Quoted text followed by a slug is that source's wording. Quoted text without one is an example. If the user asks how a claim was selected, see `references/sources.md`.

This skill covers the content and wording of an agent's instructions. agent-harness owns how the context is assembled and delivered: layers, cache order, loading on demand, compaction, state, tool design and tool descriptions. agent-security owns prompt injection, system-prompt extraction, manipulation by the person in the chat, and guardrails. agent-evals owns measuring the agent, judge prompts and simulated users. A company's own voice, policies and tool list belong in a private skill, and they override this skill where they disagree.

## What every prompt gets right

The steps below apply these ten. Where a rule names (evidence: file "heading"), that section holds its proof; open it only to check a rule you doubt.

1. **Write only what the model can't know or gets wrong by default.** Treat it as a brilliant new employee who lacks your norms, and show the prompt to a colleague with minimal context: if they'd be confused, the model will be too. Assume it is already very smart, because every line competes with the conversation for attention. (`anthropic-prompting-best-practices`, `anthropic-skill-authoring-best-practices`)
2. **Cut before you add, one group at a time, re-running the same evals after each cut.** Leaner prompts scored higher at lower cost on GPT-5.6, and Anthropic cut most of Claude Code's system prompt for Claude 5 models with no measurable loss (evidence: models.md "Migrating to a new model", examples.md "Whether to add examples at all"). (`openai-gpt-5-6-prompt-guidance`, `anthropic-new-rules-context-engineering-claude-5`)
3. **Write at the right altitude: the destination, the bar and the few decision points.** Hard-coded if-else logic breaks on the first case it didn't foresee, and vague guidance gives the model nothing to check. OpenAI's support example: "Resolve the customer's issue end to end." (`anthropic-effective-context-engineering`, `openai-gpt-5-6-prompt-guidance`)
4. **Give each rule its reason, its positive target and, where it sets a limit, a number.** The model generalizes from the reason, and a count lets it check its own draft (evidence: instructions.md "Say what you want and why"). (`anthropic-prompting-best-practices`)
5. **Add a line only for a failure you saw, and keep that requirement in the eval set.** Lines written for imagined failures pile up into conflicts; a gotchas section built from real failures is the highest-signal part of a prompt. (`anthropic-effective-context-engineering`, `anthropic-how-we-use-skills`)
6. **Keep capitals and absolute words (NEVER, ALWAYS, IMPORTANT, MUST) for the one or two true invariants, and back each invariant with a check in code.** A line counts if it uses capitals for emphasis or an absolute word (never, always, must, important) in any case. The split between system and user roles alone guarantees nothing (evidence: authority.md "Whether the model keeps the order"). (`zendesk-generative-procedures-best-practices`, `geng-control-illusion-instruction-hierarchy`)
7. **Treat the rule count as a budget: at 40 simultaneous rules (Eliav's rough threshold), restructure instead of rewording.** Past that point rephrasing stops helping (evidence: rule-sets.md "Treat rules as a budget"). (`eliav-prompt-design-at-scale`)
8. **Prompt per model family, set the API's settings before the wording, and re-check the prompt at every model change.** The same line helps one family and hurts another, and reasoning effort, verbosity and structured outputs do what prose does less reliably (evidence: models.md "Settings before wording"). (`anthropic-effort`, `openai-using-gpt-5-5`)
9. **Give the agent an honest exit (the fallback line vendor guides describe) for every gap: the exact sentence for "I don't know", for out of scope, and for a tool that failed or returned nothing.** Without one the model fills the gap with a plausible answer (evidence: grounding.md "When the agent doesn't know"). (`anthropic-reduce-hallucinations`, `google-dialogflow-cx-playbook-best-practices`)
10. **Put procedures, examples and reference material where they load when needed, and keep the always-on prompt to what a third or more of traffic needs.** (`anthropic-new-rules-context-engineering-claude-5`, `openai-skills-shell-compaction-tips`)

## Every answer

Whatever the job, your answer is done only when every number, and every prompt line you quote or adapt, is copied from a reference with its slug, model, date and who measured or wrote it, and every number you chose yourself carries "starting value to tune" where it appears. A date missing from the reference line is under the slug in article-index.md; an undated source is "undated, read 2026-10-22". Quote marks go only around a source's or the prompt's exact words, with an ellipsis wherever you cut; text you changed, even by one word, is adapted and goes unquoted, followed by its slug. A number the user gave stays as given. A count you make yourself (rules, lines, emphasis) shows what it counted.

## Steps

Pick the job and do its steps in order. At each step open only the files it names, under that step's condition, one at a time, and stop only at the job's *Done when*.

**Write a prompt from scratch.**
1. Write the success criteria as checkable numbers, then run the task with no prompt on three scenarios (read only iterate.md "Before the first draft"; `anthropic-skill-authoring-best-practices`). A larger test set is your own starting value to tune. Done when you hold a list of what the model gets wrong by default. If you can't run the model yourself, put the criteria and the no-prompt run first in your answer, as the test the user runs before adopting the draft.
2. Draft from the skeleton: identity line, goal and finish line, deployment context (anatomy.md). Add a rule only for a gap from step 1, worded per instructions.md. Done when every line answers a listed gap or states a fact the model can't know.
3. Write the procedures and the escalation (procedures.md). Done when every request type the user named, plus the highest-volume and highest-handover types in their data (procedures.md "Start from what you already have"), has a procedure with a trigger, steps and a concrete exit, and every escalation trigger is countable and carries the words to say, written out as the agent will say them (a `{{...}}` slot may fill a fact inside that sentence, not replace it).
4. Set the policies the agent applies on every turn, opening only the files this agent needs. Always: its honest exits (grounding.md). When it calls tools or works over several steps: tool use and asking (tools-and-autonomy.md), updates and stopping (progress-and-stopping.md). Tone, length and format: voice-and-output.md for a text surface, voice-agents.md for a spoken one. Reply language: language.md, only when the task names more than one language or a market where users write in another. Done when the draft holds the exact sentences for "I don't know", out of scope, and a failed or empty tool result (rule 9), plus the lines each file you opened calls for.
5. Check the draft against the target model's section in models.md (skip the other families; if the user names no model, skip models.md and list the model check as open) and rule-sets.md "Treat rules as a budget" (one rule per separate demand). Done when the always-on prompt holds fewer than 40 rules (rule 7), or you moved procedures into loaded skills and show the count after the move; every number in the draft, in digits or in words (twice, three turns, two-sentence), is a source's (slug in a list right after the draft, keyed to the line) or carries [starting value to tune] at that spot; the draft meets rules 4, 6 and 9; every branch has an exit and every conflict a stated winner; and you have counted the lines with capitals or absolute words and rewritten all but the one or two invariants, each backed by a code check. A procedure's uppercase WHEN, IF and THEN are structure, not emphasis, and don't count.

**Review an existing prompt.**
1. Give every line one verdict: keep, rewrite, move (to a procedure, a skill, a tool definition, config or code) or delete. Open common-lines.md and match each line; a match is settled, and its "Evidence:" pointer is only for a verdict you doubt. For a line it doesn't cover, use iterate.md "Auditing an existing prompt" and instructions.md "Delete lines that change nothing", plus the topic file when one applies: rule-sets.md for conflicts, authority.md for user trust, grounding.md for sources, models.md for a model family. Done when every line of the prompt has a verdict.
2. Count the lines that use capitals or absolute words (rule 6), list them, and say which one or two, if any, stay as invariants.
3. Report every line with its verdict. For each line not marked keep, add what goes wrong, the action the verdict calls for (the rewrite, the destination or the deletion) and its slug. If you advise testing the rewrite, size the test from iterate.md "Before the first draft" (three scenarios, `anthropic-skill-authoring-best-practices`). Any tally comes from the per-line verdicts, with a conditional verdict counted as its own kind. Done when every line of the prompt appears in the report with its verdict, and every line not marked keep has all four parts.

**Move a prompt to a new model.** Follow models.md "Settings before wording", then "Migrating to a new model", then the target family's section (skip the others), starting with the target model's newest prompting guide and the model switched with the prompt unchanged. Done when the evals match or beat the old model, the prompt is no longer than it was, and each model-specific line left names the defect it covers (iterate.md "Versions and rollout"). If you can't run the evals, done when your answer opens with the eval run to do first (model switched, prompt unchanged, effort pinned), the prompt is no longer than it was, and each line you deleted or kept as model-specific names the defect it covers.

**Write an instruction file** (AGENTS.md, CLAUDE.md, rules files): instruction-files.md. Done when every line is a command, convention, gotcha or pointer the agent can't find by looking, the critical lines sit at the top, and the files fit the harness's cap. For an existing file, measure the lines and bytes of everything the harness loads together (its global file, such as ~/.codex/AGENTS.md or ~/.claude/CLAUDE.md, imports and nested files; check each exists) and say where each cap falls.

**Answer a question on one topic** (how many examples, how long an AGENTS.md, what to say about X): the file the tree in "Where to look" names, plus only the files it points to for this question. Done when the answer gives that file's rule with its reason, and, when the file has a "Where the answer depends on the case" section, every position it holds on the question, each with its models and date.

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

Open one reference at a time.

## Which source wins

The same order decides inside this skill and outside it, whenever two sources answer one question differently, including a source dated after the skill's answer: a prompting guide, a model's release notes, a published system prompt, a file the user gives you. Vendors rewrite their prompting guides with each model generation, so the model-specific advice here goes stale first.

Before the order, two checks:

- **Can you open it?** A link, a file, or a page you found by searching. A claim with none of these ("OpenAI now says X", from memory) → search for it if you can. If you can't find it, ask for the link and keep the skill's answer until it arrives. A claim you can't open can't be dated or compared.
- **Is it the same question?** Same means the same instruction, for the same kind of model. Advice for another model family answers a different question, so report it next to the skill's answer, as a separate point.

Then:

1. **The newest date wins, whoever published it.** Give its date and name the rule here that it replaces. An undated docs page counts as read on 2026-10-22.
2. **Dates don't settle it → Anthropic and OpenAI win** over everyone else.
3. **Anthropic and OpenAI disagree and nothing settles it → report both side by side.** The skill's own ties sit under "Where the answer depends on the case" in rule-sets.md, examples.md, structure.md and iterate.md; open the one for the question at hand.

Inside the skill this order already ran and the losing position is gone, so answer with the position the skill states.
