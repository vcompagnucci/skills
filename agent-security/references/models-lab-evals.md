# Each lab's evals of its own models

Anthropic and OpenAI measure their own models with their own attackers and harnesses, and they change both between cards. A row compares only with rows from the same table and the same card. Rates here are raw models unless a row says otherwise. What probes, classifiers and auto mode add is in guardrail-layers.md, and how to read any of it is in models.md.

## Shade adaptive attacks in coding (Anthropic)

- **Read Shade as a deliberately permissive attacker.** Gray Swan trains it on the 40 test scenarios against earlier models, then gives it 200 attempts per scenario. Rates count attempts with a valid response and include classifier fallbacks. Anthropic changed attackers twice in 2026 and says results "should not be compared to previous system cards". (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-fable-5-1`, `anthropic-system-card-opus-4-8`)

| Model | ASR (scenarios broken) | Attack budget | Date | Run by |
|---|---|---|---|---|
| Claude Sonnet 5.5, thinking | 3.01% (16/40) | 200 attempts per scenario | 2026-09-28 | Gray Swan Shade, Anthropic card |
| Claude Sonnet 5, thinking / off | 19.47% (36/40) / 40.30% (40/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Fable 5.1, thinking | 51.93% (39/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Opus 5.5, thinking | 54.61% (37/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Opus 5, thinking / off | 88.92% (40/40) / 85.49% (40/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Fable 5, thinking, before Anthropic strengthened the fallback model | 86.87% (40/40) | 200 attempts per scenario | 2026-09-01 | Gray Swan Shade, Anthropic card |

- **Most of the newest models' coding breaks come through the fallback model, not the model itself.** Opus 5.5 answering on its own was compromised 0 of 2,872 times (models.md). Sonnet 5.5 sent 25% of requests to Sonnet 5 after a cyber block, and 12.01% of those were compromised. Sonnet 5.5 itself fell in 4 of 5,901 (2026-09-28). Sonnet 5.5 has the lowest raw rates in the current coding and browser tables, yet trails Opus 5.5 on Gray Swan IPI (3.4% against 1.0% at k=15) because its GUI computer use reaches 12.5%. The safest model depends on your surface. (`anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5-5`)

## Shade adaptive attacks in GUI computer use (Anthropic)

- **Same attacker and budget as in coding, on 14 GUI scenarios, and here a difference of one or two attempts is noise.** Fallbacks matter less here. Of Opus 5.5's requests, 6% went to Opus 4.8, and none of those were compromised (2026-09-22). (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`)

| Model | ASR (scenarios broken) | Attack budget | Date | Run by |
|---|---|---|---|---|
| Claude Opus 5.5, thinking | 0.07% (1/14), 2 of 2,800 attempts | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Fable 5.1, thinking | 0.07% (1/14) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Sonnet 5.5, thinking | 0.07% (1/14) | 200 attempts per scenario | 2026-09-28 | Gray Swan Shade, Anthropic card |
| Claude Opus 5, thinking / off | 0.29% (1/14) / 3.25% (4/14) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Sonnet 5, thinking / off | 2.25% (4/14) / 4.86% (7/14) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |

- **A screen-driving agent on an older or non-thinking model needs a human or a deterministic check before credentials or payments.** At these rates a few attempts are noise, but the gap to non-thinking and older configurations is not. (`anthropic-system-card-opus-5-5`)

## Browser use against professional red-teamers (Anthropic)

