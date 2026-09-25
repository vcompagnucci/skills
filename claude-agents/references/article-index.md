# Article index

All 10 posts on claude.dev, from 2026-04-10 to 2026-09-25, grouped by main theme. Citations use the short keys below. Each key's post lives at `https://claude.dev/blog/<slug>/`. Two pages on the site are left out on purpose: `/terminal/` is an interface and `/terms/` is legal text.

| Key | Slug (URL path) |
|---|---|
| `caching` | `lessons-from-building-claude-code-prompt-caching-is-everything` |
| `cost` | `what-a-task-costs-on-opus-5-5` |
| `ctx-eng` | `the-new-rules-of-context-engineering-for-claude-5-generation-models` |
| `effort` | `spending-your-effort` |
| `faster` | `how-we-made-claude-ai-faster` |
| `html` | `using-claude-code-the-unreasonable-effectiveness-of-html` |
| `opus-5-5` | `getting-the-most-out-of-opus-5-5` |
| `seeing` | `seeing-like-an-agent` |
| `skills` | `lessons-from-building-claude-code-how-we-use-skills` |
| `workflows` | `a-harness-for-every-task-dynamic-workflows-in-claude-code` |

## Tool design (`references/tool-design.md`)

- **Seeing like an agent: how we design tools in Claude Code** (`seeing`, 2026-04-10, Thariq Shihipar). Shape tools to the model's abilities by reading its outputs, keep the set small, and retire tools the model outgrows.

## Prompt caching (`references/prompt-caching.md`)

- **Lessons from building Claude Code: Prompt caching is everything** (`caching`, 2026-04-30, Thariq Shihipar). Caching is a prefix match, so never change the prefix. Static content goes first, updates arrive as messages, tools and models stay fixed, and compaction reuses the cache.

## HTML outputs (`references/html-outputs.md`)

- **Using Claude Code: The unreasonable effectiveness of HTML** (`html`, 2026-05-20, Thariq Shihipar). HTML beats Markdown for agent output because people read it, and that keeps them in the loop.

## Multi-agent workflows (`references/multi-agent-workflows.md`)

- **A harness for every task: dynamic workflows in Claude Code** (`workflows`, 2026-06-02, Thariq Shihipar and Sid Bidasaria). Claude can write its own multi-agent script per task, which counters laziness, self-preference, and goal drift on long or adversarial work.

## Skills (`references/skills.md`)

- **Lessons from building Claude Code: How we use skills** (`skills`, 2026-06-03, Thariq Shihipar). Good skills are single-category folders that push Claude off its defaults with gotchas, scripts, and files loaded on demand.

## Context engineering (`references/context-engineering.md`)

- **The new rules of context engineering for Claude 5 generation models** (`ctx-eng`, 2026-07-24, Thariq Shihipar). Claude 5 models are overconstrained. Delete rules, examples, and repetition, and rely on judgment and on context loaded when needed.

## Prompting and long runs (`references/long-runs.md`)

- **Getting the most out of Opus 5.5 in Claude and Claude Code** (`opus-5-5`, 2026-09-22, Addy Osmani). Hand Opus 5.5 the whole task with a finish line, name the stops you want, and read what it needs from you first.

## Measurement and hill climbing (`references/hill-climbing.md`)

- **How we made claude.ai 3x faster in two weeks** (`faster`, 2026-09-23, Raymond Wang, Sam Attard, Issac G.). With Claude, measuring something makes it tractable, so find more things to measure and ratchet every win.

## Effort (`references/effort.md`)

- **Using Claude Code: Spending your effort** (`effort`, 2026-09-25, Thariq Shihipar). Effort buys verification and judgment. It pays on tasks with hidden edge cases, not on tasks where the approach is wrong.

## Cost and model choice (`references/cost-and-model-choice.md`)

- **What a task costs on Opus 5.5** (`cost`, 2026-09-25, Addy Osmani). You pay per task, so turns, cache hits, and retries set the bill. Every setting that saves tokens risks a retry that costs more.

## Verification (`references/verification.md`)

No post is mainly about verification, but most of them touch it. Main sources: `effort`, `skills`, `workflows`, `faster`, `cost`, `opus-5-5`.
