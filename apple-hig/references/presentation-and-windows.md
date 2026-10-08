# Presentation, modality, and windows

How an app interrupts people, presents a focused task, and manages its windows. Apple says to present modally only when it clearly helps, keep each modal task short with an obvious way out, show one sheet, popover, or alert at a time, and let people control windows, full screen, and switching away without losing their place. (`modality`, `sheets`, `alerts`, `windows`, `multitasking`)

**Contents:** Choosing the presentation · Modality · Sheets · Alerts and action sheets · Popovers · Windows · Panels · Going full screen and multitasking · Key source articles

## Choosing the presentation

- **Pick the modal view by its job: an alert for critical information, an action sheet for choices about people's latest action, and a sheet or popover for a distinct, narrowly scoped task.** In iPadOS and macOS a separate window can also host the task, and a full-screen modal view suits viewing media or a multistep task. (`modality`)
- **Use alerts sparingly, and never an alert merely to inform.** An alert interrupts the current task, so information people can't act on belongs in context, like Mail's indicator when a server is unavailable. (`alerts`)
- **Don't use a popover to show a warning.** People can miss a popover or close it by accident, so a warning belongs in an alert. (`popovers`)
- **Offer choices about an action people initiated in an action sheet, not an alert or, in iOS and iPadOS, a menu.** An alert is usually unexpected and offers no extra choices, while canceling a Mail draft brings choices like deleting or saving it. People expect a menu only when they choose to reveal it. (`action-sheets`, `alerts`)
- **Use a sheet for a scoped task closely related to the current context.** A sheet can request specific information or present a simple task people complete before returning to the parent view, like attaching a file or choosing where to save it. (`sheets`)
- **For supplementary items that affect the main task, use a nonmodal view: a panel in macOS, a nonmodal sheet in iOS and iPadOS.** People keep working in the parent view, as Notes keeps a nonmodal sheet open to format text while people edit. Without panels, iOS and iPadOS can also show supplementary content in a modal view. (`sheets`, `panels`)
- **Use a popover to expose a small amount of information or functionality, limited to a few related tasks.** It disappears after people interact with it, like a calendar event popover after a time change. (`popovers`)
- **Consider a popover when you want more room for content.** Sidebars and panels take up a lot of space, so content people need only temporarily can go in a popover instead. (`popovers`)
- **(macOS) Use a panel for an inspector, and a regular window for an Info window.** An inspector updates as the selection changes, while an Info window keeps the same contents. Depending on the layout, a split view pane can also hold an inspector. (`panels`)

## Modality (`modality`)

- **Present content modally only when there's a clear benefit.** A modal view takes people out of their context and needs an action to dismiss, so use it only to help people focus or make choices that affect their content or device. (`modality`)
- **Keep a modal task short and simple, never an app within your app.** People can lose track of the task they suspended, and a hierarchy of views makes them forget how to retrace their steps. If subviews are necessary, give one path through them and no button people could mistake for dismiss. (`modality`)
- **Consider a full-screen modal style for in-depth content or a complex task.** Filling a window or the display minimizes distractions, which suits videos, photos, or camera views, and multistep tasks like marking up a document or editing a photo. (`modality`)
- **Always give an obvious way to dismiss a modal view, following platform conventions.** In iOS and iPadOS, people expect a button in the top toolbar or a swipe down, and in macOS a button in the main content view. (`modality`)
- **Confirm before closing a modal view would lose people's content, whether they used a gesture or a button.** Explain the situation and offer ways to resolve it, like an iOS action sheet that includes a save option. (`modality`)
- **Name the modal task with a title, or add text that describes it or gives guidance.** People switch away from their previous context and may not return right away, so naming the task helps them keep their place. (`modality`)
- **Let people dismiss one modal view before presenting another, and never show two alerts at once.** Stacked modal views clutter the app, make it feel scattered, and add cognitive load. Only an alert may appear on top of other modal views. (`modality`)

## Sheets (`sheets`)

