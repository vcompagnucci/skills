# Layout and content views

How an app arranges its content and which view holds each kind. Apple's position: put the most important content first, make structure visible through alignment and grouping, adapt to the space actually available without changing what the app can do, and give each view one job (lists and tables for text, collections for images, a label or text view sized to the text). (`layout`, `lists-and-tables`, `collections`, `text-views`)

**Contents:** Choosing the view · Layout · Lists and tables · Outline views and column views · Scroll views · Collections · Split views · Tab views · Labels and text views · Image views and web views · Disclosure controls and boxes · Key source pages

## Choosing the view

- **Show text in a list or table, and many images or items of widely varying size in a collection.** The row-based format makes text easy to scan and read, while collections are ideal for image-based content. (`lists-and-tables`, `collections`)
- **Use lists to express an app's information hierarchy, and a multicolumn table for complex data.** iOS Settings uses a hierarchy of lists, Mail in iPadOS and macOS puts a table in a split view, and productivity apps show attributes in separate, sortable columns. (`lists-and-tables`)
- **(macOS) Show hierarchical data in an outline view, or in a column view when people move back and forth through a deep hierarchy and don't need sorting.** Data that isn't hierarchical belongs in a table, and an iPadOS app presents hierarchical content in a split view. (`outline-views`, `column-views`, `lists-and-tables`)
- **Use a label for a little read-only text, a text field for a little editable text, and a text view for long, editable, or formatted text.** Text views offer the most options for specialized text and text input, so for small amounts a label or text field is simpler. (`labels`, `text-views`)
- **Use an image view only to display an image, and make an interactive image a system button.** Configure the button to show the image instead of adding button behaviors to an image view. (`image-views`)
- **(macOS) Switch among up to six related panes with a tab view, not a pop-up button.** Tabs show every choice and take one click, while a pop-up button takes two and hides them, so save it for more panes. iOS and iPadOS use a segmented control instead. (`tab-views`)

## Layout (`layout`)

- **Put the most important content near the top and leading side.** People usually read top to bottom and leading to trailing, and standard system components adapt that order automatically for right-to-left languages. (`layout`)
- **Align elements to aid scanning, and indent to show hierarchy.** Alignment looks neat and helps people track content as they scroll, and people assume aligned items are related and indented items subordinate to the one they follow. (`layout`)
- **Group related items with negative space, container shapes, or separator lines.** Grouping clearly shows which information and functions are related and which aren't. (`layout`)
- **Use progressive disclosure to keep layouts clean and easy to use.** Too much content and too many choices make information hard to find, so show less at first with disclosure triangles, menus, or nested views, or use scrollable sections, which suit media apps for video, music, or books. (`layout`)
- **Separate controls from content with Liquid Glass and a scroll edge effect, not a solid or semi-opaque background.** The scroll edge effect elevates controls above content. Extend full-screen background content beneath sidebars, toolbars, and tab bars to fill the screen or window. (`layout`)
- **If sidebars or inspectors would cover key parts of a full-window background image, use a background extension effect.** It mirrors the image beneath the adjacent components, flipped and blurred, so the background appears to extend under them. (`layout`)
- **Design a layout that adapts gracefully when people rotate the device, resize a window, add a display, or switch devices.** People expect the experience to stay familiar, so respect system-defined safe areas, margins, and guides, and fine-tune placement with layout modifiers. (`layout`)
- **Plan for every characteristic that changes the layout.** They include size classes, screen sizes, orientations and aspect ratios, the Dynamic Island, external displays, Display Zoom, resizable iPad and Mac windows, text size, and locale features like layout direction and text length. (`layout`)
- **Make the interface resize well even when the app is locked to one orientation.** A landscape-only game still runs across many devices and window sizes. (`layout`)
- **Respect the safe area, and use layout guides for standard margins and readable text widths.** The safe area excludes edges covered by hardware or by views like toolbars, tab bars, and the status bar, so system UI and the Dynamic Island never obstruct content or controls. (`layout`)
- **Adjust the layout for larger text sizes.** Apps that ignore Dynamic Type can be difficult or impossible to use for people who rely on it, so stack side-by-side views vertically, let rows and containers grow, and let single-line rows wrap. (`layout`)
- **Preview the app on multiple devices, size classes, localizations, and text sizes, testing the largest and smallest layouts first.** Device Hub's simulated devices catch clipping and other issues, like a layout resized on iPad or in iPhone Mirroring on Mac. (`layout`)
- **When the display changes, scale background artwork to fill the screen, never changing its aspect ratio.** A new aspect ratio can crop, letterbox, or pillarbox artwork, and very wide or very tall windows may need artwork that extends beyond what a standard display shows. (`layout`)
- **(iOS, iPadOS) Read size classes as the space available: compact or regular in each dimension.** The system sets them by device type, window configuration, and multitasking state, like full screen, Slide Over, or mirrored to a Mac, so apps can appear in every combination. (`layout`)
- **(iOS, iPadOS) Base layouts on size classes, not device type or orientation.** Size classes describe the actual space in portrait or landscape, while the device type says nothing about it. They also adapt the app to free resizing in iPhone Mirroring or iPad multitasking. (`layout`)
- **(iOS, iPadOS) Consider every combination of size classes.** A layout built only for iPhone landscape, regular width and compact height, can waste iPad landscape's vertical space at regular height, and a compact-portrait-only layout leaves extra space at regular width on iPad. (`layout`)
- **(iOS, iPadOS) Keep functionality the same as size classes change, and keep layout changes familiar to the platform.** Change only how much is visible, like switching a tab bar to a sidebar or exposing overflow items in larger spaces. The device type stays the same when people resize. (`layout`)
- **(macOS) Keep controls and critical information away from a window's bottom edge, and content out from behind the camera housing at its top.** People often move windows so the bottom edge sits below the screen. (`layout`)

