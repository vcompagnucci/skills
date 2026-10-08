# The loop

Failures, streams, and retries are in failures.md; durable state in state.md; versions, latency, cost, and spend caps in operations.md.

## Turns and endings

- **One turn is: build the prompt, call the model, run its tool calls, append the results, repeat until it answers without a tool call.** Each model call is a step, and one user message can take many. Record each message, tool call, result, and approval as its own typed item in order, because one blob with attached calls hides what happened first.
- **Name every way a run ends:** a final answer, new user input, an interrupt, a fatal error after retries, a wait for approval, the step limit, the output limit, and a full context window. Give each a controlled ending.
- **A refusal in the model's own text and an answer that fails its schema return an application fallback** (in a support agent, an apology plus a handoff), validated against the same output schema, without retrying the model or replaying tool side effects. A provider's safety-classifier refusal gets one retry first (failures.md).
- **A response cut by the output limit holds incomplete tool calls: run none of them.** Answer each with a failed result (every call gets one, failures.md), then re-request with a higher output limit or ask the model to continue. Arguments salvaged from a cut stream can pass schema validation and still be incomplete. Asking pays: in Finding the Right Fit (2026-10), 48 of 100 cut runs asked to continue went on to score above zero.
- **A response that filled the context window is truncated, not done, and so is a context-overflow error.** Compact once and retry once as a fresh attempt, never resending the same request. If compaction fails, end with the fallback instead of looping.
- **A provider pause and an empty answer end the response, not the run.** Server tools the provider runs itself (web search, code execution) stop after 10 iterations by default on Claude with stop reason `pause_turn`: send the response back unchanged to continue. An empty final answer right after tool results means your harness appended text after the results: fix the message shape and never send the empty reply.
- **When a turn must end with a result tool (a back-office worker filing its finding), code checks that it was called.** If not, the harness reminds the model at most twice, then returns the fallback. A prompt line asking for it is not enough.
- **"No reply" is a valid end** in a channel where a user's "thanks" needs nothing back. A loop that must always answer sends filler.
- **Release a forced tool call after one call.** If a tool stays required, the model must call it again after every result, forever. Sonnet 5.5 rejects a forced `tool_choice` outright. Send `auto`, mark the tool strict, and say in the prompt when to use it.
- **Every escalation carries a reason in a fixed field.** Anthropic's inbound agent halved its handoffs to humans by reading those reasons and fixing the top ones.

## Stop conditions

- **Set the step cap yourself, from your own distribution of model calls per turn.** Framework defaults range from none to 500 (Vercel's AI SDK agent stops at 20 steps, Google's ADK at 500 model calls, Strands has no cap), and some runtimes return partial output at the cap without raising. Hitting the cap is the step-limit ending, never a finished answer. Count it per user message, across every continuation that a mid-turn message starts, because each continuation gets fresh limits from the provider.
- **At the step limit, make one final call with tool use switched off for that request** (`tool_choice: none`), so the model says what it did and what is still open, validated against the output schema. Never remove the tools to do it, because that invalidates the cache and the earlier reasoning. If that call fails, return the application fallback.
- **Count consecutive tool errors separately from the step cap, and reset the count on any success.** A run that keeps failing stops early (Microsoft's Agent Framework stops after 3 in a row), and a long run with occasional failures continues.
- **When the model repeats the same failing call, answer with the error naming the bad or missing argument and warn that the next repeat ends the run.** End with the fallback only after that, never silently. Ending on the repeat throws the repair away: in Finding the Right Fit (2026-10), 180 of 192 repairs came from the model itself once the harness returned the error, while a harness that ended runs on repeats ended 55 and only 1 of those scored above zero.
- **Show the model a budget for the whole turn, so it wraps up instead of being cut off mid-action.** Size it from your measured per-task distribution and set it once: changing it per request breaks the cache, and a clearly too-small budget makes the model refuse, scope down, or stop early. It's advisory, so keep a hard output cap per request, the step cap above, and the spend caps (operations.md) in code.

## Messages that arrive mid-turn

- **Decide what happens when the user writes again while the agent works, and write the default down.** A support customer, for instance, sends three short messages in a row, so it can't be left to timing. A per-user debounce that starts a run only after messages stop arriving absorbs a burst. Implement the rest as delivery modes:
  - next: deliver when the running tool calls finish, inside the same turn.
  - later: hold for a new turn.
  - now: move tool calls that can keep running to the background and deliver at once. Feed in each background result when it lands, one per call, each as a new message after the batch is answered.
  - append: add context without a model call.
- **A message that joins a running turn rewrites nothing and cancels nothing.** The current output and any started tool finish first. The pending queue lives only on the connection, so record what you injected and reconcile it against history after a disconnect before resending.
- **An interrupt stops model output at once but waits for running tools to finish.** The provider may report the interrupted turn as an ordinary end (Claude's Managed Agents has no interrupt stop reason), so record the interrupt in your own log.
- **Tell the model what it couldn't see.** Before every model call, inject events that arrived while the agent worked, so it acts on the current state. Say when the user interrupted on purpose, that an interrupted tool may have partly run, and the current time. On Claude, relay operator facts mid-turn as a `role: "system"` message after the tool results, never mixed into the user's text.
- **When the user changes a request mid-task, update the active task and drop results that come back for the old version.** Tag delegated work with a task id or version, so a late result, including one from a previous session after a reconnect, can't overwrite newer work.
- **Give every user message you submit to the agent an idempotency key.** Create it once, save it with the message before sending, and reuse it on any retry after a timeout or a lost response, so a retry can't start a second turn. Make a new key for each distinct submission, even when the text is identical.
- **A retry of a request that is still running attaches to it and gets the same result.** Match it by idempotency key (above), and give waiters an explicit "aborted" error if the original is cancelled. A different request on the same conversation never runs alongside it (state.md): it follows the delivery modes above or is rejected. Without a guard, overlapping writes to one session overwrite each other and neither call errors.
- **Limit concurrent runs per tenant, team, and user, nested, and let resumed runs go ahead of new ones.** One account's burst or a provider slowdown then can't starve the rest (Restate's example: 1,000 per org, 100 per team, 10 per user).

## Runs longer than one context window

A support conversation fits in one window. Back-office work (a batch of reviews, an investigation) may not.

- **Give the run a goal with a completion condition and evidence:** what must be true, how to check it, what must not regress, when to stop as blocked. An exhausted budget ends in a summary, never in "done".
- **Check progress in a structured way every round:** is the request satisfied, are we looping, are we making progress, what comes next. After 3 consecutive rounds without progress, replan; after 2 replans, stop as blocked and end in a summary (Microsoft's Magentic defaults), so a stuck run doesn't spend its whole budget.
- **Keep progress in files the agent rereads:** the goal, a plan with checkable milestones, a status log that records failed approaches too. A fresh session gets its bearings from them instead of from a summary.