- **For complex or prolonged flows, consider alternatives to sheets.** iOS and iPadOS offer a full-screen modal style for videos, photos, camera views, or multistep editing. In macOS, a self-contained task like editing a document suits a separate window, and full screen helps people view media. (`sheets`)
- **Show only one sheet at a time from the main interface.** People expect closing a sheet to return them to the parent view or window, so close the first sheet before showing the next, and reopen it afterward if needed. (`sheets`)
- **Never make Done the only way out: pair it with Cancel or Back, but don't show all three together.** Done alone implies finishing is the only exit. Cancel, or Close, dismisses without saving, Done dismisses after completing or saving, and Back returns a step without dismissing. (`sheets`)
- **(iOS, iPadOS) Put Cancel at the leading edge of the top toolbar and Done at the trailing edge.** In a multistep flow, Back replaces Cancel after the first step, and Done stays inactive until the last step. (`sheets`)
- **(iOS, iPadOS) Let a resizable sheet rest at detents: large for full height, medium for about half.** Sheets support large automatically, adding medium lets a sheet rest at both heights, and medium alone keeps it from expanding fully. Custom detents are also possible. (`sheets`)
- **(iOS) On iPhone, consider the medium detent for progressive disclosure, unless content works better at full height.** A share sheet shows its most relevant items at medium height, while the Messages and Mail compose sheets open only at full height to leave room to write. (`sheets`)
- **(iOS, iPadOS) Include a grabber in a resizable sheet.** This small horizontal indicator at the top edge shows people they can drag to resize, cycles the detents on tap, and works with VoiceOver so people can resize without seeing the screen. (`sheets`)
- **(iOS, iPadOS) Support swiping down to dismiss a sheet.** People expect it instead of tapping a dismiss button. If they start swiping away unsaved changes, let them confirm with an action sheet. (`sheets`)
- **(iPadOS) Prefer the page or form sheet presentation styles.** Each uses a default size and centers the sheet's content over a dimmed background, giving a consistent experience. (`sheets`)
- **(macOS) Present a sheet at a reasonable default size, and support resizing when people need a clearer view.** People don't generally expect to resize sheets, so the default size must suit the content. (`sheets`)
- **(macOS) Let people use other app windows without first dismissing a sheet.** A macOS sheet is always modal, a cardlike view that floats on its parent window and dims it. Opening one brings the parent window, and a document's panels, to the front. (`sheets`)
- **(macOS) Use a panel instead of a sheet when people repeatedly provide input and observe results.** A find and replace panel lets people run replacements one at a time and check each result. (`sheets`)

## Alerts and action sheets (`alerts`, `action-sheets`)

