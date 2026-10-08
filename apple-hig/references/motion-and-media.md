# Motion, sound, haptics, and media

How an app moves, sounds, and feels, and how it plays photos, video, and live TV. For Apple, motion, sound, and haptics earn their place only when they carry meaning, stay brief and consistent with their cause, can be turned off, and never carry important information alone, while playback defers to the content and to the controls people already use. (`motion`, `playing-haptics`, `playing-audio`, `playing-video`)

## Choosing the feedback channel

- **Never carry important information on motion or sound alone.** Not everyone can or wants to experience motion, so supplement it with haptics and audio, and give every sound another way to be understood. (`motion`, `playing-audio`)
- **Pair channels so they agree.** As in the physical world, matched feedback feels coherent and natural: match a haptic's intensity and sharpness to the animation it accompanies, and synchronize sound with it. (`playing-haptics`)

## Motion (`motion`)

- **Prefer system components, which include motion and adapt it for you.** They adjust it to accessibility settings and input methods: Liquid Glass responds to direct touch with more emphasis than to a trackpad. The rules below are for custom motion. (`motion`)
- **Add motion only when it supports the experience.** Gratuitous or excessive animation distracts people and can leave them feeling disconnected or physically uncomfortable. (`motion`)
- **Make motion optional.** Not everyone can or wants to experience it, so never use motion as the only way to communicate important information, and supplement visual feedback with haptics and audio. (`motion`)
- **Make feedback motion realistic and consistent with the gesture that triggered it.** Motion that doesn't make sense disorients people: a view revealed by sliding down from the top shouldn't be dismissed by sliding it to the side. (`motion`)
- **Keep feedback animations brief and precise.** They feel lightweight and unobtrusive and often communicate better than prominent animation, as a succinct animation tied to a successful game action gets the message across without distracting from play. (`motion`)
- **In apps, avoid adding motion to frequent interactions.** The system already animates standard elements subtly, and motion on a custom element makes people spend extra attention every time they use it. (`motion`)
- **Let people cancel motion.** Don't make people wait for an animation to finish before they can act, especially one they experience more than once. (`motion`)
- **Consider animated symbols where it makes sense.** With SF Symbols 5 or later, you can apply animations to SF Symbols or to custom symbols. (`motion`)
- **Make a game's motion look great by default on each platform.** A consistent 30 to 60 fps typically feels smooth, and defaults tuned to each device's graphics capabilities spare people from changing settings first. (`motion`)
- **Let people customize a game's visuals for performance or battery life.** For example, let people switch power modes when the system detects an external power source. (`motion`)

## Haptics (`playing-haptics`)

- **Use system haptic patterns only for their documented meanings.** People recognize standard haptics because standard controls play them consistently. If no documented use fits, use a generic pattern or design your own rather than give one a new meaning. (`playing-haptics`)
- **Give every haptic one clear cause, and keep it consistent.** People learn to link patterns with experiences, so a game that plays its mission-failure pattern for completing a level confuses them, and a haptic without cause and effect seems gratuitous. (`playing-haptics`)
- **Avoid overusing haptics.** A haptic that feels right occasionally grows tiresome when frequent, so test with people to find the balance. The best haptics often go unnoticed but are missed when turned off. (`playing-haptics`)
- **In most apps, prefer short haptics that complement discrete events.** Long-running haptics suit gameplay, but in apps they dilute the feedback and distract from the task, and on Apple Pencil Pro they can make holding the pencil less pleasant. (`playing-haptics`)
- **Make haptics optional.** Let people turn off or mute them, and make sure people can still enjoy the app without them. (`playing-haptics`)
- **Keep haptic vibrations from disrupting the camera, gyroscope, or microphone.** Haptics produce enough physical force for people to feel the vibration, which can interfere with experiences that use those features. (`playing-haptics`)
- **Design custom haptics that vary with input and context.** A jump from a tree should hit harder than a jump in place. Combine brief transient events with sustained continuous ones, and tune their sharpness, from soft to crisp, and their intensity. (`playing-haptics`)
- **(iOS) Let standard controls play haptics first, then use the notification, impact, and selection patterns.** Toggles, sliders, and pickers already do. Notification reports an outcome like a deposited check, impact adds a physical metaphor like a view snapping into place, selection accompanies changing values. (`playing-haptics`)
- **(iPadOS, macOS) Expect external devices to play haptics too.** Game controllers can provide haptic feedback in iPadOS and macOS apps, and Apple Pencil Pro and some trackpads can when connected to certain iPad models. (`playing-haptics`)
- **(macOS) With a Magic Trackpad, answer a drag or force click with the alignment, level change, or generic pattern.** Alignment marks a dragged item aligning or a scrubber reaching its end, level change a new pressure level, like fast-forward speeding up. (`playing-haptics`)

