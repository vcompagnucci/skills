# Color, type, materials, and images

How an app uses color, type, materials, and artwork. Apple's position: color is sparing, consistent, never the only carrier of meaning, and works in light, dark, and increased contrast. Type favors legibility and scales with Dynamic Type, Liquid Glass is a layer for controls and never for content, and the brand defers to content. (`color`, `dark-mode`, `typography`, `materials`, `images`, `branding`)

## Choosing materials, accent color, and fonts

- **Liquid Glass for controls and navigation, standard materials for the content layer.** Glass forms a functional layer, like tab bars and sidebars, that floats above content, so as an app background it confuses the hierarchy. Sliders and toggles in the content layer take it on only while people use them. (`materials`)
- **Regular glass by default, clear glass only over visually rich backgrounds like photos and video.** Regular blurs and adjusts the luminosity behind it, suiting text-heavy components like alerts, sidebars, and popovers. Over bright content, add a dark dimming layer at 35% opacity behind clear glass, unless AVKit playback controls supply their own. (`materials`)
- **Use color sparingly on Liquid Glass, reserving accent color for primary actions and status indicators, like unread badges or the selected tab's icon.** Used broadly, brand color overwhelms the interface. Tint the background of a prominent button like Done, not its symbol or text, and never the backgrounds of several controls. (`color`, `branding`)
- **Signature font for headlines and subheadings, system fonts for body copy and captions.** System fonts are built for legibility at small sizes, and a brand font must stay legible at all sizes and support Bold Text and Dynamic Type. (`branding`, `typography`)

## Color (`color`)

- **Never use the same color to mean different things.** Keep color consistent, especially for status and interactivity: if the brand color marks borderless buttons as interactive, the same color on noninteractive text confuses people. (`color`)
- **Define every color for light, dark, and increased contrast.** System colors include all of them. Give each custom color light and dark variants plus a markedly more distinct increased contrast option for each, even if the app ships in one appearance, so Liquid Glass can adapt. (`color`)
- **Never rely on color alone to tell objects apart, show interactivity, or convey essential information.** Give the same information another way, like text labels or glyph shapes, so people with color blindness or other visual disabilities understand it. (`color`)
- **Avoid colors that make content hard to perceive.** Insufficient contrast makes icons and text blend into the background, and people who are color blind may not distinguish some color combinations. (`color`)
- **Check what your colors mean in other countries and cultures.** Red signals danger in some cultures and has positive connotations in others: Stocks shows a rising line in green in English and in red in Chinese. (`color`)
- **Test your color scheme under a variety of lighting conditions.** Bright surroundings make colors look darker and more muted, and dark ones make them bright and saturated, so tune colors for most use cases. (`color`)
- **Test the app on different devices and display profiles.** True Tone adjusts the white point on some iPhone, iPad, and Mac models, and apps for reading, photos, video, or gaming can strengthen or weaken it. On a Mac, preview P3 and sRGB profiles in System Settings > Displays. (`color`)
- **Adjust colors near artwork and translucency.** Variations in artwork can make nearby elements overpowering or underwhelming, so Maps uses a light scheme in map mode and a dark one in satellite mode. Colors also look different behind or on a translucent element like a toolbar. (`color`)
- **Use system colors as the system defines them.** Don't hard-code their values, which can change between releases, or repurpose a dynamic one, like separator color for text. Dynamic system colors are defined by purpose, like backgrounds at each level of hierarchy, or labels, links, and separators. (`color`)
- **When people choose colors, offer the system color picker.** It gives a consistent experience and lets people save colors they can use in any app. (`color`)
- **Expect Liquid Glass to take its color from the content behind it.** In toolbars and tab bars it shifts between light and dark with the content, and their symbols and text stay monochromatic, darker over light content and lighter over dark. Larger elements like sidebars turn more opaque to stay legible. (`color`)
- **Over colorful content, keep toolbar and tab bar labels monochromatic.** Too much color makes control labels hard to read, so use monochrome or an accent color with enough differentiation. With mostly monochromatic content, your brand color can be an effective accent color. (`color`)
- **Keep similar colors in the content layer from overlapping controls.** Colorful content may scroll beneath controls now and then, but its resting state, like the top of a scrolling screen, must stay clearly legible. (`color`)
- **Embed a color profile in every image.** Profiles make colors appear as intended on different displays, and the sRGB color space produces accurate colors on most displays. (`color`, `images`)
- **Use wide color (P3) where it adds richness or meaning, like lifelike photos or status indicators.** Use the Display P3 profile at 16 bits per channel, export PNG, and design on a wide color display. Provide per-color-space variants when similar P3 colors blur together or gradients clip on sRGB displays. (`color`)
- **(iOS, iPadOS) Use three levels of background color for hierarchy.** Primary for the overall view, secondary for groups within it, tertiary for groups within those. Use the grouped set for grouped table views and the system set otherwise. (`color`)
- **(iOS, iPadOS) Use the dynamic foreground colors for their roles.** The four label colors mark content of decreasing importance, placeholder text goes in controls, separator lets content show through while opaque separator doesn't, and link marks text that acts as a link. (`color`)
- **(macOS) Use the dynamic system colors for their named roles.** macOS defines colors for roles like control accent, control text, selected content background, and window background, all viewable in the Developer palette of the standard Color panel. (`color`)
- **(macOS) Expect people's accent color setting to override yours.** Your accent color for buttons, selection highlighting, and sidebar icons appears only when the system setting is multicolor. Fixed-color sidebar icons keep their color because it carries meaning. (`color`)

