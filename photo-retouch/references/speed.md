# Speed

The photographer asked on 2026-10-15 that no request take an hour per run, with no loss of quality. These rules took one photo in four styles from ~14 min to under 2, and all 16 masters from 61 min to 8.

- **Iterate on the smallest unit that shows the change:** a crop, one case, one photo × style. Two full one-hour runs once recomputed masters that had not changed.
- **Before a batch, time one photo × style with `/usr/bin/time -l`.** Its peak memory decides how many workers fit; timing the whole batch tells you only after the machine is already full.
- **Heavy steps:** `MallocLargeCache=0 nice -n 19 .venv/bin/python ...`, without `taskpolicy -b`. `-b` pins the work to the efficiency cores and made each photo 3.8× slower; the photographer chose the fastest option on 2026-10-15. `MallocLargeCache=0` keeps the measured footprint honest on macOS (it reads ~2× high without it). At most 2 workers, and leave a quarter of the CPU free: other work shares the machine.
- **Skip an output only when the fingerprint of its inputs is unchanged.** A check for mere existence left the original and raw exports stale after a framing edit. Pattern: `export_originals` in `templates/portrait-qa/recipe/styles.py`.
- **Every stochastic step uses a fixed seed**, so a re-render of an unchanged style is pixel-identical and a regression can be proven. The film grain used `std::random_device` until 2026-10-15, and no re-render of that portrait could be verified.
- **When a run takes over 5 minutes, time each stage** and fix the slowest before running again. The grain stage alone was 341 of 474 s; it had OpenMP pragmas compiled without OpenMP.
- **Never detach a heavy process** (`nohup`, a bare `&`, `disown`, `setsid`). Two detached Python jobs once reached 17 GB and froze the machine. Close with `pgrep -fl` and nothing of yours running.

## Agent time

Measured on 2026-10-15 over two photo sessions: the model thinking and writing was 69–85 % of the work, renders 8–18 %. Each 1 k tokens the model writes costs ~7 s, and ~80 % of them are thinking; a call that writes little takes ~3 s. So the lever is how much the model thinks, not the render code and not the number of tool calls. The same tokens are the photographer's usage limit, so time and cost fall together.

- **Effort high, never xhigh.** The skill's frontmatter sets it. The xhigh session wrote 1.9 k tokens per call against 1.1 k at high, with p90 latency 48 s against 23 s (different tasks, so consistent with, not proof).
- **Mechanical steps go to a low-effort subagent**: a render whose command is decided, QA sheets, `compare_masters.py`, editor tests. Hand it the exact commands and the list of masters expected to change; it returns numbers and paths. Judgment stays in the main loop at high: reading contours at 200 %, choosing parameters, deciding what passes.
- **One auditor per deliverable, never one per lens, and none on a pilot.** On 2026-10-15 audits were 34 % of 29 hours of work, and the QA and editor subagents wrote 988 k tokens, more than the 649 k of the session that launched them.
- **Look at a crop, never a whole sheet.** A call right after reading an image took 13–20 s and wrote 2.5× the tokens of the rest (7 s); in one session those calls were 23 % of the model's time. Measure with numbers first and look only where the numbers say the decision is. Crop the zone to ≤1000 px a side before reading it: a 4416 px sheet is shown at 2000 px anyway, so the crop is cheaper and shows more real detail.
- **Keep the context small so it doesn't compact.** Each compaction took 1–4.5 min; one session compacted 17 times in a day (~40 min). Images and long outputs fill it: a subagent reads them and only its conclusion enters. One change per request, README updated at the end of each, outputs through `| tail`.
- **Short replies.** See SKILL.md > What the photographer reads.
