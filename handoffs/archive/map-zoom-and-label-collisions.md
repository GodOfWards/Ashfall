# Ashfall Handoff — Map Zoom Ladder & Wide-Map Label Collisions

Current shipped version: v0.4.7
Implied version-change type: PATCH
Issues: #27 — Make the map's +/- zoom controls work
        #28 — Wide-map street names can collide at an intersection

## What this is

Two changes to the MAP sub-block, taken as one pass because they land in the
same code: the `+`/`−` buttons shipped inert in v0.4.5 get a working zoom
ladder, and the street-name placement rule that ladder retunes gets its
intersection-collision fix. #28 says so itself — its recommended fix "folds
naturally into whatever #27's zoom ladder does to the tiers."

Rendering only. No new persistent state, `SAVE_KEY` untouched, no WORLD DATA.

## Relevant existing state

Verified against `main` @ v0.4.7 by reading the file.

**Anchor on the names below, not on line numbers.** A v0.4.6-era audit in #33
was invalidated wholesale by v0.4.7's WORLD DATA reshuffle; every symbol here
is unique enough to find by search.

### Geometry

```
MAP_SPACING   130    intersection → intersection (one block)
                     65 = node → node, mid-blocks included
MAP_MARGIN    55
grid          MAP_MIN_COL -1 … MAP_MAX_COL 6, MAP_MIN_ROW -4 … MAP_MAX_ROW 3
content       (MAP_MAX_COL − MAP_MIN_COL) × MAP_SPACING = 910 units square
```

`MAP_CLOSE_VIEW = 260` is exactly `2 × MAP_SPACING`. `MAP_WIDE_VIEW = 800` is
not on the block pitch (`6 × MAP_SPACING` = 780); it was hand-picked in v0.4.5.

### Render pipeline

- `mapZoomMode` — module-level `let`, `"close"` or `"wide"`, deliberately **not**
  in `state` so `SAVE_KEY` stays `ashfall_save_v0.4`.
- `mapTargetViewBox(node)` — picks a span from `mapZoomMode` via a ternary and
  returns a player-centred box. Deliberately **not** clamped to the town's
  bounds; leave that as is.
- `mapUpdateViewBox(node, snap)` — snaps, or animates over 350ms. It already
  interpolates `w` and `h` alongside `x` and `y`, so a span change animates with
  no new code. Calls `mapPositionStreetLabels()` every frame.
- `renderMap()` — rebuilds SVG content only when `mapRenderedZoom !== mapZoomMode`;
  otherwise animates the box. This is already a level-of-detail cache keyed on
  mode. `mapLastNode` holds the current map node.
- `mapBindStreetLabels()` — early-returns unless `mapZoomMode === "wide"`, so
  **Close never draws street names**. Caches element refs plus each street's
  geometry (`a`, `b`, `angle`, `horizontal`, `els`) in `mapStreetLabels`.
- `mapPositionStreetLabels(box)` — places the pooled labels against the live
  viewBox, per frame.
- `mapLabelPositions(lo, hi)` — returns 1, 2 or 3 positions along a street's
  **visible** stretch: midpoint for one, `MAP_LABEL_INSET` in from each end for
  two, both plus the midpoint for three.

### Label constants

```
MAP_LABEL_OFFSET       5     nudges a name off its own street line
MAP_LABELS_PER_STREET  3     fixed pool size per street
MAP_LABEL_INSET       55     "half the widest street name, retunable"
MAP_LABEL_TIERS              600 → 3 labels, 300 → 2, 110 → 1, below → none
MAP_PLAYER_R_WIDE     12     player marker radius in Wide
```

`.map-street-name` is `font-size:15px`; `.map-bldg-label` is `10px`. Inside a
`viewBox` these are **user units**, so apparent size scales with the span.

### The buttons

```html
<button data-zoom="close" class="active">Close</button>
<button data-zoom="wide">Wide</button>
<button id="mapZoomIn" disabled>+</button>
<button id="mapZoomOut" disabled>&minus;</button>
```

The mode toggle binds `#mapZoomToggle button[data-zoom]`. **The `+`/`−` buttons
must never gain a `data-zoom` attribute** — it would capture them into the
Close/Wide handler. `#mapZoomToggle button:disabled{ opacity:.4 }` already
styles the disabled state; no CSS change is needed.

### Rendered size, and why it constrains the ladder

