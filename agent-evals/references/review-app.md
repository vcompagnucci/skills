# Review app

Build a small local app (Python standard-library server plus one HTML page) before reading traces. Raw JSON and spreadsheets make reviewers miss failures.

- Group traces by session and show each conversation in order, with every tool call and its result in one container next to the reply that relies on it.
- Render natively: markdown as HTML, JSON pretty-printed and collapsible, amounts and ids in bold. Collapse long tool results and repeated boilerplate but never hide them. Mute only content identical across records, never a whole role. Tool results and system messages hold bugs too. Strip raw HTML and remote images from model output.
- Open coding takes free-text notes only, anchored to highlighted text. No dropdowns or labels until the modes exist. Then add a view with one Pass or Fail per trace and mode.
- Keys: 1 Pass, 2 Fail, D defer, arrows to move. Show reviewed versus remaining. Save every change to disk.
- Agent suggestions look different from human notes and each one needs accept or dismiss.
- Show the policy or escalation rule that applies beside the trace, so labels follow the policy and not the reviewer's instinct.
- Test with Playwright: label, reload, confirm the labels persisted and every key works.
- With no human present, build and smoke-test the app, stop the server, and return the launch command. Never say a review happened.

## While the human reviews

Poll the annotations file every few seconds and keep a running taxonomy (mode, description, count, example ids, quotes) visible in the app. Once the agent may help (after 30 human-read traces, see discover.md), scan all records with one subagent per mode, not per record, and push the hits as suggestions, favoring recall. Check each subagent's coverage first (discover.md, step 4). A false hit costs one click, a missed one costs a failure mode. When new modes appear, tell the reviewer which earlier traces to re-read.