## Lists and tables (`lists-and-tables`)

- **Let people edit a table when it makes sense, at least to reorder.** People appreciate reordering a list even when they can't add or remove items. In iOS and iPadOS, people enter an edit mode before they can select items. (`lists-and-tables`)
- **Match selection feedback to what selecting does.** A table that navigates a hierarchy keeps the selected row highlighted to show the path people are taking, while a table of options highlights a row only briefly, then adds a checkmark. (`lists-and-tables`)
- **Keep row text succinct, and for long items list only titles that open a detail view.** Short text minimizes truncation and wrapping, so rows stay easy to read and scan instead of growing oversized. (`lists-and-tables`)
- **Keep text readable in narrow or resizable tables, sometimes with an ellipsis in the middle.** A middle ellipsis preserves both the beginning and the end of the text, so items stay recognizable and distinct. (`lists-and-tables`)
- **Give a multicolumn table descriptive column headings: nouns or short noun phrases in title-style capitalization, without ending punctuation.** A single-column table without a heading needs a label or header for context. (`lists-and-tables`)
- **Choose a table or list style that fits the data and platform.** Styles express grouping and hierarchy: the iOS and iPadOS grouped style separates groups with headers, footers, and extra space, and the macOS bordered style alternates row backgrounds to make large tables easier to use. (`lists-and-tables`)
- **Choose a row style that fits the information, like a small image at the leading end followed by a brief label.** Some platforms provide built-in row styles for arranging content in rows, headers, and footers. (`lists-and-tables`)
- **(iOS, iPadOS) Use an info button only to reveal more about a row, and a disclosure indicator to drill into it.** An info button, called a detail disclosure button in a row, doesn't navigate a hierarchical list. (`lists-and-tables`)
- **(iOS, iPadOS) Don't add an index to a table whose rows end in controls like disclosure indicators.** The index, usually the alphabet down the trailing side, lets people jump to a section, and sharing that edge makes them hit one while aiming for the other. (`lists-and-tables`)
- **(macOS) When it adds value, let people sort a table by clicking a column heading.** Clicking a column that's already sorted re-sorts the data in the opposite direction. (`lists-and-tables`)
- **(macOS) Let people resize table columns, and consider alternating row colors in a multicolumn table.** Widths vary, so resizing helps people focus or reveal clipped data, and alternating colors help them track values across a wide table. (`lists-and-tables`)

## Outline views and column views (`outline-views`, `column-views`)

