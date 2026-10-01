# Humans in the loop

How the harness pauses for a person, hands the conversation over, and ends it. Who may approve what is a security question.

## Pausing for a human

- **A checkpoint holds** the transcript, pending calls and approvals, finished sibling results, queued customer messages, the conversation's owner, usage so far, and the agent version.
- **Resuming re-runs the paused step from its start** in most runtimes (LangGraph, ADK). Put side effects after the pause or in their own step, so they don't run twice.
- **On resume, take ownership of the run first, then reload its history,** because the saved snapshot may be stale if another worker touched it.
- **Keep the sibling results.** If a turn called two tools and one needs approval, store the finished one's result before pausing. OpenAI's SDK fixed exactly this. Without it, the model is called again and `submit_order` runs twice.
- **An approval belongs to the turn that asked for it.** A later turn asks for something different, and reusing the earlier yes approves an action nobody looked at.

## A person takes over

- **The conversation has one owner at a time, stored in state, and code checks it before every agent reply.** While a person owns it, the agent doesn't answer. A prompt that says "stay quiet while a human handles this" fails the first time the customer writes again.
- **A stop or a takeover ends the run, not just the reply.** Code cancels the turn and rejects any tool call that arrives after it. If the customer said stop, the agent answers once with what already happened and what didn't. If a person took over, that summary goes to the log for them and the customer gets nothing from the agent.
- **The model picks a named outcome; code carries it out.** The agent chooses "hand to KYC team" with its reason, and code replies to the customer, tags, reassigns, and closes in a fixed order, so no step is skipped.
- **Escalate on two triggers:** failures crossing a threshold you set, or an action that is high-risk and irreversible. An optional question to the customer proceeds after a short wait on a stated assumption; a required approval blocks. Elapsed time is never an approval.
- **Two modes, kept apart:** the agent asks your team a private question and keeps the conversation, or a person takes the conversation. The first is a pause (see "Pausing for a human"); the second changes the owner.
- **When the conversation comes back, the agent reads what the person did** (their messages, actions, and notes in the log) before replying, and any run paused before the takeover is discarded, not resumed.

## When a conversation ends

- **Define the end in code:** an explicit close, or an idle timeout you choose. The end of a conversation triggers the memory pass (context-memory.md) and discards paused runs that can no longer resume. Without a defined end, both happen never or at random.