`#mapSvg` is `width:100%` inside a 460px `#sideMenu`, so it renders at **~420
CSS px**. (#28 measured a 17-user-unit overlap as "about 9 CSS px", giving a
scale of 0.53 and confirming ~423px.) Apparent text size is
`fontUnits × 420/span`:

| Span | Building label (10u) | Street name (15u) |
|---|---|---|
| 130 | 32.3px | — |
| 260 | 16.2px | — |
| 390 | 10.8px | 16.2px |
| 520 | 8.1px | 12.1px |
| 650 | 6.5px | 9.7px |
| 780 | 5.4px | 8.1px |

Close's ceiling is where its building labels cross ~10px, at span ≈ 420.

### Why #28's collisions happen

`mapLabelPositions()` insets from the **clipped visible** stretch, not from the
street's full extent, so an inset position frequently lands near an
intersection. A horizontal name sits `MAP_LABEL_OFFSET` above its line and a
vertical name the same distance beside its line, so at a crossing two 15-unit
bands can overlap. #28 measured 116 of 176 positions with at least one
overlapping pair, worst case `ELM ST` over `3RD ST` at 17 × 17 units.

## Rules / mechanics

Every number below is **retunable** and none has a prior convention behind it.

### 1. The zoom ladder

Span is a whole number of blocks:

```
span = zoomStep × MAP_SPACING
```

- **Close: `zoomStep ∈ {1, 2, 3}`** → 130 / 260 / 390. Base **2**.
- **Wide: `zoomStep ∈ {3, 4, 5, 6}`** → 390 / 520 / 650 / 780. Base **6**.

`MAP_CLOSE_VIEW` becomes `2 × MAP_SPACING` (260, unchanged). `MAP_WIDE_VIEW`
becomes `6 × MAP_SPACING` — **780, down from 800**. This is a deliberate 2.5%
change to shipped v0.4.5 behaviour, approved during planning, and must be called
out in the changelog rather than passed over.

`mapTargetViewBox()` stops selecting the span from `mapZoomMode`; it reads
`zoomStep`. `mapZoomMode` now only bounds the valid range.

**`+` zooms in, which means a *smaller* span — `mapZoomIn` decrements `zoomStep`
and `mapZoomOut` increments it.** `zoomStep` counts blocks, so more blocks is
further out. Easy to invert by accident.

### 2. Where the clamp runs

**Clamp where the index changes, never where the span is read.** Two sites, both
existing handlers:

```
click +/−   → zoomStep = clamp(zoomStep ∓ 1, rangeFor(mapZoomMode))
mode toggle → zoomStep = clamp(zoomStep,     rangeFor(mapZoomMode))
```

`mapTargetViewBox()` then reads an index it can trust and performs no clamping
of its own. Rationale, which the implementation should preserve rather than
rediscover:

- The buttons' `disabled` state must come from the same computation as the
  clamp. Clamping on read would let `zoomStep` hold an out-of-range value that
  silently renders as the clamped one while the button still reads enabled — a
  control that lies about what it does.
- `mapTargetViewBox()` runs on every animation frame and every location change.
  A clamp there is per-frame work for a value that changes only on a click.
- The mode toggle changes the valid range, so it needs the clamp too: Close@1
  switching to Wide leaves an index Wide cannot use.

**On a mode switch, clamp to the nearest valid step — do not reset to the mode's
base.** Where the ranges overlap this preserves the visual span across the
toggle: Close@3 → Wide@3 is the same 390-unit box, with only the content
changing.

### 3. What a zoom step does at runtime

A zoom step **does not rebuild content**. It leaves `mapRenderedZoom` alone:

```
click + → clamp zoomStep
        → refresh disabled on #mapZoomIn and #mapZoomOut
        → mapUpdateViewBox(mapLastNode, false)
```

`w`/`h` interpolate in the existing animation and `mapPositionStreetLabels()`
already runs per frame, so the labels re-place themselves as the span changes.
No new render path, and `renderMapClose()` / `renderMapWide()` are not called.

A **mode** switch still rebuilds, exactly as today.

Both buttons' `disabled` state is refreshed after either handler runs, from
`rangeFor(mapZoomMode)`. Remove the static `disabled` attributes from the markup;
at Close base 2 both buttons start enabled.

### 4. Derivations to name

This pass owns the `MAP_*` block's hidden derivations. #33 excluded that block
as "already-named siblings," which was wrong — those constants are *named but
not derived*, which is the same duplication in a different costume. #33 will be
amended; do not wait for it.

