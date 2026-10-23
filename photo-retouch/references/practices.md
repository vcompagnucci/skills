# Practices

How every change was made, in the pipeline and in the editor. Each one is here because skipping it once cost a redo. Speed rules live in [speed.md](speed.md); the README as handoff, in SKILL.md > Where things go; the guard hook's one-time setup, in [guard.md](guard.md).

## Every change

1. **Back up first.** Before editing an editor or server file, or migrating the versions file, copy it to `respaldos/<file>.antes-<change>.<ext>`. Masters get APFS clones before a render (SKILL.md step 6), in `respaldos/<version>-antes-<change>/`: `<version>` the masters' next, `v<N>` after the last in the README's change log; `<change>` a short name, as in `respaldos/v8-antes-ojeras/`; one folder per version, since the tools take one. Every change made this way stayed reversible.
2. **Confirm the base.** Before building a variant on saved parameters, re-render the approved master from them and check it matches. A field missing from a saved dictionary once made skin 16 L* darker, and everything built on it was redone.
3. **Make the change.** One change per request.
4. **Prove it.** A test of its own that goes red when the feature breaks, then the existing suites once. A refactor of shared code is kept only if saved cases come out pixel-identical or differ exactly where expected. When a change makes older tests expect the old behaviour, update them or list them in the README's pending list.
5. **Report.** A change that moved something not asked about (another photo, an approved value, a saved version) goes in the first line of the reply. Syncing versions once restored 9 versions to one photo and gave others values tuned for a different photo; the photographer found out by looking.
6. **Close.** README updated with the dated request, what changed, the test result and the backup path. `pgrep -fl` shows nothing the agent started still running.

Done when all six hold for the change.

## Shared machine

- **Tests run on their own servers and ports**, with copies of anything the photographer saves. Their editor stays open and untouched while tests run.
- **The photographer's running processes are theirs.** Ask before stopping one; say which process and why.
- **Another agent is working in the project** when a process of theirs shows in `pgrep -fl` for that project, or `find <project> -type f -mmin -10` lists a file. Then a README write that the export or "what did you touch" branch asks for goes in your reply instead, so two writers never overwrite each other's README.
- **An approved value changes only on a new complaint.** Weakening a delivered default "to be safe" reopens a decision they already made.
