# Sources

Checked on 2026-10-01. Where two sources disagreed, the most recent position won. Where Anthropic and OpenAI disagree with no date to settle it, both positions are under "Where the answer depends on the case" in the reference that covers the question.

## Anthropic and OpenAI

Most rules come from the harness, architecture, context, and tool files of the claude-agents (124 sources) and openai-agents (130 sources) skills in this repo. Their `references/article-index.md` lists each source with its link and date. The main ones:

- Anthropic: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (2024-12-19), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29), [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09-11), [Managed Agents](https://www.anthropic.com/engineering/managed-agents) (2026-04-08), [When to use multi-agent systems](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them) (2026-01-23), the hosting, compaction, memory, and prompt-versioning cookbooks, [Sonnet 5.5](https://claude.dev/blog/building-with-claude-sonnet-5-5/) (2026-09-28), and [Agents you can coach](https://claude.com/blog/agents-you-can-coach-how-asana-builds-human-agent-teams-with-claude) from Asana (2026-09-29).
- OpenAI: [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) (2025-04-17), [Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop) (2026-01-23), [Harness engineering](https://openai.com/index/harness-engineering) (2026-02-11), the Agents SDK docs on running agents, handoffs, tools, sessions, and human-in-the-loop, the Agents API docs (2026-09-10), and the Codex repo's protocol, goal, context, memory, and tool specs (snapshot 2026-09-29).

## Added on 2026-10-01

- Anthropic: [Mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages) (2026-09-01) and the tool changes they allow (2026-09-22, beta), [Compaction on demand](https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand) (2026-09-14), [Managed Agents permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies) (2026-09-10), [Managed Agents updates](https://claude.com/blog/claude-managed-agents-updates) (2026-05-19, self-hosted sandbox), and [How Anthropic's sales team rebuilt inbound](https://claude.com/blog/how-anthropics-sales-team-rebuilt-inbound-with-claude-managed-agents) (2026-09-30, escalation reasons, staging, rollback).
- OpenAI: Agents API [functions](https://developers.openai.com/api/docs/guides/agents-api/tools/functions), [sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions), and [multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) (2026-09-10), [openai-agents-python #5240](https://github.com/openai/openai-agents-python/pull/5240) (2026-09-29, sibling results on resume), and Codex PRs [#49441](https://github.com/openai/codex/pull/49441) and [#49880](https://github.com/openai/codex/pull/49880) (2026-09-30 and 10-01, terminal errors, turn-scoped approvals).

- OpenAI tooling changes used in build-or-buy.md: the visual workflow builder winds down by 2026-11-30 (`agentkit` in openai-agents), and the hosted Evals platform goes read-only on 2026-10-31 and shuts down on 2026-11-30 ([deprecations](https://developers.openai.com/api/docs/deprecations)).

## Support vendors

- Lorikeet: [Reliable handoffs](https://www.lorikeetcx.ai/blog/outcomes) (2026-07-07, the model picks a named outcome and code carries it out) and [Resolution Loop](https://www.lorikeetcx.ai/blog/launching-resolution-loop) (2026-03-05, asking a human privately versus handing over).
- Plaude ([docs](https://plaude.com/docs), checked 2026-09-30) and Intercom Fin ([pricing](https://www.intercom.com/pricing)) are named only as examples of vertical vendors.

## Practitioners

- Cognition: [Devin's Slack etiquette](https://devin.ai/blog/devins-slack-etiquette) (2026-08-20, re-sent channel rules, "no reply" as an end), [Multi-agents working](https://cognition.com/blog/multi-agents-working) (2026-04-22, one writer).
- Armin Ronacher: [Absurd in production](https://lucumr.pocoo.org/2026/4/4/absurd-in-production/) (2026-04-04, Postgres durability), [Better models, worse tools](https://lucumr.pocoo.org/2026/7/4/better-models-worse-tools/) (2026-07-04, strict schemas).
- Temporal: [Durable, flexible multi-agent systems](https://temporal.io/blog/durable-flexible-multi-agent-systems) (2026-08-06, waiting at zero compute). Vercel: [AI SDK 7](https://vercel.com/blog/ai-sdk-7) (2026-06-25) and [durable execution](https://vercel.com/blog/a-new-programming-model-for-durable-execution) (2026-04-16, runs finish on their version). Inngest: [durable execution](https://www.inngest.com/blog/durable-execution-key-to-harnessing-ai-agents) (2026-02-19, replay from checkpoint).
- LangChain: [The runtime behind production deep agents](https://www.langchain.com/blog/runtime-behind-production-deep-agents) (2026-04-20, messages that arrive mid-turn), [Organizing context in a multi-agent harness](https://www.langchain.com/blog/organizing-context-in-a-multi-agent-harness) (2026-09-08).
- Manus: [Context engineering lessons](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) (2025-07-18, reversible compaction, masking tools).

## Resolved conflicts

- **Changing tools mid-conversation.** The claude-agents skill says tools are part of the cache prefix and must not change mid-session. Anthropic's 2026-09-22 docs allow it on Claude 5.x through a system message. Newest wins for those models; the old rule still holds elsewhere.
- **Multi-agent.** Cognition's "Don't build multi-agents" (2025-06-12) is superseded by its 2026-04-22 post, which allows advisor agents but keeps one writer, in line with Anthropic and OpenAI.
- **Own abstraction or hosted harness.** Ronacher's "build your own abstraction" (2025-11) and Anthropic's "use the API directly" (2024-12) are older than the hosted harnesses both vendors now offer. The newer disagreement between Anthropic and OpenAI stays open in build-or-buy.md.
- **Left out:** Thorsten Ball's view that the harness matters less (2026-08), an aside rather than a lesson from building.
