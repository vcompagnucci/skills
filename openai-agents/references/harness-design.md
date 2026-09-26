# Harness design

The harness is the execution system around the model: the loop, state, tools, sandbox, approvals, and the files that carry work across hours. OpenAI's posts treat it as the reusable product, the part that tripled a benchmark score without a model change. This file covers the loop and its turns, the server and protocol that expose it, the execution environment, loop latency, and long runs. Drawn from engineering posts on openai.com, developer blog posts, and cookbook guides. What goes into the context window (layers, compaction, retained reasoning) lives in context-engineering.md.

## The harness is the product

- **An agent is the harness around the model, not a prompt plus a response.** It has to understand the task, keep context over time, inspect information, call tools, show progress, handle failures, ask for approval, and return a result. Harness choices alone can triple a benchmark score with the same model (see `context-engineering.md`). (`codex-platform`)
- **The harness runs the loop, the host application owns the fit.** The app owns the interface, business context, tools and data, and operational boundaries: where the agent runs, what it can touch, what needs approval, how work is observed, how results return to the system of record. Embed a proven harness in software built around the job instead of moving the job into a chat window. (`codex-platform`)
- **Match the integration depth to the use case.** A bounded non-interactive run with structured output for scripts and CI, a programmatic SDK to start, resume, and stream tasks, or a full client protocol (threads, turns, events, interrupts, approvals) when the agent is part of the product. (`codex-platform`)
- **The interface is part of the agent's context.** A dashboard, timeline, or record tells the agent what the user is looking at and gives the user a place to review. Users start from an action on a selected object, not a blank prompt, and consequential writes wait for approval. (`codex-platform`)
- **When the agent fails, add the missing capability instead of asking it to try harder.** Early slowness came from an underspecified environment. Ask "what capability is missing, and how do we make it legible and enforceable?", then have the agent build it, working depth-first from small blocks. (`harness-eng`)
- **Shape the interface after how the model works.** Each API generation tracked a capability shift, from text continuation to chat to a loop for reasoning models that call tools. The first fully agentic interface failed on ergonomics, not capability, and the fix was one as approachable as chat. (`responses-api`)

## The loop and its turns

- **Build a prompt, infer, run tool calls, append outputs, repeat until the model answers with a message.** One turn, from user input to final message, can hold many inference and tool iterations. For a coding agent the main output is often the edited files, not the message. (`agent-loop`)
- **Record what the model did as ordered, typed items.** Reasoning, message, and tool call as separate items make the order of actions unambiguous, where one message with attached tool calls leaves it open. That helps debugging, auditing, and richer UIs. (`responses-api`)
- **Model interaction as items inside turns inside threads.** An item (user message, agent message, tool run, approval request, diff) is started, streams deltas, and completes, so clients render at once and finalize later. A turn is one unit of work, a thread the durable container. (`app-server`)

## Serving one harness to many surfaces

- **A harness is more than the loop.** It also owns thread lifecycle and persistence (create, resume, fork, archive, replayable history), config and auth, and tool execution in a sandbox under one policy model. (`app-server`)
- **A generic tool protocol was the wrong shape for driving an agent UI.** Exposing the agent as an MCP server for an IDE lost rich session semantics like diff updates. A protocol that mirrored the terminal loop worked and hardened into a stable API. Cross-provider harness protocols trade richness for portability because they converge on the common subset. (`app-server`)
- **The channel must be two-way so the agent can pause and ask.** The server opens an approval request and the turn blocks until the client answers. One client request fans out into many events. (`app-server`)
- **Translate internal events into a small, stable set.** A handshake negotiates version and capabilities, and backward compatibility lets an old client point at a newer server and still get fixes and better compaction. (`app-server`)
- **Keep state on the server when clients come and go.** Browser tabs close and networks drop, so the web client can't be the source of truth. The same move lets a terminal drive an agent on a remote machine that keeps working while the laptop sleeps. (`app-server`)

## The execution environment

- **A general shell beats a single-language interpreter.** Standard Unix tools run any language, start servers, search text, and call APIs. The model only proposes commands, and the orchestrator runs them and feeds results back until the model stops calling tools. (`computer-env`)
- **Stage inputs in the workspace instead of packing them into the prompt.** Put files on disk and let the model choose what to open. Put structured data in SQLite with only a description of the tables, so the model queries the rows it needs. Streaming command output lets it wait, run something else, or move on. (`computer-env`)
- **Use disk as the handoff boundary.** Write deliverables to a known folder so the app can show, log, diff, or pass them on: "Tools write to disk, models reason over disk, developers retrieve from disk." Reuse the same environment across steps, start local, and move to hosted containers with the same skills. (`skills-shell`)

