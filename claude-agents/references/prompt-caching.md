# Prompt caching

Caching is what makes long-running agents affordable, and it limits how you can build them. Claude Code is "built around prompt caching from day one". The September posts add the numbers, several customer-facing guides repeat the same rules, and the cookbooks show it in code.

## The principle

- **Caching is a prefix match.** The API caches everything from the start of the request up to each breakpoint, byte for byte. Any change invalidates everything after it. "Get the ordering right and most of the caching works for free." (`caching`)
- **They track it like uptime.** Claude Code alerts on its hit rate and opens an incident (a SEV) when it drops. A few points of miss rate change cost and latency a lot. (`caching`)
- **Nothing moves input cost more.** 2.8M input tokens on Opus 5.5 cost $11.20 uncached, $1.62 at a 90% hit rate, and $0.99 at 96%. (`cost`)
- **The Agent SDK caches with no setup.** The system prompt and tool schemas cache after the first call, and later calls pay about 10% of input for that prefix. (`cb-openai-migration`)

## Order the prompt

- **Static first, dynamic last.** Static system prompt and tools (shared globally), then project instructions like CLAUDE.md (per project), then session context (per session), then the messages. (`caching`)
- **Design for 90-99% hit rates with three segments.** Global, per session, and volatile. The most common mistake is a timestamp or the current page at the top of the system prompt: anything volatile above the breakpoint changes the key on every call, so push it below, into the user turn. Load skills as tool results and move breakpoints forward each turn. Cached reads also run about 1.5-2x faster at around 100K tokens. (`commerce-agents`, `cb-cost`)
- **The order breaks easily.** The team broke it by putting a detailed timestamp in the static prompt, by shuffling tool order, and by editing tool parameters, such as which agents the Agent tool can call. (`caching`)
- **Send updates as messages.** A new time or a changed file goes in a `<system-reminder>` inside the next user message or tool result, not in an edited system prompt. (`caching`)

## What breaks the cache

- **Anything that changes the byte-exact prefix.** The cache is pinned to one model, byte-exact, and has a time limit. Timestamps or IDs in the system prompt, reordered tool definitions, and forks that aren't byte-identical on the same model all miss. (`platform-cost`, `harness-patterns`)
- **Adding or removing tools mid-session.** Tools are part of the prefix. That's why Plan Mode is a pair of tools and MCP tools load as deferred stubs. (`caching`)
- **Clearing tool results.** It invalidates the cache from the cleared point forward, so set `clear_at_least` high enough that the freed tokens pay for the new write. A local file re-read is nearly free to redo, a rate-limited API call isn't. (`cb-ctx-tools`)
- **Switching models.** Each model has its own cache. 100k tokens into an Opus session, asking Haiku an easy question costs *more* than letting Opus answer. Hand off to a subagent instead. Claude Code's Explore agents run on Haiku this way. (`caching`)
- **Changing effort mid-session: the posts differ by model.** The platform guide (published 2026-09-08, updated after 2026-09-22) says effort or thinking changes break the cache except on Opus 5 and Fable 5.1 (`platform-cost`). The cost post (2026-09-25, later) says that on Opus 5.5 with an API key, changing effort keeps the cache, while Bedrock, Google Cloud, or a gateway clears it (`cost`, `effort`). Check your model and provider.
- **Switch model or effort at compaction, when you pay for a miss anyway.** Use deferred tools for rare ones: they aren't in the initial prompt, so they don't break it. (`platform-cost`, `advanced-tool-use`)
- **Bugs that drop earlier context also burn cache.** In March 2026 a change meant to clear old thinking once after an idle hour fired every turn. Claude kept working "without memory of why", and the cache misses likely drained users' limits. (`postmortem-apr-2026`)

## Lifetimes and prices (Opus 5.5, September 2026)

- **A read costs 5% of input. A write costs 1.25× input for 5 minutes or 2× for 1 hour.** Each hit resets the lifetime for free. (`cost`)
- **A pause past the lifetime is a full rewrite.** At 120K tokens of context, a six-minute gap on the 5-minute lifetime turns a $0.02 read into a $0.60 write. (`cost`)
- **Long contexts cost more per turn, even with a warm cache.** A turn's cache read costs about $0.004 at 20K tokens and $0.03 at 150K. Thirty turns at 150K spend $0.90 on reads alone. (`cost`)
- **Pre-warm, and pick the lifetime to fit the work.** A `max_tokens: 0` request with a breakpoint warms the cache before the first real call. Use the 1-hour lifetime when tool calls or subagents outlast 5 minutes. (`platform-cost`)
- **Batch requests get best-effort hits only.** The Batch API's 50% discount stacks with caching, but concurrent batch requests aren't guaranteed to hit the cache. (`cb-cost`)
- **Screenshots need a cache-aware buffer.** At 1,000-1,800 tokens each, 200K fills in under 100. Prune old screenshots in batches so the prefix stays byte-identical between prunes. (`computer-use`)

## Compaction

- **Naive compaction misses the cache completely.** A separate "summarize this" call with its own system prompt and no tools differs from the first token, so it pays full price, and it does that on the longest conversations. (`caching`)
- **Cache-safe forking.** Reuse the parent's exact system prompt, context, and tools, and add the compaction prompt as a new user message at the end. Keep room in the context for the summary. The API now does this for you. A background session-memory summary that reuses the chat's cached prefix cut its own cost about 80%. (`caching`, `cb-session-memory`)
- **Compact while the cache is warm.** With a warm cache, compacting at 150K costs about $0.25 and pays for itself in about ten turns. After the cache expires, the input alone costs about $0.75. (`cost`)

## Key source articles
`caching` · `cost` · `platform-cost` · `harness-patterns` · `commerce-agents` · `cb-cost`
