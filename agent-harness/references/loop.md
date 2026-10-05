# The loop

## Turns and endings

- **One turn is: build the prompt, call the model, run its tool calls, append the results, repeat until it answers without a tool call.** One customer message can take many model calls. Record each message, tool call, result, and approval as its own typed item in order, because one blob with attached calls hides what happened first.
- **Name every way a run ends:** a final answer, new customer input, an interrupt, a fatal error after retries, a wait for approval, or the turn limit. Give each a controlled ending. The turn limit, a refusal, and an answer that fails its schema each return an application fallback (an apology plus a handoff), validated against the same output schema, without retrying the model or replaying tool side effects.
- **History holds what the customer actually saw.** If you stream and a check on the output fires late, cancel the reply, cut the history at what was delivered, and tell the model which check fired so it answers again.
- **Give each run a spending budget.** Reserve the worst-case cost before each model call and settle to the real cost after. When a charge is uncertain (a timed-out call may still bill), stop the run, and turn off automatic client retries, which spend money nobody reserved.
- **When a turn must end with a result tool (a back-office worker filing its finding), code checks that it was called.** If not, the harness reminds the model at most twice, then returns the fallback. A prompt line asking for it is skipped some fraction of the time.
- **"No reply" is a valid end** in a channel where a customer's "thanks" needs nothing back. A loop that must always answer sends filler.
- **Release a forced tool call after one call.** If a tool stays required, the model must call it again after every result, forever. Sonnet 5.5 rejects a forced `tool_choice` outright. Send `auto`, mark the tool strict, and say in the prompt when to use it.
- **Every escalation carries a reason in a fixed field.** Anthropic's inbound agent halved its handoffs to humans by reading those reasons and fixing the top ones.

## Messages that arrive mid-turn

- **Decide what happens when the customer writes again while the agent works:** queue it for the next turn, add it to the current turn, or interrupt. A support customer sends three short messages in a row, so the default has to be written down, not left to timing.
- **Tell the model what it couldn't see.** Say when the customer interrupted on purpose, that an interrupted tool may have partly run, and the current time. On Claude, relay operator facts mid-turn as a `role: "system"` message after the tool results, never mixed into the customer's text.

## Failures and retries

- **Know which calls are still owed.** In OpenAI's Agents API only `required_actions` lists pending calls; a tool call in the history doesn't prove a result is still owed. Store each result by session, turn, and call id.
- **An idle session is not success.** Read the turn's completed, failed, or cancelled status. A completed turn can still hold a failed tool.
- **Sort every tool failure into a fixed class** (timeout, bad arguments, not found, upstream error). A failure that fits no class is a harness bug to fix, and a class rising above its usual rate raises an alert, so a broken tool shows up the day it breaks.
- **A timeout on a state-changing call is an unknown outcome,** not a transient error. Read the real state, or retry only with the same dedup key, because the first call may still land. Never retry a model call after its output started streaming.
- **Retry only transient errors** (overload, a timeout on a read), with backoff, jitter, and an attempt limit, honoring the server's Retry-After. Quota, billing, and policy errors are terminal. They need a person, not a faster retry. Stop retrying when the error changes. Provider client libraries also retry on their own (OpenAI's and Anthropic's twice by default, with a 10-minute timeout), so set their retries to 0 and keep one retry policy in your harness, or your backoff stacks on theirs and a timeout surfaces ten minutes late.
- **When the model provider fails** (5xx, rate limits, a call slower than your p99), fail over to the same model snapshot on a second host. Switching to a different model loses the cache and changes behavior mid-conversation.
- **Put a clock on everything:** a timeout per model call and per tool call, a deadline for the whole run, and a no-progress timer. No SDK bounds the whole run for you.
- **Replay from the last checkpoint, not from the start,** so model calls and tool calls that finished don't run again.

## Durable state

- **The harness and the session outlive any container.** Keep the session log and state outside the process that runs the loop, so a crash loses nothing and a new worker picks up the run. Postgres alone carried one team's durable agent runs for five months; you need leases, a watchdog for stuck runs, and dedup keys more than you need a workflow engine.
- **One active run per conversation.** Route by conversation id or lock it, and a new message waits under the mid-turn rule above. Two runs answering the same customer contradict each other.
- **Log writes are at-least-once.** Dedupe by entry id, and alert when a batch is dropped, since a dropped batch has no other copy.
- **One conversation thread is one session.** Store the thread-to-session map, ignore repeated webhook deliveries of the same message, and acknowledge within the channel's timeout (Slack gives 3 seconds) while the work runs in the background. A redelivered webhook otherwise gets two replies.
- **Keep state on the server.** Browser tabs close and phones lose signal, so a client can't be the source of truth for a run.
- **Hooks that observe are separate from checks that control.** Logging and metrics go in hooks. Anything that blocks or changes a call is plain code before and after the model call, where you keep the rejection reason.

## Versions

- **Every change to prompt, model, or tools is a new pinned version,** tested on a staging copy before production. After staging, give a new version a small share of new conversations (Ada starts at 1%), then widen. Rollback is re-pinning the last good version, but keep the newer version runnable until the runs it paused drain, because older code rejects state saved by newer code. Edits to a saved agent reach only new sessions, so a running conversation finishes on its version. Anthropic's sales team rolled back to an older version after a week, and could only because versions were pinned.
- **Re-test after a model change before tuning anything else.** Remove workarounds written for the old model first (retry shims, "do not be lazy"), then measure.

## Latency and cost

- **Anything repeated inside the loop is paid on every model call.** Cut re-sent history and run independent tool calls in parallel before buying a faster model.
- **In chat, end the turn at the first question the agent has to ask anyway** instead of gathering everything first. Rappi cut its first turn from over 60 seconds to 20.
- **Move work that doesn't change the reply off the customer's path:** QA scoring, tagging, summaries, and memory writing run after the reply is sent.
- **Route models per step, not per message.** A small model classifies and handles routine questions; the largest takes account access and disputes. Never switch the model inside one conversation, because each model has its own cache and reasoning format; send the step to a subagent on the other model instead.

## Runs longer than one context window

A support conversation fits in one window. Back-office work (a batch of reviews, an investigation) may not.

- **Give the run a goal with a completion condition and evidence:** what must be true, how to check it, what must not regress, when to stop as blocked. "Blocked" is allowed only after the same blocker repeats for 3 consecutive turns, and an exhausted budget ends in a summary, never in "done".
- **Keep progress in files the agent rereads:** the goal, a plan with checkable milestones, a status log that records failed approaches too. A fresh session gets its bearings from them instead of from a summary.

## Where the answer depends on the case

- **Does a slower reply hurt?** Fin measured no drop in resolution for delays up to 20 seconds in web chat (2025-04). Rappi, newer and on WhatsApp, cut turns because waiting hurt (2026-09). Decide by channel, and measure it.
