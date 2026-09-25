# skills

Agent skills I use in Claude Code, Codex, Cursor, and opencode. Each skill lives in its own folder.

## claude-agents

I built this one so my agents answer questions about building with Claude from what the Claude Code team wrote on [claude.dev](https://claude.dev/), not from what the model half-remembers. It covers all 10 posts on the blog, published between April 10 and September 25, 2026:

- tool design
- context engineering
- CLAUDE.md and skills
- prompt caching and Claude Code costs
- effort and model choice
- steering long runs
- subagents and dynamic workflows
- verification
- HTML outputs
- measurement-driven performance work

Every claim ends with a short key for its post, like `effort` or `cost`, and `references/article-index.md` maps each key to the post's URL. Ask it about something the posts don't cover, like fine-tuning, and it tells you so instead of guessing.

```
claude-agents/
  SKILL.md        thesis, 14 core ideas, method, how to answer
  references/     11 topic files, a glossary, and the article index
```

### Install

```sh
npx skills add vcompagnucci/skills --skill claude-agents
```

Or copy the `claude-agents/` folder into `~/.claude/skills/`.

### Before you use it

- It's unofficial, and I'm not affiliated with Anthropic. The ideas belong to the authors, mostly Thariq Shihipar and Addy Osmani.
- It paraphrases the posts and quotes only short lines, each linked to its source. The full text of the posts isn't in this repo.
- Prices, model names, and defaults are from September 2026 and will go out of date. For current API details, use the [Claude docs](https://docs.claude.com).
