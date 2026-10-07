# Inputs

How people act on an app, from touch, keyboard, and pointer to Apple Pencil, game controllers, and hardware buttons. Apple's position: every input works the way people expect on its platform, responds at once, and is never the only way to do something, because people switch inputs constantly and many rely on alternatives like voice or Switch Control. (`gestures`, `pointing-devices`, `nearby-interactions`)

## Gestures (`gestures`)

- **Never make a gesture the only way to do something.** Many people prefer or need other inputs, like voice, the keyboard, or Switch Control. (`gestures`)
- **Use standard gestures only for standard actions, and respond to every gesture at once.** People expect tap to activate or select everywhere, so never repurpose tap or swipe for an app-specific action, and give feedback that helps people predict the result. (`gestures`)
- **Show when a gesture isn't available.** Otherwise people think the app froze or that they made the gesture wrong: a locked object should show it's locked when dragged, and an unavailable button must look clearly distinct from an available one. (`gestures`)
- **Add custom gestures only for specialized, frequent tasks, as in games and drawing apps, and only alongside standard controls.** A custom gesture must be discoverable and distinct, and an edge swipe for Back never replaces the Back button. (`gestures`)
- **Never conflict with the gestures that open system UI.** People expect them to work consistently everywhere. Games may defer one in specific circumstances. (`gestures`)
- **(iOS, iPadOS) Allow simultaneous recognition of several gestures when it improves the experience.** It rarely helps a nongame app, but a game might let people operate a joystick and firing buttons at the same time. (`gestures`)

## Keyboards (`keyboards`)

- **Support Full Keyboard Access, and in iPadOS don't build your own keyboard navigation for controls.** It reaches every control in iOS, iPadOS, and macOS. Build navigation only for text fields, text views, sidebars, and collection or custom views. (`keyboards`)
- **Don't repurpose a standard shortcut unless its action makes no sense in your app.** People rely on shortcuts working everywhere, though an app without text editing can use Command-I for Get Info. Even game players expect Command-Q to quit. (`keyboards`)
- **Add custom shortcuts only for your most frequent commands, and never extend a standard one for an unrelated command.** Too many make an app seem hard to learn, and Shift-Command-Z for anything but redo confuses people. (`keyboards`)
- **Build custom shortcuts on Command, with Shift as a secondary modifier, Option used sparingly, and Control avoided.** The system uses Control for features like screenshots, and some layouts need modifiers to type characters, as Option-5 types "{" on a French keyboard. (`keyboards`)
- **List modifiers in the order Control, Option, Shift, Command, and write the upper character instead of Shift.** Help is Command-Question mark, not Shift-Command-Slash. Let the system localize shortcuts and mirror them for right-to-left layouts. (`keyboards`)
- **Use modifier keys the way people expect.** Command while dragging moves items as a group, Shift while resizing keeps the aspect ratio, and a held arrow key moves the selection by the smallest unit. (`keyboards`)

## Pointing devices (`pointing-devices`)

- **Respond to mouse and trackpad gestures consistently, and never redefine systemwide ones.** On a Mac, Swipe between pages works the same for document pages, webpages, and images, and even in a game people expect the gestures that reveal the Dock or Mission Control. (`pointing-devices`)
- **Keep interactions the same across gestures, pointer, and keyboard, modifier keys included.** People switch inputs fluidly: if Option-drag duplicates an object with the pointer, it must by touch too. (`pointing-devices`)
- **Let people use the pointer to reveal and hide controls that minimize or fade out automatically.** In iPadOS, holding the pointer over Safari's minimized toolbar reveals it, and moving the pointer shows or hides playback controls over full-screen video. (`pointing-devices`)
- **(iPadOS) Support multiple selection in custom views when needed, and treat pointer and finger input differently only when it adds value.** Standard nonlist collection views already let the pointer drag a selection rectangle, and a video scrubber can let the pointer click a precise seek destination. (`pointing-devices`)
- **(iPadOS) Pad hit regions about 12 pt around an element with a bezel and 24 pt around one without, with no gaps between adjacent bar buttons.** Too small demands precision, too large makes the pointer hard to leave, and gaps make it flicker. (`pointing-devices`)
- **(iPadOS) Support the system content effects, including on custom elements that behave like standard ones: highlight for a small element on a transparent background, lift for a small opaque one, hover for a large one.** Custom toolbar buttons without the highlight look broken. (`pointing-devices`)
- **(iPadOS) Specify the corner radius of a nonstandard element that lifts.** The pointer morphs into the element's shape as it fades, using the system radius by default, so a circular element needs its own. (`pointing-devices`)
- **(iPadOS) Use pointer effects consistently across the app, and keep custom pointer shapes simple.** Every drawing area should feel alike so what people learn carries over, and a shape people don't instantly understand wastes their time. (`pointing-devices`)
- **(iPadOS) Draw custom pointer accessories as clear, simple images, and use the accessory transition to signal a change in state or behavior.** Accessories are small, and moving from plus to circle.slash can show that an add action became unavailable. (`pointing-devices`)
- **(iPadOS) Skip decorative pointer effects and instructional text on the pointer.** People expect every change to be useful, and instructions make an app seem complicated. Data annotations are fine, like Keynote's width and height while resizing an image. (`pointing-devices`)
- **(iPadOS) In a custom hover effect, scale only elements with room to grow, and never add a shadow without scale.** A table row can't expand without overlapping its neighbors, so tint it instead. (`pointing-devices`)
- **(macOS) Use the standard pointer styles to show what an element does or what a drag will do.** The pointing hand marks a link, the open hand draggable content, and operation not allowed an invalid drop. (`pointing-devices`)

