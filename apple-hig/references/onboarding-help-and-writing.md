# Onboarding, help, settings, and writing

The words, first-run experience, help, settings, and rating requests through which an app talks to people. Apple's position: write in one clear, consistent voice, let people learn by doing rather than through long onboarding, and offer help in context and in proportion to the task. Strong defaults should make settings nearly unnecessary, and rating requests wait for real engagement. (`writing`, `onboarding`, `offering-help`, `settings`, `ratings-and-reviews`)

## Choosing how to teach and where settings live

- **Prefer an app people understand by using it, and context-specific tips over a single onboarding flow.** Tips teach the current task while people make progress, shown near the interface they describe. If onboarding is necessary, make it fast, fun, and optional, and start it after launch completes, not as part of it. (`onboarding`)
- **Let the app's tasks decide the type of help: an inline view for one- or two-step tasks, a tutorial for complex or multistep ones.** Tie help to what people are doing right now, and make it easy to dismiss or avoid. (`offering-help`)
- **Pick a tip's type by the layout: a popover tip to preserve the content flow, an inline tip to keep surrounding information visible.** An inline tip is annotation-style when it points to a specific element, and hint-style when it doesn't relate to one. (`offering-help`)
- **Put task-specific options in the screens they affect, not in your settings area.** Showing or hiding parts of the view, reordering a collection, or filtering a list is discoverable there, while a settings area disconnects the option from its context, suspends the task, and often hides the results. (`settings`)

## Writing (`writing`)

- **Define the app's voice, and keep its vocabulary consistent.** Decide who you're talking to and how they should feel, like trust and stability in a banking app or excitement in a game, and keep a list of common terms so everything feels cohesive. (`writing`)
- **Vary the tone with the situation, in the app and in the physical world.** Someone who just reached an exercise goal and someone whose payment failed need different words, and the situation also shapes how the text appears on screen. (`writing`)
- **Be clear, with as few words as possible.** Choose words that are easily understood and convey the right thing, check that each one needs to be there, and when in doubt, read your writing out loud. (`writing`)
- **Write for everyone in simple, plain language.** Keep accessibility and localization in mind, and avoid jargon and gendered terminology, so the app speaks to as many people as possible. (`writing`)
- **Consider each screen's purpose, and put the most important information first.** Format text so it's easy to read, and when you need to convey more than one idea, break the text across several screens with a clear flow of information. (`writing`)
- **Label buttons and links with verbs, and skip cute or clever wording.** Active voice and clear labels move people from step to step. "Send" works better than "Let's do it!", and a descriptive link like "Learn more about UX Writing" beats "Click here", which matters most to screen reader users. (`writing`)
- **Build language patterns you can reuse.** Consistency builds familiarity, making the app feel cohesive, intuitive, and thoughtfully designed, and it makes writing for the app easier. (`writing`)
- **Choose a capitalization style for each element type and apply it consistently.** Title case reads formal and sentence case casual, so use, for example, title case for all alerts or sentence case for all headlines, while following component rules like those for button labels. (`writing`)
- **Label the steps of a multistep flow consistently.** Start with "Get Started", move on with a label that hints at the next step or with "Continue" or "Next", whichever you choose throughout, and end with "Done". (`writing`)
- **Use possessive pronouns sparingly, and never "we".** "Favorites" says the same as "Your Favorites" more succinctly, so keep any pronouns consistent. "We" leaves people unsure who is speaking: "Unable to load content" beats "We're having trouble loading this content." (`writing`)
- **Write for how people use each device.** Keep language consistent across devices, but describe gestures correctly, saying "tap", not "click", on iPhone and iPad. iPhone invites personalization, but its small screen requires brevity. (`writing`)
- **Give every empty state a clear next step.** A blank screen, like a finished to-do list, can welcome and teach, but it's daunting when the next action isn't obvious, so offer a button or link. Empty states are usually temporary, so never put crucial information there. (`writing`)
- **Show errors next to the problem, without blame, saying how to fix it.** "Choose a password with at least 8 characters" beats "That password is too short", and "oops!" sounds insincere. If language alone can't fix a common error, rethink the interaction. (`writing`)
- **Choose the delivery method by the message's urgency and importance.** Consider where people will see it, whether it needs immediate action, and how much supporting information they need, then pick a notification, alert, or action sheet and a fitting tone. (`writing`)
- **Label settings practically, and describe what a setting does when it's turned on.** People infer the opposite, so the explanation needn't say what happens when it's off. To send people to a setting, give a direct link or button rather than describing where it is. (`writing`)
- **Label every text field and show its expected format in hint text.** Hint text can give an example, like "name@example.com", or describe the content, like "Your name". Show errors next to the field and phrase rules positively: "Use only letters for your name" beats "Don't use numbers or symbols" or "Invalid name". (`writing`)

