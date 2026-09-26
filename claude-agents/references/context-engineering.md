# Context engineering

Everything Claude receives besides your prompt: system prompt, tools, instruction files, skills, memory, retrieved data, and history. Anthropic's frame since September 2025 is that context is a finite attention budget, so the job is curating the smallest set of high-signal tokens at every turn. The July 2026 post adds that Claude 5 models are overconstrained by habits built for weaker models, and most of those habits should go. The cookbooks add worked examples of compaction, tool-result clearing, and memory.

## Context is a budget

- **Find the smallest set of high-signal tokens.** Context engineering is the next step after prompt engineering: agents loop over many turns and generate more and more possibly-relevant data, so curating the whole context is iterative and happens every time something reaches the model. (`effective-context`)
- **Context rot is a gradient, not a cliff.** Recall falls as tokens grow, in every model, because attention stretches thin across more pairs and training favors shorter sequences. Bigger windows won't remove the need for long-horizon techniques. (`effective-context`)
- **A clean context beats a long one full of corrections.** Performance degrades as the window fills, and one debugging session can use tens of thousands of tokens. After the same correction twice, restarting with a better prompt works better than piling on more: "a clean session with a better prompt beats a long one full of corrections". (`cc-best-practices`)
- **Prompting is converging with context engineering.** For Claude 5 generation models: "less scaffolding, more curation". Instructions for every session belong in the system prompt, instruction files, skills, or other steering. (`prompt-engineering`)

## Delete most of it (Claude 5)

- **The team removed over 80% of Claude Code's system prompt for Opus 5 and Fable 5,** with no measurable loss on coding evals. (`ctx-eng`)
- **Conflicting instructions cost thinking.** Transcripts showed "leave documentation as appropriate" and "DO NOT add comments" in one request. A server that says "return JSON" and a skill that says "use markdown tables" force Claude to guess. (`ctx-eng`, `skills-and-mcp`)
- **Ritual instructions cost money and accuracy.** Verification rituals, emphasis boosters, mandatory scratchpads, stale examples, and contradictory rules patched older models. On an Opus 4.8 to 5.5 support migration, `prompt-audit` cut another 9% of cost and raised accuracy about 2 points: contradictory refund rules had withheld four owed refunds. (`platform-cost`, `cost`)
- **Rules → judgment.** The old prompt said "default to writing no comments". The new one says "Write code that reads like the surrounding code: match its comment density, naming, and idiom." (`ctx-eng`)
- **Explain why instead of shouting.** "NEVER use bullet points" works worse than stating the preference and its reason, which lets the model generalize. Say what to do, not what not to do. (`prompt-engineering`)
- **Other changes.** Examples → interface design. Everything up front → loaded when needed. Repeated instructions → one tool description. "Think carefully" lines → deleted. (`ctx-eng`, `opus-5-5`, `cb-ctx-tools`)

## Write prompts at the right altitude

- **Between brittle if-else logic and vague guidance.** Start with a minimal prompt on the best model and add instructions and examples only for failures you observe. Minimal doesn't mean short. (`effective-context`)
- **Curate a few canonical examples, not a list of edge cases.** "For an LLM, examples are the 'pictures' worth a thousand words." Claude 4.x reads examples closely, so they must show only what you want. (`effective-context`, `prompt-engineering`)
- **Let the model say "I don't know".** Permission to say the data is insufficient reduces hallucination. (`prompt-engineering`)

## Load context just in time

- **Let the agent find its own context.** Claude Code dropped vector-index RAG for Grep. Agents now hold lightweight references (paths, queries, links) and load data with tools at runtime, using `head` and `tail` on large data. Claude Code mixes both: an instruction file loaded up front, glob and grep for the rest. (`seeing`, `effective-context`)
- **Start with agentic search, add semantic search only if you need speed.** Vector search is usually faster but less accurate, harder to maintain, and less transparent. The folder structure becomes context engineering: an email agent keeps past threads in a folder to search. (`agent-sdk`)
- **Just-in-time is slower and needs guidance.** Without the right tools the agent wastes context on dead ends. Less dynamic domains like legal or finance may suit some retrieval up front. (`effective-context`)
- **Under about 200K tokens, skip retrieval.** Put the whole knowledge base in the prompt and cache it. When you do retrieve, prepending Claude-written context to each chunk cut retrieval failures 35%, 49% with BM25, and 67% with reranking (2024). (`contextual-retrieval`)

## Long horizons

