# Article index

All 10 posts on claude.dev (2026-04-10 → 2026-09-25), grouped by primary theme. Citations use short keys; each maps to `https://claude.dev/blog/<slug>/`. Excluded from the corpus: `/terminal/` (a UI) and `/terms/` (legal).

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

- `seeing` — **Seeing like an agent: how we design tools in Claude Code** (2026-04-10, Thariq Shihipar) — Shape tools to the model's abilities by reading its outputs, keep the set small, and retire tools the model outgrows.

## Prompt caching (`references/prompt-caching.md`)

- `caching` — **Lessons from building Claude Code: Prompt caching is everything** (2026-04-30, Thariq Shihipar) — Caching is a prefix match, so never change the prefix: static first, updates as messages, no tool or model swaps, cache-safe compaction.

## HTML outputs (`references/html-outputs.md`)

- `html` — **Using Claude Code: The unreasonable effectiveness of HTML** (2026-05-20, Thariq Shihipar) — HTML beats Markdown for agent output because people actually read it, which keeps them in the loop.

## Multi-agent workflows (`references/multi-agent-workflows.md`)

- `workflows` — **A harness for every task: dynamic workflows in Claude Code** (2026-06-02, Thariq Shihipar and Sid Bidasaria) — Claude can write a custom multi-agent harness per task, countering laziness, self-preference, and goal drift on long or adversarial work.

## Skills (`references/skills.md`)

- `skills` — **Lessons from building Claude Code: How we use skills** (2026-06-03, Thariq Shihipar) — Good skills are single-category folders that push Claude off its defaults with gotchas, scripts, and progressive disclosure.

## Context engineering (`references/context-engineering.md`)

- `ctx-eng` — **The new rules of context engineering for Claude 5 generation models** (2026-07-24, Thariq Shihipar) — Claude 5 models are overconstrained; delete rules, examples, and repetition, and rely on judgment and progressive disclosure.

## Prompting and long runs (`references/long-runs.md`)

- `opus-5-5` — **Getting the most out of Opus 5.5 in Claude and Claude Code** (2026-09-22, Addy Osmani) — Hand Opus 5.5 the whole task with a finish line, name the stops you want, and read what it needs from you first.

## Measurement and hill climbing (`references/hill-climbing.md`)

- `faster` — **How we made claude.ai 3x faster in two weeks** (2026-09-23, Raymond Wang, Sam Attard, Issac G.) — With Claude, measuring something makes it tractable, so find more things to measure and ratchet every win.

## Effort (`references/effort.md`)

- `effort` — **Using Claude Code: Spending your effort** (2026-09-25, Thariq Shihipar) — Effort buys verification and judgment, so it pays on tasks with hidden edge cases, not on tasks with a wrong approach.

## Cost and model choice (`references/cost-and-model-choice.md`)

- `cost` — **What a task costs on Opus 5.5** (2026-09-25, Addy Osmani) — You pay per task, so turns, cache hits, and retries set the bill, and every token-saving setting risks a costlier retry.

## Verification (`references/verification.md`)

Cross-cutting theme; no post is primarily about it. Main sources: `effort`, `skills`, `workflows`, `faster`, `cost`, `opus-5-5`.
