# Context engineering

What goes into the model's window, in what order and role, what lives in files outside it, and how to keep it useful over long runs. Draws on OpenAI's engineering posts about the Codex loop, its internal data agent and a benchmark harness experiment, plus developer-blog guides and guest posts from Dagster, Perplexity and Alpic.

## Layer the context

- **Assemble initial context in layers, most specific last.** In Codex: harness instructions and the tool list, a message describing the sandbox, developer instructions, user instructions merged from global and per-folder instruction files (repo root down to the working directory), skills, the environment (cwd, shell), then the user message. (`agent-loop`)
- **Ground a domain agent in several kinds of context, not just schemas.** OpenAI's data agent uses six layers: table usage (schema, lineage, past queries), human annotations, definitions derived from the code that produces each table, company docs ingested with permissions, memory, and live queries when the rest is missing or stale. An offline daily pipeline embeds the first layers, and at query time it retrieves only what's relevant, which keeps latency predictable across 70k datasets. (`data-agent`)
- **Meaning often lives in the code that produces the data.** Schemas show shape. Pipeline code shows assumptions, freshness and scope, which is how the agent tells apart two tables that look alike (one counts logged-out users, one doesn't). (`data-agent`)
- **Frame each piece with the right role.** Perplexity found that background sent as user input makes the model act as if the user said every paragraph aloud, and too much as system blurs what it knows, what was supplied and what is being asked. Page content while scrolling should read as background awareness. (`perplexity-voice`)
- **Feed context in small pieces so overflow degrades gracefully.** A 10,000-token update into a window with 5,000 tokens left wiped all prior history. Chunks of about 2,000 tokens meant truncation trimmed a little instead. (`perplexity-voice`)
- **Decide who needs to know what.** In an agent app the user, the UI and the model each hold part of the state. Alpic's first instinct to share everything was a mistake: the model doesn't need images and pricing variants, and some state must stay hidden. They split tool output into a model-visible channel and a UI-only one, and tag components with a line like "User is viewing reviews" that feeds the next turn. A guest post drawn from two dozen apps. (`chatgpt-apps-lessons`)

## Instruction files as a map

- **Give the agent a map, not a 1,000-page manual.** One big instruction file crowded out the task, made everything important, rotted and couldn't be checked. What worked was an entry file of about 100 lines pointing into a structured docs directory (design docs with verification status, an architecture map, quality grades, plans with decision logs). Linters and CI check freshness and cross-links, and a recurring agent opens fix-up PRs for stale docs. (`harness-eng`)
- **Prune always-on instructions and make them situational.** "Before every edit, read architecture.md, database.md, deployment.md" burns context on a typo fix. Say which doc serves which situation. (`astra-skills`)
- **Docs written well for humans double as agent instructions.** Dagster rewrote its contributor guide for people and "inadvertently significantly improved" the agent: hierarchy, structure, and rules with their reasons. A guest post. (`dagster-docs`)

## The repo as system of record

- **If the agent can't see it, it doesn't exist.** Decisions in chat, docs or people's heads have to be pushed into the repo. Prefer boring, well-known dependencies the model can reason about. (`harness-eng`)
- **Keep code, docs and examples together.** Dagster favors one repo because you can point the agent at a starting file and let it explore. With the iOS, backend and Android repos in one environment, the Sora team's agent read the iOS models and planned the Android version. (`dagster-docs`, `sora-android`)
- **Missing context produces guesses, not refusals.** When the Sora team's agent lacked context, it wasn't "refusing to cooperate". It was guessing. (`sora-android`)

## Memory

- **Keep memory outside the conversation, in files you can open, edit and diff.** A repo holds code and a vault holds rolling context: people, decisions, open loops. In git, the diff shows what the agent chose to remember. Record what changed, not vague impressions. (`codex-maxxing`)
- **Store the non-obvious corrections, and let the agent ask to save them.** The data agent couldn't filter an experiment until memory held the exact gate string. Memories are global or personal, and users can edit them. (`data-agent`)
- **Capture decisions before closing a run.** Why an option won, what's preferred now, the dead ends. Otherwise they vanish into the chat. Give each run an index file so later agents can find past runs. (`repetitive-work`)
- **Messy spoken input beats a tidy typed prompt.** A voice note keeps the half-remembered name and the uncertainty ("some guy named Ben in Slack mentioned this"). One author's practice, not measured. (`codex-maxxing`)

## Long runs: compaction and retained reasoning

- **Keep the model's reasoning across turns.** Dropping it makes the agent rediscover the task every step. On ARC-AGI-3, keeping reasoning and compacting instead of truncating took the score from 13.3% to 38.3% with about 6x fewer output tokens and no model change. Earlier, carrying reasoning forward scored 5% better on TAUBench. (`arc-agi-3`, `responses-api`)
- **Compact, don't truncate.** Rolling truncation drops the oldest observations and keeps the window near full. Compaction replaces history with a smaller set of items. In Codex it grew from a manual summary command into automatic compaction that carries an opaque state of the model's understanding. (`arc-agi-3`, `agent-loop`)
- **Match compaction to how the model was trained.** OpenAI's models are trained to keep private reasoning and summarize when long, which is how its own products run them. Tolerating small overages near the limit lets a request be compacted instead of rejected. (`arc-agi-3`, `computer-env`)
- **Plan for it from the start.** "Use compaction as a default long-run primitive, not an emergency fallback." (`skills-shell`)
- **Keep the labels on past messages.** Codex needs each earlier assistant message marked as a progress update or a final answer, or performance "degrades significantly". (`codex-prompting`)

## Prompting habits

- **Guide the goal, not the path.** Highly prescriptive prompts pushed the data agent down wrong paths. Higher-level guidance plus the model's own reasoning was more robust. (`data-agent`)
- **Stronger models need less scaffolding.** Recipes that helped earlier models now hurt. Telling the model to run tests causes extra testing because it already checks its work. Strong "ask first" language written for an overreaching model makes a well-aligned one stop early. Re-audit at each model change, and let the new model audit your instructions. (`astra-skills`)
- **Say what done means before starting.** Put "get it running, inspect, fix what fails" in the request and drop review gates you don't need, or a tentative model returns after the first draft. Codex's prompt pushes to finish end to end, never end on only a plan, and stop to ask when re-reading the same files without progress. (`astra-skills`, `codex-prompting`)
- **Underspecified prompts fall back to common training patterns.** For frontends, state hard constraints first (one H1, two typefaces, one accent) and give real copy, which the post calls the simplest quality lever. (`frontends`)
- **Point at an example, not a description.** "Build this settings screen" was unreliable. "Using the same architecture and patterns as this other screen" worked far better. (`sora-android`)
- **Fix failure modes by metaprompting.** After a weak turn, ask the model how to change its instructions, sample several times, keep what's common, then check with an eval. (`codex-prompting`)

## Where the posts disagree

- **How specific should instructions be?** The frontend guide (2026-03-20) gets distinctive output from hard numeric rules. The Astra post (2026-09-11) says overly specific guidance now hinders a stronger model. One is about taste constraints, the other about step-by-step recipes. (`frontends`, `astra-skills`)
- **Progress updates changed with the model.** The Codex prompting guide (2026-02-25) says to remove prompting for plans and status updates on earlier models, because it made them stop before finishing, and to prompt for them from the February 2026 model on. (`codex-prompting`)
- **Is truncation acceptable?** Perplexity (2026-03-25) treats trimming a little old history as graceful degradation for voice. The ARC-AGI-3 post (2026-07-29) found truncation hurt a long reasoning task and replaced it with compaction. (`perplexity-voice`, `arc-agi-3`)

## Key source articles
`harness-eng` · `data-agent` · `arc-agi-3` · `astra-skills` · `agent-loop` · `perplexity-voice` · `codex-maxxing` · `dagster-docs` · `codex-prompting`
