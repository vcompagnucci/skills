# Measurement and hill climbing

In September 2026 the team published how it made claude.ai about 3× faster in two weeks. The lesson they draw: once Claude can measure something, it can improve it, so most of the work is finding things to measure.

## The result

- **Four user journeys, thirteen measurements, at the 75th percentile.** A fresh claude.ai load went from 3.1s to 0.55s. A new Claude Code session went from 0.8s to 0.3s. A Cowork cloud session went from 2.6s to 0.73s. Across all thirteen, about 3.1× faster (geometric mean). More than 3,000 changes shipped with no incident or rollback reaching customers. (`faster`)
- **Claude picked the journeys.** Through the Datadog MCP it found four journeys that make up 95% of activity and estimated each project's gain in milliseconds. The targets came from those estimates, and 12 of 13 were met by day three. (`faster`)

## The main lesson

- **With Claude, measuring something makes it tractable.** Measurement used to come first and slow: add a metric, wait for data. With Claude it's the first step of the climb. So the most useful work is finding more things to measure. (`faster`)
- **Anything you can count, Claude can drive down.** Even frame times while text streams. Stepping headless Chrome at exactly 120Hz made "did this frame fit in 8.33ms" an exact question. About 60 PRs later, long replies blocked the main thread for about 200ms instead of 750ms and held 120fps. (`faster`)

## Good benchmarks

- **In the lab, deterministic counts beat wall-clock time.** Valgrind instruction counts under `node --predictable`, React commits per interaction, V8 call counts, style recalculations, DOM mutations. (`faster`)
- **Prove the count tracks what users feel.** On two hot paths, cutting instructions by 48% and 31% cut wall-clock time by 78% and 44%. Benchmarks that were flaky or didn't track user latency were removed "rather than let Claude climb the wrong hill". (`faster`)
- **Every benchmark is also a ratchet.** A CI ceiling that only goes down, lowered by a daily job. (`faster`)
- **Build the telemetry the standard metrics don't have.** Cumulative Layout Shift scored each shift at about 0.008, far under the 0.1 threshold. Tagging each Layout Instability entry with the page region it came from showed that 31% of page loads moved something after the page was usable. (`faster`)

## The loop

- **Each thread ran the same way.** A person opens a thread with a screen recording. Claude traces the problem and builds a benchmark. It opens several PRs sized for review, with anything users can see behind a flag. It watches the deploy and the field data. If it got faster, it lowers the ratchet. If not, it turns the flag off and tries again. Then it looks for the next slow spot. (`faster`)
- **Scale by opening more threads.** More than 150 ran at once, and a single thread could produce 50 to 100 PRs. Over time Claude opened threads itself, from nightly jobs. (`faster`)
- **Standing instructions set the job.** Watch deploys, keep telemetry and dashboards accurate, fix problems proactively, propose projects, and "become as autonomous as possible". (`faster`)

## What measuring found

- **6,900 hooks and 900 store subscriptions** re-rendering on every keystroke in the input box. (`faster`)
- **One `:root:has()` selector** adding 24ms to every DOM change. (`faster`)
- **A leftover `location.reload()`** causing half a million hidden reloads a day. (`faster`)
- **Em dashes.** Any character outside Latin-1 made V8 store the whole reply as UTF-16, which put every syntax-highlighting regex on its slow path. A 20-line fix copies code blocks into one-byte strings first. (`faster`)
- **An edge case in Chrome's prerendering.** The input box dropped 10px on new tabs because Chrome's 56px managed-browser footer disappeared after the first paint. Claude measured 0px on all 49 of the reporter's loads that day, found the cause, and pinned the layout. (`faster`)

## People steer

- **Ambition, taste, and direction stay with people.** Push Claude past its cautious default ("please be braver"). A named owner decides every tradeoff users would notice. Keep threads narrow and close them when the gains get small. (`faster`)

## Key source articles
`faster`
