# Operations

## Versions

- **Every change to prompt, model, or tools is a new pinned version,** tested on a staging copy before production. After staging, give a new version a small share of new conversations (Ada starts at 1%), then widen. Rollback is re-pinning the last good version, but keep the newer version runnable until the runs it paused drain, because older code rejects state saved by newer code. Anthropic's sales team rolled back to an older version after a week, and could only because versions were pinned.
- **Why every run finishes on its version (SKILL.md rule 8):** tool descriptions, schemas, prompts, and approval policy are how the model reads its own history, so a retried run on new code misreads old results without crashing. A risk score rescaled from 0-10 to 0-100 read an old 8 as nearly clean. Prefer runs that end per task over one long-lived workflow so old versions drain fast, and keep an audited way to move or restart a stuck run on a new version.
- **Pin nested versions too.** An orchestrator pins each specialist's version when it is created or updated, so shipping a specialist means re-releasing the orchestrator, and rolling back means re-pinning both. Update agent definitions with optimistic concurrency (send the version you read; a mismatch fails), because an update without a version silently overwrites someone else's.
- **Pin ready-made harnesses, agent SDKs, and hosted agents to an exact release and a named endpoint, never the default alias.** Patch releases change defaults, prompt text, and tool descriptions (a Claude Agent SDK patch changed the default permission mode), and a default endpoint follows the latest version. Own the prompt text and plan for migration windows of weeks: Google retired one Gemini agent version 18 days after its successor shipped.
- **At a model change, test the response shape, not only quality.** A new model can move the status notes your UI streams between tool calls into a block that comes back empty by default, so the UI goes quiet with no error (Sonnet 5.5). It can also reject parameters the old one accepted.
- **At a model change, re-check every setting counted in tokens.** A new tokenizer can yield about 30% more tokens for the same text, shifting every compaction trigger, output cap, and budget. Read context and output limits from the provider's model metadata instead of hardcoding them.
- **Set effort, reasoning retention, and sampling explicitly as part of the version.** An upgrade can change the defaults cost and quality depend on (Gemini 3.5 lowered default thinking from high to medium and kept earlier reasoning by default), so remove settings the new model deprecates and measure cost again after the upgrade.

## Latency and cost

- **Anything repeated inside the loop is paid on every model call.** Cut re-sent history and run independent tool calls in parallel before buying a faster model.
- **In chat, end the turn at the first question the agent has to ask anyway** instead of gathering everything first. Rappi cut its first turn from over 60 seconds to 20.
- **Move work that doesn't change the reply off the customer's path:** QA scoring, tagging, summaries, and memory writing run after the reply is sent.
- **Pick the model in the harness at the start of the conversation:** a small model for routine questions, the largest for account access and disputes. A step that needs another model goes to a subagent on that model; switching the conversation's own model follows failures.md. Factory modeled cache-blind switching at 2.12 times the cost of staying on the frontier model by turns 61 to 150, and cache-aware routing at 0.19 to 0.28 times.
- **Route deadline-bound steps to low effort.** Thinking time itself makes those tasks fail: on Meta's time-sensitive Gaia2 tasks, GPT-5 at high effort scored 0.0%, and 34.4% once generation latency was taken out.
- **Give each run a spending budget.** Reserve the worst-case cost before each model call and settle to the real cost after. When a charge is uncertain (a timed-out call may still bill), stop the run; client retries are off (failures.md), since they spend money nobody reserved.
- **Meter spend from per-attempt usage, not top-level totals.** One call can bill several attempts (a refusal plus its fallback, or a compaction pass whose top-level usage reads zero). Parallel tool calls share one response id, so dedupe by it, and don't trust per-step output counts. SDK-reported cost is an estimate from a bundled price table: reconcile with the provider's usage API before charging anyone or enforcing a money limit.
- **Cap each customer's usage per day, week, or month, with a hard stop or a manual review above it.** Give the customer-facing agent its own project and spend limit, because a project's hard spend limit stops all traffic in that project.

## Where the answer depends on the case

- **Does a slower reply hurt?** Fin measured no drop in resolution for delays up to 20 seconds in web chat (2025-04). Rappi, newer and on WhatsApp, cut turns because waiting hurt (2026-09). Decide by channel, and measure it.
