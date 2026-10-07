---
name: apple-hig
description: Apple's Human Interface Guidelines for iPhone, iPad, and Mac, from the 131 HIG pages that apply to them, every rule cited. Use when designing or reviewing UI for iOS, iPadOS, macOS, or Apple-style web, including layout, navigation, toolbars, tab bars, sheets, alerts, buttons, menus, controls, color, Liquid Glass, typography, SF Symbols, app icons, accessibility, widgets, notifications, Live Activities, AI features, or "what does the HIG say".
---

# Apple Human Interface Guidelines

This skill encodes the [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) that **Apple** publishes, scoped to **iPhone, iPad, and Mac**: the 131 of 158 pages that apply to iOS, iPadOS, and macOS, read on 2026-10-07. Apple Watch, Apple TV, and Vision Pro guidance is left out on purpose, and so are 13 Apple technologies (CarPlay, HealthKit and similar). `references/article-index.md` lists those 27 pages, and the script still opens them. The HIG is a living document: the newest change-log entry is 2026-09-17.

## What this is for

Use it to design or review an interface the way the HIG describes: choosing a component, laying out a screen, structuring navigation, presenting modal content, setting color, type, materials, and icons, making it accessible, giving feedback and writing the words, handling input, extending into widgets, notifications, and Live Activities, designing AI features, and adapting to iPhone, iPad, and Mac.

For a broad question, answer from the **core** below plus the relevant reference file. For a component or page, grep `references/article-index.md` for its slug, open the theme file it points to, and cite the page by slug: (`buttons`) → `https://developer.apple.com/design/human-interface-guidelines/buttons`. For an exact spec, check `references/numbers.md`.

**Before you finalize a specific component, or whenever an exact value or table matters, read the full page:** `python3 scripts/hig_page.py <slug>` (add `--section "Best practices"` for one section). The interface-design files, plus widgets, notifications, Live Activities, privacy, accounts, and AI, hold every Apple rule for these platforms. The other files keep the rules that change decisions. The page has every table and example, and it is always current.

## The one-sentence thesis

> **"The most successful and enduring designs are based on a deep understanding of how people think, feel, and interact with the world."** (`design-principles`)

Everything else is a corollary of this.

## The core (the load-bearing ideas)

1. **Eight principles are tools for weighing tradeoffs, not one right way.** Purpose, agency, responsibility, familiarity, flexibility, simplicity, craft, and delight. Simplicity isn't minimalism, and delight is never decoration that gets in the way of the task. (`design-principles`, `references/principles-and-platforms.md`)
2. **Content first: controls float above it.** Liquid Glass is a functional layer for controls and navigation, never for content, and the content layer sets the color and look of bars and buttons, not custom backgrounds. (`materials`, `color`, `toolbars`)
3. **Build on what people already know.** System components and standard patterns (Back and Close, the edit menu, the share sheet, standard icons, the menu bar order) carry learned behavior, and a custom version must look and behave the same. (`design-principles`, `toolbars`, `icons`, `the-menu-bar`)
4. **Hierarchy comes from style and placement, not size or decoration.** One or two prominent buttons per view, one primary toolbar action on the trailing side, color used sparingly and never as the only carrier of meaning. (`buttons`, `toolbars`, `color`)
5. **Adapt to the space and the person, not the device.** Lay out by size class and safe area rather than device type or orientation, let text scale with Dynamic Type, and keep the same functionality at every size. (`layout`, `typography`)
6. **Accessibility is a starting requirement.** Minimum text and control sizes per platform, 4.5:1 contrast for small text, alternatives to every gesture, labels for VoiceOver, and respect for settings like Reduce Motion. (`accessibility`, `voiceover`)
7. **Interrupt only for what is critical.** Match feedback to significance, use modality only when it helps people focus, keep alerts for critical, actionable information, and give notifications an honest interruption level. (`feedback`, `modality`, `alerts`, `managing-notifications`)
8. **Make mistakes cheap.** Prefer undo over confirmation, never make a destructive action the default, and keep people free to explore without losing time or work. (`design-principles`, `undo-and-redo`, `buttons`)
9. **Navigation stays visible, stable, and the same everywhere.** Tab bars move between sections and never hold actions or hide tabs, toolbars keep their groups and placement across platforms, and search lives in one clear place. (`tab-bars`, `toolbars`, `searching`)
10. **Speed is part of the design.** Launch instantly into where people left off, show something immediately, load in the background, and save state so an interruption costs nothing. (`launching`, `loading`, `multitasking`)
11. **Ask late, ask honestly, and default well.** Request data and permissions only when a feature needs them with a specific reason, require an account only for core features, keep onboarding short and optional, and make settings nearly unnecessary. (`privacy`, `managing-accounts`, `onboarding`, `settings`)
12. **Words are interface.** One consistent voice, labels that start with a verb, errors and empty states that say what happened and what to do. (`writing`, `alerts`, `buttons`)
13. **Motion and haptics must mean something.** Brief, cancelable, realistic, never the only way information arrives, and always respectful of Reduce Motion. (`motion`, `playing-haptics`, `accessibility`)
14. **Every platform gets its own context and the same care.** iPhone in one hand for quick visits and long sessions, iPad for hours of work that mixes touch, keyboard, trackpad, and Apple Pencil, Mac with precise pointing, keyboard shortcuts, flexible windows, and the menu bar. (`design-principles`, `designing-for-ios`, `designing-for-ipados`, `designing-for-macos`)