- **(macOS) Use an outline view for text-based hierarchical content, often on the leading side of a split view.** Related content sits on the opposite side, and the Finder uses an outline view to navigate the file system. (`outline-views`)
- **(macOS) Expose an outline view's hierarchy in the first column only.** Parent containers there get disclosure triangles, and other columns show attributes of that data, like sizes and modification dates. (`outline-views`)
- **(macOS) Always give a multicolumn outline view descriptive column headings, without punctuation or a trailing colon.** Use nouns or short noun phrases in title-style capitalization, and give a single-column view without a heading a label or other context. (`outline-views`)
- **(macOS) Consider letting people sort an outline view by clicking a column heading.** Clicking the primary column sorts every hierarchy level, as the Finder sorts top-level folders and then each folder's items, and clicking a sorted column reverses the order. (`outline-views`)
- **(macOS) Let people resize the columns of outline and column views.** Data varies in width, and resizing reveals values wider than the column or item names too long for the default width. (`outline-views`, `column-views`)
- **(macOS) Make nested containers easy to expand and collapse.** Clicking a Finder folder's disclosure triangle expands only that folder, while Option-clicking it expands all its subfolders. (`outline-views`)
- **(macOS) Retain people's expansion choices.** Storing the expanded state lets the outline view reappear as people left it, so they don't navigate back to the same place. (`outline-views`)
- **(macOS) Consider alternating row colors in a multicolumn outline view.** They help people track row values across columns, especially in a wide view. (`outline-views`)
- **(macOS) Let people edit outline view data when it makes sense, with a single click on a cell.** A double click can do something else: a file list can rename on a single click on the name and open the file on a double click. Reordering, adding, and removing rows can help too. (`outline-views`)
- **(macOS) Consider truncating cell text with a centered ellipsis instead of clipping it.** Keeping the beginning and end makes content more distinct and recognizable than clipped text. (`outline-views`)
- **(macOS) Consider a search field for finding values quickly in a lengthy outline view.** Windows built around an outline view often put one in the toolbar. (`outline-views`)
- **(macOS) Structure a column view, also called a browser, as one column per hierarchy level.** A triangle marks parent items, and selecting one shows its children in the next column, as in the Finder's column view. (`column-views`)
- **(macOS) Show the root level in a column view's first column.** People know they can scroll back to it to restart navigation from the top. (`column-views`)
- **(macOS) When the selected item has no children, consider showing information about it.** The Finder shows a preview plus the creation date, modification date, file type, and size. (`column-views`)

## Scroll views (`scroll-views`)

- **Support the default scrolling gestures and keyboard shortcuts.** People expect systemwide scrolling behavior everywhere, so custom scrolling still needs scroll indicators with the expected elastic behavior. (`scroll-views`)
- **Make it apparent when content scrolls, for example with partial content at an edge.** Scroll indicators, which show whether people are near the beginning, middle, or end, aren't always visible. Most people try scrolling, but drawing their attention is considerate. (`scroll-views`)
- **Don't nest scroll views that scroll in the same direction.** It creates an unpredictable interface that's difficult to control, though a horizontal scroll view inside a vertical one is fine. (`scroll-views`)
- **Consider page-by-page scrolling, each page the view's height or width minus an overlap.** People sometimes prefer a fixed amount per interaction, and an overlap like a line of text, a row of glyphs, or part of a picture keeps context. (`scroll-views`)
- **Scroll automatically only to bring relevant hidden content into view, and only as far as necessary.** Reveal a search match or the insertion point when people type, follow the pointer past the edge during a selection, and reveal a selection before acting on it. (`scroll-views`)
- **If you support zoom, set sensible minimum and maximum scale values.** Zooming in on text until a single character fills the screen rarely makes sense. (`scroll-views`)
- **(iOS, iPadOS, macOS) Use a scroll edge effect only where content scrolls behind floating interface elements, one per view.** It isn't decorative and doesn't block or darken like an overlay: it keeps controls distinct. Split-view panes on iPad and Mac can each have one, matched in height. (`scroll-views`)
- **(iOS, iPadOS, macOS) Prefer the automatic scroll edge effect style.** It gives a more opaque separation for top toolbars crowded with controls, text outside Liquid Glass controls, and pinned table headers. Test legibility thoroughly if you use the soft style. (`scroll-views`)
- **(iOS, iPadOS, macOS) Add a scroll edge effect to custom bars when the top layer needs extra clarity.** The effect separates elements like toolbars from the content scrolling behind them, and you can change its style from automatic to hard or soft. (`scroll-views`)
- **(iOS, iPadOS) Consider a page control for a scroll view in page-by-page mode, and then hide the scroll indicator on that axis.** A page control shows how many pages exist and which is visible, as Weather does for saved locations, and two indicators on one axis are redundant. (`scroll-views`)
- **(macOS) Use small or mini scroll bars in a panel when space is tight, with every control in the panel the same size.** Smaller scroll bars help panels coexist with other windows. In macOS, a scroll indicator is called a scroll bar. (`scroll-views`)

