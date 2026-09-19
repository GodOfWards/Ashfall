# Ashfall Handoff — Wide Map: Panning, Zoom Placeholders, Viewport-Relative Labels

Current shipped version: v0.4.3
Implied version-change type: PATCH
Issues: #19 — Make Wide view pan with the player, and add +/- zoom controls
        #20 — Street labels should be placed against the visible window

## What this is

The Wide map is a fixed box showing the whole town; it ignores the player
entirely. This pass makes it track the player the way Close already does, adds
two **inert** `+` / `−` placeholder buttons for a later zoom pass, and replaces
the one-label-per-block street naming with labels placed against the portion of
each street currently on screen.

#19 and #20 ship together because they are the same change: once the view moves,
build-time label placement stops being meaningful.

Rendering-only, and **no zoom level is persisted** — see Data / schema changes.

## Relevant existing state

Verified against the current `ashfall.html`, with geometry recomputed from the
real constants rather than taken from the v0.4.3 changelog.

- `MAP_WIDE_VIEWBOX = { x:20, y:20, w:1000, h:1000 }` (`ashfall.html:4414`) —
  a fixed box. `MAP_CLOSE_VIEW = 260` (`ashfall.html:4401`) is a *span*, used to
  build a player-centred box.
- `mapTargetViewBox(node)` (`ashfall.html:4550`) returns the constant box for
  Wide, and a player-centred `MAP_CLOSE_VIEW` window for Close.
- `mapUpdateViewBox(node, snap)` (`ashfall.html:4556`) already animates the box
  — 350ms, ease-out cubic, via `requestAnimationFrame`, setting only the
  `viewBox` attribute each frame. Close uses it on every move. **Wide never
  does, because its target never changes.**
- `renderMap()` (`ashfall.html:4584`) is already mode-agnostic: it rebuilds
  `innerHTML` only when the zoom mode changed (snapping the box), and otherwise
  animates the box whenever the player's node changed.
- `mapZoomMode` (`ashfall.html:4458`) is a module-level `let`, **not** a field
  on `state`. `serializeGame()` (`ashfall.html:4165`) persists
  `{version, state, world, doors, windows}`, so the zoom mode is already
  unsaved and every load starts at Close.
- `mapBlockLabels(name, chain)` (`ashfall.html:4484`) emits one `<text>` per
  block: 7 blocks × 16 streets = **112 labels**. It rotates each label onto the
  block heading, folding the angle into `(-90, 90]`, and offsets it off the line
  by `MAP_LABEL_OFFSET = 5` (`ashfall.html:4483`).
- `.map-street-name` is `font-size:15px; letter-spacing:.5px; font-weight:600`
  (`ashfall.html:44`).
- The zoom toggle handler binds `#mapZoomToggle button[data-zoom]`
  (`ashfall.html:4377`) — it selects on the **`data-zoom` attribute**, not on
  being a button in that container.
- `#gaitBar button:disabled` uses `opacity:.4; cursor:not-allowed`
  (`ashfall.html:59`) — the existing disabled-control treatment.

### Geometry, recomputed

`mapToSvg(col,row) = { x: 55 + (col+1)*130, y: 55 + (3-row)*130 }`, over
cols −1..6 and rows −4..3:

- Node extents: **55 → 965** on both axes (910 units).
- River line: x **30 → 990** (it overhangs the grid by 25 each side).
- The v0.4.3 Wide box covers **20 → 1020**.

### Why the span has to shrink

A 1000-unit box over 910 units of content has nothing to pan within — the
content nearly fills it at every player position, so centring on the player
would barely move anything. **Wide must zoom in for panning to mean anything**,
which is what the original "zoom in about 20%" observation was really asking
for: 1000 → **800**.

At span 800, a player-centred box has `x = px − 400` with `px ∈ [55, 965]`, so
the box ranges over `[−345, 565]` — it slides across the full width of the town
as the player crosses it.

### Void at the town edge, quantified

Unclamped, a player at the far west edge (`px = 55`) gets a box covering
−345 → 455, of which 375 units (**47%**) is empty canvas.

This is the same character as shipped behavior: Close at the same position
covers −75 → 185, of which 105 units (**40%**) is empty. Clamping the box to
content bounds was considered and **rejected** — the ask is for Wide to pan
"like Close does", and Close is unclamped. Clamping would also make Wide at any
span ≥ 960 stop panning entirely.

## Rules / mechanics

### 1. Wide becomes a span, not a box

Replace `MAP_WIDE_VIEWBOX` with a span constant mirroring `MAP_CLOSE_VIEW`:

```
const MAP_WIDE_VIEW = 800;   // was a fixed 1000-unit box at (20,20)
```

`mapTargetViewBox()` then collapses to one code path for both modes:

