# Prompt caching

Why an agent loop depends on caching, and how to assemble prompts that keep hitting it. Draws on OpenAI's engineering posts about the Codex loop and model efficiency, its realtime voice system, the Agents API launch, a cookbook on support-agent cost (a simulation), and the Codex repo's own rules for model-visible context.

## Why it matters

- **The loop is quadratic in bytes, and caching makes sampling linear.** Each iteration resends the whole growing prompt, so Codex builds every new prompt as an exact prefix extension of the last. "When we get cache hits, sampling the model is linear rather than quadratic." (`agent-loop`)
- **Caching repeated prefixes is a basic building block for long-running agents.** The system prompt, tools and schemas repeat on every call. (`devs-2025`)
- **Carrying reasoning forward helps the cache too.** OpenAI measured 40 to 80% better cache utilization in internal benchmarks when reasoning state was preserved between turns. (`responses-api`)

## Assembly order

- **Stable first, variable last.** Instructions, policy, tool definitions and output schema first, customer data at the end. (`cost-quality`)
- **Treat model-visible history as append-only.** New messages, tool results and environment updates go at the end, never inserted earlier. OpenAI credits this for Codex's high cache hit rates. The Codex repo enforces it at code review. Its AGENTS.md says "No history rewrite - the context must be built up incrementally" and to avoid context changes "that cause cache misses", and a shipped review skill checks both. (`gpt56-efficiency`, `repo-agents-md`, `repo-review`)
- **Record config changes as a new message.** When the sandbox or approval mode changes, Codex appends a new permissions message. When the working directory changes, it appends a new environment message. It never edits the old one. World-state sections are sent as diffs and re-emitted only when they change. (`agent-loop`, `repo-context`)
- **List tools in a deterministic order.** A real Codex bug: tools from external servers came back in inconsistent order and missed the cache. (`agent-loop`, `gpt56-efficiency`)
- **Keep runtime settings out of tool definitions.** Approval policies are applied at execution time, so changing them doesn't touch the prefix. (`gpt56-efficiency`)
- **Keep the tool list constant and restrict per request.** Swapping the list per request changes the prefix (`cost-quality`). Tools found by search are added for the next call instead of replacing the list (`repo-tools`), and OpenAI says its tool search cuts tokens and cost "while preserving the model's cache", a product claim with no numbers (`agents-api`).
- **Place cache breakpoints deterministically, and send the same prefix to the same engine.** Routing by prefix cuts latency as well as cost. (`gpt56-guide`)

## What breaks it

- **Anything that changes the prefix.** Changing tools mid-conversation, switching models, or editing the sandbox, approval mode or working directory in place. Honoring a tool server's "tools changed" notification mid-conversation is expensive for the same reason. Codex's model-upgrade guide lists cache behavior among what each call site must keep, and cache topology as a gate before a migration ships. (`agent-loop`, `repo-prompting`)
- **Compaction rewrites past context, so it invalidates the cache.** GPT-Live prepares a replacement instance with the compacted context while the old one keeps talking, then cuts traffic over, instead of stalling the live conversation. (`gpt-live`)
- **A cold start is a miss you can pay early.** GPT-Live prefills the delegated model with the conversation at session start and keeps it warm with stable session affinity plus caching, so the first real call doesn't wait. (`gpt-live`)

## When caching doesn't pay

- **If cache writes cost extra, caching unique content can raise cost.** A queue where prompts rarely repeat may do better without it. Check the repeat rate before assuming caching saves money. From a cookbook simulation, not production data. (`cost-quality`)

## Key source articles
`agent-loop` · `gpt56-efficiency` · `cost-quality` · `gpt-live` · `gpt56-guide` · `repo-agents-md` · `repo-context` · `agents-api`
