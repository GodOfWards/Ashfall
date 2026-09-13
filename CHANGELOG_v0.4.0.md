# Ashfall — Changelog

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
- Roadmap: **not updated by this session.** No `Ashfall_Development_Roadmap_*.md`
  exists yet in this repository for this coding session to check against
  or amend — the handoff states its accompanying planning session already
  rescoped roadmap item 15 and added item 16 (the `bandage`/`bandages`
  naming duplicate), but that roadmap file itself wasn't provided
  alongside the handoff. Whoever has the current roadmap should add/confirm:
  Tier 3 item 15 narrowed to the remaining scope (vehicle spawn pools,
  the respawn trigger, region/town data model, container property tags
  + no-respawn flag, fauna spawning), and a new Tier 0 item 16 for the
  `bandage`/`bandages` naming duplicate found during this pass's registry
  audit (not fixed here).

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