```
function mapTargetViewBox(node){
  const span = mapZoomMode === "wide" ? MAP_WIDE_VIEW : MAP_CLOSE_VIEW;
  const n = LOCATIONS[node];
  const p = mapToSvg(n.x / 100, n.y / 100);
  return { x: p.x - span/2, y: p.y - span/2, w: span, h: span };
}
```

No clamping. No new state. `renderMap()` and `mapUpdateViewBox()` need no
change to make panning work — Wide starts animating on movement purely as a
consequence of its target no longer being constant.

`MAP_WIDE_VIEW = 800` is a **retunable** balance value with no prior
convention: it is the smallest span that both delivers the requested ~20% zoom
and leaves room to pan. A smaller span pans across more of the map but shows
less of the town at once.

### 2. Player marker

Unchanged. Close keeps `r="5"`, Wide keeps `MAP_PLAYER_R_WIDE = 12`. With no
zoom variable there is no span-proportional sizing to do, and both existing
values stay exactly as shipped.

### 3. Inert zoom placeholders

Add two buttons to `#mapZoomToggle`, after the Wide button, in the order
`+` then `−`:

```html
<button id="mapZoomIn" disabled>+</button>
<button id="mapZoomOut" disabled>&minus;</button>
```

**They must not carry a `data-zoom` attribute.** The existing handler at
`ashfall.html:4377` binds `#mapZoomToggle button[data-zoom]` and would
otherwise treat them as mode buttons, breaking the Close/Wide toggle. Omitting
the attribute is sufficient — do not widen that selector.

Style them with the existing disabled treatment, matching `#gaitBar`:

```css
#mapZoomToggle button:disabled{ opacity:.4; cursor:not-allowed; }
```

They are placeholders: no handler, no behavior, no zoom variable. Reserving the
layout slot is the whole deliverable.

### 4. Viewport-relative street labels

Delete `mapBlockLabels()`. Replace it with a fixed pool of label elements
positioned against the current viewBox.

**Pool.** `renderMapWide()` creates **three `<text class="map-street-name">`
nodes per street** — 16 streets × 3 = 48 nodes — once, at render time. They are
never created or destroyed during a pan; only their `transform`, text content
and `display` change.

**Per street, each time the viewBox moves**, with box `{x,y,w,h}`:

Every street run is axis-aligned (the chain's first and last node share either
a y or an x), so visibility is a 1-D clamp. Let `A` and `B` be
`mapToSvg()` of `chain[0]` and `chain[chain.length-1]`:

```
horizontal = (A.y === B.y)

if horizontal:
   if A.y < box.y or A.y > box.y + box.h  → hide all three, done
   lo = max(min(A.x,B.x), box.x);  hi = min(max(A.x,B.x), box.x + box.w)
else:
   if A.x < box.x or A.x > box.x + box.w  → hide all three, done
   lo = max(min(A.y,B.y), box.y);  hi = min(max(A.y,B.y), box.y + box.h)

L = hi - lo                      // visible length of this street
```

**Label count and positions** along the visible span, by `L`:

| Visible length `L` | Labels | Positions |
|---|---|---|
| `L < 110` | 0 | — |
| `110 ≤ L < 300` | 1 | midpoint `(lo+hi)/2` |
| `300 ≤ L < 600` | 2 | `lo + INSET`, `hi − INSET` |
| `L ≥ 600` | 3 | `lo + INSET`, `(lo+hi)/2`, `hi − INSET` |

with `MAP_LABEL_INSET = 55`. The inset is half the widest street name:
`POPLAR ST` measured **99.1 units** at 15px in the v0.4.3 in-browser
validation, so 55 keeps a full-width label inside the visible span rather than
clipped at its edge. The `110` threshold is that same width plus a little slack.

All four numbers — 55, 110, 300, 600 — are **retunable** and have no prior
convention behind them.

**Rotation and offset.** Reuse v0.4.3's logic unchanged: rotate the label onto
the street's heading with the angle folded into `(-90, 90]`, and offset it off
the line by `MAP_LABEL_OFFSET = 5`. Orientation must be identical to the
current build — this pass changes *where* labels sit, never which way they
read.

**Hiding.** Set `display:none` on unused pool nodes and clear it on used ones.

**When to reposition.** Labels must be repositioned wherever the viewBox is
set: both in `mapUpdateViewBox()`'s snap branch and inside its `requestAnimation
Frame` `step()`, which currently sets only the `viewBox` attribute.

### 5. Close view

Entirely untouched. `renderMapClose()` emits zero `text.map-street-name` nodes
today and still will; its span stays 260, its marker stays `r="5"`, and its
building dots, node dots and labels are unchanged.

## Design decisions to make during implementation

1. **Per-frame vs. on-settle label repositioning.** *Recommended:* per frame,
   inside `step()`. The pool is at most 48 nodes and only `transform`/`display`
   change, so no element is created or destroyed during the animation —
   rebuilding `innerHTML` per frame would not be acceptable and must not be
   done. If per-frame proves janky on a phone, fall back to repositioning only
   on settle (labels then visibly jump into place after each pan). Record which
   was shipped.
2. **Where the pool lives.** *Recommended:* a module-level array of element
   references populated by `renderMapWide()`, mirroring how
   `mapPositionPlayer()` resolves `#mapPlayer` — rather than re-querying the DOM
   each frame.