## Typography (`typography`)

- **Respect each platform's default and minimum text sizes, with system and custom fonts.** The default and minimum are 17 and 11 pt in iOS and iPadOS, and 13 and 10 pt in macOS. Weight affects legibility too, so set a thin custom font larger. (`typography`)
- **Test text legibility in each context, like game text on every platform it runs on.** If text is hard to read, use a larger size, raise contrast through text or background colors, or use typefaces built for legibility, like the system fonts. (`typography`)
- **Avoid light weights, and keep the number of typefaces low.** Ultralight, Thin, and Light are hard to see, especially when small, so prefer Regular, Medium, Semibold, or Bold. Mixing many typefaces obscures the hierarchy and makes the interface feel inconsistent. (`typography`)
- **Know the two system font families: San Francisco, a sans serif, and New York, a serif that works alone or alongside it.** SF includes SF Pro, SF Compact, SF Mono, and Arabic, Armenian, Georgian, and Hebrew variants, most with rounded versions for soft UI. Both are variable fonts with dynamic optical sizes. (`typography`)
- **SF Pro is the system font in iOS, iPadOS, and macOS.** iOS and iPadOS apps can also use New York, which in macOS is available to apps built with Mac Catalyst, and macOS doesn't support Dynamic Type. (`typography`)
- **Use weight and width to build hierarchy, and pair text with SF Symbols.** The system fonts range from Ultralight to Black, SF adds widths like Condensed and Expanded, and SF Symbols use equivalent weights, so symbols match adjacent text at any size. (`typography`)
- **Adjust weight, size, and color to emphasize important information, and keep that hierarchy at every text size.** Preserve the distinctions between text elements when people change text size, and keep primary elements near the top even at very large sizes so people don't lose track of them. (`typography`)
- **When text grows, prioritize the content, not every word.** People enlarging text in a tabbed window don't expect the tab titles to grow, and in a game, dialog matters more than transient hit-damage values. (`typography`)
- **Use the built-in text styles to express hierarchy.** Each sets a weight, size, and leading per text size, like Body for comfortable multiline reading and Headline to set off a heading, and with the system fonts they support Dynamic Type. Never embed the system fonts in the app. (`typography`)
- **Modify a text style with symbolic traits when needed, like the bold trait for another level of hierarchy.** Loose leading helps people keep their place in wide columns and long passages, and tight leading fits a few lines in a list row, but never use tight leading for three or more lines. (`typography`)
- **Adjust tracking in mockups yourself.** Only the running app applies the system font's per-size tracking, so take values from the page's tables (SF Pro is -0.43 pt at 17 pt), without choosing a discrete optical size. (`typography`)
- **Hold custom fonts to the system fonts' legibility and accessibility standard.** Follow each style's minimum sizes and implement Dynamic Type and Bold Text yourself. A game without Apple's Unity plug-ins must still let players adjust text size. (`typography`)
- **Make the layout work at every text size, and test it with the larger accessibility sizes turned on.** Text and glyphs must stay readable throughout. On iPhone or iPad, the setting is Settings > Accessibility > Display & Text Size > Larger Text. (`typography`)
- **(iOS, iPadOS) Design for the whole Dynamic Type range: seven standard sizes, xSmall to xxxLarge, plus five larger accessibility sizes, AX1 to AX5.** At the default size, Large, the Body style is 17 pt with 22 pt leading. (`typography`)
- **Restructure the layout at large text sizes.** When glyphs, timestamps, and container edges crowd inline text, stack the text above secondary items, and use fewer columns. (`typography`)
- **Minimize truncation as text grows.** Show as much useful text at the largest accessibility size as at the largest standard size. Let labels wrap as needed, and truncate scrollable text only if people can open the rest. (`typography`)
- **Scale meaningful icons along with the text.** Icons that carry important information must stay easy to see at large sizes, and SF Symbols scale with Dynamic Type automatically. (`typography`)
- **(macOS) Match standard controls with the dynamic system font variants, since macOS has no Dynamic Type.** Variants cover control content, labels, menus, the menu bar, messages, palettes, titles, tooltips, and document text, giving text the look of system controls. (`typography`)

