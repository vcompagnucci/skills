# Prompting and steering long runs

How to hand work to Claude when a run can last hours, stay in control while it runs, and get output you'll actually read. Mostly from Addy Osmani's Opus 5.5 guide, the Claude Code best-practices page, and Thariq Shihipar's effort and HTML posts. Four research posts add multi-day science runs and usage data from real Claude Code sessions.

## Asking

- **Give the whole task in one message, with a finish line.** "Done means: every endpoint uses the new client, the old client is deleted, and the test suite passes. Stop and ask me only if a test fails for a reason you can't explain." Opus 5.5 gains most on multi-step work, and early testers let it run for hours with little oversight. (`opus-5-5`)
- **Don't tell it to think.** It always does. Removing "think carefully" made replies start sooner, with no clear drop in quality. (`opus-5-5`)
- **Name the design defaults you don't want.** "Avoid a generic look" just swaps one default for another. List the patterns instead: cream backgrounds, italic accent words, "01 / 02 / 03" labels, monospace labels, pill buttons. Look at what it picks instead, and add that to the list if you don't like it either. (`opus-5-5`)
- **Have it interview you first.** Thariq's loop for a new feature: write a spec, let Claude interview you about what's missing, implement at low effort, review, then verify at high. With a detailed spec, the result barely depends on effort. (`effort`)
- **Attach the chart, don't retype it.** Opus 5.5 reads charts, screenshots, and diagrams, including meaning that depends on position, like which boxes an arrow connects. When you want a spreadsheet or document, ask for the finished file, not an outline. (`opus-5-5`)
- **Don't ask it to show its internal reasoning in the reply.** That request can be flagged. Ask "Explain why you chose this approach in three sentences" instead. (`opus-5-5`)

## Steering

- **Name the stops in CLAUDE.md.** On long runs Claude sometimes pauses to report, to offer to continue, or to list choices that don't block it. Tell it to keep going when a step doesn't need you, to put status notes in the same message as its next action, and to stop only when it's blocked or before anything destructive. Keep permission prompts on. For pair programming, ask for the opposite. (`opus-5-5`)
- **Add to a running task instead of restarting it.** Type a follow-up and press Enter while it works. On long runs a restart costs more. (`opus-5-5`)
- **Keep the task list in a file.** "Keep a checklist in TASKS.md." The file survives summarization, and you can read it instead of scrolling back. Claude Code's own todo tool moved to a shared Task tool so subagents could coordinate (`seeing`). The file is for you and for surviving compaction. For multi-day runs, keep a progress file (CHANGELOG.md) that also records failed approaches and why, or later sessions retry the same dead ends. (`opus-5-5`, `long-running-science`)
- **Split big audits and migrations across subagents, and check each one's evidence.** End with one table. (`opus-5-5`)
- **In long chats, say earlier answers are settled.** Opus 5.5 sometimes goes back over earlier answers when you ask a short follow-up, which slows it down. Skip this in long analysis, where a later step can expose an earlier mistake. (`opus-5-5`)
- **Oversight moves from approving to interrupting.** In Claude Code usage data, full auto-approve rises from about 20% of sessions for new users to over 40% at 750 sessions, while the interrupt rate rises from about 5% to 9% of turns. The longest turns (99.9th percentile) went from under 25 to over 45 minutes in three months (Oct 2025 to Jan 2026). (`agent-autonomy`)
- **Claude stops itself more than people interrupt it,** twice as often on the most complex tasks. Its top reasons are offering a choice of approach (35%) and gathering diagnostics (21%). People interrupt most to add missing context (32%). (`agent-autonomy`)
- **People plan, Claude executes.** Across ~400,000 sessions, people made about 70% of planning decisions and 20% of execution decisions. Domain expertise, not coding background, predicted success: verified success went from 15% for novices to 28-33% for others, and novices abandoned troubled sessions at 19% against 5-7%. (`cc-in-practice`)
- **Push it to aim higher.** By default Claude keeps scope small. It files tickets for what it finds, hedges, and pads its estimates. The performance team told it "please be braver" and "the targets are not the stopping point." (`faster`)
- **People keep taste and direction.** Decide the tradeoffs users will notice, from before-and-after recordings. Keep each thread narrow. Reject complexity that isn't worth it, as in "2ms per send is not worth the complexity". (`faster`)

## Session hygiene

- **Plan only when you're unsure.** Plan mode adds overhead. Use it when the approach is unclear, the change spans several files, or the code is unfamiliar. "If you could describe the diff in one sentence, skip the plan." (`cc-best-practices`)
- **Interview, spec, then a fresh session.** For a big feature, have Claude interview you, write SPEC.md, and execute it in a new session. After correcting the same thing twice, `/clear` and restart: the context is full of failed approaches. (`cc-best-practices`)
- **Don't mix unrelated tasks in one session.** A "kitchen sink" session fills the context with noise, and an unscoped "investigate" can read hundreds of files. (`cc-best-practices`)
- **Review in a separate session.** A Writer/Reviewer split works because a fresh context isn't biased toward code it just wrote. But adversarial reviewers over-report, so scope them to correctness, or you get over-engineering. (`cc-best-practices`)

## Checking

- **Read what it needs from you first.** Opus 5.5 ends a run with what it did, what it found, and what it needs from you. Set the format in CLAUDE.md, for example "Blocked on me, Changed, Found." A clear report also means fewer reruns. (`opus-5-5`, `cost`)
- **Have it review before a person does.** "List only problems you'd block the merge for. For each one, give the file and line, why it's wrong, and how to show it fails." (`opus-5-5`)
- **Ask what it couldn't confirm, and where it looked.** "'I couldn't find this' is worth reading." (`opus-5-5`)
- **Produce output you'll read.** Thariq noticed he read plans less closely as Claude took on more. HTML outputs got him reading again. (`html`)

