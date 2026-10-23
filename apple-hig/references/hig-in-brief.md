# The HIG in brief

The ideas that run through every page, for broad questions and screen reviews, and the order to work in when designing an app from scratch. Each point is a summary: before stating a detail, open the topic file for the slug it cites (the topic list under "Where to look" in SKILL.md, or grep `references/article-index.md`).

> **"The most successful and enduring designs are based on a deep understanding of how people think, feel, and interact with the world."** (`design-principles`)

## Core ideas

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

## Designing an app, in order

1. **Start from purpose.** Find what matters most to the people using it and make that great. (`design-principles`)
2. **Learn the platform's context and conventions** before drawing anything. (`references/principles-and-platforms.md`)
3. **Structure navigation** with the right container: a tab bar, a sidebar, a split view, or a toolbar. (`tab-bars`, `sidebars`, `split-views`)
4. **Lay out by importance** inside safe areas and size classes. (`layout`)
5. **Use system components**, one prominent action per view, and SF Symbols for icons. (`buttons`, `sf-symbols`)
6. **Apply system color, materials, and type** with Dynamic Type, in light, dark, and increased contrast. (`color`, `materials`, `typography`)
7. **Write the words** in one voice. (`writing`)
8. **Design every state**, from loading and progress to empty and error, with feedback in proportion. (`feedback`, `loading`)
9. **Check accessibility and inclusion** for sizes, contrast, VoiceOver, right-to-left, and reduced motion. (`accessibility`, `right-to-left`)
10. **Shape the first run** with an instant launch, optional onboarding, and permissions in context. (`launching`, `onboarding`, `privacy`)
11. **Extend into the system** where it helps, with widgets, Live Activities, and notifications. (`widgets`, `live-activities`, `notifications`)
12. **Test on real devices** at the largest and smallest sizes, text sizes, and localizations, and keep iterating after launch. (`layout`, `design-principles`)
