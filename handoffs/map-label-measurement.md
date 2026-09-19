# Ashfall Handoff — Map labels measured, not tabulated

Current shipped version: v0.4.17
Implied version-change type: PATCH
Issues: #43 — MAP_LABEL_W is a hand-measured font width that nothing can catch
drifting; #87 — renderMapClose() splits a building name on its first space

## What this is

Two hand-kept facts about rendered text, both replaced by a measurement taken
at bind time against the real font.

- **#43** — `MAP_LABEL_W = 99.1` is the rendered width of `"POPLAR ST"`, copied
  into the source by hand. Six sites derive from it. Its own body says why that
  is fragile: *"`system-ui` is not one font. `99.1` was measured on whatever the
  measuring machine resolved `system-ui` to."*
- **#87** — `renderMapClose()` breaks a building's name into label lines on the
  **first space only**, so a three-word name renders `["Main", "St Pharmacy"]`
  rather than the `["Main St", "Pharmacy"]` a reader expects.

They are one pass because they are one move, and the precedent is already in the
file: v0.4.10 chose `getComputedTextLength()` over a width table for the Close
building labels, *"a table would need re-measuring on every rename and would not
survive #8 adding buildings."* This applies that to the two places that still
tabulate.

**The literal has already drifted.** Measured in Chromium during planning at the
real `.map-street-name` face (`system-ui`, 15px, weight 600), `"POPLAR ST"` is
**98.163** user units, not 99.1. That is a 0.94-unit error sitting in the source
today.

## Relevant existing state

Read from `ashfall.html` @ v0.4.17. Line numbers are from that file.

### #43 — the constant and its six consumers

```js
const MAP_LABEL_W = 99.1;        // :5114
const MAP_LABEL_CAP = 12;        // :5115
```

Every live use, comments excluded:

| # | Site | Line | Use |
|---|---|---|---|
| 1 | `MAP_LABEL_INSET` | 5119 | `MAP_LABEL_W / 2 + MAP_LABEL_EDGE_GAP` |
| 2 | `MAP_LABEL_TIERS` | 5128–5130 | `6 *`, `3 *`, `1 * MAP_LABEL_W` |
| 3 | `MAP_LABEL_CLEARANCE` | 5143 | `MAP_LABEL_W / 2 + MAP_LABEL_OFFSET + MAP_LABEL_CAP` |
| 4 | `mapClearCrossings()` `room` | 5167 | `MAP_LABEL_W / 2` |
| 5 | `mapClearCrossings()` `kept` filter | 5179 | raw `Math.abs(p - q) >= MAP_LABEL_W` |
| 6 | `mapLabelBox()` | 5210–5211 | `w` on a horizontal street, `h` on a vertical one |

**Sites 1, 2 and 3 are module-level `const`s evaluated at script-parse time,
before any DOM node exists to measure.** That is the structural constraint this
pass has to solve; it is not a naming question.

