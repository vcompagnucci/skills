#!/usr/bin/env python3
"""Print a live Apple HIG page as markdown.

Usage: python3 hig_page.py <slug> [<slug> ...]
       python3 hig_page.py buttons --section "Best practices"

The HIG site is a JavaScript app, so a plain web fetch returns only the title.
Apple serves the same content as JSON at
https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<slug>.json
and this script renders that JSON as markdown. Standard library only.
"""
import json, re, sys, urllib.request

API = "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/{}.json"
SITE = "https://developer.apple.com"


class Page:
    def __init__(self, d):
        self.refs = d.get("references", {})

    def url(self, ident):
        u = self.refs.get(ident, {}).get("url", "")
        return SITE + u if u.startswith("/") else u

    def inline(self, items):
        out = []
        for it in items or []:
            t = it.get("type")
            if t == "text": out.append(it.get("text", ""))
            elif t == "emphasis": out.append("*" + self.inline(it.get("inlineContent")) + "*")
            elif t == "strong": out.append("**" + self.inline(it.get("inlineContent")) + "**")
            elif t == "codeVoice": out.append("`" + it.get("code", "") + "`")
            elif t == "reference":
                r = self.refs.get(it.get("identifier"), {})
                out.append(f"[{it.get('overridingTitle') or r.get('title') or it.get('identifier')}]({self.url(it.get('identifier'))})")
            elif t == "link": out.append(f"[{it.get('title') or it.get('destination')}]({it.get('destination')})")
            elif t == "image": out.append(f"[Image: {self.refs.get(it.get('identifier'), {}).get('alt') or it.get('identifier')}]")
            else: out.append(self.inline(it.get("inlineContent")))
        return "".join(out)

    def blocks(self, items):
        out = []
        for b in items or []:
            t = b.get("type")
            if t == "heading": out.append("#" * b.get("level", 2) + " " + b.get("text", ""))
            elif t == "paragraph": out.append(self.inline(b.get("inlineContent")))
            elif t in ("unorderedList", "orderedList"):
                for n, li in enumerate(b.get("items", []), 1):
                    mark = f"{n}." if t == "orderedList" else "-"
                    out.append(f"{mark} " + self.blocks(li.get("content")).strip().replace("\n", "\n  "))
            elif t == "aside":
                out.append(f"> **{b.get('name') or 'Note'}:** " + self.blocks(b.get("content")).strip().replace("\n", "\n> "))
            elif t == "table":
                cell = lambda c: self.blocks(c).strip().replace("\n\n", "<br>").replace("\n", " ").replace("|", "\\|")
                grid = [[cell(c) for c in row] for row in b.get("rows", [])]
                for key, span in sorted((b.get("extendedData") or {}).items(), key=lambda kv: tuple(map(int, kv[0].split("_")))):  # merged cells: copy the spanning cell
                    ri, ci = map(int, key.split("_"))
                    if ri < len(grid) and ci < len(grid[ri]):
                        if span.get("rowspan") == 0 and ri > 0: grid[ri][ci] = grid[ri - 1][ci]
                        if span.get("colspan") == 0: grid[ri][ci] = ""
                rows = ["| " + " | ".join(row) + " |" for row in grid]
                if rows: rows.insert(1, "|" + "---|" * len(b["rows"][0]))
                out.append("\n".join(rows))
            elif t == "row":
                out.extend(self.blocks(c.get("content")) for c in b.get("columns", []))
            elif t == "tabNavigator":
                for tab in b.get("tabs", []):
                    out.append(f"**{tab.get('title')}**\n\n" + self.blocks(tab.get("content")))
            elif t == "links":
                out.extend(f"- [{self.refs.get(i, {}).get('title') or i}]({self.url(i)})" for i in b.get("items", []))
            elif t == "video": out.append(f"[Video: {self.refs.get(b.get('identifier'), {}).get('alt') or b.get('identifier')}]")
            elif "content" in b: out.append(self.blocks(b["content"]))
            elif "inlineContent" in b: out.append(self.inline(b["inlineContent"]))
        return "\n\n".join(x for x in out if x)


def render(slug):
    slug = slug.strip("/").split("/")[-1].split("#")[0].lower()
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError("a page slug has only lowercase letters, digits, and hyphens, like 'buttons'")
    req = urllib.request.Request(API.format(slug), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    p = Page(d)
    head = f"# {d['metadata'].get('title')}\n\n{SITE}/design/human-interface-guidelines/{slug}\n\n{p.inline(d.get('abstract'))}"
    body = "\n\n".join(p.blocks(s.get("content")) for s in d.get("primaryContentSections", []))
    return re.sub(r"\n{3,}", "\n\n", head + "\n\n" + body)


def section(md, name):
    parts = re.split(r"(?m)^(?=## )", md)
    hit = [s for s in parts if s.lower().startswith(f"## {name.lower()}")]
    return "\n".join(hit) if hit else f"No section named '{name}'. Sections: " + ", ".join(s.splitlines()[0][3:] for s in parts if s.startswith("## "))


if __name__ == "__main__":
    args = sys.argv[1:]
    want = None
    if "--section" in args:
        i = args.index("--section"); want = args[i + 1]; del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    failed = False
    for slug in args:
        try:
            md = render(slug)
            print(section(md, want) if want else md)
        except Exception as e:
            failed = True
            print(f"Could not fetch '{slug}' ({e}). Open {SITE}/design/human-interface-guidelines/{slug} in a browser.", file=sys.stderr)
    sys.exit(1 if failed else 0)