## Onboarding (`onboarding`)

- **Teach through interactivity.** People grasp and retain more by doing than by viewing instructions, so let them safely test an action, discover a feature, or try a game mechanic. (`onboarding`)
- **Keep a required onboarding flow brief and enjoyable, with little to memorize.** People are more likely to finish quick, entertaining onboarding, while teaching too much overwhelms them and they remember less. (`onboarding`)
- **Keep onboarding about your app or game, not the device.** People come to learn your experience, and they don't need to learn how to use the system. (`onboarding`)
- **Make a separate tutorial optional, and never show it again after people skip it.** Keep it easy to find later, for example in a help, account, or settings area. (`onboarding`)
- **Show a splash screen only if necessary, and only long enough to absorb at a glance.** Make it a beautiful graphic that communicates succinctly without feeling like a delay. (`onboarding`)
- **Never make people wait for large downloads before they can start.** People want to use the app or game right after first launch, onboarding or not, so ship enough media and content in the package itself. (`onboarding`)
- **Keep licensing details out of onboarding.** Let the App Store show agreements and disclaimers so people read them before downloading. If you must include them, integrate them without disrupting the experience. (`onboarding`)
- **Postpone nonessential setup flows and customization steps.** Reasonable default settings let most people start interacting right away without configuring anything. (`onboarding`)
- **Request permission during onboarding only when the app can't function without that data or resource.** There you can explain why you need it and what people gain. Otherwise, ask when people first use the feature that relies on it. (`onboarding`)
- **Let people experience the app before prompting for ratings or purchases.** People respond more positively to these requests once they've become engaged. (`onboarding`)

## Offering help (`offering-help`)

- **Keep help relevant to the current context, consistent with the platform, and inclusive.** Use language and images that fit how people are using the app, and don't tell people to click a button on iPhone or tap a menu item on a Mac. (`offering-help`)
- **Don't explain how standard components and patterns work.** Describe what an element does in your app instead. For a unique control, or an input device used in a nonstandard way, orient people quickly with animation or graphics, not a long description. (`offering-help`)
- **Use tips for simple features that people can complete in a few steps.** A feature that needs more than three actions is probably too complicated. A tip is a small, transient view, suited to new or less obvious features, or faster ways to do a task. (`offering-help`)
- **Keep tips to one or two short, actionable sentences, never promotional.** Say directly what the feature does and how to use it, and leave out other features, user flows, and anything that advertises or sells. (`offering-help`)
- **Set eligibility rules so tips reach only people who benefit.** Someone who already used a feature won't value a tip about it, so use parameter- or event-based rules, and pace several tips at a reasonable cadence, such as once every 24 hours. (`offering-help`)
- **Give a tip a symbol people associate with the feature, preferably filled.** A star helps people relate a tip to favorites, but don't repeat an image the tip already points to. (`offering-help`)
- **Add a button when a tip should lead to settings or more information.** It can take people straight to the settings that customize the feature, or to resources like a setup flow. (`offering-help`)
- **(macOS) Offer tooltips, called help tags in user documentation, that appear when people hold the pointer over an element.** A tooltip briefly describes how to use a component, in Mac apps and in iPhone and iPad apps running on a Mac. (`offering-help`)
- **(macOS) Make a tooltip explain only the control people indicate, starting with a verb.** People don't want nearby controls or the larger task explained: "Restore default settings", "Add or remove a language from the list". (`offering-help`)
- **(macOS) Don't repeat the control's name in its tooltip.** The name takes up space and rarely adds value to the description. (`offering-help`)
- **(macOS) Keep tooltips to 60 to 75 characters, in sentence case.** Localization changes length, so use fragments and omit articles. Sentence case feels approachable, and complete sentences skip ending punctuation unless the app's style needs it. If a control needs a lot of text, simplify the interface. (`offering-help`)
- **(macOS) Consider context-sensitive tooltips.** For example, provide different text for each of a control's states. (`offering-help`)

