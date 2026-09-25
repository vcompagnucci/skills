# HTML outputs and rich references

Thariq Shihipar's argument (May 2026, stated as personal opinion) that HTML should replace Markdown as the format Claude uses to communicate with you, and the July follow-up that rich artifacts also make better *inputs*.

## Why HTML

- **People don't read long Markdown.** "I tend to not actually read more than a 100-line Markdown file," and he can't get anyone in his org to either; he mostly has Claude edit files anyway, which removes Markdown's editing advantage. (`html`)
- **HTML can represent almost anything Claude can read.** Tables, CSS, SVG, scripts, interactions, spatial layouts, images; without it the model falls back to ASCII diagrams or "estimating colors with unicode characters". (`html`)
- **Visual structure makes big specs navigable.** Tabs, illustrations, links, even mobile-responsive layouts. (`html`)
- **Sharing is a link.** "The chance of someone actually reading your spec, report, or PR writeup is much higher if it's in HTML." (`html`)
- **Token cost is outweighed.** More tokens than Markdown, but the likelihood he reads it gives better overall output; in a 1M context it isn't noticeable. (`html`)
- **The real reason is staying in the loop.** As Claude took on more, he was reading plans less closely; HTML made him engaged again. (`html`)
- **It's a team pattern, not just his.** He "increasingly see[s] this pattern being applied by others on the Claude Code team", and the team's July context-engineering post lists HTML artifacts as the upgrade from plain markdown specs. (`html`, `ctx-eng`)
- **He's at the extreme.** "I have honestly stopped using Markdown altogether for almost everything, but I'm probably far on the HTML maximalist side of things." (`html`)

## Use cases

- **Specs and planning as a web of files.** Explorations of options → expand one with mockups → implementation plan → new session implements from all of them; keep them as references and for verification. (`html`)
- **Exploration grids.** "Generate 6 distinctly different approaches... in a grid... Label each with the tradeoff it's making." (`html`)
- **Code review.** Rendered diffs with severity-coded margin annotations, focused on the part you don't know. (`html`)
- **Design and prototypes.** Claude Design is HTML-based because HTML is expressive even when the target is React or Swift; add sliders and a copy-parameters button to tune an animation. (`html`)
- **Reports and explainers.** Synthesize Slack, code, git history into an explainer, deck, or incident report with SVG diagrams, "optimized for someone reading it once." (`html`)
- **Throwaway editors.** A single HTML file for one piece of data: a drag-to-bucket ticket board, a feature-flag form warning on unmet prerequisites, a prompt tuner with live previews. "The trick is always to end with an export" — copy as JSON, Markdown, prompt, or diff. (`html`)

## Getting started

- **Just ask.** "Make an HTML file" or "make an HTML artifact"; know what the artifact should do; build a skill only once patterns recur. (`html`)
- **Use Claude Code for ingestion.** It reads the file system, MCPs (Slack, Linear), the browser, and git history, which chat apps can't. (`html`)

## Rich references as inputs

- **Simple specs → rich references.** Claude 5 models handle HTML artifacts, test suites as specs, code to port, and rubrics. (`ctx-eng`)
- **HTML specs are for Claude too, not only for people.** Thariq uses his HTML files "as specs and reference files" and passes them to the implementing session and to the verification agent. The corpus never carves out "specs only Claude reads" as a place where Markdown is fine. (`html`, `ctx-eng`)
- **Prefer code as reference.** An HTML mockup of a design generally produces better results than a description or a screenshot. (`ctx-eng`)

## Key source articles
`html` · `ctx-eng`
