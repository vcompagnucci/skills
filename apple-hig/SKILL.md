---
name: apple-hig
description: Apple's Human Interface Guidelines (HIG) for iPhone, iPad and Mac apps, cited by page. Use for any iOS, iPadOS or macOS interface question: designing or reviewing a screen, how a component should look or behave, a size or spec, or what Apple or the HIG says, including for Apple-style web.
---

# Apple HIG

The 119 HIG pages on app interface design for iPhone, iPad and Mac, distilled into reference files where every rule cites its page by **slug**: (`buttons`) is https://developer.apple.com/design/human-interface-guidelines/buttons.

## Steps

1. **Route.** Find the question's branch in "Where to look" and open only the files it names.
2. **Read the live page** before you finalize a component, and whenever an exact value or table matters: `python3 scripts/hig_page.py <slug>`, or add `--section "Best practices"` for one section. The HIG site is a JavaScript app, so a web fetch returns only the title. When the live page differs from the reference file, the live page is newer: answer from it and say what changed.
3. **Answer in the HIG voice**, below.

Done when every rule, number, example and reason in the answer carries its slug, and every component you finalized was read on its live page.

## Where to look

- **One page or component.** Grep `references/article-index.md` for its slug and file, then open that file.
- **A named concept.** Grep `references/glossary.md`, 441 terms with the pages that define them.
- **A number** (a size, contrast ratio, spacing, count or timing). `references/numbers.md`, then the live page for the full table.
- **A review of a screen or a design.** List every component on it and check each against its file, then check the whole against the core ideas in `references/hig-in-brief.md`. Done when every component has been checked.
- **An app or a flow from scratch.** Follow "Designing an app, in order" in `references/hig-in-brief.md`, opening each file as its step comes up.
- **A topic.** The file below that holds it.
- **Apple's approach as a whole, or a question across many topics.** `references/hig-in-brief.md`, then the files its points cite.
- **Apple-style web.** The same files. Carry each principle over, and name every rule that depends on an Apple control or system feature the web lacks.
- **A page this skill leaves out:** Apple Watch, Apple TV, Vision Pro, CarPlay and the other Apple technologies, Apple Pay, Wallet, In-App Purchase, iCloud, Maps, Siri, App Shortcuts, App Clips, Control Center controls, iMessage apps, Always On. Say the skill leaves it out, find its slug at the end of `references/article-index.md`, read it with the script, and answer from the page.
- **Apple's fluid motion and gestures from the WWDC talks, translated for the web.** Call the Skill tool with "apple-design".
- **Anything outside the HIG** (WWDC sessions, developer API docs, the App Store Review Guidelines, web implementation). Say the HIG doesn't cover it, and answer in your own voice, not Apple's.

Topic files:

- `references/principles-and-platforms.md`: the eight principles, iOS, iPadOS, iPhone Duo, macOS, games, Mac Catalyst.
- `references/layout-and-content.md`: layout, safe areas, size classes, scroll views, lists and tables, collections, outline and column views, split views, tab views, boxes, disclosure controls, labels, text, image, and web views.
- `references/navigation-and-search.md`: choosing a tab bar, sidebar, or toolbar, then tab bars, sidebars, toolbars, page and path controls, search fields, searching.
- `references/presentation-and-windows.md`: modality, sheets, alerts, action sheets, popovers, panels, windows, full screen, multitasking.
- `references/buttons-and-menus.md`: buttons, pop-up and pull-down buttons, menus, context menus, the menu bar, Dock menus, Home Screen quick actions.
- `references/editing-files-and-sharing.md`: edit menus, undo and redo, drag and drop, file management, printing, collaboration, the share sheet.
- `references/controls-and-data-entry.md`: text fields, entering data, pickers, toggles, segmented controls, sliders, steppers, combo boxes, color and image wells, token fields, virtual keyboards.
- `references/visual-design.md`: color, Dark Mode, materials and Liquid Glass, typography, branding, images.
- `references/icons-and-symbols.md`: app icons, interface icons, SF Symbols.
- `references/feedback-and-status.md`: feedback, loading, launching, progress indicators, gauges, rating indicators, Activity rings, status bars, charts and charting data.
- `references/onboarding-help-and-writing.md`: writing, onboarding, offering help, settings, ratings and reviews.
- `references/accessibility-and-inclusion.md`: accessibility, VoiceOver, inclusion, right to left.
- `references/motion-and-media.md`: motion, haptics, audio, video, live-viewing apps, Live Photos, photo editing.
- `references/inputs.md`: gestures, keyboards, pointing devices, Apple Pencil and Scribble, game controls, Action button, Camera Control, motion sensors, nearby interactions, focus.
- `references/system-experiences.md`: widgets, Live Activities, and notifications with their interruption levels.
- `references/privacy-and-accounts.md`: asking for data and permissions, accounts, sign-in and deletion, Sign in with Apple, ID Verifier.
- `references/ai-and-machine-learning.md`: generative AI and machine learning features, from control and disclosure to mistakes, feedback, latency, and privacy.

## The HIG voice

- **Rule first, as a plain imperative** ("Use alerts sparingly."), then the reason in terms of what people do ("people can miss a popover or close it by accident"), then Apple's own app as the example ("Mail displays an indicator").
- **Apple's numbers and apps over adjectives.** 44x44 pt, 4.5:1, under 15 characters; Mail, Notes, Music, Weather. (`buttons`, `accessibility`, `toolbars`)
- **Tag platform differences** as **(iOS)**, **(iPadOS)**, **(macOS)**.
- **State Apple's rules as Apple states them**, the unpopular ones included: no in-app Dark Mode switch, no branded launch screen, no hidden or disabled tabs, each with Apple's reason. (`dark-mode`, `launching`, `tab-bars`)
- **Every example, exception, number and reason you attribute to Apple comes from a reference file or the live page**, never from memory. Label an inference of your own, like why Apple might want something, as yours.
- **The user's own design decisions and their project's design system win** over the HIG. Say where they part from it.
