# Numbers at a glance

The HIG numbers a designer reaches for most on iPhone, iPad, and Mac, grouped by question, each with its page. Full tables (every Dynamic Type size, widget and Live Activity sizes per device, keyboard shortcuts, menu bar items) stay on the pages: open them with `scripts/hig_page.py <slug>`.

## iPhone and iPad vs Mac

| | iOS, iPadOS | macOS |
|---|---|---|
| Control size, default / minimum (pt) | 44x44 / 28x28 | 28x28 / 20x20 |
| Text size, default / minimum (pt) | 17 / 11 | 13 / 10 |
| Body text style, size / leading (pt) | 17 / 22 | 13 / 16 |
| App icon canvas (px) | 1024x1024, masked to a rounded rectangle | 1024x1024, masked to a rounded rectangle |
| Image scale factors | iOS @2x and @3x, iPadOS @2x | @1x and @2x |
| Viewing distance | iPhone a foot or two, iPad about 3 feet | 1 to 3 feet |

Sources: sizes (`accessibility`, `typography`, `designing-for-games`), icon canvas (`app-icons`), scale factors (`images`), distance (`designing-for-ios`, `designing-for-ipados`, `designing-for-macos`).

## Targets and spacing

- **Button hit region:** at least 44x44 pt. (`buttons`)
- **Padding around interactive elements:** about 12 pt around a bezeled element, about 24 pt around the visible edges of one without a bezel. (`accessibility`, `pointing-devices`)
- **Touch controls in games:** 44x44 pt for frequent controls, 28x28 pt for less important ones like menus. (`game-controls`)
- **macOS image button:** about 10 px of padding between the image and the button edges, which define the clickable area. (`buttons`)
- **Drag threshold:** show the drag image once a selection moves about 3 pt. (`drag-and-drop`)

## Type

- **iOS, iPadOS text styles at the default Large size (size/leading, pt):** Large Title 34/41, Title 1 28/34, Title 2 22/28, Title 3 20/25, Headline 17/22 semibold, Body 17/22, Callout 16/21, Subhead 15/20, Footnote 13/18, Caption 1 12/16, Caption 2 11/13. (`typography`)
- **macOS text styles (size/line height, pt):** Large Title 26/32, Title 1 22/26, Title 2 17/22, Title 3 15/20, Headline 13/16 bold, Body 13/16, Callout 12/15, Subheadline 11/14, Footnote and captions 10/13. (`typography`)
- **Dynamic Type (iOS, iPadOS):** seven standard sizes (Large is the default) plus five accessibility sizes, AX1 to AX5. Body runs from 14 pt at xSmall to 23 pt at xxxLarge and 53 pt at AX5. (`typography`)
- **Emphasized weights (iOS):** Large Title and Titles 1 and 2 become bold, the other styles semibold. (`typography`)
- **Text enlargement:** support at least 200 percent. (`accessibility`)
- **Leading:** never tight for three or more lines of text. (`typography`)
- **Tracking:** SF Pro is 0 at 12 pt and -26/1000 em (-0.43 pt) at 17 pt; per-size tables for every system font are on the page. (`typography`)
- **Mac Catalyst:** the iPad idiom scales views and text to 77 percent on the Mac (17 pt body becomes 13 pt); the Mac idiom renders at 100 percent. (`mac-catalyst`)
- **Widgets:** text at least 11 pt. (`widgets`)
- **Right-to-left:** set Arabic or Hebrew about 2 pt larger than adjacent all-caps Latin text. (`right-to-left`)

## Color, contrast, and materials

- **Contrast minimums:** 4.5:1 for text up to 17 pt, 3:1 for text of 18 pt or larger and for bold text at any size. (`accessibility`)
- **Custom colors:** aim for 7:1, especially for small text. (`dark-mode`)
- **System colors:** 12 hues, each with light, dark, and increased-contrast values, e.g. blue R0 G136 B255 in light and R0 G145 B255 in dark. iOS and iPadOS add six system grays. (`color`)
- **Wide color:** Display P3 at 16 bits per channel, exported as PNG. (`color`)
- **Liquid Glass over bright content:** add a dark dimming layer at 35 percent opacity behind clear glass. (`materials`)
- **Standard materials (iOS, iPadOS):** ultra-thin, thin, regular (the default), and thick, with four label vibrancy levels (none on thin or ultra-thin), three fill levels, and one separator level. (`materials`)
- **Label colors:** four levels, label, secondary, tertiary, quaternary. (`labels`, `materials`)

## Layout and bars

