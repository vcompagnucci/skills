# Tool design

Which tools an agent gets and how to shape them: what earns a tool its place, how to name and describe it, how many to expose, how to keep its output from flooding context, MCP, and giving agents the instruments humans already use. Drawn from developer blog posts (several by guest customers such as Alpic, Skyscanner, and Perplexity), cookbook guides, engineering posts, the 2025 agent guide, the Agents SDK docs and migration guide, and the tool specs shipped in the Codex repo (a 2026-09-26 snapshot). Most of the evidence is practitioner experience, and the few measured results are marked.

## Decide which tools to give

- **Every tool should pass a know, do, or show test.** It adds context the model lacks (live, private, permissioned data), takes a real action for the user, or presents information better than text. If it does none of these, it adds nothing. (`great-chatgpt-app`)
- **If you can't summarize the tool surface in one sentence, the model can't either.** List the jobs to be done, ask what the user can't do without you, and turn those gaps into a handful of named operations. (`great-chatgpt-app`)
- **Prefer small composable actions over one pipeline tool.** Search, score, and send as three tools rather than one "run the full recruiting pipeline". Do your part, hand control back, and let the model pick the next tool. (`great-chatgpt-app`)
- **Tool calls against a live source can replace a retrieval pipeline.** One builder gave the model 16 tools over a music marketplace API plus web search and found it simpler than building RAG. A single builder's experience. (`responses-year`)
- **Test the tool against the no-tool baseline.** Keep a small set of positive, negative, and edge cases and track how often the tool-assisted answer beats the model's answer without it. (`great-chatgpt-app`)
- **Add a tool only when it removes a real manual loop.** Codex's guide connects external systems when context lives outside the repo, changes often, or must repeat across users, and says start with one or two. Its team guide wires in logs, deploys, and git history so an agent can trace an endpoint error to the code behind it, with scoped access tested on simulated incidents first. (`codex-best-practices`, `ai-native-team`)

- **Make business actions typed tools, not generic helpers.** OpenAI's migration guide ports domain actions (search flights, check policy) as tools with typed parameters, a description of when to use them, and structured returns. File reading, grep, and shell stay on an execution surface with an explicit boundary instead of being rebuilt as custom business tools. (`claude-sdk-migration`)

## Name and describe tools for the model

- **Write for the model as a second audience.** Plain action names, required and optional parameters made explicit, stable schemas with IDs, and a short summary paired with a machine-friendly list. "Ambiguity is a tax on routing." (`great-chatgpt-app`)
- **Make names precise and outputs look different.** "semantic_search" beats "search". Say when, why, and how to use each tool with good and bad examples, and make semantic search results look unlike grep output so the model doesn't fall back on old habits. (`codex-prompting`)
- **Replace filter UIs with enumerated parameter values.** Give the model the allowed values so it maps "sunny" to a weather value instead of guessing which options exist. (`chatgpt-apps-lessons`)
- **Mark boundaries on the tool itself.** Hints for read-only, destructive, and open-world tools, and tools the model must never call marked private. (`chatgpt-apps-lessons`)
- **Put the usage policy in the description.** Codex's tool texts say when a tool may be used and what it must not do. The web tool says browse if there's a ">10%" chance a fact changed ("if you're on the fence, you MUST browse"), and `spawn_agent` says a request for thoroughness is not permission to delegate. (`repo-tools`)
- **Enforce the limits in the handler too.** Codex's ask-the-user tool takes 1 to 3 questions ("Prefer 1") with 2 to 3 exclusive options, the recommended one first, and the client adds "Other". The handler rejects a question with no options, and default mode forbids using the tool to ask permission. (`repo-tools`, `repo-multi-agent`)
- **What the model can see is not what it may do.** One shared policy should decide which tools, MCP tools, and handoffs a run exposes, but hiding tools can't authorize a model-chosen argument or resource. That check goes inside the tool or behind an approval. OpenAI's migration guide orders it the same way: first decide what the agent sees, then gate risky calls, and it notes the Claude SDK's allowlist pre-approves calls without hiding the rest. (`sdk-context`, `claude-sdk-migration`)

## Keep tools in distribution

