# Cost and model choice

What a Claude Code task actually costs and which settings change it. The frame, from Addy Osmani's September 2026 post: you buy finished tasks, not tokens. Numbers are Opus 5.5 API list prices and the post's own illustrations; they date quickly.

## You pay per task

- **Same token price, different task cost.** Each turn resends the conversation, so the model that needs more turns costs more. "The cheapest turn is the one you don't need." (`cost`)
- **Every saving risks a retry.** Lower effort, a smaller model, or less context all save tokens, and "a retry costs more than those savings". (`cost`)
- **Four levers.** Turns, cache reads, output tokens (thinking bills as output, 5× input), and model. On Opus 5.5 an output token costs 100× a cache read: 60K output = $1.20 = 6M cache reads. (`cost`)
- **Turn math.** A task growing 20K → 120K context over 40 turns sends ~2.8M input (~$1.62 at 90% cache); the same task in 25 turns ~$1.02. (`cost`)
- **Fewer turns come from checks and batching.** A test, build, or script lets the model find mistakes earlier; gathering what it needs in one pass pays the resend fewer times. (`cost`)

## Opus 5.5 pricing (Sep 2026)

- **$4 in / $20 out / $0.20 cache read per million.** Input and output 20% cheaper than Opus 5, cache reads 60% cheaper; plan limits go ~25% further. (`cost`)
- **"40% cheaper" is a workload estimate, not a token price.** It assumes fewer tokens per task at the medium default; price alone takes an illustrative session from $3.50 to $2.40 (−31%). (`cost`)
- **Well-scoped tasks get the price cut; open-ended ones may gain more.** Fewer turns spent on the wrong idea. (`cost`)

## Three models a day

- **Haiku or Sonnet for lookups.** Search and summarize subagents, logs, test output, "where is this defined" — work where a mistake is cheap to spot. A misread search result sends the main model on a paid detour. (`cost`)
- **Opus 5.5 as daily driver.** Supervised feature work, debugging, review with follow-up edits; mechanical multi-file edits stay on Opus 5.5 at low effort. (`cost`)
- **Fable 5.1 when the result matters more than price.** Unsupervised long runs, problems with no existing pattern, large multi-subagent changes; if Opus 5.5 on xhigh hits the same problem twice, switch, then switch back. $10 / $50, cache reads $0.25 (only 1.25× Opus 5.5's), so the gap is smallest on cache-heavy runs. (`cost`)
- **Raise effort before changing models.** Effort costs less than a bigger model; a fix that stops at one layer is the sign (see `effort.md`). (`cost`)
- **Subagent model settings.** `model: haiku` in a definition, or `CLAUDE_CODE_SUBAGENT_MODEL` for all; unset subagents inherit the main model and its price. (`cost`)
- **Agent teams ≈ 7× tokens** in plan mode; keep them small and shut teammates down. (`cost`)

## Switching models: the position moved

- **April: don't switch mid-session.** Caches are per model; use subagents with a hand-off message. (`caching`, 2026-04-30)
- **September: switch at a natural break when the task justifies it.** Accept one cache write on the new model; shrink it with `/compact` or a fresh session with a short written plan; `/model` also sets the default for new sessions, so switch back. (`cost`, 2026-09-25, later)
- **Opusplan contradicts the edits-on-Opus advice.** Opus plans and Sonnet edits; "measure it on your own tasks before you make it a default". (`cost`)

## Other bill lines

- **Fast mode:** up to 2.5× faster at 2× price; first request pays uncached, so enable at session start. (`cost`, `opus-5-5`)
- **Batch API:** half price. **Typical spend:** ~$13 per developer per active day; 90% under $30. (`cost`)

## Measure it yourself

- **Read `/usage` for three things.** Cache share (low → pause, model switch, MCP change); output vs input (high → effort too high or retries); total input vs conversation size (many × → loops worth reading). (`cost`)
- **Run the same real task on both models, 3–4 times, before concluding.** "Your own numbers are the ones to trust." (`cost`)

## Key source articles
`cost` · `caching` · `opus-5-5`