- **Compaction, notes, or sub-agents.** Claude Code's compaction keeps decisions, unresolved bugs, and the five most recent files. Structured notes let Claude play Pokémon across thousands of steps. Sub-agents explore with tens of thousands of tokens and return 1,000-2,000-token summaries. Compaction suits back-and-forth, notes suit milestone work, sub-agents suit parallel research. (`effective-context`)
- **Let Claude assemble and prune its own context.** Skills load only frontmatter, context editing removes stale tool results, and subagents fork fresh windows. (`harness-patterns`)
- **Memory can live outside the prompt.** In commerce agents, an async extractor writes typed facts to the database and got 13% higher fact recall than a save tool, which competed for the model's attention. (`commerce-agents`)
- **Pick the primitive by the problem you have.** Compaction summarizes the whole transcript and is lossy. Clearing replaces only old tool results and is lossless if the tool can be called again. Memory is the only one that survives a new session. Days-long work → memory. Big re-fetchable results → clearing. Dialogue-heavy → compaction. (`cb-ctx-tools`)
- **The same overflow fails differently by window size.** A research agent reading about 320K tokens of documents kept climbing past 200K on a 1M window, with early facts buried. On a 200K window the same run hit a hard API rejection mid-task (measured). (`cb-ctx-tools`)
- **Unmanaged tool loops grow linearly.** Five support tickets at 7 tool calls each reached 150K cumulative input tokens by turn 27. SDK compaction at a token threshold cut the run to 79K. Low thresholds (5-20K) suit independent items, high ones (100-150K) suit work that needs its history. Skip it under 50-100K or when you need a full audit trail. (`cb-auto-compaction`)
- **Write your own compaction prompt in full.** The `instructions` parameter replaces the default summary prompt, it doesn't add to it, so name what must survive, like exact numbers. A cheaper model can do the summarizing. (`cb-ctx-tools`, `cb-auto-compaction`)
- **Build the summary before you need it.** "Instant compaction" writes session memory in a background thread from a soft threshold, so the swap at the limit is instant, where the demo's synchronous compaction left the user waiting over 40 seconds. When trimming, keep user corrections first, then errors, active work, and completed work. (`cb-session-memory`)
- **Order and size context editing.** `clear_thinking` goes before `clear_tool_uses` in the edits list, and production triggers sit around 30-40K tokens. (`cb-memory`)

## Memory across sessions

- **Memory is files the model chooses to write.** The memory tool is client-side: Claude calls `view`, `create`, `str_replace` and so on against `/memories`, and your app owns the storage. Its protocol assumes the window can reset at any moment, and its value depends on how well the model takes notes. (`cb-memory`, `cb-ctx-tools`)
- **In Managed Agents a memory store is a mounted directory.** Up to eight per session, for example one read-write store per customer plus a shared read-only one. The store's description goes into the system prompt, so make it specific. Seed it from data you already have, and every write is a versioned, auditable event. (`cb-user-memory`)
- **Memory is a prompt-injection vector.** "Memory poisoning": files are read back into context, so sanitize before storing, scope per user or project, log every operation, and tell Claude to ignore instructions found in memory. Store patterns, not raw history, and never secrets or PII. (`cb-memory`)

## Layer by layer

- **The system prompt is product context.** If you build your own agent, spend your time here. What a third or more of the traffic needs goes in the prompt, and the long tail goes in skills. (`ctx-eng`, `commerce-agents`)
- **Instruction files and system prompts are short and mostly gotchas.** For each line, ask whether removing it would cause mistakes, and skip what Claude can read from the code or data. "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" They are resent every turn, so the docs suggest under 200 lines. (`cc-best-practices`, `ctx-eng`, `cost`)
- **An instruction file is an onboarding document, not a data source.** It gives context and points to the source systems. With both the instruction file and detailed CSVs available, the agent prefers the granular files, so a high-level answer needs an explicit instruction. In multi-day runs it can be the plan the agent edits itself as it resolves issues. (`cb-chief-of-staff`, `long-running-science`)
- **Instructions are advisory, hooks are deterministic.** Use hooks for what must happen every time, like running a linter after each edit. (`cc-best-practices`)
- **Name the stops in the instructions.** When to keep going, when to stop before anything destructive, and the report format ("Blocked on me, Changed, Found"). (`opus-5-5`)
- **Prefer rich references as inputs.** Code or an HTML mockup beats a prose description or a screenshot. (`ctx-eng`)

## Key source articles
`effective-context` · `ctx-eng` · `prompt-engineering` · `cc-best-practices` · `contextual-retrieval` · `agent-sdk` · `harness-patterns` · `cb-ctx-tools` · `cb-memory`
