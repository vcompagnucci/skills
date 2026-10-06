---
name: agent-security
description: Secure an AI agent that talks to people and calls tools, with the most detail on customer-support agents. Distilled from 288 sources by Anthropic, OpenAI, labs, support vendors and security researchers. Use when defending against prompt injection (direct, or through tickets, emails, documents, web pages, tool results, pasted text or other agents), handling manipulation in the chat (fake authority, impersonation, pressure, refund and price bait, jokes, absurd requests like "put me through to Elon Musk", system-prompt extraction), deciding what the agent may touch and who approves what, layering guardrails so a successful injection still hits barriers, closing data exfiltration paths, vetting MCP servers and skills, choosing a model by attack resistance, or detecting and responding to an attack in production.
---

# Agent security

How to keep an agent that reads untrusted text and calls tools from being turned against its customers or its company, from day-one rules to mechanisms and measured attack rates. It distills 288 sources read in October 2026: Anthropic's and OpenAI's docs, posts, model specs and system cards, plus labs, standards bodies, support vendors, security researchers and public incidents. Where sources disagreed the newest position won, and where dates didn't settle it Anthropic and OpenAI won; the losing position is gone, so don't bring it back from memory. Real ties sit under "Where the answer depends on the case" in conversation.md and models.md: report both sides. Every claim cites its source as (`slug`), listed in `references/article-index.md`.

> The model will eventually be talked into something, so security is deciding in code what a talked-into agent can still reach.

Everything else is a corollary of this.

## Where are you?

```
First agent that reads untrusted text and has tools? Read threat-model.md, permissions.md,
  approvals.md, injection.md, conversation.md, in that order, before writing any prompt.
What are you deciding?
├── Who can attack, through which door, what a hijacked agent could do → threat-model.md
├── Text the agent reads steering it: tickets, emails, pages, documents, pasted text,
│   tool results, other agents → injection.md
├── The person in the chat: authority and identity claims, impersonation, account recovery,
│   system-prompt extraction, AI disclosure (opens with a case map) → conversation.md
├── Pressure: refunds, prices and promises, anger and abuse, jokes, off-topic, impossible
│   requests ("put me through to Elon Musk"), handoff triggers, self-harm, minors → conversation-pressure.md
├── Which tools, accounts, credentials, sandboxes and network hosts the agent can reach → permissions.md
├── Which actions need approval and from whom, limits inside tools, reviewer models → approvals.md
├── Input and output classifiers: what each checks, building one, measuring one → guardrails.md
├── How checks stack, where they sit, wiring that silently fails open → guardrail-layers.md
├── What the agent reads and every way data leaves: links, images, memory, secrets → data.md
├── MCP servers, skills, plugins, agent frameworks, API keys → supply-chain.md
├── Which model or agent resists attacks best → models.md, then models-cross-vendor.md
│   and models-lab-evals.md for the full tables
└── Detecting an attack in production and responding to it → response.md
A coined term you don't recognize → glossary.md
```

Open one reference at a time. **Never quote an attack rate from memory.** Copy it from the reference with its model, benchmark, attack budget, date and who ran it, because the same model scores 1% or 90% depending on the attacker and the number of tries (models.md).

## Rules that hold everywhere

