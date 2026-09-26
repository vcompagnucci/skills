# Tool design

How Anthropic decides which tools an agent gets and how to write them. Tools are the agent-computer interface (ACI), and Anthropic treats them with the care people give human interfaces: shaped to what the model can do, tested by reading its outputs, kept few, and retired when models outgrow them. Cookbook notebooks add worked examples of tools that write to production systems.

## Design tools for agents

- **Invest as much in the agent-computer interface as in human interfaces.** On SWE-bench the team spent more time on tools than on the prompt. Requiring absolute file paths fixed relative-path mistakes "flawlessly", and string replacement that must match exactly once was the most reliable edit strategy. (`effective-agents`, `swe-bench`)
- **A tool is a contract with a non-deterministic caller.** The agent may call it, skip it, ask a question, or misuse it, so don't wrap every API endpoint. Tools that are ergonomic for agents also turn out intuitive for humans. (`writing-tools`)
- **Fewer, consolidated tools beat one per endpoint.** Prefer `search_contacts` to `list_contacts`, and `schedule_event` to three separate calls. Group around intent: one `create_issue_from_thread` beats four tools. "Fewer, well-described tools consistently outperform exhaustive API mirrors." (`writing-tools`, `mcp-production`)
- **Descriptions are prompts, and they carry more weight than schemas.** Describe the tool as to a new hire and name parameters unambiguously (`user_id`, not `user`). Precise description edits took Claude 3.5 Sonnet to SWE-bench state of the art. Claude appending "2025" to every web search was fixed in the description. An SRE agent built the right PromQL query from the description alone, and descriptions should say what the tool returns. (`writing-tools`, `swe-bench`, `cb-sre-agent`, `cb-threat-intel`, `cb-support-agent`)
- **Return high-signal context, and make errors steer.** Drop fields like `uuid` and `mime_type`, and resolve IDs to names. A `response_format` enum let a Slack response use about a third of the tokens. Truncation notes and errors should say what to do next, not dump a traceback. (`writing-tools`, `commerce-agents`)
- **Namespace tools by service.** `asana_search` versus `jira_search`. Prefix versus suffix naming had model-dependent effects in evals. (`writing-tools`)
- **Design the interface instead of writing examples.** With Claude 5 models, examples narrow what the model tries, while expressive parameters, like a `status` enum, teach usage. (`ctx-eng`)
- **But schemas don't show usage patterns.** For ambiguous parameters, 1-5 realistic examples in the definition raised accuracy on complex parameters from 72% to 90% (2025). This sits in tension with the Claude 5 advice above. (`advanced-tool-use`, `ctx-eng`)
- **A deterministic retrieval tool can matter more than the model (research).** On 120 viral-sequence queries, agents without one scored 16.9% to 91.3%, and one model returned 106, then 15, then 5 sequences for the same query, shifting an inferred outbreak origin to 1922. A tool wrapping NCBI's APIs lifted every model above 90% and narrowed the gap between models. The authors hedge that better models may need it less. (`agents-in-biology`)

## Improve tools from evidence

- **A tool only works if the model likes calling it.** AskUserQuestion took three attempts before a dedicated tool that blocks the loop beat a plan-tool parameter and a custom markdown format. (`seeing`)
- **Evaluate with realistic multi-step tasks, then let Claude refactor the tools.** Paste eval transcripts into Claude Code. Claude-optimized Slack and Asana tools beat expert human-written ones on held-out tests. Read what agents omit, not only what they say. (`writing-tools`)
- **A tool-testing agent can fix bad descriptions.** One used a flawed MCP tool dozens of times, rewrote its description, and cut future task time 40%. (`research-system`)

## Keep the tool set small

- **The bar to add a tool is high.** Claude Code has about 20, and each one is another option to weigh. The Claude Code Guide subagent answers questions about Claude Code without adding a tool. (`seeing`)
- **Too many or overlapping tools is one of the most common failures.** "If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better." (`effective-context`)
- **Load tool definitions on demand.** Five MCP servers can mean 58 tools and 55K tokens before work starts. With `defer_loading` and the Tool Search Tool, context fell 85% and MCP eval accuracy rose from 49% to 74% on Opus 4. Use it past about 10 tools or 10K tokens, and keep the 3-5 most used always loaded. (`advanced-tool-use`, `caching`)

## Let code do the orchestration

- **Present MCP servers as code the agent calls.** One file per tool in a folder the agent explores cut usage from 150,000 to 2,000 tokens (98.7%). Filtering a 10,000-row sheet in code shows the model five rows, and PII can pass between systems tokenized, without entering context. The cost is a sandbox to run the code. (`mcp-code-exec`)
- **Programmatic tool calling suits 3+ dependent calls or large data.** In the travel-budget example, a script over 20 people's expenses cut 200KB to 1KB, and average tokens fell 37%. Skip it when Claude should see the intermediate results. (`advanced-tool-use`)
- **For huge APIs, expose a thin tool that runs code.** Cloudflare covers about 2,500 endpoints with two tools in roughly 1K tokens. (`mcp-production`)
- **Scripts beat traditional tools for many jobs.** Code is self-documenting and doesn't sit in context. When Claude kept rewriting the same slide-styling script, they had it save the script as a tool for itself. (`skills-for-agents`)

## MCP

- **MCP collapses the M×N integration problem.** A client connects to thousands of servers, and a vendor builds one server for every assistant. (`what-is-mcp`)
- **Build remote servers.** Production agents run in the cloud, behind auth, and remote is the only setup that works across web, mobile, and hosted agents. (`mcp-production`)

## Tools that act on production

- **Give write access through narrow, checked tools, not a shell.** The SRE agent's config editor only writes under `config/`, its shell only runs `docker` commands, and a `PreToolUse` hook rejects a `DB_POOL_SIZE` outside 5-100, checking what changes, not just where. Investigation runs read-only, and remediation waits for a separate authorization. (`cb-sre-agent`)
- **Pick an MCP toolset or a custom tool by reachability.** Public internet plus a bearer token suits an MCP toolset. A system inside your network needs a custom tool your application runs, as in the MongoDB example, which runs `pymongo` host-side. (`cb-production`, `cb-mongodb`)
- **Cap the loop and split formatting from analysis.** The threat-intel loop has a `MAX_TURNS` limit against runaway cost, and turns its free-text findings into schema-constrained JSON in a second call with a formatter-only prompt. (`cb-threat-intel`)

## Special tools

- **The "think" tool (2025).** A tool that changes nothing gave Claude a place to reason mid-task, reaching 0.570 versus 0.370 on τ-bench airline with a tuned prompt. A later note says extended thinking now gives similar benefits in most cases. (`think-tool`)
- **Computer use depends on harness hygiene.** Pre-downscaling screenshots is the single highest-impact fix, while tiling and coordinate grids didn't help. A recorded demonstration beats iterating on text prompts. (`computer-use`)
- **Target page structure, not pixels, on the web.** The browser tool reads the page structure alongside the screenshot and takes several actions per turn. (`production-apis`)

## Key source articles
`writing-tools` · `advanced-tool-use` · `mcp-code-exec` · `seeing` · `swe-bench` · `effective-agents` · `mcp-production` · `computer-use`
