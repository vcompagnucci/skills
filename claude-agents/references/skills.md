# Skills

How Anthropic builds, structures, shares, and measures skills in Claude Code, based on the hundreds it uses internally. Almost all of it comes from one post, `skills`. The Claude 5 update is in `ctx-eng`.

## What a skill is

- **A skill is a folder, not a markdown file.** It holds instructions plus scripts, assets, data, config, and hooks the agent can find and use. The best skills make use of that folder and those config options. (`skills`)
- **A good skill fits one of nine categories.** Library/API reference · product verification · data fetching and analysis · business process automation · code scaffolding · code quality and review · CI/CD and deployment · runbooks · infrastructure operations. Skills that span several of these confuse the agent. (`skills`)
- **Verification skills have the most measurable effect.** They're worth a week of an engineer's time. Have Claude record a video of what it tested, or assert state in code at each step (`signup-flow-driver`, `checkout-verifier`, `tmux-cli-driver`). (`skills`)

## Writing one

- **Don't state the obvious.** Claude already writes code and can read your repo. A knowledge skill should push Claude away from what it would do by default, the way the frontend design skill steers it off Inter and purple gradients. (`skills`)
- **The gotchas section carries the most information.** Build it from real failures: "`subscriptions` is append-only; the row you want has the highest version, not the latest `created_at`", or "Staging returns 200 even when the Stripe webhook didn't process." (`skills`)
- **Use the file system to load context on demand.** Tell Claude which files exist, like `references/api.md` or a template in `assets/`, and it reads them when they're relevant. (`skills`, `ctx-eng`)
- **Don't railroad.** A reusable skill states the goal and the constraints, not every step. (`skills`)
- **Write down what's particular to you.** The opinions, knowledge, and practices of you, your team, or your product. Keep the skill loose except where a mistake is expensive. (`ctx-eng`)
- **Write the description for the model.** Claude scans the list of descriptions to decide whether a skill fits the request. So the description says *when to use it*, in the words users type ("babysit"). (`skills`)

## Giving a skill more to work with

- **Setup through config.json.** If a setting is missing, such as which Slack channel to post to, the agent asks, and it can use AskUserQuestion to do it. (`skills`)
- **Memory through stored data.** An append-only log, JSON, or SQLite under `${CLAUDE_PLUGIN_DATA}`. A `standup-post` skill reads `standups.log` to see what changed since yesterday. (`skills`)
- **Scripts let Claude spend its turns combining things.** Give it a helper library with the gotchas in the docstrings. For "What happened on Tuesday?", Claude writes a one-off script that combines them. (`skills`)
- **On-demand hooks for opinionated guards.** `/careful` blocks rm -rf, DROP TABLE, force-push, and kubectl delete, but only while you're working on prod. `/freeze` blocks edits outside one directory while you debug. (`skills`)
- **Ship workflows inside skills as templates.** Put the JS workflow files in the folder, point to them from SKILL.md, and tell Claude to adapt them instead of running them as written. (`workflows`)

## Sharing and measuring

- **A repo for small teams, a plugin marketplace at scale.** Every skill checked into a repo adds context for everyone. A marketplace lets each person choose, and can include setup. (`skills`)
- **Curation happens by use.** Upload the skill to a sandbox folder and share it in Slack. Once it has traction, and the owner decides when that is, open a PR to add it to the marketplace. No central team gatekeeps. (`skills`)
- **Combine skills by name.** There's no dependency management yet. Mention another skill by name and the model calls it if it's installed. (`skills`)
- **Measure with a PreToolUse hook.** Logging each use shows which skills are popular and which trigger less than expected. (`skills`)
- **Start small.** Most of the best skills began as a few lines and one gotcha, and grew as Claude hit new edge cases. (`skills`)

## Key source articles
`skills` · `ctx-eng` · `workflows`
