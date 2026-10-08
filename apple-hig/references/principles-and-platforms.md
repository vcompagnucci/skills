# Principles and platforms

Apple's eight design principles, and what iPhone, iPad, Mac, games, and Mac Catalyst ask of a design. For Apple, the principles are tools for weighing competing priorities, not one right way, and each device's viewing distance, inputs, and session length should shape the layout. An app must feel at home wherever it runs, never a straight port from another device. (`design-principles`, `designing-for-ios`, `designing-for-macos`, `designing-for-games`, `mac-catalyst`)

## The eight principles

- **Purpose: focus on the features that matter most, and make them great.** Align them with how people want to use the product, because a product with a clear use is more effective at helping people meet their goals. (`design-principles`)
- **Create value, and find new ways to solve the problem.** At every stage, ask what the product is for and whether the design serves it. Investigate existing solutions instead of re-creating them, and define what sets your product apart. (`design-principles`)
- **Agency: stay out of the way, and make mistakes easy to undo.** Get people straight to the task, never lock them into flows or modes, and let them skip any guided flow. Knowing they can reverse an action frees people to explore. (`design-principles`)
- **Responsibility: act in people's best interest, be transparent from the first interaction, and collect only what the product needs.** Give a clear rationale when asking for permission, say what you collect and how you use it, and anticipate misuse with protections against abuse. (`design-principles`)
- **Familiarity: build on concepts people know, and apply each behavior consistently.** Once an element has a behavior or appearance, keep it everywhere so people learn faster. Give clear feedback, using system patterns for alerts and choices. (`design-principles`)
- **Flexibility: make accessibility a priority from the start, and support as many inputs as possible.** Voice, touch, keyboard, and more let people use the product their way, and every platform you support deserves the same level of care. (`design-principles`)
- **Keep people's context as the design adapts to other platforms and configurations.** Content and controls stay in predictable places, and natural animations smooth the transitions, so the app still feels familiar. (`design-principles`)
- **Simplicity: be clear and direct, and include just what's necessary, which isn't the same as minimalism.** Keep the important things close and let the rest fall away. Choose exactly the words each concept needs, and build hierarchy from recognizable controls and a consistent structure. (`design-principles`)
- **Craft: care about every detail, knowing that shipping isn't the finish line.** Prototype early, discard what doesn't work, test in real-world settings for durability, reliability, and performance, then keep the interface current with the latest platform capabilities. Quality shows in visuals, animation, wording, and audio. (`design-principles`)
- **Delight: make it human, and don't mistake delight for decoration.** It must never block the task people came to do. Name the emotion you want (a fitness app energizes, a meditation app calms) and add character at defining moments, like a button press or an error message. (`design-principles`)
- **Consider the whole: delight is the sum of everything a person experiences in the product.** The freedom to act, the safety to explore, the comfort of familiar metaphors, and the flexibility to change context add up, so design with intent, focus, and care. (`design-principles`)

## iOS and iPadOS (`designing-for-ios`, `designing-for-ipados`)

- **(iOS) Limit onscreen controls, keeping secondary details and actions discoverable with minimal interaction.** It helps people concentrate on primary tasks and content. (`designing-for-ios`)
- **(iOS) Put controls within reach of the hand holding iPhone, and support swiping to go back or act on a row.** The display's middle and bottom are easiest to reach, and people view it from a foot or two away. (`designing-for-ios`)
- **(iOS) With permission, use device capabilities instead of asking people to enter data.** Accept payments, secure the app with biometric authentication, or offer features that use the device's location. (`designing-for-ios`)
- **(iOS, iPadOS) Adapt to orientation, Dark Mode, Dynamic Type, and on iPad multitasking modes.** People choose the configurations that work best for them, and an iPad app should also transition effortlessly to running in macOS. (`designing-for-ios`, `designing-for-ipados`)
- **(iOS, iPadOS) Design for both quick visits and hours-long sessions, with several apps in play.** iPhone sees minute-long check-ins and hour-long sessions with frequent app switching, and iPad sees hours of immersion, several apps onscreen, and drag and drop between them. (`designing-for-ios`, `designing-for-ipados`)
- **(iOS, iPadOS) Build on the system features that help people use the system and their apps in familiar, consistent ways.** On iPhone: widgets, Home Screen quick actions, Spotlight, Shortcuts, and activity views. On iPad: multitasking, widgets, and drag and drop. (`designing-for-ios`, `designing-for-ipados`)
- **(iPadOS) Spend the large display on content, minimizing modal interfaces and full-screen transitions.** Put onscreen controls where they're easy to reach but not in the way. (`designing-for-ipados`)
- **(iPadOS) Size content for viewing distance and input, and support touch, keyboard, trackpad, and Apple Pencil in combination.** People hold iPad, set it down, or stand it up, usually within about 3 feet, and often mix input modes in one session. (`designing-for-ipados`)

