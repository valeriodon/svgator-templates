---
name: Departures
description: The station night of the Departures split-flap boards, carried into the TV player that gives them sound.
colors:
  ground: "#0E0F11"
  panel: "#15171B"
  raised: "#1C1E23"
  line: "#2B2E34"
  line-strong: "#3A3E46"
  well: "#060708"
  ticket-ground: "#09090B"
  ink: "#F1ECE2"
  muted: "#A7AAB1"
  amber: "#F2B33D"
  amber-ink: "#17140C"
  tile-top: "#2C2F35"
  tile-top-low: "#25282D"
  tile-bottom: "#1E2024"
  tile-bottom-low: "#1A1C1F"
  brand-aurora: "#E35D3A"
  brand-studionine: "#D9486F"
  brand-barberseven: "#B5452E"
  brand-seahouse: "#1F8FA8"
typography:
  display:
    fontFamily: "Bricolage Grotesque, Avenir Next Condensed, system-ui, sans-serif"
    fontSize: "clamp(30px, 3.3vw, 46px)"
    fontWeight: 800
    lineHeight: 1.02
    letterSpacing: "-0.025em"
  wordmark:
    fontFamily: "Bricolage Grotesque, Avenir Next Condensed, system-ui, sans-serif"
    fontSize: "22px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Bricolage Grotesque, Avenir Next Condensed, system-ui, sans-serif"
    fontSize: "21px"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Geist, Helvetica Neue, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  control:
    fontFamily: "Geist, Helvetica Neue, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.5
  body-small:
    fontFamily: "Geist, Helvetica Neue, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Geist, Helvetica Neue, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    letterSpacing: "0.14em"
  flap:
    fontFamily: "Chivo Mono, SF Mono, Menlo, monospace"
    fontSize: "clamp(15px, 1.45vw, 21px)"
    fontWeight: 700
    lineHeight: 1
rounded:
  cell: "4px"
  key: "5px"
  segment: "9px"
  control: "12px"
  screen: "14px"
  card: "16px"
  pill: "999px"
spacing:
  hairline-gap: "3px"
  xs: "4px"
  sm: "6px"
  md: "12px"
  lg: "22px"
  gutter: "clamp(16px, 3vw, 40px)"
components:
  button-primary:
    backgroundColor: "{colors.amber}"
    textColor: "{colors.amber-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "11px 18px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "11px 18px"
  step-pill:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "7px 14px 7px 8px"
  step-pill-current:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
  board-card:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
  option-row:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 14px"
  option-row-selected:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
  segmented:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "4px"
  segmented-pressed:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.segment}"
    padding: "9px 10px"
  flap-cell:
    backgroundColor: "{colors.tile-top}"
    textColor: "{colors.ink}"
    typography: "{typography.flap}"
    rounded: "{rounded.cell}"
    width: "1.18em"
    height: "1.6em"
  settings-pill:
    backgroundColor: "rgba(21,23,27,.94)"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "10px 16px"
---

# Design System: Departures

## Overview

**Creative North Star: "The Station at Night"**

Departures is an Italian station split-flap board after the last train: a near-black housing, raised panels separated by hairlines, warm white letters on dark tiles, amber reserved for whatever is about to happen next. The TV player inherits this world from the boards themselves and does not compete with them. The board is always the brightest, busiest thing on screen; the panel around it is quiet, dark and set in a sans that reads like station signage.

The setup is a ticket you fill in. Three steps (Board, Sound, Depart) sit in a pill stepper at the top, the working area scrolls in the middle, and a ticket strip of real split-flap cells is pinned at the bottom, restating every choice in the boards' own mechanism. When a choice changes, the cells flip one by one and the field label flashes amber. That flip is the only expressive motion the panel owns; everything else is restrained state change.

Density is moderate and calm. Controls are large enough for a mouse across a counter or a thumb on a 390 px phone, and the same structure collapses to one column at 880 px.

**Key Characteristics:**
- Near-black housing, raised panels and hairlines; depth by tone, not shadow.
- Warm white ink, never pure white; amber only for selection, current step and the primary action.
- Each board's own brand colour marks its card and its live dot, nothing else.
- Three faces with fixed jobs: Bricolage Grotesque titles, Geist controls, Chivo Mono only inside flap cells.
- The ticket strip of split-flap cells is the signature: it flips as two leaves on a hinge.

## Colors

A station-night palette: four steps of near-black, one warm white ink, one amber, and a brand colour per board.