## Settings (`settings`)

- **Choose defaults that give the largest number of people the best experience, and detect what you can instead of asking.** A game can tune performance for its device and detect a connected controller, and an app can detect Dark Mode, so people can start without adjusting anything. (`settings`)
- **Minimize the number of settings.** People appreciate control, but too many settings make the experience feel less approachable and make any one setting hard to find. (`settings`)
- **Never duplicate systemwide settings.** People manage accessibility, scrolling behavior, and authentication in the Settings app and expect every app to follow them. A custom copy implies the system setting may not apply, or that yours affects other apps. (`settings`)
- **Open settings the way people expect.** With a physical keyboard, people press Command-Comma to open an app's settings, and players often press Esc in a game. (`settings`)
- **Keep your own settings area for general options people rarely change.** Opening it interrupts what they're doing, so it suits things like window setup, how a game saves, key mappings, or account options. (`settings`)
- **Add only the most rarely changed options to the system Settings app.** If your settings live there, consider a button in your interface that opens them directly. (`settings`)
- **(macOS) Put a Settings item in the App menu, not a settings button in a window's toolbar.** A toolbar button takes space from essential, frequently used commands. Document-level options go in the File menu. (`settings`)
- **(macOS) Organize the settings window into panes, with a noncustomizable, always-visible toolbar that shows the active pane.** Choosing Settings in the App menu opens the window, and its toolbar buttons switch between panes of related settings. People rely on a stable settings interface to find what they need. (`settings`)
- **(macOS) Dim the settings window's minimize and maximize buttons.** Command-Comma opens it quickly, so it needn't stay in the Dock, and it already fits the current pane, so people needn't expand it. (`settings`)
- **(macOS) Title the settings window after the visible pane, and reopen it on the last pane viewed.** Without multiple panes, use "App Name Settings". People often adjust related settings more than once. (`settings`)

## Ratings and reviews (`ratings-and-reviews`)

- **Ask for a rating only after people show engagement.** Prompt after they complete a game level or significant task, judged by launches, features explored, or tasks completed. Never ask on first launch or during onboarding, before people have formed an opinion. (`ratings-and-reviews`)
- **Never interrupt a task or game to ask.** Feedback requests can disrupt the experience and feel like a burden, so wait for a natural break or stopping point. (`ratings-and-reviews`)
- **Allow at least a week or two between requests, and ask again only after more engagement.** Repeated requests irritate people and can hurt their opinion of the app. (`ratings-and-reviews`)
- **Prefer the system-provided prompt in iOS, iPadOS, and macOS.** It's consistent and nonintrusive, appears only if people haven't already given feedback, and shows at most three times per app in 365 days. People can opt out for all apps. (`ratings-and-reviews`)
- **Weigh resetting your summary rating with a new version.** A reset makes ratings reflect the current version, but fewer ratings overall can discourage some people from downloading the app. (`ratings-and-reviews`)

## Key source pages
`writing` · `onboarding` · `offering-help` · `settings` · `ratings-and-reviews`