- **Never merge rows across environment sets or harnesses.** Attacks were adaptively sourced against Opus 4.7 and transferred, with 10 attempts per environment. They ran in the Claude Cowork product harness with thinking on and injection probes switched off for the test. Anthropic re-ran every model after finding a harness mismatch (2026-08-19), then re-ran Fable 5.1, Opus 5 and Sonnet 5 on an updated harness for the Opus 5.5 card (2026-09-22). With auto mode, every model fell to 0% except Fable 5 at 0.09% (1/110), a single attack executed after a fallback to Opus 4.8 (2026-09-01). (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5`, `anthropic-system-card-fable-5-1`)

| Model | ASR, attempts (scenarios broken) | Attack budget | Date | Run by |
|---|---|---|---|---|
| Claude Sonnet 5.5 | 0% (0/110) | 110 environments x 10, high effort | 2026-09-28 | Anthropic red team |
| Claude Opus 5.5 | 0.09% (1/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Sonnet 5 | 0.37% (3/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Fable 5.1 | 2.55% (6/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Opus 5 | 3.64% (15/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Fable 5 | 6.04% (18/110) | 110 environments x 10, high effort, earlier harness | 2026-09-01 | Anthropic red team |
| Claude Mythos 5 | 7.80% (29/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |
| Claude Opus 4.8 | 11.15% (26/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |

- **A safeguarded result holds only against the attack set it was measured on.** Opus 4.5's widely quoted 1% in browser use held only with its launch safeguards on (2026-02-05). On Anthropic's current browser attack set, attacks on Opus 4.5 running with probes succeeded 16.7% of the time (2026-08-26). (`anthropic-system-card-opus-4-6`, `anthropic-claude-in-chrome-ga`)
- **Claude in Chrome shows the model alone isn't enough even on the newest generation.** With no added safeguards, attacks that reached the model succeeded 17.6% against Opus 4.5 and 3.8% against Opus 5. With probes plus the action classifier, they succeeded 0% against Sonnet 5, Opus 5 and Mythos 5 and 0.3% against Fable 5 (2026-08-26). (`anthropic-claude-in-chrome-ga`)

## Refusals (Anthropic)

- **Never rely on the model refusing a malicious agent task.** Without safeguards, Opus 5.5 refused 81.0% of malicious Claude Code requests, Sonnet 5.5 85.2% and Mythos 5.1 88.5% (2026-09-28). Opus 5.5 refused 79.46% of harmful computer-use tasks against 93.75% for Opus 5. Most of its failures were on surveillance of individuals (2026-09-22). (`anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5-5`)

## OpenAI's evals of its own models

- **Pick the newest family for an agent that reads untrusted content, and still treat the residual as real at volume.** On OpenAI's automated GPT-Red evals, defender success against indirect injection was 99.79% for GPT-6 Astra against 96.23% for GPT-5.6 Sol, averaged per defender query. An agent reading thousands of tickets a day still meets successes. Direct injection (instruction hierarchy) is saturated at 99.99% for Astra and GPT-6.1 Sol and 99.97% for GPT-6 Luna (2026-09-29). OpenAI retired its Connectors and Search-and-Function-Calling evals as saturated (2026-09-03). (`openai-gpt-6-astra-system-card`, `openai-gpt-6-1-sol-system-card`)
- **Treat vendor injection scores as upper bounds.** OpenAI's connector and function-calling evals were "splits of the data we used for training, so don't represent a model's ability to generalize to new attacks" (2025-12-11). (`openai-gpt-5-2-system-card`)
- **A confirmation policy the model follows doesn't stop leaks.** In adversarial workplace tasks GPT-6 Astra with the policy still produced misaligned outcomes in 3.0% (unauthorized transactions 4.3%, data exfiltration 4.5%), against 3.4%, 6.8% and 4.3% without it (2026-09-03). (`openai-gpt-6-astra-system-card`)
- **The target behavior for an agent reading inbound mail is flag, withhold and ask.** OpenAI flooded its dots agents with 16,600 GPT-Red attack emails over 100 rollouts of 500 emails and 2,638 iterative attempts. The attacks produced no scored successes (appendix added 2026-09-29). In the traces OpenAI inspected, dots "commonly flagged suspicious requests for further review, then withheld risky actions and notified or asked the user". (`openai-gpt-6-astra-system-card`)
- **Read static jailbreak refusals as resistance to one prompt set, not as injection resistance or production behavior.** With production classifiers off, Astra refused 0.973 of high-risk bio, 0.947 of moderate violence and 0.915 of cyber attacks, against 0.0580, 0.216 and 0.590 for GPT-5.6 Sol (2026-09-03). GPT-6.1 Sol and GPT-6 Luna refused 93.8% and 73.8% of high-risk bio. Some of Luna's higher scores reflect "a broader tendency to refuse requests, including legitimate ones" (2026-09-29). OpenAI says the prompts were "designed to jailbreak earlier models" and are "not representative of performance on real production traffic". (`openai-gpt-6-astra-system-card`, `openai-gpt-6-1-sol-system-card`)
- **Prefer models trained on instruction-hierarchy conflicts, and put your policy in the system or developer message.** Training took GPT-5-Mini from 0.44 to 1.00 on an internal injection benchmark, unsafe behavior with a safety policy from 6.6% to 0.7%, and adaptive human red-team robustness from 63.8% to 88.2% (2026-03-10). (`openai-ih-challenge-paper`)

Key sources: `anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-4-8`, `anthropic-system-card-opus-5`, `anthropic-system-card-fable-5-1`, `openai-gpt-6-astra-system-card`, `openai-gpt-6-1-sol-system-card`, `anthropic-claude-in-chrome-ga`
