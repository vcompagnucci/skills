# Architecture and multi-agent systems

Whether to build an agent at all, what one is made of, when to split work across agents, and how to orchestrate many of them. OpenAI's 2025 guide sets the default (one agent in a loop, split only when real failures demand it), and the 2026 posts stretch the same idea to parallel subagents and to a task tracker that keeps an agent running on every open ticket. Drawn from the 2025 PDF guide, engineering posts on openai.com, and developer blog posts, including customer stories without numbers.

## Decide whether you need an agent

- **An agent is a model that controls the workflow, not an app that calls a model.** It decides the steps, knows when it's done, corrects itself, hands control back to the user when it fails, and picks tools inside guardrails. Chatbots, single-turn calls, and classifiers are not agents. (`practical-guide`)
- **Reserve agents for work that resisted automation.** Three signals: nuanced judgment with exceptions (refund approval), rulesets too tangled to maintain (vendor security reviews), and heavy unstructured data (insurance claims). A fraud rules engine is a checklist, an agent is an investigator. Otherwise deterministic code may be enough. (`practical-guide`)
- **The 2025 shift was from prompting step by step to delegating whole tasks.** Better planning and longer tool use moved teams from single requests to handing over jobs, so building agents became "as much about system design (async + events + budgets) as prompting". (`devs-2025`)

## Model, tools, instructions

- **Every agent is built from the same three parts.** A model, tools, and instructions. Tools come in three kinds: data, action, and orchestration, where other agents are themselves tools. (`practical-guide`)
- **Write instructions from the procedures you already have.** Turn help-center articles and policies into routines, break dense material into small steps, map each step to an action or output (down to the exact wording for the user), and write branches for edge cases like missing information. A strong model can draft them from the documents. (`practical-guide`)
- **Use one templated prompt with policy variables instead of many prompts.** It keeps a growing set of use cases maintainable before any split is needed. (`practical-guide`)

## Single agent first

- **Maximize one agent before adding more.** Each agent is a loop that runs until an exit condition: a final-output tool, a reply with no tool call, an error, or a turn limit. Split only when the logic has too many if-then branches or the tools overlap, and try better tool names first (see tool-design.md). (`practical-guide`)
- **Let evidence pick the architecture.** At a DevDay booth demo, the agent wrote evals to choose a model trading speed for quality, compared single-agent and multi-agent designs, and refactored to a single agent. One demo, not a study. (`codex-devday`)

## Multi-agent shapes

- **Manager or handoff.** In the manager pattern a central agent calls specialists as tools and keeps the user, which fits when one voice should synthesize. In the decentralized pattern one agent hands off execution and conversation state to a peer for good, which fits triage where a specialist fully takes over. (`practical-guide`)
- **Separate gathering context from reasoning over it.** Repo Prompt runs a context-builder agent with tools that produces a structured context package, hands it to a reasoning model that makes no tool calls, and lets a reviewer agent decide whether another cycle is needed. A customer story, no numbers. (`responses-year`)
- **Decouple the fast part from the slow part.** In GPT-Live a voice model holds the conversation while it delegates deeper reasoning and tool use to a frontier model in the background. It can keep the exchange moving for a while, but it can't hide an arbitrarily slow result. (`gpt-live`)
- **Use parallel subagents for parallelizable work, and say when to spawn them.** A primary agent delegates, subagents work in parallel and return output for synthesis. Spawning is steerable, so telling the model when to use subagents keeps the extra token spend to cases where it helps. (`gpt56-guide`)

## Parallel agents and the human bottleneck

- **Parallel delegation was the main gain at DevDay.** The team often ran 3 to 4 independent tasks at once, and one engineer had seven terminals, each with an agent building a single-file game. Best-of-N made design cheap: a redesigned 404 page shipped from two attempts reviewed in five minutes. (`codex-devday`)
- **Parallel sessions bring coordination overhead back.** Building Sora for Android, several sessions (playback, search, error handling, tests) felt like leading a team, and the bottleneck moved from writing code to deciding, giving feedback, and integrating. No linear speedup, per Brooks: "Codex didn't get blocked by context switching, but we did." (`sora-android`)
- **Interactive supervision tops out at three to five sessions.** Past that, engineers forgot which session did what and spent their time nudging stalled agents. "The agents were fast, but we had a system bottleneck: human attention." (`symphony`)

## Orchestration: the tracker as control plane

- **Organize around deliverables, not sessions or PRs.** In Symphony every open issue gets its own workspace and an agent that runs until the work is done, and the orchestrator restarts crashed or stalled agents and picks up new issues. One issue can produce several PRs or just an analysis. Landed PRs rose 500% on some teams in the first three weeks, an early internal number. (`symphony`)
- **Big tickets become task trees with dependencies.** An agent writes an implementation plan, then generates the task tree, and agents start only unblocked tasks (the React upgrade waited on the Vite migration). Agents file follow-up issues for improvements outside their scope. (`symphony`)
- **Give objectives, not state-machine transitions.** Early versions only asked for implementation. With a GitHub CLI and CI-log skills the agent also answered review feedback, closed stale PRs, and reported abandoned work: "Give them tools and context and let them cook." (`symphony`)
- **When an agent misses, fix the system, not the output.** Without mid-run steering, the team added guardrails and skills (end-to-end tests, driving the app through browser devtools, QA smoke tests) and wrote down what good looks like. Ambiguous, judgment-heavy work still goes to interactive sessions. (`symphony`)
- **Write the implicit team process down as a versioned workflow file.** Check out, mark in progress, link the PR, move to review, attach a video: humans did it but never documented it. The orchestrator itself is only a spec, and the first version was a single agent in tmux polling the tracker. (`symphony`)
- **Orchestrator mechanics worth copying.** One authoritative state, bounded concurrency, stall detection that kills and retries silent workers, exponential backoff, stopping a run when its ticket leaves an active state, prompts that know whether this is a first run, a continuation, or a retry, one sanitized workspace per agent, restart recovery without a database, and secrets exposed as a tool instead of a token. Implementing the spec in six languages exposed its ambiguities. (`symphony`)
- **Cheap supervision makes exploration cheap.** Speculative tasks and prototypes are trivial to file and throw away. PMs and designers file features directly and get back a review packet with a video of the feature working, and the agent shepherds CI, rebases, and flaky retries. (`symphony`)

## Where the posts disagree

- **How many agents one person can run.** `codex-devday` (2025-10-10) presents 3 to 4 parallel tasks, even seven terminals, as the main productivity gain. `sora-android` (2025-12-12) found parallel sessions bring back coordination overhead with no linear speedup. `symphony` (2026-04-27) puts the ceiling at three to five interactive sessions and concludes the answer is to stop supervising sessions and let the tracker drive agents. The first two describe interactive use, the third changes the setup.
- **Prescribed routines or objectives.** `practical-guide` (2025-04-17) builds instructions as explicit routines from operating procedures with a branch for each edge case. `symphony` (2026-04-27) found rigid state-machine transitions limited its agents and switched to objectives plus tools, and `data-agent` (2026-01-29) found highly prescriptive prompts pushed its agent down wrong paths. The guide targets customer-facing policy work, the later posts internal engineering and analysis.

## Key source articles
`practical-guide` · `symphony` · `gpt56-guide` · `codex-devday` · `sora-android` · `responses-year` · `gpt-live` · `devs-2025`