### Primary
- **Platform Amber** (amber): the only action colour. Fills the primary button (Next, Depart), the current step's number disc, the selected radio dot, focus rings, range and checkbox accents, text selection, and the momentary flash on a changed ticket label. Text on amber is always Amber Ink, never white.
- **Amber Ink** (amber-ink): near-black with a warm cast, used only as text on amber.

### Secondary
- **Board brand colours** (brand-aurora, brand-studionine, brand-barberseven, brand-seahouse): each lives only on its own board card, as the 2 px outline of the selected card and the pulsing Live dot. They are set per card through a `--brand` custom property, not as global accents.

### Neutral
- **Housing** (ground): the page ground of the setup panel.
- **Well** (well): the darkest black, behind anything that holds a board: the full-screen stage, card stills and the step 2 and 3 preview screens.
- **Ticket Ground** (ticket-ground): the pinned ticket footer, a step darker than the housing so the strip reads as a separate object.
- **Panel** (panel): cards, option rows, segmented track, current step pill.
- **Raised** (raised): selected option row and pressed segment, one step above Panel.
- **Hairline** (line): default 1 px borders and the dividers under the bar and over the ticket.
- **Strong Hairline** (line-strong): hover borders, secondary button and pill borders, unselected radio rings, kbd keys.
- **Warm White** (ink): all primary text and flap characters.
- **Platform Grey** (muted): secondary text, leads, unselected steps, ticket field labels at rest, icons.
- **Tile faces** (tile-top, tile-top-low, tile-bottom, tile-bottom-low): the top and bottom halves of every flap cell and of the wordmark's two-tile mark, each as a short vertical gradient.

### Named Rules
**The One Amber Rule.** Amber marks what is chosen or what comes next, and nothing decorative. One amber filled button per view.

**The Brand Stays Home Rule.** A board's brand colour appears only on that board's card. It never tints panels, buttons or the ticket.

## Typography

**Display Font:** Bricolage Grotesque (with Avenir Next Condensed, system-ui)
**Body Font:** Geist (with Helvetica Neue, system-ui)
**Flap Font:** Chivo Mono (with SF Mono, Menlo)

**Character:** A tight, heavy grotesque for names and step titles, a clean neutral sans for every control, and a bold monospace that exists only inside flap cells, exactly as on the boards.

### Hierarchy
- **Display** (800, clamp(30px, 3.3vw, 46px), 1.02, -0.025em, balanced wrap): one step title per view ("Pick a board", "Pick its alert", "Ready to depart").
- **Wordmark** (800, 22px, 1, -0.02em): "Departures" in the top bar.
- **Title** (800, 21px, 1.15, -0.015em): board names on cards.
- **Body** (400, 16px, 1.5): leads, capped at 52ch, in Platform Grey.
- **Control** (600, 16px): buttons, option names, group labels, segments.
- **Body small** (400, 14px; 13px for option descriptions and upload hint): card kinds, helper lines under the preview, key hints.
- **Label** (600, 11px, 0.14em, uppercase): ticket field names (BOARD, ALERT, WHEN, VOL). The Live status on a selected card uses the same voice at 12px and 0.12em.
- **Flap** (700, clamp(15px, 1.45vw, 21px), 1; 14px under 880 px): ticket cell characters, uppercase.

### Named Rules
**The Mono Lives In Flaps Rule.** Chivo Mono appears only inside split-flap cells. Numbers elsewhere (volume readout, step numbers) use Geist with tabular figures.

## Layout

The setup panel is a fixed full-viewport grid of three rows: top bar, scrolling main, pinned ticket. Horizontal padding everywhere is the gutter (clamp(16px, 3vw, 40px)); main's vertical padding is clamp(20px, 3.2vh, 36px). Content is capped at 1180px and centred.

- **Top bar:** three columns (1fr auto 1fr): wordmark left, stepper centred, "Back to the board" right when returning from the stage. A hairline below.
- **Step 1:** a 2 x 2 grid of board cards, gap clamp(12px, 1.6vw, 20px). The grid width is tied to viewport height (min(1000px, (100dvh - 430px) x 1.778 + 20px), never below 640px) so all four cards and the ticket fit one desktop screen. The step heading shares that width.
- **Steps 2 and 3:** two columns, preview 1.55fr and controls minmax(300px, 1fr). The preview spans both rows on the left; heading and lead sit above the controls on the right.
- **Ticket:** a single row of fields (gap 18px) with Back and Next pushed to the right.
- **Rhythm:** 6px between option rows, 10 to 12px inside rows, 22px between control groups, 14px between a preview and its Flip now line.

