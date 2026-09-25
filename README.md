# skills

Agent skills I use across Claude Code, Codex, Cursor, and opencode.

## claude-agents

Answers questions about building with Claude agents from the [claude.dev](https://claude.dev/) posts, with a citation on every claim. It covers:

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

It is built from all 10 posts published between 2026-04-10 and 2026-09-25. Each claim cites its post by a short key, and `references/article-index.md` maps every key to the original URL. When a question falls outside those posts, the skill says so instead of guessing.

```
claude-agents/
  SKILL.md                  thesis, 14 core ideas, method, how to answer
  references/               11 topic files, a glossary, and the article index
```

### Install

```sh
npx skills add vcompagnucci/skills --skill claude-agents
```

Or copy `claude-agents/` into `~/.claude/skills/`.

### Notes

- Unofficial. I'm not affiliated with Anthropic. The ideas belong to the post authors, mostly Thariq Shihipar and Addy Osmani.
- The skill paraphrases the posts and quotes only short lines, always with a link to the source. It does not include the full text of any post.
- Prices, model names, and defaults reflect the posts as of September 2026. For current API details, check the [Claude docs](https://docs.claude.com).
