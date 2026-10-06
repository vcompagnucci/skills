# Each lab's evals of its own models

Anthropic and OpenAI measure their own models with their own attackers and harnesses, and change both between cards, so a row compares only with rows from the same table and the same card. Rates here are raw models unless a row says otherwise; what probes, classifiers and auto mode add is in guardrail-layers.md, and how to read any of it is in models.md.

## Shade adaptive attacks in coding (Anthropic)

- **Read Shade as a deliberately permissive attacker.** Gray Swan trains it on the 40 test scenarios against earlier models, then gives it 200 attempts per scenario; rates count attempts with a valid response and include classifier fallbacks. Anthropic changed attackers twice in 2026 and says results "should not be compared to previous system cards". (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-fable-5-1`, `anthropic-system-card-opus-4-8`)

| Model | ASR (scenarios broken) | Attack budget | Date | Run by |
|---|---|---|---|---|
| Claude Sonnet 5.5, thinking | 3.01% (16/40) | 200 attempts per scenario | 2026-09-28 | Gray Swan Shade, Anthropic card |
| Claude Sonnet 5, thinking / off | 19.47% (36/40) / 40.30% (40/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Fable 5.1, thinking | 51.93% (39/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Opus 5.5, thinking | 54.61% (37/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Opus 5, thinking / off | 88.92% (40/40) / 85.49% (40/40) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Fable 5, thinking, before Anthropic strengthened the fallback model | 86.87% (40/40) | 200 attempts per scenario | 2026-09-01 | Gray Swan Shade, Anthropic card |

- **Most of the newest models' coding breaks come through the fallback model, not the model itself.** Opus 5.5 answering on its own was compromised 0 of 2,872 times (models.md), and Sonnet 5.5 sent 25% of requests to Sonnet 5 after a cyber block, 12.01% of those were compromised, and Sonnet 5.5 itself fell in 4 of 5,901 (2026-09-28). Sonnet 5.5 has the lowest raw rates in the current coding and browser tables, yet trails Opus 5.5 on Gray Swan IPI (3.4% against 1.0% at k=15) because its GUI computer use reaches 12.5%: the safest model depends on your surface. (`anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5-5`)
- **On the April to June 2026 attacker, a newer generation cut first-attempt success sharply.** First attempt and 200 attempts with thinking: Opus 4.6 25.92% and 97.5% of scenarios, Opus 4.7 2.34% and 60.0%, Opus 4.8 7.03% and 57.5%, Sonnet 4.6 12.71% and 90.0%, Mythos Preview 0.0% and 0.0% (2026-04-16, 2026-06-17); the 5% to 6% Opus 4.7 figure some sources quote is ART, a static benchmark, not this adaptive one. Old models stay in production long after they stop being the best, so re-check yours. (`anthropic-system-card-opus-4-7`, `anthropic-system-card-opus-4-8`)
- **In late 2025 the model tier changed injection risk by an order of magnitude.** On the original attacker, Opus 4.5 with extended thinking fell on 0.3% of first attempts and 10.0% of scenarios within 200, against 17.7% and 70.0% for Sonnet 4.5 (2025-11-24); a cheaper model on untrusted repos or tickets needed more containment. (`anthropic-system-card-opus-4-5`)

## Shade adaptive attacks in GUI computer use (Anthropic)

- **Same attacker and budget as in coding, on 14 GUI scenarios, and here a difference of one or two attempts is noise.** Fallbacks matter less: 6% of Opus 5.5's requests went to Opus 4.8 and none of those were compromised (2026-09-22). (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`)

| Model | ASR (scenarios broken) | Attack budget | Date | Run by |
|---|---|---|---|---|
| Claude Opus 5.5, thinking | 0.07% (1/14), 2 of 2,800 attempts | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Fable 5.1, thinking | 0.07% (1/14) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Sonnet 5.5, thinking | 0.07% (1/14) | 200 attempts per scenario | 2026-09-28 | Gray Swan Shade, Anthropic card |
| Claude Opus 5, thinking / off | 0.29% (1/14) / 3.25% (4/14) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |
| Claude Sonnet 5, thinking / off | 2.25% (4/14) / 4.86% (7/14) | 200 attempts per scenario | 2026-09-22 | Gray Swan Shade, Anthropic card |

- **A screen-driving agent on an older or non-thinking model needs a human or a deterministic check before credentials or payments.** At these rates a few attempts are noise, but the gap to non-thinking and older configurations is not: on February 2026's stronger attacker, Sonnet 4.6 fell in 42.9% and Opus 4.6 in 78.6% of scenarios within 200 attempts with extended thinking, while both were near 0% in coding (2026-02-17). (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-4-6`)

## Browser use against professional red-teamers (Anthropic)

