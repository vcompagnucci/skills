# Failures, streams, and recovery

## Failures and retries

- **Retry only transient errors** (overload, a timeout on a read), with backoff, jitter, and an attempt limit. Without an idempotency key, retry a write only when the failure is confirmed to have happened before the write. Stop retrying when the error changes.
- **Honor the server's Retry-After wherever it arrives.** It can come inside a streamed failure event: parse it there, and prefer a valid header over a delay stated in the error text. After a shared outage, jitter each reconnect uniformly between half and all of the current backoff, capped at 30 s.
- **Quota, billing, and policy errors are terminal.** They need a person, not a faster retry. On the Claude API, a 429 without a retry-after header is a spend cap, so it's terminal too.
- **Keep one retry budget per model call across every layer,** or the backoffs stack and a timeout surfaces ten minutes late. Provider client libraries retry on their own (OpenAI's and Anthropic's twice by default, with a 10-minute timeout), and durable engines add a third layer with defaults from none (DBOS steps) to unlimited (Temporal activities).
- **Set client retries to 0 and mark terminal errors non-retryable in each durable step's retry policy.** Keep attempt counts and backoff in the durable store, since an in-process counter dies with the process.
- **A timeout on a state-changing call is an unknown outcome,** not a transient error. Read the real state, or retry only with the same idempotency key, because the first call may still land.
- **A result that came back oversized, unparseable, or over a dropped connection means the call already ran: never re-run it.** Claude Code ran MCP calls twice on results over 16 MB until it fixed this. A dropped MCP response stream is a cancellation that can't be resumed, while the server may already have acted.
- **Sort every tool failure into a fixed class** (timeout, bad arguments, not found, upstream error). A failure that fits no class is a harness bug to fix, and a class rising above its usual rate raises an alert, so a broken tool shows up the day it breaks.
- **Know which calls are still owed, and give every call exactly one result with its id.** Calls that were skipped, cancelled, denied, or cut by a limit get a result too, or the next model call fails or the transcript becomes invalid (Gemini 3.x rejects any mismatch in count, name, or id). Store each result by session, turn, and call id. In OpenAI's Agents API only `required_actions` lists pending calls; a tool call in the history doesn't prove a result is still owed.
- **An idle session is not success.** Read the turn's completed, failed, or cancelled status. A completed turn can still hold a failed tool.
- **Replay from the last checkpoint, not from the start,** so model calls and tool calls that finished don't run again. How often to checkpoint: state.md.

## Refusals and provider failures

- **Three kinds of "no", three handlings:**
  - The model declining in its own text gets the fallback (loop.md).
  - A safety-classifier refusal (a successful response with a refusal stop reason) gets one retry on another model (next bullet).
  - A provider safety stop (OpenAI's 403 `misalignment_policy_violation`) is terminal for the conversation. Stop dispatching its actions, don't retry, keep the request and response ids, and hand it to a person to review what already ran. The check is asynchronous, so actions may already be done, it can arrive mid-stream after output started, and there is no API to resume.
- **A safety-classifier refusal arrives as a successful response, so error-rate monitoring never sees it.** Emit one event per refusal and one per reply served by a fallback. It's the one model switch allowed inside a turn: retry once on a different model, since the same model usually refuses again, prefer the same family, keep sending the full history, and keep the conversation on the model that answered instead of bouncing back. Budget these retries per request and give subagent calls their own fallback.
- **When the model provider fails** (5xx, rate limits, a call slower than your p99), **fail over to the same model snapshot first, on a host whose account is linked to the primary.** Caches are isolated per workspace or account and aren't shared across speed tiers, and on newer Claude models reasoning works only in the account that produced it, so an unlinked host costs a full-price first turn without the earlier reasoning. A cheap tier that's out of capacity falls back to the standard tier for later turns.
- **Keep one model per conversation by default.** Switch only at a turn boundary where the cache is already lost (after compaction or cache expiry) or under persistent provider overload, prefer the same family, and keep sending the full history so the provider drops only what the new model can't read. Tell the model about the switch, and never strip reasoning in your own code: it comes back if you switch back.

## Timeouts

- **Put a clock on everything:** a timeout per model call and per tool call, a deadline for the whole run, and a no-progress timer. No SDK bounds the whole run for you. A paused run waits under its own approval deadline instead (humans.md). A timeout that resets on progress notifications (MCP allows it) still needs a hard maximum. Every blocking check gets its own timeout and an explicit failure mode.
- **A stream that can sit idle while a slow tool or check runs needs TCP keepalive below the network's idle timeout** (350 s behind an AWS NAT gateway) and a client read timeout above the longest expected silence, or the connection drops without an error.

## Streams

- **History holds what the user actually saw.** If you stream and a check on the output fires late, cancel the reply, cut the history at what was delivered, and tell the model which check fired so it answers again.
- **Recover a failed model call by how far the response got, not by whether bytes streamed:**
  - Nothing completed: re-issue and discard the partial.
  - Reasoning done but no text or tool call yet: re-issue, at most twice.
  - A text block or tool call completed: keep it and continue from it (newer Claude models continue from a user message quoting the partial output). A partial tool call or reasoning block can't be resumed.
  - Finished: keep it.
- **Text already delivered to a user through a channel counts as completed,** because it can't be rewound. When you retry a step that streamed to a client you control, send a reset event so the client drops the partial instead of appending the retry to it.
- **Detect a dead stream with a first-byte deadline and a no-bytes watchdog, not the whole-request timeout.** Claude Code allows 180 s to the first byte on the direct API and 180 s of byte silence, against a 600 s whole-request timeout. Re-issue a stalled request at most once. Every re-issue in this section spends the call's one retry budget (Failures and retries).
- **A dropped connection is not a cancel** (an explicit stop is in humans.md). Keep the run going when a tab closes or a phone drops, let the client reconnect by run id and stream cursor, and treat a stream that ends without a finish event as interrupted. Never rerun the work, and never pass the HTTP abort signal into the model call, because it kills the work a reconnect expects to find.
- **Reconnect with a buffer and a snapshot.** Open the stream before sending work. After a drop, open a new stream and buffer its events, fetch the session's saved items or full event history, rebuild local state keyed by item id, apply the buffered events while skipping ids already seen or final, then resume. Rebuild pending approvals from the session's pending-actions list, never from history, and never resend the task or earlier approvals.
- **Run back-office model calls that may take minutes as background jobs with an id.** Stream with the event sequence number as a cursor and reattach from it after a drop instead of resending; cancel is idempotent. Keep them off the reply path, because their time to first token is higher.