## Loop latency

- **Anything inside the repeated part of a turn is paid many times.** One turn can hold 30 model requests, so an extra second each adds up. Speed comes from cutting repeated work across the loop, not only from a faster model. (`gpt56-efficiency`)
- **Treating every turn as an independent request is the structural cost.** Loop time splits into service overhead, inference, and client-side tools, and faster inference exposes the overhead. Per-request fixes gave about 45% better time to first token, not enough for a model near 1,000 tokens per second. (`websockets`)
- **Keep state across the loop and send only what's new.** A persistent connection caches the previous response, items, tool definitions, and rendered tokens, so safety checks see only new input and post-inference work overlaps the next request. Measured: up to 40% faster loops, with partners reporting 30% to 40%. A prototype that treated the whole rollout as one long response was faster but shipped in a more familiar shape. (`websockets`)
- **Run tools next to the model when you can.** Server-side retrieval, code execution, and MCP skip a round trip through the developer's backend. (`responses-api`)
- **Long-running agents need infrastructure primitives.** Work that runs without holding a client connection, and event-driven completion instead of polling. (`devs-2025`)

## Long-horizon runs

- **Coherence comes from the loop, not a clever prompt.** Plan, edit, run tools, observe, repair, update docs and status, repeat. The loop supplies real feedback, state outside the model, and a place to steer, which is why the same model feels better in a coding harness than in chat. (`long-horizon`)
- **One run held together for about 25 hours.** Blank repo, one job (build a design tool), about 13M tokens and 30k lines, with tests, lint, and typecheck at every milestone. Framed as an experiment, "not perfect or production-ready". Pick a test task you can't bluff. (`long-horizon`)
- **Durable project memory was the most important technique.** Four files the agent rereads: a spec (goals, non-goals, constraints, "done when"), a plan (milestones sized for one loop, each with acceptance criteria and validation commands), a runbook, and a status log. If a milestone's validation fails, fix it before moving on. (`long-horizon`)
- **A plan document drove more than seven hours from one prompt.** Write it for a novice who has only the working tree and this file, and keep it restartable from the plan alone, with living sections for progress, surprises, a decision log, and outcomes. During the run the agent doesn't ask for next steps, it resolves ambiguity and records why. (`exec-plans`)
- **Anchor milestones on observable behavior.** "Navigating to /health returns 200 OK", not "added a HealthCheck struct". Make steps idempotent and verifiable, and de-risk unknown libraries with labeled prototype milestones. (`exec-plans`)
- **Plans and goals answer different questions.** A plan answers "how should we approach this?", a goal "what must be true before we are done?" Plan the risky change, then turn the accepted outcome into a goal with a concrete completion condition so the agent keeps going. A strong goal: port the library, keep the API compatible, done when the original tests pass. (`codex-remote`, `codex-maxxing`)
- **Give important workstreams a durable thread and scheduled wake-ups.** A recurring wake-up returns to the same thread with context intact and can run until a condition holds, like triaging mail every 30 minutes and drafting replies without sending. The agent prepares, the human owns approval and irreversible steps. Long threads cost more than fresh ones. (`codex-maxxing`)
- **Keep the goal, plan gate, and log inside the working artifact.** A notebook cell tells the agent to review a previous run, write a plan there, wait for approval, and log commands, output, and interpretation. Decisions get captured before closing, and a companion index lets future agents find past runs. (`repetitive-work`)
- **Save the plan to a file before context runs out.** Other sessions then follow the same direction, review becomes a check against the plan, and debugging starts with the plan. (`sora-android`)

## Where the posts disagree

- **Stateless or stateful loop.** `agent-loop` (2026-01-23) resends the full history on every request to keep requests stateless and serve zero-data-retention customers. `app-server` (2026-02-04) keeps thread state on a server because clients are ephemeral, and `websockets` (2026-04-22) caches response state per connection to stop reprocessing history, measured up to 40% faster. The later posts don't say how they handle the retention case.
- **Stop at every failure, or keep moving.** `long-horizon` (2026-02-23) requires fixing a failed milestone before the next one. `harness-eng` (2026-02-11) runs minimal blocking merge gates and reruns flaky tests because "corrections are cheap, and waiting is expensive", and calls that irresponsible at low throughput. They gate different things: a milestone inside one run versus merges across many.

## Key source articles
`agent-loop` · `app-server` · `codex-platform` · `long-horizon` · `exec-plans` · `websockets` · `computer-env` · `codex-maxxing` · `gpt-live`
