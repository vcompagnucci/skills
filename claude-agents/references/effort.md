# Effort

What the effort setting does and when to spend it. Thariq Shihipar's September 2026 post tests it on his own builds and on Terminal-Bench 3.0. Addy Osmani's cost post puts a price on it.

## What effort is

- **How much compute you want spent.** Compare being asked to do something in 12 hours with being asked to do it in 1. At higher effort Claude acts more on its own judgment and verifies more. (`effort`)
- **It mostly changes thinking, and thinking bills as output.** That's why it moves the bill so much. At lower effort the model also makes fewer and shorter tool calls. (`cost`)
- **Opus 5.5 always thinks.** Delete "think carefully" and "think step by step". For a quick answer, say "Answer directly", or change effort. (`opus-5-5`)
- **The same level means different things on different models.** At each level Opus 5.5 thinks more than Opus 5, most of all at xhigh and max. It also defaults to medium, where Opus 5 defaulted to high. Don't carry a level over from an older model. (`cost`)
- **Each level buys more.** On Fable 5.1 and Opus 5.5, every step up adds both score and tokens. (`effort`)

## What more effort buys

- **Care on tasks with hidden edge cases.** On `html-js-filter`, an HTML sanitizer, Fable 5.1 went from 1/5 at low to 5/5 at xhigh. At low it wrote a filter in one pass and tested it on one page, in about 2 minutes. At high it reviewed its own draft adversarially, read the parser's source, ran an XSS suite, and wrote a fuzzer, in about 33 minutes. (`effort`)
- **What a careful engineer would do.** On `mvcc-lsm-compaction` (0/5 to 4/5) it reproduced the crash first, tested against a reference that never compacts, and checked that its tests fail on half-finished fixes. On `cli-2ph-simplex` (0/5 to 5/5) it checked its solver against a brute-force one and timed large cases. On `gsea-proteomics` (0/5 to 4/5) it tried two ways of preparing the data and looked into why the results differed. (`effort`)
- **It doesn't fix a wrong approach.** Across 370 Fable 5.1 attempts, going from low to max raised passes from 140 to 214 and cut "a bug its tests missed" from 40 to 14. "Picked the wrong reading" went up, from 25 to 47. (`effort`)
- **Some fields gain more than others.** Fable 5.1 from low to top effort: Security 64% to 87%, Hardware 34% to 75%, ML 54% to 73%, Science 41% to 61%, Software 43% to 56%, Media 18% to 30%, Operations 12% to 22%. The post's label for the last one: "rulebook-style work stays low". (`effort`)
- **More effort also means more decisions made for you.** Asked for a fitness app with no details, low effort built a log and a graph, and max added a heat chart. With a detailed spec, every level produced similar apps. (`effort`)
- **With no user to ask, high effort does the asking's job.** (`effort`)

## Choosing a level

- **Thariq's rule of thumb.** Low for brainstorming, sketching, and easy changes while you're in the loop. Medium for most regular software work. High when verification matters or there are edge cases, like a bug in an old codebase. Max for hard problems Claude solves on its own, like security work on critical software. (`effort`)
- **Addy's rule of thumb.** Medium for well-scoped daily work. High when medium stalls. Low for mechanical work like renames and known patterns. Xhigh and max only where you've measured a gain. (`cost`)
- **What high costs.** About 20K extra thinking tokens is about $0.40 on Opus 5.5, the same as a ten-turn retry. It pays for itself if it saves one retry, and it's wasted if medium would have finished. (`cost`)
- **The "one layer" sign.** Rename a field in an API handler. At medium, Claude fixes the handler, the tests pass, and the client still sends the old field. At high, it reads the other call sites first. A test that goes through the client catches the same bug at medium, for one turn. So look for a check before raising effort, and move to a bigger model last. (`cost`)
- **You can change it mid-session.** `/effort high` sets it and `/effort status` shows it. It keeps the cache on an API key or a subscription and clears it on Bedrock, Google Cloud, or a gateway. (`cost`, `effort`)

## Where the posts disagree

- **Low or medium for implementation?** Thariq implements new features at *low* once Claude has interviewed him for a spec, then verifies at high (`effort`). Addy starts well-scoped work at *medium* (`cost`). Both are the authors' own habits.
- **Effort for code review.** Thariq lists code review among the fields where extra effort helps (`effort`). One of Addy's testers found Opus 5.5 at its *lowest* effort caught more bugs than Opus 5 at high (`opus-5-5`). That compares two models. It doesn't say low beats high.

## Key source articles
`effort` · `cost` · `opus-5-5`
