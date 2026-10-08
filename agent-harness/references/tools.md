# Tools

## Which tools

- **A tool must know, do, or show something:** bring data the model lacks (the customer's account, a transfer's status), take a real action, or present information better than text. A tool that does none of these is noise the model has to weigh.
- **Group tools by the user's intent, not by your API's endpoints.** One `get_withdrawal_status` beats `list_withdrawals` plus `get_withdrawal` plus `get_network_fee`. Each extra tool is one more choice the model can get wrong.
- **Overlap matters more than count.** OpenAI saw some agents handle 15 or more distinct tools while others failed with fewer than 10 overlapping ones. If a person can't say which tool fits a situation, the model can't either. Fix names and descriptions before splitting into more agents.
- **Business actions are typed tools with structured returns.** A support agent gets no shell or file-reading tools. No support task needs them, and each one is a choice the model can get wrong.
- **A tool that doesn't beat the model's answer without it goes;** measure that with agent-evals.

## Arguments and descriptions

- **The description is a prompt.** Say what the tool does, when to use it, when not to, what it returns, and its own limits (a time limit, a page size), as you would to a new hire, so the model plans around them. Name parameters unambiguously (`customer_id`, not `id`). A description fix changes behavior more than a schema change does.
- **Give allowed values as enums** (`network: "TRC20" | "ERC20"`), so the model maps the user's words to a value instead of guessing which exist.
- **Turn on strict schemas.** Newer models invent keys without them, and strict mode removed that failure in Ronacher's runs (2026-07).
- **Never put a `reasoning`, `thinking`, or `trace` field in a tool schema** on Claude Fable 5 and 5.1, Opus 5 and 5.5, or Sonnet 5.5. It triggers a billed refusal with no fallback model; ask for a short explanation or the evidence behind the call instead.
- **Enforce limits in the handler, not only in the description.** A refund tool rejects an amount over the limit whatever the model sends. A one-time action consumes a single-use token, so a second call fails.
- **The model never fills an amount.** A refund or credit tool takes the case and the evidence, and the handler gets the amount from your policy system. A limit check still lets the model pick any amount under the limit.
- **Build the idempotency key from the run id and the call id,** never at call time, because a key generated on each attempt changes on replay. Record times and random values once and reuse them on replay.
- **Mark each tool read-only or state-changing.** Read-only tools can run in parallel and be retried freely; state-changing ones need an idempotency key (SKILL.md rule 5), stay direct calls, and run one after another by default. If you do run state-changing calls in parallel, only across different resources: two calls on the same account or record always queue in order.

## What tools return

- **Return JSON, as text or a content block,** never a raw object, number, or boolean (Claude Code hit API errors on those). Token-saving formats (TOON, TRON) cut 18% to 27% of tokens but lost 9 to 14 points of accuracy in a 2026 study, and one broke parallel tool calls.
- **Return only the fields the next decision needs,** with ids resolved to names. Tool output can dominate the context, and internal fields ("just in case") cost tokens and leak data.
- **Log a warning when one result passes about 10K tokens, and cap it around 25K.** Let each tool set its own cap. This cap is for what the model sees: context.md's 10K is for items the harness injects, and state.md's 64 KiB is for log storage.
- **Above the cap, store the full result where the agent can fetch it** and return a preview plus the reference (a file path, or a page or fetch id for an agent without file tools), so nothing is lost. For text and logs, the preview is the head and tail with a marker saying how much was cut. For JSON, page it or offer a `response_format` parameter (concise or detailed), because cutting the middle breaks the structure.
- **Measure the cap on the serialized result.** Escaping and the result wrapper add bytes, so a preview cut to size can still overflow: shrink it until the whole serialized result fits, and make truncation idempotent, so cutting an already-cut result changes nothing.
- **Answer a parallel batch in one message:** one result per call, all in the next message, results before any text. Splitting results across messages is the most common mistake and teaches the model to stop calling in parallel. Re-check how much the model parallelizes after a model change, since Claude Fable 5.1 issues fewer parallel calls in long loops. OpenAI's Responses multi-agent is the one exception (multi-agent.md).
- **Separate what the model sees from what only the UI needs.** Images, price variants, and display data go to a channel the model never reads.
- **A call to a tool that doesn't exist, a timeout, or a human rejection also comes back as a result** (SKILL.md rule 4), so the model can pick another tool or ask the user.

## Many tools, or many calls

- **Past about 10 tools, or 10K tokens of definitions (either one), try loading definitions on demand and keep it if your evals hold.** Keep the 3 to 5 most used always loaded, and defer whole groups of related tools rather than single ones. OpenAI's function-calling guide gives a soft ceiling of 20 functions per turn and 10 per group loaded on demand. Anthropic measured the gain on 58 tools and 55K tokens (context down 85%, accuracy 49% to 74%), so expect less at a dozen.
- **Pick tools on demand at each step as the work unfolds, never once from the user's first message.** On implicit multi-step requests, one-shot retrieval found only 46% to 58% of the tools needed, and accuracy fell to 0.139, against 0.418 with the whole tool set and 0.438 when retrieving before each step (Claude 4, Amazon's TRAJECT-Bench).
- **Let code run 3 or more dependent calls or filter large data,** and show the model only what needs judgment (programmatic tool calling). The program runs in a sandbox that may call only tools you allowlisted. Keep state-changing and high-impact tools as direct calls, so each one stays reviewable.
- **Make that program replayable.** Record each call's result, so a replay after a crash re-runs the script against the recorded results instead of calling tools again. Give the script the run's clock and a seeded random source, raise tool failures inside it, and stop a script that computes for over a second without calling a tool.
- **Namespace tools by system** (`intercom_search`, `ledger_search`) so names never collide.
- **Keep the tool list stable within a conversation.** Tools sit in the cached prefix, so adding or removing one mid-conversation breaks the cache on most models. On Claude 5.x models (Opus 5 and 5.5, Sonnet 5.5, Fable 5.1), a mid-conversation `role: "system"` message can add or change a tool without breaking it (beta, 2026-09). Elsewhere, mask a tool's availability instead of removing it, and have MCP servers list tools in a fixed order for the same reason.
- **Keep a tool listed when its backend is down.** While a backend is starting, failed, or unreachable, keep the tool and its parameters listed and return the same "unavailable, wait" result each time. Never make a description depend on runtime state, and enforce policy when the call runs instead of hiding parameters, because a changed description breaks the cache like a changed tool.

## State across calls

- **When a tool creates state that later calls use** (a draft, a pending transfer), return an opaque handle and take it as an argument on later calls. State the handle's lifetime in the creating tool's description, and make a call with an expired or unknown handle return an error that says so, so the model creates a new one. MCP dropped protocol sessions on 2026-07-28, so this is how state crosses MCP calls too.
- **On MCP, a broken response stream loses the request in flight,** and the client re-issues it as a new request, so every state-changing MCP tool needs its own idempotency key.
- **Long-running work returns a task handle the client polls instead of holding a stream open.** A remote tool may answer with a durable task instead of a result (MCP's tasks extension), and the server decides per request, so handle both shapes. Save the task id with the run before polling, poll no faster than the server's interval until a terminal state, and answer its input requests through the task.
- **Treat cancelling a task as a request:** read the task's final state before telling the user it stopped.
- **A tool that needs more input from a person ends the call with `input_required` and an opaque state token** (humans.md covers the client side; verifying the token belongs to the security skill).