## Focus and selection (`focus-and-selection`)

- **Don't move focus unless people do.** People rely on it to know where they are. With a keyboard or game controller, if the focused item disappears, move focus one step away, and with other input just hide the indicator. (`focus-and-selection`)
- **Use the system's focus effects, and make custom ones only if absolutely necessary.** They're tuned to feel responsive and keep your app predictable: text and search fields get a focus ring, and lists and collections highlight the whole row. (`focus-and-selection`)
- **Make focusable exactly what the platform expects.** In iPadOS and macOS, full keyboard access already reaches controls, so make only content focusable, like list items and text fields, not buttons or toggles. (`focus-and-selection`)
- **Let focusing an item also select it only when that won't shift the context.** If selecting opens a new view, make selection a separate action. (`focus-and-selection`)
- **(iPadOS) Organize focus into groups in reading order, each with a primary item.** Tab moves between groups like sidebars, grids, and lists, and arrow keys move within one. Reshape the halo when it doesn't fit an item's contours. (`focus-and-selection`)

## Apple Pencil and Scribble (`apple-pencil-and-scribble`)

- **(iPadOS) Let people mark the moment Apple Pencil touches the screen, right under the tip.** It should feel like pencil on paper, so never require a button or mode first, and allow natural moves like writing in margins. (`apple-pencil-and-scribble`)
- **(iPadOS) Let people choose when to switch between Apple Pencil and finger input, and design for either hand.** Make every control respond to Apple Pencil, because one that ignores it seems broken or suggests a low battery. Keep controls where neither hand covers them, or let people move them. (`apple-pencil-and-scribble`)
- **(iPadOS) Let tilt, pressure, and orientation shape the stroke, and use barrel roll only to modify marking.** Pressure suits continuous properties like brush size, and barrel roll the highlighter's angle in Notes, never navigation or controls. (`apple-pencil-and-scribble`)
- **(iPadOS) Use hover to preview the mark, never to start an action.** Show the tool's size and color at a steady, mid-range value, for Apple Pencil only. Hovering is imprecise, so a pencil near the screen must never trigger anything. (`apple-pencil-and-scribble`)
- **(iPadOS) Use hover for relevant interactions close to where people are marking, and show UI that squeeze reveals near the tip of Apple Pencil Pro.** A menu of tool sizes on squeeze or a modifier key lets people choose without moving the pencil or their hands. (`apple-pencil-and-scribble`)
- **(iPadOS) Treat squeeze as a single, quick gesture for a discrete action, never a continuous one.** People sometimes squeeze hard, so holding a squeeze or squeezing repeatedly is tiring: respond to one squeeze and show the result promptly. (`apple-pencil-and-scribble`)
- **(iPadOS) Respect the systemwide double-tap setting, and keep double tap and squeeze harmless.** People trigger both by accident, so never change content on double tap or do anything destructive with either. Put custom double-tap behavior behind an off-by-default control. (`apple-pencil-and-scribble`)
- **(iPadOS) Make text entry with Scribble fluid: let people write anywhere text belongs, without selecting a field first.** Scribble works in every standard text component except password fields, so a custom field must accept writing right away. (`apple-pencil-and-scribble`)
- **(iPadOS) Keep a text field stationary and undisturbed while people write in it.** Moving it makes people feel they've lost control of their input, so delay any move or resize until they pause, hide placeholder text at the first stroke, and skip autocompletion and autoscrolling. (`apple-pencil-and-scribble`)
- **(iPadOS) When people draw on a PDF or photo, stop PencilKit's dynamic color adjustment.** Canvas colors adapt to Dark Mode by default so drawings look great in both modes, but markup on existing content must stay sharp and visible. (`apple-pencil-and-scribble`)
- **(iPadOS) Add your own undo and redo buttons in compact environments.** The tool picker includes them only in regular ones, so put them in a toolbar, and consider supporting the three-finger undo and redo gesture everywhere. (`apple-pencil-and-scribble`)

## Game controls (`game-controls`)

