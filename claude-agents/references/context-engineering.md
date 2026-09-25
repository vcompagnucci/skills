# Context engineering

Everything Claude receives besides your prompt: system prompt, CLAUDE.md, skills, memory, and references. The July 2026 post makes the case in full. Claude 5 models are overconstrained by habits built for weaker models, and the fix is to delete most of those habits and load the rest only when needed.

## The main result

- **Delete most of it.** The team removed over 80% of Claude Code's system prompt for Opus 5 and Fable 5 with no measurable loss on coding evals. `/doctor` (claude doctor) now trims your skills and CLAUDE.md the same way. (`ctx-eng`)
- **Conflicting instructions cost thinking.** Internal transcripts showed "leave documentation as appropriate" and "DO NOT add comments" in the same request, because the system prompt, a skill, and the user disagreed. Claude usually works out the intent, but it has to think harder to get there. (`ctx-eng`)
- **Ritual instructions cost money.** A prompt audit on a 44-ticket support benchmark removed a mandatory six-step procedure, a scratchpad rule, a verify-twice rule, and a few contradictions. That cut cost another 9% on top of the model upgrade. Run `/claude-api prompt-audit` when you migrate. (`cost`)

## What changed with Claude 5

- **Rules → judgment.** The old prompt said "default to writing no comments... one short line max". The new one says "Write code that reads like the surrounding code: match its comment density, naming, and idiom." The old rule was a tradeoff they accepted for older models. (`ctx-eng`)
- **Examples → interface design.** Examples narrow what the model tries. Clear parameters guide it instead. (`ctx-eng`)
- **Everything up front → loaded when needed.** Code review and verification guidance moved from the system prompt into skills. Tools load on demand through ToolSearch. (`ctx-eng`)
- **Repetition → one tool description.** (`ctx-eng`)
- **Memory in CLAUDE.md (the # hotkey) → auto-memory.** (`ctx-eng`)
- **Simple specs → rich references.** HTML artifacts, test suites used as specs, code to port, and rubrics that verifier agents check against. (`ctx-eng`)
- **"Think carefully" lines → deleted.** Opus 5.5 always thinks and decides how much. Removing the line made replies start sooner, with no clear drop in quality. (`opus-5-5`)

## Layer by layer

- **The system prompt is product context.** If you build your own agent, this is where to spend time. In Claude Code you'll probably never touch it. (`ctx-eng`)
- **CLAUDE.md is short and mostly gotchas.** Say briefly what the repo is for, then spend the space on gotchas in the codebase. Skip anything Claude can see by looking at the files. Point to skills for procedures like verification. (`ctx-eng`)
- **CLAUDE.md is resent on every turn.** The costs docs suggest keeping it under 200 lines. (`cost`)
- **CLAUDE.md is where you name the stops.** "When a step doesn't need my input, keep going... Stop and ask only when you can't continue without me, or before anything destructive." For pair programming you might want the opposite. It's also where you set the report format, like "Blocked on me, Changed, Found." (`opus-5-5`)
- **Skills are short guides that hold your opinions.** Keep them loose except where a mistake is expensive, and split long ones into several files. (`ctx-eng`, `skills`)
- **Prefer code as a reference.** An HTML mockup of a design gets better results than a description or a screenshot. (`ctx-eng`)
- **Send updates as messages, not by editing the system prompt.** Claude Code puts a `<system-reminder>` in the next user message or tool result, which keeps the cache intact. (`caching`)

## A tree of files, not one big file

- **Split it up.** A common myth says CLAUDE.md or SKILL.md has to hold every practice you *might* need, or Claude won't find it. Instead, keep a tree of files that Claude loads at the right time. (`ctx-eng`, `skills`)
- **Keep rare knowledge out of always-on context.** Claude Code's own docs in the system prompt would have added noise to every session, for questions users rarely ask. (`seeing`)

## Key source articles
`ctx-eng` · `skills` · `opus-5-5` · `cost` · `caching`