- **Build an alert from a title, optional informative text, and up to three buttons.** In iOS, iPadOS, and macOS an alert can also hold a text field, but include one only when people's input resolves the situation, like a secure field for a password. (`alerts`)
- **Don't alert for common, undoable actions, even destructive ones, or when the app starts.** People delete email on purpose and can undo it, so reserve alerts for uncommon destructive actions that can't be undone. At startup, show cached or placeholder data with a nonintrusive label instead. (`alerts`)
- **Write all alert copy in a direct, neutral, approachable tone.** Alerts often describe problems and serious situations, so never be oblique or accusatory, or mask the severity of the issue. (`alerts`)
- **Title an alert with what happened, in what context, and why, in two lines at most.** Avoid empty titles like "Error" or "Error 329347 occurred". A complete-sentence title takes sentence-style capitalization and ending punctuation, and a fragment takes title-style capitalization and none. (`alerts`)
- **Add a message only if it adds value, and don't use it to explain the buttons.** Keep it short, in complete sentences with sentence-style capitalization. If people need guidance, say "choose" and refer to a button by its exact title, without quotes. (`alerts`)
- **Title alert buttons in one or two words that describe the result, preferring verbs tied to the alert text, like View All, Reply, or Ignore.** Use title-style capitalization without ending punctuation, avoid Yes and No, and always title a canceling button Cancel. (`alerts`)
- **Use OK only in a purely informational alert, never as the default button of one that confirms an action.** OK is ambiguous there, while a specific title like Erase, Convert, Clear, or Delete tells people what they're doing. (`alerts`)
- **Put the likeliest and default buttons on the trailing side of a row or the top of a stack, and Cancel on the leading side or bottom.** That's where people expect each one. (`alerts`)
- **Pair any destructive action with a Cancel button, and never make Cancel the default.** Cancel is a clear, safe way out. To make people read an alert before pressing Return, set no default, and make a lone default button Done, not Cancel. (`alerts`)
- **Use the destructive style only for a destructive action people didn't deliberately choose.** A chosen Empty Trash isn't styled destructive, because it carries out people's intent and Return confirms it quickly, while an action they didn't intend deserves the warning. (`alerts`)
- **Offer quick alternatives to the Cancel button when it makes sense.** People can exit to the Home Screen in iOS and iPadOS, or press Esc or Command-Period on an attached keyboard in iOS, iPadOS, and macOS. (`alerts`)
- **(iOS, iPadOS) Never let an alert or action sheet scroll.** Short titles and brief messages keep large text sizes from forcing a scroll, more buttons take longer to choose from, and scrolling a sheet makes it easy to tap a button by accident. (`alerts`, `action-sheets`)
- **(macOS) Use the caution symbol in alerts sparingly, only for actions that might cause unexpected data loss.** Frequent use dilutes its significance, so skip it for tasks meant to overwrite or remove data, like saving or emptying the trash. (`alerts`)
- **(macOS) Let people suppress a repeating alert, and add an accessory view only when people need more information.** macOS shows your app icon in an alert unless you supply another icon or symbol, and an alert can include a Help button that opens your help documentation. (`alerts`)
- **Use action sheets sparingly.** They give people important information and choices but interrupt the current task, so avoiding unnecessary ones keeps people paying attention to them. (`action-sheets`)
- **Keep an action sheet's title to one line, and add a message only if necessary.** A long title is hard to read quickly and may truncate or need scrolling, and the title with the action's context usually explains the choices. (`action-sheets`)
- **Put destructive choices at the top of an action sheet in the destructive style, and Cancel at the bottom when an action might destroy data.** The top is where choices are most noticeable, and a SwiftUI confirmation dialog includes Cancel by default. (`action-sheets`)

## Popovers (`popovers`)

- **Point a popover's arrow as directly as possible at the element that revealed it.** Ideally the popover covers neither that element nor content people need to see while using it. (`popovers`)
- **Let a popover close when people click or tap outside it or select an item, and add Close, Cancel, or Done only for clarity.** Such a button helps when people can exit with or without saving. If several selections are possible, keep the popover open until people dismiss it. (`popovers`)
- **Always save work when a nonmodal popover closes automatically.** People can dismiss one unintentionally by clicking or tapping outside it, so discard work only when they choose an explicit Cancel button. (`popovers`)
- **Show one popover at a time, and never a cascade or hierarchy of popovers.** Multiple popovers clutter the interface and confuse people, so close the open one before showing another. (`popovers`)
- **Let nothing but an alert appear over a popover, and let people close one popover and open another with a single click or tap.** Avoiding extra gestures matters most when several bar buttons each open a popover. (`popovers`)
- **Make a popover only big enough for its contents and arrow, and animate size changes.** The system can adjust the size to fit, and an unanimated resize between condensed and expanded views looks as if a new popover replaced the old one. (`popovers`)
- **Avoid the word "popover" in help documentation.** Refer to the task or selection instead, like "Select the Show button" rather than "Select the Show button at the bottom of the popover." (`popovers`)
- **(iOS, iPadOS) Reserve popovers for wide views, and use a full-screen modal view like a sheet in compact views.** Adjust the layout to the content area's size class, so compact views use all the available screen space. (`popovers`)
- **(macOS) Consider letting people detach a popover into a panel that looks much like the original.** Dragging a detachable popover turns it into a panel that stays visible while people work with other content, and a similar look helps them keep context. (`popovers`)

## Windows (`windows`)

