# Cross-vendor numbers that vendors publish

These are head-to-heads that a vendor ran or published, with competitors in the same chart. The vendor chose the attack set, its own configuration and the field, so use them to shortlist and never to crown; read models.md first.

## Gray Swan IPI, as three vendors publish it

- **Compare rows only inside one publisher's block.** Gray Swan builds the benchmark from its competitions and runs it, and k counts draws from a fixed pool of attacks selected for transfer, not an attacker adapting to the model. (`anthropic-system-card-opus-5-5`)
- **Each publisher ran a different configuration.** Anthropic used 1,804 attacks over 37 scenarios (Q1+Q2 2026, Claude with extended thinking, blocking classifiers and fallbacks but no injection safeguards) or 1,130 over 28 (Q1, Claude "without additional safeguards"), other models on their public endpoints, competition targets left out. OpenAI used 1,810 attacks on Astra's "safeguards-enabled checkpoint". (`anthropic-system-card-opus-5-5`, `anthropic-system-card-fable-5-1`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5`, `openai-gpt-6-astra-system-card`)
- **Treat the Google block as a chart of mixed origin.** It is BenchmarkList's transcription of two Google launch posts: Google's own models are marked self-reported and every other row "Imported", the set is labeled "Combined Attack Set, Transfer Only, No Computer Use" and no budget is stated, yet several imported values equal the vendors' own overall k=15 figures (Opus 5.5 at 1.0%, which in Anthropic's card includes computer use; Astra 8.5% and GPT-5.6 Sol 27.0% from OpenAI's card), so the configuration behind each row is unclear. (`benchmarklist-grayswan-ipi`, `anthropic-system-card-opus-5-5`, `openai-gpt-6-astra-system-card`)

| Model | ASR | Attack budget | Date | Published by |
|---|---|---|---|---|
| Claude Opus 5.5 | 0.1%, 0.7%, 1.0% | k=1, 10, 15; Q1+Q2 set | 2026-09-22 | Anthropic |
| Claude Fable 5.1 | 0.1%, 0.7%, 1.0% | k=1, 10, 15; Q1+Q2 set | 2026-09-01 | Anthropic |
| Claude Sonnet 5.5 | 0.4%, 2.7%, 3.4% | k=1, 10, 15; Q1+Q2 set | 2026-09-28 | Anthropic |
| Claude Opus 5 | 0.4%, 3.6%, 4.8% | k=1, 10, 15; Q1+Q2 set | 2026-09-22 | Anthropic |
| Claude Fable 5 | 0.6%, 4.9%, 6.5% | k=1, 10, 15; Q1+Q2 set | 2026-09-01 | Anthropic |
| Claude Sonnet 5 | 0.7%, 5.1%, 6.7% | k=1, 10, 15; Q1+Q2 set | 2026-09-28 | Anthropic |
| Gemini 3.8 Flash | 5.5% | k=15; Q1+Q2 set | 2026-09-28 | Anthropic |
| Gemini 3.7 Flash | 9.2% | k=15; Q1+Q2 set | 2026-09-01 | Anthropic |
| Most other frontier models | 24% to 53% | k=15; Q1+Q2 set | 2026-09-01 | Anthropic |
| Claude Opus 5 | 0.2%, 2.0% | k=1, 15; Q1 set | 2026-08-19 | Anthropic |
| Claude Mythos 5 | 2.6% | k=15; Q1 set | 2026-08-19 | Anthropic |
| Claude Opus 4.8 | 0.5%, 5.5% | k=1, 15; Q1 set | 2026-08-19 | Anthropic |
| Claude Sonnet 5 | 5.9% | k=15; Q1 set | 2026-08-19 | Anthropic |
| Muse Spark | 16.5% | k=15; Q1 set | 2026-08-19 | Anthropic |
| GPT-5.6 Sol | 3.1%, 20.0% | k=1, 15; Q1 set | 2026-08-19 | Anthropic |
| GPT-5.5 | 20.8% | k=15; Q1 set | 2026-08-19 | Anthropic |
| GPT-5.6 Terra | 30.4% | k=15; Q1 set | 2026-08-19 | Anthropic |
| GPT-5.6 Luna | 43.9% | k=15; Q1 set | 2026-08-19 | Anthropic |
| GPT-6 Astra, safeguards on | 8.5% | 15 attempts per scenario; 1,810 attacks | 2026-09-03 | OpenAI |
| GPT-5.6 Sol | 27.0% | 15 attempts per scenario; 1,810 attacks | 2026-09-03 | OpenAI |
| Gemini 4 Argon | 0.7% | not stated | 2026-09-30 | Google (self-reported) |
| Claude Fable 5.1 | 1.0% | not stated | 2026-09-30 | Google chart (imported) |
| Claude Opus 5.5 | 1.0% | not stated | 2026-09-30 | Google chart (imported) |
| Claude Opus 5 | 4.6% | not stated | 2026-09-30 | Google chart (imported) |
| Gemini 3.8 Flash | 5.5% | not stated | 2026-09-30 | Google (self-reported) |
| Gemini 3.8 Flash Cyber | 6.0% | not stated | 2026-09-30 | Google (self-reported) |
| Claude Fable 5 | 6.5% | not stated | 2026-09-02 | Google chart (imported) |
| Claude Sonnet 5 | 6.7% | not stated | 2026-09-02 | Google chart (imported) |
| Claude Opus 4.8 | 8.0% | not stated | 2026-09-02 | Google chart (imported) |
| GPT-6 Astra | 8.5% | not stated | 2026-09-30 | Google chart (imported) |
| Gemini 3.7 Flash Cyber | 9.2% | not stated | 2026-09-02 | Google chart (imported) |
| GPT-6 Sol | 10.1% | not stated | 2026-09-30 | Google chart (imported) |
| Muse Spark 1.3 | 15.9% | not stated | 2026-09-30 | Google chart (imported) |
| Muse Spark 1.2 | 24.2% | not stated | 2026-09-02 | Google chart (imported) |
| GPT-5.6 Sol | 27.0% | not stated | 2026-09-30 | Google chart (imported) |
| Qwen 3.8 | 28.6% | not stated | 2026-09-02 | Google chart (imported) |
| GLM 5.3 | 31.5% | not stated | 2026-09-30 | Google chart (imported) |
| GPT-5.6 Terra | 37.3% | not stated | 2026-09-02 | Google chart (imported) |
| GPT-5.6 Luna | 50.0% | not stated | 2026-09-02 | Google chart (imported) |
| Grok 4.6 | 51.8% | not stated | 2026-09-30 | Google chart (imported) |
| Kimi K3 | 52.7% | not stated | 2026-09-30 | Google chart (imported) |
| DeepSeek V4 Pro | 60.1% | not stated | 2026-09-02 | Google chart (imported) |

