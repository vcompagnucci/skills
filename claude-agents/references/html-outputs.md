# HTML outputs and rich references

In May 2026 Thariq Shihipar argued, as his personal opinion, that HTML should replace Markdown as the format Claude uses to show you its work. The team's July post adds that rich artifacts also make better *inputs* for Claude.

## Why HTML

- **People don't read long Markdown.** "I tend to not actually read more than a 100-line Markdown file," and he can't get anyone in his org to read one either. He mostly has Claude edit the files anyway, which cancels Markdown's main advantage. (`html`)
- **HTML can show almost anything Claude can read.** Tables, CSS, SVG, scripts, interactive elements, spatial layouts, images. Without it, the model falls back on ASCII diagrams or "estimating colors with unicode characters". (`html`)
- **Big specs become easy to navigate.** Tabs, illustrations, links, even layouts that adapt to a phone. (`html`)
- **Sharing is a link.** "The chance of someone actually reading your spec, report, or PR writeup is much higher if it's in HTML." (`html`)
- **The extra tokens are worth it.** HTML uses more tokens than Markdown, but he's far more likely to read it, so the output ends up better. In a 1M context he doesn't notice the difference. (`html`)
- **The real reason is staying in the loop.** As Claude took on more, he was reading plans less closely. HTML got him paying attention again. (`html`)
- **It's a team habit, not only his.** He says he "increasingly see[s] this pattern being applied by others on the Claude Code team", and the team's July post on context engineering lists HTML artifacts as the upgrade from plain markdown specs. (`html`, `ctx-eng`)
- **He puts himself at the extreme.** "I have honestly stopped using Markdown altogether for almost everything, but I'm probably far on the HTML maximalist side of things." (`html`)

## Use cases

- **Specs and plans as a set of files.** First several explorations of options, then one of them expanded with mockups, then an implementation plan. A new session implements from all of them. He keeps the files as references and for verification. (`html`)
- **Exploration grids.** "Generate 6 distinctly different approaches... in a grid... Label each with the tradeoff it's making." (`html`)
- **Code review.** The rendered diff with margin notes colored by severity, focused on the part you don't know well. (`html`)
- **Design and prototypes.** Claude Design is built on HTML because HTML handles design well even when the final code is React or Swift. Add sliders and a button that copies the parameters to tune an animation. (`html`)
- **Reports and explainers.** Pull from Slack, the code, and git history into an explainer, a deck, or an incident report with SVG diagrams, "optimized for someone reading it once." (`html`)
- **Throwaway editors.** One HTML file for one piece of data: a ticket board you drag cards across, a feature-flag form that warns when a prerequisite is off, a prompt editor with live previews. "The trick is always to end with an export": copy as JSON, Markdown, a prompt, or a diff. (`html`)

## Getting started

- **Just ask.** "Make an HTML file" or "make an HTML artifact". Know what you want the file to do. Build a skill only once the same kind of request keeps coming back. (`html`)
- **Use Claude Code, because it can read your context.** It reads the file system, MCPs like Slack and Linear, the browser, and git history. Chat apps can't. (`html`)

## Rich references as inputs

- **Simple specs → rich references.** Claude 5 models can work from HTML artifacts, test suites used as specs, code to port, and rubrics. (`ctx-eng`)
- **HTML specs are for Claude too, not only for people.** Thariq uses his HTML files "as specs and reference files" and passes them to the session that implements and to the verification agent. The posts never make an exception where Markdown is fine because only Claude reads the spec. (`html`, `ctx-eng`)
- **Prefer code as a reference.** An HTML mockup of a design generally gets better results than a description or a screenshot. (`ctx-eng`)

## Key source articles
`html` · `ctx-eng`