- **(iPadOS, macOS) Make windows adapt fluidly to different sizes, for multitasking and multiwindow workflows.** iPadOS apps don't control or learn the multitasking configuration people choose, so an app opened in a window must adapt gracefully. (`windows`, `multitasking`)
- **(iPadOS, macOS) Use a primary window for the app's main navigation and content, and an auxiliary window for one task or area.** An auxiliary window doesn't allow navigation to other app areas and typically includes a button people use to close it after the task. (`windows`)
- **(iPadOS, macOS) Open a new window only when it helps people multitask or preserve context.** Mail opens Compose in a new window so the message and existing email stay visible, but excessive windows clutter and confuse, so don't open them by default unless it makes sense. (`windows`)
- **(iPadOS, macOS) Consider offering a way to view content in a new window.** A command in a context menu or the File menu gives people that flexibility without opening windows by default. (`windows`)
- **(iPadOS, macOS) Use system window frames and controls, never custom ones or imitations.** People recognize how system windows look and behave, and anything short of a perfect match makes the app feel broken. (`windows`)
- **(iPadOS, macOS) Call every window a "window" in user-facing text.** The system uses that term for every type, and other terms, including "scene", which refers to window implementation, confuse people. (`windows`)
- **(iPadOS) Design for both window modes people can choose: full screen and windowed.** Full-screen apps fill the screen and people switch with the app switcher, while windowed apps resize freely, overlap, and keep their size and placement even after closing. (`windows`, `multitasking`)
- **(iPadOS) Keep toolbar items clear of the window controls.** A windowed app shows those controls at the toolbar's leading edge, so move leading buttons inward when they appear instead of letting them be hidden. (`windows`)
- **(iPadOS) Consider letting people open content in a new window with a gesture, like pinching a Notes item.** To let people view just one file, you can present it without creating your own window, but the app must support multiple windows. (`windows`)
- **(macOS) Lay out a window as a frame and a body area.** People drag the frame to move a window and often its edges to resize it. The frame, above the body, can hold window controls and a toolbar, and rarely a bottom bar below the body. (`windows`)
- **(macOS) Know the window states: main, key, and inactive.** The main window is the app's frontmost, one per app, and the key window, one onscreen and sometimes a panel, accepts input. Panels like Colors or Fonts become key only when people click their title bar or a field that needs typing. (`windows`)
- **(macOS) Give custom windows the system appearances for each state.** People rely on them to find the foreground window and the one that accepts input: the key window's title bar buttons use color, and inactive windows lose vibrancy and look farther away. (`windows`)
- **(macOS) Keep critical information and actions out of a bottom bar.** People often move windows so the bottom edge is hidden. Use it only for a little information about the window's contents or selection, like the Finder's item count and free space, and an inspector for more. (`windows`)

## Panels (`panels`)

- **(macOS) Use a panel for quick access to important controls or information about the content people are working with.** A panel floats above other windows, less prominent than the main window, and can hold settings for the selected item in the active document. (`panels`)
- **(macOS) Prefer simple adjustment controls in a panel, like sliders and steppers.** They give people direct control, while typing text or selecting items to act on can take several steps. (`panels`)
- **(macOS) Give a panel a brief title, a noun or noun phrase, that describes its purpose.** A panel floats above other windows, so it needs a title bar people can use to position it. Use title-style capitalization, as in Fonts, Colors, or Inspector. (`panels`)
- **(macOS) Refer to a panel by its title, never as a "panel".** Menus say Show Fonts, Show Colors, or Show Inspector, and help can say "Fonts window" when that's clearer than "Fonts". (`panels`)
- **(macOS) Bring all open panels to the front when the app becomes active, and hide them when it's inactive.** This applies whichever window was active when a panel opened. (`panels`)
- **(macOS) Keep panels out of the Window menu's documents list.** Commands that show or hide panels can go in the Window menu, but panels aren't documents or standard app windows. (`panels`)
- **(macOS) Generally don't offer a panel's minimize button.** A panel appears only when needed and disappears when the app is inactive, so people rarely need to minimize it. (`panels`)
- **(macOS) Consider a HUD-style panel, darker and translucent, for highly visual content, like media editing or a full-screen slideshow.** It serves the same function as a standard panel, as QuickTime Player's HUD shows inspector information without obstructing much content. (`panels`)
- **(macOS) Prefer standard panels, using a HUD only in a media app, when a standard panel would obscure essential content, or when you need no controls.** An unexplained HUD distracts or confuses, may not match the appearance setting, and most system controls, except the disclosure triangle, don't match it. (`panels`)
- **(macOS) Keep one panel style when the app switches modes.** If you use a HUD in full-screen mode, keep the HUD style when people leave full-screen mode. (`panels`)
- **(macOS) Keep HUDs small, and use color sparingly in them.** A HUD should be unobtrusively useful, never obscuring or competing with the content it adjusts, and a little high-contrast color usually highlights what's important. (`panels`)

