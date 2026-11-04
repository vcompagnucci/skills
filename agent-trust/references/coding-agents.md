# Coding agents: the specifics

What Lauren Tan says that only applies when the agent writes code. The general method is in [`../SKILL.md`](../SKILL.md). Her pstack plugin holds the procedures as `/pstack:<name>` commands. Use them when they're installed. Without them, the descriptions here are enough to do the same by hand.

## Contents

- The verification skill
- Proof by type of change
- Comments and plans
- pstack commands by step

## The verification skill

How a coding agent closes the loop (step 1). Sources: "The verification skill".

- A small CLI inside the skill that launches, drives and debugs the app (CDP, a simulator, a PTY or HTTP), plus a feature map listing every feature and how a user reaches it.
- Commit it and keep it current daily. When it says green and the product is wrong, observe, diagnose and fix the skill.
- `/pstack:create-verification-skill` builds one. `/pstack:maintain-verification-skill` keeps it current.

## Proof by type of change

Step 3 applied to code. Sources: "What counts as proof".

- A CLI runs the real command. A UI walks the flow in the running app and records video or screenshots. A parser replays saved input. Storage reads back the written value.
- Perf compares before and after profiles. Vet the number before reporting it (`/pstack:benchmark-checklist`).
- A bug shows the failing test, then the passing one, and after merge the same check on main.
- "It compiles" and a green build prove it compiles. Tests alone are not verification.
- Prefer tests of observable behavior: property-based tests, fuzzing, expect tests that print behavior.

## Comments and plans

Sources: "Comments, plans and other prose".

- A reviewer who didn't write the comments deletes almost all of them (`/pstack:no-comments`). Keep license headers, doc comments on a public API, links that explain what code can't, and behavior forced by a dependency you can't reshape.
- A surprise in your own code becomes a refactor. A comment claiming a constraint becomes a type, test or lint.
- Delete plans when the work lands. Keep ADRs out of the repo unless they help agents decide.

## pstack commands by step

| Step | Command |
| --- | --- |
| 1. Close the loop | `create-verification-skill`, `maintain-verification-skill` |
| 2. Highest rung | `correct` (runs the whole step across a repo's history) |
| 3. Prove the work | `benchmark-checklist`, `create-formal-verification-skill` |
| 4. Autonomy | `show-me-your-work` (the decision log; read its Attention section in the morning) |
| Rules | `no-comments` |
