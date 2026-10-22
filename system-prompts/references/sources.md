# Sources

329 sources read in full on 2026-10-22: 103 from OpenAI (docs, the Model Spec, cookbooks, prompting guides and the Codex repo), 69 from Anthropic (docs, engineering posts, the constitution and its published app prompts), 43 from other labs (Google, Microsoft, xAI, Meta, Mistral, Cohere, Amazon, DeepSeek, Qwen, Moonshot) and 114 from open-source agents, practitioners, support vendors and research. 48 of them are published system prompts or prompt files, read at a recorded commit: Codex, the Claude apps, Gemini CLI, OpenHands, Cline, OpenCode, goose, Aider, Roo Code, Kilo Code, Grok, Copilot, Zed and others. Dated sources run from 2024-02-14 to 2026-10-21, 148 of them from 2026; 114 are live docs pages without a date. Every one is listed by slug in `article-index.md`.

## How the claims were chosen

- Five research passes extracted 840 findings, one actionable claim each, with its source, date and numbers: Anthropic, OpenAI, open-source agent prompts, the field (other labs, practitioners, support vendors, research), and a pass on gaps (few-shot, voice, language, prompt versioning, support procedures). 56 more were bullets moving here from agent-harness, agent-security, agent-evals and the two vendor skills, which now point to this one.
- JEV (TypeSafe, jev-1.13.0) scored each for scope and for the harm of not knowing it, then compared each with the claims already accepted for the same reference and with agent-harness, agent-security and agent-evals, in priority order: Anthropic and OpenAI first, newest first. 63 fell outside the scope and 73 repeated an accepted claim, so 763 entered. I reviewed the borderline cases by hand and forced 58 in. The ones left out on purpose belong to a sibling: cache order, mid-turn delivery and tool descriptions (agent-harness), testing and A/B rollout (agent-evals), safety filters and permission reviewers (agent-security).
- Editors folded every accepted finding into the references without dropping any, and a coverage table records where each one landed. Where sources disagreed, the newest position won. When dates didn't settle it, Anthropic and OpenAI won. Real ties and measurements that disagree sit under "Where the answer depends on the case" in rule-sets.md, examples.md, structure.md and iterate.md.
- Numbers are copied from the source with the model, task, date and who measured, never computed or rounded. When a source hedges its own figure, the reference says so after it ("OpenAI's rough figure") instead of adding "about". The one exception is the length of a published prompt: those are word or line counts of the file at its recorded commit, and say so. Vendor numbers about their own models are labeled as such.
- Before publishing, a second pass checked every quote and number against the source text: 107 didn't match their cited source and were corrected, re-cited or removed.
- Quoted prompt lines are verbatim, under 25 words, and name whose prompt they come from.

## Watched for changes

On the 1st and 15th of each month an updater checks three kinds of source and opens a PR when a change alters the advice:

- the 48 published prompt files the skill read, Codex first, for a new commit;
- 25 prompting guides and published Claude system prompts from Anthropic, OpenAI and Google, for an edit;
- new prompting pages in Anthropic's, OpenAI's and Google's docs, Anthropic's site, OpenAI's news and developer blog, and Simon Willison's system-prompts tag.

The commit or page state last seen for each one lives with the corpus, outside this repo.

## Use of the sources

Ideas are restated in my own words, and quotes stay under 25 words with their slug. The raw text and the per-source notes live outside this repo, with the corpus.
