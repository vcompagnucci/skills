# Humans in the loop

How the harness pauses for a person, hands the conversation over, and ends it. Who may approve what is a security question.

## Pausing for a human

- **A checkpoint holds** the transcript, pending calls and approvals, finished sibling results, queued user messages, the conversation's owner, usage so far, and the agent version.
- **Wait in process only for an answer that arrives in seconds.** When a person may take minutes or days, end the process at the tool call: record the pending call, exit, and on resume re-run that call's check with the answer. Allow this only on a turn with a single call, or after storing the sibling results (below), and on resume check that the tool still exists before re-running it.
- **Know which resume mode each step uses:**
  - Re-entry runs the paused step again from its start (LangGraph, ADK 1.x) and restores finished child steps from the checkpoint, so put side effects after the pause or in their own step, or they run twice.
  - Handoff doesn't run the paused step again and uses the person's reply as its output (the default for a leaf step in ADK 2.0).
- **An orchestrator checks for a pause before using a child's output,** because a paused child can return nothing instead of an error. Tools never swallow exceptions, or the runtime's retries and pauses stop working.
- **On resume, take ownership of the run first, then reload its history,** because the saved snapshot may be stale if another worker touched it.
- **Keep the sibling results.** If a turn called two tools and one needs approval, store the finished one's result before pausing. OpenAI's SDK fixed exactly this. Without it, the model is called again and `submit_order` runs twice.
- **When one turn asks for several approvals, resume only after every one has a decision,** then run the approved calls in the model's original order.
- **Give a paused run its own approval deadline:** longer than your longest expected wait for a person, shorter than the host's session lifetime (build-or-buy.md question 8). A run deadline sized for a live reply kills every approval wait. At the deadline, return the no-answer result below.
- **An approval belongs to the turn that asked for it.** A later turn asks for something different, and reusing the earlier yes approves an action nobody looked at.
- **Ask a person through an async tool when the agent has other work to do.** The agent keeps working and waits only before the step that needs the answer. The tool's result is the person's answer, never an acknowledgment that the question was shown. An optional question to the user proceeds after a short wait on a stated assumption; a required approval blocks. If the question is dismissed or times out, return an explicit no-answer result so the model decides how to go on.
- **An MCP tool that returns `input_required` has ended that call.** Pause the run with the server's input requests and its `requestState` in the checkpoint. After the person answers, re-issue the original call with a new request id, the answers, and `requestState` unchanged. Cap the rounds, since the server may ask again, and keep the idempotency key on one-time actions, since the state token doesn't guarantee single use.

## A person takes over

- **The conversation has one owner at a time, stored in state, and code checks it before every agent reply.** While a person owns it, the agent doesn't answer. A prompt that says "stay quiet while a human handles this" fails the first time the user writes again.
- **A stop or a takeover ends the run, not just the reply.** Code cancels the turn and rejects any tool call that arrives after it. If the user said stop, the agent answers once with what already happened and what didn't. If a person took over, that summary goes to the log for them and the user gets nothing from the agent.
- **Pass the cancel down to the model call and into every tool.** Stopping the reply leaves backend work running, a tool stops only if it checks the signal, and a provider abort is best effort. Discard partial streamed output, write the owed results (failures.md), and keep only events already committed. Mark the run stopped only after cleanup finishes, and tell the user something was cancelled only after the backend confirms it.
- **An explicit stop goes to a server endpoint** that cancels the producer, saves the partial reply, and clears the active-run pointer only if it still points to that run, so a late stop can't clear a newer run.
- **The model picks a named outcome; code carries it out.** In a support agent, the agent chooses "hand to KYC team" with its reason, and code replies to the customer, tags, reassigns, and closes in a fixed order, so no step is skipped.
- **Escalate on two triggers:** failures crossing a threshold you set, or an action that is high-risk and irreversible. Elapsed time is never an approval.
- **Two modes, kept apart:** the agent asks your team a private question and keeps the conversation, or a person takes the conversation. The first is a question the run waits on (see "Pausing for a human"); the second changes the owner.
- **When the conversation comes back, the agent reads what the person did** (their messages, actions, and notes in the log) before replying, and any run paused before the takeover is discarded, not resumed.

## When a conversation ends

- **Define the end in code:** an explicit close, or an idle timeout you choose. The end of a conversation triggers the memory pass (memory.md) and discards paused runs that can no longer resume. Without a defined end, both happen never or at random.
