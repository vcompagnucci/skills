# skills

Skills for building your own AI agent, based on what Anthropic and OpenAI published.

I built them because models half-remember this stuff. Ask one how Anthropic handles prompt caching or how Codex decides approvals, and you get a confident blend of both with no source. These skills answer from the posts, docs, cookbooks, and code themselves, and every claim cites the one it came from.

## Install

```bash
npx skills@latest add vcompagnucci/skills
```

## Reference

- **[claude-agents](./claude-agents/SKILL.md).** Building an agent the Anthropic way, from 120 sources: the engineering blog, claude.dev, claude.com, the docs' use-case guides, cookbooks, and research.
- **[openai-agents](./openai-agents/SKILL.md).** The same for OpenAI, from 125 sources. It includes the open-source Codex harness, so you can check what OpenAI ships against what it argues.

Both use the same 10 topics, so you can compare them file by file. Neither is official. A job checks their sources every two weeks and opens a pull request when something new shows up.
