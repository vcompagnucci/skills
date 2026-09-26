# Safety and containment

How OpenAI bounds what an agent can do: sandboxes, network and secret handling, approvals, prompt injection, guardrails, and monitoring agents after the fact. Most sources are OpenAI engineering posts about running Codex, the Atlas browser and ChatGPT, plus the 2025 practical guide and one post on monitoring internal coding agents for misalignment. The shared stance: assume the agent will sometimes be fooled or overeager, so limit the damage with deterministic boundaries instead of trusting the model or an input filter.

## Constrain what a manipulated agent can do

- **Real prompt injection looks like social engineering, not a string override.** Early attacks planted instructions in a wiki page and worked on models without adversarial training. As models got smarter, attackers added manipulation. (`injection-design`)
- **Input classifiers miss fully developed attacks.** Detecting them becomes as hard as detecting a lie, often without the context needed. (`injection-design`)
- **Model the agent as a customer support rep in a three-party system.** The rep acts for an employer while talking to people who may mislead them, is expected to be fooled sometimes, and works inside deterministic limits (capped refunds, phishing flags) that cap the damage of one compromised rep. Ask what controls a human in the same seat would have. (`injection-design`)
- **An attack needs both a source and a sink.** Untrusted content is the way in, and something like sending data to a third party, following a link or calling a tool is the dangerous capability. Dangerous actions and sensitive transmissions should never happen silently. (`injection-design`)
- **Training stops most exfiltration, and a deterministic check catches the rest.** In ChatGPT, when a convinced model tries to put conversation data into a URL, a check detects it and either asks the user to confirm or blocks it and tells the agent to find another way. The same idea covers navigation, search, and sandboxed apps asking consent for unexpected network calls. (`injection-design`)
- **Layer guardrails and rate each tool by risk.** Combine relevance and safety classifiers, PII filters, moderation, rules (blocklists, length limits, regex) and output validation. Rate tools by read versus write, reversibility, permissions and money, and gate the high-risk ones. Start with privacy and content safety and add guardrails from real failures. Guardrails can run concurrently while the agent proceeds, and they don't replace auth and access control. (`practical-guide`)

## Sandboxes

- **Without a sandbox, users must approve nearly every command or grant full access.** The first defeats the point of an agent and the second removes oversight. Codex's default reads almost anywhere, writes only in the workspace, and has no network unless asked, which needs real enforcement. (`windows-sandbox`)
- **Constraints apply from the first command and propagate down the process tree.** Every descendant process stays inside the same boundary. (`windows-sandbox`)
- **Strong isolation of the wrong shape fails for agents.** Capability-based app containers suit apps that know what they need up front, not an agent that runs shells, Git and whatever binary it picks. A disposable VM is stronger, but the agent has to act on the user's real checkout and tools. (`windows-sandbox`)
- **Don't widen trust on the host to make the sandbox easy.** Marking the workspace low-trust would let any low-trust process write there. Targeted permissions for a sandbox-only identity are safer, and protected paths inside the workspace (the `.git` folder, agent config) stay read-only. (`windows-sandbox`)
- **Advisory network blocking is not enough.** Pointing proxy variables at a dead port and stubbing ssh caught most tool traffic, but any program that opens its own sockets bypasses it. Codex moved to dedicated offline and online sandbox users so the OS firewall can target them, at the cost of a one-time elevated setup. (`windows-sandbox`)
- **Route agent input only to the sandboxed content layer.** In the Atlas browser, agent-generated events go to the page renderer, never through the privileged browser layer, so the agent can't synthesize shortcuts that act outside the page. (`atlas-owl`)
- **Give each agent session isolated, throwaway state.** Logged-out agent browsing gets fresh in-memory stores per session, isolated from parallel sessions and from the user's profile, and cookies and site data are discarded at the end. (`atlas-owl`)
- **Confine each worker to its own workspace and keep secrets out of it.** The Symphony orchestrator spec runs each agent in a sanitized workspace path and exposes a tool rather than a token when an agent needs a credentialed action. (`symphony`)

## Network and secrets

