# Context

Long conversations (clearing, compaction, summaries) are in compaction.md.

## What the model sees each turn

- **Assemble it in layers, most specific last:** harness instructions and tools, the agent's prompt, procedures and knowledge for this case, the customer's state, then the message. Give each kind of injected item a type and a size cap. Codex reviews any new kind of item that can exceed 1K tokens and allows none over 10K, because one unbounded item crowds out the rest.
- **Order it for the cache: static first, dynamic last.** The provider reuses only the unchanged start of the request (the cache prefix), so instructions and tools go first and the customer's data and the newest message last. Each change above the cache breakpoint (where the cached prefix ends) makes the next call pay full price; ordered well, 90% to 99% of input is read from cache.
- **Keep the prefix still:** no timestamp or current page in the system prompt, tools in a fixed order, history append-only, and updates sent as new messages.
- **Keep the model's reasoning across turns,** as the API returns it. Dropping it made one agent rediscover the task every step (13.3% versus 38.3% on ARC-AGI-3). Reasoning is tied to the model that wrote it, which is another reason not to switch models mid-conversation (failures.md).
- **Put each fact in the right role.** Background sent as if the customer said it makes the model answer things nobody asked. Customer data reaches the model through a tool result or a labeled context block, never pasted into the customer's message.
- **Keep what your code needs apart from what the model sees.** The customer id, loggers, and API clients live in the run's local context and never reach the model (SKILL.md rule 3).
- **Re-send the lines that must hold every turn** (the channel's rules, the current goal) with each message instead of trusting they survive a long conversation or a compaction. Keep them to 5 lines or fewer: it's a reminder, not the whole prompt again.
- **Put guidance that applies only sometimes at the end of the context, never in the system prompt.** A cheap classifier picks which short instruction, if any, this step needs; it goes after the newest message and is dropped after the step, so the cached prefix never changes (90% cheaper than rewriting the prompt at Replit). Keep 3 or 4 at once, since returns fell after the third or fourth.
- **A guidance check before an action fires once as a detour, never as a block** (policy limits still reject in the handler, SKILL.md rule 2). Ramp's agent rejected checks that held until it proved compliance, and kept retrying the blocked action.
- **Load account data by the customer's intent:** transaction history only for a transaction question. Monzo gained 10 points of resolution on those questions; DoorDash saw an agent with too much data start dropping instructions.
- **Detect the reply language in code,** limited to the languages you support, falling back to the account's locale, and pass it as a field. A short message ("ok", "gracias") fools a detector and the model alike.
- **Before an action, restate everything the customer asked for across all their messages.** A request spread over several messages lost 39% on average against the same request in one message, and a recap recovered most of it (measured on GPT-4o).
- **Load procedures and knowledge when the case needs them,** not all up front. What a third or more of conversations need goes in the prompt, and the long tail is loaded on demand.
- **Show a catalog of procedure names and one-line descriptions** (about 50 to 100 tokens each). Load a procedure's body only when it's picked (keep it under 5,000 tokens) and its files only when the body points to them, and never load one that's already in context.
- **Give the load tool an enum of only the procedures this run may use,** so a forbidden one is never offered instead of rejected after the model picks it.

### Per-provider cache details

- **Model settings sit in the cache prefix too.** Changing effort, output format, or tool settings mid-conversation breaks the cache on OpenAI. Changing effort or thinking breaks it on Claude, except on Opus 5, Fable 5.1, and Opus 5.5 on the direct API. Change them only through an in-band update where one exists (GPT-6's `configuration_update`, Sonnet 5.5's per-message effort in beta); a history holding `configuration_update` items compacts only through a `compaction_trigger` item.
- **Send the conversation id as `prompt_cache_key` on every call where the provider routes cache by that key** (xAI; OpenAI up to GPT-5.5), so calls land where the prefix is already cached.
- **Server-side conversation state holds only the history.** When you chain calls by a stored response or interaction id, send the instructions, tools, and model settings (thinking level included) on every call, or that turn runs without them. Stored state also expires (Gemini keeps it 1 day on the free tier, at most 55 on paid), so read history from your own log (SKILL.md rule 7).

## Where the answer depends on the case

- **Knowledge base up front or retrieved?** Decide by how big your help center is and how often it changes.
  - Anthropic (2025-09) lets the agent search with tools when it needs something, noting that slow-changing domains like finance may suit retrieval prepared ahead. Its 2024 advice to put a knowledge base under 200K tokens whole in the prompt predates its finding that recall falls as context grows.
  - OpenAI's data agent embeds its sources offline every day and retrieves only what's relevant, which kept latency predictable across 70,000 datasets.
  - On about 700 help-center documents, searching the files directly matched or beat embeddings for all 5 models tested (τ-Knowledge, 2026-03). Even with the right documents in context the best score was 39.7%, so applying procedures is the harder problem.
