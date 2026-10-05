# Support checks

Eight things a support agent needs that generic eval methods skip. Apply them at whatever stage you're in.

## Handoffs to a human

- Keep the trace open past the handoff. Log the reason, the context passed to the human, the wait, and how it ended.
- Grade escalation in both directions, escalating when it should and not when it shouldn't. A voice support bot scored 98% offline on "escalates when asked" and escalated almost everything in production, because the set had no should-not cases.
- Run escalation triggers outside the agent's own loop, so a confused agent can't talk itself out of escalating.
- Show the reviewer the escalation rules next to the trace, so labels follow the policy and not the reviewer's instinct.
- Grade the timing too. Escalating before trying the first step the procedure names fails, and so does continuing for several turns after it's clear the agent can't help. Write the expected escalation turn into the case, from the escalation policy.
- If several agents hand off to each other, test that a specialist hands control back when the topic changes and that handoffs never loop.

## Two languages

- Traces in Spanish are read and labeled by someone who knows the language and the local market. Never through LLM translation, which smooths out exactly the tone and wording errors you're looking for.
- Stratify the eval set by language and report every score per language. An average hides a language that fails.
- Validate each judge on each language separately. A judge aligned in English isn't aligned in Spanish until measured.
- Test mid-conversation language switches and answers that mix two languages.
- **Same case, different customer.** Change only the stated country, language, or identity and run it again. Report each variant's distance from the mean with a 95% bootstrap interval. It passes when no variant changes the outcome significantly.

## Sensitive data in traces

- Before using production transcripts, check retention rules and who may see them. Restrict reviewers or redact. Treat every trace as sensitive by default.
- Include probes that ask for another customer's balance, KYC status, or transactions. The only passing answer reveals nothing.
- Treat memos, uploaded documents, and retrieved articles as untrusted input that can never trigger a write.

## Tools and account state

- **A case passes only if the ledger changed exactly as intended and nothing else did.** "I processed your withdrawal" proves nothing. Check the state.
- **Verify writes against expected writes.** Map each agent write to one expected write: exact checks on arguments that must match, a narrow LLM check only for free-text arguments (a memo), order only where one write depends on another, and a count so an extra write fails. Test the verifier with perturbed runs and human labels. On 450 labeled runs this check reached 0.99 precision against 0.53 for one LLM judge given the same criteria.
- **Test authorization and preconditions in the tool,** not in the reply: KYC approved, destination allowed, customer confirmed. The tool must refuse when a precondition fails, whatever the model says.
- **The agent never states a customer fact without a tool result behind it,** and claims success only after the tool confirms it.
- **Check every tool argument in code, then its source.** Code checks the schema: types, formats, required parameters present, nothing undefined. Then check each value traces to the customer's words or an earlier tool result, meaning-changing ones first: currency (ARS vs USDT), network, amount, the account the action lands on. Name argument failures apart: invented value, omitted constraint filled by a silent default, value in the wrong parameter (swapped dates), wrong value, nonexistent parameter or tool. A step judge sees only what came before that call.
- **Separate refused from ran-and-reported.** A test must tell "the tool blocked it" apart from "the tool ran and the agent said it didn't".
- **Include requests the system can't serve:** data it doesn't hold, a feature that doesn't exist, a refund out of policy, an authorization the customer lacks. The only pass is saying so, with what to do instead, or escalating. Presenting knowingly incomplete work as done fails, and so does an empty tool result stated as a fact the tool couldn't know ("you have no pending withdrawals"). Build them as impossible twins of intact cases: models attempted reward hacks 3 to 6 times as often when a needed file was missing.

## Multi-turn

- **Grade the whole conversation first,** then find the first failure upstream and reduce it to a single-turn repro you can iterate on. To find its cause, change one element just before the failure (a tool result, a customer message), resample the agent from that point many times, grade every continuation with the same frozen judge, and compare rates. Never ask the agent why it acted: its answer changes with how the question is worded.
- Include customers who withhold information until asked, tasks where the customer must act (re-upload a document, pick a network), and both logged-in and anonymous starts. Agents score about 20 points lower when information comes out over several turns.
- **Give multi-turn cases more runs than single-turn ones, and report them apart.** Spreading a fully specified task over several turns cut scores 39% on average, mostly through run-to-run variance: aptitude fell 16% while unreliability rose 112%. Report their pass^k or the spread between the 90th and 10th percentile scores. Temperature 0 and an end-of-conversation recap don't close the gap: temperature 0 still left about 30 points of unreliability.
- **The customer changes a value mid-conversation** (amount, network, date). Check that the final reply uses the new value. In 3 of 4 such failures Google found, the state was right and the message repeated the old value, which a state check alone misses.

## Policies and procedures

- Policy judges read the actual policy or procedure text and fail any answer that contradicts it (quoting 14 days when the window is 30).
- Every tool call passes a policy check before it executes, in code.
- No unrequested extra action, however helpful. An agent told to "make the customer feel better" hands out discounts nobody authorized.
- **Push for exceptions and count the give-ins.** On should-not cases where the simulated customer keeps asking for a credit, refund, or fee waiver, report the share of runs where the agent takes the forbidden action, apart from pass^k. Two models with about equal pass^k on τ-bench Airline differed fourfold in how often a customer talked them into a violation.
- The agent explains what's missing in a KYC case and re-requests documents. It never decides risk, and never gives investment advice.
- Mandatory text (a disclosure, a legal notice) comes from the platform, never from the model. An instruction followed 99 times in 100 is a compliance failure.

## Customers that are AI agents

- **Tag conversations where the customer is an AI agent** (self-declared, relaying for a person, impersonating the account holder, machine-sent mail) and report them as their own line in resolution, CSAT, and handle time. They pass knowledge-based identity checks and never rate a conversation, which skews containment and CSAT, and Lorikeet saw up to 3% of inbound traffic come from them. Add these personas to the simulated customers (simulation.md) to test identity verification and consent.

## Voice

- **Evaluate a voice agent through synthesized speech, never text.** Drive the same cases with a simulated customer whose turns become audio, vary voices and accents, and grade on meaning or rubric checks, never reference strings. Text input skips voice activity detection, turn-taking, and transcription, where voice failures happen.
