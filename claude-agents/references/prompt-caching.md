# Prompt caching

Caching is what makes long-running agents affordable, and it limits how you can build them. Claude Code is "built around prompt caching from day one". The September cost post adds the numbers.

## The principle

- **Caching is a prefix match.** The API caches everything from the start of the request up to each breakpoint, byte for byte. Any change invalidates everything after it. "Get the ordering right and most of the caching works for free." (`caching`)
- **They track it like uptime.** Claude Code alerts on its hit rate and opens an incident (a SEV) when it drops. A few points of miss rate change cost and latency a lot. (`caching`)
- **Nothing moves input cost more.** 2.8M input tokens on Opus 5.5 cost $11.20 uncached, $1.62 at a 90% hit rate, and $0.99 at 96%. (`cost`)

## Order the prompt

- **Static first, dynamic last.** Static system prompt and tools (shared globally), then CLAUDE.md (per project), then session context (per session), then the messages. (`caching`)
- **The order breaks easily.** The team broke it by putting a detailed timestamp in the static prompt, by shuffling tool order, and by editing tool parameters, such as which agents the Agent tool can call. (`caching`)
- **Send updates as messages.** A new time or a changed file goes in a `<system-reminder>` inside the next user message or tool result. (`caching`)

## What breaks the cache

- **Adding or removing tools mid-session.** Tools are part of the prefix. That's why Plan Mode is a pair of tools and MCP tools load as deferred stubs. (`caching`)
- **Switching models.** Each model has its own cache. 100k tokens into an Opus session, asking Haiku an easy question costs *more* than letting Opus answer. Hand off to a subagent instead. Claude Code's Explore agents run on Haiku this way. (`caching`)
- **In Claude Code, you pay a cache write when you:** pause longer than the cache lifetime, change effort on Bedrock, Google Cloud, or a gateway, turn on fast mode for the first time, connect or disconnect an MCP server, switch models, or compact. "Set these up when the session starts, and leave them alone." (`cost`)
- **Changing effort is safe on the first-party path.** With an API key or a subscription, changing effort keeps the cache, so you can raise it for one hard step and lower it again. (`cost`, `effort`)

## Lifetimes and prices (Opus 5.5, September 2026)

- **A read costs 5% of input. A write costs 1.25× input for 5 minutes or 2× for 1 hour.** Each hit resets the lifetime for free. (`cost`)
- **A subscription gets 1 hour. An API key or cloud provider gets 5 minutes.** A subscription drops to 5 minutes once it's drawing on usage credits. (`cost`)
- **The coffee-break tax.** At 120K tokens of context, a six-minute break on an API key turns a $0.02 read into a $0.60 write. (`cost`)
- **Long contexts cost more per turn, even with a warm cache.** A turn's cache read costs about $0.004 at 20K tokens and $0.03 at 150K. Thirty turns at 150K spend $0.90 on reads alone. (`cost`)

## Compaction

- **Naive compaction misses the cache completely.** A separate "summarize this" call with its own system prompt and no tools differs from the first token, so it pays full price, and it does that on the longest conversations. (`caching`)
- **Cache-safe forking.** Reuse the parent's exact system prompt, context, and tools, and add the compaction prompt as a new user message at the end. Keep room in the context for the summary. The API now does this for you. (`caching`)
- **Compact before a break, not after.** With a warm cache, compacting at 150K costs about $0.25 and pays for itself in about ten turns. After the cache expires, the input alone costs about $0.75. `/clear` is free for unrelated work. `/rewind` goes back to a prefix that's still cached. Tell `/compact` what to keep. (`cost`)

## Key source articles
`caching` · `cost`