## Going full screen and multitasking (`going-full-screen`, `multitasking`)

- **Support full-screen mode when it helps people concentrate, and adjust the layout without resizing the window programmatically.** Games, videos, photo slideshows, and in-depth tasks benefit. Change proportions, not which items appear, and keep the change subtle to avoid jarring transitions. (`going-full-screen`)
- **Keep essential controls available in full screen, and hide toolbars and navigation controls only temporarily.** People should finish without exiting: playback controls stay visible or easy to reveal, and hidden bars return with a tap, a swipe down, or the pointer at the top. (`going-full-screen`)
- **(iPadOS, macOS) Except in games, let people reveal the Dock in full-screen mode.** People need it to open other apps quickly. A game can ask iPadOS to ignore the first swipe up from the bottom edge, or hide the Dock in macOS, to prevent accidental reveals. (`going-full-screen`)
- **Let people choose when to exit full screen.** They don't expect it to end automatically when they switch to a different experience or finish a game or movie. (`going-full-screen`)
- **(iOS, iPadOS) Keep the familiar one-swipe exit, and require two swipes only if one causes unexpected exits.** The Home Screen indicator hides soon after people switch to the app and reappears when they touch the bottom of the screen. (`going-full-screen`)
- **(macOS) Use the system's full-screen experience, and let people enter it themselves.** It accommodates the camera housing on some Macs. People enter with the window's Enter Full Screen button, the View menu, or Control-Command-F, not a custom menu of window modes, and a game can add its own toggle. (`going-full-screen`)
- **(macOS) In a game, don't change the display mode when players go full screen.** People expect to control their display mode, and changing it automatically doesn't improve performance. (`going-full-screen`)
- **Be ready to save and restore people's context at any moment.** People expect multitasking and may think something is wrong without it, so with rare exceptions, like some games, every app needs to work well with it. (`multitasking`)
- **Pause games, slideshows, and other activities that need attention when people switch away.** When people come back, let them continue as if they never left. (`multitasking`, `going-full-screen`)
- **Respond smoothly to audio interruptions, like a call or a playlist started by Siri.** Pause indefinitely for primary audio, like music, podcasts, or audiobooks. For short ones, like GPS directions, lower the volume or pause, then resume when the interruption ends. (`multitasking`)
- **Finish user-initiated tasks, like a download or video processing, in the background.** People expect work they started to keep going when they switch away. (`multitasking`)
- **Use notifications sparingly: notify when an important or time-sensitive task completes, not a routine one.** A completion notice helps people return for the next step, and routine tasks can wait until people check back. (`multitasking`)
- **(iOS, iPadOS) Expect people to keep a video or FaceTime call going in Picture in Picture while they use your app.** On iPad, people also view several apps' windows at once, and an app can have several windows open. (`multitasking`)
- **(macOS) Don't pause video in one window when people turn to another.** People expect playback they start in one window to continue while they view or work in another. (`multitasking`)

## Key source articles
`sheets` · `alerts` · `modality` · `popovers` · `action-sheets` · `windows` · `multitasking` · `going-full-screen` · `panels`
