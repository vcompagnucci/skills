# Compaction

## Clear before you summarize

- **Remove the cheapest thing first.** Clear old tool results that can be fetched again, or move them to a file and leave the path. Neither loses anything, but clear in batches (next section). Summarize only when that stops being enough, because a summary is lossy.
- **Never prune or compact away a loaded procedure.** Wrap each one in tags so code can find it and keep it through clearing and compaction: losing one mid-conversation degrades the agent with no visible error.
- **Judge compaction and clearing by total input cost, not cache hit rate,** because both lower cache reuse on the next call. Read the cached tokens on every response (`cached_tokens` on OpenAI, `cache_read_input_tokens` on Claude); OpenAI also returns why a call missed when you pass `comparison_response_id`.

## When and where to cut

- **Compact and clear at whole-turn boundaries,** so a tool result never loses the call it answers. Finish any pending tool call first (Claude rejects a history that ends in an unanswered call), and never cut turns out of the middle.
- **Clear in batches at natural boundaries, not a little each turn.** Each clearing is one cold cache miss and, on models that keep reasoning across turns, invalidates the reasoning after it.
- **Triggers: 5K to 20K tokens of context for a batch of independent items (tickets processed one after another), 100K to 150K when the work needs its history.** Skip compaction for runs whose cumulative input stays under 50K to 100K tokens, or when you need the full audit trail in context.
- **Compact at the end of a turn, while the cache is warm,** and reuse the conversation's prefix. A separate "summarize this" call pays full price on the longest conversations. Never wait for the user to come back: after the cache lifetime (5 minutes by default on Claude, 30 minutes on OpenAI from GPT-5.6) the compaction call reads the whole prefix cold (in Anthropic's example, about $0.75 instead of $0.25 at 150K tokens).
- **Build the summary before you need it,** in the background from a soft threshold, while the agent keeps working on the full context. Synchronous compaction left one demo's user waiting over 40 seconds, and building it off the critical path cut end-to-end latency by up to 39.7% in one study. On a model that keeps reasoning across turns, a summary you built yourself invalidates the reasoning of every turn that ran meanwhile: use the provider's background compaction, or drop reasoning from the swap on.
- **Make compaction a transaction.** If a new message arrived while the summary was being written, recompute instead of overwriting newer history.

## Writing the summary

- **If you write the summary yourself, replace the whole history with it.** One message holds the summary and the next instruction, and nothing earlier is replayed; Claude models are trained on that scheme. Keeping recent turns verbatim behind your own summary invalidates the reasoning in those turns on models that keep it across turns, so use the provider's compaction when you want a summary plus recent turns.
- **Write the summary prompt yourself, in full.** Ask for a handoff to another model: decisions, the user's stated facts with exact numbers and ids, what's done versus only planned, what's still open. Mark unknowns "UNVERIFIED" instead of guessing, and tell the summarizer not to call tools.
- **Send system instructions again after compaction,** because instructions inside the summarized range stop applying. Compaction also drops images and documents (a KYC upload), so keep a reference to them.
- **Handle every way compaction comes back empty.** With tools defined, the summarizer sometimes calls one instead of writing and returns nothing. Check `stop_reason` before reading the summary:
  - Cut off by the output limit: retry with more room.
  - No room for the prompt: shorten the input.
  - A refusal or no text: continue without a summary and compact later if the window still has room. If it's full, end with the fallback (loop.md).
- **Send the provider's summary block back byte for byte,** since an edited one is rejected. Estimate context size yourself, because the last response's usage can read zero.
- **Check the summary's size before it replaces the history.** Grok Build rejects any summary under 500 characters and retries: its broken summaries measured 75 to 264 characters, the shortest good one 3,242.
- **Then have a judge check that it keeps the agent's next intent** and the facts and constraints it relies on, which a size check misses (up to 8.8 points more accuracy in one study). A summary that replaced the history can't be undone in the context, only rebuilt from the log.

## Where the answer depends on the case

- **Trim or compact?** For voice, trimming a little old history is graceful (Perplexity). On a long reasoning task, trimming hurt and compaction fixed it (OpenAI).
- **Hide old tool results alone, or add a summary?** Test whether pruning alone holds on your multi-step cases before relying on it.
  - On coding tasks, keeping the last 10 turns' tool outputs and hiding older ones scored the same as summaries at half the cost.
  - Where earlier results set later state (amounts already processed, items already done), the last 5 tool pairs plus a summary scored 91.6%, against 79.0% for the pairs alone and 71.0% for the full history, on about 37% of the full history's tokens (GPT-5, 50 expense tasks, 2026-06).
  - Get that shape from the provider's compaction, or from your own summary only on a model that doesn't keep reasoning across turns ("Writing the summary").
