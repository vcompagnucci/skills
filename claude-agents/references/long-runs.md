# Prompting and steering long runs

How to hand work to Opus 5.5-era Claude and stay in control while it runs for hours. Mostly Addy Osmani's Opus 5.5 guide, with Thariq Shihipar's habits from the effort and HTML posts.

## Asking

- **Give the whole task in one message with a finish line.** "Done means: every endpoint uses the new client, the old client is deleted, and the test suite passes. Stop and ask me only if a test fails for a reason you can't explain." Opus 5.5's biggest gains are multi-step work; early testers ran it for hours with little oversight. (`opus-5-5`)
- **Don't tell it to think.** It always does; removing "think carefully" made replies start sooner with no clear quality drop. (`opus-5-5`)
- **Name the design defaults you don't want.** "Avoid a generic look" swaps one default for another; list the patterns (cream backgrounds, italic accent words, "01 / 02 / 03" labels, monospace labels, pill buttons), see what it picks instead, add that too. (`opus-5-5`)
- **Have it interview you first.** Thariq's feature loop: spec → Claude interviews you about missing details → implement (low) → review → verify (high). With a detailed spec, results barely depend on effort. (`effort`)
- **Share the artifact, not a retyping.** Attach charts, screenshots, and diagrams; Opus 5.5 reads spatial meaning (which boxes an arrow connects). Ask for the finished file, not an outline. (`opus-5-5`)
- **Don't ask it to show its internal reasoning in the reply.** It's a flag category; ask "Explain why you chose this approach in three sentences." (`opus-5-5`)

## Steering

- **Name the stops in CLAUDE.md.** Long runs sometimes pause to report, offer to continue, or list non-blocking choices. Tell it to keep going when a step doesn't need you, put status notes in the same message as the next action, and stop only when blocked or before destructive actions. Keep permission prompts on. For pair programming, ask for the opposite. (`opus-5-5`)
- **Add to a running task instead of restarting.** Type a follow-up and press Enter while it works; restarts cost more on long runs. (`opus-5-5`)
- **Keep the task list in a file.** "Keep a checklist in TASKS.md." It survives summarization and you read the file, not the scrollback. (`opus-5-5`) — Contrast: Claude Code's own tool moved from TodoWrite to a shared Task tool for subagent coordination (`seeing`); the file is for the human and for compaction.
- **Split big audits and migrations across subagents and check each one's evidence.** Finish with one table. (`opus-5-5`)
- **Settle earlier answers in long chats.** Opus 5.5 sometimes re-examines earlier answers on short follow-ups; say they're done — except in long analysis, where later steps can expose earlier mistakes. (`opus-5-5`)
- **Push for ambition.** Claude defaults to careful scope: it tickets findings, hedges, pads estimates. "Please be braver"; "the targets are not the stopping point." (`faster`)
- **Humans keep taste and direction.** Rule on user-perceptible tradeoffs from before/after recordings; keep threads narrow; reject complexity that isn't worth it ("2ms per send is not worth the complexity"). (`faster`)

## Checking

- **Read what it needs from you first.** Opus 5.5 closes with what it did, found, and needs; format it in CLAUDE.md, e.g. "Blocked on me, Changed, Found." Clear reports also mean fewer reruns. (`opus-5-5`, `cost`)
- **Review before a human does.** "List only problems you'd block the merge for. For each one, give the file and line, why it's wrong, and how to show it fails." (`opus-5-5`)
- **Ask what it couldn't confirm and where it looked.** "'I couldn't find this' is worth reading." (`opus-5-5`)
- **Make outputs you'll actually read.** Thariq noticed he was reading plans less closely as Claude took on more; HTML outputs pulled him back in. (`html`)

## When a message is flagged (Opus 5.5)

- **Flagged work moves to an older model and continues.** In Claude Code: `/model` to switch back, Esc twice to edit and retry, `/config` to be asked first, `/feedback` for wrong flags. The check covers the whole conversation, so a flag can come from earlier content. (`opus-5-5`)

## Key source articles
`opus-5-5` · `effort` · `faster` · `html`