**Responsive (max-width 880px):** the stepper drops to its own full-width row under the wordmark, justified across; cards and options go to one column; steps 2 and 3 reorder to heading, preview, controls. The ticket stacks: fields become rows with a fixed 4.6em label column, the VOL field is hidden, cells shrink to 14px, and Back and Next split the width equally. On the full-screen stage, a portrait phone gets the turn-phone hint.

## Elevation & Depth

Flat by tone. Depth comes from the four near-black steps (well, ground, panel, raised) and from hairlines, not from shadows. The only shadows are physical: flap cells sit on a 1 px contact shadow, and a pressed segment lifts by the same amount. Overlays on the stage (settings pill, turn hint) use a 94% Panel tint with a strong hairline instead of blur or shadow.

### Shadow Vocabulary
- **Tile contact** (`box-shadow: 0 1px 2px rgba(0,0,0,.8)`): under every flap cell.
- **Segment lift** (`box-shadow: 0 1px 2px rgba(0,0,0,.4)`): the pressed half of the segmented control.

### Named Rules
**The Housing Rule.** If something needs to stand forward, move it one tone step up and give it a hairline. Do not add a shadow.

## Shapes

Soft, rounded rectangles scaled to their role: 16px for board cards, 14px for preview screens, 12px for buttons, option rows and the segmented track, 9px for segments inside it, 5px for keycaps, 4px for flap cells. Anything that floats or navigates (step pills, settings pill, turn hint, "Back to the board") is a full pill. Radio dots and step discs are circles. Every container that holds a board clips it (overflow hidden) to its radius.

The split-flap tile is the recurring silhouette: two halves with a dark 1px seam between them and two tiny hinge pins (2 x 4px, near-black) at the left and right edges of the seam. The wordmark mark repeats it as two 13 x 18px tiles with a seam band across the middle.

## Components

### Buttons
Quiet outlined controls with one amber exception.
- **Shape:** gently rounded (12px).
- **Primary:** amber fill and border, Amber Ink text, 600 weight, 11px 18px padding. Used for Next and Depart only. Hover brightens slightly (brightness 1.06).
- **Secondary:** transparent with a strong hairline border, ink text. Hover moves the border to Platform Grey. Used for Back, Flip now, and the Upload your own label.
- **Disabled:** 40% opacity, default cursor (Back on step 1).
- **Focus:** 2px amber outline, 3px offset, everywhere.

### Navigation: top bar and stepper
- **Stepper:** three pill buttons, each a 24px circular number disc plus a word. Upcoming steps are Platform Grey with a strong-hairline disc; the current step gets a Panel fill, strong-hairline border, ink text and a filled amber disc with Amber Ink numeral; completed steps keep grey text with an amber ring and amber numeral. The current step carries `aria-current="step"`. Every step is clickable.
- **Close:** "Back to the board", a pill secondary button, shown only when setup is reopened from the stage.

### Cards / Containers: board cards
- **Corner Style:** 16px, content clipped.
- **Background:** Panel, with a 16:9 still in a Well-coloured frame on top and a meta row below (name in Title, kind in Body small grey).
- **Border:** 1px hairline at rest; hover raises the card 2px and strengthens the hairline; selected becomes a 2px outline in the board's brand colour (margin -1px to hold the size).
- **Selected state:** the still is replaced by the live, playing board, and a Live status (brand dot pulsing at 1.6s, label in the Label voice) appears at the right of the meta row.
- **Semantics:** the four cards form a radiogroup; each card is a button with role radio and `aria-checked`.

