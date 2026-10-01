# Context and memory

## What the model sees each turn

- **Assemble it in layers, most specific last:** harness instructions and tools, the agent's prompt, procedures and knowledge for this case, the customer's state, then the message. Give each kind of injected item a type and a size cap. Codex reviews any new kind of item that can exceed 1K tokens and allows none over 10K, because one unbounded item crowds out the rest.
- **Order it for the cache: static first, dynamic last.** Instructions and tools first, the customer's data and the newest message last. Never put a timestamp or the current page in the system prompt, keep tools in a fixed order, keep history append-only, and send updates as new messages. Each change above the cache breakpoint makes the next call pay full price; ordered well, 90% to 99% of input is read from cache.
- **Keep the model's reasoning across turns,** as the API returns it. Dropping it made one agent rediscover the task every step (13.3% versus 38.3% on ARC-AGI-3). Reasoning is tied to the model that wrote it, which is another reason not to switch models mid-conversation (loop.md).
- **Put each fact in the right role.** Background sent as if the customer said it makes the model answer things nobody asked. Customer data reaches the model through a tool result or a labeled context block, never pasted into the customer's message.
- **Keep what your code needs apart from what the model sees.** The customer id, loggers, and API clients live in the run's local context and never reach the model (tools.md).
- **Re-send the few lines that must hold every turn** (the channel's rules, the current goal) with each message instead of trusting they survive a long conversation or a compaction. Keep them to a few lines. It's a reminder, not the whole prompt again.
- **Load procedures and knowledge when the case needs them,** not all up front. What a third or more of conversations need goes in the prompt, and the long tail is loaded on demand.

## Long conversations

- **Remove the cheapest thing first.** Clear old tool results that can be fetched again, or move them to a file and leave the path. Neither loses anything. Summarize only when that stops being enough, because a summary is lossy.
- **Compact at whole-turn boundaries,** so a tool result never loses the call it answers. Triggers: 5K to 20K tokens when each item is independent, 100K to 150K when the work needs its history. Skip compaction entirely for conversations that stay under 50K to 100K tokens in total, or when you need the full audit trail in context.
- **Write the summary prompt yourself, in full.** Ask for a handoff to another model: decisions, the customer's stated facts with exact numbers and ids, what's done versus only planned, what's still open. Mark unknowns "UNVERIFIED" instead of guessing. System instructions inside the summarized range stop applying, so send them again after compaction. Compaction also drops images and documents (a KYC upload), so keep a reference to them, and check `stop_reason` before reading the summary.
- **Make compaction a transaction.** If a new message arrived while the summary was being written, recompute instead of overwriting newer history.
- **Compact while the cache is warm and reuse the conversation's prefix.** A separate "summarize this" call pays full price on the longest conversations. A customer who replies after the cache lifetime (5 minutes by default) makes the next call rewrite the whole prefix, so compacting right then is cheap.
- **Build the summary before you need it,** in the background from a soft threshold. Synchronous compaction left one demo's user waiting over 40 seconds.

## Memory across conversations

- **Give each carrier of state one job.** Compaction keeps the current conversation going, and memory helps later conversations start better. The system of record for a customer's facts is your database, never the agent's memory.
- **Store lessons and the customer's stated preferences, not case facts.** "This customer prefers English" helps the next conversation. "This customer was owed a refund" belongs in the ledger, where it can be checked.
- **Extract memory in the background after the reply, not through a save tool.** A background extractor recalled 13% more facts than a tool that competed for the model's attention.
- **Write only what passes a no-op gate:** would a future conversation go better because of this note? If unsure, skip it.
- **Stage first, promote later.** Notes land in the conversation's scope, and a pass when the conversation ends (loop.md) keeps only durable ones, resolving conflicts by the most recent date. "I'm traveling this week" is dropped. "Contact me in English" is kept.
- **Scope memory per customer, and gate who can write shared memory.** Anyone's feedback can shape one case, but only named owners commit a change that affects every customer.
- **Date every remembered fact and say when an answer comes from memory.** A stale fact stated as current is worse than asking again.
- Memory is read back into context, so it's an injection path. How to sanitize it belongs to the security skill.

## Where the answer depends on the case

- **Knowledge base up front or retrieved?** Anthropic (2025-09) lets the agent search with tools when it needs something, noting that slow-changing domains like finance may suit retrieval prepared ahead; its 2024 advice to put a knowledge base under 200K tokens whole in the prompt predates its finding that recall falls as context grows. OpenAI's data agent embeds its sources offline every day and retrieves only what's relevant, which kept latency predictable across 70,000 datasets. Decide by how big your help center is and how often it changes.
- **Trim or compact?** For voice, trimming a little old history is graceful (Perplexity). On a long reasoning task, trimming hurt and compaction fixed it (OpenAI).
