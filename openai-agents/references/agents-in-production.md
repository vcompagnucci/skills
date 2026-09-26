# Agents in production

What OpenAI teams, their customers and guest authors learned putting agents into real work: case studies with a build lesson, how humans steer, delegate to and review agents, voice agents, and when an agent should hand back to a person. Most sources are first-person engineering posts, so the numbers are self-reported and rarely controlled. Guest posts (Dagster, Skyscanner, Alpic, Perplexity) are one team's experience.

## Case studies with a build lesson

- **A small team plus agents shipped faster than hiring would have.** Four engineers built Sora for Android with Codex in 28 days (internal build in 18, public launch 10 days later), about 5 billion tokens, 99.9% crash-free, and an estimated 85% of the code written by the agent. (`sora-android`)
- **Treat the agent like a new senior hire: strong executor, weak on the unstated.** It doesn't infer architecture preferences, product strategy or team norms, and left alone it adds an extra view model or pushes logic into the UI to get something working. "Build the app from the iOS code. Go" technically worked, felt sub-par and was aborted. Humans built the foundation and a few representative features by hand, then pointed the agent at them: "use the same patterns as this other screen" worked far better than a description. (`sora-android`)
- **Zero hand-written code is feasible with enough scaffolding.** One internal team produced about a million lines and roughly 1,500 merged PRs in five months with three engineers (later seven), at an estimated tenth of the time. The authors warn this won't generalize without similar investment. (`harness-eng`)
- **Agents copy existing patterns, including bad ones, so run cleanup continuously.** Spending every Friday on cleanup didn't scale. Encoded "golden principles" plus recurring background agents now scan for drift and open small refactor PRs, most reviewable in under a minute. (`harness-eng`)
- **Production breaks in ways a lab doesn't predict, so stay close to the practitioners.** Early tax-agent corrections lacked context, and engineers couldn't tell an extraction miss from workflow noise. Practitioners now decide which errors matter and steer through work they already do. The pilot processed 7,000 returns, saved about a third of prep time and took one accountant from 180 to 15 hours. (`tax-agents`, `codex-platform`)
- **The first hard domain pays for the next ones.** Rental properties took about six weeks of heavy oversight to reach 90% precision and recall, and left abstractions and eval conventions that sped up other schedules. (`tax-agents`)
- **At scale the hard part is picking the right data, not writing the query.** OpenAI's data agent serves 3.5k internal users over 70k datasets full of near-duplicate tables, where a bad join or unhandled null silently invalidates a result. Recurring analyses were packaged as reusable workflows only after usage showed repetition. (`data-agent`)
- **Measure an agent by the user steps it removes.** Arcade turned screen recordings into structured steps and narration, and median actions before publishing a demo fell 50%. Collxn found tool calls against a live catalog API simpler than building a retrieval pipeline. (`responses-year`)
- **Good delegated tasks are unglamorous.** At DevDay, fragmented launch docs from three tools were handed off with a rough description and came back as a restructured PR. At Dagster, agents explain a PR to keep docs current and translate one tutorial into a video script or blog post. (`codex-devday`, `dagster-docs`)
- **For work judged by feel, brief the experience and let the agent propose the architecture.** "Everything I can see should be reachable" ruled out painted stars, and the agent chose the stack. Approved reference images became the target for each phase. (`astra-games`)

## Humans working with agents

- **Queue by default, steer when the wrong path is getting expensive.** A queued follow-up waits for the turn to end, a steer injects guidance mid-turn. Accidental mid-turn redirection usually costs more than waiting. (`codex-remote`)
- **Choose the execution context before the first prompt.** Host, base branch and fresh worktree versus current checkout: "10 seconds choosing ... save 10 minutes of cleanup." Attach the screenshot or file that removes ambiguity up front. (`codex-remote`)
- **Keep side questions out of the thread that owns the work.** A side chat seeded from selected transcript text answers questions without pulling the agent off its objective. Fork instead when the objective itself diverges. (`codex-remote`)
- **A small review loop is often enough.** Many reviews are blocked on one or two decisions: leave two inline comments, the agent addresses them in the same chat, review the smaller diff. (`codex-remote`)
- **Put the artifact in the loop.** Human and agent inspect the same object, and comments on it become instructions. A single HTML file is often enough as a live review surface. (`codex-maxxing`)
- **Agent review can own correctness, humans own choices.** Required agent review of bugs, regressions and missing tests was "safe enough in practice". Humans stay essential for choosing among valid designs, compatibility, rollout, naming and cross-team sequencing. (`skills-oss`)
- **High throughput flips merge norms.** With agents opening most PRs, one team moved to minimal blocking gates and mostly agent-to-agent review: "corrections are cheap, and waiting is expensive." They call this irresponsible in a low-throughput setting. (`harness-eng`)

## Voice agents

- **Shadow-test on real traffic before users hear it.** Read-only live sessions showed that capacity means concurrent sessions kept on schedule, not GPU throughput, and that long sessions and reconnects exposed bugs short load tests missed. Rewriting the media path in Go made the new p95 match the old p50. (`gpt-live`)
- **Tune for the messy environment first and give users a turn-taking override.** A noisy bar was a test case. Thinking pauses read as end of turn, so a "voice lock" lets the user hold the floor. (`perplexity-voice`)

## Human intervention and escalation

- **Escalate on two triggers.** Hand control to a human when failure thresholds are exceeded or when an action is high-risk and irreversible. (`practical-guide`)
- **Route ambiguous cases back to people instead of forcing them through the loop.** Automation in the tax agent is limited to extraction and mapping, engineers own architecture and shipping. (`tax-agents`)
- **Ask when unclear, default when unanswered, accept interruption.** With no date range, the data agent assumes the last 7 or 30 days to stay non-blocking. (`data-agent`)

## Where the posts disagree

- **Short prompts or careful setup?** The DevDay post (`codex-devday`, 2025-10-10) fired off tasks described in short sentences. The Sora post (`sora-android`, 2025-12-12) found a one-line brief produced a sub-par app and relied on hand-built foundations, examples and co-written plans. The difference is likely task size: isolated tasks versus a whole product.
- **How much review to keep?** `harness-eng` (2026-02-11) moved to minimal gates and agent-to-agent review at high throughput. `codex-maxxing` (2026-06-22) and `skills-oss` (2026-03-09) keep humans on approvals, irreversible actions and design choices.

## Key source articles
`sora-android` · `harness-eng` · `tax-agents` · `codex-remote` · `codex-maxxing` · `gpt-live` · `perplexity-voice` · `chatgpt-apps-lessons` · `data-agent`
