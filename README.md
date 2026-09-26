# skills

Agent skills I use in Claude Code, Codex, Cursor, and opencode. Each skill lives in its own folder.

## claude-agents

I built this one so my agents answer questions about building agents from what Anthropic actually published, not from what the model half-remembers. It covers 139 sources from six places, up to September 2026:

- [claude.dev](https://claude.dev/), the Claude Code team's blog (all 10 posts)
- the [agents category](https://claude.com/blog-category/agents) of the claude.com blog (all 38 posts)
- the [Anthropic engineering blog](https://www.anthropic.com/engineering) (all 25 posts)
- the [use-case guides](https://platform.claude.com/docs/en/about-claude/use-case-guides/overview) in the docs: customer support, ticket routing, moderation, legal, commerce (6 pages)
- the agent notebooks in [claude-cookbooks](https://github.com/anthropics/claude-cookbooks): every one the repo tags as agent patterns, Agent SDK, Managed Agents, or skills (44)
- the posts on [anthropic.com/research](https://www.anthropic.com/research) about agents working on their own, like Project Vend and agentic misalignment (16 of 164)

It's organized in 12 topics: architecture and multi-agent systems, harness design, tool and MCP design, context engineering, skills, prompt caching, cost and model choice, effort, steering long runs, evals and verification, safety and containment, and agents in production, including the docs' playbooks for support and ticket routing.

Every claim ends with a short key for its post, like `effort` or `agent-evals`, and `references/article-index.md` links each key to the post. Where the posts disagree or a position changed over time, it shows both with dates. Ask it about something the posts don't cover, like fine-tuning, and it tells you so instead of guessing.

```
claude-agents/
  SKILL.md        thesis, 14 core ideas, how to answer
  references/     12 topic files, a glossary of 189 terms, and the article index
```

### Install

```sh
npx skills add vcompagnucci/skills --skill claude-agents
```

Or copy the `claude-agents/` folder into `~/.claude/skills/`.

### Before you use it

- It's unofficial, and I'm not affiliated with Anthropic. The ideas belong to the authors of each post.
- It paraphrases the posts and quotes only short lines, each linked to its source. The full text of the posts isn't in this repo.
- Some of the claude.com posts are product announcements with only a few real positions, and most cookbooks are code walkthroughs. The index says which, and cookbook keys start with `cb-` so you can tell a worked example from a measurement.
- Prices, model names, and defaults are from September 2026 and will go out of date. For current API details, use the [Claude docs](https://docs.claude.com).