- **Always support the platform's default input, even if players prefer a controller.** A controller is an optional purchase, but every iPhone and iPad has a touchscreen and every Mac a keyboard and a trackpad or mouse, so keep a fallback to that input. (`game-controls`)
- **Detect a paired controller automatically, and with several connected, use the labels and glyphs of the one each player is using.** Players shouldn't have to set a controller up by hand. To refer to buttons on several controllers, list them together. (`game-controls`)
- **Show virtual controls only while they're relevant, and prefer direct interaction when it fits.** Tapping an object to select it is often more immersive than a selection button. Hide movement controls until a player touches the screen. (`game-controls`)
- **Put movement on the left and camera on the right, clear of the Home indicator and Dynamic Island.** Keep frequent buttons near the thumb, show the thumbstick wherever the thumb lands, and pan the camera by direct touch. (`game-controls`)
- **Make touch controls at least 44x44 pt, or 28x28 pt for minor ones like menus, with visible and tactile press states.** Without them a virtual control feels unresponsive: pair a glow visible under the finger with sound and haptics. (`game-controls`)
- **Draw virtual buttons as the action they perform, and fold related actions into single controls.** A weapon graphic for an attack is memorable, unlike A, X, or R1. Use touch and hold for a powered-up attack, and merge walking and sprinting. (`game-controls`)
- **Show controller buttons with the connected controller's own symbols, and follow UI conventions outside gameplay.** Symbols and colors differ between controllers. In menus, A activates, B goes back, shoulder buttons switch sections, Menu pauses, and Home belongs to the system. (`game-controls`)
- **Favor single-key bindings near W, A, S, D, and let players change them.** Single keys are fastest while the other hand is on the mouse, like I for Inventory. (`game-controls`)
- **Test key binding comfort on an Apple keyboard.** Remap a Control binding from other keyboards to Command, which sits next to the Space bar and is easy to reach from W, A, S, and D. (`game-controls`)

## Action button and Camera Control (`action-button`, `camera-control`)

- **Give the Action button essential functions people use regularly, like "Start Egg Timer", not a shortcut that opens your app.** The system already opens apps. In iOS, run actions in place, as Set Timer starts a Live Activity countdown without opening Clock. (`action-button`)
- **Label each Action button action in three words or fewer, starting with a present-tense verb.** People read the labels in Settings: "Start Race", not "Started Race" or "Start the Race". (`action-button`)
- **Let the system show people how to use the Action button with your app.** It helps them configure the button automatically, so don't repeat the guidance in Settings or other system usage tips. (`action-button`)
- **(iOS) Keep your interface out of the Camera Control overlay's area, and don't duplicate its controls.** The overlay sits beside the control in both orientations, and people want a large viewfinder with as few distractions as possible. (`camera-control`)
- **(iOS) Give each Camera Control control an SF Symbol for its behavior, not its state, and a short name.** The overlay doesn't support custom symbols, and labels follow Dynamic Type, so long names cover the viewfinder. (`camera-control`)
- **(iOS) Add units or symbols to Camera Control slider values, and define prominent values.** Text like EV or % tells people what a slider controls, and the system lands more easily on prominent values, like frequent choices or the major zoom increments. (`camera-control`)
- **(iOS) Disable Camera Control controls that don't fit the current mode, and put the most used ones in the middle.** You can't add or remove controls at runtime, so disable video controls while taking photos. The system remembers the last control people used in your app. (`camera-control`)
- **(iOS) Let people launch your camera experience from anywhere with the Camera Control.** A locked camera capture extension opens it from the locked device, the Home Screen, or within other apps. (`camera-control`)

## Motion sensors and nearby interactions (`gyro-and-accelerometer`, `nearby-interactions`)

- **Use motion data only for a tangible benefit, and explain why in your own permission copy.** A fitness app gives activity feedback and a game uses motion for play, but never gather data just to have it. (`gyro-and-accelerometer`)
- **Outside active gameplay, never manipulate the interface with the accelerometer or gyroscope.** Motion gestures are hard to repeat precisely, physically hard for some people, and can affect battery life. (`gyro-and-accelerometer`)
- **Base a nearby interaction on the physical action, with continuous feedback that sharpens as people get closer.** Bringing iPhone near a HomePod mini to transfer a song feels natural, and finding an AirTag turns a directional arrow into a pulsing circle. (`nearby-interactions`)
- **Never make a nearby interaction the only way to do a task, and mix visual, audible, and haptic feedback.** Not everyone can experience one. Visual feedback suits interaction with the screen, sound and haptics interaction with the surroundings. (`nearby-interactions`)
- **Design for the sensor's directional field of view and for what blocks it.** Outside it a device reports distance but not direction, and people or objects in between reduce accuracy. (`nearby-interactions`)
- **Encourage people to hold the device in portrait, with implicit visual feedback rather than explicit instructions.** Landscape can reduce the accuracy and availability of distance and direction information. (`nearby-interactions`)

## Key source articles
`gestures` · `keyboards` · `pointing-devices` · `focus-and-selection` · `apple-pencil-and-scribble` · `game-controls` · `action-button` · `camera-control` · `nearby-interactions` · `gyro-and-accelerometer`