3. **`+` / `−` button order and glyphs.** *Recommended:* `+` first, then `−`,
   using `&minus;` rather than a hyphen so the two read as a matched pair.
4. **Whether the label-count thresholds live as four named constants or one
   small table.** Either is fine; they must not be inline magic numbers.

## Data / schema changes

**None.** No PLAYER STATE fields, no item schema, no room/container/exit schema
changes. The zoom mode stays a module-level variable and is deliberately **not**
added to `state` — that keeps `versionCompat()` at `"0.4"`, so `SAVE_KEY` is
unchanged and every v0.4.x browser save keeps loading. Persisting the zoom level
would make this MINOR (see `docs/Ashfall_Handoff_Guide.md` Part 1); it is out of
scope.

Constants changed: `MAP_WIDE_VIEWBOX` is replaced by `MAP_WIDE_VIEW = 800`.
Constants added: `MAP_LABEL_INSET` and the label-count thresholds.
Function removed: `mapBlockLabels()`.

## In scope

- Wide view centres on the player and animates on movement, at span 800,
  unclamped.
- Two inert, disabled `+` / `−` buttons in the map heading, right of Wide.
- Street labels placed against the visible span of each street, 0–3 per street,
  repositioned as the view moves.
- `mapBlockLabels()` removed.

## Explicitly out of scope

- **Any working zoom.** No zoom variable, no ladder, no span stepping. The
  buttons are placeholders and ship disabled.
- **Persisting the zoom mode.** Would rotate `SAVE_KEY` and make this MINOR.
- **Clamping the viewBox to town bounds** — considered and rejected above;
  applies to Close too, and is not being changed there either.
- **Any change to Close view**, `LOCATIONS`, `MAP_STREETS`, `MAP_BUILDINGS`,
  `MAP_SPACING`, `MAP_MARGIN`, `mapToSvg()` or `mapPathD()`. No node moves.
- **Close-map building-label clipping** (#16 finding 1) and **phone-viewport
  horizontal overflow** (#16 finding 3). Both live in nearby code; neither is
  this pass's, and #16 stays open.
- Building placement in the outer ring (#8).

## Sections touched

UI/RENDERING only — the **MAP** sub-block (`mapTargetViewBox`,
`mapUpdateViewBox`, `renderMapWide`, and the removed `mapBlockLabels`), the
`#mapZoomToggle` markup, and the document `<style>` block for the disabled
button rule. No WORLD DATA, PLAYER STATE, ACTIONS or SIMULATION code changes.

## UI changes

- The Wide map now shows about 80% of the town at a time, centred on the
  player, sliding as they move — instead of the whole town, fixed.
- Street names appear at up to three points along the visible stretch of each
  street rather than once per block, dropping the on-screen label count from
  112 to at most 48 and, in practice, well below that.
- Two greyed-out `+` / `−` buttons appear to the right of Wide. They do
  nothing when clicked.
- Near the town's edges, Wide shows empty canvas on the far side of the player,
  as Close already does.

## Dependencies / issue linkage

Fulfils #19 and #20 together. A working zoom is the obvious follow-up to the
placeholders — file it as a new issue at wrap-time, referencing this handoff,
noting that a zoom variable scoped per mode (Close and Wide each scaling from
their own base span) avoids needing a content-crossover rule between the two
renderers. Does not touch and is not blocked by #16, #8, #18, #21 or #22.

## Open questions for Tom

None. Span 800, no clamping, inert placeholders and the label-placement rule are
all settled; the four label constants are flagged retunable above.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` PATCH bump and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, referencing this handoff by
path (`handoffs/wide-map-panning.md`), recording the four "Design decisions"
resolutions and the retunable constants in its Notes/assumptions section, and
closing both issues with `Closes #19` and `Closes #20`.

Validation worth citing in the entry, driven in a real browser as the v0.4.3
pass was: the Wide viewBox tracks the player across a walk from one edge of the
grid to the other; label counts per street at several player positions, with no
label crossing its visible span's bounds; no label overlapping another at a
grid corner; Close view re-checked as byte-identical in behavior (player
`r="5"`, 11 building dots, zero `text.map-street-name` nodes); the `+`/`−`
buttons present, disabled, and not interfering with the Close/Wide toggle; and
no console errors on load, on toggle, or while moving.
