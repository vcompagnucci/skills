# Context engineering

Everything Claude receives besides your prompt: system prompt, CLAUDE.md, skills, memory, references. The corpus's position, set out most fully in July 2026, is that Claude 5 models are *over*-constrained by habits built for weaker models, and the fix is deletion plus progressive disclosure.

## The core result

- **Delete most of it.** The team removed over 80% of Claude Code's system prompt for Opus 5 and Fable 5 with no measurable loss on coding evals; `/doctor` (claude doctor) now rightsizes your skills and CLAUDE.md. (`ctx-eng`)
- **Conflicts cost thinking.** Internal transcripts showed "leave documentation as appropriate" and "DO NOT add comments" in the same request, from system prompt, skills, and user clashing; Claude usually resolves intent but has to think harder. (`ctx-eng`)
- **Ritual instructions cost money too.** A prompt audit on a 44-ticket support benchmark removed a mandatory six-step procedure, a scratchpad rule, a verify-twice rule, and contradictions, cutting cost a further 9% on top of the model upgrade. Run `/claude-api prompt-audit` when migrating. (`cost`)

## Then and now (Claude 5 generation)

- **Rules → judgment.** Old prompt: "default to writing no comments... one short line max". New: "Write code that reads like the surrounding code: match its comment density, naming, and idiom." The old rule was a tradeoff accepted for older models. (`ctx-eng`)
- **Examples → interface design.** Examples constrain; expressive parameters guide. (`ctx-eng`)
- **Everything upfront → progressive disclosure.** Code review and verification guidance moved out of the system prompt into skills; tools load on demand via ToolSearch. (`ctx-eng`)
- **Repetition → one tool description.** (`ctx-eng`)
- **Memory in CLAUDE.md (# hotkey) → auto-memory.** (`ctx-eng`)
- **Simple specs → rich references.** HTML artifacts, test suites as specs, code to port, rubrics checked by verifier agents. (`ctx-eng`)
- **"Think carefully" lines → delete them.** Opus 5.5 always thinks and chooses how much; removing the line made replies start sooner with no clear quality drop. (`opus-5-5`)

## Per layer

- **System prompt: product context.** Where you should spend time if you build your own harness; in Claude Code you'll likely never touch it. (`ctx-eng`)
- **CLAUDE.md: lightweight, mostly gotchas.** Briefly say what the repo is for, spend tokens on codebase gotchas, don't state what Claude can see from the file system, point to skills for procedures like verification. (`ctx-eng`)
- **CLAUDE.md is resent every turn.** The costs docs suggest under 200 lines. (`cost`)
- **CLAUDE.md is where you name the stops.** "When a step doesn't need my input, keep going... Stop and ask only when you can't continue without me, or before anything destructive." Or the opposite for pair programming. And the report format: "Blocked on me, Changed, Found." (`opus-5-5`)
- **Skills: lightweight guides that encode your opinions.** Not overconstrained except in critical areas; long ones split into many files. (`ctx-eng`, `skills`)
- **References: prefer code.** An HTML mockup beats a description or screenshot of a design. (`ctx-eng`)
- **Updates go in messages, not the system prompt.** Claude Code injects a `<system-reminder>` into the next user message or tool result, preserving the cache. (`caching`)

## Not a monolith

- **A tree of files beats a central repository.** The myth is that CLAUDE.md or SKILL.md must hold every practice you *might* need or Claude won't find it; instead load files at the right time. (`ctx-eng`, `skills`)
- **Avoid putting rare knowledge in always-on context.** Claude Code docs in the system prompt would add context rot for questions users rarely ask. (`seeing`)

## Key source articles
`ctx-eng` · `skills` · `opus-5-5` · `cost` · `caching`