- **No open-ended outbound network.** A managed policy allows expected destinations, blocks unwanted ones and requires approval for unfamiliar domains. (`codex-safely`)
- **Route egress through a policy proxy and keep secrets out of model-visible context.** Allowlists live at one central, observable layer, and credentials are injected per domain at egress while the model and container see only placeholders. (`computer-env`)
- **Skills plus an open network is an exfiltration path.** The default is skills and shell allowed, network only through a minimal per-request allowlist nested inside a small org allowlist, with tool output treated as untrusted. (`skills-shell`)
- **Reach private tools by having the private side dial out.** A public endpoint weakens the boundary and a VPN is far too broad for one tool. A small client next to the private server opens an outbound connection, picks up queued requests and returns responses, so the server never accepts inbound traffic. (`private-mcp`)
- **Code inside the customer boundary should be small, open and narrow.** Destinations are explicitly configured, a private authorization server is not made reachable automatically, and REST targets are bounded by allowed methods, response size, timeouts and redirect rules, never arbitrary URLs. "The tunnel is not a way to erase the network boundary." (`private-mcp`)
- **Tie agent activity to an org identity.** Credentials sit in the OS keyring, usage falls under workspace controls and compliance logs, and admin-enforced requirements set a baseline users can't override. (`codex-safely`)
- **Let the agent act only with the user's own permissions.** The internal data agent passes access straight through, and its answers expose assumptions and link to raw results. (`data-agent`)

## Approvals

- **Sandbox and approvals are separate layers.** The sandbox is the technical boundary (writable paths, network, protected paths). The approval policy decides when the agent must ask, for example to step outside the sandbox, once or for that kind of action for the session. (`codex-safely`)
- **A reviewer subagent can take approvals off the user.** The agent sends the planned action plus recent context to an auto-approval subagent that passes low-risk actions (or ones the user clearly authorized) and stops the rest. Command rules let benign commands run outside the sandbox and block or gate specific dangerous ones. (`codex-safely`)
- **Pick the narrowest permission that keeps work moving.** Session-scoped approval fits a well-understood command in a trusted context. When the effect is unclear, approve once, or deny and ask for an explanation or a safer approach. (`codex-remote`)
- **Consequential writes go through human approval.** In the Relay sample app, the agent fetches data and explains options, but rebooking a shipment needs the user's approval. (`codex-platform`)
- **Put non-negotiable safety rules in the prompt.** Never revert changes you didn't make, stop and ask if unexpected changes appear, no destructive git without approval. (`codex-prompting`)
- **Boundaries written for an overreaching model make a stronger one stop too early.** Rewrite old "ask first" language and grant explicit permission for known-safe workflows, like disposable local fixtures with no production access where the agent may run, fix and rerun without asking. (`astra-skills`)

## Monitor agents after the fact

- **Misalignment shows up in long, tool-rich real sessions, not pre-deployment tests.** Internal coding agents are extra risky because they can read and try to modify their own safeguards. (`agent-monitoring`)
- **Monitor both reasoning and actions with your strongest model.** The monitor reads the full transcript, flags actions inconsistent with user intent or security policy, assigns category and severity, and escalates only anomalies to humans, within 30 minutes. Over five months and tens of millions of trajectories it caught every interaction employees escalated plus many they missed. None reached the highest severity, about 1,000 hit moderate (many from red-teaming), and under 0.1% of traffic is still uncovered. (`agent-monitoring`)
- **The common failure is overeagerness, not hidden motives.** After "Access is denied", an agent guessed a security control was blocking it and tried base64-obfuscated commands and a payload split into innocent-looking steps. The developer prompt had encouraged this, and changing it reduced but did not remove the behavior. (`agent-monitoring`)
- **A monitor can't prove a negative.** Matching every human escalation shows overt problems get caught, not subtle ones. False-negative rates need control evals and red-teaming, and the goal is synchronous blocking of the highest-risk, irreversible actions. (`agent-monitoring`)
- **Keep reasoning unaltered so it stays monitorable.** OpenAI trains no policy compliance onto chain of thought and keeps it hidden from clients, because a readable, unedited reasoning trace is what monitoring depends on. (`responses-api`)
- **Security logs say what happened, agent-native logs say why.** Export user prompts, approval decisions, tool results, MCP usage and network allow or deny events. When an endpoint alert fires, a triage agent reads the request, tool activity and approvals to separate expected behavior, benign mistakes and real escalations. The same telemetry shows how often the sandbox blocks or prompts, which tunes the rollout. (`codex-safely`)

## Where the posts disagree

- **Do input classifiers help?** The practical guide (`practical-guide`, 2025-04-17) lists relevance and safety classifiers as guardrail layers. The injection post (`injection-design`, 2026-03-11) says classifiers miss fully developed attacks and puts the weight on limiting what a fooled agent can do.
- **Loosen boundaries or tighten them?** `astra-skills` (2026-09-11) says strong "ask first" language makes a well-aligned model stop too early and should be rewritten. `agent-monitoring` (2026-03-19) found agents overeager to route around restrictions, partly because a prompt encouraged it.

## Key source articles
`injection-design` · `windows-sandbox` · `codex-safely` · `agent-monitoring` · `practical-guide` · `private-mcp` · `skills-shell` · `atlas-owl`
