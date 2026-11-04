# Sources: every claim, dated

Everything Lauren Tan (@poteto) said in public about trusting agents' work, from April to November 2026. Each claim is a paraphrase, with its date and its link. Quotes are short and only where the exact words carry the rule. Talks are machine transcripts, so lines from them are close to her words, never exact.

**When two claims conflict, the newer one wins.** "Changed positions" at the end lists each conflict and the version that wins.

## Contents

- Trust is the bottleneck
- Verification closes the loop
- What counts as proof
- The verification skill
- Formal verification
- The codebase is memory
- Where a fix goes
- Comments, plans and other prose
- Skills and rules
- Loops, autonomy and review
- Changed positions

## Trust is the bottleneck

- 2026-04-25 ([post](https://x.com/poteto/status/2048092593087721736)): parallel agents pay off when they go deep on one problem (best-of-N races, adversarial review, several agents reproducing one bug, a model per workload), not when they spread across ten problems. Trust decides how far you can delegate. With little trust you micromanage every agent, like managing people.
- 2026-05-25 ([How I Use Cursor](https://x.com/poteto/status/2058975157503570132)): agents are new hires with permanent amnesia. Capable, stupid and teachable. Without rigor they write whatever you asked for, sycophantically, and parallelizing them only writes slop faster. The bottleneck is verification. A software factory needs an agent you trust to own a problem end to end, verification included. Parallelizing agents you don't trust yet wastes tokens and adds slop.
- 2026-07-29 ([post](https://x.com/poteto/status/2082555523958976848)): you can "go exponential" once you trust what your agents do.
- 2026-08-12 (Lenny/Maven workshop, transcript, 03:12–08:52 and 29:05–31:40): agents that wing it and announce the smoking gun for the hundredth time burn your trust. You can't spawn 100 agents when you don't trust the output of one. There is no shortcut up the trust curve, because it measures your own trust. Encode your engineering standards into skills, verify the agents follow them, and the curve rises.
- 2026-09-21 ([2,500-PRs talk](https://x.com/poteto/status/2102050467505430555), transcript, 04:24–06:44): her output came from moving her knowledge into the agents so she stopped being the bottleneck. Stuck at one to five agents you babysit and correct every chat. Spawning 100 without trust buys slop PRs, regressions and shipped bugs.
- 2026-10-03 ([Matt Pocock live](https://www.youtube.com/watch?v=MN9dGgmLyso), transcript, 26:11–27:44): low on the trust ladder you are stuck micromanaging and never get time to sharpen your knives. The engineer's new job is the environment.

## Verification closes the loop

- 2026-06-24 ([Loops You Can Trust](https://x.com/poteto/status/2069824386283319343)): give agents the signals a human engineer uses (compiler diagnostics, lints, static analysis, the profiler). They must see what you see and use your tools. Teach an agent to verify before you build any loop. Without that, loops compound slop and humans get more work. Verification is the limiting step: speeding up anything else doesn't deliver sooner.
- 2026-08-31 ([pstack guide Pt. 1](https://x.com/poteto/status/2094457600259842065)): with verification the agent keeps going until it succeeds and closes the loop without you as the bottleneck. The harder a stack is to debug and control, the worse agents do in it. Pick a debuggable stack, or build your own debugging tools.
- 2026-09-21 (talk, transcript, 11:54–12:42): verification gives correctness (does the feature do what it should), not performance or code quality. Quality comes from the skills and the environment.
- 2026-10-03 (Pocock live, transcript, 15:46–17:48): verification gives the agent hands and eyes. It is the part that makes a loop a loop, and it enables hill climbing against a score. Before it, she was the proxy between the agent and the result.
- 2026-10-12 ([post](https://x.com/poteto/status/2109436202554372476)): verification is the entry point, so start there. The agent runs the work like a real user, through CLI, API or UI, and produces an artifact showing (1) the work is correct, (2) it matches your intent and (3) it is easier to review than the PR. Skill packs are optional. Not every domain verifies easily yet, and verification is an approximation, no different from trusting a person who says they ran their code.
- 2026-10-12 ([post](https://x.com/poteto/status/2109699980248408574)): two things matter: a way for the agent to verify its own work, and treating the codebase as memory. Rules and skills can come later.
- 2026-10-26 ([post](https://x.com/poteto/status/2114626630429913383), recommending [Yaron Minsky's talk](https://www.youtube.com/watch?v=rUYP4C29yCw)): types are among the best feedback agents get. Make illegal states unrepresentable. Use property-based tests, fuzzing and deterministic simulation testing. Expect tests print behavior and capture it, which shrinks the review surface ([React Compiler fixtures as an example](https://x.com/poteto/status/2114630175040348590)).

## What counts as proof

- 2026-06-24 (Loops You Can Trust): "trust, but verify". "I fixed it" doesn't count. Show the failing and the passing test, the before and after video, the trace, the heap snapshot or the screenshot, and if it merged, run it again on main. An artifact beats a plausible explanation, because you can challenge it without replaying the run. Bake each such demand back into a skill.
- 2026-06-24: catch defects at the cheapest stage. A failed check on one small component is cheap, and a regression found after a giant migration is expensive. Her StyleX migration became one leaf component per PR, styles captured before and after across themes and states, and a failed build or parity check ends the run.
- 2026-09-09 ([pstack guide Pt. 2](https://x.com/poteto/status/2097732320606507506)): tests alone are not sufficient verification. Work counts as verified only once the code ran and worked. Every task in a plan is built around its proof.
- 2026-09-09: types that need escape hatches (`any`, forced casts), or one workaround repeated across unrelated call sites, are empirical proof the architecture is wrong.
- 2026-10-27 ([guide 06](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md)): "it compiles" is not evidence. Put the finish condition in the first prompt. The reply carries exact commands and outputs, says "inconclusive" when a check couldn't run, and a confident reply without evidence is a warning sign. Match the check to the change: a CLI runs the real command, a UI walks the flow in the running app, a parser replays saved input, perf compares profiles, storage reads back the written value. Vet any measured number before reporting it. The agent that judges a change is never the one that wrote it.
- 2026-10-27 ([guide 10](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/10-recipes-and-pitfalls.md)): a green build proves it compiles, nothing more. Accept review comments only once a rerun proves them, because bots and humans file real catches and noise in one list.

## The verification skill

- 2026-07-30 ([post](https://x.com/poteto/status/2082874054483255805)): a verification skill teaches the agent to run, control and debug your app, plus a feature map: every feature and how a user reaches it. The map goes stale fast, so maintain it daily. It becomes critical infrastructure for the team. One skill per product works even for huge apps, because references load on demand ([reply](https://x.com/poteto/status/2082983927137157168)). Commit it to the repo so everyone shares it ([reply](https://x.com/poteto/status/2082908778727673876)).
- 2026-07-29 ([post](https://x.com/poteto/status/2082556871358251345)): a cheap, fast model makes "verification swarms" per PR affordable.
- 2026-08-31 (Pt. 1): treat it as critical infrastructure, even worth an on-call rotation. Put a small CLI inside the skill so agents stop writing throwaway scripts (fewer tokens, reproducible, testable). Agent-friendly CLI traits: composable commands (deep modules), `--dry-run` on anything destructive, subcommands that disclose features gradually, error messages that say what to do instead, rich `--help`, machine-readable output. Make the dev setup repeatable: seeded database, test users, a staging target, one way to bring the environment up. The feature map is "materialized memory", a compact form of the codebase. Run the maintain pass at least daily. A swarm of verifiers confirms a perf win over a real sample or fuzzes the app for regressions. Once the skill is good, routines can reproduce every user report.
- 2026-08-31 (replies): when the skill says green and the product is wrong: "observe, diagnose, fix the skill" ([reply](https://x.com/poteto/status/2094505733790609505)). Agents update the feature map in the same PR that changes the app, and an automation catches what they miss ([reply](https://x.com/poteto/status/2094492951934304568)). A first run that maps only a few features needs more subagents told to find them all ([reply](https://x.com/poteto/status/2094505328796938507)).
- 2026-09-21 (talk, 08:37–11:54): the two parts are the CLI (reproducible runs and evidence) and the feature map (it turns a vague screenshot report into a feature the agent can reach).
- 2026-10-03 (Pocock live, 22:27–23:50): without the CLI every agent rebuilt the world, each differently. Ask how much of your skills and rules could be deterministic. Agents get the fuzzy parts, scripts the mechanical ones.
- Example layout: [verification-skill-example](https://github.com/poteto/verification-skill-example), one feature file per area, each with the same four sections.

## Formal verification

- 2026-09-21 (talk, 07:44–08:37): formal methods (Lean, TLA+) prove business invariants always hold. They are much harder and still an open question, and verification skills get you far without them.
- 2026-10-03 (Pocock live, 56:28–57:47): proofs and proof-carrying languages like Bend are her hope for the future. If the proofs show the code is correct, merge it.
- 2026-10-16 ([pyramid](https://x.com/poteto/status/2111133080526495985)): TLA+ verification belongs with static analysis, as a token-efficient early catch.
- 2026-10-18 ([post](https://x.com/poteto/status/2111926622278521253)): formal verification proves invariants, the laws of your system. Keeping models in sync with business rules made it hard historically. Proving the code does what you meant gives agents "superpowers". Modeling with TLA+ already found real bugs for her.
- 2026-10-21 / 10-29 ([post](https://x.com/poteto/status/2112736749281759566), [post](https://x.com/poteto/status/2115880102601101414)): draw the flow as a statechart and check it against the TLA+ model, both to understand the code and to catch bugs users would hit.
- 2026-10-27 (guide 06): pick the strongest target: a promise the code makes, costly to break and rarely reached by tests. The question picks the tool (TLA+ for event order in any language, a code-level verifier for every input). Verify one property and show it failing on a broken variant, because a check you've never seen fail proves nothing. A pass covers the model or the bound, not the whole system. Re-sync the model after merges.

## The codebase is memory

- 2026-07-18 ([post](https://x.com/poteto/status/2078527882499150286)): the style guide enforced by review is obsolete. Agent codebases need hard constraints, so even the dumbest agent contributes well. Refactoring, and a stack with strong types and diagnostics, beat AGENTS.md and skill tweaks. "the best rules are in your code".
- 2026-08-12 (workshop, 33:42–50:41): big-tech infra already caters to the least capable engineer, so agents do well there. Greenfield, vibe-coded apps have no guardrails and spiral, so start with strong constraints. Grok Bot's framework, Dune, bans `useEffect` and code comments in CI and enforces electron main/renderer import boundaries. Its key rule: "the shortest path is the best path", because agents take shortcuts. Hard layers turn CI red, and soft layers (rules, Bugbot, skills) get forgotten. A codebase guarded only by soft layers ends up as trash. Strict compilers like Rust's earn trust. Enforcing a rule by human review comment is a smell: turn it into a hard rule.
- 2026-08-16 ([reply](https://x.com/poteto/status/2089166694719922483)): "your codebase is a form of memory too".
- 2026-08-20 ([post](https://x.com/poteto/status/2090546476464451907)): every team needs a gardener who watches incoming PRs for smells (the third ad-hoc helper this week, creeping lint suppressions). Every weed pulled becomes a rule so it can't grow back. Pointer: [dmmulroy/anti-slop](https://github.com/dmmulroy/anti-slop) for opinionated TS rules.
- 2026-08-22 ([post](https://x.com/poteto/status/2091229896907595821)): without the right constraints agents cause more problems than they solve. Put scaffolding around them and they grow into the shape you want. She sees no sign smarter models make human steering unnecessary ([reply](https://x.com/poteto/status/2091245988346527790)).
- 2026-08-27 ([AMA reply](https://x.com/poteto/status/2093108757299638301)): she still reads code. Agents scan every commit for smells and shortcuts. Each finding becomes a lint rule, existing cases get fixed (agents copy what's there), or a refactor removes it. Enough guardrails and you can auto-merge. A swarm also scans commits for slop and perf regressions ([reply](https://x.com/poteto/status/2093070988074508763)).
- 2026-09-21 (talk, 15:25–30:38): agents extend whatever patterns they see, so one workaround with its explaining comment spreads like a virus into a de facto pattern within weeks. The ideal agent codebase is so locked down it annoys humans and is so conventional that even innocent patterns are forbidden. Delete existing debt, keep one paved path, and answer every bad pattern with a lint rule. The rule stops the bleeding before cleanup. Keep the code in a state you'd be happy to see copied. Move reviewers' tribal knowledge into the framework.
- 2026-10-03 (Pocock live, 27:44–31:58): constraining a codebase works like type narrowing: shrink the space until there is one way to do something. Watch how agents fail, then make each mistake a lint rule or impossible.
- 2026-10-11 / 10-12 ([post](https://x.com/poteto/status/2109356992032817621), [post](https://x.com/poteto/status/2109699980248408574)): every nit, annoyance and repeated agent mistake must become a constraint, or agents repeat it like a virus. Repeat until agents with little context one-shot high-quality PRs. Better still, make agent anti-patterns impossible: type systems, frameworks that shrink the architectural search space, or your own framework with good primitives. Engineers are the people best placed to end slop: they can shape the codebase so anyone writes good PRs ([reply](https://x.com/poteto/status/2109761952696483905)).
- 2026-10-27 ([post](https://x.com/poteto/status/2115133011352240581)): make the easy thing the right thing, and learn from each mistake so it never happens twice.
- 2026-10-30 ([post](https://x.com/poteto/status/2116191971714953262)): code now arrives as a continuous stream. Evolve systems so agents with little context thrive. The codebase is organic architecture that grows around your constraints. Design systems, frameworks and languages to control the chaos.

## Where a fix goes

- 2026-08-16 ([post](https://x.com/poteto/status/2089067865098113024)): every time you correct an agent, think how to remove the need. In order of value: (1) architecture or data structures make it impossible, (2) a lint rule or test catches it in CI, (3) a skill or rule, (4) human review ("ngmi").
- 2026-09-21 (talk, 15:25–18:50; same slide in the 08-12 workshop): codebase, static analysis, rules/Bugbot/skills, a style guide only humans enforce. A style guide left out of the other layers is a hole no reviewer can fill at agent volume.
- 2026-10-14 ([reply](https://x.com/poteto/status/2110498629307990461)): move prose into deterministic code. Lint rules, strong types and good API design beat comments, AGENTS.md, rules and skills.
- 2026-10-16 ([the pyramid](https://x.com/poteto/status/2111133080526495985)): (1) codebase improvements: architecture, stronger types and invariants, clear boundaries, so the easy thing is the right thing; deterministic, token-efficient, lets you sleep. (2) Static analysis: lint, tests, CI, TLA+. (3) Prose: comments, rules, AGENTS.md, skills, used minimally, though a verification skill is a must. (4) Human review: hardest to scale, so spend it on designing the environment. Most effort at the top. Her project prompt: mine your own review feedback and chats, recall past transcripts, run correct and architect over past commits for common pitfalls, plan a rearchitecture backed by data, answer open questions with prototypes, and restate the goal before starting.
- 2026-10-19 ([guide 09, /correct](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/09-make-it-yours.md)): repeated corrections belong in the repo, not the next prompt. Rank: (1) architecture or a better data structure makes it impossible, (2) types, or a lint or CI check whose error names the fix, (3) a test, (4) a doc or agent rule, last because nothing fails when it's skipped. "Human review isn't on the list." A class counts once it has happened twice. Each new check must fail on a real past mistake. Keep a table pairing each rule with what enforces it.
- Principle "encode lessons in structure" (pstack): a lesson that needs judgment gets a more prominent instruction plus an example of the failure. A lesson with a structural fix gets only the structural fix.

## Comments, plans and other prose

- 2026-08-03 ([post](https://x.com/poteto/status/2084151518169895147)): `/no-comments` spawns Comment Sicko to delete useless comments.
- 2026-08-12 / 09-21 (workshop and talk): agents used existing comments to justify a bandaid instead of fixing the problem, and wrote passing review remarks into code as if they were global law. Dune bans comments for that reason.
- 2026-09-09 (Pt. 2) and 09-11 ([reply](https://x.com/poteto/status/2098214871943033209)): delete plans after the work, and commit one temporarily only for a week-long project. ADRs in the repo are noise for agents. Keep them elsewhere unless they help agents decide.
- 2026-10-13 ([post](https://x.com/poteto/status/2110149626133438732)): delete most comments. A harmless note about a temporary workaround spreads like a weed. Keep the ones that must exist (a browser quirk) and solve the rest from first principles.
- 2026-10-14 (replies): turn architectural rules into lint rules, or types with one way to do it ([reply](https://x.com/poteto/status/2110205947079721252)). Solve API drift with codegen (tRPC, gRPC). Well-thought-out code needs no explaining comment ([reply](https://x.com/poteto/status/2110206120287785088)). Comments about what is outside your control stay ([reply](https://x.com/poteto/status/2110206854920077651)). Discuss user-facing ones first ([reply](https://x.com/poteto/status/2110206498697834793)).
- 2026-10-15 ([post](https://x.com/poteto/status/2110758788525621282)): comments are unstructured and unenforceable, get ignored, go stale, and give the agent an escape hatch to a hack. Audit them for stronger types, better APIs and new lint rules.
- 2026-10-17 ([guide 05](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/05-build-and-clean.md)): comments get a pass from a reviewer who didn't write them. Keep list: license headers, doc comments on a public API, links explaining what code can't, behavior forced by a dependency you can't reshape. A surprise in your own code becomes a refactor. A comment claiming a constraint becomes a type, test or lint.

## Skills and rules

- 2026-06-12 ([post](https://x.com/poteto/status/2065261102888575028)): start with nothing: no plugins, no skills, no AGENTS.md. Prompt, watch the failure modes, codify them as skills when they repeat. Better still, lint rules or a structure that makes the mistake impossible.
- 2026-06-24 (Loops You Can Trust): she built her skills by turning each recurring failure into one. Watch transcripts and thinking blocks to find failure modes. When a script can do a step deterministically, use the script. Agents get the fuzzy parts: hypotheses, reading evidence, deciding when a human is needed. Build the lever: do the first unit by hand, then a codemod plus a checker a reviewer can rerun. When an agent keeps doing something by hand, have it write the tool it wishes it had.
- 2026-08-28 ([reply](https://x.com/poteto/status/2093182292915298366)): 250 installed skills is overkill. Start at zero and add skills that help, scientifically, comparing with and without (her [eval playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md)).
- 2026-10-14 ([post](https://x.com/poteto/status/2110496830429839869)): principles are pstack's most durable part. They came from correcting agents. The agent names each principle that shaped a decision and the choice it changed.

## Loops, autonomy and review

- 2026-06-24 (Loops You Can Trust): every stage can stop the line (triage: expected behavior; repro: can't reproduce; fix: too risky), which keeps bad work from the next, costlier stage. Repro and fix post screenshots and video, so a human sees the right thing was fixed before reading code. A repro must hit the broken state twice. Humans can reject the repro before the fix starts. Long runs keep an append-only decision log, checked against the transcript and reviewed by another model family.
- 2026-08-11 ([post](https://x.com/poteto/status/2087244771849089270)): once Dune was in place, her agents merged their own PRs and she reviewed what landed on main.
- 2026-08-13 ([post](https://x.com/poteto/status/2087977008253071816)): cloud agents earn trust because they run the code, record video and drive the UI like users. A verification swarm that fuzzes every stack lets agents merge their own work.
- 2026-08-12 (workshop, 29:05–30:39): order: verification first, trust it locally, then scale out to agents picking up signals, auto-merge last. Skipping ahead only burns tokens.
- 2026-09-22 ([reply](https://x.com/poteto/status/2102201638824157449)): her agents merge their own PRs with no human review.
- 2026-10-03 (Pocock live, 49:23–53:05): you still taste the food, but at volume you sample. Each day scrutinize what agents landed, and fix the environment, not the one agent, when several agents share a mistake. A one-off is fine. Verification plus environment lets her step away. Review happens after landing: revert, modify, add lint rules. Getting there takes long, careful work.
- 2026-10-03 (56:28): whether one-way-door PRs can merge unattended depends on how verifiable the domain is. Where the work verifies, one-way doors become two-way. Where it doesn't, she has no answer.
- 2026-10-27 ([guide 07](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/07-overnight.md)): a loop you don't trust produces unchecked work faster. Before leaving it alone: you did the task once by hand or watched it, the agent has your tools and signals, every stage proves its work and can stop the line, and you read transcripts and turned repeated failures into tools, skills or checks. Autonomous only after all four hold. A handoff names goal, finish condition, permissions and an escape hatch. A duration is not a finish condition. In the morning, audit the decision log's Attention section, not the whole night. Every automated stage hands over evidence.
- 2026-09-09 (Pt. 2): two common mistakes are accepting the agent's first design and overcooking an abstract plan. Adversarial review of an abstract plan invents risks, so settle open questions with prototypes. Ask the agent to restate the problem in its own words before it starts, without leading it with your hypothesis.

## Changed positions

Newest wins. Each line gives the older stance, then the one that holds.

1. **Verification versus codebase design.** 08-28 to 08-31: verification "is all you need". 09-21: it gives only correctness, and agent-friendly architecture is among the most important work. **Holds (10-16):** codebase design gets the most effort, and a verification skill stays mandatory. The emphasis shifted; nothing was reversed.
2. **Formal verification.** 09-21: an open question few can run. **Holds (10-18 on):** recommended for costly properties tests rarely reach, with the difficulty caveat kept.
3. **Human review.** 08-16: last rung, "ngmi". 08-27: she still reads the code. 09-22: no human reviews. **Holds (10-03, 10-16, 10-19):** no blocking review; sample what landed and fix the environment. Human review is off the placement list.
4. **Comments.** 08-12 / 09-21: Dune bans them outright. **Holds (10-14, 10-17):** delete almost all, keep a short list (license, public API docs, external constraints, links). The full ban is a fact about Dune.
5. **Isolation for parallel agents.** 06-24: worktrees. **Holds (08-13, 08-31):** cloud agents preferred, a worktree acceptable for one run (guide 07, 10-27).
6. **The ladder's rungs.** 08-16: architecture, lint/test, skill/rule, review. 10-16: tests join static analysis, types move up into the codebase tier. **Holds (10-19, /correct):** architecture, types or lint/CI, test, doc or rule; review off the list.
7. **Overnight checklist.** 06-24: five steps. **Holds (10-27, guide 07):** four checks, then autonomy.
