# Product: Departures TV player

> Product brief for the TV player. The built page is published separately at [valeriodon/departures-player](https://github.com/valeriodon/departures-player); its source is [`player/build_player.py`](../../player/build_player.py). See also [BRIEF.md](BRIEF.md) (direction) and [DESIGN.md](DESIGN.md) (the design system as shipped).

## Platform

web

## Users
Primary, for now: the judges of the SVGator Challenge on Contra and people arriving from the social post, opening the Departures TV player on a laptop or phone. They decide in a few seconds whether the template family is clever and well made, and they should understand at once that the alert sound is theirs to choose.
Secondary, later: owners of small businesses (cafés, greengrocers, gyms, cinemas, barbers, pharmacies, holiday rentals) who put the board on the TV behind the counter and set it up once with a mouse or a remote.

## Product Purpose
Departures is a family of split-flap board templates made in SVGator (list, schedule and queue layouts). SVGator exports carry no audio, so the TV player shows a board full screen and plays an alert sound each time it flips, through the SVGator Player API. Success: a visitor picks a board, hears the flip with a sound they chose, and leaves convinced the templates are usable for a real business.

## Positioning
The boards behave like an Italian station split-flap display: every row is live text in a monospaced font whose letter spacing matches the flap grid, so anything typed lands in its own flap. The player adds the one thing an SVG export cannot carry, sound, without changing the template.

## Operating Context
Opened from a link in a Contra submission, an X or LinkedIn post, or a GitHub README. Later, left running full screen on a TV in a shop, often unattended, settings changed rarely. Browsers block audio until the first click, so starting the board is also the moment audio is unlocked.

## Capabilities and Constraints
- Single static HTML page (player/index.html, built by player/build_player.py and not committed here), boards inlined as self-contained SVGator exports (player and fonts embedded, start programmatic). Hosted on GitHub Pages: https://valeriodon.github.io/departures-player/
- Four boards: Aurora Café (list), Studio Nine (schedule), Barber Seven (queue), Sea House (welcome).
- Alert sounds synthesized with Web Audio (soft bell, ding-dong, shop bell, chime, wood block), the visitor's own audio file (session only), or none; volume; every update or the first update only.
- The board flips at 0.6 s and 12.6 s of a 24 s loop; the player detects the flips through the Player API keyframe event.
- Settings persist in localStorage. Keyboard: S settings, F full screen.
- Requested additions (2026-10-16): a live preview of the chosen board inside the panel, and a "flip now" control so the sound can be heard without waiting.
- Ticker and QR overrides (2026-10-16): the boards carry an amber LED dot-matrix ticker (one text layer, up to 140 characters). Step 3 lets the visitor retype the ticker and give a link for the QR; the player rewrites the ticker text and generates the QR client side (qrcode-generator from cdnjs) on the mounted board, without changing the template.

## Brand Commitments
Name: Departures. Board fonts: Chivo Mono (flaps), Bricolage Grotesque (titles), Geist (UI). Board palette: near-black housing, warm white letters, amber statuses, one brand color per business. All content in English.

## Evidence on Hand
Board SVG exports (inlined in the published player). The family video: https://valeriodon.github.io/departures-player/media/departures-family.mp4. No testimonials, users or metrics exist; do not invent any.

## Product Principles
- The board is the hero; the panel exists to get a visitor to a flipping board with sound in one or two clicks.
- Show, then explain: hearing the chosen sound on a real flip beats any description.
- Everything a shop owner needs must still work on a TV seen from a distance and on a phone.
