# Tools

## Which tools

- **A tool must know, do, or show something:** bring data the model lacks (the customer's account, a transfer's status), take a real action, or present information better than text. A tool that does none of these is noise the model has to weigh.
- **Group tools by the customer's intent, not by your API's endpoints.** One `get_withdrawal_status` beats `list_withdrawals` plus `get_withdrawal` plus `get_network_fee`. Each extra tool is one more choice the model can get wrong.
- **Overlap matters more than count.** Agents handle 15 distinct tools and fail with fewer than 10 overlapping ones. If a person can't say which tool fits a situation, the model can't either. Fix names and descriptions before splitting into more agents.
- **Business actions are typed tools with structured returns.** Keep generic helpers (shell, file reading) out of a support agent unless a job needs them.
- **Test each tool against the no-tool baseline** on a few positive, negative, and edge cases. A tool that doesn't beat the model's answer without it goes.

## Arguments and descriptions

- **The description is a prompt.** Say what the tool does, when to use it, when not to, and what it returns, as you would to a new hire. Name parameters unambiguously (`customer_id`, not `id`). A description fix changes behavior more than a schema change does.
- **Give allowed values as enums** (`network: "TRC20" | "ERC20"`), so the model maps the customer's words to a value instead of guessing which exist.
- **Turn on strict schemas.** Newer models invent keys without them, and strict mode removed that failure in practitioners' runs.
- **The customer id is never an argument.** The harness attaches it from the authenticated session (SKILL.md rule 3). The same goes for anything that sets scope: the channel, the account, the tenant.
- **Enforce limits in the handler, not only in the description.** A refund tool rejects an amount over the limit whatever the model sends. A one-time action consumes a single-use token, so a second call fails.
- **Mark each tool read-only or state-changing,** and give every state-changing tool a dedup key (SKILL.md rule 5).

## What tools return

- **Return only the fields the next decision needs,** with ids resolved to names. Tool output can dominate the context, and internal fields ("just in case") cost tokens and leak data.
- **Cap output at about 10K tokens, keeping the head and tail,** with a marker saying how much was cut, so the model knows it saw part of the result.
- **Errors say what to do next.** "Withdrawal blocked: KYC pending. Ask the customer to finish verification in the app" lets the model recover. A traceback doesn't.
- **Separate what the model sees from what only the UI needs.** Images, price variants, and display data go to a channel the model never reads.
- **A call to a tool that doesn't exist, a timeout, or a human rejection comes back as a result,** so the model can pick another tool or ask the customer.

## Many tools, or many calls

- **Load tool definitions on demand past about 10 tools or 10K tokens of definitions,** keeping the 3 to 5 most used always loaded. Deferred loading with tool search cut context 85% and raised accuracy from 49% to 74% in Anthropic's test.
- **Let code run 3 or more dependent calls or filter large data,** and show the model only what needs judgment (programmatic tool calling). Keep state-changing and high-impact tools as direct calls, so each one stays reviewable.
- **Namespace tools by system** (`intercom_search`, `ledger_search`) so names never collide.
- **Keep the tool list stable within a conversation.** Tools sit in the cached prefix, so adding or removing one mid-conversation breaks the cache on most models. On Claude 5.x a mid-conversation `role: "system"` message can add or change a tool without breaking it (beta, 2026-09). Elsewhere, mask a tool's availability instead of removing it.