## Dark Mode (`dark-mode`)

- **Don't offer an app-specific appearance setting.** People would adjust more than one setting, and may think the app is broken when it ignores their systemwide choice. (`dark-mode`)
- **Make the app look good in both appearances, including when Auto switches them while it runs.** The Auto setting changes between light and dark as conditions change throughout the day. (`dark-mode`)
- **Reserve a dark-only appearance for rare cases, like an app for viewing media.** A permanently dark interface lets the UI recede and helps people focus on the media. Stocks on iPhone uses a dark-only appearance. (`dark-mode`)
- **Use colors that adapt to the appearance, never hard-coded values.** Dark Mode uses dimmer backgrounds and brighter foregrounds, not simple inversions, so use semantic colors like label or separator, and give each custom color bright and dim variants in a Color Set. (`dark-mode`)
- **Keep contrast at least 4.5:1, and aim for 7:1 with custom foreground and background colors, especially in small text.** System colors help reach a good ratio, and 7:1 helps content meet recommended accessibility guidelines. (`dark-mode`)
- **Test legibility in both appearances with Increase Contrast and Reduce Transparency, separately and together.** Dark text on a dark background can lose legibility, and Increase Contrast in Dark Mode can even reduce contrast between them, which many people can't read. (`dark-mode`)
- **Use SF Symbols wherever possible.** Symbols adapt automatically and work in both appearances when you tint them with dynamic colors or add vibrancy. (`dark-mode`)
- **Design separate interface icons for light and dark when needed.** A full-moon icon may need a subtle dark outline on a light background but none on a dark one, and an oil-drop icon a slight border to show its edge on a dark background. (`dark-mode`)
- **Make full-color images and icons work in both appearances.** Use one asset if it works in both, otherwise modify it or create light and dark versions, combined in an asset catalog as one named image. (`dark-mode`)
- **Soften white backgrounds in content images.** Slightly darken an image with a white background so it doesn't glow in the surrounding Dark Mode context. (`dark-mode`)
- **Use the system label colors and text views instead of drawing text yourself.** The four label levels, primary to quaternary, adapt automatically, and system views adjust text for the presence or absence of vibrancy on any background. (`dark-mode`)
- **(iOS, iPadOS) Prefer the system background colors so base and elevated levels keep working.** Dim base colors make background interfaces recede, and brighter elevated colors bring forward a popover or sheet and separate apps and windows in multitasking. Custom backgrounds hide these distinctions. (`dark-mode`)
- **(macOS) Add some transparency to a custom component's visible background or bezel, but only in a neutral state.** With the graphite accent color, desktop tinting pulls color from the desktop picture into windows, and transparency lets the component share it. In a colored state, transparency makes the color fluctuate. (`dark-mode`)

