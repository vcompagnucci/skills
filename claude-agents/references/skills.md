# Skills

How Anthropic builds, structures, distributes, and measures skills in Claude Code, drawn from hundreds in active internal use. Almost all of it comes from one post, `skills`, with the Claude 5 update in `ctx-eng`.

## What a skill is

- **A skill is a folder, not a markdown file.** Instructions plus scripts, assets, data, config, and dynamic hooks the agent can discover and manipulate; the most effective skills use the folder structure and configuration options. (`skills`)
- **Good skills fit one of nine categories.** Library/API reference · product verification · data fetching and analysis · business process automation · code scaffolding · code quality and review · CI/CD and deployment · runbooks · infrastructure operations. Skills that straddle several confuse the agent. (`skills`)
- **Verification skills have the most measurable impact.** Worth an engineer spending a week on them: record a video of what was tested, assert state programmatically at each step (`signup-flow-driver`, `checkout-verifier`, `tmux-cli-driver`). (`skills`)

## Writing one

- **Don't state the obvious.** Claude already codes and can read your repo; knowledge skills should push Claude out of its normal thinking, like the frontend design skill steering away from Inter and purple gradients. (`skills`)
- **The Gotchas section is the highest-signal content.** Grow it from real failures: "`subscriptions` is append-only; the row you want has the highest version, not the latest `created_at`"; "Staging returns 200 even when the Stripe webhook didn't process." (`skills`)
- **Use the file system as progressive disclosure.** Tell Claude which files exist (`references/api.md`, a template in `assets/`) and it reads them at the right time. (`skills`, `ctx-eng`)
- **Don't railroad.** Reusable skills state the goal and constraints, not every step. (`skills`)
- **Encode what's particular to you.** Opinions, knowledge, and practices specific to you, your team, or product; lightweight, overconstrained only where it truly matters. (`ctx-eng`)
- **Write the description for the model.** Claude scans a listing of descriptions to decide "is there a skill for this request?", so the description says *when to trigger*, with the words users type ("babysit"). (`skills`)

## Giving a skill capabilities

- **Setup through config.json.** If config is missing (e.g. which Slack channel), the agent asks, optionally via AskUserQuestion. (`skills`)
- **Memory through stored data.** An append-only log, JSON, or SQLite under `${CLAUDE_PLUGIN_DATA}`; a `standup-post` skill reads `standups.log` to see what changed since yesterday. (`skills`)
- **Scripts let Claude spend turns on composition.** A helper library with gotchas in the docstrings; Claude writes a one-off script composing them for "What happened on Tuesday?" (`skills`)
- **On-demand hooks for opinionated guards.** `/careful` blocks rm -rf, DROP TABLE, force-push, kubectl delete only while you touch prod; `/freeze` blocks edits outside one directory while debugging. (`skills`)
- **Ship workflows inside skills as templates.** Put the JS workflow files in the folder, reference them from SKILL.md, and tell Claude to adapt rather than run verbatim. (`workflows`)

## Distributing and measuring

- **Repo for small teams, plugin marketplace at scale.** Every checked-in skill adds context for everyone; a marketplace lets people choose and includes setup. (`skills`)
- **Curation is organic.** Upload to a sandbox folder, share in Slack; once it has traction (the owner decides), PR it into the marketplace. No central gatekeeping team. (`skills`)
- **Compose by name.** No native dependency management yet; reference other skills by name and the model invokes them if installed. (`skills`)
- **Measure with a PreToolUse hook.** Logging skill usage finds popular and undertriggering skills. (`skills`)
- **Start small.** Most of the best skills began as a few lines and a single gotcha, and got better as Claude hit new edge cases. (`skills`)

## Key source articles
`skills` · `ctx-eng` · `workflows`