- **Never merge rows across environment sets or harnesses.** Attacks were adaptively sourced against Opus 4.7 and transferred, with 10 attempts per environment, run in the Claude Cowork product harness with thinking on and injection probes switched off for the test; Anthropic re-ran every model after finding a harness mismatch (2026-08-19). With auto mode, every model in the 129-environment run fell to 0% except Fable 5 at 0.25% (3/129, three low-severity breaks). (`anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5`)

| Model | ASR, attempts (scenarios broken) | Attack budget | Date | Run by |
|---|---|---|---|---|
| Claude Sonnet 5.5 | 0% (0/110) | 110 environments x 10, high effort | 2026-09-28 | Anthropic red team |
| Claude Opus 5.5 | 0.09% (1/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Sonnet 5 | 0.37% (3/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Fable 5.1 | 2.55% (6/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Opus 5 | 3.64% (15/110) | 110 environments x 10, high effort | 2026-09-22 | Anthropic red team |
| Claude Sonnet 5 | 0.47% (5/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |
| Claude Opus 5 | 3.84% (11/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |
| Claude Mythos 5 | 7.80% (29/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |
| Claude Opus 4.8 | 11.15% (26/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |
| Claude Fable 5 | 14.75% (43/129) | 129 environments x 10, medium effort | 2026-08-19 | Anthropic red team |

- **An older model behind the provider's safeguards can stay badly exposed.** With deployed safeguards, Sonnet 4.6 was still broken in 46.5% of scenarios (23.6% of attempts) against 3.9% (0.5%) for Opus 4.8 (129 environments x 10, 2026-06-17); safeguards cut rates in proportion and don't lift a weak model to a strong one. (`anthropic-system-card-opus-4-8`)
- **The widely quoted 1% for Opus 4.5 in browser use held only with safeguards on.** Its card measured 100 adaptive attempts per environment and gave per-model rates only in a figure (2025-11-24). Re-measured on 389 scenarios x 10 Best-of-N strings, raw Opus 4.5 fell in 16.20% of scenarios (5.06% of attempts) at standard thinking and 18.77% (6.40%) at extended, and with its launch safeguards in 1.03% (0.21%) at standard thinking; raw Opus 4.6 with extended thinking was 2.06% (0.29%) and Sonnet 4.5 54.24% (20.45%) (2026-02-05). (`anthropic-system-card-opus-4-5`, `anthropic-system-card-opus-4-6`)
- **A safeguarded result holds only against the attack set it was measured on.** On Anthropic's current browser attack set, attacks on Opus 4.5 running with probes succeeded 16.7% of the time (2026-08-26). (`anthropic-claude-in-chrome-ga`)
- **Claude in Chrome shows the model alone isn't enough even on the newest generation.** Attacks that reached the model succeeded 17.6% against Opus 4.5 and 3.8% against Opus 5 with no added safeguards, and 0% against Sonnet 5, Opus 5 and Mythos 5 and 0.3% against Fable 5 with probes plus the action classifier (2026-08-26); the 2025 pilot measured 23.6% raw and 11.2% with mitigations on 123 cases over 29 scenarios, and 35.7% to 0% on four browser-specific attacks (2025-08-25). (`anthropic-claude-in-chrome-ga`, `anthropic-claude-in-chrome-pilot`)

## Static benchmarks and refusals (Anthropic)

- **On ART, a single attempt sits at the floor and the 100-attempt number separates models.** k=1 was 0.1% for Mythos 5, Mythos Preview and Opus 4.8 alike, and k=100 with extended thinking 4.8%, 6.1% and 9.6% (2026-06-09); Opus 4.7 was 6.0% without thinking and 4.8% with adaptive thinking against 14.8% and 21.7% for Opus 4.6 (2026-04-16). k counts draws from a fixed transferable pool, and Anthropic says Claude models have saturated ART. (`anthropic-system-card-fable-5`, `anthropic-system-card-opus-4-7`)
- **Give MCP-connected agents least-privilege tools and confirmation on writes.** With no classifiers, models stayed on task against injected email, Slack and document MCP servers in 92.5% (Haiku 4.5), 92.0% (Sonnet 4.5), 91.1% (Sonnet 4) and 95.5% (Haiku 3.5) of cases, and in bash tool use 93.4%, 96.0%, 90.6% and 91.6% (2025-10-15). In computer use the classifier mattered most for the small model: Haiku 4.5 resisted 72.2% alone and 92.4% with it, Sonnet 4.5 78.0% and 82.6%. (`anthropic-system-card-haiku-4-5`)
- **Never rely on the model refusing a malicious agent task.** Without safeguards Opus 5.5 refused 81.0% of malicious Claude Code requests (79.8% in its own card a week earlier), Sonnet 5.5 85.2% and Mythos 5.1 88.5% (2026-09-28), and Opus 5.5 refused 79.46% of harmful computer-use tasks against 93.75% for Opus 5, mostly failing on surveillance of individuals (2026-09-22). (`anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-5-5`)

## OpenAI's evals of its own models

- **Pick the newest family for an agent that reads untrusted content, and still treat the residual as real at volume.** On OpenAI's automated GPT-Red evals, defender success against indirect injection was 99.79% for GPT-6 Astra against 96.23% for GPT-5.6 Sol, averaged per defender query, so an agent reading thousands of tickets a day still meets successes; direct injection (instruction hierarchy) is saturated at 99.99% for Astra (2026-09-03) and 99.97% for GPT-6 Sol and Luna (appendix added 2026-09-22), and OpenAI retired its Connectors and Search-and-Function-Calling evals as saturated. (`openai-gpt-6-astra-system-card`)
- **Treat vendor injection scores as upper bounds.** OpenAI's connector and function-calling evals are "splits of the data we used for training, so don't represent a model's ability to generalize to new attacks" (2025-12-11); on the harder Search and Function-Calling set, GPT-5.1 Thinking scored 0.423, GPT-5.4 Thinking 0.697, GPT-5.6 Sol 0.910, Terra 0.946 and Luna 0.897, while connector scores were 0.998 to 1.000 from GPT-5.4 Thinking on, against 0.649 for GPT-5.1 Thinking and 0.971 for GPT-5.2 Thinking (2026-06-26). (`openai-gpt-5-2-system-card`, `openai-gpt-5-6-system-card`)
- **Budget for the injections that get past training.** gpt-5-codex and codex-1 ignored OpenAI's Codex injection attacks (end the task, or answer "HACKED!") 0.98 of the time (2025-09-15), and OpenAI pairs them with sandboxing and network off by default. (`openai-gpt-5-codex-system-card`)
- **Models resist redirection far better than exfiltration.** ChatGPT agent disregarded irrelevant injected instructions in 95% of visual-browser cases (99.5% on a text-browser set that also counts exfiltration attempts), but resisted in-context exfiltration in 78% and active exfiltration in 67%, against 75% and 58% for Operator 4o, and Operator o3 beat it on both exfiltration rows (80% and 75%) (2025-07-17); design egress checks as if the model fails one in three. (`openai-chatgpt-agent-system-card`)
- **Never put secrets or a password gate in the prompt.** gpt-5-main resisted realistic system-prompt extraction 0.885 of the time against 0.990 for gpt-5-thinking, and protected an "access granted" phrase 0.619 against a malicious user and 0.404 against a malicious developer message, against 0.940 and 0.911 (2025-08-07). (`openai-gpt-5-system-card`)
- **A confirmation policy the model follows doesn't stop leaks.** In adversarial workplace tasks GPT-6 Astra with the policy still produced misaligned outcomes in 3.0% (unauthorized transactions 4.3%, data exfiltration 4.5%), against 3.4%, 6.8% and 4.3% without it (2026-09-03). (`openai-gpt-6-astra-system-card`)
- **The target behavior for an agent reading inbound mail is flag, withhold and ask.** OpenAI's dots agents, flooded with 16,600 GPT-Red attack emails over 100 rollouts of 500 emails and 2,638 iterative attempts, produced no scored successes (appendix added 2026-09-29). (`openai-gpt-6-astra-system-card`)
- **Read static jailbreak refusals as resistance to one prompt set, not as injection resistance or production behavior.** With production classifiers off, Astra refused 0.973 of high-risk bio, 0.947 of moderate violence and 0.915 of cyber attacks, against 0.0580, 0.216 and 0.590 for GPT-5.6 Sol (2026-09-03), and GPT-6 Sol and Luna refused 85.8% and 73.8% of high-risk bio, with some of Luna's higher scores reflecting "a broader tendency to refuse requests, including legitimate ones" (appendix added 2026-09-22). OpenAI says the prompts were "designed to jailbreak earlier models" and are "not representative of performance on real production traffic". (`openai-gpt-6-astra-system-card`)
- **Prefer models trained on instruction-hierarchy conflicts, and put your policy in the system or developer message.** Training took GPT-5-Mini from 0.44 to 1.00 on an internal injection benchmark, unsafe behavior with a safety policy from 6.6% to 0.7%, and adaptive human red-team robustness from 63.8% to 88.2% (2026-03-10). A hierarchy paragraph in the prompt alone left GPT-3.5 Turbo flat or worse in 2024 (TensorTrust hijacking 59.2 baseline, 55.5 with the prompt, 79.2 trained), and on the trained model it cost User Conflicting robustness (92.6 to 72.0). (`openai-ih-challenge-paper`, `openai-instruction-hierarchy-2024`)

Key sources: `anthropic-system-card-opus-5-5`, `anthropic-system-card-sonnet-5-5`, `anthropic-system-card-opus-4-8`, `anthropic-system-card-opus-4-7`, `anthropic-system-card-opus-5`, `anthropic-system-card-opus-4-6`, `openai-gpt-6-astra-system-card`, `openai-gpt-5-6-system-card`, `anthropic-claude-in-chrome-ga`
