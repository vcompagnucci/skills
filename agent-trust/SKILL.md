---
name: agent-trust
description: Lauren Tan's (poteto) method for trusting an AI agent's work enough to leave it alone, for any agent (coding, customer support, ops). Use when an agent repeats a mistake or you're deciding where a rule or fix should live (system design, tool limits, validators, evals, prompt or human review), giving an agent a way to prove its work, choosing what counts as proof, deciding how much an agent may do without approval, or reviewing an agent's output at volume.
---

# Agent trust

How Lauren Tan (@poteto, pstack's author) builds enough trust in AI agents to leave them alone. She said all of it about coding agents, in public, between April and November 2026. This skill states each principle for **any agent** whose work someone has to trust, with two examples per step: a coding agent and a customer-facing agent (support). The general wording and the support examples apply her method. The coding examples are her own words.

Every claim traces to a dated source in [`references/sources.md`](references/sources.md), and each section names the heading that holds it. Where she changed her mind, the newest position is the one written here. The older one is under "Changed positions". The coding-only specifics (verification CLI, comments, plans, pstack commands) are in [`references/coding-agents.md`](references/coding-agents.md). Read that file when the agent you're trusting writes code.

Her frame is a **trust ladder**. Human attention climbs from watching every run, to approving each result, to **sampling** what already happened. You climb it with two things together: an agent that can **close the loop** by proving its own work, and an environment (code, tools, data, knowledge) built so it steers the agent toward the right move. Sources: "Trust is the bottleneck".

## The procedure

Run it whenever an agent got something wrong, or you want an agent to do more with less watching.

### 1. Close the loop first

Ask: can the agent check its own result in the real system, the way a person would, and hand back an **artifact**? If it can't, build that before anything else. Verification is the limiting step. Every other improvement waits on it, and more agents without it produce unchecked work faster.

- Coding agent: it launches the app, reaches the changed feature and records what happened.
- Support agent: after an action it reads the account back to confirm the change landed, and the reply names the data it relied on. For whoever builds the agent, the loop is a harness that replays real past cases through the agent and grades each result (the `agent-evals` skill covers building one).
- Version the verifier and fix it like code, because everything else rests on it. When it says green and the result is wrong, observe, diagnose and fix the verifier.
- The harder a system is to inspect and control, the worse agents do in it. Give the agent the inspection tools a person would use, or build them.

Sources: "Verification closes the loop", "The verification skill".

**Done when** the agent, with no help from you, can run a real case end to end and hand back evidence of the result.

### 2. Put the fix on the highest rung that holds

A correction typed into one conversation helps one run. Agents copy whatever their environment already shows them, so every repeated mistake becomes a constraint in the system or it spreads. Rungs, strongest first:

1. **Design** makes the mistake impossible. One paved path, where the shortest path is the right path. Coding: the architecture or data structure. Support: the tool itself, such as a refund tool that can't exceed the order total, or an action that doesn't exist without a verified identity. A design that needs escape hatches, or the same workaround repeated in many places, means this rung is the one that's wrong.
2. **A hard check** whose error message names the fix. Coding: types, lint, CI. Support: a schema or validator on tool inputs and outputs, a guard that blocks the action and says why. Write the check before cleaning up old cases, because it stops the bleeding.
3. **A test.** Coding: a behavior test, property test or fuzzing. Support: an eval case built from the real failure.
4. **Prose** last (a system-prompt rule, a doc, a skill), because nothing fails when the agent skips it. If a lesson needs judgment and has no structural form, make the instruction prominent and add an example of the failure.

Human review is off this list. A reviewer who must catch the same mistake every time is the problem this step removes. A class of mistake counts once it has happened twice.

Sources: "Where a fix goes", "The codebase is memory".

**Done when** each mistake class names the rung that now enforces it, or why every higher rung failed, and the new check has been seen failing on a real past instance of the mistake.

### 3. Prove the work, every time

Ask for proof. "Done" and "it ran without errors" are reports. Work is verified once the result happened in the real system and was right.

- State the finish condition up front, as a check that can pass or fail.
- Match the proof to the work. Coding: the real command's output, a recording of the flow, before and after profiles. Support: the tool call and its result, the account state read back, the policy the reply applied.
- The output carries its evidence and says "inconclusive" when a check couldn't run. A confident answer without evidence is a warning sign. For a support agent, inconclusive means hand off to a person.
- A different agent from the author judges the work, either grading offline in the replay harness or checking live before the result ships. Several judges help where one would miss things.
- For a costly promise tests rarely reach (two retries overlapping, events arriving out of order), model it formally: one property, seen failing on a broken variant first. A pass covers the model, and the real system still needs its own proof.

Sources: "What counts as proof", "Formal verification".

**Done when** every result in the batch has an artifact someone could challenge without replaying the run.

### 4. Raise autonomy only when it is earned

A loop you don't trust compounds bad work. Let an agent act alone only after all four hold:

- Someone did the task by hand, or watched the agent do it, so you know what good looks like.
- The agent has the tools and signals a person would use.
- Every stage proves its work and can **stop the line** when the work misses the bar. Coding: triage finds expected behavior, the fix is too risky. Support: identity can't be confirmed, the request is outside policy, the action can't be undone.
- You read transcripts and turned repeated failures into tools, checks or eval cases.

Then hand it the work with a brief that names the goal, a finish condition that can pass or fail (a time limit doesn't count), its permissions and an escape hatch. Long runs keep a decision log, and the review reads the part that flags what needs attention.

Sources: "Loops, autonomy and review".

**Done when** the four checks hold and the brief names all four parts. Until then, a person watches or approves each result.

## The gardener's routine

Once an agent works at volume, review becomes **sampling**. You still taste the food, just not every dish.

- Each day, scrutinize a sample of what the agent did, or have another agent scan every result for shortcuts and regressions.
- When the same mistake shows up across runs, fix the environment (step 2) instead of the one run. A one-off needs nothing.
- Revert, correct, add the check. Keep the environment in a state you'd be happy to see copied, because the agent copies it.
- Whether an irreversible action can happen without a person depends on how verifiable the domain is. Where the result verifies, a one-way door becomes a two-way door. Where it doesn't, she has no rule yet, so the human gate stays.

Sources: "Loops, autonomy and review".

## Rules for every case

- **Make the easy thing the right thing.** Agents take the shortest path, so design the system so the shortest path is correct. The most effort goes into design, invariants and boundaries, then hard checks, then prose, and the least into human review. Sources: "Where a fix goes", "Changed positions".
- **The environment is memory.** It's the most durable context an agent reads. In code, the codebase. For support, the knowledge base, macros and past replies it learns from. Workarounds and stale examples spread like a virus, and clean ones spread the same way. Sources: "The codebase is memory".
- **Start with zero rules and skills.** Watch how the agent fails, add a rule or skill only when a failure repeats, and compare runs with and without it. A hard check or a better tool beats a new rule. This covers rules guessed from expected mistakes. Rules a law or a contract imposes (disclosures, identity checks, complaint handling) go in from day one, on the highest rung that holds them. Sources: "Skills and rules".
- **Code for the mechanical, agents for the fuzzy.** Whatever can be done the same way every time (a calculation, a lookup, a format) goes in code someone can rerun. The agent chooses hypotheses, reads evidence and decides when a person is needed. When an agent keeps doing something by hand, have it write the tool it wishes it had. Sources: "Skills and rules".
