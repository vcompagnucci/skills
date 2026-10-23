# Practices

How every change was made, in the pipeline and in the editor. Each one is here because skipping it once cost a redo. Speed rules live in [speed.md](speed.md); the README as handoff, in SKILL.md > Where things go.

## Every change

1. **Back up first.** Before editing an editor or server file, copy it to `work/<file>.antes-<change>.<ext>`; before migrating the versions file, copy it to `respaldos/`. Masters get APFS clones before a render (SKILL.md step 6). Every change made this way stayed reversible.
2. **Confirm the base.** Before building a variant on saved parameters, re-render the approved master from them and check it matches. A field missing from a saved dictionary once made skin 16 L* darker, and everything built on it was redone.
3. **Make the change.** One change per request.
4. **Prove it.** A test of its own that goes red when the feature breaks, then the existing suites once. A refactor of shared code is kept only if saved cases come out pixel-identical or differ exactly where expected. When a change makes older tests expect the old behaviour, update them or list them in the README's pending list.
5. **Report.** A change that moved something not asked about (another photo, an approved value, a saved version) goes in the first line of the reply. Syncing versions once restored 9 versions to one photo and gave others values tuned for a different photo; the photographer found out by looking.
6. **Close.** README updated with the dated request, what changed, the test result and the backup path. `pgrep -fl` shows nothing the agent started still running.

Done when all six hold for the change.

## Shared machine

- **Tests run on their own servers and ports**, with copies of anything the photographer saves. Their editor stays open and untouched while tests run.
- **The photographer's running processes are theirs.** Ask before stopping one; say which process and why.
- **An approved value changes only on a new complaint.** Weakening a delivered default "to be safe" reopens a decision they already made.

## Guard hook

`scripts/photo_guard.py` turns two rules into blocks for Claude Code: nothing of a photo project is written to `/tmp` (macOS clears it, and process images were lost there), and no JPEG is produced in a project whose root holds `.sin-jpg`. It also warns about non-images or subfolders inside `proceso/`. No dependencies; if it fails, it lets the call through.

Copy it to `~/.claude/hooks/photo_guard.py` (or point at the skill's copy) and add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse":  [{ "matcher": "Bash|Write|Edit", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/photo_guard.py\"", "timeout": 10 }] }],
    "PostToolUse": [{ "matcher": "Bash|Write|Edit", "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/hooks/photo_guard.py\"", "timeout": 10 }] }]
  }
}
```

Projects under another root: set `PHOTO_ROOT`.

Done when a test command that writes a project file to `/tmp` is denied.