## iPhone Duo (`designing-for-iphone-duo`)

- **Follow the system's vertical placement of toolbars, tab bars, and navigation controls.** The outer display is wider and shorter than other iPhones, so bars sit at the side everywhere except the inner display in portrait. (`designing-for-iphone-duo`)
- **Build one layout that resizes instead of a custom layout per pose.** Compact width on the outer display and regular width on the inner cover every pose. Avoid fixed widths and display-specific dependencies, and let the existing layout expand. (`designing-for-iphone-duo`)
- **Keep content out of reserved regions, and adapt to the fold with small adjustments, not rearrangement.** Prefer self-adapting containers, like Notes' split view, and an even number of grid columns. Controls that vanish or jump are harder to find. (`designing-for-iphone-duo`)
- **Keep functionality, state, and control positions consistent across displays and poses.** The same controls stay reachable even when some overflow. Add one hierarchy level on the inner display if it fits: Mail shows list and email side by side when open. (`designing-for-iphone-duo`)
- **When space runs short, keep the toolbar or the tab bar according to the view's job.** In navigation-focused views, toolbar items move into overflow so the tab bar stays, the default. In task-oriented views, minimize the tab bar to keep the task's actions. (`designing-for-iphone-duo`)
- **Order the vertical toolbar by importance: Back or Close first, then prominent actions like Done, then the remaining groups.** Items overflow bottom to top, so prioritize whole groups, then frequent items like Compose in Mail, and keep badged items visible. (`designing-for-iphone-duo`)
- **Give every toolbar item that isn't text-only a title and a symbol, and reserve the ellipsis for the system overflow menu.** The system picks the representation and uses titles in overflow. Move your own overflow actions into the system menu. (`designing-for-iphone-duo`)
- **Group related toolbar items instead of spacing them manually, and keep text-based buttons to a minimum.** Item groups add space automatically and adapt as the available space changes. Labels that include text stay in a horizontal bar, so prefer a symbol wherever one works. (`designing-for-iphone-duo`)
- **Use safe areas for the asymmetric content area, and keep controls next to the content they affect.** Edge controls must not cover content, including another app's controls in Split View. Mail's list controls sit above the leading pane rather than at the side. (`designing-for-iphone-duo`)
- **Let visual, immersive interfaces without scrolling or bars use the full display width.** Calculator does, with nothing conflicting with the Dynamic Island or status bar. Elsewhere, a background image or header can span the width while scrolling content stays inset. (`designing-for-iphone-duo`)
- **Use an arrangement view when the layout already resembles one, and keep navigation outside it.** Side-by-side or stacked views become a split arrangement, layered views an overlay. It lays out content but doesn't navigate. (`designing-for-iphone-duo`)
- **Make games playable in every pose by changing the aspect ratio, not letterboxing.** A game may lock orientation but must fill the screen as the pose changes and keep text and control sizes consistent. If letterboxing is unavoidable, fill the padding with artwork. (`designing-for-iphone-duo`)

## macOS (`designing-for-macos`)

- **Use the large display to show more content in fewer nested levels, with less modality.** Keep density comfortable, since people sit about 1 to 3 feet away, often with extra displays. (`designing-for-macos`)
- **Let people resize, hide, show, and move windows, support full-screen mode, and allow personalization.** Windows should fit each work style and setup. Let people customize toolbars, configure windows, and choose interface colors and fonts. (`designing-for-macos`)
- **Put every command people need in the menu bar.** It's how people get easy access to everything an app can do. (`designing-for-macos`)
- **Support high-precision pointing and keyboard shortcuts.** People expect pixel-perfect selections and edits, shortcuts that speed up actions and allow keyboard-only work, and combinations of keyboard, pointing device, game controls, and Siri. (`designing-for-macos`)
- **Expect sessions from a few minutes to hours of deep concentration, with several apps open.** People expect smooth transitions between active and inactive states as they switch apps. (`designing-for-macos`)

## Games (`designing-for-games`)

