# Support checks

Six things a support agent needs that generic eval methods skip. Apply them at whatever stage you're in.

## Handoffs to a human

- Keep the trace open past the handoff. Log the reason, the context passed to the human, the wait, and how it ended.
- Grade escalation in both directions, escalating when it should and not when it shouldn't. A voice support bot scored 98% offline on "escalates when asked" and escalated almost everything in production, because the set had no should-not cases.
- Run escalation triggers outside the agent's own loop, so a confused agent can't talk itself out of escalating.
- Show the reviewer the escalation rules next to the trace, so labels follow the policy and not the reviewer's instinct.
- Grade the timing too. Escalating before a reasonable attempt fails, and so does continuing for several turns after it's clear the agent can't help. Write the expected escalation turn into the case, from the escalation policy.

## Two languages

- Traces in Spanish are read and labeled by someone who knows the language and the local market. Never through LLM translation, which smooths out exactly the tone and wording errors you're looking for.
- Stratify the eval set by language and report every score per language. An average hides a language that fails.
- Validate each judge on each language separately. A judge aligned in English isn't aligned in Spanish until measured.
- Test mid-conversation language switches and answers that mix two languages.

## Sensitive data in traces

- Before using production transcripts, check retention rules and who may see them. Restrict reviewers or redact. Treat every trace as sensitive by default.
- Include probes that ask for another customer's balance, KYC status, or transactions. The only passing answer reveals nothing.
- Treat memos, uploaded documents, and retrieved articles as untrusted input that can never trigger a write.

## Tools and account state

- **A case passes only if the ledger changed exactly as intended and nothing else did.** "I processed your withdrawal" proves nothing. Check the state.
- **Test authorization and preconditions in the tool,** not in the reply: KYC approved, destination allowed, customer confirmed. The tool must refuse when a precondition fails, whatever the model says.
- **The agent never states a customer fact without a tool result behind it,** and claims success only after the tool confirms it.
- **Check arguments that change meaning:** currency (ARS vs USDT), network, amount, the account the action lands on.
- **Separate refused from ran-and-reported.** A test must tell "the tool blocked it" apart from "the tool ran and the agent said it didn't".
- **Include requests the system can't serve:** data it doesn't hold, features that don't exist. The only pass is saying it can't, with what to do instead. An empty tool result stated as a fact ("you have no pending withdrawals") fails when the tool couldn't have known.

## Multi-turn

- Grade the whole conversation first, then find the first failure upstream and reduce it to a single-turn repro you can iterate on.
- Include customers who withhold information until asked, and tasks where the customer must act (re-upload a document, pick a network). Agents score about 20 points lower when information comes out over several turns.
- Test both logged-in and anonymous starts.

## Policies and procedures

- Policy judges read the actual policy or procedure text and fail any answer that contradicts it (quoting 14 days when the window is 30).
- Every tool call passes a policy check before it executes, in code.
- No unrequested extra action, however helpful. An agent told to "make the customer feel better" hands out discounts nobody authorized.
- The agent explains what's missing in a KYC case and re-requests documents. It never decides risk, and never gives investment advice.
- Mandatory text (a disclosure, a legal notice) comes from the platform, never from the model. An instruction followed 99 times in 100 is a compliance failure.
