# Context and memory

## What the model sees each turn

- **Assemble it in layers, most specific last:** harness instructions and tools, the agent's prompt, procedures and knowledge for this case, the customer's state, then the message. Give each kind of injected item a type and a size cap. Codex reviews any new kind of item that can exceed 1K tokens and allows none over 10K, because one unbounded item crowds out the rest.
- **Put each fact in the right role.** Background sent as if the customer said it makes the model answer things nobody asked. Customer data reaches the model through a tool result or a labeled context block, never pasted into the customer's message.
- **Keep what your code needs apart from what the model sees.** The customer id, loggers, and API clients live in the run's local context and never reach the model (tools.md).
- **Re-send the few lines that must hold every turn** (the channel's rules, the current goal) with each message instead of trusting they survive a long conversation or a compaction. Keep them short: this is a reminder, not the whole prompt again.
- **Load procedures and knowledge when the case needs them,** not all up front. What a third or more of conversations need goes in the prompt, and the long tail is loaded on demand.

## Long conversations

- **Remove the cheapest thing first.** Clear old tool results that can be fetched again, or move them to a file and leave the path: both lose nothing. Summarize only when that stops being enough, because a summary is lossy.
- **Compact at whole-turn boundaries,** so a tool result never loses the call it answers. Triggers: 5K to 20K tokens when each item is independent, 100K to 150K when the work needs its history. Skip compaction entirely for conversations that stay under 50K to 100K tokens in total, or when you need the full audit trail in context.
- **Write the summary prompt yourself, in full.** Ask for a handoff to another model: decisions, the customer's stated facts with exact numbers and ids, what's done versus only planned, what's still open. Mark unknowns "UNVERIFIED" instead of guessing. System instructions inside the summarized range stop applying, so send them again after compaction.
- **Make compaction a transaction.** If a new message arrived while the summary was being written, recompute instead of overwriting newer history.
- **Build the summary before you need it,** in the background from a soft threshold. Synchronous compaction left one demo's user waiting over 40 seconds.

## Memory across conversations

- **Give each carrier of state one job.** Compaction keeps the current conversation going, and memory helps later conversations start better. The system of record for a customer's facts is your database, never the agent's memory.
- **Store lessons and the customer's stated preferences, not case facts.** "This customer prefers English" helps the next conversation. "This customer was owed a refund" belongs in the ledger, where it can be checked.
- **Write only what passes a no-op gate:** would a future conversation go better because of this note? If unsure, skip it.
- **Stage first, promote later.** Notes land in the conversation's scope, and a pass when the conversation ends (loop.md) keeps only durable ones, resolving conflicts by the most recent date. "I'm traveling this week" is dropped. "Contact me in English" is kept.
- **Scope memory per customer, and gate who can write shared memory.** Anyone's feedback can shape one case, but only named owners commit a change that affects every customer.
- **Date every remembered fact and say when an answer comes from memory.** A stale fact stated as current is worse than asking again.
- Memory is read back into context, so it's an injection path. How to sanitize it belongs to the security skill.

## Where the answer depends on the case

- **Knowledge base up front or retrieved?** Anthropic puts a knowledge base under about 200K tokens whole in the prompt and caches it, and otherwise lets the agent search with tools; it says slow-changing domains like finance may suit retrieval prepared ahead. OpenAI's data agent embeds its sources offline every day and retrieves only what's relevant at query time, which kept latency predictable across 70,000 datasets. They describe different sizes and change rates: decide by how big your help center is and how often it changes.
- **Trim or compact?** For voice, trimming a little old history is graceful (Perplexity). On a long reasoning task, trimming hurt and compaction fixed it (OpenAI).
