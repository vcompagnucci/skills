# Controls and data entry

How people enter text and set values. Apple's position: minimize typing by gathering data from the system and offering choices, match each field and keyboard to the content expected, and pick the control by the kind of value (a toggle for two opposing states, a segmented control for a few related choices, a slider for a range, a picker for longer ordered lists). (`entering-data`, `text-fields`, `toggles`, `segmented-controls`, `pickers`)

**Contents:** Choosing the control · Text fields and entering data · Virtual keyboards · Toggles · Segmented controls · Pickers · Sliders and steppers · Combo boxes, token fields, color wells, and image wells · Key source pages

## Choosing the control

- **Use a toggle only to choose between two opposing values that affect the state of content or a view.** A toggle always manages a state, so for anything else, like choosing from a list, use another control such as a pop-up button. (`toggles`)
- **Use a picker for medium-to-long lists, a pull-down button for a fairly short list, and a list or table for a very large set.** A picker adds too much visual weight to a short list, while lists and tables adjust in height and a table's index targets a section fast. (`pickers`)
- **Use a segmented control for closely related choices that affect an object, state, or view, like attributes in an inspector or actions in a toolbar.** Consider it when grouping or selection state matters: unlike other button styles, it keeps its grouping at any view size or placement, so people see at a glance which segments are selected. (`segmented-controls`)
- **(macOS) Use a checkbox for a single on/off setting, radio buttons for more than two mutually exclusive options, and a pop-up button past about five.** A checkmark's presence reads at a glance, and a long list of radio buttons takes a lot of space and can overwhelm people. (`toggles`)
- **Set a value in a range with a slider, adding a text field and a stepper for exact values.** The field accepts a specific value and the stepper steps in whole values. A stepper alone suits small changes, so pair it with a field when large changes are likely, like copies on a printing screen. (`sliders`, `steppers`)
- **Use a text field for a small amount of text, like a name or email address, and a text view for more.** In macOS, consider a combo box when text input needs a list of choices, so people can type a value or choose one. (`text-fields`, `combo-boxes`)

## Text fields and entering data (`text-fields`, `entering-data`)

- **Get information from the system instead of asking for it, and offer choices instead of typing.** Gather what you can automatically, like settings, or with permission, like location or calendar data. Choosing from a picker, menu, or list is usually easier than typing, even with a keyboard at hand. (`entering-data`)
- **Be clear about the data you need, and prefill reasonable defaults.** Show a prompt in the field, like "username@company.com", or an introductory label, like "Email". Defaults minimize decision making and speed data entry. (`entering-data`)
- **Show a hint in a text field to communicate its purpose, and consider a separate label too.** Placeholder text like "Email" or "Password" shows only while the field is empty and disappears when people start typing, so a label keeps reminding them. (`text-fields`)
- **Use a secure field for any sensitive data, like a password, and never prepopulate a password field.** A secure field obscures each character as people enter it, typically with a small filled circle. Always ask for the password, or use biometric or keychain authentication. (`text-fields`, `entering-data`)
- **Size a text field to the amount of text you expect.** Its size helps people visually gauge how much information to provide. (`text-fields`)
- **Space multiple text fields evenly, stacked vertically when possible, with consistent widths.** Enough space shows which field belongs to each introductory label. An address form might give first and last name one width, and address and city another. (`text-fields`)
- **Make tabbing between fields move focus in a logical sequence.** The system attempts this automatically, so you rarely need to customize it. (`text-fields`)
- **Validate values as soon as people enter them, timed to the field.** Fixing mistakes after a long form frustrates people, and a field that accepts only digits should flag any other character. Check an email address when people switch fields, but a user name or password before they leave it. (`entering-data`, `text-fields`)
- **Use a number formatter for numeric data, without assuming how values will appear.** It makes a field accept only numbers and can show fixed decimal places, a percentage, or currency, but formatting varies widely with people's locale. (`text-fields`, `entering-data`)
- **Support every input method, including drag and drop and pasting.** Letting people drag or paste data eases entry and makes the experience feel integrated with the rest of the system. (`entering-data`)
- **Make clear that people must provide the required data before they can proceed.** If a Next or Continue button follows a set of text fields, enable it only after people enter the data you require. (`entering-data`)
- **Choose how a field handles text that overflows it.** The system clips it by default, and a field can instead wrap at the character or word level, or truncate with an ellipsis at the beginning, middle, or end. (`text-fields`)
- **(macOS) Consider an expansion tooltip to show the full text of a clipped or truncated field.** It appears when the pointer rests on the field, and iOS and iPadOS apps running on a Mac can use it too. (`text-fields`, `entering-data`)
- **(iOS, iPadOS) Put a Clear button at the trailing end of a text field.** People can tap it to erase the field's contents without repeatedly tapping the Delete key. (`text-fields`)
- **(iOS, iPadOS) Use a text field's leading end to show its purpose and its trailing end for extra features.** Either end can hold a custom image, or a system-provided button like Bookmarks. (`text-fields`)

