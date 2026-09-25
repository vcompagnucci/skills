# Effort

What the effort setting really does and when to spend it. Thariq Shihipar's September 2026 post tests it on real builds and Terminal-Bench 3.0; Addy Osmani's cost post prices it.

## What effort is

- **An approximation of how much compute you want spent.** Like being told to do something in 12 hours versus 1: higher effort means more independent action for judgment and verification. (`effort`)
- **It mostly changes thinking, and thinking bills as output.** That's why it moves the bill so much; at lower effort the model also makes fewer, shorter tool calls. (`cost`)
- **Opus 5.5 always thinks.** Delete "think carefully" / "think step by step"; say "Answer directly" for quick answers, or change effort. (`opus-5-5`)
- **Levels aren't comparable across models.** Opus 5.5 thinks more per level than Opus 5, most at xhigh and max, and defaults to medium (Opus 5 defaulted to high). Don't carry a level over. (`cost`)
- **Curves are monotonic.** On Fable 5.1 and Opus 5.5 each level adds score and tokens. (`effort`)

## What more effort buys

- **Thoroughness on hidden edge cases.** `html-js-filter` (HTML sanitizer): Fable 5.1 1/5 at low → 5/5 at xhigh. Low wrote a filter in one pass and tested one page (~2 min); high adversarially reviewed its draft, read the parser's source, ran an XSS suite, and wrote a fuzzer (~33 min). (`effort`)
- **What a careful engineer does.** `mvcc-lsm-compaction` 0/5 → 4/5: reproduced the crash first, randomized test against a never-compacting reference, checked tests fail on half-fixes. `cli-2ph-simplex` 0/5 → 5/5: brute-force oracle and timing big cases. `gsea-proteomics` 0/5 → 4/5: tried two data preps and investigated why results diverged. (`effort`)
- **It doesn't fix a wrong approach.** Fable 5.1 low → max over 370 attempts: passes 140 → 214, "a bug its tests missed" 40 → 14, but "picked the wrong reading" 25 → 47. (`effort`)
- **Domains differ.** Fable 5.1 low → top: Security 64 → 87%, Hardware 34 → 75%, ML 54 → 73%, Science 41 → 61%, Software 43 → 56%, Media 18 → 30%, Operations 12 → 22% ("rulebook-style work stays low"). (`effort`)
- **More effort also means more assumptions on your behalf.** Underspecified fitness app: low = log + graph; max adds a heat chart. With a detailed spec, outputs converge across levels. (`effort`)
- **Without a user in the loop, high effort substitutes for asking.** (`effort`)

## Choosing a level

- **Thariq's rule of thumb.** Low: in-the-loop brainstorming, sketching, easy changes. Medium: most regular SWE. High: verification matters or edge cases, e.g. a brownfield bug. Max: fully autonomous hard problems, security in critical software. (`effort`)
- **Addy's rule of thumb.** Medium for well-scoped daily work; high when medium stalls; low for mechanical work (renames, known patterns); xhigh/max only where you've measured a gain. (`cost`)
- **The price of high.** ~20K extra thinking ≈ $0.40 on Opus 5.5 ≈ a ten-turn retry; it pays for itself if it saves one retry and is wasted if medium would have finished. (`cost`)
- **The "one layer" sign.** A renamed API field: medium fixes the handler, tests pass, the client still sends the old field; high reads call sites first. But a test through the client catches it at medium for one turn: check for checks before raising effort, and move to a bigger model last. (`cost`)
- **Change it mid-session.** `/effort high`, `/effort status`; keeps the cache on API key or subscription, clears it on Bedrock, Google Cloud, or gateways. (`cost`, `effort`)

## Tension across posts

- **Implementation effort: low or medium?** Thariq implements new features on *low* after an interview spec, then verifies on high (`effort`); Addy starts well-scoped work at *medium* (`cost`). Both are the authors' own habits.
- **Review effort.** Code review is listed among domains where extra effort helps (`effort`), yet one tester found Opus 5.5 at its *lowest* effort caught more bugs than Opus 5 at high (`opus-5-5`) — a cross-model comparison, not a claim that low beats high.

## Key source articles
`effort` · `cost` · `opus-5-5`
