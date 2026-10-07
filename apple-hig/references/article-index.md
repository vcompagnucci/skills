# Article index

The 131 pages of Apple's Human Interface Guidelines that apply to iPhone, iPad, and Mac, grouped by the reference file that covers them. Each line gives the slug (cite it as (`slug`); the page is https://developer.apple.com/design/human-interface-guidelines/<slug>), the title, the platforms when a page covers only some of iOS, iPadOS, and macOS, and the page's thesis in one line. Grep for a slug or a keyword instead of reading this file whole.

The other 27 pages are listed at the end: they are left out on purpose (Apple Watch, Apple TV, and Vision Pro pages, and Apple technologies outside this skill's iPhone, iPad, and Mac focus), but `scripts/hig_page.py <slug>` still opens any of them. The HIG's 15 navigation pages only list links, so they aren't counted.

## Principles and platforms (`references/principles-and-platforms.md`)

- `design-principles` — **Design principles** — Great design rests on how people think, feel, and interact, and eight principles (purpose, agency, responsibility, familiarity, flexibility, simplicity, craft, delight) serve as tools for weighing competing priorities, not as one right way.
- `designing-for-games` — **Designing for games** — A game should get people playing the moment it installs and then feel at home on every Apple device: legible text and big-enough buttons per platform, the platform's default input plus alternatives, and settings that let every player tune the experience.
- `designing-for-ios` — **Designing for iOS** — An iOS design should start from how people use iPhone (a medium-size high-resolution display held in one or both hands, short check-ins and long sessions, frequent app switching) and favor few onscreen controls, seamless adaptation, reachable controls, and data the device already has; the page is an overview with four best practices.
- `designing-for-ipados` — **Designing for iPadOS** — An iPad design should spend the large display on content (few modals and full-screen transitions), size that content to viewing distance and input mode, and support touch, keyboard, trackpad, and Apple Pencil in combination; the page is an overview with four best practices.
- `designing-for-iphone-duo` — **Designing for iPhone Duo** — An iPhone Duo app should be one resizable iPhone layout (compact on the outer display, regular on the inner) that keeps the same functionality across displays and poses, works around reserved regions like the fold, and follows the system's vertical placement of toolbars and tab bars; iOS patterns still apply.
- `designing-for-macos` — **Designing for macOS** — A Mac design should put a large display, flexible windows, the menu bar, precise pointing, keyboard shortcuts, and personalization to work for long, multi-app sessions at a desk; the page is an overview with six best practices.
- `mac-catalyst` — **Mac Catalyst** · iPadOS, macOS — A Mac Catalyst app must go beyond an iPad layout in a Mac window: choose the right idiom, then adopt Mac conventions for navigation, layout, toolbars, menus, and the app icon.

## Layout and content views (`references/layout-and-content.md`)

- `boxes` — **Boxes** — Use a box to set apart a small group of related content, and show finer grouping inside it with padding and alignment rather than more boxes.
- `collections` — **Collections** — Present image-based content in the standard row or grid layout, keep every item easy to reach, and make changes to the collection easy to follow.
- `column-views` — **Column views** · macOS — Use a column view to let people move back and forth through a deep hierarchy one level per column, starting from the root and with columns they can resize.
- `disclosure-controls` — **Disclosure controls** — Hide details behind a disclosure control until they're relevant, keeping the most-used controls always visible and making clear what each control reveals.
- `image-views` — **Image views** — Use an image view only to display an image: make clickable images with buttons, show icons with symbols, and keep any text laid over an image legible.
- `labels` — **Labels** — Use a label for small amounts of read-only text, set it in system fonts and the system label colors so importance reads at a glance, and let people copy anything useful.
- `layout` — **Layout** — Structure a layout by importance and reading order, keep controls visually distinct from content, and adapt to the space actually available (size classes, safe areas, text size) without changing what the app can do.
- `lists-and-tables` — **Lists and tables** — Use lists and tables to make text easy to scan: keep rows succinct, give selection feedback that matches what selecting does, and pick styles and row controls that fit the data and the platform.
- `outline-views` — **Outline views** · macOS — Use an outline view for hierarchical, text-based data, with the hierarchy in the first column only, columns people can sort and resize, and expansion state that's easy to change and gets remembered.
- `scroll-views` — **Scroll views** — Keep scrolling predictable and discoverable: support the system's gestures, signal when there's more content, avoid nesting same-axis scroll views, and add a scroll edge effect only to keep floating controls distinct.
- `split-views` — **Split views** — Use a split view to show several levels of an app's hierarchy side by side, keep each pane's selection visible so people stay oriented, and use it only where there's horizontal room for every pane to stay legible.
- `tab-views` — **Tab views** · macOS — Use a tab view to switch among a few closely related, self-contained panes in one area, each with a descriptive tab label, and keep it to six tabs at most.
- `text-views` — **Text views** — Reserve text views for text that is long, editable, or specially formatted, and keep that text legible and, when it's useful, selectable.
- `web-views` — **Web views** — Use a web view to let people see web content briefly without leaving your app, add forward and back navigation when they'll visit several pages, and never use it to rebuild a browser.

## Navigation and search (`references/navigation-and-search.md`)

- `page-controls` — **Page controls** · iOS, iPadOS — A page control shows position in an ordered, flat list of peer pages, so keep it centered at the bottom, under about 10 dots, and visually plain, with at most one special indicator.
- `path-controls` — **Path controls** · macOS — A path control shows where a selected file or folder sits in the file system, and it belongs in the window body, never in a toolbar or status bar; the page has one rule plus a description of the two styles.
- `search-fields` — **Search fields** — Make search feel immediate (placeholder text, results while typing, suggestions, the most relevant results first) and place its entry point where it fits the app's layout and the scope it covers.
- `searching` — **Searching** — Make search easy to find and predictable: one prominent location with a clearly shown scope and helpful suggestions, plus Spotlight indexing so people can find your content without opening your app.
- `sidebars` — **Sidebars** — Use a sidebar to navigate an app's top-level areas only when there's room for it, keep it to two levels, let people customize and hide it (never hidden by default), and extend rich content beneath it.
- `tab-bars` — **Tab bars** — A tab bar is for navigating between an app's top-level sections, so keep it visible and stable (no hidden or disabled tabs, no overflow), use few tabs with short labels and familiar icons, and never put actions in it.
- `toolbars` — **Toolbars** — A toolbar should give quick access to the commands, navigation, and search people use most, so choose items deliberately, label them with clear borderless symbols, group them in a few familiar sections, and let content (not custom backgrounds) set its look.

## Presentation, modality, and windows (`references/presentation-and-windows.md`)

- `action-sheets` — **Action sheets** — Use an action sheet, sparingly, to offer choices about an action people just initiated (not an alert, not a menu), with a one-line title, destructive choices on top, and a Cancel button when data is at risk.
- `alerts` — **Alerts** — Interrupt people with an alert only for critical, actionable information, and make its title and buttons say exactly what happened and what each choice will do.
- `going-full-screen` — **Going full screen** — Offer full-screen mode for games, media, and deep tasks, keep essential controls reachable while content takes over, and leave people in control of entering, exiting, and resuming.
- `modality` — **Modality** — Use modality only when it clearly helps people focus or decide, and then keep each modal task short, single-path, clearly named, easy to dismiss, and never stacked on another.
- `multitasking` — **Multitasking** — Every app must survive being switched away from at any moment: save and restore context, pause what needs attention, finish started work in the background, and leave the system's multitasking behavior untouched.
- `panels` — **Panels** · macOS — Use a macOS panel to float quick, selection-related controls above your windows, keep it small, titled, and out of the way, and reserve the dark HUD style for media apps where a standard panel would obstruct content.
- `popovers` — **Popovers** — Use a popover for a small, transient task tied to the control that revealed it: one at a time, sized to its content, not for warnings, and always saving work when it closes on its own.
- `sheets` — **Sheets** — Use a sheet for a scoped task closely tied to the current context, show one at a time, always give people a way out besides Done, and move complex flows or supplementary tools to a full-screen view, window, or panel.
- `windows` — **Windows** · iPadOS, macOS — Use system-provided windows that adapt fluidly to any size, open new ones only when they help people multitask or keep context, and in visionOS keep the glass window for familiar UI and a volume for rich 3D content.

## Buttons and menus (`references/buttons-and-menus.md`)

- `buttons` — **Buttons** — A button should be instantly recognizable and easy to hit: generous hit region, a press state, one prominent style for the likeliest action, and a role that never makes a destructive action the default.
- `context-menus` — **Context menus** — Put only the few commands most relevant to an item in a context menu, keep it short and consistently available, and never make it the only path to a command, because it's hidden by default.
- `dock-menus` — **Dock menus** · macOS — A Dock menu should hold a few high-value shortcuts (open windows, actions useful when the app isn't frontmost) that people can also reach elsewhere in the app.
- `home-screen-quick-actions` — **Home Screen quick actions** · iOS, iPadOS — Offer up to four predictable, high-value quick actions on the app icon, each with a short title that says what happens and a monochrome symbol, never an emoji.
- `menus` — **Menus** — Menus work because people already know them, so keep them familiar: succinct verb labels, important items first, related items grouped, few and shallow submenus, and icons only where they clearly help.
- `pop-up-buttons` — **Pop-up buttons** — Use a pop-up button for one choice from a flat list of mutually exclusive options, with a sensible default and a label that lets people predict the options without opening it.
- `pull-down-buttons` — **Pull-down buttons** — Use a pull-down button to offer at least three commands directly related to the button's action, never to hide a view's primary actions, and confirm any destructive item before it runs.
- `the-menu-bar` — **The menu bar** · iPadOS, macOS — Give the menu bar the standard menus in the standard order, list every command there (custom ones included), disable rather than hide what's unavailable, and treat menu bar extras as optional conveniences people control.

## Editing, files, and sharing (`references/editing-files-and-sharing.md`)

- `activity-views` — **Activity views** · iOS, iPadOS — Open the activity view (share sheet) from the Share button, offer only relevant, non-duplicate activities with short verb titles, and keep share and action extensions quick, familiar, and free of extra modal views.
- `collaboration-and-sharing` — **Collaboration and sharing** — Build sharing and collaboration on the system's sharing interfaces and Messages, with a convenient Share button, a succinct permission summary over few options, a prominent Collaboration button, and only essential custom actions.
- `drag-and-drop` — **Drag and drop** — Support drag and drop wherever people might try it, make its move-or-copy result predictable and reversible, and give clear, continuous feedback from the first few points of movement to the final drop.
- `edit-menus` — **Edit menus** — Use the system edit menu, revealed by the interactions people already know, and show only the commands that apply to the current selection, relying on undo and redo instead of confirmation.
- `file-management` — **File management** — Let people create, open, save, and preview documents through the conventions they already know (menus, the platform's file system, automatic saving, Quick Look), and customize only where it clearly helps.
- `printing` — **Printing** — Put printing where people expect it, offer it only when it can work, and present only relevant options through the system views, adding app-specific extras in their own macOS print panel category.
- `undo-and-redo` — **Undo and redo** — Make undo predictable and visible: say what will be reversed, show the result even offscreen, allow many and batched undos, and use the standard menus, shortcuts, and gestures people already know.

## Controls and data entry (`references/controls-and-data-entry.md`)

- `color-wells` — **Color wells** — Use a color well to let people change the color of onscreen elements, and prefer the system color picker it opens so the experience stays familiar and saved colors work across apps.
- `combo-boxes` — **Combo boxes** · macOS — A combo box pairs free text entry with a list of the most likely choices, so give it a meaningful default from that list, an introductory label, and list items no wider than the field.
- `entering-data` — **Entering data** — Minimize what people have to type: gather data from the system, offer choices, drag, and paste, say clearly what you need, and validate entries as people make them.
- `image-wells` — **Image wells** · macOS — An image well is an editable image view, so restore its default image when a required image is cleared and support the standard copy and paste commands people expect.
- `pickers` — **Pickers** — Use a picker for medium-to-long lists of predictable, logically ordered values, show it in context near the field being edited, and choose the date picker style that fits the space and the task.
- `segmented-controls` — **Segmented controls** — Use a segmented control to group a few closely related choices or actions that affect an object, state, or view, with equal-width segments, one kind of content, and one consistent behavior per control.
- `sliders` — **Sliders** — A slider sets a value between a minimum and a maximum, so keep its direction familiar, customize it only to clarify meaning, and add a text field, stepper, or tick marks when people need exact values.
- `steppers` — **Steppers** — A stepper changes a value it doesn't display, so make the affected value obvious and add a text field (or, in macOS, Shift-click) when people need large changes.
- `text-fields` — **Text fields** — Use a text field only for small, specific input, and fit its label, size, validation timing, and keyboard to exactly what people are expected to type.
- `toggles` — **Toggles** — Use a toggle only to flip a state between two opposing values, make each state obvious without relying on color, and pick the style by context: a switch in an iOS list row, a toggle-like button elsewhere, checkboxes and radio buttons for macOS hierarchies and exclusive choices.
- `token-fields` — **Token fields** · macOS — A token field turns typed text into tokens people can select and manipulate, so make each token useful (a context menu), easy to create (more shortcuts than the comma), and suggested without distracting people mid-typing.
- `virtual-keyboards` — **Virtual keyboards** · iOS, iPadOS — Match the virtual keyboard to the content being edited, keep it from hiding your interface, and replace it (an in-app input view or a systemwide custom keyboard) only when people clearly understand the benefit.

## Color, type, materials, and images (`references/visual-design.md`)

- `branding` — **Branding** — An app should express its brand through voice, a judiciously used accent color, and familiar components while always deferring to content: no logo on every screen, no branded launch screen, and brand color kept off most controls.
- `color` — **Color** — Color should be used judiciously and consistently, never as the only carrier of meaning, defined for light, dark, and increased contrast, and applied sparingly to Liquid Glass, where it belongs on the background of the one primary action.
- `dark-mode` — **Dark Mode** — Apps should respect the systemwide Dark Mode choice instead of offering their own, and stay legible in both appearances through adaptive semantic colors, sufficient contrast, and icons and images tuned for each appearance.
- `images` — **Images** — Artwork looks right everywhere only if you ship each bitmap at every scale factor your devices need (vectors where the system scales freely), check it on real hardware, and keep tvOS and visionOS depth effects subtle and comfortable.
- `materials` — **Materials** — Use Liquid Glass sparingly as a floating functional layer for controls and navigation, never in the content layer, and give the content layer structure with standard materials and vibrant colors chosen by meaning, not by look.
- `typography` — **Typography** — Choose type for legibility first (platform default and minimum sizes, no light weights, few typefaces), express hierarchy through the system text styles, and let text scale with Dynamic Type without losing hierarchy or content.

## Icons and symbols (`references/icons-and-symbols.md`)

- `app-icons` — **App icons** — An app icon should express one simple, memorable concept in layers the system can mask and light, stay consistent across platforms and appearances, and leave shape, highlights, shadows, and blur to the system.
- `icons` — **Icons** — An interface icon should express a single concept through a simple, familiar metaphor, match the other icons and nearby text in size, weight, and perspective, sit optically centered, scale as a vector, and carry a label for VoiceOver.
- `sf-symbols` — **SF Symbols** — Use SF Symbols as interface icons that match the system font in weight and scale, choose rendering modes, variants, and animations for what they mean (change, state, feedback), and build custom symbols from the templates so they stay consistent and accessible.

## Feedback, status, and data display (`references/feedback-and-status.md`)

- `activity-rings` — **Activity rings** · iOS, iPadOS — Treat Activity rings as a fixed system element for one person's Move, Exercise, and Stand progress: show them where they're relevant, never alter their look, and never repurpose them for other data, decoration, or branding.
- `charting-data` — **Charting data** — Use a chart only when it helps people learn something from data, and then keep it simple, familiar, explained with descriptive text, accessible, and consistent with related charts.
- `charts` — **Charts** — Build each chart to communicate a few key points: pick marks and axes that fit what the data means, keep the data most prominent with familiar, well-described context, and make every chart fully accessible and readable without interaction.
- `feedback` — **Feedback** — Match how feedback is delivered to how significant it is, from passive status shown in place to interruptions reserved for critical problems, and deliver it through several channels so everyone receives it.
- `gauges` — **Gauges** — A gauge shows where a value sits within a range, so label the value and both endpoints and use color to make the range's meaning readable at a glance.
- `launching` — **Launching** — Make launch feel instant: a launch screen (where required) that mimics the first screen and never advertises, branding saved for a splash screen in onboarding, and the previous state restored so people continue where they left off.
- `loading` — **Loading** — Make loading finish before people notice it: show something immediately, load in the background while people do other things, and when a wait is unavoidable, show progress or something worth looking at.
- `progress-indicators` — **Progress indicators** — A progress indicator must prove the app isn't stalled: prefer an honest determinate indicator that keeps moving in a consistent place, and let people stop the work when that's safe.
- `rating-indicators` — **Rating indicators** · macOS — A macOS rating indicator shows a ranking as whole, evenly spaced symbols; let people change the rank right where it appears and keep the symbol recognizable as a rating.
- `status-bars` — **Status bars** · iOS, iPadOS — Keep the status bar readable and available: obscure the content beneath it, hide it only temporarily for full-screen media, and let people bring it back with a simple gesture.

## Onboarding, help, settings, and writing (`references/onboarding-help-and-writing.md`)

- `offering-help` — **Offering help** — Offer help only in context and in proportion to the task: inline help or tips for simple features, a tutorial for complex goals, and tooltips that explain one control, never padding that explains standard components.
- `onboarding` — **Onboarding** — Let people learn by doing: if onboarding is needed at all, make it fast, fun, optional, and interactive, and defer setup, downloads, and requests that stand between people and the experience.
- `ratings-and-reviews` — **Ratings and reviews** — Earn ratings with a great overall experience, then ask at the right moment: after real engagement, at a natural break, rarely, and through the system prompt.
- `settings` — **Settings** — Make settings nearly unnecessary: strong defaults, few options, nothing you could detect, no copies of system settings, task options kept inside the task, and only general, rarely changed choices in a settings area.
- `writing` — **Writing** — Treat the words as part of the user experience: write in one consistent voice, tune the tone to the moment, and keep every label, error, and empty state clear, action-oriented, and consistent.

## Accessibility and inclusion (`references/accessibility-and-inclusion.md`)

- `accessibility` — **Accessibility** — An accessible interface is intuitive, perceivable, and adaptable, so Apple asks for enlargeable text, sufficient contrast, information that never depends on color or audio alone, controls big and far enough apart, alternatives to every gesture, and respect for system settings like Reduce Motion.
- `inclusion` — **Inclusion** — Inclusive design puts people first: write plainly and respectfully, portray human diversity without stereotypes or built-in assumptions, and make every experience accessible, because an inoffensive app is not automatically an inclusive one.
- `right-to-left` — **Right to left** — Mirror the interface for right-to-left languages wherever direction carries meaning (alignment, progress, navigation, ordered items, motion), and leave alone what has no reading direction: a number's digits, photos, logos, universal marks, and real-world objects.
- `voiceover` — **VoiceOver** — Make the interface fully usable by ear: give every meaningful element and image a descriptive label (and decorative images none), expose structure through titles, headings, grouping, and the rotor, and announce changes so people's mental map of the content stays accurate.

## Motion, sound, haptics, and media (`references/motion-and-media.md`)

- `live-photos` — **Live Photos** — Treat a Live Photo as one intact thing in every app: edit and share it whole, fall back to a still where it isn't supported, and identify it with motion or the system badge, never with a play button.
- `live-viewing-apps` — **Live-viewing apps** — Put live content first: one tap (or none) to play, unmistakably marked as live, with instant feedback, consistent actions, and a program guide and cloud DVR that never pull people away from what they're watching.
- `motion` — **Motion** — Use motion only when it serves people: brief, realistic, cancelable, and never the sole carrier of information; in visionOS, keep it from making people feel that they or their surroundings are moving.
- `photo-editing` — **Photo editing** — A photo-editing extension runs inside the Photos app's own modal editor, so protect people's work (confirm before canceling, show a preview), rely on the host toolbar instead of adding one, and identify the extension with your app icon.
- `playing-audio` — **Playing audio** — Make your sound behave the way people already control sound: respect silent mode, the system volume, and the output they choose, pick an audio category that doesn't stop other audio needlessly, and never rely on sound alone.
- `playing-haptics` — **Playing haptics** — Make every haptic mean something: use system patterns only for their documented meanings, tie each haptic to a clear cause in harmony with visuals and sound, play them sparingly, and let people turn them off.
- `playing-video` — **Playing video** — Use the system video player and keep everything else out of the content's way: original aspect ratio, the controls people expect on every input, no barriers or prompts before playback, and comfort-first immersion in visionOS.

## Inputs (`references/inputs.md`)

- `action-button` — **Action button** · iOS — Map the Action button to a few essential functions people use regularly, labeled with short verbs, that run without pulling people out of context and, on Apple Watch, extend naturally through later presses.
- `apple-pencil-and-scribble` — **Apple Pencil and Scribble** · iPadOS — Make Apple Pencil behave like a real pen on paper: mark on contact, respond to how it's held, preview on hover without acting, keep accidental gestures harmless, and let Scribble take handwriting anywhere text belongs.
- `camera-control` — **Camera Control** · iOS — Use the Camera Control overlay to put a few clearly labeled camera adjustments under people's finger, keep the viewfinder large and uncluttered around it, and let people launch your camera from anywhere.
- `focus-and-selection` — **Focus and selection** · iPadOS, macOS — Let focus show people exactly where their next interaction lands: use the platform's own focus effects, move focus only when people do, and make focusable exactly what that platform's people expect to reach.
- `game-controls` — **Game controls** — Make game controls feel native to however people play: always support the platform's default input, keep touch controls few, large, and where thumbs expect them, and label controller and keyboard input the way players' own hardware does.
- `gestures` — **Gestures** — Make gestures behave the way people already expect on each platform: standard gestures for standard actions, immediate feedback, custom gestures only when necessary and never as the only way, and nothing that collides with system gestures or demands a particular body.
- `gyro-and-accelerometer` — **Gyroscope and accelerometer** — Use device motion only when it gives people a tangible benefit, explain why when you ask for access, and keep it out of interface manipulation outside gameplay (beyond that, the page points to the motion framework).
- `keyboards` — **Keyboards** — Keep keyboard input predictable: support Full Keyboard Access, never repurpose the standard shortcuts people already know, and add only a few custom shortcuts, built on Command and written the standard way.
- `nearby-interactions` — **Nearby interactions** · iOS, iPadOS — Build nearby interactions on people's physical sense of the world: let proximity and direction drive continuous, multisensory feedback, design around the sensor's limits, and always offer another way to do the task.
- `pointing-devices` — **Pointing devices** — Make the pointer a consistent, precise addition to touch, eyes, and keyboard: respect systemwide gestures, prefer the system's pointer shapes and content effects over decorative ones, and pad hit regions so targets are easy to reach and easy to leave.

## Widgets, notifications, and system experiences (`references/system-experiences.md`)

- `always-on` — **Always On** · iOS — Design the Always On state as a dimmed, quiet, private glance: redact sensitive data, keep only what matters legible, and change the layout as rarely and as gently as possible.
- `app-clips` — **App Clips** · iOS, iPadOS — Make an App Clip an instant, native, complete slice of your app (no splash, no ads, no account wall, no install nagging), and treat App Clip Codes as precise artifacts: generated, unmodified, and sized, placed, and printed for reliable scanning.
- `app-shortcuts` — **App Shortcuts** · iOS, iPadOS — Expose your app's most common tasks systemwide as App Shortcuts (or through app schemas for common domains), with brief memorable phrases, at most one predictable parameter, and responses that still work by voice alone.
- `controls` — **Controls** — A control gives quick access to one app feature from Control Center, the Lock Screen, or the Action button, so its symbol must carry the meaning on its own, its state must stay accurate, and a locked device must not expose what it controls.
- `imessage-apps-and-stickers` — **iMessage apps and stickers** · iOS, iPadOS — An iMessage app serves people in the middle of a conversation, so offer one focused experience with its essentials in the compact view, and make stickers legible anywhere, described for VoiceOver, and built at one size per pack.
- `live-activities` — **Live Activities** — A Live Activity tracks one bounded task or event at a glance, so design all four presentations (compact, minimal, expanded, Lock Screen) to show only essential, current information, and start, update, alert, and end it exactly when people expect.
- `managing-notifications` — **Managing notifications** — Keep people's permission to notify them by representing each notification's urgency honestly: pick the right interruption level, reserve Time Sensitive for the moment, and send marketing only after explicit opt-in.
- `notifications` — **Notifications** — Send only timely, high-value notifications people can understand at a glance: one per event, never instructions or errors, nothing sensitive, with useful actions and a badge that counts only unread notifications.
- `siri` — **Siri** — Siri knows only what an app exposes (intents, entities, schemas), so expose your most relevant actions and content in familiar words, rely on built-in responses, and keep any custom dialogue clear, succinct, voice-ready, inclusive, ad-free, and respectful of Siri's name and reserved phrases.
- `snippets` — **Snippets** — A snippet answers an action taken through Siri, Spotlight, or the Shortcuts app with a compact view, so keep it short, legible, visually self-explanatory, and labeled with the specific action it confirms.
- `widgets` — **Widgets** — Make a widget a glanceable, timely slice of your app's main purpose that stays legible and meaningful in every size, context, and system appearance, and leave complexity to the app.

## Privacy and accounts (`references/privacy-and-accounts.md`)

- `id-verifier` — **ID Verifier** · iOS — Verify mobile IDs in person by asking for the minimum data, keeping it inside system UI unless the law requires you to store it, and starting the check from a plainly labeled button.
- `managing-accounts` — **Managing accounts** — Require an account only when core functionality needs it, make signing in late, clearly labeled, and password-free where possible, and make deleting an account as clear and easy as creating one.
- `privacy` — **Privacy** — Ask only for the data a feature needs, when it needs it, with a specific purpose string and no manipulation around the system alert, and protect what people share with system security features.
- `sign-in-with-apple` — **Sign in with Apple** — Keep Sign in with Apple the fast, private path it promises: ask for sign-in late and only in exchange for value, collect the minimum data (no passwords, respect relay addresses), and show a button that is prominent, high-contrast, and instantly recognizable, whether system-provided or custom.

## AI and machine learning (`references/ai-and-machine-learning.md`)

- `generative-ai` — **Generative AI** — Use generative AI only where it adds clear value, and design it responsibly: keep people in control, be transparent about AI and its limits, protect privacy, and plan for errors, latency, misuse, and models that keep changing.
- `machine-learning` — **Machine learning** — Because an ML feature's behavior comes from data, design how it learns and fails: place it on five axes (critical or complementary, private or public, proactive or reactive, visible or invisible, dynamic or static), raise the accuracy bar with the stakes, and keep trust through feedback, corrections, confidence, attribution, and stated limitations.

## Apple services and frameworks (`references/apple-services.md`)

- `apple-in-app-purchase` — **Apple In-App Purchase** — Sell digital goods through a store that feels like part of your app: let people try before they pay, show total prices and complete subscription terms, keep the system purchase and refund flows intact, and make canceling as easy as subscribing.
- `apple-pay` — **Apple Pay** — Make Apple Pay the fast, prominent default wherever it's supported, keep the payment sheet lean and honest (only essential fields, clear line items, the real merchant name), collect everything else before it, and use Apple's buttons, mark, and name exactly as provided.
- `icloud` — **iCloud** — iCloud should be invisible: content and app state sync automatically, with no per-document decisions or availability alerts, while the app respects people's paid storage and handles deletion and version conflicts with care.
- `maps` — **Maps** — Keep maps interactive and legible: reveal detail as people zoom, never permanently hide the Apple logo and legal link, style annotations and indoor maps as part of your own app rather than a copy of Apple Maps, and choose place cards that fit the map without duplicating it.
- `wallet` — **Wallet** — Put passes, orders, and ID verification in Wallet at the moment people need them: add passes in one tap and keep them current without nagging, design clean passes that work on every device, keep order tracking immediate and accurate, and ask for identity data only when, and only as much as, a transaction requires.

## Not in this skill (open with the script)

- `complications` — **Complications** — Apple Watch, Apple TV, or Vision Pro only.
- `designing-for-tvos` — **Designing for tvOS** — Apple Watch, Apple TV, or Vision Pro only.
- `designing-for-visionos` — **Designing for visionOS** — Apple Watch, Apple TV, or Vision Pro only.
- `designing-for-watchos` — **Designing for watchOS** — Apple Watch, Apple TV, or Vision Pro only.
- `digit-entry-views` — **Digit entry views** — Apple Watch, Apple TV, or Vision Pro only.
- `digital-crown` — **Digital Crown** — Apple Watch, Apple TV, or Vision Pro only.
- `eyes` — **Eyes** — Apple Watch, Apple TV, or Vision Pro only.
- `immersive-experiences` — **Immersive experiences** — Apple Watch, Apple TV, or Vision Pro only.
- `lockups` — **Lockups** — Apple Watch, Apple TV, or Vision Pro only.
- `ornaments` — **Ornaments** — Apple Watch, Apple TV, or Vision Pro only.
- `remotes` — **Remotes** — Apple Watch, Apple TV, or Vision Pro only.
- `spatial-layout` — **Spatial layout** — Apple Watch, Apple TV, or Vision Pro only.
- `top-shelf` — **Top Shelf** — Apple Watch, Apple TV, or Vision Pro only.
- `watch-faces` — **Watch faces** — Apple Watch, Apple TV, or Vision Pro only.
- `airplay` — **AirPlay** — Apple technology left out of this skill.
- `augmented-reality` — **Augmented reality** — Apple technology left out of this skill.
- `carekit` — **CareKit** — Apple technology left out of this skill.
- `carplay` — **CarPlay** — Apple technology left out of this skill.
- `game-center` — **Game Center** — Apple technology left out of this skill.
- `healthkit` — **HealthKit** — Apple technology left out of this skill.
- `homekit` — **HomeKit** — Apple technology left out of this skill.
- `nfc` — **NFC** — Apple technology left out of this skill.
- `researchkit` — **ResearchKit** — Apple technology left out of this skill.
- `shareplay` — **SharePlay** — Apple technology left out of this skill.
- `shazamkit` — **ShazamKit** — Apple technology left out of this skill.
- `tap-to-pay-on-iphone` — **Tap to Pay on iPhone** — Apple technology left out of this skill.
- `workouts` — **Workouts** — Apple technology left out of this skill.
