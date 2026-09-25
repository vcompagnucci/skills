# Tool design

How the Claude Code team decides which tools an agent gets. They work from evidence. A tool is shaped to what the current model can do, they find that out by reading its outputs, and they expect to retire tools as models improve. Most of this comes from Thariq Shihipar's posts on building Claude Code.

## Shape tools to the model

- **Give the agent tools that fit its abilities.** Paper, a calculator, or a computer each suit a different kind of solver. You learn what the model can do by watching it, reading its outputs, and experimenting. (`seeing`)
- **A tool only works if the model likes calling it.** They kept AskUserQuestion because "Claude seemed to like calling this tool" and its outputs worked. (`seeing`)
- **A dedicated tool beats format instructions.** Asking the user questions took three tries. A questions parameter on ExitPlanTool confused Claude, because it had to produce a plan and questions about that plan at once. A custom markdown format for questions was unreliable: Claude added sentences, dropped options, or dropped the format. What worked was a separate tool that pauses the loop behind a modal, and it can also be called from the Agent SDK and from skills. (`seeing`)
- **Design the interface instead of writing examples.** With Claude 5 models, examples narrow what the model tries. Clear parameters teach usage instead. The Todo tool's `status` enum (pending, in_progress, completed) plus one rule about keeping a single item in progress is enough. (`ctx-eng`)
- **Write tool instructions once, in the tool description.** Older models needed the same instruction repeated in the system prompt and paid more attention to the end of the context. The team deleted the repeats. (`ctx-eng`)

## Keep the tool set small and stable

- **The bar to add a tool is high.** Claude Code has about 20 tools, and the team keeps asking whether it needs all of them. Each one is another option the model has to weigh. (`seeing`)
- **Add a capability without adding a tool.** Claude couldn't answer questions about Claude Code itself. Putting the docs in the system prompt would have filled every session with text few users need. A docs link made Claude pull huge chunks to answer in one sentence. The fix was the Claude Code Guide subagent, which searches the docs in its own context and returns only the answer. (`seeing`)
- **Model state changes as tools, not as tool swaps.** Plan Mode keeps every tool loaded and adds EnterPlanMode and ExitPlanMode as tools. Swapping to a read-only set would break the cache. A side benefit: the model can now enter plan mode by itself when a problem looks hard. (`caching`)
- **Defer tools instead of removing them.** Dozens of MCP tools ship as name-only stubs with `defer_loading: true`, always in the same order. The full schema loads when tool search picks the tool. (`caching`, `ctx-eng`)

## Let the agent find its own context

- **Search tools beat retrieval pipelines.** Early Claude Code used RAG over a vector index. It was fast, but it broke across environments, and Claude was *given* context instead of finding it. A Grep tool replaced it. (`seeing`)
- **Better models search deeper.** In one year Claude went from barely building its own context to searching through several layers of files. Skills turned that into a pattern: files that point to other files, read only when needed. (`seeing`)

## Tools expire

- **A tool that once helped can start to hold the model back.** TodoWrite plus a reminder every 5 turns kept early models on task. Later models took the reminders as an order not to change the plan, and subagents couldn't share one list. The Task tool replaced it, with dependencies, updates shared across subagents, and tasks the model can edit or delete. (`seeing`)
- **Support a few models with similar abilities.** Revisiting what tools a model needs is easier when every supported model is roughly as capable as the others. (`seeing`)
- **It's an art, not a science.** It depends on the model, the goal, and the environment. Their advice: "Experiment often, read your outputs, try new things." (`seeing`)

## Key source articles
`seeing` · `caching` · `ctx-eng`