## Collections (`collections`)

- **Use the standard row or grid layout whenever possible.** People expect these simple, effective appearances, and a custom layout can confuse them or draw undue attention to itself. (`collections`)
- **Make every item easy to choose, with adequate padding around images.** Hard-to-reach items frustrate people before they get to what they want, and padding keeps focus and hover effects visible and content from overlapping. (`collections`)
- **Add custom gestures only when the app needs them.** By default people tap to select, touch and hold to edit, and swipe to scroll, and you can add more gestures for custom actions. (`collections`)
- **Consider animations as feedback when people insert, delete, or reorder items.** Collections support standard animations for these actions, and custom ones too. (`collections`)
- **(iOS, iPadOS) Make dynamic layout changes sensible and easy to track, and avoid them while people are viewing and using the collection.** Change the layout mid-use only in response to an explicit action. (`collections`)

## Split views (`split-views`)

- **Use a split view to show several levels of hierarchy at once, often with a sidebar in the leading pane.** Selecting an item in the primary pane shows its contents in the secondary pane, and a tertiary pane can show more. Rarely, panes supplement the main view, like Keynote's navigator, notes, and inspector in macOS. (`split-views`)
- **Keep the selection highlighted in every pane that leads to the detail view.** The highlight shows how the panes' contents relate and keeps people oriented. (`split-views`)
- **Consider letting people drag content between panes.** A split view reaches several hierarchy levels, so dragging items to another pane is a convenient way to move content around the app. (`split-views`)
- **(iOS) Prefer a split view in a regular environment, not a compact one.** Panes need horizontal space, and on iPhone in portrait they wrap or truncate content, making it less legible and harder to use. (`split-views`)
- **(iPadOS) Design a split view for narrow, compact, and intermediate window widths.** iPad windows resize fluidly, so navigating between panes must stay logical at every width. A split view can have two vertical panes, like Mail, or three, like Keynote. (`split-views`)
- **(macOS) Set minimum and maximum pane sizes that keep the divider visible.** People drag dividers to resize panes, which can sit vertically, horizontally, or both, and in a pane that's too small the divider seems to disappear. (`split-views`)
- **(macOS) Prefer the thin divider, 1 pt wide.** It maximizes space for content while staying easy to use. Use a thicker one only for a specific need, like table rows with strong lines on both sides. (`split-views`)
- **(macOS) Consider letting people hide a pane when it makes sense.** Hiding panes reduces distractions or makes room for editing, as people hide Keynote's navigator and presenter notes to edit slides. (`split-views`)
- **(macOS) Provide more than one way to reveal a hidden pane.** Offer a toolbar button or a menu command, including a keyboard shortcut, so people can restore it. (`split-views`)

## Tab views (`tab-views`)

- **(macOS) Use a tab view for closely related areas of content.** Its look strongly signals enclosure, so people expect every tab to hold content similar or related to the others. (`tab-views`)
- **(macOS) Keep each pane's controls affecting only that pane.** Panes are mutually exclusive, so each must be fully self-contained. (`tab-views`)
- **(macOS) Label each tab with what its pane contains, usually a noun or short noun phrase in title-style capitalization.** A good label predicts the pane's contents before people click, and a verb phrase can suit some contexts. (`tab-views`)
- **(macOS) Keep a tab view to six tabs at most.** More can overwhelm people and create layout issues, so present more panes another way, like view options in a pop-up button's menu. (`tab-views`)
- **(macOS) Put the tabbed control on the top edge of the content area, or hide it when the app switches panes programmatically.** Without the control, the content area can be borderless, bezeled, or bordered with a line, and a borderless one solid or transparent. (`tab-views`)
- **(macOS) Inset a tab view with a margin of window body on every side.** It looks clean and leaves room for controls unrelated to the tabs. Extending it to the window edges is possible but unusual. (`tab-views`)

## Labels and text views (`labels`, `text-views`)

