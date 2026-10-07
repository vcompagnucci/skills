# Feedback, status, and data display

How an app tells people what's happening, from status and progress to launch and charts. Apple's position: match the delivery to the information's significance, showing status in place and interrupting only for critical problems, and make waits feel short with immediate content and honest progress. A chart earns its place only by highlighting what people can learn, and every form of feedback must stay accessible. (`feedback`, `loading`, `progress-indicators`, `launching`, `charting-data`, `charts`)

**Contents:** Choosing how to show status, waits, and data · Feedback · Loading · Progress indicators · Launching · Charts · Chart accessibility · Status bars · Gauges and rating indicators · Activity rings · Key source pages

## Choosing how to show status, waits, and data

- **Show status in place, and interrupt with an alert only for critical, ideally actionable, information.** Mail shows the latest update and unread count in its mailbox toolbar, easy to check without leaving context. Alerts used too often lose their impact. (`feedback`)
- **Show something at once, and when loading takes more than a moment or two, say so with a progress indicator.** An empty screen reads as a problem with the app, so show placeholder text, graphics, or animations and replace them as content arrives. (`loading`)
- **Use a determinate indicator whenever you know how long a task will take, switching from indeterminate as soon as you do.** An indeterminate one only shows that work is happening, while a determinate one lets people decide whether to wait, do something else, or abandon the task. (`progress-indicators`, `loading`)
- **A launch screen mimics the first screen, while a splash screen, if you need one, opens your onboarding flow.** A splash screen is a graphic that communicates branding and other information you need to provide. With no onboarding, show it as soon as launching completes. (`launching`)
- **Use a chart to highlight what people can learn from data, and a list or table when you only need to provide it.** Charts are visually prominent and draw attention, while a list or table lets people scroll, search, and sort. (`charting-data`)

## Feedback (`feedback`)

- **Make all feedback accessible by delivering it in more than one way.** Combining color, text, sound, and haptics reaches people whether they silence the device, look away from the screen, or use VoiceOver. (`feedback`)
- **Warn people before a task causes unexpected, irreversible data loss, and only then.** Don't warn when loss is the expected result: the Finder doesn't warn every time people throw away a file. (`feedback`)
- **Confirm completion only for significant actions.** People appreciate confirmation of a successful Apple Pay transaction, but they expect most tasks to succeed and only need to know when one doesn't. (`feedback`)
- **When a command can't be carried out, say so and help people understand why.** Asked for directions without a destination, Maps explains it can't give directions to and from the same location. (`feedback`)

## Loading (`loading`)

- **Load in the background so people can keep doing other things in your app or game.** Background loading gives people access to other actions: a game loads while players learn about the next level or view an in-game menu. (`loading`)
- **Download large assets in the background to shorten installation and launch.** Schedule downloads like game level packs, 3D character models, and textures for right after installation, during updates, or at other nondisruptive times. (`loading`)
- **When a long wait is unavoidable, give people something worth viewing.** Offer gameplay hints, tips, or introductions to new features, and gauge the remaining time accurately so the content is neither cut short nor repeated. (`loading`)
- **For games, consider a custom loading view.** Standard progress indicators work well in most apps but can feel out of place in a game, so use custom animations and elements that match its style. (`loading`)

## Progress indicators (`progress-indicators`)

- **Know the two types: determinate for a task with a well-defined duration, indeterminate for an unquantifiable one.** A file conversion gets a determinate indicator, and loading or synchronizing complex data an indeterminate one. Every indicator is transient, appearing only while the operation runs. (`progress-indicators`)
- **Expect a bar or a circle: a progress bar fills from the leading to the trailing side, and a circular indicator fills clockwise.** An indeterminate activity indicator, or spinner, spins in a circle on all platforms, and macOS also offers an indeterminate bar. (`progress-indicators`)
- **Report progress accurately and at an even pace.** Showing 90% in five seconds and the last 10% in five minutes makes people wonder whether the app still works, and can even feel deceptive. (`progress-indicators`)
- **Keep indicators moving, and explain any stall.** People read a stationary indicator as a stalled process or frozen app, so if work stalls, say what the problem is and what people can do about it. (`progress-indicators`)
- **Never switch between the circular and bar styles.** Spinners and progress bars have different shapes and sizes, so changing from one to the other disrupts the interface and confuses people. (`progress-indicators`)
- **Display progress indicators in a consistent location.** People can then reliably find the status of an operation within and between apps and across platforms. (`progress-indicators`)
- **Add a description only when it gives useful context, and keep it accurate and succinct.** Vague terms like loading or authenticating seldom add value. (`progress-indicators`)
- **Let people halt processing when feasible, and warn them when stopping costs something.** Offer Cancel when interrupting is harmless, and add Pause when it isn't, like losing a partly downloaded file. If canceling loses progress, show an alert to confirm or resume. (`progress-indicators`)
- **(iOS, iPadOS) Use a refresh control to let people reload content immediately, typically in a table view.** It's an activity indicator hidden until people drag down the view they want to reload, as when they drag down Mail's Inbox to check for new messages. (`progress-indicators`)
- **(iOS, iPadOS) Keep updating content automatically, and give a refresh control a short title only if it adds value.** People expect periodic updates without starting each one, and the animation already shows loading. Podcasts' title says when the last update occurred, never how to refresh. (`progress-indicators`)
- **(macOS) Prefer an unlabeled spinner for background operations and tight spaces.** Spinners are small and unobtrusive, suiting tasks like retrieving messages or progress inside a text field or beside a button. People usually started the process, so a label is unnecessary. (`progress-indicators`)

