# skills

Agent skills I use in Claude Code, Codex, Cursor, and opencode. Each skill lives in its own folder.

## claude-agents

I built this one so my agents answer questions about building an agent from what Anthropic actually published, not from what the model half-remembers. It's scoped to building your own agent (Messages API, Agent SDK, or Managed Agents), and cites 120 sources from six places, up to September 2026:

- [claude.dev](https://claude.dev/), the Claude Code team's blog (8 posts)
- the [agents category](https://claude.com/blog-category/agents) of the claude.com blog (26 posts)
- the [Anthropic engineering blog](https://www.anthropic.com/engineering) (24 posts)
- the [use-case guides](https://platform.claude.com/docs/en/about-claude/use-case-guides/overview) in the docs: customer support, ticket routing, moderation, legal, commerce (6 pages)
- the agent notebooks in [claude-cookbooks](https://github.com/anthropics/claude-cookbooks) (43)
- posts on [anthropic.com/research](https://www.anthropic.com/research) about agents working on their own, like Project Vend and agentic misalignment (13)

What's left out on purpose: tips for using Claude Code day to day, HTML as an output format, and enterprise adoption stories. The article index lists what was cut and why.

It's organized in 10 topics: architecture and multi-agent systems, harness design and long runs, tool and MCP design, context engineering, skills, prompt caching, cost, model and effort, evals and verification, security and containment, and agents in production, including the docs' playbooks for support and ticket routing.

Every claim ends with a short key for its source, like `cost` or `agent-evals`, and `references/article-index.md` links each key to the source. Where the sources disagree or a position changed over time, it shows both with dates. Ask it about something they don't cover, like fine-tuning, and it tells you so instead of guessing.

```
claude-agents/
  SKILL.md        thesis, 14 core ideas, how to answer
  references/     10 topic files, a glossary of 170 terms, and the article index
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

## openai-agents

The same idea for OpenAI: my agents answer questions about building an agent from what OpenAI published and shipped, as concepts that work on any stack, not OpenAI platform specifics. It cites 117 sources, from April 2025 to September 2026:

- [developers.openai.com/blog](https://developers.openai.com/blog) (21 of 30 posts)
- the [Engineering category](https://openai.com/news/engineering/) of openai.com (13 of 20 posts)
- 23 agent posts from other openai.com categories, including *A practical guide to building agents*, the Agents API launch, and the computer-using agent
- 29 articles from the [OpenAI cookbook](https://developers.openai.com/cookbook/topic/agents/), 16 concept pages and page groups from the Agents SDK and API docs, and 2 Codex guides
- the open-source [Codex harness](https://github.com/openai/codex): its system prompts for each model, compaction, approvals, memory, goals, review rubric, and tool descriptions (145 files in 13 groups)

The harness shows what OpenAI ships, not only what it argues, and the skill says which of the two a claim comes from.

It uses the same 10 topics as `claude-agents`, so you can compare the two file by file. Posts about OpenAI's own infrastructure, launches, and showcases are left out, and the article index says which.

```
openai-agents/
  SKILL.md        thesis, 14 core ideas, how to answer
  references/     10 topic files, a glossary of 135 terms, and the article index
```

```sh
npx skills add vcompagnucci/skills --skill openai-agents
```

Same caveats as above: it's unofficial, it paraphrases with short quotes linked to each source, and some sources are guest posts or simulations, which the index marks.