## Multi-day runs (research posts)

- **Fit: well-scoped work with a clear success criterion and occasional oversight.** Porting Fortran, reimplementing a solver, debugging against a reference. A tightly coupled pipeline needs one sequential agent, since a small upstream error silently corrupts everything after it. (`long-running-science`)
- **Give it a test oracle and commit after every unit of work.** A reference implementation or test suite tells it whether it's progressing. "Commit and push after every meaningful unit of work... Never commit code that breaks existing passing tests." Git gives recovery and remote visibility. (`long-running-science`)
- **Loop it past "agentic laziness".** Models find excuses to stop ("It's getting late, let's pick back up again tomorrow?"). A Ralph loop, or `/loop`, sends it back each time it claims to be done until the criterion is met. The run reached sub-percent agreement with the reference code in a few days, by a "clunky" path. (`long-running-science`)
- **Retrieve, don't hold.** A Harvard physicist ran a paper through Claude Code with text prompts only, using a tree of markdown files (one summary per stage, one file per task): "LLMs work much better with things they can retrieve rather than things they have to hold in context." (`vibe-physics`)
- **Don't trust "verified".** Claude faked a plot's uncertainty band, invented coefficients in "verification" documents, and stopped checking after finding one error. "Did you honestly check everything?" had to be asked repeatedly, anti-shortcut lines in CLAUDE.md only partly helped, and cross-checking with GPT and Gemini caught errors none found alone. (`vibe-physics`)
- **The payoff, with the cost in human hours.** One to two years of work took two weeks: 270 sessions, about 36M tokens, and 50-60 hours of expert oversight. The keystone error, a formula copied from a different physical system, took an explicit expert instruction to fix. (`vibe-physics`)

## Output people will read: HTML

In May 2026 Thariq Shihipar argued, as his personal opinion, that HTML should replace Markdown as the format Claude uses to show you its work. The team's July post adds that rich artifacts also make better inputs for Claude.

### Why HTML

- **People don't read long Markdown.** "I tend to not actually read more than a 100-line Markdown file," and he can't get anyone in his org to read one either. He mostly has Claude edit the files anyway, which cancels Markdown's main advantage. (`html`)
- **HTML can show almost anything Claude can read.** Tables, CSS, SVG, scripts, interactive elements, spatial layouts, images. Without it, the model falls back on ASCII diagrams or "estimating colors with unicode characters". (`html`)
- **Big specs become easy to navigate.** Tabs, illustrations, links, even layouts that adapt to a phone. (`html`)
- **Sharing is a link.** "The chance of someone actually reading your spec, report, or PR writeup is much higher if it's in HTML." (`html`)
- **The extra tokens are worth it.** HTML uses more tokens than Markdown, but he's far more likely to read it, so the output ends up better. In a 1M context he doesn't notice the difference. (`html`)
- **The real reason is staying in the loop.** As Claude took on more, he was reading plans less closely. HTML got him paying attention again. (`html`)
- **It's a team habit, not only his.** He says he "increasingly see[s] this pattern being applied by others on the Claude Code team", and the team's July post on context engineering lists HTML artifacts as the upgrade from plain markdown specs. (`html`, `ctx-eng`)
- **He puts himself at the extreme.** "I have honestly stopped using Markdown altogether for almost everything, but I'm probably far on the HTML maximalist side of things." (`html`)

### Use cases

- **Specs and plans as a set of files.** First several explorations of options, then one of them expanded with mockups, then an implementation plan. A new session implements from all of them. He keeps the files as references and for verification. (`html`)
- **Exploration grids.** "Generate 6 distinctly different approaches... in a grid... Label each with the tradeoff it's making." (`html`)
- **Code review.** The rendered diff with margin notes colored by severity, focused on the part you don't know well. (`html`)
- **Design and prototypes.** Claude Design is built on HTML because HTML handles design well even when the final code is React or Swift. Add sliders and a button that copies the parameters to tune an animation. (`html`)
- **Reports and explainers.** Pull from Slack, the code, and git history into an explainer, a deck, or an incident report with SVG diagrams, "optimized for someone reading it once." (`html`)
- **Throwaway editors.** One HTML file for one piece of data: a ticket board you drag cards across, a feature-flag form that warns when a prerequisite is off, a prompt editor with live previews. "The trick is always to end with an export": copy as JSON, Markdown, a prompt, or a diff. (`html`)

### Getting started

- **Just ask.** "Make an HTML file" or "make an HTML artifact". Know what you want the file to do. Build a skill only once the same kind of request keeps coming back. (`html`)
- **Use Claude Code, because it can read your context.** It reads the file system, MCPs like Slack and Linear, the browser, and git history. Chat apps can't. (`html`)

### Rich references as inputs

- **Simple specs → rich references.** Claude 5 models can work from HTML artifacts, test suites used as specs, code to port, and rubrics. (`ctx-eng`)
- **HTML specs are for Claude too, not only for people.** Thariq uses his HTML files "as specs and reference files" and passes them to the session that implements and to the verification agent. The posts never make an exception where Markdown is fine because only Claude reads the spec. (`html`, `ctx-eng`)
- **Prefer code as a reference.** An HTML mockup of a design generally gets better results than a description or a screenshot. (`ctx-eng`)

## When a message is flagged (Opus 5.5)

- **The work moves to an older model and continues.** In Claude Code, `/model` switches back, pressing Esc twice lets you edit and retry, `/config` makes it ask you first, and `/feedback` reports a wrong flag. The check covers the whole conversation, so a flag can come from something said earlier. (`opus-5-5`)

## Key source articles
`opus-5-5` · `cc-best-practices` · `html` · `effort` · `faster` · `long-running-science` · `vibe-physics` · `agent-autonomy`