### Inputs / Fields
- **Option rows (alert sounds):** Panel rows, 12px radius, 10px 14px padding, in a 2-column grid (1 column under 880px). Content is a radio ring, a bold name over a 13px grey description, and a speaker icon (inline SVG) except for Silent. Selected rows move to Raised with a strong hairline and an amber ring with an 8px amber dot. Choosing a row plays its sound.
- **Segmented control (When):** a Panel track with 4px padding and 4px gap holding two equal segments; the pressed segment is Raised, ink text, with the segment lift shadow. Uses `aria-pressed`.
- **Range (Volume):** native range with amber accent colour, followed by a tabular Geist readout. Releasing the thumb plays the sound once.
- **Checkbox:** native 18px box with amber accent and a 500-weight label.
- **File upload:** a visually hidden file input behind a secondary-button label; focus on the input draws the amber ring on the label. Helper text in 13px grey.
- **Text fields (Ticker message, Link for the QR code):** step 3 only, under the preview. Panel fill, strong hairline, 12px radius, 11px 14px padding, ink text, placeholder in #7D8088; focus turns the border amber with the 2px amber ring. The ticker textarea is 15px Geist 500 set in capitals (it previews the LED line), caps at 140 characters with a tabular counter; the URL field shows a one-line helper that confirms where the QR now points. Both apply to the live board 250 ms after typing stops and persist with the other settings; empty means the board keeps its own message and QR.
- **Keycaps:** 12px Geist 600 on a strong hairline with a 2px bottom border, 5px radius.

### Preview screen
A 16:9 Well-coloured frame with a 14px radius and hairline border that receives the single live board on steps 2 and 3. Below it, a Flip now secondary button and a one-line grey hint. Only one board is ever mounted and playing; it is moved between card, preview and stage.

### Full-screen stage
The departed board fills a Well-coloured fixed stage, held at 16:9 (min(100vw, 177.78vh)) and centred. No chrome is visible at rest.
- **Settings pill:** bottom right, a pill of 94% Panel with a strong hairline and 600 14px text ("Settings (S)", the key hint hidden under 880px). Invisible until the pointer moves; fades in at .35s and hides again after 2.5s of stillness. Always visible on keyboard focus.
- **Turn-phone hint:** a centred pill at the top, same material, 14px text, shown only on a portrait screen up to 880px wide.

### Ticket strip (signature component)
The ticket is the pinned footer on Ticket Ground with a hairline above. Each field is a Label-voice name over a row of split-flap cells (BOARD 12 cells, ALERT 10, WHEN 10, VOL 4; gap 3px, 2px on phones). An off-screen polite live region repeats the whole ticket as a sentence for screen readers; the cells themselves are `aria-hidden`.

- **Cell:** 1.18em x 1.6em of Flap type, 4px radius, a top half and a bottom half each showing half the character, the top half on the lighter tile gradient with a 1px dark seam, hinge pins on both sides, tile contact shadow.
- **The flip:** when a character changes, the new character is already printed under a top leaf showing the old one. The top leaf falls on its bottom hinge (rotateX 0 to -90deg, darkening to 45%, .14s, ease-in cubic-bezier(.55,0,1,.6)), then a bottom leaf with the new character lands from 90deg to 0 (.14s, ease-out cubic-bezier(0,.4,.4,1), brightening from 60%). The bottom half is updated and both leaves removed at 300ms. Cells in a field start 22ms apart, left to right, so a word ripples.
- **Changed flash:** when any cell of a field changes, its label snaps to amber and fades back to grey over .3s after 900ms.

### Named Rules
**The Real Flap Rule.** Anything that restates a choice in the ticket is shown in split-flap cells that flip as two leaves on a hinge, with the new character revealed under the falling leaf. Never cross-fade or slide a flap character.

**The One Live Board Rule.** Exactly one board plays at a time, and it moves to wherever the visitor is looking.

## Do's and Don'ts

### Do:
- **Do** keep amber for selection, the current step, focus and the single primary action per view.
- **Do** mark a board only with its own brand colour, and only on its card.
- **Do** separate surfaces with tone steps (well, ground, panel, raised) and 1px hairlines.
- **Do** use Chivo Mono only inside flap cells, uppercase, and Geist with tabular figures for any other number.
- **Do** give every interactive element the 2px amber focus ring at 3px offset.
- **Do** honour reduced motion: flap cells swap instantly, the Live dot stops pulsing, card, pill and label transitions are removed.
- **Do** collapse to one column at 880px and keep Back and Next as equal-width thumb targets.

### Don't:
- **Don't** use pure white or pure black for panel text or surfaces; ink is warm white and the darkest surface is Well (white QR tiles inside the boards are board content, not panel material).
- **Don't** add drop shadows, glows or blur to panels, cards or overlays; the only shadows are the tile contact and segment lift.
- **Don't** put a second amber filled button in a view, or tint panels with amber or a brand colour.
- **Don't** set flap characters in Bricolage Grotesque or Geist, or animate them with fades or slides.
- **Don't** show more than one playing board at once.
