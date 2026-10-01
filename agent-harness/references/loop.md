# The loop

## Turns and endings

- **One turn is: build the prompt, call the model, run its tool calls, append the results, repeat until it answers without a tool call.** One customer message can take many model calls. Record each message, tool call, result, and approval as its own typed item in order, because one blob with attached calls hides what happened first.
- **Name every way a run ends:** a final answer, new customer input, an interrupt, a fatal error after retries, a wait for approval, or the turn limit. Give each a controlled ending. The turn limit, a refusal, and an answer that fails its schema each return an application fallback (an apology plus a handoff), validated against the same output schema, without retrying the model or replaying tool side effects.
- **History holds what the customer actually saw.** If you stream and a check on the output fires late, cancel the reply, cut the history at what was delivered, and tell the model which check fired so it answers again.
- **Give each run a spending budget.** Reserve the worst-case cost before each model call and settle to the real cost after. When a charge is uncertain (a timed-out call may still bill), stop the run, and turn off automatic client retries, which spend money nobody reserved.
- **"No reply" is a valid end** in a channel where a customer's "thanks" needs nothing back. A loop that must always answer sends filler.
- **Release a forced tool call after one call.** If a tool stays required, the model must call it again after every result, forever. Sonnet 5.5 rejects a forced `tool_choice` outright. Send `auto`, mark the tool strict, and say in the prompt when to use it.
- **Every escalation carries a reason in a fixed field.** Anthropic's inbound agent halved its handoffs to humans by reading those reasons and fixing the top ones.

## Messages that arrive mid-turn

- **Decide what happens when the customer writes again while the agent works:** queue it for the next turn, add it to the current turn, or interrupt. A support customer sends three short messages in a row, so the default has to be written down, not left to timing.
- **Tell the model what it couldn't see.** Say when the customer interrupted on purpose, that an interrupted tool may have partly run, and the current time. On Claude, relay operator facts mid-turn as a `role: "system"` message after the tool results, never mixed into the customer's text.

## Failures and retries

- **Know which calls are still owed.** In OpenAI's Agents API only `required_actions` lists pending calls; a tool call in the history doesn't prove a result is still owed. Store each result by session, turn, and call id.
- **An idle session is not success.** Read the turn's completed, failed, or cancelled status. A completed turn can still hold a failed tool.
- **Retry only transient errors** (timeouts, overload), with backoff, jitter, and an attempt limit, honoring the server's Retry-After. Quota, billing, and policy errors are terminal. They need a person, not a faster retry. Stop retrying when the error changes.
- **Replay from the last checkpoint, not from the start,** so model calls and tool calls that finished don't run again.

## Pausing for a human

- **On resume, take ownership of the run first, then reload its history,** because the saved snapshot may be stale if another worker touched it.
- **Keep the sibling results.** If a turn called two tools and one needs approval, store the finished one's result before pausing. OpenAI's SDK fixed exactly this. Without it, the model is called again and `submit_order` runs twice.
- **An approval belongs to the turn that asked for it.** A later turn asks for something different, and reusing the earlier yes approves an action nobody looked at.

## A person takes over

- **The conversation has one owner at a time, stored in state, and code checks it before every agent reply.** While a person owns it, the agent doesn't answer. A prompt that says "stay quiet while a human handles this" fails the first time the customer writes again.
- **The model picks a named outcome; code carries it out.** The agent chooses "hand to KYC team" with its reason, and code replies to the customer, tags, reassigns, and closes in a fixed order, so no step is skipped.
- **Escalate on two triggers:** failures crossing a threshold you set, or an action that is high-risk and irreversible. An optional question to the customer proceeds after a short wait on a stated assumption; a required approval blocks. Elapsed time is never an approval.
- **Two modes, kept apart:** the agent asks your team a private question and keeps the conversation, or a person takes the conversation. The first is a pause (above); the second changes the owner.
- **When the conversation comes back, the agent reads what the person did** (their messages, actions, and notes in the log) before replying, and any run paused before the takeover is discarded, not resumed.

## When a conversation ends

- **Define the end in code:** an explicit close, or an idle timeout you choose. The end of a conversation triggers the memory pass (context-memory.md) and discards paused runs that can no longer resume. Without a defined end, both happen never or at random.

## Durable state

- **The harness and the session outlive any container.** Keep the session log and state outside the process that runs the loop, so a crash loses nothing and a new worker picks up the run. Postgres alone carried one team's durable agent runs for five months; you need leases, a watchdog for stuck runs, and dedup keys more than you need a workflow engine.
- **One conversation thread is one session.** Store the thread-to-session map, ignore repeated webhook deliveries of the same message, and acknowledge within the channel's timeout (Slack gives 3 seconds) while the work runs in the background. A redelivered webhook otherwise gets two replies.
- **Keep state on the server.** Browser tabs close and phones lose signal, so a client can't be the source of truth for a run.
- **Hooks that observe are separate from checks that control.** Logging and metrics go in hooks. Anything that blocks or changes a call is plain code before and after the model call, where you keep the rejection reason.

## Versions

- **Every change to prompt, model, or tools is a new pinned version,** tested on a staging copy before production. Rollback is re-pinning the last good version. Edits to a saved agent reach only new sessions, so a running conversation finishes on its version. Anthropic's sales team rolled back to an older version after a week, and could only because versions were pinned.
- **Re-test after a model change before tuning anything else.** Remove workarounds written for the old model first (retry shims, "do not be lazy"), then measure.

## Latency and cost

- **Anything repeated inside the loop is paid on every model call.** Cut re-sent history and run independent tool calls in parallel before buying a faster model.
- **Move work that doesn't change the reply off the customer's path:** QA scoring, tagging, summaries, and memory writing run after the reply is sent.
- **Route models per step, not per message.** A small model classifies and handles routine questions; the largest takes account access and disputes. Never switch the model inside one conversation, because each model has its own cache and reasoning format; send the step to a subagent on the other model instead.

## Runs longer than one context window

A support conversation fits in one window. Back-office work (a batch of reviews, an investigation) may not.

- **Give the run a goal with a completion condition and evidence:** what must be true, how to check it, what must not regress, when to stop as blocked. "Blocked" is allowed only after the same blocker repeats for 3 consecutive turns, and an exhausted budget ends in a summary, never in "done".
- **Keep progress in files the agent rereads:** the goal, a plan with checkable milestones, a status log that records failed approaches too. A fresh session gets its bearings from them instead of from a summary.
