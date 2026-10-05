# Memory across conversations

## What goes in memory

- **Give each carrier of state one job.** Compaction keeps the current conversation going (compaction.md), and memory helps later conversations start better. The system of record for a customer's facts is your database, never the agent's memory.
- **Store lessons and the customer's stated preferences, not case facts.** "This customer prefers English" helps the next conversation. "This customer was owed a refund" belongs in the ledger, where it can be checked.
- **Write only what passes a no-op gate:** would a future conversation go better because of this note? If unsure, skip it. Only specific, current notes help: vague or stale ones made agents worse in Notion's tests, more so on small models, while well-kept memory recovered about 46% of the failures an agent without memory never solved.
- **Keep many small notes, not a few large ones,** so one can be replaced, expired, or forgotten without touching the rest.

## Writing it

- **Extract memory in the background after the reply, not through a save tool.** A background extractor recalled 13% more facts than a tool that competed for the model's attention.
- **Run extraction as a job queue, and plan for its lag.** Extraction can take a minute or more, so a customer who comes straight back gets the conversation that just ended from the session log, not from memory. Failed jobs land in a dead-letter queue (held aside, not retried automatically), with a failure metric and a way to re-run them.
- **Stage first, promote later.** Notes land in the conversation's scope, and a pass when the conversation ends (humans.md) keeps only durable ones, resolving conflicts by the relation each note declares, then by the most recent date. "I'm traveling this week" is dropped. "Contact me in English" is kept. Before promoting a note, check its format and that its evidence supports each claim: those two checks raised correctness from 0.600 to 0.661 at Perplexity.
- **Each new note declares how it relates to an older one** (supersedes it, narrows its scope, or conflicts with it) instead of silently overwriting it, so the promotion pass and the consolidation job know which one wins.
- **Consolidate in an offline job that writes a new store.** It merges duplicates, removes orphaned notes, and replaces contradicted ones by their declared relation, then the latest date, leaving the input untouched. Review the output before sessions switch to it.
- **Scope memory per customer, and gate who can write shared memory.** Anyone's feedback can shape one case, but only named owners commit a change that affects every customer. Guard concurrent writes with a content-hash precondition and re-read on conflict, so two conversations never overwrite each other's notes.

## Reading it back

- **Put a compact index of what memory holds in the first message,** so the agent knows what it can look up. In a randomized test it cut memory-related dissatisfaction by 6.9%.
- **Date every remembered fact, link it to the conversation it came from, and say when an answer comes from memory.** A stale fact stated as current is worse than asking again. Store an `expires_at` on each note, set per note type, and push it back when a later conversation reinforces the fact. Before a consequential action the agent checks the source conversation.
- Memory is read back into context, so it's an injection path. How to sanitize it belongs to the security skill.

## Forgetting

- **"Forget that" removes every version of the matching notes, right away, only those, and the reply says what was forgotten.** If memory keeps versions, deleting the current note leaves the earlier ones readable: write a new version or delete first, then redact the earlier versions (Claude Managed Agents can't redact the current version of a live note). Log each deletion, and have the background pass read that log first, so it never re-adds a forgotten fact from an old conversation.
