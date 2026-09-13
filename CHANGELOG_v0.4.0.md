# Ashfall — Changelog

Reverse-chronological. Each entry covers one version bump. Older entries are
kept for context but should not need to be re-read for a change scoped to a
single system — see the ARCHITECTURE comment in the script for which section
owns which behavior.

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