## Audio (`playing-audio`)

- **In silent mode, play only the audio people explicitly start.** People switch to silent to avoid unexpected sounds, so silence keyboard clicks, sound effects, game soundtracks, and other audible feedback. Media playback, alarms, and audio and video messaging still play. (`playing-audio`)
- **Adjust only the relative levels in your mix, never the overall volume.** The system volume always governs the final output, in-app sound effects included, and only iPhone's ringer volume is set separately, in Settings. (`playing-audio`)
- **Use the system volume view for audio adjustments.** It pairs a volume slider, whose appearance you can customize, with a control for rerouting audio output. (`playing-audio`)
- **Follow the output people choose.** Reroute without interruption when headphones connect, pause immediately when they disconnect, and allow rerouting to a living room stereo or car radio unless there's a compelling reason not to. (`playing-audio`)
- **Pick the audio category that matches your use of sound, and don't stop other audio needlessly.** The category decides whether sound mixes with other audio, plays in the background, and obeys the Ring/Silent switch. In macOS, notification sounds mix with other audio by default. (`playing-audio`)
- **Choose among the five categories by whether sound is essential.** Solo ambient, like a game soundtrack, and ambient, which lets other music play, obey the silence switch and stop in the background. Playback, like an audiobook, record, and play and record, like video calling, ignore it and can run in the background. (`playing-audio`)
- **Respond to Control Center and headphone controls only when you're playing, in an audio context, or connected over Bluetooth or AirPlay.** People use these controls whether or not your app is in front, and responding otherwise would halt another app's audio. (`playing-audio`)
- **Never repurpose audio controls.** People expect them to behave the same in every app, so don't redefine what one does, and don't respond to controls your app doesn't support. (`playing-audio`)
- **Create custom audio player controls only for commands the system doesn't support.** Examples are custom increments for skipping forward or backward, or content related to the playing audio, like a sports score. (`playing-audio`)
- **Decide how your app responds to audio-session interruptions.** A recording app can ask not to be interrupted by a call unless people accept it, and a VoIP app must end a call when people close an iPad Smart Folio, because restarting the session would unmute the microphone unknowingly. (`playing-audio`)
- **After an interruption, resume only when it fits the interruption and your app.** A media app resumes after a resumable interruption like a call, but not after people start a new playlist, while a game can resume without checking. (`playing-audio`)
- **Let other apps know when your temporary audio ends.** If your app can briefly interrupt the audio of other apps, flag your audio session so they know when they can resume. (`playing-audio`)
- **(iOS, iPadOS) Use the system's sound services to play short sounds and vibrations.** Apple's developer guidance for this is the Audio Services API. (`playing-audio`)

## Video (`playing-video`)

- **Use the system video player, and model any custom player on its behavior and interface.** Its consistent interactions let people focus on content, and a custom player that diverges even slightly frustrates people who can't tell which habits still work. (`playing-video`)
- **Expect the system player to pick full-screen mode for wide video and fit-to-screen for the rest.** Aspect-fill fills the display, cropping edges, by default for 2:1 through 2.40:1. Aspect fit shows the whole frame, letterboxed or pillarboxed, for up to 2:1, like 4:3 and 16:9, and above 2.40:1. (`playing-video`)
- **Always show video at its original aspect ratio, with no letterbox or pillarbox padding in the frame.** Embedded padding keeps the system from scaling video correctly, shrinks it in full-screen and fit-to-screen modes, and breaks edge-to-edge contexts like Picture in Picture on iPad. (`playing-video`)
- **(iOS, iPadOS) Provide additional information about a video only when it adds value.** You can supply an image, title, description, and other useful details, but keep them from obscuring media playback. (`playing-video`)
- **Support the playback interactions people expect on every input.** People expect pressing Space on any connected keyboard, Bluetooth included, to play or pause media on Mac, iPhone, and iPad. (`playing-video`)
- **Don't let audio from different sources mix as people switch modes.** It happens when a source mishandles secondary audio: someone moves a video into Picture in Picture, where the system mutes it, starts a game with music, then unmutes the video. (`playing-video`)
- **When the TV app hands you playback, go from a black screen straight into the content.** The TV app fades to black without showing your launch screen, so present your own black screen at once, then the content, with no splash screens, detail screens, or intro animations. (`playing-video`)
- **Resume playback automatically, without asking, where people left off.** Starting a long clip at its previous end time lets people quickly continue. (`playing-video`)
- **Avoid loading screens, and if loading takes over two seconds, show a black screen with only a centered activity spinner.** Keep it only until enough content loads for playback to begin, and load the rest in the background. (`playing-video`)
- **Keep any branding or images on a loading screen minimal, and keep its background black.** The black background makes the transition into playback smooth. (`playing-video`)
- **Play content for the correct viewer.** Switch automatically to the profile the TV app specifies, and if it specifies none, ask the viewer to choose one before playback so it's known next time. (`playing-video`)
- **When people exit playback, show a contextually relevant screen.** They stay in your app rather than returning to the TV app, so show a detail view of what they watched with a resume option, or else a menu listing it or your main menu. (`playing-video`)
- **Prepare that exit view as soon as you receive a playback notification.** People may exit right after playback begins, and the view needs to be ready when they do. (`playing-video`)