- **Mac bars and dividers:** the menu bar is 24 pt tall; a thin split-view divider is 1 pt. (`the-menu-bar`, `split-views`)
- **iPad split views:** two panes, like Mail, or three, like Keynote. (`split-views`)
- **iPhone Duo:** compact width on the outer display, regular on the inner one, and an even number of grid columns on the inner display. (`designing-for-iphone-duo`)
- **Widget margins:** 16 pt standard, 11 pt for tighter groupings. (`widgets`)
- **Live Activities:** a 14 pt standard margin on the Lock Screen, and a 44 pt corner radius in the Dynamic Island. (`live-activities`)
- **iPhone widget sizes (largest screen, 430x932 pt):** small 170x170, medium 364x170, large 364x382, circular 76x76, rectangular 172x76, inline 257x26. (`widgets`)

## Counts and limits

- **Prominent buttons:** one or two per view. A toolbar gets one primary action and three groups at most. (`buttons`, `toolbars`)
- **Titles:** a window title under 15 characters; the app name in About, Hide, and Quit 16 characters or fewer. (`toolbars`, `the-menu-bar`)
- **Mac windows:** one main window per app and one key window on screen at a time. (`windows`)
- **Alerts:** a title of two lines at most, up to three buttons titled in one or two words, and never more than one alert on screen. (`alerts`, `modality`)
- **Action sheets:** a one-line title. (`action-sheets`)
- **One at a time:** one sheet from the main interface, one popover (only an alert may cover it). (`sheets`, `popovers`)
- **Tabs:** six at most in a tab view; five or fewer default tabs in a customizable iPad tab bar. (`tab-views`, `tab-bars`)
- **Segmented controls:** about five to seven segments in a wide interface, about five on iPhone. (`segmented-controls`)
- **Radio buttons:** two to five per set; past about five options, use a pop-up button. (`toggles`)
- **Menus:** a pull-down menu needs at least three items; context-menu submenus go one level deep, with about three separator groups at most. (`pull-down-buttons`, `context-menus`)
- **Page control:** about 10 dots at most. (`page-controls`)
- **Sidebar:** two levels of hierarchy at most. Disclosure buttons: one per view. (`sidebars`, `disclosure-controls`)
- **Shortcuts:** four Home Screen quick actions at most; up to 10 App Shortcuts per app. (`home-screen-quick-actions`, `app-shortcuts`)
- **Notifications:** up to four action buttons. (`notifications`)
- **Help:** tooltips of 60 to 75 characters at most; tips of one or two sentences, about one every 24 hours when there are several. (`offering-help`)
- **Rating prompts:** the system shows at most three per app in 365 days; wait at least a week or two between requests. (`ratings-and-reviews`)
- **Keyboard shortcuts:** list modifiers in the order Control, Option, Shift, Command. (`keyboards`)

## Timing

- **Launch:** people sometimes won't wait more than a couple of seconds. (`launching`)
- **Loading:** show progress when loading takes more than a moment or two; show a video loading screen only past two seconds. (`loading`, `playing-video`)
- **Progress pacing to avoid:** 90 percent in five seconds, then the last 10 percent in five minutes. (`progress-indicators`)
- **Widgets and Live Activities:** update animations of two seconds at most. Live Activities suit activities up to eight hours and stay on the Lock Screen up to four hours after they end. (`widgets`, `live-activities`)
- **Time Sensitive notifications:** only for events happening now or within an hour. (`managing-notifications`)
- **Games:** a consistent 30 to 60 fps, and an initial download of 30 minutes or less. (`motion`, `designing-for-games`)

## Icons and images

- **App icon appearances (iOS, iPadOS, macOS):** default, dark, clear light, clear dark, tinted light, tinted dark, built from a background plus one or more foreground layers. (`app-icons`)
- **macOS document icons:** shown as small as 16x16 px, with background fills at 512, 256, 128, 32, and 16 px @1x. (`icons`)
- **SF Symbols:** 9 weights matching San Francisco, 3 scales, 4 rendering modes (monochrome, hierarchical, palette, multicolor). (`sf-symbols`)
- **Share sheet activity icon:** centered in an area of about 70x70 px. (`activity-views`)
- **Apple Pay buttons:** at least 100x30 pt (140x30 pt for titled variants like Buy or Check Out), with margins of at least 1/10 of the button's height. (`apple-pay`)

## Key source pages
`accessibility` · `typography` · `buttons` · `layout` · `color` · `app-icons` · `widgets` · `live-activities` · `toolbars` · `alerts`