## Launching (`launching`)

- **Launch instantly, with a launch screen only where the platform requires one: iOS and iPadOS, not macOS.** People sometimes won't wait more than a couple of seconds, and the system swaps the launch screen for the first screen so the app feels fast. (`launching`)
- **(iOS, iPadOS) Downplay the launch screen, and never advertise on it.** Its sole job is to make the app feel quick and ready, so it's no place for onboarding, artistic expression, a splash or About look, or logos that aren't a fixed part of the first screen. (`launching`)
- **(iOS, iPadOS) Make the launch screen nearly identical to the first screen, and leave text off it.** Differing elements cause an unpleasant flash, so a solid-color first screen gets a solid-color launch screen, matching orientation and appearance. Its content never changes, so text wouldn't be localized. (`launching`)
- **Restore the previous state when the app restarts, down to granular details.** Don't make people retrace their steps: return them to their most recent scroll position and show windows in the same state and location. (`launching`)
- **(iOS, iPadOS) Launch in the device's current orientation if the app supports both.** Otherwise launch in the supported orientation and let people rotate, making a landscape-only interface work whichever way the device is turned. (`launching`)

## Charts (`charts`, `charting-data`)

- **Prefer common chart types like bar and line charts, and teach people to read any chart that presents data in a novel way.** People likely already know how to read common types. When a Watch pairs with iPhone, Activity animates each ring individually to show what it measures. (`charting-data`)
- **Build a chart from marks in a plot area, framed by axes with ticks and grid lines.** Ticks locate important values along an axis, grid lines help estimate a mark far from an axis, and a legend explains properties unrelated to position, like color for categories. (`charts`)
- **Choose the mark type by what you want to communicate.** Bars compare categories or parts of a whole, and over time suit values that are sums, like daily steps. Lines show change and trends over time, and points show individual values, relationships, outliers, and clusters. (`charts`)
- **Consider combining mark types when it adds clarity.** Point marks on top of a line chart draw attention to individual values while the line still shows the overall trend. (`charts`)
- **Keep a chart simple, letting people choose when they want more detail.** Too much data hides the relationships you want to convey, so reveal it gradually through levels of detail or subsets, or offer several versions of an interactive chart, each with more functionality. (`charting-data`)
- **Let people interact with the data when it makes sense, but never require interaction to reveal critical information.** Stocks shows performance over the period people choose, and people can drag a vertical indicator through the line to reveal the value at any time. (`charts`)
- **Examine the data at several levels to find what's worth showing.** A macro view suggests totals or averages, a mid-level view useful subsets, and individual points specific values to call out. Several perspectives encourage people to engage. (`charting-data`)
- **Write titles and labels that explain a chart's purpose and functionality before people view it.** VoiceOver users and people with certain cognitive disabilities rely on that context to grasp the chart's main message before deciding to investigate. (`charts`)
- **Summarize the main message in descriptive text: a title, subtitle, annotations, or a headline.** Weather's "Chance of light rain in the next hour" gives people what they need at a glance. A headline makes a chart more accessible but doesn't replace accessibility labels. (`charts`, `charting-data`)
- **Make the data the most prominent element.** Keep a consistent visual hierarchy in which descriptions and axes add context without competing with the data. (`charts`)
- **Set the axis range by what the chart means: fixed when the bounds matter, dynamic when values vary widely.** People expect battery charge to run from 0% to 100%, while Health's Steps chart moves its upper bound so the largest count sits near the top. (`charts`)
- **Choose the lower bound by mark type and use.** A zero lower bound lets people compare bar heights to estimate values, but it can hide meaningful differences, like those between resting and active heart rates, far from zero. (`charts`)
- **Use familiar sequences for tick and grid-line labels.** People read 0, 5, 10 at a glance, but spend extra time on 1, 6, 11, even though it follows the same rule. (`charts`)
- **Tailor grid lines and labels to the chart's use.** Too many overwhelm and too few make values hard to estimate. If people can inspect individual points, use fewer grid lines and light label colors to keep the data prominent. (`charts`)
- **Size a chart for its functionality, topic, and level of detail.** A large chart leaves room to read its details and explore the data, while a small one suits glanceable information or a preview of a larger version people can open. (`charting-data`)
- **In a compact environment, maximize the plot area's width.** Keep vertical-axis labels short, describe units elsewhere, like the title, and put a long axis label inside the plot area when it hides nothing important. (`charts`)
- **Align a chart with the interface around it.** Align its leading edge with other views, put vertical grid-line labels on their trailing side, and consider a trailing Y axis. A tick can anchor a label that seems unattached to a grid line. (`charts`)
- **Never rely on color alone to differentiate data or convey essential information.** Supplement it with shapes or patterns, so people can use the chart whether or not they discern colors: Health uses two point shapes for the two blood-pressure readings. (`charts`)
- **Add visual separation between contiguous areas of color.** In a bar that stacks differently colored marks, separators help people distinguish each one, as in iPhone Storage. (`charts`)
- **Keep charts consistent when they serve a similar purpose, deviating only to highlight differences.** A different type or style implies the charts are unrelated, and consistency lets people apply what they learn from one chart to another. (`charting-data`)
- **Maintain continuity among charts that show the same data.** Use one chart type and consistent colors, annotations, layouts, and text: each small Health Trends chart expands into a version with the same style, colors, marks, and annotations. (`charting-data`)

