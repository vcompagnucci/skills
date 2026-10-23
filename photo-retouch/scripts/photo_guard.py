#!/usr/bin/env python3
"""Guard for photo projects (photo-retouch skill). A Claude Code hook for PreToolUse and PostToolUse
on Bash|Write|Edit.

Photo projects live under one root folder: $PHOTO_ROOT, default ~/PHOTOS. Each project is a folder there.

PreToolUse denies:
  - writing anything of a photo project to /tmp. macOS clears /tmp and process images were lost
    there; they go to <project>/proceso/ (images) or work/ (regenerable scratch).
  - producing a JPEG in a project whose root holds the marker file .sin-jpg (the brief said
    "no JPG": no JPEG at any step, previews included).
PostToolUse warns the agent, once per file, about a JPEG in a .sin-jpg project, a non-image or a
subfolder inside proceso/ (the photographer browses it in Finder's gallery, which shows images
only and does not open subfolders; notes and numbers go to proceso-notas/).

No dependencies. If anything fails it does not block (exit 0).
"""
import json
import os
import re
import sys

PHOTOS = os.path.expanduser(os.environ.get("PHOTO_ROOT") or "~/PHOTOS").rstrip("/")
HOME = os.path.expanduser("~")
STATE = os.environ.get("PHOTO_GUARD_STATE") or os.path.expanduser("~/.claude/hooks/state/photo_guard.json")  # files already warned about
IMAGES = {".png", ".tif", ".tiff", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".dng", ".exr"}
_REL = PHOTOS[len(HOME):] if PHOTOS.startswith(HOME + "/") else None  # the root as written from ~
PROJECT_RE = re.compile((r"(?:(?:~|\$HOME|\$\{HOME\})" + re.escape(_REL) + "|" if _REL else "(?:")
                        + re.escape(PHOTOS) + r")/([^/\s'\"]+)")
TMP_RE = re.compile(r"(?<![\w.])(?:/private)?/tmp(?:/[^\s'\"]*)?")
TMP_OK = ("/tmp/claude-", "/private/tmp/claude-")  # the harness's own task outputs
JPEG_RE = re.compile(r"jpe?g|\bjfif\b", re.I)
READ_ONLY = {"find", "ls", "grep", "rg", "pgrep", "stat", "file", "mdls", "test", "[", "wc", "rm", "trash",
             "open", "du", "head", "tail", "cat", "which", "echo", "sed", "awk", "cd", "pwd", "printf",
             "basename", "dirname", "realpath", "shasum", "md5", "sort", "uniq", "diff", "cmp", "jq", "less"}
PREFIX = {"do", "then", "else", "!", "{", "(", "time"}  # not the command: look at the next word
SPLIT_RE = re.compile(r"&&|\|\||[;|\n]")


def projects_in(text: str, cwd: str) -> set:
    found = {m.group(1) for m in PROJECT_RE.finditer(text or "")}
    for path in (cwd or "",):
        if path.startswith(PHOTOS + "/"):
            found.add(path[len(PHOTOS) + 1:].split("/")[0])
    return {p for p in found if os.path.isdir(os.path.join(PHOTOS, p))}


def sin_jpg(project: str) -> bool:
    return os.path.exists(os.path.join(PHOTOS, project, ".sin-jpg"))


def tmp_paths(text: str) -> list:
    return [m.group(0) for m in TMP_RE.finditer(text or "") if not m.group(0).startswith(TMP_OK)]


TEXT_HEREDOC_RE = re.compile(r"^([^\n]*\b(?:cat|tee)\b[^\n]*<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n)(.*?\n)?\2[ \t]*$",
                             re.M | re.S)


def drop_text_heredocs(cmd: str) -> str:
    """Drop the body of heredocs that cat or tee write to a file: it is text, not commands.
    Heredocs fed to an interpreter (python3 - <<EOF) stay: there every line is code."""
    return TEXT_HEREDOC_RE.sub(lambda m: m.group(1) + m.group(2), cmd)


def first_word(segment: str) -> str:
    words = [w.lstrip("({") for w in segment.split() if not re.match(r"^\w+=", w)]
    words = [w for w in words if w]
    while words and words[0] in PREFIX:
        words.pop(0)
    return os.path.basename(words[0]) if words else ""


def reads_only(segment: str) -> bool:
    word = first_word(segment)
    if word == "sed" and re.search(r"\s(?:-\w*i|--in-place)", segment):  # sed -i writes
        return False
    return word in READ_ONLY