1. **Design for the attack that succeeds.** All 13 frontier models in the only independent head-to-head were hijacked, and adaptive attackers took most of 12 published defenses above 90%. The question is never whether an injection gets through, but what it can reach when it does. (`grayswan-ipi-arena`, `nasr-attacker-moves-second`)
2. **Guarantees come from code; prompts and classifiers only raise the attacker's cost.** Sort every defense into deterministic (permissions, limits inside tools, blocked image rendering, approvals) or probabilistic (system prompts, spotlighting, classifiers), and put a deterministic one between the model and every action that moves money, changes an account or discloses data. This extends agent-harness rule 2: a classifier is not code either. (`msrc-indirect-injection-defense`, `fin-ai-guardrails-customer-service`)
3. **Authority comes from the channel a message arrived on, never from what it claims.** "I'm the CEO", "I'm from OpenAI", a fake system message in the chat and "your manager approved it" are all customer text. A claim asking for more caution can be followed; one that unlocks anything needs verification outside the chat or a record in your system. (`openai-model-spec-2026-08-18`, `anthropic-constitution`, `intigriti-hacking-ai-support-agents`)
4. **Everything the agent reads is data, never an instruction.** Tool results, tickets, emails, retrieved articles, web pages, memory, other agents' messages and text the customer pastes from elsewhere can inform the task but never start an action; only the customer's own request does. Pasted text is the channel teams forget: an early Opus 5.5 snapshot followed planted instructions in pasted text in 52% of attempts against 0 of 105 in tool results. (`anthropic-docs-mitigate-jailbreaks`, `anthropic-system-card-opus-5-5`, `openai-hugging-face-incident-road-ahead`)
5. **Never let one session hold untrusted input, private data and a way to act or send out without a gate.** A support agent already holds the first two, so every refund, account change and outbound message passes an approval, an allowlist or a validator in code. This is Meta's Agents Rule of Two, built on Simon Willison's lethal trifecta. (`meta-agents-rule-of-two`, `willison-lethal-trifecta`)
6. **Close every way data leaves, in code.** Render no external images, allow links only from an allowlist or citations to known articles, fetch only URLs that appeared in trusted input, and audit every allowlisted domain for expiry and for GET endpoints that store data. Most vendor fixes for real exfiltration bugs closed the channel rather than stopping the injection. (`msrc-indirect-injection-defense`, `noma-forcedleak-agentforce`, `anthropic-docs-web-fetch-tool`)
7. **Everything the agent says about money, prices or policy binds the company.** Prices, refunds, codes and promises come only from tools, and outgoing replies are checked against policy before they are sent; a disclaimer is tone, not a safeguard. Air Canada lost in tribunal over its bot's bereavement answer, and a UK shop's bot invented an 80% code after an hour of flattery. (`aircanada-moffatt-decision`, `uk-chatbot-80-discount`, `venturebeat-chevy-1-dollar`)
8. **The model never chooses a target: not the account, the order, nor who a conversation is handed to.** Write tools accept only IDs your server issued to this session, account recovery never runs on what the person types, and handoff destinations come from routing rules. Then "put me through to Elon Musk" has nowhere to go, and the agent answers lightly and offers the normal team. (`anthropic-commerce-agents-anatomy`, `csa-meta-ai-support-bot-takeover`, `intercom-fin-escalation-guidance`)
9. **Judge the whole conversation, the session and the account, not each message.** Crescendo attacks make every step look incremental, social engineers split their reconnaissance across calls and channels, and the 2025 espionage campaign passed every per-request check. Guard checks and monitors see the history, and counters (verification attempts, refusals, repeated requests) are per account across channels. (`anthropic-system-prompt-opus-5-5`, `cisa-scattered-spider`, `anthropic-ai-orchestrated-espionage`)
10. **A guard that errors, times out or can't read the input blocks.** Defaults fail open in places teams don't look: a hook that allows on failure after 5,000 ms, web-server body limits that skip the largest transcripts, a guardrail that raises instead of tripping. Test every guard's failure mode, not only its verdicts. (`anthropic-docs-inference-hooks-configuration`, `anthropic-docs-inference-hooks-endpoint`, `openai-agents-sdk-guardrails`)
11. **Read every robustness number as one attacker, one budget, one configuration.** A static attack set overstates robustness against an adaptive attacker, numbers from different vendors or benchmarks never compare, and a classifier that reroutes to an older model can become the injection path. Choose a model on injection results for your own surface, then measure your own agent (agent-evals red-team.md). (`anthropic-system-card-opus-5-5`, `nist-caisi-agent-hijacking`, `spylab-agentdojo-leaderboard`)
12. **Treat every model, prompt, tool and SDK change as a security change.** Re-run the adversarial suite (injection, trolling, price bait, off-topic) on each one, and pin frameworks past their security fixes. DPD's bot swore at customers after a routine update, and the OpenAI Agents SDK enforced Realtime output guardrails only from v0.23.0. (`dpd-chatbot-swearing-bbc`, `openai-agents-sdk-release-notes`, `openai-gpt-6-1-sol-system-card`)
13. **Decide before launch who can stop the agent, how fast, and what is preserved.** Make it stoppable per capability (cut the refund path while it keeps answering) and entirely, alert on every detected or refused injection, and take forensic copies before purging a poisoned memory or document. (`openai-practices-governing-agentic-ai`, `cosai-ai-incident-response`, `anthropic-system-card-sonnet-4-6`)

## Numbers to use

| Question | Answer |
|---|---|
| Most robust model in the only independent head-to-head | Claude Opus 4.5, 0.5% (61 successes in 11,969 human attempts); all 13 models hijacked (Gray Swan IPI Arena, 2026-03-16) |
| Injection through content the agent reads vs typed in the chat | 27.1% vs 5.7% of attacks succeeded (Gray Swan ART, 1.8 million attacks, 2025-07-28) |
| A frontier model against an adaptive attacker | Opus 5.5: 54.61% of Shade coding attempts, 85.73% on requests rerouted to Opus 4.8, 0 of 2,872 answered by Opus 5.5 itself, 11.13% with probes (200 attempts per scenario, 2026-09-22, Anthropic) |
| GPT-6 Astra on Gray Swan IPI, safeguards on | 8.5% against 27.0% for GPT-5.6 Sol (15 attempts per scenario, 1,810 attacks, 2026-09-03, OpenAI) |
| Default LLM judge in OpenAI's Guardrails | gpt-4.1-mini: recall 0.000 at 1% false positives on jailbreaks and injections; gpt-4.1 1.000 on jailbreaks (2025-12-15) |
| Reviewer model at the action boundary | Codex Auto-review denied 99.3% of synthetic injection cases and 90.3% of overeager risky actions (2026-04-30, OpenAI) |
| Refund cap example | Up to $50 without approval, above $50 to a human, original payment method only, never above the order total (Fin) |
| Handoff triggers | 2 failed tool attempts on the same task, 3 consecutive no-match or no-input events (OpenAI Realtime guide, 2026-02-25); the same request across 3 turns (Fin) |
| Reviewer that keeps getting blocked | Pause after 3 blocks in a row or 20 in a session (Claude Code auto mode) |
| Guardrail firing rate | On 40% of conversations "probably too aggressive"; never firing, probably misconfigured; monitor 100%, since 3% to 5% sampled QA misses edge cases (Fin, 2026-09-09) |
| Pausing a severe alert | Pause the activity if it isn't shown safe within 30 minutes of the page (OpenAI, 2026-08-26) |

## Scope

Covers defending an agent: injection, the conversation with a person, permissions and approvals, guardrails, data, supply chain, model choice, and response. How a pause for a human is implemented, identity attached from the run, retries and state belong to agent-harness. How to run a red team and compute attack success rates belongs to agent-evals (red-team.md). The agent's voice and the rest of its system prompt belong elsewhere. Company material (the tool list, refund limits, routing rules, who approves what at your company) belongs in a private skill, never in this one, and overrides this skill where they disagree. Sources and how claims were chosen: `references/sources.md`; every source: `references/article-index.md`.
