---
name: apple-hig
description: Apple's Human Interface Guidelines on designing app interfaces for iPhone, iPad, and Mac, distilled from 119 HIG pages. Covers layout, navigation, modal views, controls, color and type, icons, accessibility, widgets and notifications, privacy, and AI features. Use when designing or reviewing UI for iOS, iPadOS, macOS, or Apple-style web, or for what Apple, the HIG, or the Human Interface Guidelines say.
---

# Apple Human Interface Guidelines

This skill encodes the body of work published at [developer.apple.com/design/human-interface-guidelines](https://developer.apple.com/design/human-interface-guidelines/) by **Apple**, the design guidance for its own platforms. It is distilled from the 119 pages on designing app interfaces for iPhone, iPad, and Mac, read on 2026-10-07, from the oldest change-log entry ("Action button", September 2022) through the newest ("Designing for iPhone Duo", September 2026). Every claim cites its page by slug.

## What this is for

Use this skill to answer questions the way the HIG would: which component fits a job, how to lay out a screen and move between its parts, how to present and dismiss things, how to use color, type, icons, and materials, how to make an interface accessible and word it, and how widgets, notifications, privacy prompts, and AI features should behave on iPhone, iPad, and Mac.

When the user asks a broad question, answer from the **core philosophy** below plus the relevant reference file. When they ask about a specific page or term, open the matching reference file and cite the page by slug, e.g. (`buttons`) → `https://developer.apple.com/design/human-interface-guidelines/buttons`. `references/article-index.md` lists all 119 pages with one-line theses, and `references/glossary.md` defines every named concept.

**Before you finalize a specific component, or whenever an exact value or table matters, read the full page:** `python3 scripts/hig_page.py <slug>` (add `--section "Best practices"` for one section). The interface files, plus widgets, notifications, Live Activities, privacy, accounts, and AI, hold every Apple rule for these platforms. The other files keep the rules that change decisions. The page has every table and example, and it's always current.

## The one-sentence thesis

> **"The most successful and enduring designs are based on a deep understanding of how people think, feel, and interact with the world."** (`design-principles`)

Everything else is a corollary of this.

## The core philosophy (the load-bearing ideas)

1. **Eight principles are tools for weighing tradeoffs, not one right way.** Purpose, agency, responsibility, familiarity, flexibility, simplicity, craft, and delight. Simplicity isn't minimalism, and delight is never decoration that gets in the way of the task. (`design-principles`, `references/principles-and-platforms.md`)
2. **Content comes first, and controls float above it.** Liquid Glass is a functional layer for controls and navigation, never for content. The content layer sets the color and look of bars and buttons, not a custom background. (`materials`, `color`, `toolbars`)
3. **Build on what people already know.** System components and standard patterns (Back and Close, the edit menu, the share sheet, standard icons, the menu bar order) carry learned behavior, and a custom version must look and behave the same. (`design-principles`, `toolbars`, `icons`, `the-menu-bar`)
4. **Hierarchy comes from style and placement, not size.** One or two prominent buttons per view, one primary toolbar action on the trailing side, and color used sparingly, never as the only carrier of meaning. (`buttons`, `toolbars`, `color`)
5. **Adapt to the space and the person, not the device.** Lay out by size class and safe area rather than device type or orientation, let text scale with Dynamic Type, and keep the same functionality at every size. (`layout`, `typography`)
6. **Accessibility is a starting requirement.** Minimum text and control sizes per platform, 4.5:1 contrast for small text, an alternative to every gesture, labels for VoiceOver, and respect for settings like Reduce Motion. (`accessibility`, `voiceover`)
7. **Interrupt only for what is critical.** Match feedback to its significance, use modality only when it helps people focus, keep alerts for critical, actionable information, and give notifications an honest interruption level. (`feedback`, `modality`, `alerts`, `managing-notifications`)
8. **Make mistakes cheap.** Prefer undo over confirmation, never make a destructive action the default, and keep people free to explore without losing time or work. (`design-principles`, `undo-and-redo`, `buttons`)
9. **Navigation stays visible, stable, and the same everywhere.** Tab bars move between sections and never hold actions or hide tabs, toolbars keep their groups and placement across platforms, and search lives in one clear place. (`tab-bars`, `toolbars`, `searching`)
10. **Speed is part of the design.** Launch straight into where people left off, show something at once, load in the background, and save state so an interruption costs nothing. (`launching`, `loading`, `multitasking`)
11. **Ask late, ask honestly, and default well.** Request data and permissions only when a feature needs them, with a specific reason. Require an account only for core features, keep onboarding short and optional, and make settings nearly unnecessary. (`privacy`, `managing-accounts`, `onboarding`, `settings`)
12. **Words are interface.** One consistent voice, labels that start with a verb, and errors and empty states that say what happened and what to do next. (`writing`, `alerts`, `buttons`)
13. **Motion and haptics must mean something.** They're brief, cancelable, and realistic, never the only way information arrives, and they respect Reduce Motion. (`motion`, `playing-haptics`, `accessibility`)
14. **Every platform gets its own context and the same care.** iPhone sees quick visits and long sessions in one hand, iPad hours of work mixing touch, keyboard, trackpad, and Apple Pencil, and Mac precise pointing, keyboard shortcuts, flexible windows, and the menu bar. (`design-principles`, `designing-for-ios`, `designing-for-ipados`, `designing-for-macos`)

## The HIG method, end to end

1. **Start from purpose.** Find what matters most to the people using it and make that great. (`design-principles`)
2. **Learn the platform's context and conventions** before drawing anything. (`references/principles-and-platforms.md`)
3. **Structure navigation** with the right container: a tab bar, a sidebar, a split view, or a toolbar. (`tab-bars`, `sidebars`, `split-views`)
4. **Lay out by importance** inside safe areas and size classes. (`layout`)
5. **Use system components**, one prominent action per view, and SF Symbols for icons. (`buttons`, `sf-symbols`)
6. **Apply system color, materials, and type** with Dynamic Type, in light, dark, and increased contrast. (`color`, `materials`, `typography`)
7. **Write the words** in one voice. (`writing`)
8. **Design every state**, from loading and progress to empty and error, with feedback in proportion. (`feedback`, `loading`)
9. **Check accessibility and inclusion**: sizes, contrast, VoiceOver, right-to-left, reduced motion. (`accessibility`, `right-to-left`)
10. **Shape the first run** with an instant launch, optional onboarding, and permissions in context. (`launching`, `onboarding`, `privacy`)
11. **Extend into the system** where it helps, with widgets, Live Activities, and notifications. (`widgets`, `live-activities`, `notifications`)
12. **Test on real devices** at the largest and smallest sizes, text sizes, and localizations, then keep iterating. Shipping isn't the finish line. (`layout`, `design-principles`)

## Reference files

- **`principles-and-platforms.md`**: the eight principles, iOS, iPadOS, iPhone Duo, macOS, games, Mac Catalyst.
- **`layout-and-content.md`**: layout, safe areas, size classes, scroll views, lists and tables, collections, outline and column views, split views, tab views, boxes, disclosure controls, labels, text, image, and web views.
- **`navigation-and-search.md`**: choosing a tab bar, sidebar, or toolbar, then tab bars, sidebars, toolbars, page and path controls, search fields, searching.
- **`presentation-and-windows.md`**: modality, sheets, alerts, action sheets, popovers, panels, windows, full screen, multitasking.
- **`buttons-and-menus.md`**: buttons, pop-up and pull-down buttons, menus, context menus, the menu bar, Dock menus, Home Screen quick actions.
- **`editing-files-and-sharing.md`**: edit menus, undo and redo, drag and drop, file management, printing, collaboration, the share sheet.
- **`controls-and-data-entry.md`**: text fields, entering data, pickers, toggles, segmented controls, sliders, steppers, combo boxes, color and image wells, token fields, virtual keyboards.
- **`visual-design.md`**: color, Dark Mode, materials and Liquid Glass, typography, branding, images.
- **`icons-and-symbols.md`**: app icons, interface icons, SF Symbols.
- **`feedback-and-status.md`**: feedback, loading, launching, progress indicators, gauges, rating indicators, Activity rings, status bars, charts and charting data.
- **`onboarding-help-and-writing.md`**: writing, onboarding, offering help, settings, ratings and reviews.
- **`accessibility-and-inclusion.md`**: accessibility, VoiceOver, inclusion, right to left.
- **`motion-and-media.md`**: motion, haptics, audio, video, live-viewing apps, Live Photos, photo editing.
- **`inputs.md`**: gestures, keyboards, pointing devices, Apple Pencil and Scribble, game controls, Action button, Camera Control, motion sensors, nearby interactions, focus.
- **`system-experiences.md`**: widgets, Live Activities, and notifications with their interruption levels.
- **`privacy-and-accounts.md`**: asking for data and permissions, accounts, sign-in and deletion, Sign in with Apple, ID Verifier.
- **`ai-and-machine-learning.md`**: generative AI and machine learning features, from control and disclosure to mistakes, feedback, latency, and privacy.
- **`numbers.md`**: the specs people reach for most on iPhone, iPad, and Mac (sizes, type, contrast, spacing, counts, timing, icon canvases), each with its page.
- **`glossary.md`**: 441 named concepts, each with the pages that define it. Grep it instead of reading it whole.
- **`article-index.md`**: all 119 pages by theme with slug, date, platforms, and a one-line thesis, plus the 39 left out. Grep it instead of reading it whole.

## How to answer

- **Write like the HIG**: lead with the rule as a plain imperative ("Use alerts sparingly."), give the reason in terms of what people do ("people can miss a popover or close it by accident"), point to Apple's own apps ("Mail displays an indicator"), and tag platform differences (**(iOS)**, **(iPadOS)**, **(macOS)**).
- **Prefer the concrete**: Apple's numbers (44x44 pt, 4.5:1, under 15 characters) and its own apps as examples (Mail, Notes, Music, Weather). (`buttons`, `accessibility`, `toolbars`)
- **Always cite** the page slug, so the user can open the original.
- If the user asks about a specific page, check `references/article-index.md` first, then the theme file.
- These are Apple's guidelines, distilled faithfully, including the ones people push back on: no in-app Dark Mode switch, no branded launch screen, no hidden or disabled tabs. Present them as Apple's, with Apple's reasoning, and don't soften them. (`dark-mode`, `launching`, `tab-bars`)
- **Every example, exception, number, and reason you attribute to Apple comes from a reference file or the page, never from memory.** The core above is a summary, so open the reference for details. If you add an inference of your own, such as why Apple might want this, label it as yours.
- **For the web**, carry the principle over and say plainly when a rule depends on an Apple control or system feature the web doesn't have.
- **A newer page wins.** If the live page differs from this skill, answer from the page and say what changed.
- If the HIG doesn't cover the question, say so, and don't answer in Apple's voice from outside the HIG. For a page this skill leaves out, like Apple Watch, Apple TV, Vision Pro, Apple Pay, In-App Purchase, Siri, or App Clips, say so, then read the page with the script and answer from it, never from memory.

## Scope

This skill holds only what Apple published in the HIG, for iPhone, iPad, and Mac. It leaves out watchOS, tvOS, and visionOS, 13 Apple technologies like CarPlay, Apple's services (Apple Pay, Wallet, In-App Purchase, iCloud, Maps), and system integrations (Siri, App Shortcuts, App Clips, Control Center controls, iMessage apps, Always On), all listed at the end of the article index. It doesn't cover WWDC sessions, developer API documentation, the App Store Review Guidelines, or web implementation. The `apple-design` skill covers Apple's WWDC talks on fluid motion, translated for the web, while this one is the HIG. The user's own design decisions and a project's design system override this skill when they disagree.

It isn't affiliated with or endorsed by Apple, and the Human Interface Guidelines are © Apple Inc. Each rule links back to its page, and `scripts/hig_page.py` reads Apple's public pages without storing them.
