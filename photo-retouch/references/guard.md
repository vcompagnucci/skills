# Guard hook

Install it only with the photographer's OK, because it edits `~/.claude/settings.json`.

`scripts/photo_guard.py` turns two rules into blocks for Claude Code: nothing of a photo project is written to `/tmp` (macOS clears it, and process images were lost there), and no JPEG is produced in a project whose root holds `.sin-jpg` (a plain `python tools/ref_import.py ...` call passes, since it converts a JPEG reference in memory and writes PNG; chained, backgrounded or with a `$(...)` inside, it is checked like any command). It also warns about non-images or subfolders inside `proceso/`. No dependencies; if it fails, it lets the call through.

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