## Materials (`materials`)

- **Apply Liquid Glass to custom controls sparingly, only on the most important functional elements.** Standard components get it automatically, and spread across many custom controls it distracts from the content it exists to highlight. (`materials`)
- **Choose materials and effects by meaning and recommended use, never by apparent color.** System settings change their appearance, and Liquid Glass variants shift with a preferred look, reduced transparency, or increased contrast. (`materials`)
- **Use standard materials and effects, like blur, vibrancy, and blending modes, to give the content layer structure beneath Liquid Glass.** They separate foreground elements, like text and controls, from background content while letting color pass through. (`materials`)
- **Keep foreground content legible with system vibrant colors and the right thickness.** Vibrant colors stay legible on any material. Thicker materials give text and fine detail more contrast, and thinner ones keep the background visible for context. (`materials`)
- **(iOS, iPadOS) Use the four standard materials, ultra-thin, thin, regular, and thick, to create distinction in the content layer.** Regular is the default. Each has vibrant colors for labels, fills, and separators, where the default level has the highest contrast and quaternary the lowest. (`materials`)
- **(iOS, iPadOS) Never use the quaternary vibrancy level for labels on thin and ultra-thin materials.** Its contrast is too low there. Every other label level, every fill level, and the separator work on any material. (`materials`)
- **(macOS) Decide where vibrancy helps custom views, and choose behind-window or within-window blending to suit the design.** System views use vibrancy to make foreground content stand out, so test it in varied contexts. macOS offers several purpose-specific standard materials and vibrant versions of all system colors. (`materials`)

## Images (`images`)

- **Ship each bitmap at every scale factor your devices need.** iOS needs @2x and @3x, iPadOS @2x, and macOS @1x and @2x, each named with its suffix in the asset catalog. The pixel density per point is 1:1 at @1x, 2:1 at @2x, and 3:1 at @3x. (`images`)
- **Design images at the lowest resolution and scale up, with vector control points on whole values.** Points aligned at 1x stay aligned to the raster grid at 2x and 3x, which are multiples of 1x. (`images`)
- **Match the file format to the image.** De-interlaced PNG for bitmap art, an 8-bit palette for PNG graphics that don't need 24-bit color, JPEG or HEIC for photos, and PDF or SVG for flat icons and artwork that must scale. (`images`)
- **Test every image on a range of actual devices.** Art that looks great at design time can turn pixelated, stretched, or compressed on real hardware. (`images`)

## Branding (`branding`)

- **Don't use the launch screen for branding.** It disappears too quickly to convey any information, so put branded content in a welcome or onboarding screen at the start of the experience instead. (`branding`)
- **Show your logo only where it's essential for context, and let branding defer to content.** People seldom need reminding which app they're using, and a brand-only element takes room from the content they care about, so brand in refined, unobtrusive ways. (`branding`)
- **To express the brand through color, move it into the content layer.** There it scrolls beneath Liquid Glass controls, which pick it up dynamically. Apple's counterexample is an airport map with brand color on every control. (`branding`)
- **Express the brand through familiar components and standard patterns, even in a stylized interface.** Customize components without changing sizing, placement, or behavior, and keep UI in expected places with standard symbols and navigation and modality conventions, so people can focus on your content. (`branding`)
- **Use the brand's voice and tone in all written communication.** A brand can convey encouragement and optimism with plain words, occasional exclamation marks and emoji, and simple sentence structures. (`branding`)
- **Keep Apple trademarks out of your app name and images.** Apple's trademark guidelines apply to both. (`branding`)

## Key source articles
`color` · `typography` · `dark-mode` · `materials` · `images` · `branding`