- **The same model gets a different number from each publisher and each attack set.** Opus 5 is 2.0% (Q1, 2026-08-19) and 4.8% (Q1+Q2 with fallbacks, 2026-09-01) in Anthropic's cards and 4.6% in Google's chart; GPT-5.6 Luna is 43.9% and Terra 30.4% in Anthropic's Q1 run against 50.0% and 37.3% in Google's chart, while GPT-5.6 Sol's 27.0% in Google's chart is OpenAI's own figure imported. Google's post says only that Argon "is leading in prompt injection robustness" on this benchmark. (`anthropic-system-card-opus-5`, `anthropic-system-card-fable-5-1`, `openai-gpt-6-astra-system-card`, `benchmarklist-grayswan-ipi`, `google-gemini-4-argon`)

## Live bug bounties hosted with Gray Swan

- **Read these as expert humans attacking models they can't identify, published in Anthropic's cards.** Each red-teamer could submit one success per scenario per model over one week; Claude ran at high effort without product protections (a lower bound for deployed systems) and the others in their production configuration. No Claude model had a successful computer-use attack in the August round. Anthropic counts more than 20,000 attempts against each Claude model and gives no count for the others. (`anthropic-system-card-opus-5`, `anthropic-system-card-sonnet-5`)

| Model | ASR | Attack budget | Date | Published by |
|---|---|---|---|---|
| Claude Fable 5 | 0.04% | >20,000 attempts; 11 scenarios | 2026-08-19 | Anthropic |
| Claude Opus 5 | 0.08% | >20,000 attempts; 11 scenarios | 2026-08-19 | Anthropic |
| Claude Opus 4.8 | 0.11% | >20,000 attempts; 11 scenarios | 2026-08-19 | Anthropic |
| Claude Sonnet 5 | 0.12% | >20,000 attempts; 11 scenarios | 2026-08-19 | Anthropic |
| Kimi K3 | 0.58% | not stated; 11 scenarios | 2026-08-19 | Anthropic |
| GPT-5.6 Sol, high reasoning | 0.61% | not stated; 11 scenarios | 2026-08-19 | Anthropic |
| DeepSeek V4 Flash | 8.09% | not stated; 11 scenarios | 2026-08-19 | Anthropic |
| Claude Sonnet 5 | 0.19% | one week; 11 scenarios | 2026-06-30 | Anthropic |
| Claude Opus 4.8 | 0.19% | one week; 11 scenarios | 2026-06-30 | Anthropic |
| Claude Sonnet 4.6 | 1.41% | one week; 11 scenarios | 2026-06-30 | Anthropic |
| GPT-5.5, high reasoning | 3.08% | one week; 11 scenarios | 2026-06-30 | Anthropic |
| Gemini 3.5 Flash | 6.66% | one week; 11 scenarios | 2026-06-30 | Anthropic |
| Least robust model in the round | 14.29% | one week; 11 scenarios | 2026-06-30 | Anthropic |

Key sources: `anthropic-system-card-opus-5-5`, `anthropic-system-card-fable-5-1`, `anthropic-system-card-opus-5`, `anthropic-system-card-sonnet-5`, `anthropic-system-card-sonnet-5-5`, `openai-gpt-6-astra-system-card`, `benchmarklist-grayswan-ipi`