`mapBindStreetLabels()` (`:5187`) is the natural measuring point — it already
walks every street's pooled `<text>` nodes and sets `el.textContent =
street.name` (`:5199`). It returns early when `mapZoomMode !== "wide"` (`:5189`),
and the game opens in Close mode (`mapZoomMode = "close"`, `:5077`), so **the
measurement does not run until the player first switches to Wide.**

`mapLabelPositions()` and `mapClearCrossings()` are reached from
`mapPositionStreetLabels()`, which runs on **every animation frame** of a pan
(`:5451`). Whatever holds the derived values must be readable there without a
layout read.

### The hidden-node hazard, confirmed

Wide's pool ships hidden (`renderMapWide()`, `:5390`):

```js
html += `<text class="map-street-name" data-street="${i}" y="${-MAP_LABEL_OFFSET}" text-anchor="middle" style="display:none"></text>`;
```

Close's pool deliberately does not, and the comment at `:5360` says why:

> Unlike Wide's pool these do not ship hidden: a hidden node has no layout, so
> `getComputedTextLength()` would measure every name as zero wide and the clamp
> would silently do nothing.

Probed directly during planning: `getComputedTextLength()` returns **0** on a
`display:none` SVG text node and **98.163** on the same node once shown. The
hazard is real and this pass must handle it.

### #87 — the split and the centring

`renderMapClose()` (`:5370–5374`):

```js
const words = BUILDINGS[id].name.split(" ");
const lines = words.length > 1 ? [words[0], words.slice(1).join(" ")] : [BUILDINGS[id].name];
lines.forEach(line=>{
  html += `<text class="map-bldg-label" data-bldg="${id}" text-anchor="middle">${line}</text>`;
});
```

`mapBindBuildingLabels()` (`:5289–5293`) then lays the lines out and centres the
block off the **widest** line:

```js
const lines = els.map((el, i)=> ({ el, dy: first + i * MAP_BLDG_LINE_H }));
const half = Math.max.apply(null, els.map(el => el.getComputedTextLength() / 2));
```

Both `lines` and `first` already generalise over `els.length`, so line count is
not hard-coded. `half` drives the edge clamp in `mapPositionBuildingLabels()`
(`:5328–5330`), which is why a needlessly wide second line drags the whole block
away from its own dot near a view edge.

All eleven `BUILDINGS` names are one or two words: Acorn Apartments, Alley,
Corner Store, Pharmacy, Hardware Store, Storage Facility, Riverbank, Oak
Apartments, Auto Workshop, Police Station, Riverside Freight.

## Rules / mechanics

### Part A — #43, a single measured width

**A1. Measure at bind, take the maximum.** In `mapBindStreetLabels()`, after the
existing `els.forEach(el => el.textContent = street.name)`, measure each street's
name once and keep the largest across all sixteen. One measurement per street,
not per pooled node — the three nodes of a street carry the same string.

**A2. Handle the hidden pool.** A pooled node is `display:none` at bind time and
measures zero. Make the node measurable before reading it: set `style.display =
""` on the node being measured, take the reading, and leave the rest to
`mapPositionStreetLabels()`, which sets `display` on every pooled node on the
snap that immediately follows (`mapUpdateViewBox(node, true)` in `renderMap()`,
`:5472`). Do **not** simply ship the pool visible: that would paint sixteen
streets' worth of names at the origin before the first position pass, which is
the flash Close's build-order comment (`:5362–5364`) exists to avoid.

**A3. The derived values become bind-time values.** Sites 1, 2 and 3 cannot stay
`const`s initialised at parse time. Recompute them whenever the measured width
changes, and seed them from the fallback (A5) so they are valid before the first
Wide bind ever runs. Sites 4, 5 and 6 read the width directly and need only to
read the new binding.

**A4. Keep every multiplier exactly as it is.** `6 /`, `3 /`, `1` for the tiers,
`/ 2` for the inset and the clearance, `MAP_LABEL_EDGE_GAP`, `MAP_LABEL_OFFSET`.
Only the width they multiply changes. This pass does not retune the map; it
replaces one number's *source*.

**A5. A fallback is required, not optional.** If the measurement returns `0` or
anything non-finite — a detached node, a pool that never got layout, a browser
that throws — the tiers degrade to `hi - lo >= 0`, which is always true, and
every street silently jumps to three names. Guard it: a measured maximum that is
not `> 0` leaves the previous value in place, and the value the game starts with
is the current literal, kept as a named fallback constant with a comment saying
it is the last known good Chromium measurement and is only ever used when
measurement fails.

**A6. `MAP_LABEL_CAP` stays a literal.** Measured during planning:
`getBBox().height` on `"POPLAR ST"` at this face is **17.83**, which is the em
box, not the cap height — `getBBox()` reports the layout box and
`getComputedTextLength()` gives width only. There is no cheap correct
measurement for a cap height here, so `12` stays, and its comment should say
that it is deliberately not measured and why. This is a finding, not a deferral.

**A7. Record the cross-machine consequence.** This is the one thing the pass
must say out loud, because #43's own scope note gets it wrong. Its scope note
reads *"no player-visible change if the measured value matches the literal"* —
but the measured value does **not** match, and even where it does the claim
would not generalise. Measuring trades:

- *before* — identical on every machine, correct only on the one where 99.1 was
  measured;
- *after* — correct on every machine, identical on none.

The neutrality band is narrow. Derived during planning by sweeping the real
placement arithmetic: any single width in **[97.55, 101.15]** produces byte-identical
placement everywhere, and outside it placement changes. That is roughly ±2%,
and `system-ui` resolves to Segoe UI, SF Pro, Roboto and Cantarell on different
machines, which differ by more than that. So on some machines this pass *will*
change label placement — correctly, but visibly. The changelog entry must state
this rather than claim a blanket "no visible change".

### Part B — #87, a width-balanced line split

**B1. Line count stays decided at markup time.** `renderMapClose()` emits two
`<text>` nodes when the name contains at least one space and one when it does
not. No measurement is needed for that count, so the markup stays deterministic.

**B2. The markup ships the whole name in the first node,** with the second node
empty. That is what makes the name measurable as a single string at bind time.
Close's pool already ships visible, so it has layout.

**B3. `mapBindBuildingLabels()` chooses the split.** For a name with at least one
space, for every space at index `i`:

```
lw = el.getSubStringLength(0, i)
rw = el.getSubStringLength(i + 1, name.length - i - 1)
score = Math.abs(lw - rw)
```

Take the lowest score. On an exact tie, take the **earliest** index, so the
choice is deterministic and does not depend on iteration order. Then assign
`name.slice(0, i)` to the first node and `name.slice(i + 1)` to the second.

**B4. `half` is computed after the split, not before.** It already reads both
nodes; it must now run once the final text is assigned to each.

**B5. Always exactly two lines when there is a space.** A one-word name stays one
line. Three lines are out of scope (see below), and collapsing a two-word name to
one line is not a case: one line is always wider than the wider of two.

**B6. Why measured rather than character-balanced.** Both were tested during
planning against six hypothetical three-word landmark names. They agree on five
and disagree on `"Sunoco Gas Station"`, where character-balancing picks
`["Sunoco Gas", "Station"]` and width-balancing picks `["Sunoco", "Gas Station"]`
with the smaller widest line — and the widest line is what `half` feeds to the
edge clamp. Measured wins on the case where they differ, and the measurement is
already being taken for `half`.

## Design decisions to make during implementation

Narrow calls. Record whichever is taken in the changelog's Notes or Documentation
section rather than choosing silently.

1. **How the measured width reaches its six consumers.**
   - *(a, recommended)* A module-level `let` beside `mapStreetLabels` /
     `mapZoomStep`, plus `let`s for the three derived values, all recomputed by a
     small function called at the end of `mapBindStreetLabels()`. Smallest diff,
     and module-level `let` for map view state is already this file's idiom
     (`mapZoomMode`, `mapZoomStep`, `mapRenderedZoom`, `mapLastNode`,
     `mapCurrentViewBox`).
   - *(b)* Thread the width through `mapLabelPositions()` / `mapClearCrossings()`
     / `mapLabelBox()` as a parameter. More explicit, but those run per frame and
     it widens three signatures for a value that is constant between binds.
   - *(c)* A factory returning the placement functions closed over the width.
     Cleanest in the abstract, largest diff, and #113 may want it later — but
     building it now for a follow-up that may not happen is speculative.

2. **Where the measurement lives inside bind.** Either a first pass over all
   sixteen streets before the existing loop, or folded into the existing loop with
   the max accumulated as it goes. The second is one pass; the first reads more
   plainly. Either is fine.

3. **`getSubStringLength()` vs. setting each candidate and re-reading
   `getComputedTextLength()`.** Recommend `getSubStringLength()`: one layout per
   name rather than one per candidate split, and no text thrash. Both are
   available on `SVGTextContentElement` and neither is a compatibility risk.

4. **Whether the fallback constant keeps the name `MAP_LABEL_W`.** Reusing the
   name keeps the diff small but leaves a reader thinking the literal is still
   live. A distinct name (`MAP_LABEL_W_FALLBACK` or similar) costs a rename at
   six sites and says what it is. Slight preference for the distinct name; either
   is defensible if the comment is honest.

## Data / schema changes

**None.** No PLAYER STATE field, no item schema field, no room/container/exit
schema field, no `ITEM_REGISTRY` entry, no `BUILDINGS` entry. `SAVE_KEY` does not
rotate — `versionCompat()` stays at `0.4` under a PATCH bump, so existing browser
saves keep loading.

## In scope

- `MAP_LABEL_W` replaced by a bind-time measurement, with all six derivation
  sites reading it (#43).
- A guarded fallback for a failed measurement (A5).
- `MAP_LABEL_CAP` left a literal, with its comment updated to say it is
  deliberately not measured (A6).
- The building-name split moved from first-space to width-balanced, computed in
  `mapBindBuildingLabels()` (#87).
- `renderMapClose()` emitting the unsplit name plus an empty second node.
- Comment updates at `:5108–5119`, `:5132–5143` and `:5354–5364` to describe what
  is now measured and what is still assumed.

## Explicitly out of scope

- **#113 — per-street measured widths.** Filed during this planning session and
  deliberately left. It changes 2,159 of 11,264 street-views and is a visible
  densification of the two lower Wide spans; this pass takes the **maximum**
  precisely so it can prove zero change. Do not fold it in.
- **#37 — labels drawn outside the viewBox.** Same functions, different fault
  (it turns on `MAP_LABEL_CAP` and the one-sided band, not on the width). This
  pass leaves its measured table exactly valid, since placement does not change.
- **#108 — the duplicated `viewBox` literal** at `:148`. Map-adjacent and also a
  one-source-of-truth complaint, but it is markup and belongs to that issue's
  pass.
- **Three-line building labels.** `MAP_BLDG_LINE_H` and the `first`/`lines` maths
  generalise, but a third line makes the block taller against
  `MAP_BLDG_LABEL_PAD` at the narrowest Close span and the map is already
  crowded. Two lines stay the maximum.
- **Measuring `MAP_LABEL_CAP`.** See A6 — settled as "stays a literal", not
  deferred.
- **Renaming any street or building,** and any change to `MAP_STREETS`,
  `BUILDINGS` or `MAP_BUILDING_OFFSETS`.
- **#8.** This pass is one of the things that makes #8's landmark buildings safe
  to add; it adds none of them.

## Sections touched

**RENDERING only**, specifically the MAP sub-block named in the ARCHITECTURE
comment. Nothing in WORLD DATA, PLAYER STATE, CORE UTILITIES, INVENTORY / ITEM
SYSTEM, WORLD INTERACTION, SURVIVAL / TIME SIMULATION, CRAFTING, FIRE / COOKING
or PERSISTENCE. No content and no mechanic: this is a new way of deriving a
number the renderer already used.

## UI changes

**None on the measuring machine, and that is provable rather than assertable.**

- Street labels: identical count and identical position in every view, provided
  the measured maximum lands inside [97.55, 101.15] — see Validation.
- Building labels: all eleven current names split identically under the old and
  new rules, so no marker changes.

On a machine whose `system-ui` falls outside that band, street-label counts may
differ — correctly, per A7. That is the intended trade and belongs in the
changelog, not in a "no visible change" claim.

## Validation required

The repo's standard is a diff or a data sweep, never an assertion. Three
obligations, all of which the planning session has already run once and which the
coding session must re-run on its own build:

1. **The street-label sweep (#43).** Drive the real `mapLabelPositions()` /
   `mapClearCrossings()` / `mapLabelBox()` / `mapLabelHitsPlayer()` arithmetic
   over every view a player can occupy — **176 street/mid-block nodes × 4 Wide
   spans × 16 streets = 11,264 street-views** — under the literal and under the
   measured maximum, and compare label count and each label's position. Planning
   measured 98.163 and got **0 count differences and 0 position shifts**. Report
   the same two numbers.

2. **The neutrality band.** Re-derive the interval of single widths that produce
   identical placement, and confirm the machine's own measured maximum lands
   inside it. Planning found **[97.55, 101.15]**. If the build's measurement
   falls outside, the pass is **not** placement-neutral there — say so in the
   changelog with the actual counts, rather than reporting a neutral result from
   a different machine.

3. **The eleven building names (#87).** Render or compute the line split for
   every current `BUILDINGS` name under the old and the new rule and show the same
   two lines for each. Planning confirmed all eleven are identical. Worth also
   recording the new rule's output for two or three three-word names, to show the
   fix does what it claims — `"Main St Pharmacy"` should give
   `["Main St", "Pharmacy"]`, not `["Main", "St Pharmacy"]`.

The planning harnesses were throwaway and are not in the repo; the game file was
never edited to produce any of these numbers.

## Dependencies / issue linkage

- **Closes #43** and **closes #87**. Both are `tier-1` → PATCH, both RENDERING,
  and the pull request should carry both.
- **Unblocks #113** (per-street widths), which is the deliberate remainder of
  #43 and should not be implemented here.
- **Does not block, and is not blocked by, #37** — its counts survive this pass
  intact.
- **#68 is closed** (shipped in v0.4.16 as part of the same #8 landmine group);
  no action.
- Nothing else is expected to be deferred. If the implementation turns up a
  seventh consumer of `MAP_LABEL_W` or a second measurement hazard, file it
  rather than widening the pass.

## Open questions for Tom

None. The two that existed were resolved during planning:

- **How much of #43 to take** — the single measured maximum, with per-street
  widths filed as #113. Settled on the evidence that the maximum is provably
  zero-change and per-street moves 19% of street-views.
- **Whether #87 and #43 ship together** — yes, one pass, one changelog entry.

This handoff is ready to build from.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` bump and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff by the
path it was read at (`handoffs/map-label-measurement.md`), recording which of the
four design decisions above were taken, and stating the cross-machine consequence
from A7 explicitly rather than claiming a blanket "no visible change". Close both
issues with `Closes #43` and `Closes #87`. Move this file to
`handoffs/archive/map-label-measurement.md` with `git mv` in the same pull
request, filename unchanged.
