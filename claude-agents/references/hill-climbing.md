# Measurement and hill climbing

The September 2026 case study of making claude.ai ~3x faster in two weeks, and the general lesson it draws: once Claude can measure something, it can improve it, so the work becomes finding things to measure.

## The result

- **Four journeys, thirteen measurements, p75.** Fresh claude.ai load 3.1s → 0.55s; new Claude Code session 0.8s → 0.3s; Cowork cloud session 2.6s → 0.73s; ~3.1× geometric mean. 3,000+ changes, no customer-facing incident or rollback. (`faster`)
- **Claude picked the journeys.** Via the Datadog MCP it found four journeys covering 95% of activity, estimated each project's impact in milliseconds, and targets came from those estimates; 12 of 13 were hit by day three. (`faster`)

## The central lesson

- **With Claude, measuring something makes it tractable.** Measurement used to be step zero (add a metric, wait for data); with Claude it's step one of the climb. The highest-leverage work is finding more things to measure. (`faster`)
- **Anything countable can be climbed.** Even frame times during streaming: deterministic 120Hz stepping in headless Chrome made "did this frame fit 8.33ms" exact; ~60 PRs later long replies blocked the main thread ~200ms instead of ~750ms and held 120fps. (`faster`)

## Good benchmarks

- **Deterministic beats wall-clock in the lab.** Valgrind instruction counts under `node --predictable`, React commits per interaction, V8 call counts, style recalcs, DOM mutations. (`faster`)
- **Prove the proxy tracks what users feel.** Instructions −48% / −31% on two hot paths gave wall-clock −78% / −44%; benches that were flaky or uncorrelated were unshipped "rather than let Claude climb the wrong hill". (`faster`)
- **Each benchmark is also a ratchet.** A CI ceiling that only goes down, lowered daily. (`faster`)
- **Build the telemetry standard metrics lack.** CLS scored each shift ~0.008 (well under 0.1), but mapping Layout Instability sources to named regions showed 31% of loads moved something after the page was usable. (`faster`)

## The loop

- **Per thread:** a human opens it with a recording → Claude traces and builds a benchmark → several risk-sized PRs, user-visible changes behind flags → Claude watches the deploy and field data → ratchet down, or flag off and iterate → next slow spot. (`faster`)
- **Scale horizontally by opening threads.** 150+ at once; single threads produced 50–100 PRs; Claude increasingly opened threads itself from nightly jobs. (`faster`)
- **Standing instructions set the charter.** Monitor deploys, curate telemetry and dashboards, fix proactively, propose projects, "become as autonomous as possible". (`faster`)

## What measurement found

- **6,900 hooks and 900 store subscriptions** re-rendering on every keystroke in the composer. (`faster`)
- **One `:root:has()` selector** adding 24ms to every DOM change. (`faster`)
- **A stray `location.reload()`** causing half a million hidden reloads a day. (`faster`)
- **Em dashes.** Any non-Latin-1 character made V8 store the reply as UTF-16, putting every highlighting regex on its slow path; a 20-line fix copies code blocks into one-byte strings. (`faster`)
- **A Chrome prerender edge case.** A 10px composer drop on new tabs was Chrome's 56px managed-browser footer disappearing after first paint; Claude measured 0px on all 49 of the reporter's handoffs and pinned the layout. (`faster`)

## Humans steer

- **Ambition, taste, direction.** Push Claude past cautious scope ("please be braver"); a named owner rules on every user-perceptible tradeoff; keep threads narrow and close them at diminishing returns. (`faster`)

## Key source articles
`faster`
