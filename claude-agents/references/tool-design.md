# Tool design

How the Claude Code team decides what an agent's tools should be. The stance is empirical: tools are shaped to what the current model can do, found by reading its outputs, and they expire as models improve. Most of this comes from Thariq Shihipar's posts on building Claude Code.

## Shape tools to the model

- **Give the agent tools shaped to its own abilities.** A solver with paper, a calculator, or a computer does different work depending on skill; you learn the model's skill by paying attention, reading outputs, and experimenting. (`seeing`)
- **A tool only works if the model likes calling it.** AskUserQuestion was kept because "Claude seemed to like calling this tool" and its outputs worked well. (`seeing`)
- **Structure beats format instructions.** Elicitation took three tries: a questions parameter on ExitPlanTool confused Claude (plan and questions at once); a custom markdown question format was unreliable (extra sentences, dropped options); a dedicated tool that blocks the loop behind a modal worked and is composable from the Agent SDK and skills. (`seeing`)
- **Design interfaces instead of writing examples.** With Claude 5 models, examples narrow the exploration space; expressive parameters teach usage instead, e.g. the Todo `status` enum (pending / in_progress / completed) plus one rule about keeping one item in progress. (`ctx-eng`)
- **Put tool instructions once, in the tool description.** Older models needed repeats in the system prompt and favored end-of-context instructions; that repetition was deleted. (`ctx-eng`)

## Keep the tool set small and stable

- **The bar to add a tool is high.** Claude Code has ~20 tools and the team keeps asking whether it needs all of them, because each one is another option to think about. (`seeing`)
- **Add capability without adding a tool.** Instead of docs in the system prompt (context rot) or a docs link (Claude pulled huge chunks for one-sentence answers), the Claude Code Guide subagent searches docs in its own context and returns only the answer. (`seeing`)
- **Model state changes as tools, not tool swaps.** Plan Mode keeps every tool present and adds EnterPlanMode / ExitPlanMode tools; swapping to read-only tools would break the cache, and the model can now enter plan mode itself on hard problems. (`caching`)
- **Defer, don't remove.** Dozens of MCP tools ship as name-only stubs with `defer_loading: true` in a stable order; full schemas load when tool search selects them. (`caching`, `ctx-eng`)

## Let the agent find its own context

- **Search tools beat retrieval pipelines.** Early Claude Code used RAG over a vector index: fast but fragile across environments, and Claude was *given* context rather than finding it. A Grep tool replaced it. (`seeing`)
- **Capability growth shows up as search depth.** In a year Claude went from not building its own context to nested search across several layers of files; skills formalized this as progressive disclosure. (`seeing`)

## Tools expire

- **Tools that once helped can start constraining.** TodoWrite plus a reminder every 5 turns kept early models on task; later models read the reminders as an order not to change course, and subagents couldn't share one list. It was replaced by the Task tool: dependencies, shared updates, editable by the model. (`seeing`)
- **Support a small set of similar models.** Revisiting tool assumptions is easier when the supported models have a similar capability profile. (`seeing`)
- **It's an art, not a science.** It depends on model, goal, and environment: "Experiment often, read your outputs, try new things." (`seeing`)

## Key source articles
`seeing` · `caching` · `ctx-eng`