## Virtual keyboards (`virtual-keyboards`)

- **(iOS, iPadOS) Show the keyboard that matches the content people are editing by giving each field a semantic meaning.** The system then supplies the right keyboard and refines its corrections, as an email keyboard adds @ and a period. (`virtual-keyboards`, `text-fields`)
- **(iOS, iPadOS) Pick from the system keyboard types, each with keys optimized for its task.** Default, ASCII capable, ASCII capable number pad, decimal pad, email address, name phone pad, number pad, numbers and punctuation, phone pad, Twitter, URL, and web search. A virtual keyboard doesn't support keyboard shortcuts. (`virtual-keyboards`)
- **(iOS, iPadOS) Customize the Return key type when it clarifies text entry.** It defaults from the keyboard type, and an app that starts a search can use a search Return key, consistent with other places people search. (`virtual-keyboards`)
- **(iOS, iPadOS) Offer a custom input view only when its benefit is clear in your app.** It replaces the system keyboard while people are in your app, as Numbers does for numeric values in a spreadsheet. Without a clear benefit, people wonder why they can't get the system keyboard back. (`virtual-keyboards`)
- **(iOS, iPadOS) Play the standard keyboard sound when people tap keys in a custom input view.** People expect the familiar feedback of the system keyboard, and they can turn keyboard sounds off in Settings > Sounds. (`virtual-keyboards`)
- **(iOS, iPadOS) Build a systemwide custom keyboard only for unique functionality, like a novel input method or a language the system doesn't support.** For a keyboard used only in your app, make a custom input view. Custom keyboards, chosen in Settings, don't work in secure text or phone number fields. (`virtual-keyboards`)
- **(iOS, iPadOS) Give a custom keyboard an obvious way to switch keyboards, and don't duplicate system keys.** People know the Globe key switches keyboards, and the system may show the Emoji/Globe and Dictation keys beneath yours, so repeating them confuses. (`virtual-keyboards`)
- **(iOS, iPadOS) Teach a custom keyboard with a tutorial in your app, never with help inside the keyboard.** Learning a new keyboard takes time, so explain how to choose it, activate it during text entry, use it, and switch back to the standard keyboard. (`virtual-keyboards`)
- **(iOS, iPadOS) Use the keyboard layout guide so the keyboard feels like an integrated part of the interface.** It keeps important parts of the interface visible while the keyboard is onscreen, so the keyboard doesn't cover a field or button. (`virtual-keyboards`)
- **(iOS, iPadOS) Keep custom controls above the keyboard relevant to the current task.** Numbers shows calculation controls there. If other views use Liquid Glass or the controls look out of place, apply Liquid Glass to their view, which a standard toolbar adopts automatically, and position it with the layout guide and standard padding. (`virtual-keyboards`)

## Toggles (`toggles`)

- **Choose a toggle style by platform: a switch, a checkbox, or a button that behaves like a toggle.** All platforms support toggle buttons, which show their purpose with an interface icon and change appearance, typically the background, with their state. macOS also offers checkboxes and radio buttons. (`toggles`)
- **Clearly identify what a toggle affects, and make its states obvious without relying on color.** Context usually suffices, and macOS apps often add a label. Add or remove a fill, a background shape, or a checkmark or dot, because not everyone perceives color differences. (`toggles`)
- **(iOS, iPadOS) Use the switch style only in a list row.** The row's content provides the context for the state the switch controls, so the switch needs no label. (`toggles`)
- **(iOS, iPadOS) Change a switch's default green only if necessary.** Your app's accent color can work, if it contrasts enough with the switch's uncolored appearance to be perceptible. (`toggles`)
- **(iOS, iPadOS) Outside a list, use a button that behaves like a toggle, not a switch, and don't add a label explaining it.** Its icon and changing background explain it, as Phone's filter button shows a blue highlight while it filters recent calls. (`toggles`)
- **(macOS) Keep switches, checkboxes, and radio buttons in the window body, never in the window frame.** In particular, keep them out of toolbars and status bars. (`toggles`)
- **(macOS) Prefer a switch for a setting you want to emphasize, like turning a group of settings on or off.** A switch carries more visual weight than a checkbox, so it suits a control with more functionality than a checkbox typically has. (`toggles`)
- **(macOS) In a grouped form, consider a mini switch for a single row's setting.** Its height matches buttons and other controls, keeping rows consistent. For a hierarchy, use a regular switch for the primary setting and mini switches for subordinate ones. (`toggles`)
- **(macOS) Don't replace a checkbox with a switch, and use checkboxes, not switches, for a hierarchy of settings.** If you already use a checkbox, keep it. Checkboxes align well and show grouping, and leading-edge alignment with indentation shows which settings depend on others. (`toggles`)
- **(macOS) Make a checkbox show its real state: on, off, or mixed.** A checkbox that turns subordinate checkboxes on and off shows mixed when they differ, like a text-style setting with only some of bold, italic, and underline on. (`toggles`)
- **(macOS) Give a checkbox a title on its trailing side, except in an editable checklist.** A checkbox is a small square that's empty when off, holds a checkmark when on, and shows a dash when mixed. (`toggles`)
- **(macOS) Label a group of checkboxes when the connection between them isn't obvious.** The label describes the set, and its baseline lines up with the group's first checkbox. (`toggles`)
- **(macOS) Use radio buttons for mutually exclusive options, and checkboxes when people can choose several.** Each radio button clarifies an option beyond just on or off with a unique label. A radio button is a small circle followed by its label, filled when selected and empty when deselected, usually in groups of two to five. (`toggles`)
- **(macOS) Use a checkbox, not a radio button, to show a mixed state.** A radio button can show a mixed state as a dash, but it's rarely useful, because additional radio buttons can communicate more states. (`toggles`)
- **(macOS) Use a pair of radio buttons for one on/off setting only when a single checkbox can't make both states clear.** Otherwise prefer the checkbox, whose checkmark shows the state at a glance, and label each radio button with the state it controls. (`toggles`)
- **(macOS) Space horizontal radio buttons consistently, by the width of the longest label.** Measure the space that label needs and use the same measurement for every button. (`toggles`)