## Live Photos and photo editing (`live-photos`, `photo-editing`)

- **Keep a Live Photo whole: apply every edit to all its frames, or offer to convert it to a still.** Never take it apart or show its frames or audio separately, so people get the same visual treatment and interaction in every app. (`live-photos`)
- **When sharing, let people preview the entire Live Photo, and always offer to share it as a traditional photo.** While one downloads, show a progress indicator, then signal when it's playable. (`live-photos`)
- **Identify a Live Photo with a hint of movement you design yourself.** That's the best way to set it apart from a still, and there's no built-in effect like the one in Photos' full-screen browser, so create custom motion effects. (`live-photos`)
- **Where movement isn't possible, show the system badge in the same place on every photo, never a play button.** The badge, with or without text, typically looks best in a corner, and a play button reads as video playback. (`live-photos`)
- **Where Live Photos aren't supported, show a traditional still photo.** Don't try to replicate the Live Photos experience of a supported environment. (`live-photos`)
- **Expect a photo-editing extension to run from Photos' edit mode, in a modal view with a top toolbar.** People pick it from the extension icon in the toolbar, and dismissing the view saves the edit as a new file, preserving the original, or cancels it. (`photo-editing`)
- **In a photo-editing extension, confirm before Cancel discards edits, and let people preview the result before they close it.** Editing can take a long time, and it's hard to approve an edit without seeing it. Skip the confirmation when no edits have been made. (`photo-editing`)
- **In a photo-editing extension, add no top toolbar, and use your app icon as its icon.** Photos' modal view already has one, so a second confuses people and takes space from the content. Your icon assures people it comes from your app. (`photo-editing`)

## Live-viewing apps (`live-viewing-apps`)

- **Feature live content, and let people start it with one tap or none.** People come to watch: live content in the first tab is one tap away, and a Watch Now button over featured content disappears as full-screen playback begins. (`live-viewing-apps`)
- **Make live content look live on every screen, and show how far along it is.** Playing it is the best cue, plus a Live row and a badge, symbol, or sash per item, setting it apart from video-on-demand. A progress bar shows where people will land. (`live-viewing-apps`)
- **Keep playback the primary action, and list other actions in the same order everywhere.** For example Watch, Start Over, Record, Favorite, and show when the content plays again so people can schedule viewing. (`live-viewing-apps`)
- **Consider a content footer for browsing channels without leaving playback.** Darken it subtly so text stays legible, badge the playing item's thumbnail or tint its progress bar, reuse the program guide's categories, and dismiss it the way it opened, like swiping down after swiping up. (`live-viewing-apps`)
- **Confirm every channel change with instant visual feedback.** It tells people they reached the channel they want and gives the stream time to load. (`live-viewing-apps`)
- **Keep live audio playing while people browse, but stop it when they leave the live tab.** Leaving the tab means they've left the live-viewing context. (`live-viewing-apps`)
- **Open the program guide on what's playing now, and keep that content playing while people browse it.** Make the current program, channel, and time easy to spot so people can return instantly, and keep playback going in Picture in Picture or in the background. (`live-viewing-apps`)
- **Make the program guide effortless to page, scroll, or jump through.** It holds a lot of information, so consider a My Channels or Favorites group for what people watch most. (`live-viewing-apps`)
- **Group program guide content into familiar categories.** Categories like Movies, TV Shows, Kids, Sports, and Popular help people find content, and a content footer should use the same ones. (`live-viewing-apps`)
- **In a cloud DVR, let people start and stop recording from the info panel.** People want to record immediately while streaming, and a program's details view should let them record it alone or with all future episodes. (`live-viewing-apps`)
- **Let people specify precisely what to record.** Offer choices like only the current episode, only new episodes, or only games that involve specific teams. (`live-viewing-apps`)
- **Allow playback and other content-specific actions in your cloud DVR area.** From a content details view there, people can play or delete content and, if applicable, adjust recording settings. (`live-viewing-apps`)
- **Consider a control for managing cloud DVR storage.** Let people delete watched recordings or content older than a set number of days, and ideally overwrite the oldest or watched content automatically so they don't run out of space. (`live-viewing-apps`)

## Key source articles
`motion` · `playing-haptics` · `playing-audio` · `playing-video` · `live-photos` · `live-viewing-apps` · `photo-editing`