def writes_tmp(segment: str) -> bool:
    """A segment that uses /tmp and is not read-only (ls, find, cat...), or redirects into /tmp."""
    if not tmp_paths(segment):
        return False
    if re.search(r">>?\s*(?:/private)?/tmp", segment):
        return True
    return not reads_only(segment)


def writes_jpeg(segment: str) -> bool:
    """A segment that mentions JPEG (not counting the .sin-jpg marker name) and is not read-only,
    or redirects into a .jpg."""
    segment = segment.replace(".sin-jpg", "")
    if not JPEG_RE.search(segment):
        return False
    if re.search(r">>?\s*\S*\.jpe?g\b", segment, re.I):
        return True
    return not reads_only(segment)


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def pre(tool: str, inp: dict, cwd: str) -> None:
    if tool == "Bash":
        cmd = inp.get("command", "")
        projects = projects_in(cmd, cwd)
        cmd = drop_text_heredocs(cmd)
        if not projects:
            return
        tmp = [t for seg in SPLIT_RE.split(cmd) if writes_tmp(seg) for t in tmp_paths(seg)]
        if tmp:
            deny(f"photo_guard: this command touches a photo project and uses {tmp[0]}. macOS clears /tmp: "
                 "process images go to <project>/proceso/, notes and numbers to proceso-notas/, "
                 "regenerable scratch to work/.")
        blocked = [p for p in projects if sin_jpg(p)]
        if blocked and any(writes_jpeg(seg) for seg in SPLIT_RE.split(cmd)):
            deny(f"photo_guard: {blocked[0]} has .sin-jpg (the brief said no JPG) and this command "
                 "mentions JPEG. No step, previews included, produces JPEG: use PNG or TIFF. If you "
                 "are only reading or searching, start the segment with find, ls, grep, cat or test.")
        return
    path = inp.get("file_path", "")
    content = inp.get("content", "") or inp.get("new_string", "")
    if path.startswith(("/tmp/", "/private/tmp/")) and not path.startswith(TMP_OK) and (PHOTOS in content or (_REL and _REL in content)):
        deny(f"photo_guard: {path} is in /tmp and its content touches a photo project. macOS clears /tmp: "
             "scripts go to <project>/recipe/ or tools/, images to proceso/.")
    for p in projects_in(path, ""):
        if sin_jpg(p) and os.path.splitext(path)[1].lower() in (".jpg", ".jpeg"):
            deny(f"photo_guard: {p} has .sin-jpg: no JPEG file in the project. Use PNG or TIFF.")


def violations(project: str) -> list:
    root = os.path.join(PHOTOS, project)
    out = []
    proceso = os.path.join(root, "proceso")
    for dirpath, dirs, files in os.walk(proceso):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if dirpath == proceso:
            out += [("folder inside proceso/ (keep it flat: the group is a filename prefix)", os.path.join(dirpath, d)) for d in dirs]
        for f in files:
            if not f.startswith(".") and os.path.splitext(f)[1].lower() not in IMAGES:
                out.append(("not an image in proceso/", os.path.join(dirpath, f)))
    if sin_jpg(project):
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if os.path.splitext(f)[1].lower() in (".jpg", ".jpeg"):
                    out.append(("JPEG in a .sin-jpg project", os.path.join(dirpath, f)))
    return out


def post(tool: str, inp: dict, cwd: str) -> None:
    text = inp.get("command", "") if tool == "Bash" else inp.get("file_path", "")
    projects = projects_in(text, cwd if tool == "Bash" else "")
    if not projects:
        return
    try:
        with open(STATE) as fh:
            seen = set(json.load(fh))
    except (OSError, ValueError):
        seen = set()
    new = [(why, path) for p in sorted(projects) for why, path in violations(p) if path not in seen]
    if not new:
        return
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as fh:
        json.dump(sorted(seen | {path for _, path in new}), fh)
    lines = [f"- {why}: {path}" for why, path in new[:20]]
    if len(new) > 20:
        lines.append(f"- and {len(new) - 20} more")
    print(json.dumps({
        "decision": "block",
        "reason": "photo_guard (one warning per file):\n" + "\n".join(lines) + "\n"
                  "Process images go to proceso/; notes and numbers to proceso-notas/ (same group "
                  "name); a script that is run again, to tools/. In a .sin-jpg project, redo it as PNG or TIFF. "
                  "If the file is not yours, tell the user instead of moving it.",
    }))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    event, tool = data.get("hook_event_name"), data.get("tool_name")
    inp, cwd = data.get("tool_input") or {}, data.get("cwd", "")
    if tool not in ("Bash", "Write", "Edit"):
        return
    if event == "PreToolUse":
        pre(tool, inp, cwd)
    elif event == "PostToolUse":
        post(tool, inp, cwd)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass
