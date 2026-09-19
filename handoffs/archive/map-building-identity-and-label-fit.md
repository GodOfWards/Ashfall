# Ashfall Handoff — Building identity, and Close-map labels that fit

Current shipped version: v0.4.9
Implied version-change type: PATCH
Issues: #39 — MAP_BUILDINGS is world data living in RENDERING; #16 — Map view &
UI rendering fixes

## What this is

Two issues taken as one pass because they rewrite the same twenty lines.

**#39** asks where a building's name and anchor belong, given that
`MAP_BUILDINGS` mixes them with the per-building label offsets that are
genuinely a rendering concern. Its stated reason for filing it now still holds:
*"#8 (expand the map, building placement in the 8×8 grid) will add entries to
this table, and it would be better to know which section owns them before that
pass rather than after."*

**#16** has two live findings. Close-map building labels are cut off by the
viewBox edge, and the page overflows horizontally below 480px. Both reproduce at
v0.4.9. The label fix reads the same table #39 moves, so doing them apart means
writing that loop twice.

#16's second finding was fixed years of versions ago and is recorded closed in
the issue. It is not part of this pass.

## Relevant existing state

Verified against `main` @ v0.4.9 by reading the file and by replaying the
placement math in Chromium. Line numbers are v0.4.9's.

### The table as it stands

`MAP_BUILDINGS` (`:4648`) is an 11-entry array inside RENDERING, read in exactly
one place — the `MAP_BUILDINGS.forEach(b=>{…})` loop in `renderMapClose()`
(`:4851`). Each entry carries three fields that are not the same kind of fact:
`name` (a player-visible place name), `anchor` (a `LOCATIONS` id), and `dx`/`dy`
(a label offset in block fractions).

`Pharmacy` and `Hardware Store` deliberately share the coordinate — they are
entered from the same mid-block, and `pharmacy_f0` / `hardware_f0` are two
`LOCATIONS` entries with identical `x,y,z`. The offset, not a second coordinate,
is what keeps them legible as two markers. `Alley` shares `acorn_f0` outright.

### The name is not derivable from the rooms

#39's suggested option 1 — drop `name`, read it from the anchor room — does not
hold. Checked against all eleven entries:

- Five buildings keep their map name in the rooms' `building` field: Acorn
  Apartments, Oak Apartments, Auto Workshop, Police Station, Riverside Freight.
- Six keep it in `room`, with `building` holding a street instead: Corner Store,
  Pharmacy, Hardware Store and Storage Facility all read `building:"Main St"` or
  `"Water St"`; `alley` reads `building:"Poplar St"`; `riverbank` reads
  `building:""`.
- An anchor does not resolve to one room. `acorn_f0` carries nine, and two
  different markers point at it.

The split tracks room count — multi-room buildings put the name in `building`,
single-room ones put the street there — and `roomLabel()` (`:3509`) composes
both correctly, so nothing is visibly wrong. Normalising the fields so a
derivation works would change what `#locBar` prints. That underlying
inconsistency is filed as **#42** and is deliberately not this pass's problem.

### Close labels are placed once and never moved again

This is what makes the label fix more than a clamp.

`renderMap()` (`:4952`) rebuilds the SVG only when `mapZoomMode` changed. A
location change, or a `+`/`−` step change within a mode, animates the viewBox
instead: `mapUpdateViewBox()` (`:4919`) interpolates it over 350ms and never
touches the markup. Building labels are therefore written at build time in
absolute user units and the box then slides underneath them. There is no point
in the current Close path where a label and its live viewBox are both in hand.

**Wide already solved this**, in v0.4.5 and v0.4.8: a fixed pool of `<text>`
nodes bound once by `mapBindStreetLabels()` (`:4774`), then repositioned against
the live box by `mapPositionStreetLabels()` (`:4820`) — called from both the
snap branch (`:4914`) and every animation frame (`:4941`). Close needs the same
split, and both call sites already exist: `mapUpdateViewBox()` calls the Wide
positioner unconditionally and it no-ops outside Wide because `mapStreetLabels`
is empty.

`renderMapClose()` currently emits each label as one or two `<text>` elements
with `text-anchor="middle"` at a raw `p.x` (`:4863`, `:4865`), picking `y1`/`y2`
from the sign of `b.dy` (`:4857`-`:4859`) — which decides whether the name sits
above or below its dot, but never checks the box either.

### How bad it is, measured

Replayed in Chromium at v0.4.9 over every one of the 191 Locations a player can
stand on, at all three Close steps, counting label *lines* (a two-word name is
two independently-positioned `<text>` nodes):

| Close span | Lines on screen | Cut left/right | Cut top/bottom |
|---|---|---|---|
| 130 (step 1) | 114 | **43 — 37.7%** | 7 — 6.1% |
| 260 (step 2, the default) | 332 | **66 — 19.9%** | 31 — 9.3% |
| 390 (step 3) | 674 | **119 — 17.7%** | 17 — 2.5% |

The original v0.4.0 repro still reproduces exactly: from the starting location
at the default zoom, `Pharmacy` renders as `Pharm`.

**Vertical clipping is real** — 9.3% of visible lines at the default step. #16's
text and the superseded `handoffs/map-view-ui-fixes.md` both describe the
horizontal case only. A fix that clamps `x` alone leaves roughly one line in
eleven still cut.

Widest line on the map is `"Apartments"` at **66.3** user units, at the 10px
`.map-bldg-label` face. That is comfortably inside even the 130-unit span, so a
clamp is never impossible — see **Rules** for the invariant.

### The page at phone widths

Still zero `@media` rules in the stylesheet; `main` is still
`grid-template-columns:1fr 320px` (`:61`). Re-measured, identical to the v0.4.7
figures in #16: `scrollWidth` is 476px at 320/360/375/414 (overflow
156/116/101/62px) and clean from 480 up. `#sideMenu` is `position:fixed` and
contributes nothing; the 476px floor is entirely `main`'s two tracks.

Overflow is the smaller half of it. At 375px the room description renders as a
three-words-wide column and the sidebar's right edge is unreachable without
scrolling sideways — the layout is unusable well before it stops overflowing.

## Rules / mechanics

Three parts. Parts 1 and 2 are one continuous edit to the MAP sub-block; part 3
is independent and touches only the stylesheet.

### Part 1 — Building identity moves to WORLD DATA

Add `BUILDINGS` to WORLD DATA, immediately after the `LOCATIONS` object. Keys
are stable ids; use the anchor's own prefix so the pairing is obvious.

```js
const BUILDINGS = {
  acorn:       { name:"Acorn Apartments",  anchor:"acorn_f0" },
  alley:       { name:"Alley",             anchor:"acorn_f0" },
  cornerstore: { name:"Corner Store",      anchor:"cornerstore_f0" },
  pharmacy:    { name:"Pharmacy",          anchor:"pharmacy_f0" },
  hardware:    { name:"Hardware Store",    anchor:"hardware_f0" },
  storage:     { name:"Storage Facility",  anchor:"storage_f0" },
  riverbank:   { name:"Riverbank",         anchor:"riverbank_f0" },
  oak:         { name:"Oak Apartments",    anchor:"oak_f0" },
  auto_shop:   { name:"Auto Workshop",     anchor:"auto_shop_f0" },
  police:      { name:"Police Station",    anchor:"police_f0" },
  industrial:  { name:"Riverside Freight", anchor:"industrial_f0" }
};
```

RENDERING keeps the offsets, keyed by the same id:

```js
const MAP_BUILDING_OFFSETS = {
  acorn:       { dx:-0.05, dy:-0.28 },
  alley:       { dx: 0.32, dy:-0.05 },
  cornerstore: { dx:-0.32, dy:-0.05 },
  pharmacy:    { dx:-0.05, dy:-0.28 },
  hardware:    { dx:-0.05, dy: 0.28 },
  storage:     { dx: 0.32, dy: 0.05 },
  riverbank:   { dx: 0.05, dy: 0.32 },
  oak:         { dx: 0.3,  dy: 0.05 },
  auto_shop:   { dx:-0.05, dy: 0.28 },
  police:      { dx: 0.32, dy:-0.05 },
  industrial:  { dx: 0.32, dy: 0.05 }
};
```

Every `dx`/`dy` is carried across unchanged — these are the hand-tuned values
already in the file, and this pass retunes none of them.

`MAP_BUILDINGS` is deleted. `renderMapClose()` iterates
`MAP_BUILDING_OFFSETS` and reads `BUILDINGS[id]` for the name and anchor.

**`MAP_BUILDING_OFFSETS` is what decides which buildings get a marker.** A
`BUILDINGS` entry with no offsets entry is a building the map does not name, and
`renderMapClose()` simply never reaches it. Every building has one today, so
this pass draws exactly the same eleven markers — but it is the seam #8 needs,
where two buildings sit close enough that only one can carry a label. Say so in
a comment on `MAP_BUILDING_OFFSETS`; it is not inferable from a table where
every key happens to be present.

**`BUILDINGS` holds buildings the map could name, not every building.** The
`anchor` field exists for the map's benefit, so a building that will never carry
a marker has no reason to be listed — and listing one would put its name in a
second place alongside the `building` field its own rooms already carry, which
is the duplication #42 is about. `handoffs/building-placement-and-elm-st.md`
relies on this: the houses it adds are buildings with addresses and no
`BUILDINGS` entry. Say it in a comment on `BUILDINGS`, because a table where
every current entry is map-named cannot show it.

Two comments carry over rather than being rewritten: the note that
Pharmacy/Hardware share an anchor deliberately, and `LOCATIONS`' note that two
buildings sharing an anchor "correctly share the same real (x,y) —
`MAP_BUILDINGS`' dx/dy label-offset (below) is what keeps their map markers
visually distinct." The second names `MAP_BUILDINGS` and now points at a table
in a different section, so retarget it to `MAP_BUILDING_OFFSETS`.

This pass touches **no room definition** and does not go near `roomLabel()`, so
there is no player-visible change from part 1. `BUILDINGS` belongs in WORLD DATA
for the same reason `LOCATIONS` does — the Project Guide counts "static
positional/reference data like map coordinates" as WORLD DATA, and a building's
name and anchor are exactly that. It is reference data, not content, so this
does not make the pass a content pass.

### Part 2 — Close labels bind once, then fit the live box

Mirror the Wide architecture exactly. Nothing here is a new pattern; it is the
one already in the file, applied to the other mode.

**Module state**, beside `mapStreetLabels`:

```js
let mapBuildingLabels = [];  // Close's label pool: one entry per marked building
```

**Constants**, in the MAP sub-block:

- `MAP_BLDG_DOT_R = 6` — the marker circle's radius. It is a literal `r="6"` in
  `renderMapClose()` today and is now read twice, by the circle and by the
  visibility test below, so it becomes one fact with one name.
- `MAP_BLDG_LINE_H = 11` — hoisted out of the loop's `const LINE_H = 11`, since
  positioning needs it too.
- `MAP_BLDG_LABEL_PAD = 6` — breathing room between a clamped label and the
  viewBox edge. A judgment call with no prior convention; **retunable**.

**`renderMapClose()`** emits the dot and the label's `<text>` nodes carrying a
`data-bldg="<id>"` attribute, the way `renderMapWide()` emits
`data-street="<i>"`. It no longer computes `y1`/`y2` or sets `x`/`y` at all —
placement is the positioner's job now.

**`mapBindBuildingLabels()`**, mirroring `mapBindStreetLabels()`: clears the
array, returns early unless `mapZoomMode === "close"`, then for each id in
`MAP_BUILDING_OFFSETS` caches

- `dot` — `mapToSvg(anchor.x/100 + dx, anchor.y/100 + dy)`, the same expression
  `renderMapClose()` uses today;
- the one or two lines, each with its text, its measured width, and its `y`
  offset relative to `dot.y` (the existing rule: `dy < 0` puts the block above
  the dot, otherwise below);
- `half` — **half the widest line**, not each line's own half;
- `top`/`bot` — the block's ink extent, for the vertical clamp;
- the element references, so a pan touches no DOM queries.

**Widths are measured, not tabulated.** `getComputedTextLength()` on the bound
element returns the real width for the real font in user units. A hand-kept
width table would have to be re-measured every time a building is renamed and
does not survive #8 adding buildings. Bind runs only on a zoom-mode change — the
moment that already rebuilds the SVG — so this is a handful of layout reads at a
moment that is already doing more work, not a per-pan cost. (`MAP_LABEL_W`, the
street-name equivalent, is still a hand-measured literal; that is **#43**, and
deliberately not this pass.)

**`mapPositionBuildingLabels(box)`**, called from both places
`mapPositionStreetLabels()` is called — the snap branch and every animation
frame. For each cached label:

1. **Suppress if the dot is off screen.** If the marker circle — centre `dot`,
   radius `MAP_BLDG_DOT_R` — does not intersect `box` at all, hide every line
   and move on. Partial visibility counts as visible.
2. **Clamp horizontally, on a shared centre.**
   `cx = min(max(dot.x, box.x + PAD + half), box.x + box.w - PAD - half)`.
   Both lines take the same `cx`, so a two-line name stays centred as a block
   instead of staggering.
3. **Clamp vertically, moving the block as a unit.** Shift the block so its ink
   extent sits inside `[box.y + PAD, box.y + box.h - PAD]`, and apply that one
   shift to both lines' `y`.
4. Write `x`/`y` on each line and show it.

**Why suppression and not just a clamp.** A clamp alone removes 100% of the
clipping at every step and is never impossible — but it can drag a name 65 user
units, half the closest view, away from the dot it names. Splitting the measured
shifts by whether the building's own dot is on screen settles it:

| | dot on screen | dot off screen |
|---|---|---|
| median shift | 13–27 | 9–41 |
| **max shift** | **33** | **65** |

Every runaway shift belongs to a building whose marker is not drawn at all — a
name pinned to the edge pointing at nothing. Suppressing those leaves every
surviving label both fully inside the box *and* within `MAP_BLDG_LABEL_PAD +
half` of its own dot: **33 units measured, ~39 as the provable bound**.
Suppressing rather than sliding is also what `mapLabelHitsPlayer()` already does
for street names under the player marker, for the same reason — a slide can
cascade.

**The clamp cannot fail today, and should say so rather than assume it.** It is
impossible only when a label is wider than the box can hold, i.e. when
`2*PAD + 2*half > span`. The widest is 66.3 units against the smallest span of
130, so there is 51.7 units of slack. If `lo > hi`, leave `cx = dot.x` — the
label is then cut as it is today rather than placed somewhere arbitrary. A
comment should state the invariant and name the numbers, because #8 adds
buildings and a long enough name would break it.

**Expected result**, measured on the prototype across all 191 Locations: zero
clipped lines at every Close step. Labels suppressed: 21 of 70 visible at step
1, 55 of 203 at step 2, 55 of 402 at step 3 — every one a building whose dot is
off screen.

**Wide is untouched.** It draws no building markers at all, and
`mapBindBuildingLabels()` returning early outside Close is what keeps it that
way.

### Part 3 — One breakpoint for the two-column grid

Add to the document `<style>` block:

```css
@media (max-width:760px){
  main{ grid-template-columns:1fr; }
  #left{ border-right:none; border-bottom:1px solid var(--line); }
}
```

The border swap is not decoration: at one column `#left` spans the full width
and its `border-right` reads as a stray vertical rule down the right edge of the
page.

Verified in Chromium — `scrollWidth` equals the viewport width at 320, 360, 375,
414, 480 and 760, with no element extending past the client edge. `min-width:0`
on the tracks was tested and is not needed; leave it out.

**760px is a judgment call and is retunable.** The measured overflow cliff is
between 414 and 480, so any breakpoint in 480–760 removes the overflow. 760 is
chosen because the layout stops being usable well before it starts overflowing —
at 375px the description is three words wide — and because it is what the
superseded handoff proposed, so it is the value with the most thought already
behind it. Nothing below depends on the exact number.

## Design decisions to make during implementation

Both are narrow; record which was picked in the changelog's Notes/assumptions or
Documentation section rather than choosing silently.

1. **Where the label text is written.** Either `renderMapClose()` emits each
   `<text>` with its content already set and `mapBindBuildingLabels()` only
   measures and caches, or the nodes ship empty and bind sets `textContent`
   first — which is what `mapBindStreetLabels()` does, because its pool is
   generic across streets. **Recommended: emit the text in `renderMapClose()`.**
   Building labels are not a generic pool — each node belongs to one building —
   so the extra step buys nothing, and bind still has to measure either way.
2. **`MAP_BLDG_LABEL_PAD`'s value.** 6 user units is recommended and is what the
   prototype measured. Anything from about 4 to 10 behaves the same; the bound
   on label shift moves with it. Flag it as retunable in the source, per the
   Project Guide's judgment-calls rule.

Neither changes the versioning tier — both stay PATCH.

## Data / schema changes

- **New state fields:** none. `mapBuildingLabels` is module-level beside
  `mapStreetLabels`, deliberately outside `state`, exactly as `mapZoomMode` and
  `mapZoomStep` are.
- **Item schema:** untouched.
- **Room / container / exit schema:** untouched. No room definition is edited.
- **New WORLD DATA table:** `BUILDINGS`. Reference data keyed by a stable id,
  not content — the same category as `LOCATIONS`. It is not persisted: saves
  restore `world`, `doors` and `windows`, and `BUILDINGS` is none of those.
- **`SAVE_KEY` is unchanged.** PATCH, so `versionCompat()` still yields `0.4`
  and existing browser saves keep loading.

## In scope

- `MAP_BUILDINGS` split into `BUILDINGS` (WORLD DATA) and
  `MAP_BUILDING_OFFSETS` (RENDERING), with `renderMapClose()` reading both, and
  the `LOCATIONS` comment that names the old table retargeted.
- A bind/position split for Close building labels, matching Wide's.
- Horizontal and vertical clamping against the live viewBox, on a shared centre,
  with the block moved as a unit.
- Suppression of any label whose dot is off screen.
- `MAP_BLDG_DOT_R`, `MAP_BLDG_LINE_H`, `MAP_BLDG_LABEL_PAD` named in the MAP
  sub-block.
- One `@media` block collapsing `main` to a single column, with the `#left`
  border swap.

## Explicitly out of scope

- **#8** — no building is added, moved or renamed. The offsets table is the seam
  #8 needs; filling it is that pass's job.
- **#42** — the `building` field's two meanings. This pass routes around it with
  a separate table and edits no room definition.
- **#43** — `MAP_LABEL_W` as a hand-measured font width. Deliberately after this
  pass, which is what establishes whether bind-time measurement reads well here.
- **#37** — wide-map street names drawn outside the box. Same family of bug, the
  other mode, and its fix is in `mapPositionStreetLabels()`, which this pass does
  not touch.
- **Label-vs-label overlap between buildings.** No two building label lines
  overlap at any position today — checked pairwise across all 19 lines. That is
  a property of there being eleven buildings, not of the placement logic, which
  has no overlap test at all. `Oak Apartments` and `Acorn Apartments` already
  render nearly edge to edge at the default step. Leave it; #8's Elm pass adds no
  markers, so nothing makes it worse in the meantime.
- **Retuning any `dx`/`dy`.** They carry across byte-identical.
- **The zoom ladder**, `MAP_ZOOM_RANGE`, and anything in Wide mode.
- **A mobile-first redesign, touch or gesture support**, and any change to
  `#sideMenu`, which is `position:fixed` with `max-width:92vw` and already
  behaves at phone widths.

## Sections touched

- **WORLD DATA** — the new `BUILDINGS` table only, plus one comment retarget.
  No room, item, container or exit definition is edited.
- **RENDERING / MAP** — `MAP_BUILDING_OFFSETS`, `renderMapClose()`,
  `mapBindBuildingLabels()`, `mapPositionBuildingLabels()`, the two call sites
  in `mapUpdateViewBox()`, and the bind call in `renderMap()`.
- **The document `<style>` block** — one `@media` rule.

Nothing in ACTIONS, SIMULATION, PLAYER STATE or PERSISTENCE. Per the Project
Guide, a new way of displaying existing state is neither content nor a mechanic,
and part 1 moves reference data rather than adding content.

## UI changes

- **Close map:** no building label is ever cut off. Names near an edge sit up to
  ~39 user units from their dot instead of hanging past the box, and a name whose
  building marker is off screen is not drawn at all. The set of markers, their
  positions and their offsets are unchanged.
- **Below 760px:** the sidebar moves under the main column instead of beside it,
  and the page no longer scrolls sideways. Above 760px nothing changes.
- **No text changes.** No label, button, log line or description is reworded.

## Dependencies / issue linkage

- Fulfils **#39** and **#16**. The pull request closes both: `Closes #39`,
  `Closes #16`.
- **#42** and **#43** were filed from this session's verification. Neither is a
  prerequisite and neither should be touched here.
- **#8** consumes the `MAP_BUILDING_OFFSETS` seam this pass establishes.
  `handoffs/building-placement-and-elm-st.md` specs it and assumes this has
  shipped.
- Nothing is expected to be deferred. If the coding session does cut anything,
  file it as a new issue at wrap-time and reference it in the pull request; if
  it doesn't, say so in the changelog's Documentation section.

## Open questions for Tom

None. The seam (#39), the suppression rule, the clamp geometry and the
breakpoint were all settled during planning, and the two choices left open above
are narrow implementation calls the coding session can make and record on its
own.

## After implementation

Open a pull request carrying the version bump and a new `CHANGELOG.md` entry per
`docs/CHANGELOG_GUIDE.md`, referencing this handoff by path, recording both
"Design decisions" resolutions in it, and closing both issues with `Closes #39`
and `Closes #16`.

For **Validation performed**, the claims worth proving are:

- `git diff origin/main...HEAD -- ashfall.html` is the diff of record.
- **Every `dx`/`dy` and every `name` survives the table split unchanged** —
  eleven entries, checkable one by one against the list in **Rules** above.
- **Zero clipped label lines**, replaying the placement over every Location at
  all three Close steps. The prototype measured 43/66/119 cut lines before and 0
  after.
- **No marker moved.** The same eleven dots at the same coordinates.
- `scrollWidth === clientWidth` at 320/360/375/414/480, and unchanged above 760.
- Syntax check on the extracted `<script>` body, and a runtime check under a DOM
  stub — the hazard in part 2 is a label positioned before it is bound.
