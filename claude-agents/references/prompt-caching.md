# Prompt caching

Why long-running agents are economically possible at all, and the design constraints that follow. Claude Code is "built around prompt caching from day one"; the September cost post puts numbers on it.

## The principle

- **Caching is a prefix match.** The API caches everything from the start of the request up to each breakpoint, byte for byte; any change invalidates everything after it. "Get the ordering right and most of the caching works for free." (`caching`)
- **It's an operational metric.** Claude Code alerts on hit rate and declares SEVs when it drops; a few points of miss rate dramatically change cost and latency. (`caching`)
- **Nothing moves input cost more.** 2.8M input tokens on Opus 5.5: $11.20 uncached, $1.62 at 90% hit, $0.99 at 96%. (`cost`)

## Lay out the prompt

- **Static first, dynamic last.** Static system prompt + tools (global) → CLAUDE.md (per project) → session context (per session) → messages. (`caching`)
- **The layout is fragile.** The team broke it with a detailed timestamp in the static prompt, non-deterministic tool ordering, and editing tool parameters (which agents the Agent tool can call). (`caching`)
- **Updates go in messages.** Time or file changes ride in a `<system-reminder>` in the next user message or tool result. (`caching`)

## What breaks the cache

- **Adding or removing tools mid-session.** Tools sit in the prefix; that's why Plan Mode is a pair of tools and MCP tools are deferred stubs. (`caching`)
- **Switching models.** Caches are per model: 100k tokens into Opus, asking Haiku an easy question costs *more* than letting Opus answer. Use a subagent with a hand-off message instead (Explore agents run on Haiku). (`caching`)
- **In Claude Code, expect a cache write when:** you pause longer than the lifetime; change effort on Bedrock, Google Cloud, or a gateway; turn on fast mode the first time; connect or disconnect an MCP server; switch models; compact. "Set these up when the session starts, and leave them alone." (`cost`)
- **Effort is cache-safe on the first-party path.** On an API key or subscription, changing effort keeps the cache, so you can raise it for one hard step. (`cost`, `effort`)

## Lifetimes and prices (Opus 5.5, Sep 2026)

- **Read 5% of input; write 1.25× (5 min) or 2× (1 h).** Each hit resets the lifetime free. (`cost`)
- **Subscription = 1 hour, API key or cloud = 5 minutes.** A subscription drops to 5 minutes once it draws on usage credits. (`cost`)
- **The coffee-break tax.** At 120K context, a six-minute break on an API key turns a $0.02 read into a $0.60 write. (`cost`)
- **Long contexts cost per turn even when warm.** A cache read is ~$0.004 per turn at 20K and ~$0.03 at 150K; 30 turns at 150K spend $0.90 on reads alone. (`cost`)

## Compaction

- **Naive compaction misses the cache entirely.** A separate "summarize this" call with its own system prompt and no tools diverges at token one and pays full price on the longest conversations. (`caching`)
- **Cache-safe forking.** Reuse the parent's exact system prompt, context, and tools; append the compaction prompt as a new user message; reserve a compaction buffer. Now built into the API. (`caching`)
- **Compact before a break, not after.** Warm: ~$0.25 at 150K, repaid in ~10 turns; cold after the lifetime: ~$0.75 input alone. `/clear` is free for unrelated work; `/rewind` returns to an already-cached prefix; tell `/compact` what to keep. (`cost`)

## Key source articles
`caching` · `cost`
