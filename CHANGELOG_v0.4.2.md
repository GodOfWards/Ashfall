# Ashfall — Changelog

Reverse-chronological. Each entry covers one version bump. Older entries are
kept for context but should not need to be re-read for a change scoped to a
single system — see the ARCHITECTURE comment in the script for which section
owns which behavior.

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
