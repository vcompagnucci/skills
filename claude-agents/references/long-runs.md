# Prompting and steering long runs

How to hand work to Claude when a run can last hours, and how to stay in control while it runs. Mostly from Addy Osmani's Opus 5.5 guide, plus Thariq Shihipar's habits from the effort and HTML posts.

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
- **Keep the task list in a file.** "Keep a checklist in TASKS.md." The file survives summarization, and you can read it instead of scrolling back. Claude Code's own todo tool moved to a shared Task tool so subagents could coordinate (`seeing`). The file is for you and for surviving compaction. (`opus-5-5`)
- **Split big audits and migrations across subagents, and check each one's evidence.** End with one table. (`opus-5-5`)
- **In long chats, say earlier answers are settled.** Opus 5.5 sometimes goes back over earlier answers when you ask a short follow-up, which slows it down. Skip this in long analysis, where a later step can expose an earlier mistake. (`opus-5-5`)
- **Push it to aim higher.** By default Claude keeps scope small. It files tickets for what it finds, hedges, and pads its estimates. The performance team told it "please be braver" and "the targets are not the stopping point." (`faster`)
- **People keep taste and direction.** Decide the tradeoffs users will notice, from before-and-after recordings. Keep each thread narrow. Reject complexity that isn't worth it, as in "2ms per send is not worth the complexity". (`faster`)

## Checking

- **Read what it needs from you first.** Opus 5.5 ends a run with what it did, what it found, and what it needs from you. Set the format in CLAUDE.md, for example "Blocked on me, Changed, Found." A clear report also means fewer reruns. (`opus-5-5`, `cost`)
- **Have it review before a person does.** "List only problems you'd block the merge for. For each one, give the file and line, why it's wrong, and how to show it fails." (`opus-5-5`)
- **Ask what it couldn't confirm, and where it looked.** "'I couldn't find this' is worth reading." (`opus-5-5`)
- **Produce output you'll read.** Thariq noticed he read plans less closely as Claude took on more. HTML outputs got him reading again. (`html`)

## When a message is flagged (Opus 5.5)

- **The work moves to an older model and continues.** In Claude Code, `/model` switches back, pressing Esc twice lets you edit and retry, `/config` makes it ask you first, and `/feedback` reports a wrong flag. The check covers the whole conversation, so a flag can come from something said earlier. (`opus-5-5`)

## Key source articles
`opus-5-5` · `effort` · `faster` · `html`
