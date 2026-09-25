# Multi-agent workflows and subagents

When and how to split work across agents. The June 2026 post on dynamic workflows is the main source. Later posts add cost and steering advice.

## Why split at all

- **One long context fails in three named ways.** Agentic laziness: Claude handles 35 of 50 items in a security review and calls it done. Self-preferential bias: it favors its own findings when judging them. Goal drift: compaction loses details, including "don't do X" constraints. Separate subagents, each with its own context and goal, counter all three. (`workflows`)
- **Subagents keep the main context clean.** The Claude Code Guide subagent searches the docs and returns only the answer (`seeing`). Each subagent hands back a summary, but it still pays for its own tokens (`cost`).
- **Subagents let you use a different model cheaply.** Claude Code's Explore agents run on Haiku and get a hand-off message, instead of the main session switching models. (`caching`)

## Dynamic workflows

- **Claude writes the orchestration script for each task.** It's a JS file that uses `agent()`, `parallel()`, and `pipeline()`. It picks each agent's model, decides which ones get their own worktree, and resumes where it left off after an interruption. (`workflows`)
- **Dynamic beats static.** A pipeline built with the SDK or `claude -p` has to handle every edge case, so it stays generic. Claude can now write one for the specific question. (`workflows`)
- **How to start one.** Ask for a workflow, or use the word `ultracode`. Ask for a "quick workflow" for a fast adversarial check. Set a budget ("use 10k tokens"). Pair it with `/loop` and `/goal`. Press "s" to save it to `~/.claude/workflows`. (`workflows`)

## Six patterns

- **Classify-and-act.** A classifier sends the task to different agents, or classifies the output at the end. (`workflows`)
- **Fan-out-and-synthesize.** One agent per step, each in a clean context. A final step waits for all of them and merges their outputs. (`workflows`)
- **Adversarial verification.** A separate agent checks each output against a rubric. (`workflows`)
- **Generate-and-filter.** Generate many options, filter them by rubric or test, and drop duplicates. (`workflows`)
- **Tournament.** N agents try the same task in different ways, and pairwise judging continues until one wins. (`workflows`)
- **Loop until done.** Keep spawning agents until a stop condition holds, such as no new findings, instead of running a fixed number of passes. (`workflows`)

## Use cases from the posts

- **Migrations.** One subagent per call site or failing test, each in its own worktree, then adversarial review, then merge. Bun was rewritten from Zig to Rust this way. Tell the agents to avoid heavy commands so more of them can run at once. (`workflows`)
- **Audits.** "Give each service to its own subagent. When a subagent reports back, check its evidence before you accept it." End with one table. (`opus-5-5`)
- **Sorting 1,000+ items.** Comparing two items is more reliable than scoring each one. Run a tournament where each comparison gets a fresh agent. (`workflows`)
- **Following rules.** One verifier per CLAUDE.md rule, plus a skeptic agent to throw out false positives. Or go the other way: mine past sessions for corrections you keep making and turn the ones that survive review into CLAUDE.md rules. (`workflows`)
- **Root causes.** Separate agents build hypotheses from separate evidence (logs, files, data), and each hypothesis faces agents that try to confirm it and agents that try to refute it. It works for "why did sales drop in March?" too. (`workflows`)
- **Triage with quarantine.** Agents that read untrusted content get no privileges. The agent that acts sees only their summaries. (`workflows`)
- **Deep research and deep verification.** `/deep-research` runs many searches in parallel, verifies the claims, and writes a cited report. For verification, one checker per factual claim. (`workflows`)
- **Taste and evals.** Explore many solutions against a rubric, or compare outputs in separate worktrees to improve a skill. (`workflows`)
- **Choosing the model.** A classifier agent looks at how complex the task is and routes it to Sonnet or Opus. (`workflows`)
- **Work that isn't code.** Tearing apart a business plan from an investor's, a customer's, and a competitor's view. Ranking resumes. A naming tournament. (`workflows`)
- **At team scale, many threads at once.** More than 150 Slack threads ran at the same time, each on one narrow problem: "a hundred and fifty hammers seeking nails". (`faster`)

## When not to

- **Most coding doesn't need it.** "Most traditional coding tasks do not need a panel of 5 reviewers." Running agents in parallel has to be worth what it costs to coordinate them. (`workflows`)
- **Teams are expensive.** Agent teams in plan mode use about 7× the tokens of a normal session. Keep them small, give each teammate a self-contained task, and shut them down when they're done. (`cost`)
- **A cheap subagent model can end up costing more.** If a small model misreads a search result, the main model goes after the wrong file, and you pay for that. (`cost`)

## Key source articles
`workflows` · `opus-5-5` · `cost` · `seeing` · `faster`