- **Use the formats the model was trained on.** The patch format and shell tool the coding model learned work best. A wrapper tool does well when its name, arguments, and output mirror the command underneath. A dedicated git tool plus a rule to use only it fully stopped raw terminal git calls. Codex ships its patch tool as freeform text constrained by a grammar: "do not wrap the patch in JSON". (`codex-prompting`, `repo-tools`)
- **Return structured fields, not instructions mixed into text.** Perplexity's voice tools return JSON with separate fields for user-facing text and behavior flags like "repeat verbatim", which made tool use more stable than spoken text with inline directions. (`perplexity-voice`)

## Keep the tool set small

- **Overlap matters more than count.** Some systems handle 15 or more distinct tools while others fail with fewer than 10 overlapping ones. Improve names and descriptions before splitting into more agents. (`practical-guide`)
- **Fewer, consolidated tools worked better for the data agent.** Exposing its full overlapping tool set confused it, so the team restricted and merged tools. Perplexity likewise narrowed to under ten core tools, with system-prompt instructions on when and how to call each. (`data-agent`, `perplexity-voice`)
- **Give each task only the tools it needs, with small schemas.** A deliberately wasteful support agent exposed every tool on every request. Trimming tools and payloads was part of the first round that took quality from 0.51 to 0.98, in a simulation, not a benchmark. (`cost-quality`)
- **Load tools on demand.** The Codex harness uses deferred discovery, so integrations, custom tools, skills, and plugins surface only when needed instead of sitting in context. In the repo, tool search runs BM25 over deferred tool metadata and exposes matches for the next model call. Installing a tool is allowed only after search fails, and only for the exact tool the user named. (`gpt56-efficiency`, `repo-tools`, `agents-api`)

## Keep tool output from flooding context

- **Cap output and keep the head and tail.** Truncate at about 10,000 tokens, estimating tokens as bytes divided by four, with half the budget for the start, half for the end, and a marker between. The shell does the same per command, and the harness default is 10,000 unless the model asks for a different limit. Codex's shell tool returns output or a session id to poll, and reports the original token count so the model knows how much was cut. Connector tool descriptions are capped too, at 400 tokens each and labeled untrusted. (`codex-prompting`, `computer-env`, `gpt56-efficiency`, `repo-tools`, `repo-context`)
- **Give the agent tools over its own context.** Codex exposes one tool that returns the tokens left in the window and another that starts a fresh window without touching environment state. (`repo-tools`)
- **Return only decision-critical fields.** Tool outputs "can dominate input tokens". Don't accept blob parameters or the whole conversation, request only needed fields and say why for sensitive ones, and don't return internals or secrets "just in case" (`cost-quality`, `great-chatgpt-app`). Data only the UI needs goes to a channel the model never sees (`chatgpt-apps-lessons`).
- **Let code move the data and the model make the judgment.** When an agent pulls 100 filings and filters them by date, code should run the independent calls in parallel and process results outside the context window, leaving the model only what needs judgment. OpenAI's Agents API ships this as programmatic tool calling. (`gpt56-guide`, `agents-api`)
- **Batch independent calls.** Decide every file you need first, read them in one parallel batch, and list the calls together followed by their outputs. The shell runs several commands at once in separate sessions and streams their output. (`codex-prompting`, `computer-env`)
- **Error messages can carry the fix.** Custom linters write remediation instructions into their error messages, so a failure teaches the agent the rule in its own context. (`harness-eng`)

## Computer and browser tools

- **A screenshot-driven agent needs the whole screen in one frame.** Dropdowns and pickers render in separate windows, so Atlas composites them back into the page image at the right coordinates. (`atlas-owl`)

## MCP and private tools

- **MCP is one of the shared conventions that decouple tools from any single runtime.** Along with instruction files and skills, it cuts one-off integrations. At DevDay an agent built an MCP server for the venue lights and implemented a 1990s camera protocol in an afternoon. (`devs-2025`, `codex-devday`)
- **Put setup and troubleshooting inside the agent loop.** A bundled assistant reads the local tunnel state (active profile, config, whether the server responds) so it reasons from the real setup, not generic instructions. (`private-mcp`)
- **Not every capability needs a server.** Runme registers tools in the browser, because a server just for a tool endpoint would add infrastructure and move where data is handled. Early tunnel customers also had plain REST APIs, which is why the narrow path grew beyond MCP. (`repetitive-work`, `private-mcp`)

## Key source articles
`great-chatgpt-app` · `codex-prompting` · `repo-tools` · `chatgpt-apps-lessons` · `perplexity-voice` · `private-mcp` · `gpt56-efficiency` · `practical-guide` · `sdk-context` · `claude-sdk-migration`