## Chart accessibility (`charts`, `charting-data`)

- **Make every chart accessible, like any infographic.** Beyond the visual descriptions, provide accessibility labels that describe values and components and accessibility elements that let people interact with the chart. (`charts`, `charting-data`)
- **Consider Audio Graphs, which Swift Charts provides by default.** It turns values and trends into tones for VoiceOver, and you can add a title and summary. Without it, give an overview: the chart type, what each axis represents, and the axis bounds. (`charts`)
- **Give each important or interactive element an accessibility label written for the chart's purpose.** Maps summarizes elevation over portions of a cycling route, while Health labels each Steps bar with its count. A small chart inside a button can take one label. (`charts`)
- **Give each value context and actual numbers in its accessibility label.** Include its date or location without repeating what the overview already says, and avoid subjective words like rapidly or almost so people form their own interpretation. (`charts`)
- **Describe what the data represents, not what it looks like, in unambiguous formats.** Name what a red or blue series means rather than its color, and write "June 6" not "6/6" and "60 minutes" not "60m". (`charts`)
- **Refer to axes consistently throughout the app, like always mentioning the X axis first.** People then spend less time figuring out which axis a description refers to. (`charts`)
- **Hide visible axis and tick labels from assistive technologies.** They help sighted people assess trends and estimate values, but VoiceOver users get values and trends from accessibility labels and Audio Graphs. (`charts`)
- **Make an interactive chart easy to target.** When marks are too small for a finger or pointer, hard for people with reduced motor control, make the whole plot area the hit target and let people scrub across it. (`charts`)
- **Give keyboard and Switch Control users a logical path through an interactive chart.** These inputs visit elements in linear order, so define a predictable path, like along the X axis, or for a very large dataset let focus move among subsets of values. (`charts`)
- **Help people notice important changes to marks or axes.** Animate them, and also highlight the change in other ways for VoiceOver users and people who turn off animations, so nobody misreads the chart. (`charts`)

## Status bars (`status-bars`)

- **(iOS, iPadOS) Obscure content under the status bar, preferably with a scroll edge effect.** Its background is transparent, so content showing through makes the time, carrier, and battery level hard to read, and controls behind it invite taps that can't work. (`status-bars`)
- **(iOS, iPadOS) Consider hiding the status bar temporarily for full-screen media.** It distracts people from media, so Photos hides it and other interface elements while people browse full-screen photos. (`status-bars`)
- **(iOS, iPadOS) Never hide the status bar permanently, and let people restore it with a simple, discoverable gesture.** Without it, people must leave the app to check the time or Wi-Fi. In Photos, a single tap brings it back. (`status-bars`)

