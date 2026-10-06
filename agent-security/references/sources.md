# Sources

312 sources read in full on 2026-10-06: 97 from Anthropic (docs, engineering and research posts, the constitution, system cards from Opus 4.5 to Opus 5.5 and Sonnet 5.5, threat reports), 72 from OpenAI (docs, the Model Spec, the Guardrails library, the Agents SDK, cookbooks, system cards from Operator to GPT-6.1 Sol), 25 from Cognition (Devin and Windsurf docs, blog posts, release notes) and 118 from labs, standards bodies, support vendors, security researchers and incident reports, dated 2023-02-23 to 2026-10-05. Every one is listed by slug in `article-index.md`.

## How the claims were chosen

- Three research passes extracted 645 findings, one actionable claim each, with its source, date and numbers. A fourth pass on Cognition added 26.
- JEV (TypeSafe, jev-1.13.0) scored each for scope and for the harm of not knowing it, then compared each with the claims already accepted for the same reference and with agent-harness and agent-evals, in priority order: Anthropic and OpenAI first, newest first. A claim that repeated an accepted one or a sibling skill stayed out. 580 entered, 12 fell outside the scope and 53 were repeats. I reviewed the borderline cases and every contradiction by hand. All 26 Cognition findings passed, compared against the published references.
- Editors folded all accepted findings into the references without dropping any. Where sources disagreed, the newest position won. When dates didn't settle it, Anthropic and OpenAI won. Real ties and measurements that disagree sit under "Where the answer depends on the case" in conversation.md, guardrail-layers.md and models.md.
- An audit on 2026-10-06 removed or updated every claim a newer source superseded: retired benchmarks, old-model figures where 2026 measurements exist, product facts that changed. The change log lives with the corpus.
- Numbers are copied from the source with the model, benchmark, attack budget, date and who ran it, never computed or rounded. Vendor numbers about their own models are labeled as such.

## Watched for changes

The updater checks these on the 1st and 15th of each month and opens a PR when something changes the advice.

| Source | Last checked |
|---|---|
| OpenAI Model Spec (`openai/model_spec`) | `7f1cf79fcb65` |
| OpenAI Guardrails (`openai/openai-guardrails-python`) | `4e3f3717017c` |
| AgentDojo (`ethz-spylab/agentdojo`) | `089ed468cf3e` |
| Simon Willison, prompt-injection tag | 2026-10-06 |
| Embrace The Red (Johann Rehberger) | 2026-10-06 |
| OpenAI news, security and safety posts | 2026-10-06 |
| Anthropic news, research and engineering, security posts | 2026-10-06 |
| Cognition blog (Devin, Windsurf) | 2026-10-06 |

## Use of the sources

Ideas are restated in my own words, and quotes stay under 25 words with their slug. The raw text and the per-source notes live outside this repo, in the corpus the updater reads.
