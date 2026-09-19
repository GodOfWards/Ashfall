> **SUPERSEDED — do not implement this handoff.**
>
> **Status: inert.** Written against v0.4.0; re-verified against v0.4.7 and
> found partly wrong. It is kept for its commit date and for the record of
> what was measured at the time, not as an instruction. Nothing below is a
> live spec.
>
> Its three findings now stand as:
>
> | Finding | Status at v0.4.7 | Live tracker |
> |---|---|---|
> | 1. Close-map building labels clip at the view edge | Still open; the recommended fix still applies | **#16** |
> | 2. Wide-map vertical street labels unreadable | **Fixed** — twice over, and the code described here (`mapRepeatedLabel()`, `mapBlockLabels()`, `textPath`) no longer exists in the file | residual label collisions: **#28** |
> | 3. Page overflows on phone-class viewports | Still open; numbers re-measured and unchanged | **#16** |
>
> Implementing section 2 as written would edit code that is not there. The
> re-verified findings live in **#16** — go there, not here.

# Ashfall Handoff — Map View & UI Fixes

Current shipped version: v0.4.0
Implied version-change type: PATCH
Roadmap item: Tier 1, item 17 — Map View & UI Rendering Fixes (new item;
none of this was previously tracked on the roadmap)

## What this is

Three concrete, reproduced rendering/layout bugs in the existing UI —
not new content or a new mechanic, so per the Project Guide ("Rendering
is its own concern... a new way of *displaying* existing state... shouldn't
be forced into either bucket") this is a RENDERING-only pass. Found by
loading the current-version HTML in a real browser (Playwright/Chromium)
and driving it — not from reading the code alone, per the Project Guide's
"proven, not asserted" rule.

## Relevant existing state

Verified against the current HTML (search for the cited names):

- **Close-map view**: `MAP_MARGIN=55`, `MAP_SPACING=130`,
  `MAP_CLOSE_VIEW=260`. `renderMapClose()` draws each `MAP_BUILDINGS`
  entry as a dot at `anchor + {dx,dy}` (grid units) plus one or two
  `<text text-anchor="middle">` lines for its name. `renderMap()` /
  `mapUpdateViewBox()` center the SVG's `viewBox` on the player's current
  node in a fixed 260×260 window. `#mapSvg` has no `overflow` override, so
  it clips to its `viewBox` (SVG default is `overflow:hidden` on the root).
  Text position is never checked against the current viewBox bounds.
- **Wide-map view**: `renderMapWide()` draws every street name via
  `<textPath>` bound to that street's own path (`MAP_STREETS` chains),
  repeated 3× (`mapRepeatedLabel()`). For the five vertical streets (4TH,
  2ND, 1ST, 3RD, 5TH), the path itself runs vertically, so `textPath`
  rotates each glyph to follow it — the label renders as a stack of
  individually 90°-rotated characters rather than one readable vertical
  line. `MAP_WIDE_VIEWBOX = {x:20,y:20,w:610,h:480}` is fixed regardless
  of viewport.
- **Overall layout**: `main{ grid-template-columns:1fr 320px }` (no media
  query anywhere in the stylesheet) plus `#sideMenu{ width:360px }` fixed.
  `#left`'s content (room text, move/here action buttons) has no min-width
  constraint of its own, but the combined layout's intrinsic minimum width
  exceeds any phone-class viewport.

## Rules / mechanics

N/A — this is a rendering-only pass. No PLAYER STATE, WORLD DATA, or
SIMULATION rule changes.

## Findings (reproduced, not guessed)

### 1. Close-map building labels clip at the view edge
`renderMapClose()` centers a fixed 260×260 window on the player and
places each building's two-line label with `text-anchor="middle"` at a
raw `{dx,dy}` offset from its anchor node, with no check against the
current viewBox. Because `#mapSvg` clips to its viewBox, any label whose
estimated width pushes past the edge gets visually truncated.

Reproduced in-browser: starting the game (player in Acorn Apartments) and
opening the menu renders "Pharmacy" as **"Pharm"** — the last four
characters are clipped by the SVG boundary. Confirmed via
`getBBox()`: the label's rendered box runs to x≈401, while the current
viewBox's right edge is at x=380.

This isn't a one-off — replaying the same math (`mapToSvg`/`MAP_BUILDINGS`
offsets) across every street/anchor node as a hypothetical player position
finds **at least 8 distinct player-position × building combinations** that
clip today, including:
- **Oak Apartments' own label clips while standing at Oak Apartments** —
  a building's name is unreadable from its own doorstep.
- Pharmacy clips when standing at Acorn Apartments (i.e. from the game's
  actual starting location).
- Riverside Freight, Auto Workshop, Riverbank, Acorn Apartments (from Oak)
  also clip from at least one nearby standing position.

### 2. Wide-map vertical street labels are unreadable
Vertical streets' `textPath`-bound labels render as a column of
individually-rotated single characters (confirmed via screenshot — see
`4TH ST`/`2ND ST`/etc. in the Wide view) instead of one legible line of
text. Horizontal streets (Maple/Poplar/Main/Water) are unaffected — only
the five N–S streets use a vertical path. Additionally, a street's
repeated label can render directly under the player marker (observed:
"POPLAR ST" text sitting on top of the player dot when the player is on
Poplar St), though the player dot itself still paints on top since it's
drawn last.

### 3. Page overflows horizontally on every phone-class viewport
`main`'s `1fr 320px` grid plus the always-360px `#sideMenu` give the page
an intrinsic minimum width around 476px, with no responsive breakpoint
anywhere in the stylesheet. Measured `document.documentElement.scrollWidth`
vs. viewport width in-browser:

