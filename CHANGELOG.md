# Ashfall — Changelog

Reverse-chronological. Each entry covers one version bump. Older entries are
kept for context but should not need to be re-read for a change scoped to a
single system — see the ARCHITECTURE comment in the script for which section
owns which behavior. The file begins at v0.1.3; 0.1.0–0.1.2 predate it and are
project genesis, not missing entries. The one genuine gap, v0.2.3, is marked in
place.

---

## v0.4.11 — Reproduced defect sweep: Sleep, fire spend, load atomicity, log freshness

Implements: handoffs/reproduced-defect-sweep.md

Implements #61, #62, #63, #64 and #65 in full, per
`handoffs/reproduced-defect-sweep.md`. Five independent defects, each with a
deterministic reproduction, bundled into one correctness pass because each is
small and none needs new state. No new mechanic, no content, no save field.
`SAVE_KEY` does not rotate — existing browser saves keep loading.

**Fixed**
- **Sleep could lower Energy (#61).** `doSleep()` ended with
  `state.vitals.energy = clamp(ceiling)`, an unconditional assignment to the
  Fatigue-derived ceiling. At `E=70 Fa=40` the ceiling is 60, so a
  zero-duration Sleep dropped Energy by 10 and still cleared Fatigue; at
  `E=16.1 Fa=100` the ceiling is 0 and Sleep emptied Energy outright. The
  assignment is now `Math.max(state.vitals.energy, sleepEnergyCeiling())` — it
  still snaps the loop's approximate landing exact, but can only raise.
- **The first campfire cost no firewood, or three too many (#62).**
  `canBuildFire()` gated a first build on a `campfire_kit` alone, while
  `doBuildFire()` then called `consumeFromPools("firewood", FIRE_BUILD_WOOD)`
  unconditionally. `consumeFromPools()` takes what it can and reports nothing,
  so with no firewood the fire lit free, and with firewood in a pocket it
  silently ate three pieces the gate never asked for. `doBuildFire()`'s spend is
  now a three-way branch: a first build consumes the kit only and banks
  `CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD`; a rebuild in an existing
  campfire consumes `FIRE_BUILD_WOOD`; a banked relight consumes nothing.
- **"Add fuel" at the burn cap wasted a firewood (#64).** The render gate
  offered the button at any `fireMinutesLeft < FIRE_MAX_MIN`, so at 350 minutes
  one piece of wood bought 10 minutes and `doAddFuel()`'s `Math.min` discarded
  the other 50. The gate is now
  `room.fireMinutesLeft <= FIRE_MAX_MIN - FIRE_MINUTES_PER_WOOD`, so the button
  is offered only while a piece buys its full value. `doAddFuel()` itself is
  unchanged; its `Math.min` is simply no longer the binding constraint from the
  UI path.
- **A collapsed log summary changed brightness with its last line's class
  (#65).** `log()` decided `fresh` from the caller's `cls` argument, but a
  `LOG_SUMMARIES` line renders unclassed regardless of what the call passed.
  A fishing run ending on a bite (`"good"`) therefore rendered dim while the
  same run ending on a miss (`null`) rendered bright. A `summarised` local now
  records that the summary branch ran, and `if(summarised || !cls)` marks the
  line fresh — freshness follows what was rendered, not what was asked for.

**Hardened**
- **A rejected load no longer leaves a broken world on screen (#63).**
  `applyLoadedData()` assigned `world` before running `resyncUidCounter()`, the
  three backfills and `render()`, any of which throws on a malformed save. Both
  callers caught the throw and reported "nothing was loaded" — untrue, since the
  bad world was already committed and the session was unplayable with `doRestart()`
  the only way out, and nothing surfaced it. The load is now atomic: `nextState`,
  `nextWorld`, `nextDoors` and `nextWindows` are built as locals, a new
  `validateLoadedWorld()` checks them, and the four module bindings are assigned
  only on success. The backfills run after validation, not before — they repair
  old-but-well-formed saves and are not what makes a malformed one safe.
- **New `validateLoadedWorld(nextWorld, nextState)` in PERSISTENCE**, returning
  an array of problem strings the way `validateItemRegistry()` and
  `validateLocations()` do. It covers exactly the five shapes that throw today —
  a room's `floor`, `exits` or `containers` not being an array,
  `state.inventory.items` not being an array, and any populated `CONTAINER_SLOTS`
  bag whose `items` is not an array — and no more. This is a shape check, not a
  schema validator. `carContainers` is optional on a room and is checked only
  when present. It sits in PERSISTENCE beside the backfills rather than in the
  dev-helper block, because unlike its two siblings it is wired into a real code
  path and runs on every load.

**Changed / Reworked**

*Sleep availability*
- **A Sleep that would restore no Energy is no longer offered.**
  `sleepAvailable()` was purely a cooldown test and is now the conjunction of
  two named halves: `sleepOffCooldown()` (the old `SLEEP_COOLDOWN_MIN` test,
  unchanged) and `sleepRestoresEnergy()` (`state.vitals.energy <
  sleepEnergyCeiling()`). `doSleep()`'s existing `if(!sleepAvailable()) return;`
  guard now blocks the zero-duration case at the action level, not only in the UI.
- **At Fatigue 100 the ceiling is 0, so Sleep is never offered.** `energy < 0`
  is never true. The Sneak lock must be worked off through `recoveryStep()`
  instead. This is the intended price of the decision, not a side effect — see
  **Open questions / decisions resolved**.

**New**
- `sleepEnergyCeiling()` in the STAMINA / FATIGUE sub-block, returning
  `clamp(100 - state.vitals.fatigue)`. The ceiling was derived independently in
  `doSleep()` and `estimateSleepMinutes()`; this pass added a third consumer, so
  it is now defined once and read by all three.

**Removed**
- `doSleep()`'s `fatigueAtSleep` local. Extracting `sleepEnergyCeiling()` left
  it with no reader — its only use was the ceiling derivation it no longer
  performs. The snapshot semantics it carried are unchanged and now belong to
  `const ceiling`, which is still read once before the loop; the comment above
  it says so explicitly. See **Notes / assumptions**.

**UI**
- **The Sleep note names which of the two reasons applies.** The existing
  string `"You're not tired enough to sleep yet."` moves to the case it was
  always describing — no Energy deficit — and the cooldown gets
  `"You've slept too recently to manage it again."` Both are functional UI text,
  held to clarity rather than the game's prose tone.
- **The spurious `"Sleep (0:01)"` label is gone**, as a consequence of the gate
  rather than a change to `fmtDuration()`. The button renders only when the
  Sleep will really run, so `estimateSleepMinutes()` is never 0 at that point.
- **"Add fuel to the fire" now disappears from 300 minutes rather than 360.**
  No new text; `renderLocationPanel()` already prints the fire's remaining fuel,
  so the button's absence is explicable on screen.
- **A collapsed `fish` / `rest` / `chop` / `fuel` summary is now consistently
  the bright (`fresh`) line.** No wording changed.
- **A rejected save shows the same message as before.** The difference is that
  the session is still playable afterwards.

**Open questions / decisions resolved**
The handoff carried two balance calls, both answered by Tom during planning and
specced as settled. Neither was re-opened during implementation.
- **A — a Sleep that would restore no Energy is refused.** Sleep exists to
  recover Energy; when there is none to recover it is not offered, and the free
  Fatigue wipe goes with it. **The first-proposed predicate was wrong and is not
  what shipped.** It was `energy < ceiling || fatigue > 0`, and the `|| fatigue > 0`
  clause is true in exactly the cases the defect lives in — it would have
  permitted all six tested states, including `E=70 Fa=40` and `E=16.1 Fa=100`,
  closing nothing. The shipped test is `energy < ceiling` alone, which is true
  only when the Sleep would actually run.
- **A's consequence, verified not a trap.** From the state a chop-and-fish grind
  actually reaches (`E=16.1 St=0.0 Fa=100.0 Hu=51 Th=3`), standing still and
  doing nothing, Fatigue reaches 0 without plateauing — driving `recoveryStep()`
  directly it clears at 436 game minutes, and through the real awake path
  (`advanceTime()`, where collapses fire and each grants Energy) at 733 with
  three collapses. Recovery never stalls; there is no softlock. The cost of
  reaching Fatigue 100 is roughly one wasted day, which is the point.
- **B — a campfire kit contains its own first load of wood.** A first fire costs
  the kit and nothing else: 3 firewood total, not 6. `canBuildFire()` was already
  right, so `doBuildFire()` is what changed. This also makes the economy
  internally consistent — a kit is `CAMPFIRE_KIT_COST` firewood and yields
  `CAMPFIRE_KIT_COST * FIRE_MINUTES_PER_WOOD` = 180 minutes, and a rebuild is
  `FIRE_BUILD_WOOD` firewood for `FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD` = 180.
  Same wood, same burn. What the kit buys over loose wood is the 15 crafting
  minutes and the permanent `campfireBuilt` structure in that room.

**Notes / assumptions**
The handoff left four narrow calls to implementation. All four took its
recommendation, and a fifth arose from the work itself.
- **`validateLoadedWorld()` returns strings, not booleans**, matching the two
  existing validators, and `applyLoadedData()` `console.warn`s them on rejection
  the way `validateLocations()` does. A failed import leaves something
  diagnosable in the console while the player-facing message stays generic.
- **The two `catch` messages are unchanged.** Now that the load is atomic,
  `"Couldn't read a save from this browser."` and `"That file couldn't be read
  as a save."` are no longer untrue, and the validator's `console.warn` carries
  the detail. No third message was added for a shape failure.
- **The `summarised` flag is a local in `log()`**, not a second
  `LOG_SUMMARIES[key]` test at the bottom of the function. The second test would
  be a second source of truth for one condition.
- **The cooldown note reads `"You've slept too recently to manage it again."`** —
  the handoff's proposed string, taken as-is. Retunable: anything equally plain
  would do.
- **`doSleep()`'s `fatigueAtSleep` local was removed rather than kept.** The
  handoff asked for it to be kept, on the grounds that its snapshot semantics
  are load-bearing. Extracting `sleepEnergyCeiling()` left it with no reader at
  all, and the semantics the handoff was protecting are carried by `const
  ceiling` — read once, before the loop, with the loop measuring against it. An
  unused local would have been dead code standing in for a comment, so the
  comment now states the snapshot directly. This is the one place the pass
  departs from the handoff's letter.
- **Decision A raises the value of #49** (player condition UI). Fatigue is
  displayed nowhere, which is why #61 arrived without warning, and A makes the
  Fatigue-100 state more costly without making it more legible. Not this pass's
  job; worth stating.

**Explicitly out of scope**
Restated from the handoff so this needn't be opened to know what isn't here.
- **`consumeFromPools()` gaining a return value.** It is the root hazard behind
  both #62 and #64 — five call sites can all silently under-pay the same way —
  and it is a different pass, because it touches `doCraft()` and
  `doDismantleCampfire()`, which are otherwise untouched here. Nothing in this
  pass forced it.
- **`fmtDuration()`'s `MIN_MOVE_MIN` floor (#75).** The Sleep gate removed the
  symptom that made it visible; the floor itself is untouched.
- **Whether "Add fuel", "Put out the fire" and Eat/Drink should cost game time.**
  All three are free while every other action charges. A balance question
  spanning three subsystems; #64 notes it and this pass does not answer it.
- **#66** (ten spawn pools never roll) and **#67** (single-copy tool gates).
  Both bear on the firewood economy and neither is touched.
- **#29** (the log's size and 50-entry cap). This pass edits `log()` and leaves
  `LOG_MAX_ENTRIES` and `#log`'s `max-height` alone.
- **#78** (accessibility). The new cooldown note inherits `var(--ink-faint)` at
  12.5px, matching the existing note's styling and its WCAG AA failure. #78
  fixes both together or neither.
- **The `", Riverbank"` location label.** Real and reproduced, but it belongs to
  #42's decision about what the `building` field means.

**Explicitly NOT changed**
- **WORLD DATA.** No room, item, container, exit, door, window or description.
  `ITEM_REGISTRY`, `LOCATIONS`, `BUILDINGS` and every `build*()` function show
  zero diff.
- **The save format.** No new or changed PLAYER STATE field, ITEM DATA SCHEMA
  field, tag or category, and no room/container/exit schema change. `SAVE_KEY`
  does not rotate. Fix #63 does make some previously-loadable saves refuse to
  load — the malformed ones that currently load halfway and break the session.
  That is the point, and it is not a format change.
- **Balance constants.** `CAMPFIRE_KIT_COST`, `FIRE_BUILD_WOOD`,
  `FIRE_MINUTES_PER_WOOD`, `FIRE_MAX_MIN`, `SLEEP_ENERGY_RATE`,
  `SLEEP_COOLDOWN_MIN` and every recovery rate are untouched — only the
  comment above `FIRE_BUILD_WOOD` changed, to stop reading as though every
  fresh burn costs it.
- **`doAddFuel()`, `canBuildFire()` and `consumeFromPools()` bodies.**
  `canBuildFire()` gained a comment and nothing else; it was already correct
  under decision B.
- **`recoveryStep()` and the Stamina/Fatigue recovery rules.** The no-softlock
  result above is a measurement of existing behavior, not a change to it.

**Validation performed**
- **The handoff's acceptance tests were run as written**, against the real file
  in headless Chromium, on `origin/main` and on this branch, with the internals
  exposed by a test-only shim rather than by editing the shipped file.
- **#61:** all five table rows match. `E=70 Fa=40` and `E=16.1 Fa=100` — button
  absent, note "not tired enough", vitals untouched (was: `"Sleep (0:01)"`,
  Energy → 60 and → 0 respectively). `E=50 Fa=40` still runs 60 minutes to
  Energy 60; `E=85 Fa=0` still runs 90 minutes to Energy 100. Cooldown-not-elapsed
  now reads "slept too recently". No-softlock measured as recorded above.
- **#62:** a first build carrying 5 firewood leaves all 5 (was: 2), banks 170
  minutes after `BUILD_FIRE_MIN`, and consumes the kit. With 0 firewood,
  `canBuildFire()` is still true and the fire still lights. Relight with
  `campfireBuilt`, `fireMinutesLeft = 0` and 0 firewood is still refused; with 3
  firewood it builds, firewood → 0, `fireMinutesLeft = 170`. A banked relight
  spends nothing. All three log strings still reach their cases.
- **#64:** at 350 the button is absent (was: shown, one wood for 10 minutes); at
  301 absent; at 300 shown, and one wood takes it to 360.
- **#63:** eight save shapes. The four that previously threw — missing `floor`,
  missing `containers`, missing `exits`, non-array `inventory.items` — now
  return `false` cleanly with `state`, `world` and `totalMinutes` provably
  unchanged. The three already rejected (empty object, missing `world`, unknown
  `currentRoom`) still return `false`. A well-formed save still round-trips
  byte-identically through `serializeGame()`.
- **#65:** three casts ending on a bite and three ending on a miss both render
  `[fresh]` (was: `[(none)]` and `[fresh]` for the same text). Regression guards
  hold — a `warn` line still breaks a tally run into separate lines, a `craft:`
  run still keeps its `good` class and its `×3` counter and is still not fresh,
  and the 50-entry cap still trims from the front.
- **No page errors** on load or during any test run.
- **Diff discipline:** `git diff origin/main...HEAD -- ashfall.html` is 14 hunks
  and 127 changed lines, the lowest at line 256 (the version bump) and the next
  at 3576 — past the whole of WORLD DATA. No `build*()` function appears in the
  diff.

**Sections touched**
- **SURVIVAL / TIME SIMULATION**, STAMINA / FATIGUE sub-block — `doSleep()`,
  `sleepAvailable()` and its two new halves, `sleepEnergyCeiling()`,
  `estimateSleepMinutes()`.
- **FIRE / COOKING** — `doBuildFire()`, `canBuildFire()`'s comment, the
  `FIRE_BUILD_WOOD` constants comment.
- **PERSISTENCE** — `applyLoadedData()`, new `validateLoadedWorld()`.
- **CORE UTILITIES** — `log()`.
- **RENDERING** — the sleep gate and the "Add fuel" gate in
  `renderHereActionsPanel()`.

**Documentation**
- Comments added or rewritten at each changed site: the `FIRE_BUILD_WOOD` block
  (a first fire comes from the kit, a rebuild costs `FIRE_BUILD_WOOD`),
  `canBuildFire()`'s first-build branch, `doBuildFire()`'s hoisted `banked` and
  its kit-burn derivation, `doSleep()`'s ceiling snapshot and its `Math.max`
  rationale, the Sleep-gate halves including the Fatigue-100 consequence,
  `log()`'s summary branch (unclassed *and therefore* fresh), the "Add fuel"
  gate, and `validateLoadedWorld()`/`applyLoadedData()`'s atomicity contract.
  The ARCHITECTURE comment needed no change — no section gained or lost a
  responsibility.
- **Nothing was deferred and no new issues were filed.** The pass surfaced
  nothing beyond what the handoff already listed as out of scope; every item in
  that list has an existing issue or is named there.

**Version**: `GAME_CONFIG.VERSION` `"0.4.10"` → `"0.4.11"`

---

## v0.4.10 — Building identity in WORLD DATA, and Close-map labels that fit

Implements: handoffs/map-building-identity-and-label-fit.md

Implements #39 and #16 in full, per
`handoffs/map-building-identity-and-label-fit.md`. Three parts: a building's
name and anchor move out of RENDERING into WORLD DATA, Close-map building
labels stop being cut off by the edge of the view, and the two-column layout
collapses to one column on a phone. No mechanic, no content, no save field and
no player-facing text changed.

**Organization / Structural**
- **`MAP_BUILDINGS` is split in two along the line between what a building is
  and how it is drawn.** `BUILDINGS` (WORLD DATA, immediately after
  `LOCATIONS`) holds `name` and `anchor` keyed by a stable building id;
  `MAP_BUILDING_OFFSETS` (RENDERING/MAP) holds the `dx`/`dy` label offset under
  the same keys. `renderMapClose()` and `mapBindBuildingLabels()` read both.
  `MAP_BUILDINGS` is gone. A building's name and the Location it sits on are
  reference data, the same category as `LOCATIONS` itself — the label offset is
  the only part of the old table that was genuinely about rendering.
- **Membership of `MAP_BUILDING_OFFSETS` is now what decides which buildings
  the map names.** A `BUILDINGS` entry with no offsets entry is never reached by
  `renderMapClose()`. Every building has one today, so exactly the same eleven
  markers are drawn; the seam exists for #8, where two buildings can sit close
  enough that only one can carry a label. Both tables carry a comment saying so,
  since a table whose every key is present cannot show it.
- The `LOCATIONS` comment on Pharmacy/Hardware Store sharing an anchor now names
  `MAP_BUILDING_OFFSETS` and says which section it lives in, rather than naming
  a table that no longer exists.

**Fixed**
- **Close-map building labels are no longer cut off by the edge of the view.**
  Root cause: `renderMap()` rebuilds the SVG only when the zoom *mode* changes —
  a move or a `+`/`−` step animates the viewBox underneath the existing markup
  instead — so `renderMapClose()` wrote each label's `x`/`y` once, at build
  time, and the box then slid out from under it. There was no point in the Close
  path where a label and its live viewBox were both in hand. Fixed by mirroring
  the split Wide has used since v0.4.5: `mapBindBuildingLabels()` caches the
  pool once per rebuild, and `mapPositionBuildingLabels(box)` places it from both
  sites that set the viewBox — the snap branch and every animation frame of
  `mapUpdateViewBox()`.
- Measured over all 191 Locations at all three Close steps: **41 / 62 / 117
  clipped label lines before, 0 / 0 / 0 after**. The original v0.4.0 repro —
  `Pharmacy` rendering as `Pharm` from the starting location at the default
  zoom — no longer reproduces.
- **The page no longer scrolls sideways below 480px.** `main` was
  `grid-template-columns:1fr 320px` with no `@media` rule anywhere in the
  stylesheet, giving the document a hard 476px floor: `scrollWidth` was 476 at
  320, 360, 375 and 414. One breakpoint at 760px collapses it to a single
  column. `scrollWidth === clientWidth` at 320/360/375/414/480/760, and the
  grid is unchanged from 761 up.

**New**
- `mapBindBuildingLabels()` (RENDERING/MAP) caches each marked building's dot
  position, its one or two `<text>` nodes, half the width of its widest line,
  and the block's vertical extent. Widths come from `getComputedTextLength()` on
  the bound node rather than a hand-kept table — a table would need re-measuring
  on every rename and would not survive #8 adding buildings. Bind runs only on a
  zoom-mode change, the moment that already rebuilds the SVG, so a pan does no
  layout reads. It returns early outside Close, which is what keeps Wide
  untouched.
- `mapPositionBuildingLabels(box)` (RENDERING/MAP) applies three rules per
  label. **Suppress** — if the marker circle does not intersect the box at all,
  every line is hidden. **Clamp horizontally on a shared centre** — `cx` is
  `dot.x` clamped into `[box.x + PAD + half, box.x + box.w - PAD - half]`, the
  same `cx` for both lines, so a two-line name stays centred as a block instead
  of staggering. **Clamp vertically as a unit** — the block's extent is shifted
  inside `[box.y + PAD, box.y + box.h - PAD]` and that one shift applies to both
  lines' `y`.
- Suppression rather than a bigger clamp is what keeps a name near the thing it
  names. A clamp alone removes all the clipping but can drag a name most of a
  view away to sit pinned against an edge pointing at a dot that isn't drawn.
  Every such case is a building whose own marker is off screen, so those are
  hidden instead — the same call `mapLabelHitsPlayer()` already makes for street
  names under the player marker, for the same reason: a slide can cascade.
  Measured max distance from a drawn label's centre to its own dot: **32.7 user
  units**, against `MAP_BLDG_LABEL_PAD + half` as the bound.
- `MAP_BLDG_DOT_R` (6), `MAP_BLDG_LINE_H` (11) and `MAP_BLDG_LABEL_PAD` (6) are
  named in the MAP sub-block. The first two were literals inside
  `renderMapClose()`'s loop and are now each read from two places — the marker
  circle and the visibility test, the line spacing and the positioner.

**UI**
- Close map: no building label is drawn outside the view, and a label whose
  building marker is off screen is not drawn at all. The set of markers, their
  coordinates and their offsets are unchanged.
- Below 760px the sidebar sits under the main column instead of beside it, and
  `#left`'s `border-right` becomes a `border-bottom` — at full width it would
  otherwise read as a stray rule down the right edge of the page. Above 760px
  nothing changes.
- No label, button, log line or description was reworded.

**Open questions / decisions resolved**
- **Where the label text is written** — the handoff left this between
  `renderMapClose()` emitting each `<text>` with its content already set, and
  the nodes shipping empty for `mapBindBuildingLabels()` to fill the way
  `mapBindStreetLabels()` does. Took the handoff's recommendation and emit the
  text in `renderMapClose()`: Wide's pool is generic across streets, whereas
  each building node belongs to one building, so filling it at bind time buys
  nothing.
- **The nodes ship visible, not hidden.** Wide's pool ships
  `style="display:none"` and this one deliberately does not: a hidden node has
  no layout, so `getComputedTextLength()` measures every name as zero wide and
  the clamp silently does nothing — caught in the browser during validation,
  where every label sat unmoved on its dot. `renderMap()` sets the markup,
  binds and snaps in one synchronous pass, so nothing is painted at the origin
  in between.

**Notes / assumptions**
- **`MAP_BLDG_LABEL_PAD = 6` is a judgment call with no prior convention and is
  retunable**, flagged as such in the source. Anything from about 4 to 10
  behaves the same; the bound on how far a name can sit from its dot moves with
  it.
- **The 760px breakpoint is retunable.** The measured overflow cliff is between
  414 and 480, so any value from 480 up removes the overflow. 760 is chosen
  because the layout stops being *usable* well before it starts overflowing — at
  375px the room description renders about three words wide — and because it is
  the value the superseded `handoffs/map-view-ui-fixes.md` proposed, so it has
  the most thought behind it. Nothing depends on the exact number.
- **The label block's vertical extent is taken from the line box, not a measured
  ink band.** `MAP_BLDG_LINE_H` (11) is taller than the 10px face's cap height,
  so the top edge is conservative, and `MAP_BLDG_LABEL_PAD` covers what a
  descender reaches past the bottom baseline. Retunable with the face, like
  `MAP_LABEL_CAP` for street names.
- **The gaps between a dot and its label (10 above, 16 below) stay literals**
  and keep their v0.4.9 values, so no unclamped label moved. They are not
  symmetric because a baseline below the dot has to clear the circle while one
  above it only has to clear the cap height.

**Explicitly out of scope**
- **#8** — no building is added, moved or renamed. This pass builds the
  `MAP_BUILDING_OFFSETS` seam #8 needs; filling it is that pass's job, specced
  in `handoffs/building-placement-and-elm-st.md`.
- **#42** — the `building` field meaning a building name on multi-room buildings
  and a street on single-room ones. Routed around with a separate table; no room
  definition was edited and `roomLabel()` was not touched.
- **#43** — `MAP_LABEL_W` as a hand-measured font width. This pass is what
  establishes whether bind-time measurement reads well.
- **#37** — Wide-map street names drawn outside the box. Same family of bug in
  the other mode; its fix is in `mapPositionStreetLabels()`, untouched here.
- **Label-vs-label overlap between buildings.** No two building label lines
  overlap at any position today, which is a property of there being eleven
  buildings rather than of the placement logic, which has no overlap test at
  all. Left as is.
- Retuning any `dx`/`dy`; the zoom ladder and `MAP_ZOOM_RANGE`; anything in Wide
  mode; a mobile-first redesign, touch or gesture support, and `#sideMenu`,
  which is `position:fixed` with `max-width:92vw` and already behaves at phone
  widths.

**Explicitly NOT changed**
- **No room, item, container, exit, door or window definition.** `BUILDINGS` is
  a new reference table; `makeDefaultWorld()` is untouched.
- **No balance constant, threshold or duration.**
- **The save format.** PATCH, so `versionCompat("0.4.10")` still yields `0.4`
  and `SAVE_KEY` is unchanged — existing browser saves keep loading. `BUILDINGS`
  is not persisted; saves restore `world`, `doors` and `windows`, and it is none
  of those. No new `state` field: `mapBuildingLabels` is module-level beside
  `mapStreetLabels`, deliberately outside `state`, as `mapZoomMode` and
  `mapZoomStep` already are.
- **Wide mode.** It draws no building markers, `mapBindBuildingLabels()` returns
  early outside Close, and `mapPositionStreetLabels()` was not edited.
- **Marker positions.** All eleven dots are at byte-identical coordinates before
  and after, and every `name`, `anchor`, `dx` and `dy` survived the table split
  unchanged.
- ACTIONS, SIMULATION, PLAYER STATE and PERSISTENCE.

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` is the diff of record.
- Syntax check on the extracted `<script>` body (`node --check`), clean.
- **Table split proven entry by entry**, not asserted: both versions loaded in
  Chromium side by side and all eleven entries compared by name — `anchor`,
  `dx` and `dy` identical across the split, no `BUILDINGS` entry without an
  offset and no offset without a `BUILDINGS` entry.
- **Clipping replayed in Chromium over all 191 Locations at all three Close
  steps**, on both `origin/main` and this branch, by placing the labels for each
  Location's target viewBox and reading each visible node's `getBBox()`. Lines
  crossing a box edge: **41 / 62 / 117 before, 0 / 0 / 0 after**. Every drawn
  label is fully inside its box, and the set of drawn labels is exactly the set
  whose own marker circle intersects the box.
- **No marker moved**: the eleven `circle.map-bldg-dot` coordinates are
  identical between `origin/main` and this branch.
- **The real game run in Chromium**, not just the placement replayed: load, open
  the map, toggle Close → Wide → Close, step the zoom through its range in both
  directions, and walk to another room. No page errors, no console errors. Wide
  emits 48 street-name nodes and zero building labels; Close rebinds after the
  round trip and places its labels with zero clipped.
- **Widths measured in Chromium at 320/360/375/414/480/760/761/900/1200.**
  `scrollWidth === clientWidth` at every one; `main` is one column through 760
  and `1fr 320px` from 761 up. The same measurement on `origin/main` gives
  `scrollWidth` 476 at 320/360/375/414, which is the overflow being fixed.

**Sections touched**
- **WORLD DATA** — the new `BUILDINGS` table and one comment retarget on
  `LOCATIONS`. No room, item, container or exit definition.
- **RENDERING / MAP** — `MAP_BUILDING_OFFSETS`, `MAP_BLDG_DOT_R`,
  `MAP_BLDG_LINE_H`, `MAP_BLDG_LABEL_PAD`, `renderMapClose()`,
  `mapBindBuildingLabels()`, `mapPositionBuildingLabels()`, the two call sites
  in `mapUpdateViewBox()` and the bind call in `renderMap()`.
- **The document `<style>` block** — one `@media` rule.

**Documentation**
- Nothing was deferred and no scope was cut, so this pass files no new issues.
  #42, #43 and #37 were already open before it started and none was touched.
- `handoffs/building-placement-and-elm-st.md` is unblocked by this pass: it
  assumes the `BUILDINGS` / `MAP_BUILDING_OFFSETS` seam has shipped.

**Version**: `GAME_CONFIG.VERSION` `"0.4.9"` → `"0.4.10"`

## v0.4.9 — Self-documenting source: named game rules, comments without history

Implements: handoffs/source-self-documenting.md

Implements #33 in full, per `handoffs/source-self-documenting.md`. One pass over
`ashfall.html` with a single goal: the source should say what is true now,
without prose propping it up. No mechanic, value, string or save field changed.

**Organization / Structural**
- **Five action durations that were written twice now have one home.**
  `FISH_DURATION_MIN` (20), `LIGHT_STOVE_MIN` (5), `BUILD_FIRE_MIN` (10),
  `DISMANTLE_CAMPFIRE_MIN` (10) and `CHOP_TREE_MIN` (30) are declared once in
  FIRE/COOKING; `advanceTime()` in ACTIONS and `fmtDuration()` in RENDERING both
  read them. A button and the action it launches can no longer disagree about
  what something costs — that was six literals across a section boundary, and is
  now five constants. `BUILD_FIRE_MIN` and `DISMANTLE_CAMPFIRE_MIN` share a value
  and are deliberately kept as two constants: they are different facts, and
  merging them would mean retuning one silently retunes the other.
- **The fire derivation is written out.** `FIRE_BUILD_WOOD` (3) and
  `FIRE_MINUTES_PER_WOOD` (60) replace the bare `3` in `canBuildFire()` /
  `doBuildFire()` and the bare `60` in `doAddFuel()`, and `doBuildFire()` now
  sets `room.fireMinutesLeft = FIRE_BUILD_WOOD * FIRE_MINUTES_PER_WOOD` instead
  of a literal `180`. The 3 x 60 = 180 relationship previously existed only as a
  coincidence between two functions thirteen lines apart; it now holds by
  construction. `CAMPFIRE_KIT_COST` (also 3) is untouched and deliberately not
  merged — it is what the kit contains, not the fuel a burn costs.
- Also named in FIRE/COOKING: `HEAT_CONTAINER_CAPACITY_KG` (8, the stove and the
  campfire alike, previously two literals), `CHOP_TREE_FIREWOOD` (6) and
  `FISH_BITE_CHANCE` (0.55). `FIRE_MAX_MIN` (360) moved up from its inline
  declaration into the same block so FIRE/COOKING's constants have one home.
- `LOG_MAX_ENTRIES` (50) names the log cap in `log()`. This is the number #29
  exists to re-judge; naming it is the precondition for that issue, not its
  fulfilment, and the value is unchanged.
- SURVIVAL / TIME SIMULATION gained the health-drain rates as named divisors:
  `STARVATION_MINUTES_PER_HEALTH` (30), `DEHYDRATION_MINUTES_PER_HEALTH` (15),
  `ILLNESS_MINUTES_PER_HEALTH` (20), plus `ILLNESS_DURATION_MIN` (180), which
  `doConsume()` sets and `applyHungerThirst()` spends. The divisor form
  (`min/30`, not `(1/30)*min`) was kept deliberately — see **Validation
  performed**.
- `advanceTime()`'s collapse branch had five anonymous numbers in six lines and
  now has `COLLAPSE_BLACKOUT_EVERY` (3), `COLLAPSE_BLACKOUT_MIN` (300),
  `COLLAPSE_BLACKOUT_ENERGY` (90), `COLLAPSE_STUMBLE_MIN` (20) and
  `COLLAPSE_STUMBLE_ENERGY` (30).
- `DAY_START_MIN` (`8*60`) names the start-of-day offset in `getClockText()`.
  It shares a value with `SLEEP_COOLDOWN_MIN` and is deliberately separate.

**Documentation**
- **Version tails stripped, sentences kept** across some 60 comment sites. Where a
  version was the whole comment it went entirely: `// Current version: 0.4.6.`
  inside the ARCHITECTURE block (two versions stale, and duplicating
  `GAME_CONFIG.VERSION` twenty-odd lines below), and the six-line RENDERING
  preamble whose "Unchanged in this revision" had no referent at `main`. The
  seven `Silent:` notes in INVENTORY/ITEM SYSTEM kept their sentences — each
  explains why a `log()` call is *absent*, which is the one thing no reader can
  see in the code.
- **A version naming save-data vintage is a live predicate and stayed.**
  `backfillLocationIds()`'s "Older saves (pre-v0.2.9) predate the locationId
  field" and `backfillContainerFields()`'s "(pre-v0.4.0)" describe the shape of
  data still sitting in people's browsers, not when code arrived. Strip the
  version and the comment stops meaning anything. Both kept verbatim.
- **All 18 `sec. N` citations stripped, sentences kept.** They cited numbered
  sections of a Stamina & Fatigue handoff that is not in the repository, and the
  v0.2.1 changelog entry that carries those rules has no numbered sections to
  resolve them against. Every sentence stands without the citation.
- **Dead handoff pointers stripped.** None of the cited names
  (*"Ashfall v0.2.1 — Stamina & Fatigue System"*, *"Container Spawn Pools &
  Population System"*, *"Ashfall v0.2.9.md"*, *"Ashfall v0.2.5.md"*, the v0.3.0
  handoff) resolves to anything in `handoffs/`. Where a pointer carried a
  provenance clause and nothing else, both went; where it sat beside a live
  judgment-call flag, the flag stayed — ITEM_REGISTRY keeps *"weights are
  estimates … retunable"* and SPAWN_POOLS keeps the *"commoner items 5-8, rarer
  or bulkier ones 1-3"* convention.
- **Stale references retargeted.** `lastRolledMinute`'s "roadmap item 15" →
  `#15`; the RENDERING/MAP banner dropped "Tier 1 item 3" (tier is a GitHub
  label now); the PERSISTENCE comment's "Save format is unchanged in 0.1.3
  (still {…})" became a plain statement of the format, which is the only place
  it is written down.
- **One correction to the handoff.** It directed the documents/lore comment's
  "roadmap item 13" to `#13`, reasoning from the `#15` coincidence. It does not
  hold: `#13` is *Hunting with traps*; roadmap item 13 migrated to **`#7` — Lore
  development**, which its issue body states outright. Retargeted to `#7`.
- **One dead pointer the handoff's audit did not catch.** The STAMINA/FATIGUE
  module header said "(see CORE ACTIONS below)". No CORE ACTIONS section exists —
  ACTIONS is grouped as INVENTORY/ITEM SYSTEM, WORLD INTERACTION, CRAFTING and
  FIRE/COOKING — and the sections it meant are *above* that line, not below.
  Pointer stripped; the sentence stands on its own. Every remaining `see X` in
  the file now resolves to something in the file.
- **Two whole-comment pointers were repointed rather than deleted**, per the
  handoff's first design decision — see **Open questions / decisions resolved**.
- Nothing was deferred that needs a new issue. The Part B4 literals left alone
  are recorded below as judgment calls, not cut scope.

**Explicitly NOT changed**
- **No value changed.** Every constant introduced equals the literal it
  replaced, checkable one by one against the handoff's tables.
- **No player-visible string changed.** The five duration buttons render the
  same text; they just read the constant the action spends.
- Balance constants, `RECIPES`/`HEAT_RECIPES`, the stamina/fatigue rules, and
  both recovery ladders are untouched.
- **Save format and `SAVE_KEY` unchanged.** No new or changed state fields, item
  schema fields, tags, categories, or room/container/exit fields. This is a
  PATCH, so `versionCompat()` still yields `0.4` and existing browser saves load.
- **No WORLD DATA content changed** — no room, item, container, exit or
  description. The pass reached into WORLD DATA's *comments* only.
- Rendering logic and every function body outside the literal-to-constant
  substitutions are byte-identical.
- The ARCHITECTURE block's section list, the ROOM/CONTAINER/EXIT/ITEM schema
  blocks, and the LOCATIONS coordinate convention all keep their content.

**Validation performed**
- `git diff origin/main...HEAD -- ashfall.html` is the diff of record.
- **Part A proof:** with every full-line `//` comment stripped from both sides,
  the before and after files are identical apart from one trailing comment on a
  code line (`mapStreetLabels`). No comment edit ran into code.
- **Part B proof:** every non-comment line in the diff is a literal replaced by a
  constant of the same value, or the version bump — the full list is short enough
  to read in one screen of `git diff`. For the five duration pairs, both halves
  now read the same constant, so button and action cannot disagree by
  construction.
- The health-drain constants are divisors (`min/STARVATION_MINUTES_PER_HEALTH`),
  not per-minute rates (`STARVATION_HEALTH_PER_MIN*min`), specifically so the
  floating-point arithmetic is bit-identical to what it replaced. The rate form
  reads marginally better and can differ by an ulp; on a pass whose whole claim
  is "no behaviour change", the divisor form was the honest choice.
- Syntax check: the `<script>` body extracted and run through `node --check`.
- Runtime check: the same body evaluated under a minimal DOM stub, which
  completes module init and a full first render pass. This catches the one real
  hazard in Part B — a temporal-dead-zone error from a `const` referenced before
  its declaration (`ILLNESS_DURATION_MIN` is declared in SURVIVAL and read by
  `doConsume()` above it; safe because the read happens inside a function body).
- Section-banner audit: all 19 ARCHITECTURE section and sub-block banners present
  and well-formed. Deleting the RENDERING preamble briefly collapsed the
  RENDERING and MAP banners into one; caught and fixed.

**Sections touched**
CONFIG / CONSTANTS, WORLD DATA (comments only), PLAYER STATE (comments only),
SURVIVAL / TIME SIMULATION including STAMINA/FATIGUE, ACTIONS — chiefly
FIRE/COOKING — PERSISTENCE (comments only), and UI / RENDERING including MAP.
Wide but shallow: outside Part B's constant introductions, no executable line
changed.

**Open questions / decisions resolved**
- **Repointing whole-comment pointers: taken, twice.** Where a dead pointer was
  the comment's entire content *and* the target changelog entry genuinely carries
  the rules, it was repointed rather than deleted — the STAMINA/FATIGUE header
  now reads "See the v0.2.1 entry in CHANGELOG.md for the full rules", and
  SPAWN_POOLS points at the v0.4.0 entry. A reader following either comment wants
  the rules, and unlike a `sec. N` citation this resolves. The SPAWN_POOLS one
  was reworded rather than repointed verbatim: the v0.4.0 entry describes the
  design but has no per-container assignment table, so that half of the sentence
  now says the assignments live on the containers' own `spawnPools` fields, which
  is both true and closer to hand.
- **`FIRE_MAX_MIN` left as 360, not derived.** It is `6 * FIRE_MINUTES_PER_WOOD`,
  but writing it that way invents a `FIRE_MAX_WOOD` nothing else uses. The cap
  reads as its own fact — six hours of banked burn, however you got there.
- **Both recovery ladders left as `if`-chains.** `energyRecoveryMultiplier()`
  (80/60/40/20 → 1.00/.90/.75/.50/.25) and `staminaMaxForEnergy()`
  (40/20 → 100/80/50) read perfectly well today; a table of named thresholds
  would be more machinery for no gain at the call site.
- **Left literal, read at the call site and judged clearer as numbers:** the
  sleep-vs-rest energy multipliers (`applyEnergyBaseline(dt, mode === "rest" ? 1
  : 2)`) — the parameter already names itself; the starting vitals
  (75/75/85/100/100/0) and starting inventory capacity — per-instance data in an
  object literal whose keys name each number; and the `-9999` "never happened"
  sentinels, which the comment directly above them explains better than a name
  would.
- **The LOCATIONS coordinate-convention block** is on the handoff's "stays
  untouched" list, but its stale `"Ashfall v0.2.9.md"` pointer is named in the
  handoff's own dead-pointer enumeration. It was read as structural protection —
  don't rewrite the convention — so the block keeps every word of its content and
  received only the line-level version/pointer strips, on the precedent the
  handoff itself set for `// Current version: 0.4.6.` inside ARCHITECTURE.
- **Naming judgment calls, all retunable:** `STARVATION_MINUTES_PER_HEALTH` and
  its siblings use a `_MINUTES_PER_HEALTH` suffix rather than the file's `_MIN`
  suffix, because `_MIN` reads as "a duration" everywhere else and these are
  rates. `COLLAPSE_BLACKOUT_ENERGY` is set-to while `COLLAPSE_STUMBLE_ENERGY` is
  added-to; the asymmetry is pre-existing behaviour and is flagged in a trailing
  comment on each rather than hidden behind matching names.

**Explicitly out of scope**
- **#29** — the log cap's *value*. The 50 is named, not changed.
- **#23** — the illness system. `ILLNESS_DURATION_MIN` names the existing timer
  and nothing is built on it.
- **#39** — `MAP_BUILDINGS` as world data living in RENDERING.
- **#37, #16** — open map/UI issues, adjacent but not prerequisites.
- **#32** — the v0.4.4 / v0.4.5 tag correction, which is run locally.

**Version**: `GAME_CONFIG.VERSION` `"0.4.8"` → `"0.4.9"`

---

## v0.4.8 — Map zoom ladder, and street names clear of intersections

Implements: handoffs/map-zoom-and-label-collisions.md

Implements #27 and #28 in full, per `handoffs/map-zoom-and-label-collisions.md`.
Two changes taken as one pass because they land in the same code: the `+`/`−`
buttons shipped inert in v0.4.5 get a working zoom ladder, and the street-name
placement that ladder retunes gets its intersection-collision fix.

RENDERING only, and within it the MAP sub-block. No new state fields — the zoom
step joins `mapZoomMode` as a module-level `let`, deliberately outside `state` —
so `SAVE_KEY` still derives from `0.4` and existing browser saves keep loading.
No WORLD DATA, no mechanics, no stylesheet change.

**Changed / Reworked**

*Zoom ladder*

- A view's span is now a whole number of blocks: `span = mapZoomStep *
  MAP_SPACING`. `MAP_ZOOM_RANGE` gives each mode the steps it allows and the
  step it opens at — Close `1..3`, base `2` (130 / 260 / 390 units across);
  Wide `3..6`, base `6` (390 / 520 / 650 / 780). `mapTargetViewBox()` reads the
  step instead of picking a span from `mapZoomMode`, which now only bounds the
  range.
- `+` zooms in, which is a *smaller* span: the step counts blocks across, so
  `mapZoomIn` decrements it.
- The step is clamped in `mapSetZoomStep()`, at the two places it changes — a
  `+`/`−` click, and the mode toggle moving the range under it — and nowhere
  else. Both buttons take their `disabled` state from the same range in the
  same call, so a button never offers a step that would do nothing, and
  `mapTargetViewBox()` does no per-frame clamping of a value that changes only
  on a click.
- Switching mode clamps to the nearest step the new mode allows rather than
  resetting to its base. Where the ranges overlap this keeps the box: Close@3 →
  Wide@3 is the same 390-unit view with only the content changing.
- A zoom step re-aims the existing viewBox and does not rebuild the SVG —
  content stays keyed on the mode via `mapRenderedZoom`. The existing 350ms
  animation already interpolates `w`/`h`, and `mapPositionStreetLabels()`
  already runs per frame, so the names re-place themselves as the span changes.
  A **mode** switch still rebuilds, as before.

*Street-name placement (Wide)*

- `mapLabelPositions()` now passes its tier positions through
  `mapClearCrossings()`: a position within `MAP_LABEL_CLEARANCE` of an
  intersection slides to the mid-block beside it. Intersections fall on the grid
  pitch along both axes, so this is arithmetic on the position rather than a
  walk through the street's chain.
- `mapPositionStreetLabels()` takes the player's map node and drops any name
  whose box would fall under the player marker, which nothing in the placement
  previously knew about. `mapLabelBox()` is the one description of what a name
  occupies, used by that test and derived from the same constants as the
  clearance.

**Fixed** — #28, street names colliding at intersections

A name is placed against the *clipped visible* stretch of its street, so an
inset position frequently landed within a name's own width of a crossing, where
a horizontal name's band and a vertical name's band overlap. v0.4.7 put 213
overlapping pairs on screen across the 176 map nodes at its single span. Sliding
those positions to a mid-block — `MAP_SPACING / 2` from either crossing — is
what removes them; the count is now 0 at every span on the ladder (see
**Validation performed**).

**Removed**

- `MAP_CLOSE_VIEW` (260) and `MAP_WIDE_VIEW` (800). Both are now the `base`
  entries of `MAP_ZOOM_RANGE`, expressed in blocks, and the span is derived
  where it is read. Keeping either as a named derivation would have left a
  constant with no remaining use.

**New constants**

- `MAP_LABEL_W` (99.1) and `MAP_LABEL_CAP` (12) — the rendered width of the
  widest name on the map (`"POPLAR ST"`) and the cap height, in user units at
  the 15px `.map-street-name` face. Measured against the font, not chosen, and
  commented as such: every name is upper case with no descender, so the cap
  height is the whole ink band.
- `MAP_LABEL_CLEARANCE` = `MAP_LABEL_W / 2 + MAP_LABEL_OFFSET + MAP_LABEL_CAP`
  (66.55) — how far past an intersection a name's box can still reach the
  crossing street's name.
- `MAP_LABEL_EDGE_GAP` (5), the breathing room in the inset below.

**Derivations named** (previously bare literals, same or near-same values)

| Was | Now | Value |
|---|---|---|
| `MAP_CLOSE_VIEW = 260` | `MAP_ZOOM_RANGE.close.base * MAP_SPACING` | 260 |
| `MAP_WIDE_VIEW = 800` | `MAP_ZOOM_RANGE.wide.base * MAP_SPACING` | **780** |
| `MAP_LABEL_INSET = 55` | `MAP_LABEL_W / 2 + MAP_LABEL_EDGE_GAP` | 54.55 |
| `MAP_LABEL_TIERS` 600 / 300 / 110 | `6 / 3 / 1 * MAP_LABEL_W` | 594.6 / 297.3 / 99.1 |

Wide's default view is **780 rather than 800** — a deliberate 2.5% tightening
of shipped v0.4.5 behaviour, approved during planning, so that every view on the
ladder sits on the block pitch. The tier thresholds move by under 2% except the
smallest, where 110 → 99.1 makes "one name wide" the literal condition for
getting one name. The tiers are a crowding rule, not a legibility one: a name's
width in user units is the same at every span, so what they measure still means
the same thing, and the ladder's ranges are what keep names readable. As
predicted in #27, the 1-label tier is reachable now — unreachable at span 800,
it fires at every span on the ladder.

**UI**

- `+` and `−` are live, each disabling itself at its end of the current mode's
  range; the static `disabled` attributes are gone from the markup and the
  initial state is set from the range at boot. Neither button gained a
  `data-zoom` attribute, which would have captured it into the Close/Wide
  handler.
- Close gains one step in and one step out of its previous view; Wide gains
  three steps in, and its default view is very slightly tighter.
- Wide street names no longer collide at intersections and no longer sit under
  the player marker. A street that loses one of its two or three names to either
  rule keeps the others; where it was the only one, `#locBar` still names the
  player's location.

**Open questions / decisions resolved**

The handoff left four implementation choices open. The first three took its
recommended default; the fourth did too, as `mapSetZoomStep()`.

1. *Nudge direction* — toward the centre of the visible stretch. The mid-block
   on the far side is the fallback, and a name with neither left inside the
   stretch is dropped rather than slid again.
2. *Two names converging on one mid-block* — the one nearer the centre of the
   stretch keeps it. Generalised slightly: any two names on a street that end
   up closer than one name's width apart resolve the same way, which covers the
   near-miss as well as the exact tie.
3. *Shape of the clearance constant* — computed from the width and geometry
   constants at use, so retuning the face or the widest name carries through.
4. *How `disabled` is refreshed* — one helper, called from both handlers.

A fifth decision the handoff did not anticipate: **the clearance formula
itself**. The handoff derived `(width + height) / 2 ≈ 57.05` by treating a name
as a box centred on its anchor. It is not centred — it sits `MAP_LABEL_OFFSET`
off its own street line and its ink runs one cap height further, so the distance
at which a crossing name can still be touched is `MAP_LABEL_W / 2 +
MAP_LABEL_OFFSET + MAP_LABEL_CAP` = 66.55, and under the handoff's number a name
could sit 9.5 units inside that reach without being nudged. The implemented
constant uses the measured geometry.

**Notes / assumptions**

- Every number introduced here is retunable and none has a prior convention
  behind it: the two step ranges and their bases, the tier multipliers, and
  `MAP_LABEL_EDGE_GAP`. Close's ceiling was picked as the step where its 10-unit
  building labels stay near 10 CSS px (the map renders ~420px wide); Wide's base
  is the widest step that still leaves the town's 910 units something to pan
  within.
- `MAP_LABEL_W` keeps the handoff's measured 99.1. The same string measures
  98.2 in the browser this pass was validated in — fonts resolve differently per
  system — and the larger value is the conservative one for a clearance.
- **The clearance a mid-block gives is not symmetric, and one side of it is
  thin.** A mid-block sits 65 units from either crossing, which clears the 66.55
  reach on the side a name is slid away from but comes ~1.5 units short of it at
  the crossing beyond. Closing that gap needs the two names meeting there to
  *both* be within ~3 units of the widest: only `"POPLAR ST"` is, and it runs
  east-west, so it never meets another name that wide. The sweep confirms it —
  zero overlaps, and the closest two crossing names come is 12.6 units. A
  north-south street named wider than `MAP_SPACING - 2 * (MAP_LABEL_OFFSET +
  MAP_LABEL_CAP)` would reintroduce the collisions, and that constraint is
  recorded beside the constant. It is a tighter bound than the handoff's
  estimate of ~115 units, which came from the centred-box model above.

**Documentation**

- Filed #37: in Wide, a street lying exactly on the viewBox edge is still
  treated as on screen and given its names, which then render entirely outside
  the box. Pre-existing — v0.4.7 emitted the same 370 such labels at span 800,
  where they were sliced by the edge rather than missed by it — and out of this
  pass's scope. Surfaced by this pass's sweep.
- Nothing else was deferred. No ARCHITECTURE comment or schema comment changed:
  no section moved and no schema shape changed.

**Explicitly out of scope** (deferred by the handoff, still open)

- #16's close-map building-label clipping, and its mobile breakpoint.
- Neighbourhood / district labels, and any content that varies by span — that
  needs a spatial grouping layer the file does not have.
- Zoom or mode persistence, and any preferences store.
- Viewport culling in `renderMapClose()`, which still emits all 176 node dots
  per rebuild.
- Clamping `mapTargetViewBox()` to the town's bounds, deliberately left
  unclamped in v0.4.5.
- Any change to `LOCATIONS`, `MAP_STREETS` or `MAP_BUILDINGS`.
- #33's comment and literal pass, apart from the `MAP_*` derivations above,
  which this pass owned by agreement.

**Validation performed**

Headless sweep in Chromium against the real renderer, driving an instrumented
copy of `ashfall.html` (the shipped file plus one line exporting the map
internals). Every label box is read from the element's own `getBBox()` and
transform, so the geometry checked is what the browser drew, not the model the
code places from.

- **Wide — 176 nodes × 4 spans (390/520/650/780) = 704 positions, 11,428
  labels.** Zero overlapping pairs. Zero names outside their street's visible
  stretch. Zero clipped along the street's axis. No street over its tier's
  count. Zero names intersecting the player marker. Closest approach between two
  crossing names: 12.6 units.
- **The same sweep against v0.4.7** (176 nodes at span 800, 4,696 labels):
  **213 overlapping pairs**. This is the #28 regression test.
- **Close — 176 nodes × 3 spans (130/260/390) = 528 positions.** The viewBox is
  exactly the expected player-centred box at every one, and zero street names
  are emitted in any of them.
- **Controls**, clicked through the real UI: opens at Close step 2 with both
  buttons enabled; `+` reaches 130 and disables itself; `−` reaches 390 and
  disables itself; a forced click on a disabled button changes nothing; a zoom
  step leaves the SVG's children untouched (a marker attribute on the first
  child survives every step) while a mode switch replaces them (224 ↔ 66
  children); Close@3 → Wide holds the 390 box; Wide@6 → Close clamps to 3, not
  to base 2; Close@1 → Wide clamps to 3. Neither `+` nor `−` carries
  `data-zoom`.
- `node --check` on the extracted script, and a play-through (move six times,
  switch modes, zoom) with no page or console errors.
- Diff: `git diff origin/main...HEAD -- ashfall.html`.

**Sections touched**

RENDERING, MAP sub-block only — `MAP_ZOOM_RANGE` and the `MAP_LABEL_*`
constants, `mapSetZoomStep()`, `mapTargetViewBox()`, `mapUpdateViewBox()`,
`mapLabelPositions()`, `mapClearCrossings()`, `mapLabelBox()`,
`mapLabelHitsPlayer()`, `mapPositionStreetLabels()`, and the `#mapZoomToggle`
handlers. Plus the two `<button>` elements in the document body, and one line in
the boot sequence.

**Version**: `GAME_CONFIG.VERSION` `"0.4.7"` → `"0.4.8"`

---

## v0.4.7 — WORLD DATA cleanup: street/building split, vestigial exit fields, registry duplicate

Implements: handoffs/world-data-cleanup.md

Implements #3, #4 and #5 in full, per `handoffs/world-data-cleanup.md`. Three
`tier-0` cleanups taken as one pass because they all land in WORLD DATA. No
mechanics, no rendering, no new state fields, no save-format change —
`SAVE_KEY` still derives from `0.4`, so existing browser saves keep loading.

Parts 1 and 2 below are content edits; Part 3 is pure code motion. The only
player-visible change in the whole pass is the item name in Part 2.

**Removed** — WORLD DATA, 26 vestigial `distanceM` fields

`exitMinutes()` reads `exit.distanceM` only when both rooms share a
`locationId`; for a cross-Location exit it calls `locationDistance()` on the
two `LOCATIONS` entries instead and the field is never consulted. 26
cross-Location exits still carried one. All 26 are gone, leaving `{ to, label }`
(plus `doorId` where present), which is the shape the EXIT SCHEMA comment
already documented — this makes the code match a comment that was already
right, so the comment itself needed no edit.

- The 68 same-Location exits are untouched; every one still carries its
  hand-authored `distanceM`.
- `getExitsForRoom()`'s synthesized window-climb exit keeps its `distanceM:4`.
  Both windows (`2a-transom`, `1b-alley`) join rooms inside one Location, so
  that value *is* read; stripping it would have made a climb cost `NaN`
  minutes. It is also built at render time in WORLD INTERACTION, not WORLD
  DATA.

**Removed** — WORLD DATA, the `bandages` registry entry

`ITEM_REGISTRY` carried `bandages` ("Bandages") and `bandage` ("Bandage") as
byte-identical `Medical` / `0.05 kg` entries differing only in display name.
The singular survives; the plural is deleted and its seven references
repointed, every quantity preserved exactly:

- One `SPAWN_POOLS` entry (`{ itemId:"bandage", weight:8, qtyMin:1, qtyMax:3 }`)
  and six world placements (qty 4, 2, 2, 3, 5, 2 — 18 in total).
- The singular wins because it is the `RECIPES` output, so "Craft a bandage"
  no longer produces **Bandages ×1**; and because `Medical` is in `STACKABLE`
  and the detail view appends `×N`, where **Bandage ×4** is unambiguous and
  **Bandages ×4** is not. The registry's other Medical plurals (`Painkillers`,
  `Gauze rolls`) are mass or packaged nouns where `×N` counts containers; a
  bandage is not one of those.

**Organization / Structural** — WORLD DATA, one builder per street and per building

`buildStreetsAndOutdoor()` (60 rooms) and `buildOuterStreets()` (125 rooms) are
deleted and their 185 rooms redistributed across 21 new builders. The old seam
was "original core vs. the v0.4.1 outer ring", which cut through ten of the
sixteen streets — Maple, Main, Water and Poplar each had nodes in both
functions, as did 4th, 2nd, 1st, 3rd and 5th. A room now belongs to the street
its id names, so each street is defined in exactly one place.

- **Five building builders**, matching the existing `buildOakApartments()`
  pattern and placed beside the other building builders: `buildCornerStore()`,
  `buildPharmacy()`, `buildHardwareStore()`, `buildStorageFacility()`,
  `buildRiverbank()`. The v0.2.8 modularity pass extracted one function per
  building but left these four buildings and the riverbank set-piece inside
  the street function.
- **Sixteen street builders**, each merging that street's core and outer
  nodes: `buildDockSt()`, `buildMillSt()`, `buildCedarSt()`, `buildElmSt()`,
  `buildMapleSt()`, `buildPoplarSt()`, `buildMainSt()`, `buildWaterSt()` (15
  rooms each — 8 intersections plus 7 mid-blocks), and `buildSixthSt()`,
  `buildFourthSt()`, `buildSecondSt()`, `buildFirstSt()`, `buildThirdSt()`,
  `buildFifthSt()`, `buildSeventhSt()`, `buildNinthSt()` (7 mid-blocks each).
  They are emitted west to east, the order the grid itself runs in.
- `makeDefaultWorld()` now lists all 26 builders. Its `Object.assign` shape and
  its `applyComputedDirections(world)` return are unchanged.
- `buildOuterStreets()`'s sixteen `// DOCK ST` … `// 9TH ST` group comments are
  deleted rather than moved: the function names now carry what they carried.
  Its header comment describing the core/outer seam went with it, that seam no
  longer existing.
- Every room definition moved verbatim — same id, `locationId`, `desc`, flags,
  containers, floor items and exit list, in the same order within each room.

**Open questions / decisions resolved**

Both placement calls the handoff left open, resolved as it recommended:

- **`outside` goes in `buildPoplarSt()`.** It is the Poplar St / 1st St
  intersection under an id predating the grid, so the id-names-the-street rule
  doesn't reach it. The counts settle it: with `outside` in Poplar, all eight
  named streets own 15 rooms and all eight numbered streets own 7. It is
  **not** renamed to `poplar1st` — `applyLoadedData()` restores a save's world
  wholesale rather than rebuilding it from `makeDefaultWorld()`, so the id
  every existing save already holds has to keep resolving. A comment at the
  definition says so.
- **`alley` goes in `buildPoplarSt()`** too, keeping `buildAcornApartments()`
  strictly interior. The room's own `building:"Poplar St"` field is the
  tiebreak against its `locationId:"acorn_f0"`; it is the one room in the pass
  that neither the naming rule nor the room counts decide, which is why Poplar
  holds 16 rooms where the other named streets hold 15.

**Explicitly NOT changed**

- **No room id, container id or item id renamed**, the `bandages` deletion
  aside. See the `outside` note above for why.
- **No travel time re-tuned.** The 26 stripped values were already unread; see
  Validation below.
- **No new `distanceM` added anywhere**, and no same-Location exit lost one.
- **`SAVE_KEY`, the save format, and `applyLoadedData()`** — untouched. A PATCH
  bump keeps `ashfall_save_v0.4`.
- **No ACTIONS, SIMULATION, PERSISTENCE, or UI/RENDERING code.** `exitMinutes()`
  was read to confirm Part 1's premise and not edited.
- **No balance constant, threshold, or spawn weight.** `bandage` inherits the
  plural's `weight:8, qtyMin:1, qtyMax:3` exactly.
- **The outer nodes keep their empty `containers:[]`.** Placing buildings in
  the 44 new intersections and 81 new mid-blocks is #8, not this pass.
- **`bandage` gains no mechanical behavior.** It still has no `restores`,
  `verb`, `durability` or tags, and "Craft a bandage" is still a dead end;
  that belongs to #23.

**Validation performed**

`git diff origin/main...HEAD -- ashfall.html` is the diff of record (973
insertions, 880 deletions — the net +93 lines is the 21 function headers and
returns replacing 2, plus the `outside` comment). Beyond reading it, the world
was built out of the file before and after and compared:

- **Room set identical.** `Object.keys(makeDefaultWorld())` sorted matches
  exactly, 218 ids before and after.
- **Exit census.** Cross-Location exits carrying `distanceM` went 26 → 0; the
  26 that lost the field are exactly the 26 the handoff named. Same-Location
  exits missing one stayed 0. Totals held at 706 cross and 68 same.
- **Travel times unchanged.** `exitMinutes()` was evaluated for all 774 exits
  at all three gaits — 2,322 probes — with zero differences. This is the real
  test of Part 1: the field being unread was the premise, and this is what
  checks it.
- **Every room otherwise byte-identical.** With the stripped distances and the
  `Bandages`/`bandages` → `Bandage`/`bandage` rename normalized away, all 218
  room objects compare equal, exit order included. Nothing else moved.
- **Window climbs still finite.** Both windows, both directions, all three
  gaits: same-Location and 0:01, not `NaN`. Confirmed again in the browser —
  "Climb through the transom window (0:01)".
- **Syntax and runtime.** The script block parses, and the file was loaded in
  Chromium and driven through the DOM: a route out of the apartment across
  `mid_poplar_1_2`, `alley`, `outside`, `main1st` and `main3rd` (four different
  new builders) reported correct durations at every step, both map views
  rendered (188 node dots, 16 street runs, and the street names inside the
  player-centred window), and the medicine cabinet read
  `Bandage ×4 — 0.20 kg (Medical)`. Zero page errors throughout.

**UI**

- Six world placements and one loot pool now read **"Bandage ×N"** instead of
  **"Bandages ×N"**. Same weight, category, stacking and spawn odds.
- Nothing else the player sees changes: same rooms, same exits, same labels,
  same travel times, same map.

**Sections touched**

**WORLD DATA only** — the room builder functions, `makeDefaultWorld()`,
`ITEM_REGISTRY` and `SPAWN_POOLS`. Content-only in the Project Guide's sense.

**Documentation**

- The EXIT SCHEMA comment needed no edit: it already described the
  post-#4 bimodal shape.
- A comment at `outside`'s definition records that its id is historical and
  why renaming it would strand saves.
- **Nothing was deferred.** The pass surfaced no new work, so no issues were
  filed. #33 (the comment and magic-number pass) was already blocked on this
  one — its audit is expressed in line numbers that Part 3 invalidates — and is
  now unblocked.

**Version**: `GAME_CONFIG.VERSION` `"0.4.6"` → `"0.4.7"`

---

## v0.4.6 — Log: routine lines removed, repeated lines collapsed

Implements: handoffs/log-noise-and-collapse.md

Implements #21 and #22 in full, per `handoffs/log-noise-and-collapse.md`. The
log stops confirming what a panel already shows, and a run of the same action
reports once instead of once per repetition. Rendering behavior — how existing
state changes are surfaced. No mechanics, no world data, no vitals math, no new
state fields, no save-format change.

**Removed** — INVENTORY / ITEM SYSTEM, seven routine `log()` calls

Each failed the same test: does the line tell the player something the screen
doesn't already show?

- `doTake()` and `doStore()` — the item visibly moves between the Here and
  Inventory panels. `doStore()`'s `verb` local went with its line.
- `doEquip()` and `doUnequip()` — a new inventory tab appears, or disappears.
- The battery controls in `getItemActions()`: on/off (the detail view already
  reads "— On" / "— Off"), removal (the batteries appear in inventory and the
  view reads "No batteries installed") and replacement (the charge readout
  jumps to 100%).
- Every failure and redirect still speaks: "That won't fit", "No room for the
  … — it drops to the floor instead", "Your keychain can't hold that", "You're
  already carrying something in that slot", and every consequence line with no
  visible counterpart.
- `doConsume()` keeps its line. Eating is the one case where the panels don't
  tell the story: the item count drops, but the effect lands on Hunger and
  Thirst, which live behind the ☰ menu and are invisible during normal play.

**New** — EVENTS / UI HELPERS, collapsing consecutive runs

- `log(text, cls)` becomes `log(text, cls, key, outcome)`. Both new parameters
  are optional and every existing unkeyed call site behaves exactly as before:
  it never collapses, and nothing collapses into it.
- With a `key`, the line collapses into `#log`'s last child if that child
  carries the same `dataset.logKey`; otherwise it appends a new element
  carrying it. **Only consecutive runs collapse.** Any intervening line breaks
  a run — including a `warn`, on purpose: a string of ten "That won't fit"
  failures is worth seeing in full, and hiding repeated failures would hide a
  stuck player from themselves. `fish, fish, chop, eat, eat, drink, fish, eat`
  logs as `fish, chop, eat, drink, fish, eat`.
- **Tally actions** (fixed text) key on the action and re-render as prose from
  the second occurrence: `doFish()` as `fish` with `bite`/`miss` outcomes,
  `doRest()` as `rest`, `doChopTree()` as `chop`, `doAddFuel()` as `fuel`. The
  four sentences live in one `LOG_SUMMARIES` table beside `log()`: "You fish
  seven times. Three bites." / "Nothing bites." / "One bite." for the
  degenerate counts, "You rest for three hours.", "You chop down three
  trees.", "You feed three more pieces of wood into the fire."
- **Counted actions** (the text names an object) keep their sentence and class
  and gain a dim trailing `<span class="logcount">×3</span>`. Their keys carry
  the object — `consume:` + item id, `craft:` + output id, `cook:` + recipe id
  — so eating three different things can never render as one line naming the
  first. New style: `.logcount{ color:var(--ink-faint); font-size:11.5px;
  margin-left:5px; }`, so the count reads as functional UI rather than as part
  of the prose.
- `numberWord()` in UTILITIES, beside `fmtDuration()`: spelled out through
  ten, digits from eleven up, matching the game's prose.
- On collapsing a tally run the element's outcome class is cleared — a fishing
  run mixes a `good` bite with an unclassed miss, and the summary is a neutral
  report of both. Counted runs keep their class.
- `.fresh` follows its existing rule unchanged — stripped from every line,
  then applied to the line just written when `cls` is falsy — so the newest
  line stays highlighted whether it was appended or rewritten in place.
- Runs may span movement: `doMove()` logs nothing, so chopping a tree in three
  rooms in a row still collapses to one line. Intended.
- `doSearch()` is deliberately unkeyed: a room can only be searched once and
  different rooms would key differently, so it could never collapse.
- The 50-entry cap and the scroll-to-bottom behavior are unchanged.

**UI**

- Taking, storing, equipping, unequipping and servicing batteries are silent.
  Their failure warnings are not.
- Eating and drinking still report.
- A repeated action reads as one line: "You fish seven times. Three bites." /
  "You rest for three hours." / "You chop down three trees." / "You eat the
  canned soup. ×3".
- Failures never collapse.

**Sections touched**

- EVENTS / UI HELPERS — `log()`, the new `LOG_SUMMARIES` table.
- UTILITIES — the new `numberWord()` and `NUMBER_WORDS`.
- INVENTORY / ITEM SYSTEM — five removed `log()` calls across `doTake()`,
  `doStore()`, `doEquip()`, `doUnequip()` and the battery actions in
  `getItemActions()`; one key added in `doConsume()`.
- FIRE / COOKING — keys in `doFish()`, `doAddFuel()`, `doChopTree()`,
  `doCookInContainer()`.
- CRAFTING — key in `doCraft()`.
- WORLD INTERACTION — key in `doRest()`.
- The document `<style>` block for `.logcount`.

Only the `log()` calls inside those action functions changed; no ACTIONS
logic, no simulation rule and no vitals math was touched.

**Open questions / decisions resolved**

The handoff left four implementation calls open; all four took its recommended
default.

- **Where the summary text lives**: one `LOG_SUMMARIES` table next to `log()`,
  keyed by action id and taking the tally object — not sentences built at the
  four call sites. A future content pass edits all four strings in one place.
- **How a call site passes its outcome**: a fourth optional parameter
  defaulting to the key itself, so only `doFish()` names an outcome
  (`bite`/`miss`) and the three single-outcome actions pass nothing extra.
- **`numberWord()` placement**: UTILITIES, beside `fmtDuration()`.
- **When a tally run starts tallying**: from the first occurrence, so the
  transition at n = 2 is a re-render rather than a reconstruction.

**Notes / assumptions**

- The two battery-servicing removals ("You pull the batteries out of the …",
  "You put fresh batteries in the …") are an **explicit extension of #21's
  original table by two call sites**, made because they fail the same test and
  leaving them would have made the battery controls inconsistent — silent when
  toggled, chatty when serviced.
- Collapse state lives on the `<p>` element: `dataset.logKey` for matching and
  a `_logTally` expando for the counts, since `dataset` values are strings.
  Nothing about the log is in `state`, so nothing about it is serialized.
- `doConsume()`'s key is `"consume:" + (it.itemId || it.name)`. The handoff
  specified `it.itemId`; the name fallback is a guard for the runtime-literal
  items the remaining `giveItem()` call sites still build (the `tier-0`
  registry cleanup), which would otherwise all key as `consume:undefined` and
  collapse different foods into one line.
- The summary wording is the handoff's, including "You fish two times." for a
  run of exactly two — retunable prose, not a settled style rule.

**Explicitly NOT changed**

- `#log`'s 110px cap, its 50-entry trim, its gap and its line styles.
- `serializeGame()`, `applyLoadedData()`, `doRestart()`'s `innerHTML = ""`.
  `SAVE_KEY` is unchanged: `versionCompat()` reads `MAJOR.MINOR`, and this
  pass adds no state.
- Illness, vitals, `doConsume()`'s mechanics — only its `log()` call's key.
- `doSearch()`, `doSleep()`, `doLightStove()`, `doBuildFire()`,
  `doExtinguish()`, `doDismantleCampfire()`, the door/window lines, the save
  and load `sys` lines, and every `warn` in the file: all unkeyed, all
  unchanged.
- No vitals readout was added outside the ☰ menu, per the handoff.

**Validation performed**

Driven in headless Chromium against an instrumented copy, with `Math.random`
scripted where an outcome had to be forced:

- Seven fishing attempts, three bites: one line, "You fish seven times. Three
  bites." Two attempts with one bite: "You fish two times. One bite." Three
  attempts, no bites: "You fish three times. Nothing bites." A single attempt
  keeps its ordinary sentence with no summary.
- A fishing run broken by an intervening `warn` produces two fish lines with
  the warning between them, not a run of two.
- Rest ×3 → "You rest for three hours."; ×12 → "You rest for 12 hours."
  (digits above ten). Fuel ×3 → "You feed three more pieces of wood into the
  fire." Chop ×3 across three different rooms → "You chop down three trees.",
  confirming a run spans movement.
- Eating the same item three times then a different one: two lines, "You eat
  the canned soup. ×3" and "You eat the granola bars." Alternating two items
  four times: four separate lines, never collapsed. Three raw fish where the
  second triggers the illness warning: "×2", the warning, then a fresh line.
- Crafting the same recipe twice: one line with "×2".
- Equipping, unequipping, storing and taking, all four verified to have
  actually moved the item: **zero** log lines. The following "That won't fit
  there." warning still appears. Battery on/off, removal and replacement write
  nothing.
- `.fresh` lands on the rewritten line when the collapsing call is unclassed,
  and exactly one line carries it.
- The cap holds: 60 filler lines plus a collapsed rest run leaves exactly 50
  children with the summary last.
- `node --check` on the extracted script; no page or console errors in any
  scenario.
- Re-ran v0.4.4's and v0.4.5's own validations against this build: 672/102
  exit split intact with all 224 head/block pairs ordered, 42 rooms hiding
  Move, and the Wide map still exactly player-centred with label counts
  matching their tiers.

**Explicitly out of scope**

Per the handoff: no resizing or restyling of `#log`, no vitals readout outside
the ☰ menu, no change to illness or vitals, no summarising across
non-consecutive occurrences (rejected during planning — it deletes the events
between survivors and implies an order that didn't happen), and no collapsing
of `warn` lines. #23 (illness system) is the recorded home of the
hidden-vitals finding and is untouched.

**Documentation**

- The ARCHITECTURE comment's "Current version" line is bumped to 0.4.6.
- Filed #29: re-judge `#log`'s 110px cap and 50-entry limit against the
  quieter feed. The handoff deferred this explicitly on the grounds that it
  has to be judged in play rather than guessed at; the issue records the
  current values and says so.
- Nothing else was deferred out of this pass.

**Version**: `GAME_CONFIG.VERSION` `"0.4.5"` → `"0.4.6"` (third of three
passes in this pull request: `"0.4.3"` → `"0.4.4"` → `"0.4.5"` → `"0.4.6"`)

---

## v0.4.5 — Wide map: panning, zoom placeholders, viewport-relative labels

Implements: handoffs/wide-map-panning.md

Implements #19 and #20 in full, per `handoffs/wide-map-panning.md`. The Wide
map now centres on the player and slides as they move; street names are placed
against the part of each street on screen; two inert `+` / `−` buttons reserve
the layout slot for a later zoom pass. Rendering-only, MAP sub-block. No
mechanics, no world data, no new state fields, no save-format change.

**Changed / Reworked** — RENDERING / MAP, Wide is a span, not a box

- `MAP_WIDE_VIEWBOX = { x:20, y:20, w:1000, h:1000 }` is replaced by
  `MAP_WIDE_VIEW = 800`, a span mirroring `MAP_CLOSE_VIEW = 260`.
  `mapTargetViewBox()` collapses to one code path for both modes: a
  player-centred box of the active span. Wide never panned before because its
  target was a constant; nothing in `renderMap()` or `mapUpdateViewBox()`
  needed changing to make it pan, and the existing 350ms ease-out animation
  now runs for Wide moves too.
- The span had to shrink for panning to mean anything. Node extents run 55 →
  965 on both axes — 910 units — so a 1000-unit box has almost nothing to pan
  within. At span 800 the box ranges over x ∈ [−345, 565] as the player
  crosses town, which is the full width of the grid.
- The box is **not clamped** to content bounds. At the western edge a
  player-centred Wide box is 47% empty canvas; Close at the same spot is
  already 40% empty. Clamping was rejected: the ask was for Wide to pan the
  way Close does, and clamping would also stop Wide panning at all for any
  span ≥ 960.
- The player marker is untouched: `r="5"` in Close, `MAP_PLAYER_R_WIDE = 12`
  in Wide.

**Changed / Reworked** — RENDERING / MAP, street names placed against the viewport

- `mapBlockLabels()` is gone. It emitted one `<text>` per block at build time
  — 7 blocks × 16 streets = 112 labels — which stops meaning anything once the
  view moves.
- `renderMapWide()` now emits a fixed pool of `MAP_LABELS_PER_STREET` (3)
  empty, hidden `<text class="map-street-name" data-street="N">` nodes per
  street: 48 in total, created once per Wide render and thereafter only moved,
  shown or hidden. Nothing is created or destroyed during a pan.
- `mapBindStreetLabels()` caches that pool as element references, plus each
  street's endpoints and heading angle, in the module-level `mapStreetLabels`.
  It runs from `renderMap()` right after the SVG content is rebuilt, and
  clears the pool for Close, which emits no street names at all.
- `mapPositionStreetLabels(box)` places them. Every street run is
  axis-aligned, so visibility is a 1-D clamp: a horizontal street is on screen
  only if its single `y` lies inside the box, and its visible stretch is
  `[max(min(ax,bx), box.x), min(max(ax,bx), box.x + box.w)]`; vertical streets
  are the same with the axes swapped. Label count follows `MAP_LABEL_TIERS` on
  that stretch's length — 3 at ≥ 600, 2 at ≥ 300, 1 at ≥ 110, none below —
  positioned at `lo + MAP_LABEL_INSET`, the midpoint, and `hi −
  MAP_LABEL_INSET` (one label sits at the midpoint alone). Unused pool nodes
  get `display:none`.
- Rotation and offset are v0.4.3's logic unchanged: the label rides its
  street's heading folded into `(-90, 90]`, so vertical streets still read
  bottom-to-top, offset off the line by `MAP_LABEL_OFFSET = 5`. This pass
  changes where labels sit, never which way they read.
- Labels are repositioned wherever the viewBox is set — the snap branch of
  `mapUpdateViewBox()` and every `requestAnimationFrame` step — since the
  placement is relative to the window, not to the street.

**UI**

- Wide shows about 80% of the town at a time, centred on the player, sliding
  as they move, instead of the whole town fixed in place.
- On-screen street names drop from 112 to at most 42, averaging 26.7 across
  all 176 street positions.
- Two greyed-out `+` / `−` buttons sit to the right of Wide, in that order,
  using `&minus;` so they read as a matched pair. They are `disabled`, carry no
  handler, and deliberately carry **no `data-zoom` attribute** — the mode
  toggle binds `#mapZoomToggle button[data-zoom]`, and giving the placeholders
  that attribute would have broken the Close/Wide switch. They get the
  existing disabled treatment, `#mapZoomToggle button:disabled{ opacity:.4;
  cursor:not-allowed; }`, matching `#gaitBar`.
- Near the town's edges Wide shows empty canvas past the player, as Close
  already does.

**Removed**

- `mapBlockLabels()` and `MAP_WIDE_VIEWBOX`. Replaced by the label pool and
  `MAP_WIDE_VIEW` respectively.

**Sections touched**

UI/RENDERING, the MAP sub-block only — `mapTargetViewBox()`,
`mapUpdateViewBox()`, `renderMapWide()`, `renderMap()`, the new
`mapBindStreetLabels()` / `mapPositionStreetLabels()` / `mapLabelPositions()`,
the `#mapZoomToggle` markup, and one rule in the document `<style>` block.

**Open questions / decisions resolved**

The handoff left four implementation calls open; all four took its recommended
default.

- **Per-frame vs. on-settle label repositioning**: per frame, inside
  `step()`. At most 48 nodes exist and only `transform` and `display` change,
  so no element is created or destroyed mid-animation. Verified mid-pan:
  labels track the intermediate box, not the target.
- **Where the pool lives**: a module-level array of element references,
  `mapStreetLabels`, populated once per rebuild — the DOM is not re-queried
  per frame. Mirrors how `mapPositionPlayer()` resolves `#mapPlayer`.
- **Button order and glyphs**: `+` then `−`, using `&minus;`.
- **Four named constants or one table**: one table, `MAP_LABEL_TIERS`, read by
  `mapLabelPositions()` via a `find()` on the longest matching tier. No inline
  magic numbers.

**Notes / assumptions**

- `MAP_WIDE_VIEW = 800`, `MAP_LABEL_INSET = 55`, and all three
  `MAP_LABEL_TIERS` thresholds (600 / 300 / 110) are **retunable** and have no
  prior convention behind them. 800 is the smallest span that both zooms in
  noticeably and leaves room to pan; 55 is half the widest street name
  (`POPLAR ST`, 99.1 units at 15px), which is what keeps a full-width label
  inside the visible span instead of clipped at its edge.
- The 1-label tier is currently unreachable: sweeping all 176 street nodes at
  span 800 produced only 0-, 2- and 3-label streets. It is kept because the
  spans a working zoom introduces (#27) will reach it.
- Zoom mode stays a module-level `let`, not a field on `state`, so
  `versionCompat()` still yields `"0.4"` and `SAVE_KEY` is unchanged.
  Persisting a zoom level would have made this MINOR.

**Explicitly NOT changed**

- Close view: `renderMapClose()` is untouched, its span stays 260, its marker
  stays `r="5"`, and it still emits zero `text.map-street-name` nodes.
  Re-checked after a Wide round trip.
- `LOCATIONS`, `MAP_STREETS`, `MAP_BUILDINGS`, `MAP_STREET_NODE_IDS`,
  `MAP_SPACING`, `MAP_MARGIN`, `mapToSvg()`, `mapPathD()`,
  `mapPositionPlayer()` — no node moves.
- The viewBox is not clamped in either mode; Close's own edge behavior is
  unchanged.
- `serializeGame()`, `SAVE_KEY`, and every balance constant outside the MAP
  sub-block.

**Validation performed**

Driven in headless Chromium against an instrumented copy of the new file:

- The Wide viewBox is exactly player-centred at every one of 14 sampled
  positions across two full-width walks (POPLAR ST west → east, 1ST ST south →
  north, plus the four grid corners): `box.x === px − 400` and
  `box.y === py − 400` with no exception.
- Sampled mid-animation as well as settled: the box is intermediate and the
  labels are placed against that intermediate box, confirming per-frame
  repositioning.
- Swept **all 176 street/mid-block nodes**. At every position, each street's
  label count matches `MAP_LABEL_TIERS` applied to its own visible stretch
  (992 two-label streets, 904 three-label, 920 with none, zero mismatches); no
  label falls outside its street's visible span; and no label — measured with
  its real rendered width — is clipped at a span edge. Peak 42 labels on
  screen, mean 26.7.
- Close view after load and after a Wide round trip: `viewBox` back to the
  260-span player-centred box, player `r="5"`, 11 building dots, 19 building
  labels, 176 node dots, 0 street-name nodes, empty label pool.
- The `+` / `−` buttons are present, `disabled`, rendered at `opacity:.4` with
  `cursor:not-allowed`; clicking both changes neither the zoom mode, the
  active-button class, nor the viewBox.
- No page or console errors on load, on toggling modes, or across the walks.
- `node --check` on the extracted script; `git diff main -- ashfall.html`
  confirms the MAP sub-block, the markup and the one CSS rule are all that
  moved.
- One property the handoff asked for did **not** hold: labels can collide at
  an intersection. 116 of the 176 positions show at least one overlapping
  pair, worst case `ELM ST` over `3RD ST` at 17 × 17 units. It is inherent to
  the placement rule as specced — an inset position often lands near a
  crossing, where two 15-unit-tall name bands can cross — so this pass shipped
  the rule as written and filed #28 rather than inventing a placement rule the
  handoff didn't specify.

**Explicitly out of scope**

Per the handoff: no working zoom (the buttons ship inert), no persisted zoom
level, no viewBox clamping, no change to Close view or to any map geometry
constant. Close-map building-label clipping and phone-viewport overflow (both
findings under #16) live in nearby code and are untouched; #16 stays open.
Building placement in the outer ring (#8) is unrelated.

**Documentation**

- The ARCHITECTURE comment's "Current version" line is bumped to 0.4.5.
- Filed #27: make the `+` / `−` controls work, carrying the handoff's
  recommendation that the zoom variable be scoped per mode so Close and Wide
  each scale from their own base span, plus the note that
  `MAP_LABEL_TIERS` needs re-checking at any new span.
- Filed #28: Wide-map street names can collide at an intersection, with the
  measured sweep above and three candidate fixes.

**Version**: `GAME_CONFIG.VERSION` `"0.4.4"` → `"0.4.5"`

---

## v0.4.4 — Exit split: grid travel vs. Here

Implements: handoffs/exit-move-split.md

Implements #18 in full, per `handoffs/exit-move-split.md`. Rendering-only:
the Move panel now holds street travel alone, ordered by compass, and every
other exit renders at the top of Here. No WORLD DATA, no PLAYER STATE, no
mechanics, no save-format change.

**Changed / Reworked** — UI/RENDERING, exit panels

Every exit used to render as a Move button in `exits`-array authoring order,
so "Climb the stairs", "Enter the pharmacy" and "Climb through the window" all
sat under a heading that means travel, and a street's four directions came out
in whatever order the world data happened to list them.

- New `isGridTravel(fromId, toId)` in WORLD INTERACTION, beside
  `getExitsForRoom()`: an exit is grid travel if and only if both endpoints are
  street/mid-block nodes, which the ROOM SCHEMA marks by giving such a room its
  own id as its `locationId`. This is deliberately *not* the cross-Location
  test (`fromRoom.locationId !== toRoom.locationId`), which sends 706 of the
  world's 774 exits to Move — 34 too many, among them the stairwells, the
  apartment-over-shop doors, the `balcony → alley` fire escape and every
  "Enter the …" building door.
- `renderMoveActionsPanel()` filters `getExitsForRoom()` to grid travel and
  sorts it by `MOVE_DIRECTION_RANK` — `north:0, east:1, west:2, south:3` —
  keyed on `computeDirection()` of the two rooms' `locationId`s. No label
  parsing and no new exit field: `computeDirection()` already reproduces the
  compass word in every grid exit's own label.
- The sort has no secondary key on purpose. `Array.prototype.sort` is stable,
  which is what keeps each intersection's "Head …" exit ahead of its
  "Step into the block …" exit — the relationship is authoring order, not
  something re-derived from label text.
- `renderHereActionsPanel()` renders the non-grid exits first, above the
  locked-door notices, in unmodified authoring order, with their existing
  `fmtDuration(exitMinutes(exit))` cost suffix and `actionButton` styling.
  Window-climb exits are among them: `getExitsForRoom()` still generates them
  and they still track window state; only their parent panel changed.
- `getExitsForRoom()` is untouched — same signature, same one list, same
  window handling. Each panel filters it.

**UI**

- Indoors the Move group disappears entirely: the static markup's Move
  `.actions-group` gained `id="moveGroup"`, and the panel hides it when it
  holds no buttons, mirroring `hereGroup`. 42 of the game's 218 rooms are
  non-street rooms, so an empty "MOVE" heading was the common case indoors.
- The game-over branch of `render()` returns before
  `renderMoveActionsPanel()` runs and puts its "Restart" button in
  `moveActions`, so it now sets `moveGroup` back to visible — otherwise dying
  indoors would have left Restart behind a hidden group.
- On a street, Move holds only travel, ordered North, East, West, South.
  Nine street rooms with building entrances gain a Here section; the other
  167 still show none.
- No button label, cost, or styling changed.

**Sections touched**

- UI/RENDERING — `renderMoveActionsPanel()`, `renderHereActionsPanel()`,
  `render()`'s game-over branch, and the static Move `.actions-group` markup.
- WORLD INTERACTION — one added helper, `isGridTravel()`.

**Open questions / decisions resolved**

The handoff left three narrow implementation calls open; all three took its
recommended default.

- **Where the classification helper lives**: WORLD INTERACTION, beside
  `getExitsForRoom()`, which already owns "which exits does this room offer".
  It reads WORLD DATA and is consumed by RENDERING, so RENDERING was the other
  candidate.
- **One list or two**: one. `getExitsForRoom()` keeps its signature and each
  render function filters, which keeps window-exit generation in a single
  place and makes the change provably additive.
- **A visual separator for the relocated exits in Here**: none. They are
  ordinary action buttons and the panel already mixes kinds. If they read as
  crowded in play, that is a follow-up.

**Notes / assumptions**

- The compass order North/East/West/South comes from the handoff, not from a
  prior convention in the code — it is the retunable part of this pass.
- An unknown direction ranks 4, after `south`, rather than resolving to
  `undefined` and poisoning the comparator. No street node can currently
  produce `up`/`down` (every one is `z:0`), but the sort no longer depends on
  that staying true.

**Explicitly NOT changed**

- No `exits` array is reordered, renamed, or given a new field; no exit label,
  `distanceM`, or duration changed.
- `getExitsForRoom()`'s body, `doMove()`, `exitMinutes()` and
  `computeDirection()` are untouched.
- The Here panel's existing actions (locked doors, Rest, Sleep, Search,
  windows, vehicle, fishing, stove, fire, tree, container locks) keep their
  order; the relocated exits are inserted ahead of them.
- `SAVE_KEY` is unchanged — `versionCompat()` reads `MAJOR.MINOR`, so a PATCH
  bump keeps existing browser saves loading.

**Validation performed**

Driven in headless Chromium against an instrumented copy of the new file,
walking all 218 rooms and all 774 exits:

- The split classifies 672 exits as grid travel and 102 as everything else,
  matching the handoff's verified counts exactly. 176 rooms satisfy
  `locationId === id`.
- Every street room's Move buttons match the expected filtered-and-sorted
  list, label for label; direction ranks are monotonic in all 176 street
  rooms; the compass word in every grid label agrees with the computed
  direction. Move-button counts per street room: 2 buttons in 112 rooms, 4 in
  4, 6 in 24, 8 in 36.
- All 224 two-exit direction buckets render "Head …"/"Continue …" before
  "Step into the block …", with no secondary sort key.
- All 42 non-street rooms hide the Move group; no street room hides it.
- In the nine street rooms with non-grid exits, the relocated exits render
  first in Here and in authoring order.
- Both windows, driven through `closed` and `open` in both of their rooms:
  the climb exit appears in Here and never in Move when open, and is absent
  from both when closed.
- No page errors or console errors during the walk.
- The diff is the proof of the data claim: `git diff main -- ashfall.html`
  (equivalently `git diff v0.4.3:ashfall_0_4_3.html`, since the release tags
  predate the filename-normalization pass) touches only the five sites listed
  under **Sections touched** and the version constants.

**Explicitly out of scope**

Per the handoff: no reordering of the Here panel's existing actions, no
compass-rose or spatial button layout (a rose degrades badly in the many rooms
with no directional exits), no change to `exits` data or labels, no renaming
of the "Move" and "Here" headings. #4 (vestigial `distanceM` on cross-Location
exits) is adjacent but not a prerequisite. Phone-viewport layout (#16) and map
rendering (#19, #20) are untouched.

**Documentation**

- The ARCHITECTURE comment's "Current version" line is bumped to 0.4.4.
- Filed #26: the `git diff vX.Y.Z -- ashfall.html` recipe in the Project Guide
  and the changelog guide no longer resolves, because every existing release
  tag predates the rename to `ashfall.html` and carries a versioned filename
  instead.
- Nothing else was deferred out of this pass.

**Version**: `GAME_CONFIG.VERSION` `"0.4.3"` → `"0.4.4"`

---

## v0.4.3 — Wide-view map readability

No handoff file — a direct request to make the side-menu map's Wide view
legible. Scoped to the MAP sub-block of RENDERING plus the document
`<style>` block. No mechanics, no world data, no new state fields, no
save-format change.

**Changed** — RENDERING / MAP, one street name per block

Wide view drew each street as a single continuous `<textPath>` carrying
`mapRepeatedLabel()`'s three copies of the name spaced by bullets, so a
street read `1ST ST • 1ST ST • 1ST ST` with the copies falling wherever
the path put them rather than on anything meaningful.

- `mapRepeatedLabel()` is gone, replaced by `mapBlockLabels(name, chain)`.
  Every chain in `MAP_STREETS` alternates intersection, mid-block,
  intersection, so its even indices are the intersections; the function
  walks them in steps of two and emits one `<text>` per block, centred
  between the two intersections that bound it. That is exactly one name
  per block, each one centred on its own block.
- Each label is rotated onto its block's heading, folded into `(-90, 90]`
  so vertical streets read bottom-to-top instead of upside down, and
  offset off the line by `MAP_LABEL_OFFSET` (5 units) so the name sits
  beside the street rather than on it.
- `renderMapWide()` no longer emits the `<defs>` block of
  `mapstreetpath-N` paths, since nothing references them now; it draws
  every street line first and every label after, so no run is painted
  over its own names.
- Labels are `<text transform="translate(...) rotate(...)">` rather than
  `<textPath>`. The grid is axis-aligned, so a block's heading is always
  0 or ±90 and the flat transform is enough — no path-following needed.

**Changed** — RENDERING / MAP, player marker

- New `MAP_PLAYER_R_WIDE` (12), used for `#mapPlayer` in
  `renderMapWide()` only. Wide's viewBox is 1000 units against Close's
  `MAP_CLOSE_VIEW` of 260, so the shared radius of 5 rendered at roughly
  4px across and read as another node dot. `renderMapClose()` still
  emits `r="5"`.

**UI**

- `#sideMenu` width 360px → 460px, with `max-width:92vw` added so the
  panel still fits a phone-width viewport. Wide's viewBox is fixed, so
  the whole map scales up with the panel.
- `.map-street-name` font-size 11px → 15px, letter-spacing 2px → .5px.
  The looser tracking was there to stretch names along a whole street
  run; with one name per block the size is what matters and the tracking
  only costs width.

**Explicitly NOT changed**

- Close view: `renderMapClose()` is untouched — same street paths, node
  dots, building dots and labels, same `r="5"` player marker.
- `LOCATIONS`, `MAP_STREETS`, `MAP_SPACING`, `MAP_MARGIN`,
  `MAP_WIDE_VIEWBOX`, `mapToSvg()` and `mapPathD()` — the grid geometry
  and every street run are identical, so no node moved.
- `mapPositionPlayer()`, `mapTargetViewBox()`, `mapUpdateViewBox()` and
  `renderMap()` — marker tracking and the Close-view viewBox animation
  are unchanged.
- Movement, exits, compass wording, world data and the save format.
  `versionCompat()` truncates to `"0.4"`, so `SAVE_KEY` is unchanged and
  a v0.4.0–v0.4.2 save still loads with no version warning.

**Validation performed**

Driven in headless Chromium against the real file, Wide view open:

- 112 labels rendered — 16 streets × 7 blocks — one per block, with each
  of the 16 names appearing exactly 7 times.
- Widest label (`POPLAR ST`) measures 99.1 units against a block length
  of 130 (`MAP_SPACING`), and no label exceeds its block, so nothing
  overflows into a neighbouring block or an intersection.
- No page or console errors on load, on the Close↔Wide toggle, or while
  moving.
- Close view re-checked after the change: player `r="5"`, 11 building
  dots, and zero `text.map-street-name` nodes, matching v0.4.2.
- Player marker in Wide: `r="12"`, 10.2px across on screen against ~4px
  before, and it tracks movement — walking Poplar St west from between
  1st & 2nd stepped the marker 380 → 315 → 185 → 55 in SVG units, with
  the viewBox correctly staying fixed at `20 20 1000 1000`.
- Panel measured at 460px with the map SVG at 423px.

**Notes / assumptions**

- The 460px panel width, 15px type, `MAP_PLAYER_R_WIDE` of 12 and the
  5-unit `MAP_LABEL_OFFSET` are tuned by eye against the current 130-unit
  block, with no prior convention behind them — all four are retunable.
- 15px leaves 31 units of slack on the longest street name. A future
  street name longer than about 11 characters, or a smaller
  `MAP_SPACING`, would need the size dropped or the name abbreviated;
  nothing in the code enforces the fit.

**Version**: `GAME_CONFIG.VERSION` `"0.4.2"` → `"0.4.3"`

---

## v0.4.2 — Missing Item Category Population

Implements the "Ashfall Handoff — Missing Item Category Population"
handoff in full. Continuation of the v0.4.0 `SPAWN_POOLS`/`ITEM_REGISTRY`
work, closing the category gaps a post-v0.4.0 audit found. Content pass
(WORLD DATA) plus the small RENDERING generalization the new equippable
bags needed — no new mechanics, no new state fields, no save-format
change.

**New content** — WORLD DATA, `ITEM_REGISTRY`

36 new entries, 119 → 155. Weights are estimates consistent with existing
entries for similar real-world items; retunable.

- **Pet supplies** (none existed): `dry_pet_food`, `canned_pet_food`,
  `pet_leash`, `pet_collar`, `pet_toy`, `cat_litter`, `pet_carrier`.
- **Baby/child** (2 existed): `diapers`, `baby_formula`, `pacifier`,
  `childrens_book`, `toy_action_figure`, `baby_blanket`. `baby_formula`
  deliberately carries no `restores` — it is flavor, not player food.
- **Self-defense** (police-only items existed): `baseball_bat` and
  `riot_baton` (`blunt`), `combat_knife` (`blade`), `pepper_spray`,
  `stun_gun`.
- **Cleaning supplies**: `dish_soap`, `laundry_detergent`,
  `rubber_gloves`, `trash_bags`.
- **Documents/lore**: `dated_newspaper`, `personal_journal`,
  `unsent_letter`, `utility_bill`, `missing_person_flyer` — generic item
  types only, per Design decision 2.
- **Electronics**: `walkie_talkie` (`battery`), `dead_cellphone`,
  `disposable_camera`.
- **Money/valuables**: `gift_card`, `checkbook`.
- **Equippable bags**, `category:"Container"`, following `worn_backpack`
  exactly: `duffel_bag` (`duffel`, 18 kg), `tote_bag` (`tote`, 8 kg),
  `purse` (`purse`, 5 kg), `fanny_pack` (`fannypack`, 3 kg).

**New content** — WORLD DATA, `SPAWN_POOLS`

- 5 new pools, 23 → 28: `pet_supplies` (`rollCount:[1,2]`,
  `emptyChance:0.2`), `baby_items` (`[0,2]`, `0.3`), `self_defense`
  (`[0,1]`, `0.35`), `cleaning_supplies` (`[1,2]`, `0.15`) and
  `electronics` (`[0,1]`, `0.3`). Roll counts and empty chances are the
  handoff's; per-entry weights follow the existing convention (commoner
  items 5-8, rarer or bulkier ones 1-3) and are flagged retunable in the
  code comment.
- 6 existing pools extended: `hygiene` (+ the four cleaning items, at
  lower weights than its bathroom staples), `valuables` (+ `gift_card`,
  `checkbook`), `police_gear` (+ `riot_baton`), `office_supplies` and
  `residential_personal` (+ the electronics), and `documents_lore` (+ the
  five document types).
- `spawnPools` added on **20 existing containers**, alongside their
  current pools rather than replacing them: `pet_supplies` on four
  residential closets/dressers, `baby_items` on two bedroom containers,
  `self_defense` on the two nightstands, one Oak dresser and the hardware
  store's Tool Wall, `cleaning_supplies` on both under-sink cabinets, the
  superintendent's tool cabinet and closet and the corner store's back
  room, and `electronics` on the five `office_supplies` containers and
  both nightstands. Each new pool lands on at least one container that
  still has its roll pending, so every one of them can actually appear in
  play rather than only mattering to a future respawn cycle.
- 4 hand-placed (not pool-rolled) bags, one per building, following the
  `worn_backpack` precedent: `duffel_bag` in Acorn 2B's closet, `purse`
  in Acorn 1A's open suitcase, `tote_bag` in the flat above the corner
  store, `fanny_pack` in the flat above the hardware store. All four
  containers already carried authored contents and `spawnRolled:true`, so
  placing a bag there costs no container its spawn roll.

**Changed** — RENDERING and PLAYER STATE, slot generalization

The equip mechanism was already generic (`state[it.slotType]`), but four
places named `"keychain"`/`"backpack"` by hand, so a new `slotType` would
have silently had no tab and no Unequip button. Design decision 3 resolved
to option **(b)**, the fuller generalization, so the next bag type needs
no RENDERING edit at all:

- New `CONTAINER_SLOTS` and `SLOT_LABELS` (WORLD DATA, beside
  `itemsFromRegistry`), derived from `ITEM_REGISTRY` rather than listed.
  `keychain` is named explicitly in both, since it is the one slot that
  isn't a found item.
- New optional `slotLabel` registry property for slots whose key doesn't
  capitalize into a good tab name — `"Fanny Pack"`, `"Duffel Bag"`,
  `"Tote Bag"`. `worn_backpack` needs none, so its tab still reads
  "Backpack" exactly as before.
- `invTabDefs` and the unequip-button condition (`renderInventoryPanel`),
  `invSlot()` and `invPools()` now all read `CONTAINER_SLOTS` instead of
  naming slots. Tab order is unchanged for existing saves: Inventory,
  Keychain, Backpack, then any new bag in registry order.
- `makeDefaultState()` derives its empty slots from `CONTAINER_SLOTS`
  instead of the literal `backpack:null`, so a new bag type needs no edit
  there either.
- `keychainAllows()` is untouched and still restricts the keychain to
  `Key` items. That restriction is deliberately not inherited by the new
  bag slots.

**UI**

- Equipping a duffel bag, purse, fanny pack or tote bag adds an inventory
  tab named for it, with a working Unequip button, matching the existing
  Backpack tab's behavior exactly.

**Explicitly out of scope** (per the handoff)

- **Firearms and any combat/ammo mechanics** — Design decision 1,
  resolved to the recommended default of excluding them entirely. A
  working firearm needs ammo tracking, reload and a combat system that
  doesn't exist; inert loot would mislead the player. Deferred to roadmap
  item 6 (Zombies/Threats) so the item and its mechanics ship together.
  `stun_gun` and `pepper_spray` are in, being non-firearm deterrents with
  no ammo model implied.
- **Deep, personalized lore content** for the new document items —
  Design decision 2, resolved to the recommended default. The item
  *types* ship with plain generic names; writing dated, location-specific
  content for them is roadmap item 13's job and this pass does not
  fulfill it.
- Container property tags, the no-respawn flag and fauna (roadmap item
  15); new buildings to house these categories properly — a pet store,
  nursery or sporting-goods store (roadmap item 14's remaining half);
  map expansion, which shipped separately in v0.4.1.

**Validation performed**

Audited with a harness that evaluates the real `<script>` body under a
DOM stub and drives the assembled game, plus a real-browser check:

- All 36 new items resolve with the exact category and weight the handoff
  specced, checked entry by entry against a transcription of its tables.
  `baby_formula` confirmed to carry no `restores`.
- No firearm- or ammunition-shaped id exists in `ITEM_REGISTRY`.
- `CONTAINER_SLOTS` covers every `slotType` in the registry; every slot
  resolves a label; the Backpack tab label and the tab ordering are
  unchanged from v0.4.1.
- Equip → stash an item → unequip round-trips for all five equippable
  bags: the slot populates, `invSlot()` resolves it with the right
  capacity, its contents appear in `invPools()`, and the stored contents
  survive being unequipped back into a stowable item.
- `keychainAllows()` still accepts `Key` and rejects everything else.
- Every pool is attached to at least one container, and each of the five
  new pools reaches at least one container whose roll is still pending.
- 120,000 weighted rolls across all 28 pools — every result resolves to a
  real registry item with qty ≥ 1, and every entry has a positive weight
  and `qtyMin <= qtyMax`.
- All four new bag types confirmed findable in the default world, each in
  a `spawnRolled` container so no container lost its pool roll. (This
  check first ran too loosely — it counted the pre-existing
  `worn_backpack` toward the total and so passed while `fanny_pack` had
  silently failed to place. Tightened to exclude `worn_backpack` and to
  assert each of the four bag ids individually, which caught it.)
- A v0.4.1-shaped save, with none of the new slot keys, still loads and
  picks up every slot from `makeDefaultState()`.
- The v0.4.1 world audit re-run unchanged: 218 rooms, 774 exits, exit
  reciprocity, grid adjacency, compass wording, map coverage and
  reachability all still pass.
- Loaded in a real browser: the game boots at v0.4.2 and renders, and
  with all four bags equipped the panel shows Inventory / Keychain /
  Duffel Bag / Purse / Fanny Pack / Tote Bag with Unequip on the active
  slot.
- Diffed against `ashfall_0_4_1.html`: every removed line is an intended
  edit (version strings, the registry/pool lines being extended, the 20
  container lines gaining pools, the 4 gaining a bag, and the slot
  generalization). No room, container, item or exit was removed.

**Notes / assumptions**

- Per-entry spawn weights for the five new pools, and for the additions
  to the six existing ones, had no prior convention beyond "commoner
  higher, rarer lower" — retunable, not designed.
- **Category mismatch worth a look:** `dish_soap`, `laundry_detergent`,
  `rubber_gloves` and `trash_bags` are `Misc`, exactly as the handoff
  specifies, but their closest existing siblings (`bar_soap`, `bleach`,
  `toilet_paper`) are `Materials`. `Materials` is in `STACKABLE` and
  `Misc` is not, so as shipped these four do not stack while the older
  cleaning items do. Implemented as specced rather than silently
  deviating; it's a one-word change per entry if the stacking behavior is
  wanted.
- Which specific containers got which pool is this session's call within
  the handoff's stated pattern — in particular, pet supplies are on some
  residential units and not others, and baby items on only two, so not
  every apartment reads as having had a pet or a baby.
- `combat_knife`'s `blade` tag is currently decorative: no mechanic reads
  `blade` yet (`blunt` breaks cars and windows, `cutting` cuts locks,
  `chopping` fells trees). It is tagged for consistency with
  `kitchen_knife` and `box_cutter`, not because it does anything new.
- `baseball_bat` and `riot_baton` carry `blunt`, so they are immediately
  usable for forcing car doors and breaking windows. That is a real
  increase in how many tools can do those jobs, and worth a look if
  forced entry starts feeling too easy.
- The handoff listed four existing pools to extend; six were extended.
  `documents_lore` and `residential_personal` are the extra two, both
  named in the handoff's own per-category text (the document types and
  "extend `office_supplies`/`residential_personal`" for electronics) but
  omitted from its summary list.

**Version**: `GAME_CONFIG.VERSION` `"0.4.1"` → `"0.4.2"`

---

## v0.4.1 — Map Expansion to 8×8 Street Grid

Implements the "Ashfall Handoff — Map Expansion to 8×8 Grid" handoff for
its street-grid component. Fulfills roadmap Tier 1 item 14 (Expand the
Map) **in part only** — the building-placement half of that item is
untouched by this pass and item 14 stays open. Content pass: WORLD DATA
additions plus the mechanical `MAP` updates the larger grid required. No
new mechanics, no new state fields, no save-format change.

**Open questions resolved** (the handoff shipped with three unresolved;
Tom answered all three before this session)

- **Street names/direction.** Cedar, Elm, Mill and Dock confirmed, but all
  four placed **south** of Maple St rather than Mill/Dock north of Water.
  The handoff's table put Mill at y=400 and Dock at y=500, north of Water
  St — which would have put both streets in the river. Water St is the
  riverfront on every existing node (`fishable:true`, "just a drop to the
  mud", `riverbank`'s "Climb down to the riverbank"), so the town grows
  *away* from the water instead: Elm and Cedar continue the residential
  tree-name ring, Mill and Dock are the industrial and rail-freight edge
  beyond it. Water St remains the river / north hard limit and no existing
  description needed rewriting.
- **Numbered-street asymmetry.** Resolved symmetric the other way round:
  8th St dropped, 9th St added east, giving 3 streets west of center
  (6th, 4th, 2nd) and 4 east (3rd, 5th, 7th, 9th).
- **Pass size/phasing.** Built as a single pass, not split.

**New content** — WORLD DATA, `LOCATIONS` and the new `buildOuterStreets()`

- Street grid grown from 5 numbered × 4 named to **8 × 8**. New numbered
  streets (x, west→east): 6th `-100`, [4th `0`, 2nd `100`, 1st `200`,
  3rd `300`, 5th `400`], 7th `500`, 9th `600`. New named streets (y,
  south→north): Dock `-400`, Mill `-300`, Cedar `-200`, Elm `-100`,
  [Maple `0`, Poplar `100`, Main `200`, Water `300`]. Every existing
  coordinate is unchanged — origin stays `maple4th`, and the new grid is
  what introduces negative x and y.
- **125 new rooms**, each with a `LOCATIONS` entry at the same fixed
  100m spacing: 44 intersections (`dock6th` … `water9th`, `building`
  `"<Named> St & <Numbered> St"`, `floorCap:100`), 40 mid-blocks along the
  named streets (`mid_<name>_<lo>_<hi>`) and 41 along the numbered streets
  (`mid_<number>_<a>_<b>`), all `floorCap:20`. Mid-block coordinates are
  the midpoint of their two endpoints; adjacency is spatial order, not
  numeric, exactly as in the original grid. Room total 93 → 218.
- All 125 descriptions hand-written per the Project Guide's tone
  checklist — one to two sentences, matching the existing mid-block and
  intersection density rather than building-interior depth. New areas
  carry their own character: Elm and Cedar are the outer residential
  ring thinning into fields, Mill is the fenced industrial belt, Dock is
  the rail-freight edge where the town stops.
- New nodes ship with empty `containers:[]` — no loot placed in this
  pass. Eight mid-blocks get incidental `floor` items for texture, each
  tied to what the description already shows: `mid_cedar_5_7` (firewood,
  the dumped yard waste), `mid_dock_1_2` (planks, the broken pallet),
  `mid_dock_2_4` (tow chain), `mid_elm_2_4` (stuffed toy), `mid_main_5_7`
  (tire iron, the used-car lot), `mid_mill_7_9` (scrap metal),
  `mid_7th_mp_p` (metal pipe, the collapsed trampoline's leg) and
  `mid_water_7_9` (firewood, driftwood off the bend).
- The three new Water St nodes and their three mid-blocks carry
  `fishable:true`, matching every existing Water St node.
  `mid_elm_1_3`, `mid_maple_7_9` and `mid_9th_c_e` carry `hasTree:true`,
  the only three new descriptions that name a tree.

**Changed** — WORLD DATA, `buildStreetsAndOutdoor()`

- The 11 rooms that were the old grid's outer edge gained 26 exits
  connecting them outward: `maple4th`…`water4th` west toward 6th St,
  `maple5th`…`water5th` east toward 7th St, and all five Maple St nodes
  south toward Elm St (`maple4th` and `maple5th` were corners and gained
  two directions each). Each direction adds the established pair — one
  exit to the next intersection, one "Step into the block" exit to the
  new mid-block between them. All are cross-`Location` exits carrying
  only `{ to, label }`; `exitMinutes()` and `computeDirection()` derive
  travel time and compass wording from coordinates, as since v0.3.0.
- Water St gained no new exits north: it is still the river and the
  town's north hard limit.

**Fixed**

- `poplar2nd` was missing both of its southbound exits. `maple2nd` and
  `mid_2nd_mp_p` each point north to it, but it had no exit back, so
  Poplar & 2nd was a one-way trip from the south — a pre-existing v0.4.0
  content bug, not something this pass introduced (confirmed by running
  the reciprocity audit below against the unmodified v0.4.0 file). Added
  `{ to:"maple2nd" }` and `{ to:"mid_2nd_mp_p" }`, matching the
  intersection pattern every other node follows.

**Function relocation / new function**

- New `buildOuterStreets()` (WORLD DATA), merged in `makeDefaultWorld()`
  directly after `buildStreetsAndOutdoor()`. The handoff left placement
  of the 125 rooms to this session; they went in a sibling function
  rather than into `buildStreetsAndOutdoor()`, which would otherwise have
  roughly tripled in length. The split is along the obvious seam — the
  original 5×4 core versus the outer ring added here — and moved no
  existing line, so it is not roadmap item 9 (a by-town/by-location split
  of the existing function), which stays open and is now more pressing.

**UI** — RENDERING, `MAP` sub-block

- `MAP_STREETS` rebuilt: 16 chains (8 named + 8 numbered) of 15 nodes
  each, replacing the previous 9 chains of 9 and 7. The new nodes are
  inserted at their correct spatial position within each existing chain,
  not appended.
- `MAP_MAX_COL` `4` → `6` and `MAP_WIDE_VIEWBOX` `{20,20,610,480}` →
  `{20,20,1000,1000}`, both scaled from the 5×4 values by the same
  margin/spacing logic. New `MAP_MIN_COL` (`-1`) and `MAP_MIN_ROW` (`-4`)
  constants, because the grid now carries negative coordinates:
  `mapToSvg()` offsets by `MAP_MIN_COL` so column −1 still lands on the
  left margin. `MAP_MAX_ROW` is deliberately unchanged at `3` — Water St
  is still the northernmost row, so the river line and every pre-existing
  node keep their exact old SVG positions.
- The river path in `renderMapClose()`/`renderMapWide()` now spans
  `mapToSvg(MAP_MIN_COL, …)` → `mapToSvg(MAP_MAX_COL, …)` instead of
  starting at column 0, so it runs the full width of the wider grid.
- `MAP_BUILDINGS` untouched — no buildings were placed by this pass.
  Wide view shows the larger grid; Close view is structurally unaffected
  (it already pans per-node) and was spot-checked against the new nodes.

**Documentation**

- `LOCATIONS`' coordinate-convention comment rewritten for the 8×8 grid:
  the new col/row ranges and street orders, why the four new named
  streets sit south of Maple, and that the origin did not move.
- `MAP`'s grid-extents comment updated, including why `MAP_MIN_COL`/
  `MAP_MIN_ROW` exist and why `MAP_MAX_ROW` didn't change.
- ARCHITECTURE comment's "Current version" line bumped.
- Roadmap updated and renamed to `Ashfall_Development_Roadmap_v0.4.1.md`.
  Item 14 kept open with its scope narrowed to the building-placement
  half that this pass did not build. Item 9's room count corrected
  (60 → 185 street/outdoor rooms across two functions) and its "no
  urgency yet" note revised, since this pass is exactly the growth that
  note was waiting on. Nothing was removed.

**Explicitly out of scope** (per the handoff)

- Any new buildings in the new blocks, and any new outdoor set-pieces
  like the Storage Facility or Riverbank. This pass is the street
  skeleton only; what gets placed out there is a separate planning pass
  and the remaining half of roadmap item 14.
- No loot in the new blocks beyond the eight incidental floor items above.
- Splitting `buildStreetsAndOutdoor()` itself (roadmap item 9).
- The missing item-category population pass (separate handoff).
- Container property tags / item respawn (roadmap item 15).

**Validation performed**

Audited with a harness that evaluates the real `<script>` body under a DOM
stub and inspects the assembled `world`, run against both this file and
the unmodified v0.4.0 file for comparison:

- 218/218 rooms resolve a `locationId` in `LOCATIONS`; 774 exits, every
  target resolving to a real room.
- Every street↔street exit is reciprocal (this is the check that caught
  the `poplar2nd` bug, and it fails identically on unmodified v0.4.0).
- Every street exit spans exactly one grid step — 50m to a mid-block or
  100m to the next intersection — so no exit accidentally skips a node.
- Every compass word in every cross-`Location` exit label matches the
  direction `computeDirection()` derives from the coordinates.
- All 176 expected grid nodes present (64 intersections + 56 + 56
  mid-blocks) against an independently enumerated 8×8 grid.
- All 16 `MAP_STREETS` chains are 15 nodes, every id resolving; every
  grid node appears in some chain; all 176 render inside
  `MAP_WIDE_VIEWBOX`.
- Every room reachable from the player's start room by exit-graph search.
- Wide map rendered to SVG and rasterized — 8×8 grid draws correctly with
  the river along Water St at the north edge.
- Diffed against `ashfall_0_4_0.html`: 23 lines removed, all of them the
  intended `MAP`/comment/version edits. No existing room, container, item
  or exit was removed or rewritten — every world-data change is an
  addition.

**Notes / assumptions**

- Street names, the north/south flip, the symmetric numbered-street
  scheme and the one-pass phasing are Tom's answers to the handoff's
  three open questions, not this session's picks.
- Which four new named streets are residential (Elm, Cedar) versus
  industrial (Mill, Dock), and the specific character given to each — the
  mill and its yards, the rail spur and loading docks along Dock St — is
  this session's invention, extrapolated from the existing Riverside
  Freight warehouse and the "INDUSTRIAL-something" sign already on
  Maple St's south side. Retunable; nothing mechanical depends on it.
- The eight incidental floor items, the three `hasTree` nodes and the
  `fishable` flags on the new Water St nodes are judgment calls within the
  handoff's "sprinkle a handful for texture" guidance. Item choices are
  flavor, but `hasTree` feeds `doChopTree` and `fishable` feeds `doFish`,
  so they are live gameplay affordances and worth re-balancing if the
  outer grid ends up too generous a firewood/food source.
- `MAP_MIN_ROW` is defined and documented but not yet read by any code,
  since `MAP_MAX_ROW` alone still anchors the y axis. It is there as the
  matching half of `MAP_MIN_COL` so the extents read as a pair.
- The handoff described the 14 edge rooms as gaining "a new exit" each.
  Following the file's own convention, each new direction gains a *pair*
  (next intersection + mid-block), which is why the count here is 26
  exits across 11 rooms rather than 14.

**Version**: `GAME_CONFIG.VERSION` `"0.4.0"` → `"0.4.1"`

---

## v0.4.0 — Container Spawn Pools & Population System

Implements the "Ashfall Handoff — Container Spawn Pools & Population
System" handoff, item-spawn-pool portion in full (Tier 3 item 15, partial
fulfillment — see Explicitly NOT in this pass below).

**New**

- `SPAWN_POOLS` registry (WORLD DATA, sibling to `ITEM_REGISTRY`) — 23
  weighted loot pools (`kitchen_perishable`, `kitchen_nonperishable`,
  `kitchen_tools`, `hygiene`, `medical_otc`, `medical_pharmacy`,
  `residential_personal`, `clothing`, `documents_lore`, `recreation`,
  `tools_general`, `tools_workshop`, `office_supplies`,
  `retail_stock_food`, `retail_stock_general`, `hardware_store`,
  `outdoor_camping`, `valuables`, `police_evidence`, `police_gear`,
  `warehouse_goods`, `trash`, `fuel_fire`). Each pool entry carries
  `weight`/`qtyMin`/`qtyMax`; each pool has its own `rollCount` range and
  `emptyChance`.
- `doOpenContainer(room, container)` (WORLD INTERACTION) — rolls a
  container's `spawnPools` independently the first time it's opened
  (gated by the new `spawnRolled` container field), then stamps
  `lastRolledMinute`. Wired in by having the container-tab click handler
  in `renderWorldItemsPanel()` (RENDERING) call it instead of setting
  `state.worldTab` directly.
- `weightedPick()` / `randInt()` (CORE UTILITIES) — small RNG helpers
  backing the roll.
- `backfillContainerFields()` (PERSISTENCE), wired into
  `applyLoadedData()` alongside the existing three backfills.
- 37 new `ITEM_REGISTRY` entries (Food, Medical, Clothing, Recreation,
  Tools/Workshop, Retail, Outdoor, and Police categories) needed for pool
  depth — see the handoff's Appendix B for the full list.

**Content**

- `spawnPools` tagging retrofit across all 74 containers (69 existing +
  5 new) per the handoff's Appendix C assignment table — every building:
  Acorn Apartments, Auto Workshop, Main St (Corner Store, Pharmacy,
  Hardware Store, and the apartments above each), Oak Apartments, Police
  Station, Riverside Freight, the Poplar St alley dumpster, and the Water
  St storage units.
- The 19 previously-empty containers (Oak Apartments ×8, Auto Workshop
  ×4, Police Station ×3, Riverside Freight ×4) now populate via their
  assigned pools on first open instead of sitting permanently empty.
- Acorn Apartments 2B parity fix: added Fridge (`kitchen_perishable`),
  Pantry (`kitchen_nonperishable`), and Under-sink cabinet (`hygiene`) to
  `twobee_kitchen`/`twobee_bathroom`, and a Dresser (`clothing`,
  `residential_personal`) to `twobee_bedroom` — 2B was missing fixtures
  its 2A twin has. All four ship empty and roll on first open.
- Superintendent's unit (`onebee`) gets a new Closet (`clothing`), same
  treatment.
- All 50 pre-existing hand-placed containers reviewed against their new
  pool tags and retagged `spawnRolled:true` at authoring time so
  `doOpenContainer()` never overwrites their authored contents; their
  pools exist only so a future respawn cycle (roadmap item 15's
  remaining scope) has something to draw from.

**Content review adjustments** (existing hand-placed contents swapped
for pool consistency, per the Project Guide's "judgment calls get
flagged" principle):

- Acorn Apartments 2B, `twobee_bedroom` nightstand: swapped 2×
  `bandages` for 1× `loose_change`. The nightstand is tagged
  `residential_personal`/`documents_lore`, not a medical pool — a
  medical item sitting there was a category mismatch; `loose_change` is
  a direct `residential_personal` entry.
- Pharmacy `shelves`: swapped `vitamins` for `cold_medicine`. `shelves`
  is tagged `medical_otc` only, but `vitamins` is a `medical_pharmacy`
  pool entry per the handoff's own tables (pharmacy-grade, not OTC);
  `cold_medicine` is a `medical_otc` entry — this is the exact kind of
  swap the handoff's "In scope" item 4 calls for.

**Hardened**

- `backfillContainerFields()` was implemented slightly beyond the
  handoff's literal wording. The handoff describes it as backfilling
  only `spawnRolled`, but a genuinely old (pre-v0.4.0) save's containers
  don't carry a `spawnPools` field at all — so `doOpenContainer()`'s
  `container.spawnPools && !container.spawnRolled` guard could never
  fire for anything loaded from such a save, silently defeating the
  "still-empty containers get a chance to roll on next open" behavior
  the function exists for. Found by simulating `applyLoadedData()`
  against a save stripped of both fields. Fixed by having the backfill
  copy `spawnPools` itself from the default world (mirroring how
  `backfillLocationIds()` already copies a missing `locationId`), then
  `spawnRolled`, keyed off the same "does the default container have
  `spawnPools`" check.

**Documentation**

- Updated the CONTAINER SCHEMA comment (WORLD DATA) to document the
  three new optional container fields: `spawnPools`, `spawnRolled`,
  `lastRolledMinute`.
- Roadmap reconciled against this pass, per `Ashfall_Development_Roadmap_v0.3.0.md`'s
  own Purpose note that its accompanying planning session had already
  narrowed item 15's scope and added item 16 in advance of this
  implementation. Item 15's "Current status" note is updated from
  "specced and shipped as its own handoff" (pre-implementation wording)
  to confirm the item-spawn-pool mechanism is now actually implemented,
  in this version — the remaining scope (container property tags,
  no-respawn flag, the respawn trigger, region/town data model, vehicle
  spawn pools, fauna) was already correctly described as still open and
  needed no further edit. Item 16 (`bandage`/`bandages` naming
  duplicate) is untouched by this pass, exactly as the roadmap already
  expected — not removed. File renamed to
  `Ashfall_Development_Roadmap_v0.4.0.md` per the tracker-naming
  convention.

**Notes / assumptions**

- Duplicate-`itemId`-within-one-roll (the handoff's one open design
  decision): resolved via the existing `addToList()`/`STACKABLE`
  mechanism rather than new special-casing. Two picks of the same
  `Food`/`Medical`/`Materials` item in one roll merge into a single
  stack (the handoff's recommended default). Picks in non-`STACKABLE`
  categories (`Tool`, `Misc`, `Clothing`, etc.) remain separate stack
  entries — not a special case, just the same rule every other duplicate
  item in the game already follows.
- Helper names: `weightedPick`/`randInt`, matching the handoff's own
  suggested names.

**Explicitly NOT in this pass** (per the handoff's own scope — restated
here so a future session doesn't have to reopen the handoff to know
what's still open):

- `carContainers` (vehicle trunk/glovebox) spawn pools.
- The respawn trigger itself (time-based reroll after leaving/returning
  to town) — `lastRolledMinute` is stamped now but nothing reads it yet.
- Region/town data model.
- Container property tags (`equippable`/`movable`/`disassemblable`) and
  the no-respawn flag.
- Fauna alive/dead spawning.
- `master_key` remains purely hand-placed on `onebee`'s Desk — not a
  pool entry, and permanently lost if the player loses it (deliberate).
- The `bandage`/`bandages` naming duplicate (new roadmap Tier 0 item 16,
  not fixed here).

**Validation performed**

- `node --check` on the extracted script: no syntax errors.
- Standalone simulation of `makeDefaultWorld()` + every `SPAWN_POOLS`
  entry: all 23 pools referenced by at least one container, zero unknown
  `itemId` references from any pool into `ITEM_REGISTRY`, zero unknown
  pool ids referenced from any container, all 74 containers accounted
  for with exactly 50 `spawnRolled:true` / 24 roll-eligible (matches the
  handoff's stated counts exactly).
- 1,200-trial stochastic run of `doOpenContainer()` across every
  roll-eligible container: zero errors, ~2.2 items/roll average, ~15%
  fully-empty rolls (consistent with the authored `emptyChance` values).
- Simulated loading a save stripped of `spawnPools`/`spawnRolled`
  (representing a genuine pre-v0.4.0 save) through `applyLoadedData()`:
  confirmed all 74 containers regain correct `spawnPools`/`spawnRolled`
  and a previously-empty container successfully rolls loot on first
  open afterward.
- Headless-browser smoke test (Playwright + the pre-installed Chromium):
  loaded the file with zero console/page errors, confirmed the title
  bar reads v0.4.0, opened a `spawnRolled:true` container (Fridge) and
  confirmed it shows only its original hand-placed contents (no
  unwanted roll), then opened a previously-empty container (Oak
  Apartments 1A Dresser) and confirmed it rolled real loot on first open
  and returned identical contents on a second open (no re-roll).

**Version**: `GAME_CONFIG.VERSION` `"0.3.0"` → `"0.4.0"`

---

## v0.3.0 — Auto-Distance & Direction Wiring

Implements the `Ashfall v0.3.0.md` handoff in full — Part 2 of 2 of the
coordinate-system initiative (roadmap item 11). Part 1 (item 10,
`LOCATIONS`/`locationId`) shipped in v0.2.9. Genuine mechanics pass:
the exit-time-cost rule changes for cross-Location movement, not just
content or rendering.

**Changed — ACTIONS/WORLD INTERACTION (movement)**
- `exitMinutes(exit)` rewritten: compares `world[state.currentRoom]
  .locationId` against `world[exit.to].locationId`. Same-Location
  (`fromLoc === toLoc`) still uses hand-authored `exit.distanceM`,
  unchanged. Cross-Location (`fromLoc !== toLoc`) now calls the new
  `locationDistance(fromLoc, toLoc)` instead of a flat per-gait constant.
  `moveMinutes()`'s existing `MIN_MOVE_MIN` floor (1 minute) is unchanged
  and already covered the "minimum move stays 0:01" requirement — no
  edit needed there.
- `locationDistance(a, b)`: new helper, 3D Euclidean distance between two
  `LOCATIONS` entries, `Math.round`ed to the nearest whole meter.
  Computed on demand every call — never cached or stored on the exit, so
  `LOCATIONS` stays the single source of truth for cross-Location
  distance, per the "no duplicated source of truth" principle.
- `computeDirection(a, b)`: new helper. Pure vertical movement (`dx===0
  && dy===0`) resolves to `"up"`/`"down"` by sign of `dz`. Otherwise the
  larger of `|dx|`/`|dy|` wins the axis, with sign giving the
  cardinal direction. A genuine diagonal tie (`|dx| === |dy|`, both
  nonzero) defaults to the north/south axis, per the handoff — none was
  found in the current rectilinear grid (see Validation).
- `applyComputedDirections(world)`: new helper, called once from
  `makeDefaultWorld()` right after the six `build*()` functions are
  merged. Walks every room/exit; for any exit whose target Location
  differs from the room's own and whose label already contains an
  explicit compass word (matched via `COMPASS_WORD_RE`), replaces that
  word in place with the one `computeDirection()` derives from real
  coordinates. Chosen over a render-time approach per the handoff's
  recommended default — runs once at world-build time rather than on
  every render, keeping `exitMinutes()`/label logic simple. Labels with
  no compass word (building entrances, floor transitions, "Leave the
  apartment", etc.) are never touched, cross-Location or not.

**Removed**
- `exit.block` / `exit.blockHalf` fields, stripped from all 192 exit
  literals across the six `build*()` functions (61 `block:true` + 131
  `blockHalf:true`, confirmed by direct count against the shipped
  v0.2.9 file).
- `BLOCK_MIN`, `HALF_BLOCK_MIN` constants (CONFIG/CONSTANTS) — fully
  superseded by the computed path above.

**Data / schema changes**
- EXIT SCHEMA simplifies: cross-Location exits are now just `{ to,
  label }` (optionally `doorId`) — no `distanceM`, `block`, or
  `blockHalf`. Same-Location exits are unchanged: `{ to, label,
  distanceM }`. ARCHITECTURE's EXIT SCHEMA comment updated to describe
  the two shapes and point at `exitMinutes()`/`locationDistance()`
  instead of the old flat-constant table.
- No PLAYER STATE changes.
- **MINOR bump — `SAVE_KEY` rotates** from `ashfall_save_v0.2` to
  `ashfall_save_v0.3` (`versionCompat()` derives the key from
  `MAJOR.MINOR`). Existing browser-slot saves won't auto-load under the
  new key; still recoverable via Export/Import. This is the intended
  "real seam" for a MINOR bump, not a bug — no exit-specific save
  backfill is needed, since `world` is embedded verbatim in saves and
  the new `exitMinutes()` never reads the retired `block`/`blockHalf`
  fields even if a stale save's `world` still carries them.

**Sections touched**
- ACTIONS/WORLD INTERACTION (movement): `exitMinutes()`. `doMove()`'s
  call site is unchanged; both call sites (`doMove()` and
  `renderMoveActionsPanel()`) already read `state.currentRoom` as the
  FROM room before it's updated to `exit.to`, so no change was needed
  there.
- WORLD DATA: every `build*()` function's exit definitions lose
  `block`/`blockHalf`; `makeDefaultWorld()` now pipes its merged result
  through `applyComputedDirections()` before returning it.
- CONFIG/CONSTANTS: `BLOCK_MIN`/`HALF_BLOCK_MIN` removed.
- Documentation: ARCHITECTURE's LOCATIONS note and EXIT SCHEMA comment
  updated (see Documentation below); this is a mechanics pass, not
  content-only.

**UI**
- Exit button labels: the compass word in cross-Location labels is now
  computed rather than authored. Confirmed unchanged text in every
  case that has one today (see Validation) — this is a substitution
  mechanism going forward, not a wording change now.
- Displayed travel times shift for street-grid movement at the current
  100m-block / 3m-floor scale (e.g. a full block on foot: 2 min → ~1
  min; see the handoff's balance table). Intentional consequence of
  moving to real coordinates, not a rebalance.

**Explicitly out of scope** (per the handoff)
- Any change to same-Location exits, distance or label.
- Floor-transition/building-entrance label phrasing (no compass word
  today, none added).
- New content (rooms, basements, roofs).
- Re-deriving or adjusting the v0.2.9 `LOCATIONS` data or building/floor
  coordinates.

**Validation performed**
- `node --check` syntax pass on the extracted script: clean.
- Full diff against v0.2.9: every changed line traces to
  `CONFIG/CONSTANTS`, the EXIT SCHEMA/LOCATIONS ARCHITECTURE comments,
  the 192 `block`/`blockHalf` exit literals (field removed, label text
  untouched), `makeDefaultWorld()`, or `exitMinutes()` — no stray
  content or unrelated-mechanics edits.
- Standalone Node harness (full script through `makeDefaultWorld()`,
  executed in isolation) built the real `world` and walked all 93
  rooms / 286 exits: every exit resolves a target room and a
  `LOCATIONS` entry on both ends; 68 same-Location exits all still
  carry `distanceM`; 218 cross-Location exits correctly carry none;
  zero diagonal ties.
- Label-substitution check: 184 cross-Location exits carry a compass
  word. Diffed every one's label, old build vs. new, matched by exit
  target — **zero actual text changes**. The computed directions match
  the hand-authored ones in every existing case, confirming the
  handoff's "should read the same in virtually all cases" prediction
  rather than merely assuming it.
- `SAVE_KEY` rotation confirmed directly: `versionCompat("0.3.0")` →
  `"0.3"`, so `SAVE_KEY` = `ashfall_save_v0.3` (was `ashfall_save_v0.2`
  under v0.2.9).

**Documentation**
- ARCHITECTURE's LOCATIONS note updated: was "read only by MAP
  rendering as of v0.2.9," now describes both MAP rendering and
  movement (`exitMinutes()`/`locationDistance()`/
  `applyComputedDirections()`/`computeDirection()`) as readers. Current
  version line bumped to 0.3.0.
- EXIT SCHEMA comment rewritten to describe the same-Location vs.
  cross-Location shapes above, replacing the old three-variant
  (`distanceM`/`block`/`blockHalf`) description.
- Closes the two-part "Coordinate System" roadmap item opened in
  v0.2.9: item 11 removed from the roadmap in this same update,
  alongside the rename to `Ashfall_Development_Roadmap_v0_3_0.md`.

**Notes / assumptions**
- Audit finding, not a scope change: beyond the 192 `block`/`blockHalf`
  exits, 26 pre-existing plain-`distanceM` exits are *also*
  cross-Location — building entrances/exits and floor transitions
  (e.g. `cornerstore ↔ main2nd`, `stairs2 ↔ stairs1`, `pharmacy_apt ↔
  pharmacy`). The handoff's existing-state audit only enumerated the
  `block`/`blockHalf` population; it didn't separately flag these. The
  new `exitMinutes()` rule ("cross-Location → computed") applies to
  them the same as any other cross-Location exit, so their
  `exit.distanceM` field is now unread/vestigial rather than acted on.
  Checked, not assumed: for all 26, the old hand-authored distance and
  the newly-computed distance both fall well under the one-minute floor
  at every gait, so the *displayed* travel time (`fmtDuration`, which
  itself rounds) is identical in every case — confirmed by direct
  computation, not inferred from the small numbers involved. Left the
  vestigial `distanceM` fields in place rather than expanding this
  pass's scope to strip them; added as a new Tier 0 roadmap item
  (below) instead, per "unplanned gaps get documented as new roadmap
  items rather than silently expanded."
- No diagonal-tie case was found in the current grid (checked
  programmatically across all 218 cross-Location exit pairs) — the
  tie-break default (north/south axis) is implemented per the handoff
  but currently unexercised.

**Version**: `GAME_CONFIG.VERSION` `"0.2.9"` → `"0.3.0"`

---


## v0.2.9 — Coordinate Data Model & Map Rendering Migration

Implements the `Ashfall v0.2.9.md` handoff in full — Part 1 of 2 of the
coordinate-system initiative (roadmap item 10). Part 2 (item 11,
auto-distance & direction wiring) is specced separately in
`Ashfall v0.3.0.md` and depends on this pass. Content/rendering/
persistence only — no movement mechanic touched yet.

**New**
- `LOCATIONS`: new WORLD DATA table giving every street/mid-block node
  and building floor a real integer `(x, y, z)` position in meters.
  Origin `(0,0,0)` = `maple4th` (town SW corner), street level; +X east,
  +Y north, +Z up. Block size 100m, floor height 3m. 66 entries total:
  51 street/mid-block Locations (id = the room id itself, `z:0`,
  `(x,y)` = the old `MAP_NODES {col,row} * 100`) + 15 building-floor
  Locations (one per floor, shared by every room on that floor; `(x,y)`
  = the building's old `MAP_ANCHORS` node; `z:0`/`z:3` for ground/
  upper floor). Replaces `MAP_NODES`/`MAP_ANCHORS` entirely.
- `locationId`: new required ROOM SCHEMA field, added to every one of
  the 93 rooms across all six `build*()` functions, resolving into
  `LOCATIONS`.
- `backfillLocationIds()` (PERSISTENCE, beside `backfillItemIds()`):
  assigns `locationId` to any loaded room missing it, by direct room-id
  lookup against a freshly-built `makeDefaultWorld()` — room ids are
  stable, so (unlike `backfillItemIds()`'s name-matching) this is an
  unambiguous key lookup. Wired into `applyLoadedData()` alongside
  `resyncUidCounter()`/`backfillItemIds()`.
- `validateLocations()` (dev-only console helper, beside
  `validateItemRegistry()`): walks every room, confirms `locationId` is
  set and resolves in `LOCATIONS`; logs any that don't. Not wired to
  any button.

**Changed — MAP rendering**
- `mapToSvg`, `mapPathD`, `renderMapClose`, `renderMapWide`,
  `mapPositionPlayer`, `mapTargetViewBox` now read
  `LOCATIONS[id].x / 100` / `.y / 100` in place of the old
  `MAP_NODES[id].col` / `.row` — dividing by 100 recovers the exact same
  grid-unit spacing the SVG layout constants (`MAP_SPACING`,
  `MAP_MARGIN`) already assume, so rendered output is unchanged.
- `renderMap()` resolves the player's current map position via
  `world[state.currentRoom].locationId` instead of the removed
  `mapNodeForRoom()`.
- `MAP_BUILDINGS[i].anchor` now names a building's ground-floor
  `LOCATIONS` id (e.g. `acorn_f0`) instead of a `MAP_NODES` key. Same
  field, same usage — Pharmacy/Hardware Store still correctly share one
  anchor (`mid_main_1_3` → both resolve to `x:250,y:200`), kept visually
  distinct by their existing `dx`/`dy` cosmetic offset, which is
  untouched.
- Added `MAP_STREET_NODE_IDS` (derived once via
  `Array.from(new Set(MAP_STREETS.flatMap(s => s.chain)))`) for the
  Close-map node-dot loop in `renderMapClose()`, replacing
  `Object.keys(MAP_NODES)`. Deriving it from `MAP_STREETS` — which
  already lists every street node across its nine chains — avoids
  hand-duplicating the 51-id list a second time, per the "no duplicated
  source of truth" principle.

**Removed**
- `MAP_NODES`, `MAP_ANCHORS`, `mapNodeForRoom()` — fully superseded by
  `LOCATIONS`/`locationId`.

**Sections touched**
- WORLD DATA: new `LOCATIONS` table; `locationId` added to every room
  across all six `build*()` functions.
- UI/RENDERING → MAP sub-block: `mapToSvg`, `mapPathD`,
  `renderMapClose`, `renderMapWide`, `mapPositionPlayer`,
  `mapTargetViewBox`, `renderMap`.
- PERSISTENCE: `backfillLocationIds()`, `applyLoadedData()`.
- ACTIONS/SIMULATION untouched — no movement mechanic changed. That's
  `Ashfall v0.3.0.md` (Part 2).

**Explicitly out of scope** (per the handoff)
- `distanceM` auto-computation, `block`/`blockHalf` removal, and
  exit-label direction templating — all `Ashfall v0.3.0.md`, Part 2.
- Any new player-facing content (no new rooms, no roof/basement
  content).
- `Z` is laid down for every Location but not consumed by anything yet
  (the map is top-down) — intentional, so Part 2 and future systems
  don't have to retrofit it.

**Design decision resolved**
- `oak_stairs` floor assignment: resolved to `oak_f0` (the lower of the
  two floors it connects), per the handoff's recommended default. Acorn's
  stairwell needed no such call — it's already split into
  `stairs1`/`stairs2`, one per floor.

**Explicitly NOT changed**
- Room/item/container/exit data and values, all `distanceM`/`block`/
  `blockHalf` exit fields, `GAITS`/`BLOCK_MIN`/`HALF_BLOCK_MIN`, UI
  layout/styling, and every mechanics function outside the MAP
  rendering sub-block listed above.
- Rendered map output: pixel-identical by construction (see Validation).

**Validation performed**
- `node --check` syntax pass on the extracted script: clean.
- Full diff against v0.2.8: confirmed every changed/removed line traces
  to the `LOCATIONS`/`locationId` migration, the MAP rendering sub-block,
  `backfillLocationIds()`/`validateLocations()`, or the version-bump
  comment updates — no stray content edits.
- Standalone Node harness (`ITEM_REGISTRY`, `LOCATIONS`, all six
  `build*()` functions, and `makeDefaultWorld()` extracted and executed
  in isolation) confirmed all 93/93 rooms resolve a `locationId` that
  exists in `LOCATIONS` (mirrors `validateLocations()`'s own check).
- Confirmed mathematically, for all 51 street/mid-block ids, that
  `LOCATIONS[id].x / 100` and `.y / 100` exactly equal the old
  `MAP_NODES[id].col` and `.row` — the map's rendered coordinates are
  unchanged, not just visually similar.
- `SAVE_KEY` unaffected: confirmed `versionCompat()` still derives
  `"0.2"` from `"0.2.9"` (PATCH bump, no `SAVE_KEY` rotation).

**Documentation**
- Fixed the stale "Current version: 0.2.7" line in the ARCHITECTURE
  comment (had drifted two versions behind) and added a brief
  `LOCATIONS`/`locationId` note there and in the ROOM SCHEMA comment
  block.
- Roadmap item 10 ("Coordinate System — Part 1") is complete as of this
  entry; removed from the roadmap in the same update that renames it to
  `Ashfall_Development_Roadmap_v0_2_9.md`. Item 11 ("Part 2") is now
  unblocked and stays on the roadmap.

**Notes / assumptions**
- Count discrepancy in the handoff, resolved by following the
  authoritative table over the prose: the handoff's "Rules / mechanics"
  section states 16 building-floor Locations ("5 two-floor buildings ×
  2 + 6 one-floor buildings × 1"), but its own "Building → Location
  membership" table — marked "authoritative — apply exactly" — lists
  only 5 one-floor buildings (Storage Facility, Riverbank, Auto
  Workshop, Police Station, Riverside Freight), for 15 building-floor
  Locations, not 16. The likely source: the handoff's "Relevant existing
  state" section separately notes `MAP_BUILDINGS` has 11 entries (5
  two-floor + "the other 6"), but that 11 includes a purely cosmetic
  "Alley" marker sharing Acorn's anchor for map-label purposes only —
  not a real building with its own floor. `alley` (the room) is already
  a member of `acorn_f0` in the membership table, consistent with its
  pre-existing `MAP_ANCHORS` entry (`alley:"mid_poplar_1_2"`, the same
  anchor as every other Acorn Apartments room). Implemented as 15
  building-floor Locations (66 total, not 67) — internally consistent
  with the table, `MAP_ANCHORS`, and the live v0.2.8 room count; flagging
  here rather than silently resolving, per the "judgment calls get
  flagged" convention.

**Version**: `GAME_CONFIG.VERSION` `"0.2.8"` → `"0.2.9"`

---

## v0.2.8 — WORLD DATA / RENDERING Modularity Pass

Pure code-organization pass, per the `Ashfall v0.2.8.md` handoff. No
roadmap item — a standalone maintainability pass done at Tom's request.
No gameplay, content, or DOM-output change.

**Organization / Structural**
- Split `makeDefaultWorld()` (previously one ~1,025-line object literal,
  93 rooms) into six per-building functions —
  `buildAcornApartments()`, `buildStreetsAndOutdoor()`,
  `buildOakApartments()`, `buildAutoWorkshop()`, `buildPoliceStation()`,
  `buildRiversideFreight()` — merged back via `Object.assign()` in a now
  thin `makeDefaultWorld()`. Grouping follows the handoff's recommended
  default: one function per named building on `MAP_BUILDINGS`, plus
  `buildStreetsAndOutdoor()` for street/outdoor rooms (`building:""` or a
  street name). No room id, key, or value changed; no duplicate-key
  collisions found.
- Extracted the remaining inline sections of `render()` into six named
  panel functions, matching the existing `renderCraftPanel()` /
  `renderMap()` pattern: `renderLocationPanel()`, `renderStatsPanel()`,
  `renderMoveActionsPanel()`, `renderHereActionsPanel()`,
  `renderInventoryPanel()`, `renderWorldItemsPanel()`. `render()` is now
  a short orchestrator; the `gameOver` early-return branch stays inline
  per the handoff. Panel functions each resolve `world[state.currentRoom]`
  independently where needed, rather than threading it as a parameter —
  matching the self-contained style of the existing extracted panels.

**Sections touched**: WORLD DATA (`makeDefaultWorld()` restructure only —
no room data changed), RENDERING (`render()` and the six new panel
functions).

**Explicitly out of scope**: any content/value/DOM-output change; any
build tooling or multi-file split; the Tier 0 `giveItem()` registry
cleanup item; any roadmap edit, per Tom's explicit instruction for this
handoff.

**Explicitly NOT changed**: room/item/container/exit data and values;
UI layout, styling, or displayed text; save format (`SAVE_KEY` unaffected
— PATCH bump); any mechanics function outside `render()`'s panel
extraction.

**Validation performed**
- `node --check` syntax pass on the extracted script: clean.
- Full diff against v0.2.7: confirmed the only changes are the
  `GAME_CONFIG.VERSION` bump and the two structural relocations described
  above (no stray content edits).
- Programmatic deep-equality check of the merged `world` object against
  v0.2.7's `makeDefaultWorld()` output: 93/93 room keys present,
  order-independent structural match confirmed via a Node harness
  requiring both versions' pre-render script and comparing sorted JSON.
- Multiset comparison of every `document.getElementById(...)` call
  across both files: identical (48/48), confirming no panel dropped or
  duplicated a DOM reference during extraction.
- Functional simulation: both v0.2.7 and v0.2.8 scripts executed in a
  sandboxed DOM stub (Node `vm`, stubbed `document`/`localStorage`),
  triggering the game's initial `render()` call. Resulting DOM state
  (text/HTML/children/style/disabled) compared element-by-element across
  every panel — identical, apart from the expected version-string
  difference in `pageTitle`.

**Documentation**
- The roadmap was updated separately from this handoff, at Tom's
  explicit follow-up request (overriding the handoff's "no roadmap
  edits" instruction for that one instruction only) — not part of this
  coding pass's own scope. `Ashfall_Development_Roadmap_v0_2_7.md` was
  renamed to `Ashfall_Development_Roadmap_v0_2_8.md` and a new Tier 0
  item (#9, "Split `buildStreetsAndOutdoor()` by town/location") was
  added, noting that the v0.2.8 building-level split left all
  street/outdoor rooms in one combined function and flagging a future
  further split by town/location as a low-priority, deferrable cleanup
  item.

**Notes / assumptions**
- Building/grouping boundaries and function names follow the handoff's
  recommended defaults exactly (see "Design decisions" in
  `Ashfall v0.2.8.md`), so no deviation to record.

**Version**: `GAME_CONFIG.VERSION` `"0.2.7"` → `"0.2.8"`

---

## v0.2.7 — Item Identity & Reference Consistency

Implements `Ashfall v0.2.7.md` in full (Tier 0, item 0.1). Gives every
runtime item a stable `itemId` (registry-definition identity, alongside
the existing `_uid` instance identity) and converts the remaining
mechanics that keyed off display name to `itemId` lookups instead. This
is a cross-cutting identity-consistency pass — no content or mechanic
changes, no new persistent state.

**New — WORLD DATA**
- Four `ITEM_REGISTRY` entries added, matching properties previously
  only inline in `RECIPES`/`HEAT_RECIPES` output and `doFish()`
  (no balance changes): `bandage`, `campfire_kit`, `cooked_fish`,
  `raw_fish`.
- `RECIPES[].inputs[]` schema changed from `{name, qty}` to `{id, qty}`
  (`cloth`, `duct_tape`, `firewood`). `RECIPES[].output` /
  `HEAT_RECIPES[].output` changed from a literal item object to `{id}`.
  `HEAT_RECIPES[].input` changed from a name string (`"Raw fish"`) to an
  id string (`"raw_fish"`).

**Changed — ITEM SYSTEM**
- `itemFromRegistry()` now stamps `item.itemId = ref.id` on every item it
  produces, in addition to existing `qty`/`overrides` behavior.
- `addToList()`'s stacking match changed from
  `i.name===item.name && i.category===item.category` to
  `i.itemId===item.itemId && i.category===item.category`.
- `countInPools()` / `consumeFromPools()` now take an `itemId` first
  argument and match `it.itemId === itemId`, instead of matching on
  `name`. All nine call sites updated (`canCraft`/`doCraft`, and the
  fire/cooking `"firewood"`/`"campfire_kit"` id literals in
  `canBuildFire`/`doBuildFire`/`doAddFuel`/render's add-fuel check).
- `it.name === "Campfire Kit"` (gating the Campfire Kit "Disassemble"
  action) replaced with `it.itemId === "campfire_kit"`.

**Changed — CRAFTING, FIRE/COOKING**
- `doCraft()` and `doCookInContainer()` now resolve their output through
  `itemFromRegistry({ id: recipe.output.id, qty:1 })` instead of
  spreading a literal `recipe.output` object.
- `doFish()`'s raw-fish grant now goes through
  `itemFromRegistry({ id:"raw_fish", qty:1 })`.
- `doCookInContainer()`'s input match changed from
  `it.name===recipe.input` to `it.itemId===recipe.input`.
- Display text that previously read `.name` directly off `recipe.output`
  / `recipe.input` / a recipe input entry now looks the name up via
  `ITEM_REGISTRY[id].name` instead, since those fields are now id
  references rather than full item objects: the craft-success log line,
  the cook-finishes log line, the crafting-menu ingredient list
  (`needs Cloth x2, Duct tape x1`), and the "Cook the X" action label +
  its container-has-ingredient visibility check. Player-facing text is
  unchanged; only how it's produced changed.

**New — PERSISTENCE**
- `backfillItemIds()`, a sibling function called alongside
  `resyncUidCounter()` from `applyLoadedData()` on every load. For any
  loaded item missing `itemId`, it looks up the id by reverse name match
  against `ITEM_REGISTRY` (current registry names are unique) and
  assigns it if found. Items with no registry match are left without
  `itemId` and continue working via `_uid`/list position, same as
  before this pass. No save-format migration — additive only, no
  `SAVE_KEY` change.

**New — dev tooling**
- `validateItemRegistry()`, a console-only helper (not wired to any
  button or UI) that walks `RECIPES`/`HEAT_RECIPES` inputs/outputs and
  logs any `id` that doesn't resolve in `ITEM_REGISTRY`.

**Documentation**
- Fixed the ARCHITECTURE comment's stale `Current version: 0.2.3.` note
  to `0.2.7` (already stale independent of this pass; fixed while in the
  area).
- Roadmap: removed Tier 0, item 0.1 (Item Identity & Reference
  Consistency) — closed by this pass. No other roadmap changes; nothing
  else audited as drifted.

**Explicitly NOT changed**
- No balance values, no item weights/restores/tags changed on any
  existing or new registry entry.
- `hasTool()` and the tag system — already fully capability-based, not
  touched.
- Equipment/`doEquip()`/`doUnequip()` instance-identity reconstruction —
  out of scope per the handoff, not touched.
- No new player-state fields, no `SAVE_KEY` change.

**Validation performed**
- `node --check` on the extracted script: passes.
- Full diff against `ashfall_0_2_6.html`: confirmed every changed line
  maps to an item in the handoff's Rules/In-scope sections or a
  necessary display-text follow-through (see above); no unrelated line
  changed.
- Sandboxed functional run of the actual updated script (DOM stubbed):
  verified `validateItemRegistry()` reports no unresolved ids; crafting
  a bandage consumes `cloth`×2 + `duct_tape`×1 and yields a `bandage`
  item with `itemId` set; `doFish()` yields a `raw_fish` item with
  `itemId` set; `itemId`-based stacking in `addToList()` correctly
  merges same-id gives within one list and correctly does *not* merge
  across list/floor-overflow boundaries; `consumeFromPools()` correctly
  depletes by `itemId`; `backfillItemIds()` correctly assigns `itemId`
  to a synthetic legacy item (no `itemId`, name-only) by reverse name
  match.

**Notes / assumptions**
- The backfill scan was implemented as a sibling function
  (`backfillItemIds()`) rather than folded into `resyncUidCounter()`,
  per the handoff's "Design decisions" section leaving that shape
  choice open.

**Version**: `GAME_CONFIG.VERSION` `"0.2.6"` → `"0.2.7"`

---

## v0.2.6 — giveItem() Registry Cleanup + Street Grid Expansion & Rename

Implements `Ashfall v0.2.6.md` in full — two independent pieces of work
bundled into one pass: the last `giveItem()` registry cleanup (Tier 0,
item 0.1), and a 3×3→5×4 street grid expansion with a full north-south
street renumbering and 4 new buildings. Content-only in the WORLD DATA
sense (no new mechanic anywhere), plus the RENDERING changes the bigger
grid requires.

**Fixed**
- `giveItem()` call sites that hand-authored a literal item object instead
  of resolving through `ITEM_REGISTRY` now use `itemFromRegistry()`: the
  "Remove batteries" action (Spare batteries), the Campfire Kit
  "Disassemble" action, the campfire-dismantle refund, and the tree-chop
  yield (all three Firewood). Closes Tier 0 item 0.1 — no `giveItem()`
  call site anywhere in the script hand-authors a registry-covered item
  anymore.

**New — WORLD DATA**
- Street grid grown from 3 north-south × 3 east-west streets (9
  intersections, 12 mid-blocks) to 5×4 (20 intersections, 31 mid-blocks).
  Added Maple St (new southernmost east-west street) and 4th/5th St (new
  outer-ring north-south streets, west and east of the existing three).
  Water St remains the fixed north edge.
- 11 new intersections and 19 new mid-blocks, all outer-ring content per
  the low-density design principle (shorter descriptions, fewer parked
  cars/props than downtown).
- 4 new buildings, containers only, no items in any of them, no locks on
  any door:
  - **Oak Apartments** (4 units, no superintendent's unit) at
    `mid_poplar_2_4` — each unit is a single combined room rather than a
    full Acorn-style suite.
  - **Auto Workshop** (`auto_shop`, `auto_shop_back`) at `mid_main_3_5`.
  - **Police Station** (`police_lobby`, `police_evidence`) at `maple3rd`.
  - **Riverside Freight**, an industrial/warehouse building
    (`industrial_floor`, `industrial_office`) at `maple2nd`.

**Changed — Street renumbering**
- North-south streets renumbered west→east as 4th·2nd·1st(center)·3rd·5th
  (west of center gets evens, east gets odds). The 9 existing
  intersections were renamed accordingly (`poplar1st`→`poplar2nd`,
  `main1st`→`main2nd`, `main2nd`→`main1st`, `water1st`→`water2nd`,
  `water2nd`→`water1st`; `outside`, `poplar3rd`, `main3rd`, `water3rd`
  keep their ids). `building` display strings and every exit/label
  touching these rooms were updated to match.
- The 12 existing mid-block rooms were **also** renamed to keep ids
  internally consistent with the new numbering (e.g. `mid_poplar_1_o` →
  `mid_poplar_1_2`, `mid_main_2_3` → `mid_main_1_3`, `mid_1st_p_m` →
  `mid_2nd_p_m`). The handoff's explicit rename list only covered the two
  mid-blocks with building anchors on them; the rest were renamed to
  match for consistency, since leaving some ids on the old numbering
  scheme and others on the new would read as an authoring error rather
  than a deliberate choice. Flagged here per the "no duplicated source of
  truth" / judgment-call convention.
- Descriptions rewritten for `outside`, `main1st` (was `main2nd`), and
  `water3rd` per the handoff; `poplar3rd`'s description was left as-is
  (still geographically accurate).

**New — exits at the grid's old boundary**
- The handoff explicitly called out `main3rd` and `water3rd` gaining new
  east exits (to the new 5th St column). Working through the full grid
  geometry, the same logic applies to every other room that sat on the
  old grid's edge: `poplar3rd` also gains an east exit (to `poplar5th`),
  and `outside`/`poplar2nd`/`main2nd`/`water2nd` gain new south/west
  exits (to the new Maple row and 4th St column respectively) — all
  wired via the new mid-blocks the handoff already specifies
  (`mid_poplar_3_5`, `mid_1st_mp_p`, `mid_poplar_2_4`, `mid_main_2_4`,
  `mid_water_2_4`). The handoff's "existing renamed intersections keep
  the same number of exits" note doesn't hold once the grid grows on
  both edges; resolved using the grid data itself (Part C's node table
  and the full new-mid-block list) as ground truth, since that data is
  exact and this generalization follows directly from it.

**RENDERING**
- `mapToSvg`'s row-flip generalized from a hardcoded `(2 - row)` to
  `(MAP_MAX_ROW - row)`, with new `MAP_MAX_COL = 4` / `MAP_MAX_ROW = 3`
  constants.
- River-line coordinates in `renderMapClose` and `renderMapWide`
  generalized from `mapToSvg(0,2)`–`mapToSvg(2,2)` to
  `mapToSvg(0, MAP_MAX_ROW)`–`mapToSvg(MAP_MAX_COL, MAP_MAX_ROW)`.
- `MAP_WIDE_VIEWBOX` grown from `{x:20,y:20,w:360,h:360}` to
  `{x:20,y:20,w:610,h:480}` to fit the larger grid extent.
- `MAP_STREETS` rebuilt as 9 chains (4 horizontal + 5 vertical, up from
  6). `MAP_BUILDINGS` updated: 7 existing entries retargeted to their
  renamed anchors, 4 new entries added for the new buildings.

**Documentation**
- Roadmap reconciled: Tier 0 item 0.1 (giveItem() registry cleanup)
  removed — closed in full. Tier 1 item 2 (Adams/Washington outer-ring
  expansion) removed rather than edited in place, per the handoff's
  recommendation — this pass substantially fulfills its intent but with
  materially larger scope and different street names (4th/5th/Maple, not
  "Adams/Washington") than the item's original wording described.

**Notes / assumptions**
- Industrial building's name: "Riverside Freight" (handoff left this
  open, coding session's call).
- New container capacities followed existing precedent (e.g. Auto
  Workshop's Workbench at 30kg ≈ Hardware Store's Tool Wall).
- Industrial office's safe left unlocked (recommended default in the
  handoff) rather than seeded as a locked dead end.
- Police Station's evidence room: only `evidencelocker` was implemented
  as an actual container. The handoff also listed a `cell` container id,
  but its own parenthetical ("the cell itself isn't a container, just
  flavor") reads as the room description doing that work instead — the
  cell is mentioned in the room's `desc` text only.

**Explicitly NOT changed**
- No PLAYER STATE, ACTIONS/SIMULATION, WORLD INTERACTION,
  STAMINA/FATIGUE, CRAFTING, or PERSISTENCE code touched anywhere in this
  pass. Acorn Apartments' interior (rooms, containers, items) is
  untouched — only its map anchor id changed. No items were added to any
  of the 4 new buildings. No locks were added anywhere new; the existing
  Acorn master-key mechanic is untouched. No rooftops (Tier 1 item 1) —
  not touched.

**Validation performed**
- `node --check` on the extracted script: passes.
- Full reachability check: all 93 rooms in `makeDefaultWorld()` resolve
  through `MAP_NODES`/`MAP_ANCHORS`, and all 93 are reachable from the
  starting room (`living`) via a BFS over `exits`. Every `MAP_NODES` id
  has a corresponding room; every `MAP_STREETS` chain and `MAP_BUILDINGS`
  anchor resolves to a valid node.
- Diff against `ashfall_0_2_5.html`: every changed hunk falls within
  `CONFIG/CONSTANTS` (version bump), `WORLD DATA`, the two
  `INVENTORY/ITEM SYSTEM` and `FIRE/COOKING` `giveItem()` call sites, and
  `RENDERING`/`MAP`. No hunk touches PLAYER STATE, CORE UTILITIES, WORLD
  INTERACTION, SURVIVAL/TIME SIMULATION, STAMINA/FATIGUE, CRAFTING, or
  PERSISTENCE.

**Version**: `GAME_CONFIG.VERSION` `"0.2.5"` → `"0.2.6"`

---

## v0.2.5 — In-Game Viewing Map

Implements roadmap Tier 1, item 3 in full, per the "Ashfall v0.2.5.md"
handoff. Ported directly from `map_demo.html`, the standalone prototype
built and iterated on during the planning session.

**New**
- The side-menu `Map` section's placeholder is replaced with a working
  static orientation map: a Close/Wide zoom toggle in the section header
  (styled like the existing `#gaitBar` pace buttons) and an SVG map below
  it.
- **Close view** (default): centers on the player's current location,
  draws every street-grid node, and labels each of the 7 buildings with a
  small marker (two-line label for multi-word names, e.g. "Hardware" /
  "Store"). Re-centering on a location change is animated — a ~350ms
  cubic-ease-out `viewBox` tween via `requestAnimationFrame` (`viewBox`
  isn't CSS-animatable).
- **Wide view**: a fixed `viewBox` showing the whole grid. No building
  markers — streets only, each identified by its own name running along
  the line itself via `<textPath>` (repeated three times with a bullet
  separator), with a thin low-opacity guide stroke underneath.
- Switching between Close and Wide re-renders the SVG content and snaps
  the `viewBox` to the new view (no animation); only in-Close location
  changes animate.
- A single player-position dot repositions to the resolved map node in
  both views whenever the map re-renders.
- `#sideMenu` widened from 270px to 360px (the width the demo's two-line
  building labels and the Wide view were tuned against).

**Explicitly out of scope** (per the handoff, not implemented here)
- Fog of war / reveal-as-explored — the full grid always renders.
- Room/floor-level detail — the map resolves to *building*, never a
  specific room or floor within one.
- Click-to-travel or any interaction beyond viewing and switching zoom.
- Rooftops and the Adams/Washington outer-ring expansion — neither exists
  in world data yet; the coordinate scheme is deliberately extensible
  (plain integer/half-integer grid, no hardcoded bounds) for when they do.

**Sections touched**
- **WORLD DATA** — additive only, placed after `itemFromRegistry`/
  `itemsFromRegistry` and before `makeDefaultDoors()`: `MAP_NODES` (21
  street-grid node coordinates) and `MAP_ANCHORS` (id -> map node for
  every non-street room), plus `mapNodeForRoom()`. No existing room,
  item, container, exit, door, or window definition changed.
- **RENDERING** — new self-contained MAP sub-section (`MAP_STREETS`,
  `MAP_BUILDINGS`, `mapToSvg`, `mapPathD`, `mapRepeatedLabel`,
  `renderMapClose`, `renderMapWide`, `mapPositionPlayer`,
  `mapTargetViewBox`, `mapUpdateViewBox`, `renderMap`). `renderMap()` is
  called once, at the end of the existing top-level `render()`, alongside
  the other per-frame render calls — no new render loop or hook point was
  needed since `render()` already runs on every location change.
- **EVENTS/UI HELPERS** — click handlers for the two zoom-toggle buttons,
  added next to the existing `#gaitBar` handler.
- Menu markup/CSS: the `Map` `menu-section`'s placeholder div replaced
  with the toggle + `<svg id="mapSvg">`; new `.map-*`-prefixed CSS rules
  (no existing class names touched).

**Explicitly NOT changed**
- No PLAYER STATE, movement/WORLD INTERACTION, SURVIVAL/TIME SIMULATION,
  CRAFTING, FIRE/COOKING, or PERSISTENCE code — this is a RENDERING
  addition plus two small pieces of new static WORLD DATA, no new
  mechanic.
- No existing room, item, exit, or content definitions were altered.

**Validation performed**
- Extracted script passes `node --check` with no syntax errors.
- Confirmed via script that every room id returned by `makeDefaultWorld()`
  (50 rooms) resolves through `MAP_NODES` or `MAP_ANCHORS` — exact set
  match, none missing, none extra.
- Full diff against v0.2.4 confirms the only changes are the map feature
  (CSS, menu markup, `MAP_NODES`/`MAP_ANCHORS`/`mapNodeForRoom`, the new
  MAP rendering sub-section, the zoom-toggle event handlers, the
  `renderMap()` call, and the sideMenu width) plus the version string —
  no mechanics code touched.
- Manually traced the starting room (`living` → `mid_poplar_1_o`) through
  `mapToSvg`/`mapTargetViewBox` to confirm the default Close-view
  `viewBox` centers correctly on game start.

**Documentation**
- `Ashfall_Development_Roadmap.md` reconciled against the actual v0.2.5
  code (it had drifted — two Tier 0/1 items it still listed as pending
  were already implemented):
  - Tier 1 item 3 (this feature, In-Game Viewing Map) removed.
  - Tier 0 item 0.1 ("Remove the Phone placeholder") removed — the code
    has no Phone-related menu section, item, comment, or state field
    remaining; already fully implemented.
  - Tier 1 item 4 ("Item Registry / ID-Based Item Definitions") removed
    — `ITEM_REGISTRY` and `itemsFromRegistry()` are already in place and
    used throughout `makeDefaultWorld()`; already fully implemented.
  - New Tier 0 item 0.1 added in its place: four `giveItem()` call sites
    (Firewood ×3 in INVENTORY/ITEM SYSTEM and FIRE/COOKING, Spare
    batteries ×1 in INVENTORY/ITEM SYSTEM) still construct a literal item
    object instead of reading `ITEM_REGISTRY` via `itemFromRegistry()` —
    confirmed present via `grep` against the v0.2.5 script.
  - All subsequent Tier 1/2/3 items renumbered accordingly.

**Version**: `GAME_CONFIG.VERSION` `"0.2.4"` → `"0.2.5"`

---

## v0.2.4 — Fix missing mid-block movement directions

**Fixed**
- Every mid-block `mid_*` WORLD DATA location (12 total) has two through
  exits — one back the way you came, one continuing onward. The v0.2.3
  pass that added compass-direction wording to movement labels only
  applied it to the "back" exit (`"Head [direction] toward X"`); the
  "onward" exit kept its pre-existing `"Continue toward X"` label with no
  direction word at all. Depending on the street segment, the missing
  direction was east or north in each case (never west/south, since those
  always landed on the "back" exit of the pair).
- Fixed by adding the correct compass word to each affected `"Continue
  toward X"` label, derived as the opposite of that mid-block's paired
  `"Head [direction]"` exit and cross-checked against the adjacent
  intersection locations' own exit lists for consistency (e.g.
  `mid_main_1_2`'s "toward 2nd St" exit must be east, since `main2nd`'s
  exit back to `main1st` is labeled west).
- Affected locations: `mid_poplar_1_o`, `mid_poplar_o_3`, `mid_1st_p_m`,
  `mid_2nd_o_m`, `mid_3rd_p_m`, `mid_main_1_2`, `mid_main_2_3`,
  `mid_1st_m_w`, `mid_2nd_m_w`, `mid_3rd_m_w`, `mid_water_1_2`,
  `mid_water_2_3`.

**Scope**
- WORLD DATA only (content) — exit `label` strings exclusively. No exit
  `to` targets, no other fields, no mechanics code touched.

**Validation performed**
- Extracted script passes `node --check` with no syntax errors.
- Confirmed via `grep` that no `"Continue toward"` label (missing a
  direction word) remains in the file — all 12 now read `"Continue
  [direction] toward X"`.
- Each derived direction was cross-checked against the corresponding
  full-intersection location's exit list to confirm the two ends of each
  street segment agree on direction (e.g. a "west" exit on one side
  implies an "east" exit on the other).

**Version**: `GAME_CONFIG.VERSION` `"0.2.3"` → `"0.2.4"`

---

## v0.2.3 — no entry was written

This version shipped and no entry was written for it. `v0.2.4`'s closing line
records the bump as `"0.2.3"` → `"0.2.4"`, and two later entries name v0.2.3
directly, so the gap is an omission rather than a skipped number. Nothing has
been reconstructed: `git log` is the only surviving record of what it changed,
and a reconstruction written this long after the fact would not be the record
this file exists to keep. There is no `v0.2.3` tag either — tagging begins at
v0.4.0.

This placeholder exists so the gap reads as known rather than as an oversight
waiting to be found again.

**Version**: `GAME_CONFIG.VERSION` `"0.2.2"` → `"0.2.3"`

---

## v0.2.2 — Structural reorganization pass

Pure layout/reorg pass. No gameplay, balance, or rendering behavior changed.

**Summary**
The file's ARCHITECTURE comment documents an intended section order and
grouping rule ("ACTIONS grouped by system, as contiguous blocks"), but the
actual code had drifted from it — three sections were fragmented into
separate chunks scattered across the file. This pass makes the physical
layout match the documented architecture.

**Sections merged into single contiguous blocks**
- **INVENTORY / ITEM SYSTEM** — previously split into 3 chunks (pool/lookup
  helpers, quantity-transfer actions, item-detail action list) with WORLD
  INTERACTION, SURVIVAL/TIME SIMULATION, CRAFTING, and FIRE/COOKING sitting
  between them. Now one contiguous section, internal order preserved:
  1. pool/lookup helpers (`totalWeight` … `hasWatch`)
  2. quantity-transfer actions (`normalizeQty`, `doTake`, `doStore`,
     `doConsume`, `doEquip`, `doUnequip`)
  3. `getItemActions`
- **WORLD INTERACTION** — previously split into 2 chunks (lookup helpers,
  actions) with SURVIVAL/TIME SIMULATION and STAMINA/FATIGUE sitting between
  them. Now one contiguous section:
  1. lookup helpers (`doorsForRoom` … `getExitsForRoom`)
  2. actions (`doMove` … `doUnlockContainer`)
- **SURVIVAL / TIME SIMULATION** — previously split into 2 chunks with the
  entire STAMINA/FATIGUE SYSTEM sandwiched between them. Now one contiguous
  section, with STAMINA/FATIGUE folded in as an explicit sub-block (its own
  subheader comment retained):
  1. `applyHungerThirst`, `applyWorldTicking`, `applyEnergyBaseline`,
     `checkGameOver`
  2. STAMINA/FATIGUE SYSTEM sub-block (`applyExertion`,
     `isExertionDelayActive`, `energyRecoveryMultiplier`,
     `staminaMaxForEnergy`, `hungerThirstRecoveryPenalty`,
     `fatigueRecoveryAllowed`, `recoveryStep`, `sleepAvailable`,
     `estimateSleepMinutes`)
  3. `runAwakeStep`, `advanceTime`
  - The duplicate "SURVIVAL / TIME SIMULATION" banner that previously
    re-introduced the second fragment was removed, since the section is now
    a single contiguous block (each top-level header now appears exactly
    once, per the file's own contiguity rule).

**Function relocation**
- `doRestart` moved out of SURVIVAL/TIME SIMULATION (where it sat next to
  `advanceTime`) and into **PERSISTENCE**, placed directly after
  `applyLoadedData`. Rationale: it resets/reinitializes game state — the
  same kind of whole-state replacement `applyLoadedData` does on load —
  rather than a time-driven update. Implementation unchanged.

**Sections left untouched** (already contiguous, correct order)
CONFIG/CONSTANTS, WORLD DATA, PLAYER STATE, CORE UTILITIES, CRAFTING,
FIRE/COOKING, PERSISTENCE (aside from the `doRestart` insertion above),
EVENTS/UI HELPERS, RENDERING.

**Documentation**
- ARCHITECTURE comment updated:
  - Version reference bumped from 0.2.1 to 0.2.2.
  - Added a note that STAMINA/FATIGUE is a sub-section living inside
    SURVIVAL/TIME SIMULATION, not a separate top-level section (to prevent
    future passes from re-splitting it out).
  - Added a note that `doRestart` lives in PERSISTENCE, not SIMULATION,
    since it performs a full state reset rather than a time-driven update.
  - The "_uid is the stable identity" paragraph and the CONTENT vs
    MECHANICS guidance were left as-is (still accurate).

**Explicitly NOT changed**
- No function implementation, name, or variable was changed.
- No rendering logic changed.
- No functions were reordered *within* a section beyond what was needed to
  merge fragments together.
- No save format / version-compat logic changed beyond the version string.
- No new mechanics, tags, items, rooms, or content were added.
- No new abstractions, helper layers, or data refactors were introduced.
- No balance constants (`GAITS`, `DECAY`, etc.) were changed.

**Validation performed**
- Extracted script passes `node --check` with no syntax errors.
- Full non-blank-line multiset diff against 0.2.1 confirms the only content
  differences are: the version string, the three ARCHITECTURE comment
  additions listed above, and removal of the one duplicate section banner —
  everything else is a pure line-level move, no changed lines within any
  moved function body.
- Confirmed each of the twelve top-level section headers appears exactly
  once, in the documented order, with no other top-level header nested
  inside a section's span.

**Version**: `GAME_CONFIG.VERSION` `"0.2.1"` → `"0.2.2"`

---

## v0.2.1 — Stamina & Fatigue System

**New**
- Two new persistent vitals: **Stamina** (0–100, visible) and **Fatigue**
  (0–100, hidden).
- Strenuous actions now declare an **Exertion** amount; Stamina absorbs it
  first, and any excess spills into Fatigue. Exertion is not a stat itself —
  it's resolved once, right after a task completes.
- New dedicated Stamina/Fatigue module owns all the rules below. Tasks still
  just declare Exertion; they don't contain Stamina logic themselves.

**Exertion costs**
- Tree chopping: 30 Exertion.
- Fishing: 8 Exertion.
- Jogging: 0.5 Exertion/minute while moving at the "fast" gait. Walking
  costs nothing.
- Exertion is applied only after a task successfully completes — never at
  task start, never mid-task, and never on failure.

**Stamina recovery**
- Baseline recovery: 1 Stamina/minute while awake.
- Recovery only begins after 1 full game minute with no exertion; any
  completed exertive action resets that delay.
- Recovery speed scales with Energy (100% at Energy 80–100, down to 25% at
  Energy 0–19).
- Low Energy also caps the *maximum* Stamina you can currently recover to
  (100 above Energy 40, 80 at Energy 20–39, 50 below Energy 20). This cap is
  temporary and never forcibly reduces Stamina you already have.
- Low Hunger and low Thirst each cut recovery speed by 15%, stacking
  additively (up to -30% when both are low).

**Fatigue recovery**
- Fatigue recovers continuously at 0.5/minute, but only once Stamina has
  reached its current (Energy-capped) maximum.
- Fatigue recovery is impossible while Energy is below 20.
- Fatigue never directly damages Health. At Fatigue 100, movement is
  restricted to Sneaking until it drops.

**Energy changes**
- Awake baseline Energy depletion is now 100 → 0 over 24 game hours
  (previously ~16 hours).
- Active Stamina recovery now costs Energy at 2× the awake baseline; active
  Fatigue recovery costs 4×. This is on top of normal baseline drain, not a
  replacement for it.

**Rest (reworked)**
- Rest still lasts exactly 1 game hour.
- Rest now recovers Stamina/Fatigue at a flat 0.5 Stamina/minute *without*
  the extra recovery-related Energy cost.
- Rest no longer restores Energy directly — only Sleep does. Baseline
  Energy drain still applies during Rest.

**Sleep (reworked)**
- Sleep is now a fully separate simulation state: normal awake Energy
  depletion, Stamina recovery, and Fatigue recovery are all suspended while
  asleep.
- Sleep duration is no longer fixed at 8 hours — it's derived from how much
  Energy is missing, at a rate of 10 Energy/hour.
- If Fatigue is present when Sleep begins, it's snapshotted and temporarily
  caps how high Energy can recover that night
  (`ceiling = 100 − Fatigue at sleep start`).
- Fatigue always fully resets to 0 by the time you wake, regardless of the
  snapshot.
- After waking, Sleep is unavailable again for 8 game hours.

**UI**
- Stamina is now shown in the stats panel as a whole number, alongside
  Hunger/Thirst/Energy/Health.
- Fatigue remains hidden from normal gameplay UI (no debug panel exists in
  this build to expose it through).
- The Sleep button now shows its actual estimated duration instead of a
  fixed time, and is replaced with a note when Sleep isn't available yet
  (still on cooldown).
- Gait switching is locked to Sneak whenever Fatigue is at 100.

**Notes / assumptions**
- No "low Hunger/Thirst" threshold existed anywhere in the prior build to
  inherit, so this pass introduces one explicit value (30) used for both —
  easy to retune later if needed.
- All existing v0.1.3 systems (tasks, inventory, movement, crafting, fire,
  save/load) are unchanged apart from the specific hooks listed above.

**Version**: `GAME_CONFIG.VERSION` `"0.1.3"` → `"0.2.1"`

---

## v0.1.3

**Fixed**
- **"Take 1" disappearing bug** (root cause of the reported
  `Cannot read properties of undefined (reading 'qty')` class of errors):
  splitting a stack copied `_uid` onto the new stack via `{ ...item }`, so
  the moved portion and the remainder briefly shared one uid. The detail
  panel would then resolve to the wrong copy and show a stale quantity.
  Fixed by stripping `_uid` whenever `addToList()` creates a new stack
  entry, so every split stack gets its own fresh id on demand.

**Hardened**
- Added `getItemAt(list, index)` — safe list lookup that returns `null`
  instead of throwing when an index is stale or out of range.
- Added `normalizeQty(requested, available)` — explicit quantity
  resolution (`qty == null ? available : qty`) replacing the ambiguous
  `qty || it.qty` pattern; rejects 0, negative, NaN, non-integer, and
  over-limit values.
- `doTake`, `doStore`, `doConsume`, and `doEquip` now resolve their source
  item defensively via `getItemAt` and bail out safely if it's gone,
  instead of assuming the array index is still valid.
- `getItemActions()` now resolves its item via `getItemAt` as well, so it
  can no longer throw on a stale `list[index]`.
- Transfers remain atomic: capacity/destination checks still happen before
  any mutation, so a failed transfer changes nothing.

**Organization** (no behavior change)
- Added clear section headers throughout the script: CONFIG/CONSTANTS,
  WORLD DATA, PLAYER STATE, CORE UTILITIES, INVENTORY/ITEM SYSTEM, WORLD
  INTERACTION, SURVIVAL/TIME SIMULATION, CRAFTING, FIRE/COOKING,
  PERSISTENCE, EVENTS/UI HELPERS, RENDERING.
- Added an architecture comment near the top of the script explaining the
  data-driven design, the content-vs-mechanics split, and the uid-vs-index
  identity rule.
- Documented the ROOM, CONTAINER, EXIT, and ITEM data schemas inline as
  comments above `makeDefaultWorld()`.
- No changes to rendering logic, save file format, or world/item content.

**Version**: `GAME_CONFIG.VERSION` `0.1.2` → `0.1.3`