## Segmented controls (`segmented-controls`)

- **Keep each segmented control either selecting or acting, never both.** Don't assign actions to segments in a control that shows selection, or show selection in one that performs actions, like Mail's Reply, Reply All, and Forward. (`segmented-controls`)
- **Let a segmented control offer a single choice, or in macOS, a single choice or several.** In macOS Keynote, the alignment control allows one choice, the font attributes control combines bold, italics, and underline, and the toolbar uses a segmented control to show and hide editing panes. (`segmented-controls`)
- **Keep to about five to seven segments in a wide interface and about five on iPhone.** More segments are hard to parse and time-consuming to navigate. (`segmented-controls`)
- **Make segments equal in width, with content of similar size.** Equal widths feel balanced, so keep icon and title widths consistent too, since content that fills some segments but not others doesn't look good. (`segmented-controls`)
- **Use either text or images in one control, never both, and write text labels as nouns or noun phrases.** Mixing feels disconnected and confusing. Labels use title-style capitalization, and a control with text labels needs no introductory text. (`segmented-controls`)
- **(iOS, iPadOS) Consider a segmented control to switch between closely related subviews, and a tab bar for separate sections.** Calendar's New Event sheet uses one to switch between creating an event and a reminder. (`segmented-controls`)
- **(macOS) Use a tab view, not a segmented control, to switch views in the main window area.** A tab view looks like a box combined with a segmented control. A segmented control can switch views in a toolbar or an inspector pane. (`segmented-controls`)
- **(macOS) Consider introductory text to clarify a segmented control's purpose.** With symbols or interface icons, you could add a label below each segment, and if the app uses tooltips, give every segment one. (`segmented-controls`)
- **(macOS) Consider supporting spring loading.** On a Mac with a Magic Trackpad, people can drag selected items over a segment and force click to activate it without dropping them, then keep dragging. (`segmented-controls`)

## Pickers (`pickers`)

- **Use predictable, logically ordered values, like an alphabetized list of countries.** Many values stay hidden until people interact, so they need to predict what's there to move through quickly. The exact values and their order depend on the device language. (`pickers`)
- **Show a picker in context instead of switching views.** It works best below or near the field people are editing, typically at the bottom of a window or in a popover. (`pickers`)
- **Consider coarser minute intervals in a date picker, any that divides evenly into 60.** The default lists 60 values, 0 to 59, and quarter-hour intervals give 0, 15, 30, and 45. (`pickers`)
- **(iOS, iPadOS) Choose a date picker style: compact, inline, wheels, or automatic.** Compact is a button that opens editable content in a modal view, inline shows wheels for time or a calendar for dates, wheels also accept keyboard entry, and automatic lets the system choose by platform and mode. (`pickers`)
- **(iOS, iPadOS) Use a compact date picker when space is constrained.** Its button shows the value in your accent color and opens a calendar-style editor and time picker, where people make several edits before tapping outside to confirm. (`pickers`)
- **(iOS, iPadOS) Set a date picker's mode: date, time, date and time, or countdown timer.** Time can add an AM/PM designation. A countdown timer shows hours and minutes up to 23 hours and 59 minutes, and isn't available in the inline or compact styles. (`pickers`)
- **(macOS) Use a textual date picker for specific selections in limited space, and a graphical one for browsing days or selecting a range.** The graphical style also suits an app where the look of a clock face fits. (`pickers`)