## Gauges and rating indicators (`gauges`, `rating-indicators`)

- **Pick a gauge's standard or capacity style by how it should mark the value.** A gauge maps the current value to a point on a circular or linear path. The standard style shows an indicator at that point, and the capacity style a fill that stops there. (`gauges`)
- **Label the current value and both endpoints of a gauge succinctly.** Not every style shows every label, but VoiceOver reads the visible ones so people understand the gauge without seeing the screen. (`gauges`)
- **Consider a gradient fill that communicates the gauge's purpose.** A temperature gauge can run from red to blue for hot to cold and label the highest and lowest temperatures for context. (`gauges`)
- **(iOS) Use the accessory gauge variant in Lock Screen widgets.** Circular and linear gauges, in standard or capacity style, come in this variant, which works well in iOS Lock Screen widgets. (`gauges`)
- **(macOS) Use a level indicator to convey capacity, rating, or, rarely, relevance.** macOS offers it alongside gauges. The relevance style's shaded horizontal bar helps people compare items, as in a list of search results. (`gauges`)
- **(macOS) Pick a continuous or discrete capacity indicator.** Continuous is a horizontal translucent track that fills with a solid bar. Discrete is a row of equally sized rectangular segments, as many as the total capacity, that fill completely, never partially. (`gauges`)
- **(macOS) Prefer the continuous capacity style for large ranges.** A large range makes a discrete indicator's segments too small to be useful. (`gauges`)
- **(macOS) Change the fill color to flag significant parts of the range.** The default is green. Switch colors when the value gets very low, very high, or just past the middle, for the whole indicator or as tiers within one. (`gauges`)
- **(macOS) Let people change a rating inline.** In a list of ranked items, people should adjust a rank without opening a separate editing screen. (`rating-indicators`)
- **(macOS) Keep the star unless a custom symbol's purpose is clear, and expect only whole symbols at fixed spacing.** People may not link other symbols to a rating. The indicator rounds to complete symbols, which never stretch to fill the width. (`rating-indicators`)

## Activity rings (`activity-rings`)

- **(iOS, iPadOS) Show Activity rings where they're relevant to your app's purpose.** People expect them in health and fitness apps, especially ones contributing to HealthKit, on a workout metrics screen or an end-of-workout summary. macOS doesn't support them. (`activity-rings`)
- **(iOS, iPadOS) Use the rings only for one person's Move, Exercise, and Stand progress.** Never replicate or modify them for other data or show that progress in another ring-like element, and identify the person with a label, photo, or avatar. (`activity-rings`)
- **(iOS, iPadOS) Keep the rings' appearance the same everywhere, adapting the interface to them.** Never recolor them with filters or opacity, and scale them so they don't look out of place. Keep them on black, ideally in a circle made by the enclosing view's corner radius, not a mask. (`activity-rings`)
- **(iOS, iPadOS) Keep the black background visible around the outermost ring.** If necessary, add a thin black stroke around its outer edge, but never a gradient, shadow, or other visual effect. (`activity-rings`)
- **(iOS, iPadOS) Color each ring's labels and values with that ring's color.** Move is RGB 250, 17, 79, Exercise 166, 255, 0, and Stand 0, 255, 246, covering the ring names and each ring's current and goal values. (`activity-rings`)
- **(iOS, iPadOS) Keep an outer margin at least as wide as the gap between rings, and set other ring-like elements apart.** Nothing may crop or encroach on the margin, and padding, lines, labels, color, or scale keep mixed ring styles from confusing people. (`activity-rings`)
- **(iOS, iPadOS) Don't send notifications that repeat the Activity app's updates, and never put the rings in one.** The system already reports Move, Exercise, and Stand progress, so duplicates confuse people. Mentioning progress unique to your app is fine. (`activity-rings`)
- **(iOS, iPadOS) Never use Activity rings for decoration or branding.** They inform rather than embellish, so keep them out of labels, background graphics, your app icon, and marketing materials. (`activity-rings`)
- **(iOS) Expect activity history to mix three-ring and Move-only displays.** With a paired Apple Watch iOS shows all three rings, and without one only the Move ring, estimated from steps and other apps' workouts. (`activity-rings`)

## Key source pages
`feedback` · `loading` · `progress-indicators` · `launching` · `charts` · `charting-data` · `status-bars` · `gauges` · `activity-rings` · `rating-indicators`
