# Simulate customers and replay real traffic

## Pick the method

```
Testing one hard turn of a real conversation? → replay its prefix
Agent live, and you need a new version's rates on real traffic? → forecast by replay
Must runs be comparable across versions? (CI, regression)
├── Yes → scripted follow-ups, written before the run, each plausible whatever the agent says
└── No → adaptive simulated user with a persona
    (capability tests, cases where the customer must act in the app, exploration)
```

Check every simulated or replayed batch for evaluation awareness (testing.md) before comparing versions on it.

## Replay real conversations

- **Replay real prefixes first.** For a multi-turn case, take the first N-1 turns of a real ticket and let the agent write only turn N. It tests the hard turn with real wording and no simulator drift. Use a simulated customer only when the agent's earlier turns must be allowed to vary. Prefixes are production data, so the retention rules in support-checks.md apply.
- **A one-turn replay is sound only when the prefix is mostly the customer's words.** On chat traffic, OpenAI found regenerating the last turn as good as simulating several. When most of the prefix is another model's long run of actions, Anthropic found the new model's one turn from inside it unreliable: confirm with multi-turn runs from scratch. Seed simulations with real sessions sparingly, since a transcript one model wrote is off-distribution for the next.
- **Forecast a new version's rates from live traffic.** Take recent real conversations, regenerate only the last agent turn with the candidate, and grade it with your validated judges. Replay the production version first: it must reproduce its known rates, and any gap is replay error, not a model difference. Write the predictions down before release and compare them with production afterward. OpenAI's median error was 1.5x and its tail errors about 10x, and the most recent prefixes cut the error.
- **A replay forecast can't see rare behaviors.** On about 1.3M conversations it missed anything rarer than about 1 in 200,000 messages, so tail risks still need targeted cases and red teaming (red-team.md).
- **Simulate tools in replays, never calling live systems.** A model gets the original rollout, a snapshot of the data at the time, recorded tool calls with their responses, and read-only connectors. Tool fidelity was the largest source of replay error. CI keeps the stateful sandbox with real writes (testing.md).
- **Test the replay's realism with a discriminator** that tries to tell simulated rollouts from real ones. With those simulator inputs, OpenAI's simulated rollouts went from fooling it 11.6% of the time to 49.5%, where 50% means it can't tell.

## Build the simulated customer

- **Pin the simulator with the eval.** Its model and prompt go in the frozen config, and changing either starts a new baseline. With the agent fixed, swapping only the simulator model moved one retail benchmark's success from 67.0 to 75.9.
- **Read a simulator framework's default prompt before using it.** One widely used default told the simulated user to coach the agent ("It looks like you skipped a step") and leaked its reasoning. Its realism scored 1.5 to 2.0 of 5 against 4.4 to 4.7, and porting a better prompt into the same harness closed 96% to 99% of the gap. A simulator that corrects the agent hides its failures.
- **Make it behave like real customers.** Make it write in fragments, leave out context, repeat itself, and give it the goals real customers bring: a refund, a human, distrust of the bot. Vary language, patience, how much they withhold, whether they start logged in, and whether they correct the agent's mistakes or retry after an error.
- **Build it from real conversations, not a longer prompt.** Retrieve similar real customer conversations as in-context examples on each turn, or fine-tune on transcripts. A persona prompt written from measured gaps moved some behaviors closer to humans and others further away, and lowered a fidelity index from 70.9 to 64.6.

## Calibrate it before trusting it

- **Compare pass rates with real customers, per bin.** Run the frozen judges on simulated conversations and on a random sample of real ones for the same intents. If the real pass rate falls below the simulated rate's 95% interval, the simulated customer is too easy. Compare per difficulty bin and per customer population (language, dialect, age), never only the aggregate: real users succeeded 30.8% on tasks a simulator rated 0% and 39.0% on tasks it rated 60%, so the errors cancel in the average.
- **Compare how they talk.** For the same intents, measure the share of customer turns that are 3 words or fewer, polite, uncertain, a change of strategy, frustrated, or phrased like an agent, in simulated and real conversations. GPT-4o as the customer wrote 1.0% short turns against 29.0% for humans, and 49.0% polite turns against 15.3%. Re-measure after every simulator change.
- **Never estimate abandonment from simulated customers.** They don't walk away: simulated non-buyers expressed resistance 13.5% of the time against 25.1% for real ones, and telling the simulator it may disengage left that gap almost unchanged.
- **Point it at a deliberately degraded copy of the agent.** Real customers facing a bad agent get frustrated, ask more clarifying questions, and reject more. A simulator that stays polite and patient will hide the same failures in your agent. In Google's test, simulators built from real conversations reacted like humans to an unseen bad agent, and a prompted one didn't.
- **Score the simulator on behavior and style separately.** Score an explicit no-coaching check (it never tells the agent how to do its job) apart from on-topic, consistency, responsiveness to the last agent turn, persona fidelity, prose realism, and cohort diversity. Compare two simulators by swapping one component at a time, with at least 100 conversations per condition: an apparent catastrophic failure at 10 was noise at 100.

## Grade simulated runs

- **Grade the simulator before the agent.** Check each simulated turn against the case's plan and persona, and discard a run where the simulator broke them. Otherwise its mistakes count as the agent's.
- **The simulator stopping isn't the agent succeeding.** Grade every simulated session with the same state checks and judges as scripted ones. Record "hit the turn cap" and "simulator sent no message" as their own outcomes, never as success: one vendor's default treats an empty simulator turn as goal completion. Set the cap above the longest legitimate conversation (vendor defaults run from 5 to 20 turns) and count cap hits.