## Sliders and steppers (`sliders`, `steppers`)

- **Put a slider's minimum on the leading side or bottom, and its maximum on the trailing side or top.** People expect the same directions in every app, like a percentage that runs from 0 on the leading side to 100 on the trailing side. (`sliders`)
- **Customize a slider's appearance only when it adds value.** The track fills with color up to the thumb, and you can adjust the track color, thumb image and tint, and optional end icons, like a small and a large image icon on an image-size slider. (`sliders`)
- **(iOS, iPadOS) Use a volume view, not a slider, to adjust audio volume.** It's customizable and includes a volume-level slider and a control for changing the active audio output device. (`sliders`)
- **(macOS) Consider live feedback as a slider's value changes.** It shows results in real time, as Dock icons resize while people adjust the Size slider in Dock settings. (`sliders`)
- **(macOS) Use a horizontal slider between fixed start and end points, and a circular slider for values that repeat or continue indefinitely.** Opacity from 0 to 100 percent suits a horizontal slider, and rotation from 0 to 360 degrees, or four spins of 1440 degrees, a circular one. (`sliders`)
- **(macOS) Know the two slider shapes: a linear slider has a narrow lozenge thumb, and a circular slider a small circle.** Tick marks are optional on both and appear as evenly spaced dots around a circular slider. A linear slider often adds icons for its minimum and maximum. (`sliders`)
- **(macOS) Use tick marks to increase clarity and accuracy, labeling only as many as needed.** Ticks show the scale and help people locate values. Often only the minimum and maximum need labels, nonlinear values like Energy Saver's get periodic ones, and a tooltip can show the thumb's value. (`sliders`)
- **(macOS) Consider introducing a slider with a label.** Labels generally use sentence-style capitalization and end with a colon. (`sliders`)
- **Make the value a stepper changes obvious, since the stepper itself shows none.** A stepper is a two-segment control that sits next to a field showing its current value, so people know which value they're changing. (`steppers`)
- **(macOS) For large value ranges, consider letting people Shift-click a stepper to change the value faster.** A Shift-click can step by more than the default increment, for example 10 times as much. (`steppers`)

## Combo boxes, token fields, color wells, and image wells (`combo-boxes`, `token-fields`, `color-wells`, `image-wells`)

- **(macOS) Fill a combo box with a meaningful default from its list, which needn't be the first item.** A combo box pairs a text field with a pull-down button, and although the field can start empty, a default that refers to the hidden choices works best. (`combo-boxes`)
- **(macOS) Offer the most likely choices in a combo box, each no wider than the field.** People like typing a custom value, which isn't added to the list, and choosing from relevant ones. A wider item may be truncated, which is hard to read. (`combo-boxes`)
- **(macOS) Introduce a combo box with a label that says what kinds of items to expect.** The label generally uses title-style capitalization and ends with a colon. (`combo-boxes`)
- **(macOS) Use a token field to turn entered text into tokens people can select and manipulate.** In Mail's address fields, people drag recipient tokens to reorder them or move them to another field, and the field suggests recipients as people type. (`token-fields`)
- **(macOS) Give each token a context menu with useful options or information.** Mail's recipient tokens let people edit the name, mark the recipient as a VIP, or view the contact card. (`token-fields`)
- **(macOS) Consider more ways than the comma to turn text into a token, and slow suggestions to a comfortable pace.** Pressing Return can also create a token, and suggestions that appear immediately, the default, can distract people while they type. (`token-fields`)
- **Consider the system color picker for a color well.** It's familiar across iOS, iPadOS, and macOS and lets people save colors they can use in any app. A color well can instead open a custom picker you design. (`color-wells`)
- **(macOS) Expect a clicked color well to highlight, open a color picker, and then show the chosen color.** Color wells also support drag and drop, from one well to another and from the picker to a well. (`color-wells`)
- **(macOS) Restore an image well's default image when people clear one that requires an image.** An image well is an editable image view: people select it to copy, paste, or delete its image, or drag a new image in without selecting it first. (`image-wells`)
- **(macOS) If an image well supports copy and paste, make the standard Edit menu items available.** People expect to use those menu items, or the standard keyboard shortcuts, with an image well. (`image-wells`)

## Key source pages
`text-fields` · `entering-data` · `toggles` · `segmented-controls` · `pickers` · `sliders` · `virtual-keyboards` · `steppers` · `combo-boxes` · `token-fields` · `color-wells` · `image-wells`
