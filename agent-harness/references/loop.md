# The loop

## Turns and endings

- **One turn is: build the prompt, call the model, run its tool calls, append the results, repeat until it answers without a tool call.** One customer message can take many model calls. Record each message, tool call, result, and approval as its own typed item in order, because one blob with attached calls hides what happened first.
- **Name every way a run ends:** a final answer, new customer input, an interrupt, a fatal error after retries, a wait for approval, or the turn limit. Give each a controlled ending. The turn limit, a refusal, and an answer that fails its schema each return an application fallback (an apology plus a handoff), validated against the same output schema, without retrying the model or replaying tool side effects.
- **"No reply" is a valid end** in a channel where a customer's "thanks" needs nothing back. A loop that must always answer sends filler.
- **Release a forced tool call after one call.** If a tool stays required, the model must call it again after every result, forever. On Claude 5.x a forced `tool_choice` is rejected outright: send `auto`, mark the tool strict, and say in the prompt when to use it.
- **Every escalation carries a reason in a fixed field.** Anthropic's inbound agent halved its handoffs to humans by reading those reasons and fixing the top ones.

## Messages that arrive mid-turn

- **Decide what happens when the customer writes again while the agent works:** queue it for the next turn, add it to the current turn, or interrupt. A support customer sends three short messages in a row, so the default has to be written down, not left to timing.
- **Tell the model what it couldn't see.** Say when the customer interrupted on purpose, that an interrupted tool may have partly run, and the current time. On Claude, relay operator facts mid-turn as a `role: "system"` message after the tool results, never mixed into the customer's text.

## Failures and retries

- **An unknown outcome is not a failure.** A dropped stream, a lost acknowledgement, or a crashed turn may already have changed the account. Re-read the real state, then continue only the unfinished work.
- **Know which calls are still owed.** In OpenAI's Agents API only `required_actions` lists pending calls; a tool call in the history doesn't prove a result is still owed. Store each result by session, turn, and call id.
- **An idle session is not success.** Read the turn's completed, failed, or cancelled status. A completed turn can still hold a failed tool.
- **Retry only transient errors** (timeouts, overload), with backoff, jitter, and an attempt limit, honoring the server's Retry-After. Quota, billing, and policy errors are terminal: they need a person, not a faster retry. Stop retrying when the error changes.
- **Replay from the last checkpoint, not from the start,** so model calls and tool calls that finished don't run again.

## Pausing for a human

- **An approval or a question to your team pauses the run; it doesn't end it.** The run records the pending call, the state goes to your server, compute is released, and the same run resumes when the answer comes, minutes or hours later.
- **Keep the sibling results.** If a turn called two tools and one needs approval, store the finished one's result before pausing. OpenAI's SDK fixed exactly this: without it, the model is called again and `submit_order` runs twice.
- **An approval belongs to the turn that asked for it.** A later turn doesn't inherit a one-time approval.
- **Paused state is data you control.** Keep it on your server and authenticate whoever answers. A paused run restored from a client copy can be edited.
- **Store the version with the state.** A run paused before you shipped a new prompt resumes on the version it started with.

## Durable state

- **The harness and the session outlive any container.** Keep the session log and state outside the process that runs the loop, so a crash loses nothing and a new worker picks up the run. Postgres alone carried one team's durable agent runs for five months; you need leases, a watchdog for stuck runs, and dedup keys more than you need a workflow engine.
- **Keep state on the server.** Browser tabs close and phones lose signal, so a client can't be the source of truth for a run.
- **Hooks that observe are separate from checks that control.** Logging and metrics go in hooks. Anything that blocks or changes a call is plain code before and after the model call, where you keep the rejection reason.

## Versions

- **Every change to prompt, model, or tools is a new pinned version,** tested on a staging copy before production. Rollback is re-pinning the last good version. Anthropic's sales team rolled back to an older version after a week, and could only because versions were pinned.
- **Re-test after a model change before tuning anything else.** Remove workarounds written for the old model first (retry shims, "do not be lazy"), then measure.

## Latency

- **Anything repeated inside the loop is paid on every model call.** One customer turn can hold many calls, so cut repeated work (re-sent context, sequential tool calls that could run in parallel) before buying a faster model.
- **A persistent connection to the model API cut loop time up to 40%,** at the price of one response at a time per connection and lost state on reconnect. Keep a local copy of the conversation you can rebuild from, and use plain HTTP streaming where reliability matters more than speed.

## Runs longer than one context window

Support conversations rarely need this. Back-office work (a batch of reviews, an investigation) does.

- **Give the run a goal with a completion condition and evidence:** what must be true, how to check it, what must not regress, when to stop as blocked. "Blocked" is allowed only after the same blocker repeats for 3 consecutive turns, and an exhausted budget ends in a summary, never in "done".
- **Keep progress in files the agent rereads:** the goal, a plan with checkable milestones, a status log that records failed approaches too. A fresh session gets its bearings from them instead of from a summary.
