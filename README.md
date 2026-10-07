# skills

Skills for building, measuring and securing your own AI agent, starting from what Anthropic and OpenAI published, and one for designing iPhone, iPad and Mac apps with Apple's Human Interface Guidelines.

I built them because models half-remember this stuff. Ask one how Anthropic handles prompt caching or how Codex decides approvals, and you get a confident blend of both with no source. These skills answer from the posts, docs, cookbooks, system cards and code themselves, and every claim cites the one it came from.

## Install

```bash
npx skills@latest add vcompagnucci/skills
```

## Reference

Two skills hold one vendor each:

- **[claude-agents](./claude-agents/SKILL.md).** Building an agent the Anthropic way, from 124 sources: the engineering blog, claude.dev, claude.com, the docs' use-case guides, cookbooks, and research.
- **[openai-agents](./openai-agents/SKILL.md).** The same for OpenAI, from 130 sources. It includes the open-source Codex harness, so you can check what OpenAI ships against what it argues.

They use the same 10 topics, so you can compare them file by file.

Three skills cross sources, Anthropic and OpenAI first:

- **[agent-harness](./agent-harness/SKILL.md).** How to build the harness around an agent, whether to buy one instead, and what stays yours if you do. It merges the harness parts of the two vendor skills with what Google, Microsoft, Amazon, Meta, Cognition, Temporal, Vercel, LangChain and researchers learned building theirs.
- **[agent-evals](./agent-evals/SKILL.md).** Evals for an AI agent, from the first conversations to production, with extra checks for customer-support agents. It builds on Hamel Husain and Shreya Shankar's eval method and adds what Anthropic, OpenAI, Google, Microsoft, Amazon, Meta, eval vendors and support teams published.
- **[agent-security](./agent-security/SKILL.md).** How to keep an agent that reads untrusted text and calls tools from being turned against its customers. It draws on 312 sources by Anthropic, OpenAI, Cognition, labs, standards bodies, support vendors, security researchers and public incidents, and goes as far as a customer asking to be put through to Elon Musk. Every attack rate carries its date and who measured it, because the same model breaks on 2.68% or 88.92% of attempts depending on who attacks.

## Design

- **[apple-hig](./apple-hig/SKILL.md).** Apple's Human Interface Guidelines for iPhone, iPad and Mac, from the 131 pages that apply to them. The interface pages (layout, navigation, presentation, controls, color, type, icons, accessibility, motion), widgets, notifications, Live Activities, privacy, accounts and AI hold every one of Apple's rules for those platforms, each cited to its page. Apple Watch, Apple TV and Vision Pro are left out, and so are 13 Apple technologies like CarPlay and HealthKit. A bundled script reads any page live from Apple's site, so the full tables and the newest wording are one command away. It isn't affiliated with Apple.

## When sources disagree

The newest source wins. In the three cross-source skills, when dates don't settle it, Anthropic and OpenAI win over everyone else, and a real tie between the two is reported both ways. The two vendor skills take their vendor's newest source and keep everyone else's apart. In all five agent skills, a source newer than the skill replaces its answer only if the agent can open it (a link, a file, or a page it found), so "I read that OpenAI changed this" gets checked before anything changes. apple-hig has one source, Apple's own pages: when a page changed after the skill was built, the live page wins.

None of them is official. A job checks the agent skills' sources every two weeks and opens a pull request when something new shows up.
