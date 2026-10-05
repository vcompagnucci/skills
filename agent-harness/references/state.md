# Durable state

## Where state lives

- **The harness and the session outlive any container.** Keep the session log and state outside the process that runs the loop, so a crash loses nothing and a new worker picks up the run.
- **Keep state on the server.** Browser tabs close and phones lose signal, so a client can't be the source of truth for a run. Token previews streamed to a client are a scratch buffer, never the record: they are neither persisted nor replayed.
- **One active run per conversation.** Route by conversation id or lock it, and a new message follows the delivery modes (loop.md). Two runs answering the same customer contradict each other.
- **Fence out a worker you presumed dead.** A lock or lease doesn't stop it from waking up and writing. Give each attempt a monotonic epoch (a counter that rises with every takeover) and have the session log reject appends from a superseded attempt, so a late tool result or reply from the old worker can't land after its replacement took over.
- **Hooks that observe are separate from checks that control.** Logging and metrics go in hooks. Anything that blocks or changes a call is plain code before and after the model call, where you keep the rejection reason.

## Sessions and the log

- **One conversation thread maps to one session at a time, and may span several.** Store the thread-to-session map as a chain. A hosted session can end for good while the conversation goes on (OpenAI's Agents API ends one on context overflow, an exhausted session budget, or an expired idle environment), so open the next with a handoff summary and the facts still needed.
- **Inbound webhooks arrive at least once, for days.** Acknowledge within the channel's timeout (Slack gives 3 seconds) while the work runs in a queue, and dedupe on the delivery id for as long as the sender retries (OpenAI retries for up to 72 hours). A redelivered webhook otherwise gets two replies.
- **Fetch the current state before acting on a webhook** (verifying the webhook belongs to the security skill). Payloads carry ids, not state, so acting on the payload of a retried delivery applies stale data. Deleting a session sends no webhook and doesn't stop provider compute.
- **Log writes are at-least-once.** Dedupe by entry id, and alert when a batch is dropped, since a dropped batch has no other copy.
- **The log replays exactly what was sent and received.** Persist the rendered system prompt, the tool definitions, and every assistant content block as returned (all block types, in order, including reasoning blocks with empty text), and replay that on every turn and on resume. A serializer that drops empty reasoning blocks loses all reasoning with no error.
- **Never rewrite history in place,** because newer Claude models check reasoning against an unchanged prefix (next bullet). Never re-render the prompt, the tools, or the first user turn from templates, and never shorten, redact, or re-encode an earlier message: shorten a tool result before its first send, put changes in the newest turn, and reference files by a stable id. The one exception is a deliberate clearing or compaction pass at a turn boundary (compaction.md): it changes what you send, never what the log holds.
- **On a history-mismatch 400, retry once with the failing reasoning dropped, and store that choice with the session.** On Claude that is `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` (beta header `thinking-binding-controls-2026-08-01`). Never resend the same body. Newer Claude models reject a changed prefix with a 400 on accounts created from 2026-08-31, while older accounts drop the reasoning silently, so a clean run on your own key proves nothing.
- **When nothing will fetch it later, the log may store a raw tool output as a bounded preview:** head, tail, and a truncation marker, keeping the call's arguments and error flag and recording the original and stored sizes. Keep what the model was sent whole, and set the cap above your largest normal payload so support data is never cut (Codex caps each stored item at 64 KiB).

## Checkpoints

- **Save history after every model call inside the tool loop, not only when the turn ends.** A crash three tool calls into a turn then keeps the finished calls and their results, and replay (failures.md) resumes from the last model call. Write the checkpoint before the next step starts: writing it alongside the step (LangGraph's default) can lose the last step on a crash, and writing only at exit gives no crash recovery.
- **Journal each side effect, not each step.** A tool that made three writes and died after two reruns all three under step-level checkpoints. Store deltas or prune, because a full snapshot per step grows with the conversation.

## Runs in flight

- **Give every run an id that survives retries and redeploys, and give operators pause, resume, cancel, and restart-from-step on it.** Pause every run that depends on a broken tool or a downstream outage instead of letting them burn retries, cancel with compensation (an action that undoes each completed write), and restart from the failed step after a fix, keeping completed work and approvals.
- **Emit a span (one timed record in your trace) when a long run starts, one per attempt with failed retries marked, and one at the end, each published when it closes.** A single span per run shows nothing until a run that paused for days finally ends.
- **On a hosted runtime, work that continues after the reply must keep reporting busy,** or the host reaps the session as idle (AgentCore after 15 minutes, with an 8-hour maximum). Keep the handler non-blocking so health checks still answer, and report a status change only when the status really changes, or sessions never expire and use up the quota.

## Realtime channels

- **Keep the network connection separate from the conversation.** Save the conversation in your store and rebuild the realtime session from it. Reconnect when the provider warns of a drop (a Gemini Live connection lasts about 10 minutes), cap consecutive failed reconnects (Google's ADK gives up after 5), and queue new callers before the provider's concurrency quota rejects them.
- **Decide per tool whether it blocks the conversation.** When a background result arrives, choose whether it interrupts, waits until the agent finishes speaking, or joins the context silently. On barge-in (the customer talking over the agent), keep only what the customer already heard, cancel pending tool calls by id, and stop playback.

## Where the answer depends on the case

- **Postgres or a workflow engine?** One team ran durable agent runs on Postgres alone for five months, with leases, a watchdog for stuck runs, and idempotency keys (Ronacher, 2026-04). Cursor moved its agent loop onto Temporal and went from 90% to over 99% reliability (2026-06). Decide by how many workers share a run and how long runs pause.
