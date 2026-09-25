# Multi-agent workflows and subagents

When and how to split work across agents. The June 2026 dynamic workflows post is the core; later posts add cost and steering advice.

## Why split at all

- **One long context fails in three named ways.** Agentic laziness (35 of 50 security items, then "done"); self-preferential bias (favoring its own findings when judging); goal drift (compaction is lossy and drops "don't do X"). Separate subagents with isolated goals counter all three. (`workflows`)
- **Subagents keep the main context clean.** The Claude Code Guide subagent searches docs and returns only the answer. (`seeing`) Each subagent returns a summary, but still pays for its own tokens. (`cost`)
- **Subagents are how you use a different model cheaply.** Explore agents run on Haiku with a hand-off message rather than switching the main model. (`caching`)

## Dynamic workflows

- **Claude writes the harness per task.** A JS file using `agent()`, `parallel()`, `pipeline()`, choosing each agent's model and worktree isolation, resumable after interruption. (`workflows`)
- **Dynamic beats static.** SDK or `claude -p` pipelines must handle every edge case, so stay generic; Claude can now tailor one to the question. (`workflows`)
- **Trigger it.** Ask for a workflow, or use `ultracode`; "quick workflow" for a fast adversarial check; set budgets ("use 10k tokens"); pair with `/loop` and `/goal`; save with "s" to `~/.claude/workflows`. (`workflows`)

## Six patterns

- **Classify-and-act** — a classifier routes to agents, or classifies the output. (`workflows`)
- **Fan-out-and-synthesize** — one clean context per step; synthesis is a barrier merging structured outputs. (`workflows`)
- **Adversarial verification** — a separate agent checks each output against a rubric. (`workflows`)
- **Generate-and-filter** — generate many, filter by rubric or test, dedupe. (`workflows`)
- **Tournament** — N agents attempt the same task differently; pairwise judging until one wins. (`workflows`)
- **Loop until done** — keep spawning until a stop condition (no new findings), not a fixed pass count. (`workflows`)

## Use cases from the corpus

- **Migrations.** A subagent per callsite or failing test in its own worktree, adversarial review, merge; Bun was rewritten from Zig to Rust this way. Tell agents to avoid resource-heavy commands. (`workflows`)
- **Audits.** "Give each service to its own subagent. When a subagent reports back, check its evidence before you accept it." End with one table. (`opus-5-5`)
- **Sorting 1,000+ items.** Comparative judgment beats absolute scoring: a tournament where each comparison is a fresh agent. (`workflows`)
- **Rule adherence.** One verifier per CLAUDE.md rule plus a skeptic to filter false positives; or mine past sessions for recurring corrections and distill survivors into CLAUDE.md. (`workflows`)
- **Root cause.** Hypotheses from disjoint evidence (logs, files, data), each facing verifiers and refuters — also for "why did sales drop in March?". (`workflows`)
- **Triage with quarantine.** Agents reading untrusted content get no privileges; the actor sees only their summaries. (`workflows`)
- **Deep research / deep verification.** `/deep-research` fans out searches, verifies claims, synthesizes a cited report; or one checker per factual claim. (`workflows`)
- **Taste and evals.** Explore many solutions against a rubric; compare outputs in worktrees to refine a skill. (`workflows`)
- **Model routing.** A classifier agent researches complexity and routes to Sonnet or Opus. (`workflows`)
- **Non-technical work.** Business-plan teardown from investor/customer/competitor views, resume ranking, naming tournaments. (`workflows`)
- **At org scale, parallel threads.** 150+ concurrent Slack threads, each narrow ("a hundred and fifty hammers seeking nails"). (`faster`)

## When not to

- **Most coding doesn't need it.** "Most traditional coding tasks do not need a panel of 5 reviewers"; parallelism has to earn its coordination cost. (`workflows`)
- **Teams are expensive.** Agent teams in plan mode use ~7× the tokens of a normal session; keep them small, tasks self-contained, shut teammates down. (`cost`)
- **Cheap subagent models can cost more.** A small model's misread sends the main model after the wrong file. (`cost`)

## Key source articles
`workflows` · `opus-5-5` · `cost` · `seeing` · `faster`