| Currently written as | Should be |
|---|---|
| `MAP_CLOSE_VIEW = 260` | `2 × MAP_SPACING` |
| `MAP_WIDE_VIEW = 800` | `6 × MAP_SPACING` |
| `MAP_LABEL_TIERS` 600 / 300 / 110 | `6 / 3 / 1 ×` widest label width |
| `MAP_LABEL_INSET = 55` | half the widest label width, plus padding |

Introduce a named constant for the widest street name's rendered width —
**99.1 user units**, `"POPLAR ST"` at 15px — since the tiers, the inset and the
collision threshold below all derive from it. Record in a comment that it is a
measured value tied to the font, not a free parameter.

### 5. #28 — nudge labels off intersections

For each candidate position `mapLabelPositions()` returns: if it falls within
the clearance distance of an **intersection** node in that street's chain, slide
it to the nearest mid-block point on that street.

**Clearance, derived from label geometry rather than picked:**

```
clearance = (widestLabelWidth + labelHeight) / 2 = (99.1 + 15) / 2 ≈ 57.05
```

Two labels whose centres are closer than this along the crossing axis can
overlap; beyond it they cannot.

**Why mid-blocks are safe.** A mid-block sits `MAP_SPACING / 2` = **65** units
from either adjacent intersection, and 65 > 57.05, so a nudged label clears both
crossings with about **8 units** to spare. Vertical streets run on integer
columns and never pass through a horizontal street's mid-block, so the nudged
position has no crossing label to collide with.

⚠️ **This margin is load-bearing on `"POPLAR ST"` remaining the widest street
name.** The fix holds while `(W + 15) / 2 < 65`, i.e. while `W < 115` units —
roughly 10–11 characters at the current font. Record this as a constraint in a
comment beside the constant: a longer street name added later silently
reintroduces the collisions.

Only Wide is affected, since `mapBindStreetLabels()` early-returns for Close.
Under the ladder that means spans 390 / 520 / 650 / 780.

### 6. Player-marker avoidance

The player marker sits at the box centre at `MAP_PLAYER_R_WIDE` (12) and
**nothing in the current placement code knows it exists.** #28 did not audit for
it. Since the player always stands on a node, and nudged labels sit on
mid-blocks, a label can land on a player standing at a mid-block.

**Rule: after nudging, suppress any label whose box intersects the player marker
inflated by the clearance above.** Suppress rather than nudge again — a second
nudge can cascade, and a street that loses one of its two or three names still
reads. Where it was the street's only label, losing it is acceptable: the player
is standing on that street and the `#locBar` already names their location.

### 7. `MAP_LABEL_TIERS` needs no retune

The thresholds stay as they are. They are keyed on visible user units, and with
box-only zoom a label's user-unit width is constant, so "how many names fit"
stays meaningful at every span on the ladder.

The tiers are a **crowding** rule, not a **legibility** rule — legibility is
handled by the ladder's clamps. Expect the 1-label tier, unreachable at span 800
and reported as such in #27, to become reachable: a visible stretch always runs
between `S/2` and `S`, so at 390 both the 1- and 2-label tiers fire.

## Design decisions to make during implementation

Record whichever is picked in the changelog's Notes/assumptions section.

1. **Nudge direction.** A candidate near an intersection has a mid-block on
   either side. *Recommended default:* slide toward the centre of the street's
   visible stretch — sliding outward risks crossing the inset or leaving the
   visible span.
2. **Two candidates nudging to the same mid-block.** Possible on a 2- or
   3-label street near a tier boundary. *Recommended default:* keep the one
   nearer the centre of the visible stretch and suppress the other, matching
   the player-marker rule rather than inventing a second behaviour.
3. **Shape of the clearance constant.** Whether to store the derived ≈57 or
   compute it from the width and font-size constants at use. *Recommended
   default:* compute it, so retuning the font or the widest name carries
   through — this is the pass's own "name the derivation" rule applied to
   itself.
4. **How `disabled` is refreshed.** A shared helper called from both handlers,
   or inline in each. *Recommended default:* a helper — two call sites that must
   agree is exactly the duplication this pass is naming constants to avoid.

None of these changes scope, player-facing behaviour, or the versioning tier.

## Data / schema changes

**None.**

- No new or changed **state fields**. `zoomStep` joins `mapZoomMode` as a
  module-level `let`, deliberately outside `state`.
- No **item schema**, tag or category changes.
- No **room / container / exit** schema changes.
- No `ITEM_REGISTRY` involvement.

`SAVE_KEY` stays `ashfall_save_v0.4` and existing browser saves keep loading.
This is what holds the pass at PATCH.

