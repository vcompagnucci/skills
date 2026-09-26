# Skills

How Anthropic builds, structures, and improves skills, from the hundreds it runs internally and from what customers built. The shift behind them is that Anthropic stopped building a separate agent per domain and now gives one general agent its expertise as skills. Cookbook notebooks add the API mechanics.

## Why skills exist

- **Domain agents converged into one general agent.** Anthropic "used to think" coding, research, finance, and marketing agents would each need their own tools and scaffolding. As models improved, code became the interface for almost any digital work, and the scaffolding shrank to bash and a filesystem. (`skills-for-agents`)
- **General capability isn't expertise.** You'd hire the tax professional who has filed thousands of returns over the math genius working from first principles. Agents are the genius, missing context and organizational know-how. (`skills-for-agents`)
- **Building a skill is like writing an onboarding guide for a new hire.** Package procedural knowledge as composable skills instead of fragmented custom agents. (`agent-skills`)
- **The architecture has four layers.** "The loop reasons, the runtime executes, MCP connects, and skills guide." Each evolves on its own. (`skills-for-agents`)

## What a skill is

- **A folder, not a markdown file.** Instructions plus scripts, assets, data, config, and hooks. Skills are deliberately just files, so they version in Git, share with a team, and non-engineers can write them. (`skills`, `skills-for-agents`)
- **Progressive disclosure makes them scale.** Only the name and description load by default (about 50-100 tokens), the full SKILL.md when relevant (under 5K), and bundled files only when needed. So the context a skill can bundle "is effectively unbounded". The API caps the name at 64 characters and the description at 1,024. The cookbook's "98% savings" over pasting 5,000-10,000 tokens of instructions into every request applies only until the skill is invoked. (`agent-skills`, `skills-explained`, `skills-for-agents`, `cb-skills-intro`)
- **Nine categories, and a good skill fits one.** Library/API reference, product verification, data analysis, business process automation, code scaffolding, code quality and review, CI/CD, runbooks, infrastructure operations. (`skills`)

## Skills versus the other building blocks

- **MCP gives access, skills give the procedure.** "If you're explaining how to do something, that's a skill. If you need Claude to access something, that's MCP." A Notion MCP can search the workspace, and a meeting-prep skill knows which pages, what format, and the team's standards. (`skills-and-mcp`)
- **Keep them separate.** Server instructions stay generic (query syntax, formats). Process lives in the skill (which records first, output format). One skill can drive several servers, and one server can back dozens of skills. (`skills-and-mcp`)
- **Put shared expertise in skills, not inside individual subagents.** Skills are portable across agents. (`skills-explained`)
- **Build a skill only for repeated work.** A real task done at least five times and expected ten more. (`create-skills`)
- **Team conventions and runbooks belong in skills, not the system prompt.** The SRE agents load runbooks, escalation policies, and post-mortem templates as skills when the symptoms match. (`cb-sre-responder`, `cb-sre-agent`)

## Writing one

- **The description decides triggering.** Name and description are the only parts that influence it, so write from Claude's perspective, with specific verbs, use cases, and boundaries ("Not for simple PDF viewing"). Triggering is semantic and fails both ways. (`create-skills`, `skills`)
- **Don't state the obvious.** Push Claude off its defaults, like the frontend design skill steering away from Inter and purple gradients. Name the defaults concretely, and ask for variation across runs, since even a full aesthetics prompt keeps converging on the same font (Space Grotesk). (`skills`, `cb-frontend`)
- **The gotchas section carries the most information.** Build it from real failures. (`skills`)
- **Write principles and their why, not rules.** "Construct the skill as though you're instructing a smart person, not like you're programming a computer." Don't railroad a reusable skill. (`warp`, `skills`)
- **Keep SKILL.md a menu that points to files.** The docx skill routes by decision tree to workflows and reads its long references only when it takes that path. Put success criteria in the skill so Claude can check itself. (`create-skills`)
- **Put deterministic or expensive work in code.** The PDF skill's script extracts form fields without loading the script or the PDF into context. (`agent-skills`)
- **Ask document skills for small, focused files.** Generation is slow (about 2 minutes for a formatted Excel file, 40-60 seconds for a simple PDF), and 2-3 sheets per workbook is the reliable unit. Build big dashboards as several files and combine them in code. (`cb-skills-intro`, `cb-skills-finance`)
- **Test triggering and execution separately.** An NDA-review skill should stay dormant for "review this employment agreement". (`create-skills`)

## Skills that improve themselves

- **Feedback dies with the session unless you capture it.** Warp pairs a base skill with an improver skill that runs on a schedule, compares suggestions to how people responded, and opens a small PR to the base skill. A human approves, and the next run inherits it. (`warp`)
- **Capture feedback where people already work, and assume some of it is wrong.** A little detailed feedback from a senior engineer beats many thumbs. Skills aren't memory. They are stable, and people change them on purpose. (`warp`)
- **Build skills by doing the work with Claude.** A 617-line investigation skill was written turn by turn during a real incident, and a lessons log the agent appends to feeds the next run. (`ci-first-responder`)
- **Serve skills fresh.** When data models change several times a day, a stale skill gives "last Tuesday's wrong answer with full confidence". Claude Tag re-reads the skills folder every conversation. (`slack-analytics`)

## Shipping and governing

- **Custom skills compose with Anthropic's in one request,** like brand guidelines plus `pptx`. (`cb-skills-custom`)
- **Keep code-bound skills in the repo, org-wide ones in the Skills API.** Managed Agents announces a mounted repo's root `.claude/skills/<name>/SKILL.md` at session start, so a PR changes process and code together. The scan isn't live, stops at 64 skills, and finds nested skills only after the agent reads that folder with the `read` tool. (`cb-repo-skills`)
- **Version skills like dependencies.** Use `"latest"` for Anthropic's skills, which it updates, and pin custom skill versions in production, adding versions to the same skill ID rather than recreating it. (`cb-skills-intro`, `cb-skills-custom`)
- **Skills are an attack surface.** Install from trusted sources and audit bundled code. Never put credentials or sensitive data in skill files. (`agent-skills`, `cb-skills-custom`)
- **Measure with a hook.** A PreToolUse hook logging usage finds skills that trigger less than expected. (`skills`)
- **Start small.** Most of the best skills began as a few lines and one gotcha. (`skills`)

## Key source articles
`skills` · `agent-skills` · `skills-for-agents` · `create-skills` · `skills-explained` · `skills-and-mcp` · `warp`
