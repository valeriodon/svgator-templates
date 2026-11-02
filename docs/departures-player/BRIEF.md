# Brief: Departures TV player, setup panel

> The direction contract for the redesign of the TV player's setup panel, agreed before the build. The three-step ticket was one of several ranked directions; it is the one I picked. [DESIGN.md](DESIGN.md) records what actually shipped.

**Scope:** the setup panel of `player/index.html` (built by `player/build_player.py`).
**Visitor mode:** operate.
**Audience, first:** SVGator Challenge judges and visitors from the social post, on a laptop or a phone. **Later:** shop owners, on a TV.
**Job:** pick a board, hear it flip with a chosen alert sound, start it full screen.
**Requested:** a live preview of the chosen board and a "Flip now" control.
**Constraints:** standard web controls; board SVGs inlined and driven by the SVGator Player API; works with the keyboard and at 390 px wide.

## Direction contract

**Thesis.** Setup is a three-step ticket (Board, Sound, Depart), and the visitor ends up holding a split-flap ticket strip that states their choices. It refuses the category default: one long settings form with every option visible at once.

**Own world.** The boards' station at night: near-black housing `#0E0F11`, raised panels `#15171B` with `#2B2E34` hairlines, warm white `#F1ECE2` ink, amber `#F2B33D` for selection and the primary action, each board's own brand colour marking its card. Bricolage Grotesque for titles, Geist for controls, Chivo Mono only inside flap cells.

**Story.** The visitor sees four boards, taps one and watches it come alive, chooses a sound and hears it on a real flip, then departs to a full-screen board that rings when it changes.

**First viewport.** Top bar with the Departures wordmark on the left and a three-step stepper (Board, Sound, Depart) in the centre; below, step 1 as a 2 x 2 grid of board cards with stills, the selected card live and outlined in its brand colour; a ticket strip of flap cells pinned at the bottom with Back and Next, Next in amber.

**Form.** A three-step ticket flow. Signature: the ticket strip's flap cells flip character by character whenever a choice changes; "Flip now" makes the live board flip on demand.

**Finish.** Unreviewed and undocumented is unfinished: the build ends with a review against this contract (desktop and mobile screenshots), a verdict, and DESIGN.md.
