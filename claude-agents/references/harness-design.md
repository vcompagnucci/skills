# Harness design

The harness is everything around the model: the loop, tools, context management, and guardrails. Anthropic's position, repeated across its engineering and product posts, is that every harness piece encodes an assumption about what Claude can't do, that those assumptions expire with each model, and that the job is to keep testing what you can take out.

## Assumptions go stale

- **Every harness component encodes an assumption about what the model can't do.** Radical cuts failed, but removing one component at a time worked. With Opus 4.6 the sprint construct was dropped and the evaluator moved to one pass at the end, while the planner stayed because without it the generator under-scoped. "The space of interesting harness combinations doesn't shrink as models improve. Instead, it moves." (`harness-design-apps`)
- **Context anxiety is the standard example.** Sonnet 4.5 wrapped up early as it sensed its context limit, so harnesses added context resets. On Opus 4.5 the behavior was gone and the resets "had become dead weight". (`managed-agents`, `harness-patterns`, `agentic-surfaces`, `harness-design-apps`)
- **Tools expire too.** TodoWrite plus reminders every 5 turns kept early models on task, then started holding stronger ones back, and the Task tool replaced it. (`seeing`)
- **An evaluator is worth its cost only beyond the model's solo boundary.** On Opus 4.5, builds sat at the edge of what the generator could do. On 4.6 the boundary moved out and the evaluator became overhead for tasks inside it. (`harness-design-apps`)

## Build on what Claude already knows

- **Keep scaffolding minimal and give the model control.** A prompt, a Bash tool, and an Edit tool took Claude 3.5 Sonnet to 49% on SWE-bench Verified, then state of the art. Sample until the model decides it's done. (`swe-bench`, `harness-patterns`)
- **Give your agent a computer.** The harness behind Claude Code powers almost all of Anthropic's major agent loops, including research, video, and note-taking, which is why the Claude Code SDK became the Claude Agent SDK. The loop is: gather context, take action, verify work, repeat. (`agent-sdk`)
- **Move orchestration from the harness to the model.** When Claude writes code that filters its own tool results, only the output reaches context. On BrowseComp, letting Opus 4.6 filter its tool outputs took accuracy from 45.3% to 61.6%. "A strong coding model is also a strong general agent." (`harness-patterns`)
- **Let Claude choose what to keep.** With a memory folder, Sonnet 4.5 on BrowseComp-Plus rose from 60.4% to 67.2%. Playing Pokémon, Sonnet 3.5 left 31 transcript-like files and was still in the second town after 14,000 steps. Opus 4.6 left 10 organized files, three badges, and a learnings file. (`harness-patterns`)
- **Promote an action to its own tool only when the harness needs a hook.** Bash gives the harness just a command string. A typed tool can be gated, rendered, logged, or checked for staleness, so hard-to-reverse actions and blocking modals earn one. Auto mode, where a second Claude judges each bash command, reduces how many need it. (`harness-patterns`)

## Structure for long runs

- **Compaction alone isn't enough across many context windows.** Given only "build a clone of claude.ai", Opus 4.5 in a loop falls short. Agents either try to one-shot everything and run out of context mid-feature, or a later session sees progress and declares victory. (`long-running-harness`)
- **Use an initializer agent, a feature list, and one feature per session.** The first session writes `init.sh`, a progress file, and a first commit, and expands the prompt into 200+ features marked failing in JSON (JSON because the model is less likely to overwrite it). Every later session gets its bearings, smoke-tests, fixes one feature, commits, and logs progress. (`long-running-harness`)
- **Separate the builder from a skeptical grader.** A planner, a generator, and an evaluator with sprint contracts turned a one-line retro game prompt from a broken 20-minute, $9 build into a working 6-hour, $200 one. Out of the box Claude is a poor QA agent: it finds real issues, then talks itself into approving. (`harness-design-apps`)
- **Write the harness for Claude, not for yourself.** Fresh containers need maintained READMEs and progress files. Tests should print a few lines and log the rest, and a default `--fast` sample counters time blindness. (`c-compiler`)

## Production infrastructure

- **Infrastructure, not the prompt, separates a prototype from a production agent.** The recurring problems are hosting, sessions, filesystem, execution isolation, credentials, and observability. For most teams, maintaining a harness is overhead that doesn't differentiate their product. (`agentic-surfaces`)
- **Decouple the brain from the hands.** Running the harness in the same container as the code made containers "pets": a dead container lost the session, and credentials sat next to generated code. Managed Agents virtualizes session (an append-only log), harness, and sandbox behind stable interfaces, so each can be swapped. Time to first token dropped about 60% at p50 and over 90% at p95. (`managed-agents`, `agentic-surfaces`)
- **The session is not the context window.** Compaction and trimming are irreversible bets on which tokens you'll need. A durable event log outside the window lets the harness fetch and transform what it needs, and makes resuming, observability, and memory come free. (`managed-agents`, `agentic-surfaces`)
- **The surface evolved from a single-turn API to a managed harness.** 2023: one request, one turn, you build the loop. Then Claude Code, then the Agent SDK exposing its harness, then Managed Agents with hosted infrastructure. (`agentic-surfaces`)

## Contrast worth knowing

- **Own the harness, or let Anthropic run it?** The Managed Agents posts argue most teams should spend effort on context and domain expertise, not the harness (`agentic-surfaces`). Customer stories show teams still customizing: Outtake prototyped in Claude Code, then moved to the Agent SDK for control over memory and filesystem (`outtake`).

## Key source articles
`harness-patterns` · `managed-agents` · `agentic-surfaces` · `harness-design-apps` · `long-running-harness` · `swe-bench` · `agent-sdk`