- **Let people play as soon as installation completes.** Put as much playable content as possible in a download of 30 minutes or less, fetch the rest in the background, and pick defaults from the device: resolution, paired controllers, accessibility settings. (`designing-for-games`)
- **Teach through play instead of a required tutorial.** Players learn better by discovering mechanics in the game's world, so fold setup into a playable tutorial and keep any written one as a later reference. (`designing-for-games`)
- **Defer permission and rating requests until the moment that needs them.** Integrate a request for sensor or personal data into the scenario that requires it, so people understand why you ask, and ask for a rating only after quality time with the game. (`designing-for-games`)
- **Never set text below each platform's minimum size, and keep buttons at its recommended size.** Text defaults to 17 pt in iOS and iPadOS, 11 pt minimum, and 13 pt in macOS, 10 pt minimum. Buttons default/minimum: iOS, iPadOS 44x44/28x28 pt, macOS 28x28/20x20 pt. (`designing-for-games`)
- **Make the game look at home on every display, with menus that adapt to any aspect ratio.** Prefer resolution-independent art, respect safe areas around rounded corners and camera housings, and lay out menus dynamically for ratios like 16:10, 19.5:9, and 4:3. (`designing-for-games`)
- **Support each platform's default input, and never require a game controller.** Touch on iPhone and iPad, keyboard and mouse or trackpad on Mac. Not every player can use a controller, so offer alternatives like touch controls overlaid on the game. (`designing-for-games`)
- **Make content perceivable by sight, hearing, or touch, and let players personalize it.** Never rely on color alone or ship cutscenes without descriptive subtitles, and let players adjust type size, control mapping, motion intensity, and sound balance. (`designing-for-games`)
- **Support the spectrum of self-identity, and avoid stereotypes.** Offer avatar and name options representing as many human characteristics as possible, check whether enemies are depicted with a certain race, gender, or heritage, and reference real cultures respectfully. (`designing-for-games`)
- **Let players pick up the game on any of their devices.** People often use one iCloud account across several Apple devices, and supporting GameSave lets them save their game state and resume exactly where they left off on another. (`designing-for-games`)
- **Support haptics to help players feel the action, and Spatial Audio to immerse them in the soundscape.** Core Haptics, in iOS, iPadOS, and many game controllers, plays custom patterns, optionally with custom audio, and multichannel audio adapts automatically to the current device. (`designing-for-games`)
- **Use Apple technologies to enable unique gameplay mechanics.** For example, integrate machine learning, or request access to location data and to functionality like the camera and microphone. (`designing-for-games`)

## Mac Catalyst (`mac-catalyst`)

- **Bring an iPad app to the Mac only if its essential features work there.** Strong candidates already support drag and drop, keyboard navigation, multitasking, and multiple scenes. Apps that depend on the gyroscope, rear camera, HealthKit, or ARKit may not suit it. (`mac-catalyst`)
- **Start in the iPad idiom, then switch to the Mac idiom when the app feels at home.** The iPad idiom scales views and text to 77%, so 17 pt body text becomes 13 pt. The Mac idiom renders at 100% with more detail. (`mac-catalyst`)
- **When you adopt the Mac idiom, audit the whole layout.** Text at 100% can look too large, so use text styles instead of fixed sizes, check views and images at full detail, and consider a separate asset catalog for the Mac. (`mac-catalyst`)
- **Replace a tab bar with a split view and sidebar, list its items in the View menu, and add Next and Previous buttons for paging.** A sidebar keeps navigation consistent with iPad, and buttons serve people using a pointer or only the keyboard. (`mac-catalyst`)
- **Use the wider screen and a top-down flow.** Split a single column into several, reflow content side by side as the window resizes, show inspectors instead of popovers, and move key controls from the side and bottom edges into the window toolbar. (`mac-catalyst`)
- **Put every command in the menu bar, and give every object a context menu.** iPad has no persistent menu bar, but Mac users expect all commands there, including those moved to the toolbar, and expect relevant actions on every object. (`mac-catalyst`)
- **Create a macOS app icon, and limit appearance customizations to standard macOS ones.** Mac icons have the lifelike rendering people expect while staying harmonious across platforms, and not every iPadOS control customization exists on the Mac. (`mac-catalyst`)

## Key source articles
`design-principles` · `designing-for-ios` · `designing-for-ipados` · `designing-for-iphone-duo` · `designing-for-macos` · `designing-for-games` · `mac-catalyst`