| Viewport width | scrollWidth | Horizontal overflow |
|---|---|---|
| 320px | 476px | 156px |
| 375px | 476px | 101px |
| 414px | 476px | 62px |
| 768px | 768px | 0px (fine) |

This affects every current phone size, not just small/unusual ones — the
game is not usable without horizontal scrolling below ~476px wide today.

## Design decisions to make during implementation

Each of these is a rendering-technique choice, not a game-design call —
narrow enough to leave to the coding session, with a recommended default.
Record which option was taken in the changelog's Notes/assumptions.

1. **Close-map label clipping fix.**
   - *Recommended default:* after computing each label's target x/y,
     estimate its rendered width (character count × a fixed per-character
     width is fine — exact font metrics aren't needed) and clamp the
     label so its bounding box stays within the *current* viewBox with a
     small (~6px) inner padding — e.g. by shifting the anchor point or
     switching `text-anchor` from `middle` to `start`/`end` for labels
     that would otherwise overflow one side, rather than changing
     `MAP_MARGIN`/`MAP_CLOSE_VIEW` globally (which would just move the
     problem to different buildings/positions).
   - Alternative considered and not recommended: enlarging
     `MAP_CLOSE_VIEW` — reduces how often it happens but doesn't eliminate
     it (the map math above shows it recurs at multiple margins), and
     shrinks everything else on the Close map.
2. **Wide-map vertical street label legibility.**
   - *Recommended default:* for the five vertical streets, stop using
     `textPath` for the label and instead draw one `<text>` block with a
     `transform="rotate(-90 x y)"` at the path's midpoint (mirroring how
     horizontal streets already read as one clean line) — same repeated
     `mapRepeatedLabel()` string is fine, just rendered as a rotated block
     instead of glyph-by-glyph path-following. Horizontal streets keep the
     existing `textPath` approach unchanged.
   - The player-marker-under-label overlap (finding 2's second half) is
     minor and can be left as-is unless the rotation change above happens
     to resolve it incidentally.
3. **Mobile/narrow-viewport layout.**
   - *Recommended default:* add a single responsive breakpoint (suggest
     `@media (max-width: 760px)`, retunable) that switches `main` to a
     single column (`grid-template-columns:1fr`, sidebar panels stacking
     below the room/action content) and caps `#sideMenu`'s width to
     `min(360px, 92vw)` so the menu itself can never exceed the viewport.
   - This handoff does not ask for a from-scratch mobile redesign — just
     removing the horizontal-overflow bug at existing phone widths using
     the existing panel components, restacked.

## Data / schema changes

None. No PLAYER STATE, item schema, or room/container/exit schema fields
are added or changed.

## In scope

- Fix Close-map building-label clipping so no label's text is cut off by
  the SVG boundary, at any player position (verify against the ~8
  reproduced cases above, not just the Pharmacy example).
- Fix Wide-map vertical street-name legibility so vertical streets read
  as one line of upright-readable (rotated-as-a-block, not glyph-rotated)
  text, matching horizontal streets' readability.
- Add a responsive breakpoint eliminating horizontal page overflow at
  320/375/414px viewport widths (re-measure `scrollWidth` vs. viewport
  width at all three after the fix, per the Project Guide's "proven, not
  asserted" rule).

## Explicitly out of scope

- Any new map content (new buildings, new streets, new zoom levels) —
  that's roadmap item 14 (Expand the Map), untouched here.
- A full mobile-first redesign, touch-specific controls, or gesture
  support — only the overflow bug is in scope.
- Any change to `LOCATIONS`, `MAP_STREETS`, or `MAP_BUILDINGS` *data*
  (coordinates, anchors, offsets) — this pass changes how existing data
  renders, not the data itself. (An alternate fix to finding 1 by
  retuning individual buildings' `dx`/`dy` offsets is not recommended —
  see Design decisions above — but if the coding session finds the
  clamping approach insufficient for a specific building, that's a
  narrow follow-up, not license to re-tune the whole table.)
- Desktop layout changes above the chosen breakpoint — current
  desktop/tablet layout is not reported as broken and shouldn't change.

## Sections touched

UI/RENDERING only — specifically the MAP sub-block (`renderMapClose`,
`renderMapWide`, and their shared helpers) and the top-level stylesheet
(`main`, `#sideMenu`). No WORLD DATA, PLAYER STATE, ACTIONS, or SIMULATION
code should need to change for any of the three findings.

## UI changes

- Building name labels on the Close map will always render fully
  on-screen instead of being cut off near view edges.
- Vertical street names on the Wide map will read as upright, legible
  text blocks instead of a stack of sideways-rotated letters.
- On phone-width screens, the game will no longer require horizontal
  scrolling — the sidebar panels (Inventory/Here/Craft) will stack below
  the main room/action content instead of being squeezed into a
  too-narrow fixed column.

## Dependencies / roadmap linkage

Fulfills new Tier 1 roadmap item 17 (Map View & UI Rendering Fixes) —
add this item to the roadmap only if this handoff's implementation is not
completed in full; per the Project Guide, the roadmap doesn't need an
entry for something a coding session ships in the same pass. Not a
prerequisite for, and doesn't touch, roadmap item 14 (Expand the Map) or
item 9 (splitting `buildStreetsAndOutdoor()`).

## Open questions for Tom

None. All three findings are reproduced bugs with a recommended,
narrow-scope fix; the choices above are implementation technique, not
scope or design calls.

## After implementation

Write the `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, referencing this
handoff by filename, and record which option was taken for each of the
three "Design decisions" above (including the actual breakpoint width
used) in the entry's Notes/assumptions section.
