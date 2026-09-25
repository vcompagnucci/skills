# Skills

How Anthropic builds, structures, shares, and improves skills, from the hundreds it runs internally and from what customers built. The shift behind them: Anthropic stopped building a separate agent per domain and now gives one general agent its expertise as skills.

## Why skills exist

- **Domain agents converged into one general agent.** Anthropic "used to think" coding, research, finance, and marketing agents would each need their own tools and scaffolding. As models improved, code became the interface for almost any digital work, and the scaffolding shrank to bash and a filesystem. (`skills-for-agents`)
- **General capability isn't expertise.** You'd hire the tax professional who has filed thousands of returns over the math genius working from first principles. Agents are the genius, missing context and organizational know-how. (`skills-for-agents`)
- **Building a skill is like writing an onboarding guide for a new hire.** Package procedural knowledge as composable skills instead of fragmented custom agents. (`agent-skills`)
- **The architecture has four layers.** "The loop reasons, the runtime executes, MCP connects, and skills guide." Each evolves on its own. (`skills-for-agents`)

## What a skill is

- **A folder, not a markdown file.** Instructions plus scripts, assets, data, config, and hooks. Skills are deliberately just files, so they version in Git, share with a team, and non-engineers can write them. (`skills`, `skills-for-agents`)
- **Progressive disclosure makes them scale.** Only the name and description load by default (about 50-100 tokens), the full SKILL.md when relevant (under 5K), and bundled files only when needed. So the context a skill can bundle "is effectively unbounded". (`agent-skills`, `skills-explained`, `skills-for-agents`)
- **Nine categories, and a good skill fits one.** Library/API reference, product verification, data analysis, business process automation, code scaffolding, code quality and review, CI/CD, runbooks, infrastructure operations. (`skills`)
- **Verification skills have the most measurable impact.** Worth an engineer's week: record a video of what was tested, assert state at each step. (`skills`)

## Skills versus the other building blocks

- **MCP gives access, skills give the procedure.** "If you're explaining how to do something, that's a skill. If you need Claude to access something, that's MCP." A Notion MCP can search the workspace, and a meeting-prep skill knows which pages, what format, and the team's standards. (`skills-and-mcp`)
- **Keep them separate.** Server instructions stay generic (query syntax, formats). Process lives in the skill (which records first, output format). One skill can drive several servers, and one server can back dozens of skills. (`skills-and-mcp`)
- **Projects say what to know, skills say how to do things.** Put shared expertise in skills, not inside individual subagents, because skills are portable across agents. (`skills-explained`)
- **Repetition is the signal.** Typing the same prompt across conversations means it should become a skill. Build one only for real, repeated tasks: done at least five times and expected ten more. (`skills-explained`, `create-skills`)
- **Skills, not subagents, for per-domain modularity in one conversation.** Across enterprise commerce deployments, a single agent with skills beat both one giant prompt and subagent designs. Anything relevant to a third or more of traffic goes in the prompt instead. (`commerce-agents`)

## Writing one

- **The description decides triggering.** Name and description are the only parts that influence it, so write from Claude's perspective, with specific verbs, use cases, and boundaries ("Not for simple PDF viewing"). Triggering is semantic and fails both ways. (`create-skills`, `skills`)
- **Don't state the obvious.** Push Claude off its defaults, like the frontend design skill steering away from Inter and purple gradients. (`skills`)
- **The gotchas section carries the most information.** Build it from real failures. (`skills`)
- **Write principles and their why, not rules.** "Construct the skill as though you're instructing a smart person, not like you're programming a computer." Don't railroad a reusable skill. (`warp`, `skills`)
- **Keep SKILL.md a menu that points to files.** The docx skill routes by decision tree to workflows and reads its long references only when that path is chosen. Put success criteria in the skill so Claude can check itself. (`create-skills`)
- **Put deterministic or expensive work in code.** The PDF skill's script extracts form fields without loading the script or the PDF into context. (`agent-skills`)
- **Test triggering and execution separately.** An NDA-review skill should stay dormant for "review this employment agreement". (`create-skills`)

## Skills that improve themselves

- **Feedback dies with the session unless you capture it.** Warp pairs a base skill with an improver skill that runs on a schedule, compares suggestions to how people responded, and opens a small PR to the base skill. A human approves, and the next run inherits it. (`warp`)
- **Capture feedback where people already work, and assume some of it is wrong.** A little detailed feedback from a senior engineer beats many thumbs. Skills aren't memory: they are stable and changed on purpose. (`warp`)
- **Build skills by doing the work with Claude.** A 617-line investigation skill was written turn by turn during a real incident, and a lessons log the agent appends to feeds the next run. (`ci-first-responder`)
- **Serve skills fresh.** When data models change several times a day, a stale skill gives "last Tuesday's wrong answer with full confidence". Claude Tag re-reads the skills folder every conversation. (`slack-analytics`)

## Sharing and governing

- **Repo for small teams, marketplace at scale.** Every checked-in skill adds context for everyone. Curation happens by use, and admins can provision skills on by default. Govern shared skills like code: owners, versioning, quarterly reviews. (`skills`, `org-skills`, `create-skills`)
- **A skill can ship expertise inside other products.** The `claude-api` skill encodes which agent pattern fits, what changes between model generations, and when to cache, and CodeRabbit, JetBrains, Resolve AI, and Warp bundle it. "When a new model is released or the API gains a feature, Claude already knows." (`claude-api-skill`)
- **Skills should be portable, like MCP.** Agent Skills is an open standard, and plugins bundle skills, connectors, commands, and sub-agents as files you own. (`org-skills`, `cowork-plugins`, `cowork-enterprise`)
- **Skills are an attack surface.** Install from trusted sources and audit bundled code. (`agent-skills`)
- **Measure with a hook.** A PreToolUse hook logging usage finds skills that trigger less than expected. (`skills`)
- **Start small.** Most of the best skills began as a few lines and one gotcha. (`skills`)

## Key source articles
`skills` · `agent-skills` · `skills-for-agents` · `create-skills` · `skills-explained` · `skills-and-mcp` · `warp`