## The HIG method, end to end

1. **Start from purpose**: what matters most to the people using it, made great. (`design-principles`)
2. **Know the platform's context and conventions** before drawing anything. (`references/principles-and-platforms.md`)
3. **Structure navigation** with the right container: tab bar, sidebar, split view, or toolbar. (`tab-bars`, `sidebars`, `split-views`)
4. **Lay out by importance** inside safe areas and size classes. (`layout`)
5. **Use system components**, one prominent action per view, SF Symbols for icons. (`buttons`, `sf-symbols`)
6. **Apply system color, materials, and type** with Dynamic Type, in light, dark, and increased contrast. (`color`, `materials`, `typography`)
7. **Write the words** in one voice. (`writing`)
8. **Design every state**: loading, progress, empty, error, and feedback in proportion. (`feedback`, `loading`)
9. **Check accessibility and inclusion**: sizes, contrast, VoiceOver, right-to-left, reduced motion. (`accessibility`, `right-to-left`)
10. **Shape the first run**: instant launch, optional onboarding, permissions in context. (`launching`, `onboarding`, `privacy`)
11. **Extend into the system** where it helps: widgets, notifications, Live Activities, shortcuts. (`widgets`, `notifications`)
12. **Test on real devices** at the largest and smallest sizes, text sizes, and localizations, then keep iterating: shipping isn't the finish line. (`layout`, `design-principles`)

## Reference files

- **`principles-and-platforms.md`**: the eight principles, iOS, iPadOS, iPhone Duo, macOS, games, Mac Catalyst.
- **`layout-and-content.md`**: layout, safe areas, size classes, scroll views, lists and tables, collections, outline and column views, split views, tab views, boxes, disclosure controls, labels, text, image, and web views.
- **`navigation-and-search.md`**: choosing tab bar vs sidebar vs toolbar, tab bars, sidebars, toolbars, page and path controls, search fields, searching.
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
- **`system-experiences.md`**: widgets, Live Activities, notifications and their interruption levels, Control Center controls, Always On, App Shortcuts, Siri, snippets, App Clips, iMessage apps.
- **`privacy-and-accounts.md`**: asking for data and permissions, accounts, sign-in and deletion, Sign in with Apple, ID Verifier.
- **`ai-and-machine-learning.md`**: designing generative AI and machine learning features: control, disclosure, mistakes, feedback, latency, privacy.
- **`apple-services.md`**: Apple Pay, Wallet, In-App Purchase, iCloud, Maps.
- **`numbers.md`**: the specs people reach for most on iPhone, iPad, and Mac (sizes, type, contrast, spacing, counts, timing, icon canvases), each with its page.
- **`glossary.md`**: Apple's named concepts, each with its page. Grep it; don't read it whole.
- **`article-index.md`**: the 131 pages by theme, with slug, title, platforms, and a one-line thesis, plus the 27 left out. Grep it; don't read it whole.

## How to answer

- **Write like the HIG**: the rule first as a plain imperative ("Make buttons easy for people to use."), then Apple's reason, then the concrete case, with platform differences tagged (**(iOS)**, **(iPadOS)**, **(macOS)**).
- **Prefer the concrete**: Apple's numbers (44x44 pt, 4.5:1, under 15 characters) and its own apps as examples (Mail, Notes, Music, Weather). (`buttons`, `accessibility`, `toolbars`)
- **Always cite** the page slug, so the user can open the original.
- **Present Apple's positions as Apple's, unsoftened**, including the ones people push back on: no in-app Dark Mode switch, no branded launch screen, no hidden or disabled tabs. (`dark-mode`, `launching`, `tab-bars`)
- **The web**: the HIG is written for Apple platforms. When building for the web, carry the principle over and say plainly when a rule depends on an Apple control or system feature the web doesn't have.
- **Every example, exception, number, and reason you attribute to Apple comes from a reference file or the page, never from memory.** The core above is a summary: open the reference for the details. If you add an inference of your own (why Apple might want this, what changed from an older HIG), label it as yours.
- **If the HIG doesn't cover it, say so.** Don't invent Apple guidance. For Apple Watch, Apple TV, Vision Pro, or a technology this skill leaves out, say so and open the page with the script.
- **A newer page wins.** If the live page (from the script) differs from this skill, the page is newer: answer from the page and say what changed.

## Scope

It is not affiliated with or endorsed by Apple. The Human Interface Guidelines are © Apple Inc.: this skill restates their rules in its own words, with a link to each page, and `scripts/hig_page.py` reads Apple's public pages without storing them.

This skill holds only what Apple published in the HIG, for iPhone, iPad, and Mac. It leaves out watchOS, tvOS, visionOS, and 13 Apple technologies (listed at the end of the article index). It does not cover WWDC sessions, developer API documentation, App Store Review Guidelines, or web implementation details. The `apple-design` skill covers Apple's WWDC talks on fluid motion, translated for the web; this one is the HIG. The user's own design decisions and a project's design system override this skill when they disagree.
