# Tools

## Which tools

- **A tool must know, do, or show something:** bring data the model lacks (the customer's account, a transfer's status), take a real action, or present information better than text. A tool that does none of these is noise the model has to weigh.
- **Group tools by the customer's intent, not by your API's endpoints.** One `get_withdrawal_status` beats `list_withdrawals` plus `get_withdrawal` plus `get_network_fee`. Each extra tool is one more choice the model can get wrong.
- **Overlap matters more than count.** OpenAI saw some agents handle 15 or more distinct tools while others failed with fewer than 10 overlapping ones. If a person can't say which tool fits a situation, the model can't either. Fix names and descriptions before splitting into more agents.
- **Business actions are typed tools with structured returns.** A support agent gets no shell or file-reading tools. No support task needs them, and each one is a choice the model can get wrong.
- **Test each tool against the no-tool baseline** on a few positive, negative, and edge cases. A tool that doesn't beat the model's answer without it goes.

## Arguments and descriptions

- **The description is a prompt.** Say what the tool does, when to use it, when not to, and what it returns, as you would to a new hire. Name parameters unambiguously (`customer_id`, not `id`). A description fix changes behavior more than a schema change does.
- **Give allowed values as enums** (`network: "TRC20" | "ERC20"`), so the model maps the customer's words to a value instead of guessing which exist.
- **Turn on strict schemas.** Newer models invent keys without them, and strict mode removed that failure in practitioners' runs.
- **Enforce limits in the handler, not only in the description.** A refund tool rejects an amount over the limit whatever the model sends. A one-time action consumes a single-use token, so a second call fails.
- **The model never fills an amount.** A refund or credit tool takes the case and the evidence, and the handler gets the amount from your policy system. A limit check still lets the model pick any amount under the limit.
- **Build the dedup key from the run id and the call id,** never at call time, because a key generated on each attempt changes on replay. Record times and random values once and reuse them on replay.
- **Mark each tool read-only or state-changing.** Read-only tools can run in parallel and be retried freely; state-changing ones need a dedup key (SKILL.md rule 5) and stay direct calls.

## What tools return

- **Return JSON.** Token-saving formats (TOON, TRON) cut 18% to 27% of tokens but lost 9 to 14 points of accuracy in a 2026 study, and one broke parallel tool calls.
- **Return only the fields the next decision needs,** with ids resolved to names. Tool output can dominate the context, and internal fields ("just in case") cost tokens and leak data.
- **Cap output at about 10K tokens.** For text and logs, keep the head and tail with a marker saying how much was cut. For JSON, page it or offer a `response_format` parameter (concise or detailed), because cutting the middle breaks the structure.
- **Separate what the model sees from what only the UI needs.** Images, price variants, and display data go to a channel the model never reads.
- **A call to a tool that doesn't exist, a timeout, or a human rejection also comes back as a result** (SKILL.md rule 4), so the model can pick another tool or ask the customer.

## Many tools, or many calls

- **Past about 10 tools, or 10K tokens of definitions (either one), try loading definitions on demand and keep it if your evals hold.** Keep the 3 to 5 most used always loaded, and defer whole groups of related tools rather than single ones. OpenAI's function-calling guide gives a soft ceiling of 20 functions per turn and 10 per group loaded on demand. Anthropic measured the gain on 58 tools and 55K tokens (context down 85%, accuracy 49% to 74%), so expect less at a dozen.
- **Let code run 3 or more dependent calls or filter large data,** and show the model only what needs judgment (programmatic tool calling). The program runs in a sandbox that may call only tools you allowlisted. Keep state-changing and high-impact tools as direct calls, so each one stays reviewable.
- **Namespace tools by system** (`intercom_search`, `ledger_search`) so names never collide.
- **Keep the tool list stable within a conversation.** Tools sit in the cached prefix, so adding or removing one mid-conversation breaks the cache on most models. On Claude 5.x models (Opus 5 and 5.5, Sonnet 5.5, Fable 5.1), a mid-conversation `role: "system"` message can add or change a tool without breaking it (beta, 2026-09). Elsewhere, mask a tool's availability instead of removing it.
