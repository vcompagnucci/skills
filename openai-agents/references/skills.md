# Skills

What a skill is, how its description routes it, how a repo's instruction file makes skills mandatory, and which parts belong in scripts. Draws on OpenAI's developer-blog posts on skills in its Agents SDK repos and for GPT-6 Astra, its hosted computer-environment post, and customer results from Glean.

## What a skill is

- **A folder of instructions and resources, run through a shell.** Its name, description and path go into context, the bundle is unpacked into the workspace, and the model explores and runs it step by step with shell commands. It stops the agent rediscovering a repeated workflow on every run. (`computer-env`)
- **Skills are the "how", the shell is the "do", compaction is continuity.** Splitting them avoids "turning your system prompt into a brittle megadoc". (`skills-shell`)
- **Move templates and worked examples out of the system prompt into skills.** They load only when the skill fires and cost nothing otherwise. Glean reported some of its biggest quality and latency gains from this. (`skills-shell`)
- **Skills close the gap between one tool call and a multi-tool workflow.** A Glean Salesforce skill raised eval accuracy from 73% to 85% and cut time to first token 18.1%, through careful routing, negative examples and embedded templates. Customer-reported. (`skills-shell`)
- **Package a workflow once it works.** Instructions, references and scripts, so it isn't retaught. The data agent packaged recurring analyses like weekly reports after usage showed the repetition. Alpic turned lessons it kept rediscovering into a framework plus a skill covering ideation through deployment. (`codex-maxxing`, `data-agent`, `chatgpt-apps-lessons`)
- **Taste can be a skill too.** OpenAI's frontend skill lists defaults, hard rules, named failures to reject, and questions to check the result against. It has the agent write a visual thesis and content plan before any code. (`frontends`)
- **Skills are a shared convention, not tied to one runtime.** Alongside AGENTS.md and MCP, they let agent tooling move between products and UIs. (`devs-2025`)

## The description is routing logic

- **The model decides from name and description alone.** Write it like routing logic: when to use, when not to, outputs and success criteria. "Your skill's description is effectively the model's decision boundary." Vague or overloaded descriptions make triggering unreliable. (`skills-shell`, `eval-skills`)
- **Minimal, and exact about when.** Bad: "Use when working with databases, queries, models, or persistence", which fires on anything database. Good: "Use when adding or changing a migration, or reviewing its rollout." (`astra-skills`)
- **Fix the metadata before adding code.** In the SDK repos, "Run the mandatory verification stack" became "...when changes affect runtime code, tests, or build/test behavior", which says when it applies and that it isn't optional. (`skills-oss`)
- **Adding skills can lower correct triggering at first.** Glean saw routing drop about 20% in targeted evals, then recover after adding "don't call this skill when..." cases and edge cases. This matters most when skills look alike. (`skills-shell`)
- **Too many skills with long descriptions crowd each other out.** Every name and description loads into context. Past a budget the harness truncates descriptions, so the model sees less of each and picks worse. Descriptions also start to contradict or over-trigger. (`astra-skills`)
- **Name the skill when you need determinism.** Model routing is often right, but in a production workflow with a clear contract, "Use the X skill" turns fuzzy routing into a contract. (`skills-shell`)

## Repo-local and mandatory skills

- **Each skill needs a narrow contract, a clear trigger and a concrete output.** The SDK repos run skills for the verification stack, docs audits against code, running examples, release review, implementation strategy before API changes and PR drafts at handoff. Several are report-first: they rank findings and ask before editing. (`skills-oss`)
- **The instruction file makes skills mandatory with short if/then rules, highest value first.** "Before editing runtime or API changes, call implementation-strategy." "If SDK code changed, run verification and don't mark done until it passes." The condition keeps docs-only work light. "The skill encodes the repository's definition of 'verified', and AGENTS.md makes that definition enforceable." (`skills-oss`)
- **The result was a before-and-after, not a controlled test.** With repo instructions, repo-local skills and the same workflows in CI, the two SDK repos merged 457 PRs in three months against 316 in the three months before. (`skills-oss`)
- **Gate skills need a default and evidence.** Release review starts from "safe to release", blocks only on concrete evidence in the diff, and every block comes with an unblock checklist. (`skills-oss`)

## Scripts for mechanics, the model for judgment

- **If the model rediscovers the same shell recipe every time, make it a script.** Scripts run fixed-order commands, collect logs and write rerun files. The model reads source to infer intent, compares the logs with it and judges compatibility risk. (`skills-oss`)
- **Check output against intent, not exit codes.** A runner saves each example's output, then the model reads each example's source, infers the intended flow and compares. It's more accurate than fixed assertions for code that calls real APIs. Automating it first required a non-interactive mode (auto-answered prompts, a skip list, rerun files). (`skills-oss`)

## Keep them lean as models improve

- **Make a multi-workflow skill's root a minimal router.** Reading a skill spends context, pushes toward compaction and injects guidance that may not apply. Point to supporting docs and scripts instead. (`astra-skills`)
- **Recipe-style skills now slow down a model that handles nuance.** Itineraries that helped earlier models hurt now. Shared repo skills also serve teammates on other models, so write for whoever reads them. Ask the new model to audit your skills against these points instead of reviewing by hand. (`astra-skills`)

## Where the posts disagree

- **How much detail belongs inside a skill.** The February post (2026-02-11) credits embedded templates and worked examples for Glean's gains, and the frontend skill (2026-03-20) is built on hard rules and rejects. The Astra post (2026-09-11) says recipe-style guidance written for earlier models now hinders and skill roots should be routers. All three agree on keeping detail out of always-loaded context. What changed is the model reading it. (`skills-shell`, `frontends`, `astra-skills`)

## Key source articles
`skills-oss` · `skills-shell` · `astra-skills` · `computer-env` · `eval-skills` · `frontends`