## In scope

- A working zoom ladder on `span = zoomStep × MAP_SPACING`, per-mode ranges,
  clamped at both state-change sites.
- `MAP_WIDE_VIEW` 800 → 780.
- Clamp-to-nearest on mode switch.
- Live `disabled` state on `#mapZoomIn` / `#mapZoomOut`, static attributes
  removed from the markup.
- Naming the four `MAP_*` derivations, plus the widest-label-width constant.
- #28's nudge-off-intersections rule, with clearance derived from label
  geometry.
- Player-marker avoidance in Wide label placement.

## Explicitly out of scope

- **#16's close-map building-label clipping.** Same class of problem — text
  placed without regard to the viewBox — but in `renderMapClose()`, which this
  pass does not touch. Still open; do not fold it in.
- **#16's mobile breakpoint.** Unrelated stylesheet work on `main`.
- **Neighbourhood / district labels, and any content that varies by span.**
  Considered during planning and deliberately declined: it needs a spatial
  grouping layer that does not exist anywhere in the file, and that layer is a
  world-structure decision shared with #15, #8 and #7. See #27's decision
  comment.
- **Zoom or mode persistence**, and any `localStorage` preferences store.
- **Viewport culling in `renderMapClose()`**, which emits all 176 node dots and
  every building on each rebuild. Real, but a separate concern and only
  pressing once #8 places buildings.
- **Clamping `mapTargetViewBox()` to the town's bounds.** v0.4.5 left the box
  unclamped on purpose; leave it.
- **Any change to `LOCATIONS`, `MAP_STREETS` or `MAP_BUILDINGS` data.**
- **#33's comment and literal pass**, apart from the `MAP_*` derivations named
  above, which this pass owns by agreement.

## Sections touched

**UI / RENDERING only**, and within it the **MAP** sub-block — `mapTargetViewBox()`,
`mapUpdateViewBox()`, `renderMap()`, `mapLabelPositions()`,
`mapPositionStreetLabels()`, the `MAP_*` constants, and the `#mapZoomToggle`
handler.

Also the two `<button>` elements in the document body, to drop their static
`disabled` attributes.

**No WORLD DATA, no PLAYER STATE, no ACTIONS, no SURVIVAL/TIME SIMULATION, no
PERSISTENCE.** No stylesheet change.

## UI changes

- The `+` and `−` buttons become live, each disabling itself at its end of the
  mode's range.
- Close gains one step in and one step out of its current view; Wide gains three
  steps in.
- Wide's default view is very slightly tighter (780 rather than 800).
- Wide street names no longer collide at intersections, and no longer sit under
  the player marker.

## Dependencies / issue linkage

Fulfils **#27** and **#28**. The pull request closes both.

Nothing is expected to be deferred. If the zero-collision bar below is not met
at every span, file an issue recording which positions survive and why, rather
than relaxing the bar silently.

Unblocked by this pass: nothing. Still open and deliberately untouched: #16
(both findings), #33 (minus the `MAP_*` derivations).

## Validation

v0.4.5's standard was a headless sweep of all 176 street/mid-block nodes at one
span. This pass has more spans, so:

- **Wide: 176 nodes × 4 spans (390/520/650/780) = 704 positions.** At each,
  assert **zero** overlapping label pairs; no label outside its street's visible
  span; none clipped at a span edge; counts match `MAP_LABEL_TIERS`; no label
  intersecting the player marker.
- **Close: 176 nodes × 3 spans (130/260/390) = 528 positions.** Assert the
  viewBox is the expected player-centred box and that no street names render.
- **Controls:** at each end of each mode's range the corresponding button is
  disabled; a mode switch clamps to the nearest valid step rather than resetting;
  a zoom step does not rebuild SVG content.

Zero overlaps is the stated bar. If a residue survives, report it honestly with
the positions rather than adjusting the threshold to make the number pass.

## Open questions for Tom

**None.** All four of #27's open points and #28's choice of fix were resolved
during planning — see the decision comment on #27. This handoff is ready to
build from.

## After implementation

Open one pull request carrying:

- `ashfall.html` with `GAME_CONFIG.VERSION` bumped to **0.4.8** (PATCH; verify
  nothing shipped in between).
- A new `CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff
  by path, recording which "Design decisions" defaults were taken, and calling
  out the `MAP_WIDE_VIEW` 800 → 780 change explicitly.
- `Closes #27` and `Closes #28` in the description.
- New issues for anything deferred; if nothing was, say so in the changelog's
  Documentation section.