- **Use labels for the uneditable text in buttons, lists, and views.** A button label says what it does, like Edit or Send, a list label describes an item, often with a symbol or image, and a view label introduces a control or a task. (`labels`)
- **Prefer system fonts in labels, and keep any custom style legible.** Labels show plain or styled text and support Dynamic Type by default. (`labels`)
- **Use the four system label colors to show relative importance.** Label is for primary information, secondary for a subheading or supplemental text, tertiary for an unavailable item or behavior, and quaternary for watermark text. (`labels`)
- **Make useful text selectable.** People need to copy things like an error message, a location, a serial number, or an IP address to use elsewhere. (`labels`, `text-views`)
- **Keep text views legible, adopting Dynamic Type and testing with accessibility options like bold text.** Use multiple fonts, colors, and alignments creatively only while the content stays readable, and Dynamic Type keeps text looking good when people change its size. (`text-views`)
- **Let a text view be any height, scrolling when its content overflows.** By default its text aligns to the leading edge in the system label color. In iOS and iPadOS, an editable text view raises the keyboard when people select it. (`text-views`)
- **(iOS, iPadOS) Show the keyboard type that fits a text view's content.** Each keyboard type facilitates a different kind of input, so the right one streamlines data entry. (`text-views`)

## Image views and web views (`image-views`, `web-views`)

- **Show an icon with an SF Symbol or interface icon instead of an image view.** Symbols are vector images you can render in various colors and opacities, interface icons are bitmaps whose opaque pixels take color, and both can use people's accent colors. (`image-views`)
- **Stretch, scale, size to fit, or pin the image within an image view.** An image view shows one image or an animated sequence, in formats like PNG, JPEG, and PDF, and typically isn't interactive. (`image-views`)
- **Take care when laying text over an image.** Compositing reduces both the image's clarity and the text's legibility, so ensure strong contrast and consider a text shadow or background layer. (`image-views`)
- **Use one size for every image in an animated sequence, ideally prescaled to the view.** Prescaled images need no system scaling, and when the system must scale, images of the same size and shape perform better. (`image-views`)
- **(macOS) Use an image well for an editable image and an image button for a clickable one.** An image well supports copying, pasting, dragging, and clearing with the Delete key, and an image button starts an instantaneous app-specific action. (`image-views`)
- **Use a web view to show web content briefly without leaving the app, never to build a browser.** Safari is the primary way people browse, so replicating it is unnecessary and discouraged. Mail uses a web view to show HTML in messages. (`web-views`)
- **Support forward and back navigation in a web view when people are likely to visit several pages.** It's off by default, so enable it and provide controls for it. (`web-views`)

## Disclosure controls and boxes (`disclosure-controls`, `boxes`)

- **Hide details behind a disclosure control until they're relevant, keeping the most-used controls always visible.** Likely controls at the top of the disclosure hierarchy, with advanced functionality hidden by default, help people find the essentials without being overwhelmed. (`disclosure-controls`)
- **Use a disclosure triangle for content tied to a view or list, and a disclosure button for functionality tied to one control.** Keynote's triangle shows advanced export options and the Finder's progressively reveal folders in list view, while the macOS Save sheet's button expands location options. (`disclosure-controls`)
- **Give a disclosure triangle a label that says what it reveals, like Advanced Options.** The triangle points inward from the leading edge while the content is hidden and down while it's visible. (`disclosure-controls`)
- **Place a disclosure button near the content it reveals, and use at most one per view.** Proximity makes the relationship clear, and several disclosure buttons add complexity and confuse people. The button points down while content is hidden and up while it's visible. (`disclosure-controls`)
- **Keep a box small relative to its containing view.** A box near the size of its window or screen separates grouped content less well and crowds other content. (`boxes`)
- **Show subgroups inside a box with padding and alignment, not nested boxes.** A box's border is a distinct visual element, so nested borders make the interface feel busy and constrained. (`boxes`)
- **Add a succinct introductory title if it helps clarify a box's contents.** The box already signals that its contents are related, a title can explain how, and it helps VoiceOver users predict what's inside. (`boxes`)
- **Write a box title as a brief phrase in sentence-style capitalization, without ending punctuation.** The exception is a box in a settings pane, whose title ends with a colon. (`boxes`)
- **Separate a box's contents with its default border or background color.** iOS and iPadOS use the secondary and tertiary background colors in boxes, and macOS shows a box's title above it. (`boxes`)

## Key source pages
`layout` · `lists-and-tables` · `scroll-views` · `split-views` · `collections` · `labels` · `text-views` · `image-views` · `disclosure-controls` · `outline-views` · `tab-views` · `boxes` · `column-views` · `web-views`
