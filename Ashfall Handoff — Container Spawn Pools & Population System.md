# Ashfall Handoff — Container Spawn Pools & Population System

Current shipped version: v0.3.0
Implied version-change type: **MINOR** (new persistent container fields —
  `spawnPools`, `spawnRolled`, `lastRolledMinute` — require a `SAVE_KEY`
  rotation per the Handoff Guide, Part 1)
Roadmap item: Tier 3, item 15 — **partial fulfillment.** This handoff
  ships the item-spawn-pool mechanism, the full container/item tagging
  pass, and population of previously-empty containers. It does **not**
  touch the remaining sub-scope of item 15 (container property tags,
  the no-respawn flag, the actual respawn trigger, vehicle spawn pools,
  or fauna) — that stays open and has been re-scoped in the roadmap
  update accompanying this handoff.

## What this is

Replaces hand-authoring every container's contents with a data-driven,
weighted RNG pool system. A new `SPAWN_POOLS` registry (23 pools, sibling
to `ITEM_REGISTRY`) defines what each *category* of container can spawn;
every regular container in the game (`carContainers` excluded — see
Explicitly out of scope) gets tagged with one or more pools via a new
`spawnPools` field. The roll happens once, the first time a player opens
a container that has never been rolled — not at world-build time, and
not on a timer.

This also fulfills the original ask behind roadmap item 14's population
gap: the 19 previously-empty containers across Oak Apartments, Auto
Workshop, Police Station, and Riverside Freight get real, RNG-populated
contents instead of sitting empty forever. Two content gaps found during
planning are fixed alongside it: Acorn Apartments 2B was missing fixtures
its 2A twin has, and the superintendent's unit (`onebee`) had nowhere to
store clothes.

37 new `ITEM_REGISTRY` entries are added to give the pools realistic
depth, particularly in Food, Medical, and Police-flavored categories
that the existing 82-item registry didn't cover.

## Relevant existing state

Verified against the attached `ashfall_0_3_0.html`:

- **Container schema today** (per the ROOM SCHEMA / CONTAINER SCHEMA
  comment, confirmed against every container in the file): `{ id, name,
  capacityKg, items }`, optionally `locked` + `breakTag`. No
  `spawnPools`, `spawnRolled`, or `lastRolledMinute` exist anywhere —
  these are net-new fields, not extensions of anything partial.
- **69 containers exist today** across the six world-builder functions:
  50 hand-placed (with real `itemsFromRegistry()` contents) and 19 empty
  (`items:[]`) in the four newest buildings. This handoff adds 5 more
  (see Data / schema changes), bringing the total to 74.
- **No RNG spawn/respawn system of any kind exists.** The only two
  `Math.random()` calls in the file are the illness-chance roll on
  consumption (`doTake`-adjacent code) and the fishing success roll in
  `doFish()`.
- **Container tabs have no mechanic behind them today.** Each container
  tab's click handler in `renderWorldItemsPanel()` (RENDERING) currently
  does only `state.worldTab = key; render();` — no function call, no
  rule. This handoff adds the first one.
- **The backfill pattern is established** — `resyncUidCounter()`,
  `backfillItemIds()`, `backfillLocationIds()` all run together in
  `applyLoadedData()` (PERSISTENCE). This handoff's `backfillContainerFields()`
  follows the same shape and gets wired into the same call site.
- **`ITEM_REGISTRY` has 82 entries today**, categorized: Materials (17),
  Misc (15), Tool (13), Food (9), Medical (9), Clothing (6), Electronics
  (5), Literature (5), Key (2), Container (1). Food and Medical are both
  thin relative to how many pools need them, which is why most of the 37
  new items land in those two categories.
- **`master_key`** (`{ masterKey:true, building:"acorn" }`) is hand-placed
  once, on `onebee`'s Desk. It unlocks every door in Acorn Apartments.
  **This handoff does not touch it** — see Notes/assumptions for why a
  pool-based safety net for this item was considered and rejected.
- **No region/town concept exists in the data model.** `LOCATIONS` is
  flat coordinates with no grouping above individual rooms; `building`
  is a display string only. This matters only insofar as it's *why* the
  respawn-trigger portion of roadmap item 15 is explicitly out of scope
  here (see below) — this handoff's mechanism doesn't need a town concept
  to function, since the initial roll needs no notion of leaving/entering
  anything.
- **`ITEM_REGISTRY` has a probable naming duplicate**: `bandage`
  (singular) and `bandages` (plural), both Medical, both 0.05 kg. Not
  touched by this pass — flagged as new roadmap Tier 0 item 16 instead.

## Rules / mechanics

### `SPAWN_POOLS` shape

```js
const SPAWN_POOLS = {
  <poolId>: {
    entries: [
      { itemId:"<id>", weight:<int>, qtyMin:<int>, qtyMax:<int> },
      ...
    ],
    rollCount: [<min>, <max>],   // how many entries get picked per roll
    emptyChance: <0-1>           // chance the whole roll produces nothing
  },
  ...
};
```

- `weight` is a plain relative integer (no sum constraint) — picks which
  entries get selected.
- `qtyMin`/`qtyMax` is per-entry, independent of `weight` — decides how
  many of that item spawn once it's picked (e.g. `bottled_water` might
  pick 1–3 at once).
- `rollCount` decides how many *entries* (not items) get picked from the
  pool in one roll. Duplicate picks of the same entry within one roll are
  allowed by this spec (see Design decisions below for how the coding
  session should resolve the resulting duplicate `itemId` question).
- `emptyChance` is rolled once per pool per container-open, independent
  of `rollCount` — if it hits, that pool contributes nothing this time,
  regardless of `rollCount`.

### Container-side field

```js
spawnPools: ["kitchen_perishable", "kitchen_tools"]
```

- Optional. Absence means the container is never touched by this system
  at all — purely hand-authored, exactly as today.
- Always an array, even for single-pool containers (most containers in
  this pass carry 1–2 pools; a few carry none because they're intentionally
  hand-curated exceptions — there are none of those in this pass, but the
  field shape supports it for future containers).
- When present, each pool in the array **rolls independently** — its own
  `rollCount` and `emptyChance` — and results concatenate into the
  container's `items`. This is deliberate: a dumpster's `trash` roll and
  its `kitchen_perishable` roll are separate chances, not one shared
  weighted table, so adding a pool to a container never changes another
  pool's odds.

### Trigger: roll-on-first-open, not world-build, not lazy-on-render

New function in WORLD INTERACTION, `doOpenContainer(room, container)`,
called from the container tab's click handler instead of the handler
directly mutating `state.worldTab`:

```js
function doOpenContainer(room, container){
  state.worldTab = container.id;
  if(container.spawnPools && !container.spawnRolled){
    container.spawnPools.forEach(poolId => {
      const pool = SPAWN_POOLS[poolId];
      if(!pool) return; // defensive — see Hardened note below
      if(Math.random() < pool.emptyChance) return;
      const rollCount = randInt(pool.rollCount[0], pool.rollCount[1]);
      for(let i=0; i<rollCount; i++){
        const entry = weightedPick(pool.entries); // by `weight`
        const qty = randInt(entry.qtyMin, entry.qtyMax);
        addToList(container.items, ...itemsFromRegistry([{ id:entry.itemId, qty }]));
      }
    });
    container.spawnRolled = true;
    container.lastRolledMinute = state.totalMinutes;
  }
  render();
}
```

(`weightedPick`/`randInt` are small new UTILITIES helpers, not existing
functions — name them however fits the existing utility-naming
convention.) The exact function signature/body above is illustrative of
the *rule*, not a mandate to copy verbatim — the coding session should
fit it to the file's actual helper conventions, but the **behavior**
(roll-once-per-container, independent per-pool rolls, `spawnRolled` gate,
`lastRolledMinute` stamp) is not negotiable.

- This is why RENDERING never contains this rule: the click handler in
  `renderWorldItemsPanel()` must call `doOpenContainer(room, c)` instead
  of setting `state.worldTab` directly, keeping the rule in WORLD
  INTERACTION per the ARCHITECTURE comment's separation of concerns.
- Containers **without** `spawnPools` are entirely unaffected — the `if`
  guard means hand-authored-only containers never enter this code path.
- Containers **with** `spawnPools` but already carrying hand-placed
  content (all 50 of the pre-existing populated containers, after this
  pass reviews/retags them) get `spawnRolled:true` set at **authoring**
  time (in the world-data literal itself, not by this function) — so
  `doOpenContainer` never overwrites hand-placed loot with an RNG roll.
  The pools on these containers exist so a *future* respawn cycle
  (roadmap item 15, not this pass) has something to draw from later —
  they are inert under this handoff alone.
- Only the 19 previously-empty containers (plus the 5 new ones this pass
  adds) ship with `spawnRolled` absent/`false`, so only those roll the
  first time a player opens them.

### Auto-inference table (authoring aid, not runtime code)

This is WORLD DATA, used only while authoring the container definitions
below — it is not a runtime lookup the game needs at play time, since
every container's final `spawnPools` value is written directly into its
literal. Included here so the reasoning is traceable, per the "no
duplicated source of truth" principle not applying to one-time authoring
decisions.

| Container type (by name) | Pools |
|---|---|
| Stove | `kitchen_perishable`, `kitchen_tools` |
| Cabinets (kitchen) | `kitchen_nonperishable`, `kitchen_tools` |
| Kitchen drawers | `kitchen_tools` |
| Fridge | `kitchen_perishable` |
| Pantry | `kitchen_nonperishable` |
| Kitchen Shelf / Kitchenette Shelf / Kitchenette Cabinet | `kitchen_nonperishable`, `kitchen_tools` |
| Medicine cabinet | `medical_otc`, `hygiene` |
| Under-sink cabinet | `hygiene` |
| Closet | `clothing` |
| Nightstand | `residential_personal`, `documents_lore` |
| Dresser | `clothing`, `residential_personal` |
| Storage bin | `fuel_fire`, `tools_general` |
| Half-packed Bag | `clothing`, `residential_personal` |
| Shelf (residential) | `recreation`, `residential_personal` |
| TV Stand | `recreation`, `residential_personal` |
| Bookshelf | `recreation`, `documents_lore` |
| Open Suitcase | `clothing`, `residential_personal` |
| Tool Cabinet | `tools_general`, `tools_workshop` |
| Desk | `office_supplies`, `documents_lore` |
| Filing Cabinet | `office_supplies`, `documents_lore` |
| Dumpster | `trash`, `fuel_fire` |
| Tool Wall / Hardware Bins | `hardware_store`, `tools_general` |
| Paint Aisle | `hardware_store`, `tools_workshop` |
| Workbench | `tools_workshop` |
| Parts Shelf | `tools_workshop`, `warehouse_goods` |
| Pallet Rack | `warehouse_goods` |
| Front Desk (police) | `office_supplies`, `police_gear` |
| Locker Room (police) | `police_gear`, `clothing` |
| Evidence Locker | `police_evidence` |
| Safe | `valuables`, `documents_lore` |

Per-instance overrides (building context beats the type default):

| Container | Pools |
|---|---|
| Cornerstore Shelves | `retail_stock_food`, `retail_stock_general` |
| Cornerstore Register | `valuables`, `retail_stock_general` |
| Cornerstore Storage Room | `retail_stock_food`, `retail_stock_general` |
| Pharmacy Counter | `medical_pharmacy` |
| Pharmacy Shelves | `medical_otc` |
| Pharmacy Back Room | `medical_pharmacy`, `medical_otc` |
| Pharmacy-apt Cabinet | `kitchen_nonperishable` |
| Storage Unit 1 | `outdoor_camping` |
| Storage Unit 2 | `recreation`, `residential_personal` |
| Storage Unit 3 | `outdoor_camping` |

## Design decisions to make during implementation

- **Duplicate `itemId` within one roll** — if a single container's roll
  picks the same entry twice (e.g. two separate `bottled_water` picks in
  one `kitchen_nonperishable` roll), the coding session decides whether
  they merge into one stacked entry or remain separate list entries, and
  records which in the changelog's Notes/assumptions section. Recommended
  default: merge, since `Food` is already in `STACKABLE` and merging
  matches how the inventory already treats stacks elsewhere — but this is
  a narrow call, not a scope question.
- **Helper function names** (`weightedPick`, `randInt`) — name to fit
  existing UTILITIES conventions; the pseudocode above is illustrative,
  not a mandated signature.

## Data / schema changes

**New container-instance fields** (CONTAINER SCHEMA, optional):
- `spawnPools: string[]` — pool ids this container draws from.
- `spawnRolled: boolean` — whether the initial roll has happened (or, for
  containers with pre-existing hand-placed content, set `true` at
  authoring time so they're never auto-rolled).
- `lastRolledMinute: number` — `state.totalMinutes` at the moment of the
  last roll. Unused by any mechanic in this pass; exists so the future
  respawn-cycle work (roadmap item 15) has a timestamp to compare against
  without needing its own backfill later.

**New top-level registry**: `SPAWN_POOLS` (23 pools — full tables below),
sibling to `ITEM_REGISTRY`, placed in WORLD DATA immediately after it.

**New `ITEM_REGISTRY` entries** (37 — full list below).

**New PERSISTENCE function**: `backfillContainerFields()`, following the
`backfillItemIds()`/`backfillLocationIds()` pattern — for any loaded
container missing `spawnRolled` where the default world's matching
container has `spawnPools`, set `spawnRolled` to match the default
world's value (so an old save's already-populated container doesn't
suddenly become eligible for an auto-roll it was never meant to get, and
so an old save's still-empty container *does* get a chance to roll on
next open). Wire it into `applyLoadedData()` alongside the other three
backfills.

## In scope

1. `SPAWN_POOLS` registry — all 23 pools, full weighted tables (below).
2. 37 new `ITEM_REGISTRY` entries (below), realistic `unitWeight` values
   cross-referenced against the existing 82-item registry.
3. `spawnPools` tagging on **every one of the 74 final containers**
   (69 existing + 5 new) per the tables below — this is a full-map
   retrofit, not limited to the four newest buildings.
4. Review and, where needed, adjust the **existing hand-placed contents**
   of all 50 previously-populated containers so their authored contents
   are thematically consistent with the pool(s) they're now tagged with.
   (Example of the kind of adjustment expected: if a container tagged
   `medical_otc` currently holds something that reads as pharmacy-grade,
   swap it for something that fits the OTC framing, or re-tag the
   container — the coding session should use judgment here and note any
   changes made, per the Project Guide's "judgment calls get flagged"
   principle.)
5. `doOpenContainer()` new function (WORLD INTERACTION) + rewiring the
   container-tab click handler in `renderWorldItemsPanel()` to call it.
6. `backfillContainerFields()` (PERSISTENCE), wired into `applyLoadedData()`.
7. Acorn Apartments 2B parity fix: add **Fridge** (`kitchen_perishable`),
   **Pantry** (`kitchen_nonperishable`) to `twobee_kitchen`; **Under-sink
   cabinet** (`hygiene`) to `twobee_bathroom`; **Dresser** (`clothing`,
   `residential_personal`) to `twobee_bedroom`. All four ship empty
   (`spawnRolled` absent) so they populate on first open.
8. Superintendent's unit (`onebee`) gets a new **Closet** (`clothing`),
   same treatment.
9. `GAME_CONFIG.VERSION` bump (MINOR) and `SAVE_KEY` rotation.

## Explicitly out of scope

- **`carContainers` (vehicle trunk/glovebox) spawn pools.** Deliberately
  excluded from the retrofit to avoid inflating this pass's scope —
  tracked as part of roadmap item 15.
- **The respawn trigger itself** (time-based reroll after the player
  leaves and returns to town). This pass only builds the *initial*
  roll-on-first-open. `lastRolledMinute` is stamped now so that future
  work has data to compare against, but nothing in this pass reads it.
  Tracked in roadmap item 15.
- **Region/town data model.** Not needed for this pass and not built
  here. Needed for the item above.
- **Container property tags** (`equippable`/`movable`/`disassemblable`)
  and the **no-respawn flag**. Fully separate concept from `spawnPools`
  — not touched. Tracked in roadmap item 15, including a newly-found
  design collision (`equippable` vs. the existing item-side equip
  mechanism) documented there.
- **Fauna alive/dead spawning.** Not built. Tracked in roadmap item 15.
- **`master_key` as a pool entry.** Explicitly considered and rejected
  during planning — see Notes/assumptions. It remains purely hand-placed
  on `onebee`'s Desk, with no pool safety net. If a player loses it, it
  is permanently lost; this is intentional.
- **The `bandage`/`bandages` naming duplicate.** Found during this
  pass's registry audit but not fixed here — tracked as new roadmap
  Tier 0 item 16.
- **Any new rooms or buildings.** This pass only adds containers to
  rooms that already exist.

## Sections touched

- **WORLD DATA** — all six world-builder functions (every container
  definition gets a `spawnPools` field; 5 new containers added across
  two of them), plus the new `SPAWN_POOLS` registry and 37 new
  `ITEM_REGISTRY` entries.
- **WORLD INTERACTION** — new `doOpenContainer()` function.
- **PERSISTENCE** — new `backfillContainerFields()`, wired into
  `applyLoadedData()` alongside the existing three backfills.
- **RENDERING** — `renderWorldItemsPanel()`'s container-tab click handler
  changes from directly setting `state.worldTab` to calling
  `doOpenContainer(room, c)`. No other rendering logic changes; this is
  content-and-mechanics work, not a UI redesign.
- **UTILITIES** — new small helpers (`weightedPick`, `randInt` or
  equivalent), per Design decisions above.

This pass is a mix of **content** (container/item definitions) and a
**small, genuinely new mechanic** (the roll-on-open system) — not a
pure content pass. Per the Project Guide, this is the correct exception
to "content passes touch WORLD DATA only," since populating containers
via RNG requires the roll logic to exist somewhere.

## UI changes

None. The 19 previously-empty containers will show contents after their
first open where they showed none before; no new buttons, panels, or
labels are introduced by this pass.

## Dependencies / roadmap linkage

Fulfills the item-spawn-pool portion of Tier 3 item 15 (roadmap updated
alongside this handoff to reflect the narrower remaining scope). Also
surfaces new roadmap Tier 0 item 16 (`bandage`/`bandages` naming
duplicate) — unrelated cleanup, not fixed in this pass.

## Open questions for Tom

None. Every decision that came up during planning was resolved in
conversation — this handoff is ready to build from as-is.

## Notes on decisions made during planning (for the changelog's
Notes/assumptions section to reference)

- **`master_key` was initially proposed as a pool entry** (in a
  since-removed `super_unit_keys` pool) so a lost master key could be
  recovered via a future respawn cycle. **Rejected** — a unique,
  building-defining key should not be RNG-recoverable; if it's lost,
  it's lost. It stays purely hand-placed, exactly as today.
- **Acorn Apartments 2B's furniture gap** (missing Fridge, Pantry,
  Under-sink cabinet, Dresser relative to 2A) was found by comparing
  identical exit distances/layout between the two units and is treated
  as an authoring gap, not an intentional "this tenant left in a hurry
  and took the fridge" narrative choice — confirmed with Tom.
- **Full-map retrofit scope** (tagging all 50 existing hand-placed
  containers, not just the 19 empty ones) was a deliberate scope
  expansion made during planning, specifically so existing containers
  become eligible for the *future* respawn cycle without a second
  retrofit pass later.

## After implementation

Write the `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, referencing this
handoff by filename. Record the duplicate-`itemId` resolution and any
hand-placed-content adjustments made during the review step in
Notes/assumptions. Confirm in the Documentation section that roadmap item
15 was already updated by this handoff's accompanying planning session
(no further roadmap edits needed for what this pass shipped) and that
item 16 was added, not fixed, by that same session.

---

# Appendix A — Full `SPAWN_POOLS` Tables

Format per entry: `itemId — weight / qtyMin–qtyMax`.

**kitchen_perishable** — `rollCount:[0,1]`, `emptyChance:0.3`
rotten_leftovers — 8/1 · spoiled_milk — 6/1 · moldy_bread — 6/1 ·
rotten_produce — 5/1 · pot_of_spoiled_stew — 4/1 · raw_fish — 1/1 ·
cooked_fish — 1/1

**kitchen_nonperishable** — `rollCount:[1,3]`, `emptyChance:0.1`
canned_soup — 8/1–2 · bottled_water — 8/1–3 · canned_beans — 7/1–2 ·
canned_corn — 7/1–2 · canned_tuna — 6/1–2 · crackers — 6/1 · pasta — 6/1 ·
granola_bars — 6/1–3 · potato_chips — 5/1–2 · rice_bag — 5/1 ·
cereal_box — 5/1 · peanut_butter — 4/1 · coffee_grounds — 4/1

**kitchen_tools** — `rollCount:[0,2]`, `emptyChance:0.25`
can_opener — 7/1 · frying_pan — 6/1 · kitchen_knife — 6/1 ·
dented_saucepan — 4/1 · burnt_saucepan — 3/1

**hygiene** — `rollCount:[1,2]`, `emptyChance:0.15`
toilet_paper — 8/1–2 · bar_soap — 7/1 · toothpaste — 6/1 · shampoo — 5/1 ·
bleach — 4/1 · hand_sanitizer — 4/1

**medical_otc** — `rollCount:[1,2]`, `emptyChance:0.2`
bandages — 8/1–3 · painkillers — 6/1 · aspirin — 6/1 ·
cold_medicine — 5/1 · antiseptic_wipes — 5/1 · gauze_rolls — 4/1 ·
childrens_medicine — 2/1

**medical_pharmacy** — `rollCount:[1,2]`, `emptyChance:0.15`
prescription_bottles — 7/1 · strong_painkillers — 6/1 ·
antibiotics — 6/1 · vitamins — 5/1 · cough_syrup — 5/1 ·
rubbing_alcohol — 5/1

**residential_personal** — `rollCount:[1,2]`, `emptyChance:0.2`
crumpled_cash — 7/1 · spare_batteries — 6/1–2 · loose_change — 6/1 ·
wristwatch — 3/1 · jewelry_piece — 2/1

**clothing** — `rollCount:[1,2]`, `emptyChance:0.15`
folded_clothes — 8/1–2 · t_shirt — 7/1 · jeans — 6/1 · work_gloves — 5/1 ·
winter_jacket — 4/1 · sturdy_boots — 4/1 · work_boots — 4/1

**documents_lore** — `rollCount:[0,2]`, `emptyChance:0.3`
handwritten_note — 6/1 · old_photographs — 5/1 · photo_album — 4/1 ·
registration_papers — 3/1 · owners_manual — 3/1 · building_ledger — 2/1

**recreation** — `rollCount:[0,2]`, `emptyChance:0.25`
board_games — 6/1 · paperback_novel — 6/1 · playing_cards — 5/1 ·
comic_book — 4/1

**tools_general** — `rollCount:[1,2]`, `emptyChance:0.15`
duct_tape — 8/1 · nails — 6/1–3 · rope — 6/1 · length_of_rope — 5/1 ·
wrench — 5/1 · crowbar — 2/1

**tools_workshop** — `rollCount:[1,2]`, `emptyChance:0.2`
wrench — 6/1 · metal_pipe — 5/1 · box_cutter — 5/1 ·
spare_parts_box — 5/1 · motor_oil — 5/1 · tire_iron — 4/1 ·
bolt_cutters — 2/1 · hand_axe — 2/1 · propane_torch — 1/1

**office_supplies** — `rollCount:[0,2]`, `emptyChance:0.25`
building_ledger — 5/1 · registration_papers — 4/1 · reading_lamp — 4/1 ·
owners_manual — 4/1 · portable_radio — 2/1

**retail_stock_food** — `rollCount:[1,3]`, `emptyChance:0.1`
bottled_water — 8/1–3 · candy_bar — 7/1–2 · potato_chips — 7/1–2 ·
canned_corn — 6/1–2 · canned_soup — 6/1–2 · granola_bars — 6/1–2 ·
chewing_gum — 6/1

**retail_stock_general** — `rollCount:[1,2]`, `emptyChance:0.15`
candy_bar — 7/1 · chewing_gum — 7/1 · loose_change — 6/1 · lighter — 4/1

**hardware_store** — `rollCount:[1,3]`, `emptyChance:0.1`
nails — 8/1–3 · duct_tape — 8/1–2 · rope — 7/1 · plank — 6/1–2 ·
paint_can — 5/1 · wrench — 5/1 · crowbar — 3/1 · bolt_cutters — 2/1 ·
hand_axe — 2/1 · propane_torch — 2/1

**outdoor_camping** — `rollCount:[1,2]`, `emptyChance:0.2`
sleeping_bag — 4/1 · tackle_box — 4/1 · water_purification_tablets — 4/1 ·
camping_tent — 3/1 · fishing_rod — 3/1 · compass — 3/1

**valuables** — `rollCount:[0,1]`, `emptyChance:0.35`
crumpled_cash — 6/1 · jewelry_piece — 4/1 · cash_bundle — 3/1 ·
wristwatch — 3/1

**police_evidence** — `rollCount:[0,1]`, `emptyChance:0.4`
evidence_bag — 6/1 · sealed_evidence_box — 3/1

**police_gear** — `rollCount:[1,2]`, `emptyChance:0.2`
police_uniform — 5/1 · handcuffs — 4/1 · police_badge — 2/1

**warehouse_goods** — `rollCount:[1,2]`, `emptyChance:0.2`
scrap_metal — 6/1–2 · metal_pipe — 6/1 · plank — 6/1–2 ·
spare_machine_parts — 5/1

**trash** — `rollCount:[0,2]`, `emptyChance:0.4`
empty_soda_can — 7/1 · scrap_metal — 6/1 · metal_pipe — 5/1 ·
rotten_leftovers — 5/1 · dead_potted_plant — 3/1

**fuel_fire** — `rollCount:[1,2]`, `emptyChance:0.15`
firewood — 8/1–3 · box_of_matches — 6/1 · lighter — 5/1 ·
campfire_kit — 2/1

---

# Appendix B — New `ITEM_REGISTRY` Entries (37)

Weight anchors reference existing registry items of comparable real-world
mass (see Relevant existing state).

**Food** (verb:"Eat" + `restores` only where edible without cooking —
mirrors the existing `pasta`-has-neither / `canned_soup`-has-both split)
```
canned_tuna:    { name:"Canned tuna", category:"Food", unitWeight:0.4, restores:{hunger:20}, verb:"Eat" }
cereal_box:     { name:"Box of cereal", category:"Food", unitWeight:0.5, restores:{hunger:15}, verb:"Eat" }
crackers:       { name:"Crackers", category:"Food", unitWeight:0.2, restores:{hunger:8}, verb:"Eat" }
peanut_butter:  { name:"Peanut butter", category:"Food", unitWeight:0.5, restores:{hunger:20}, verb:"Eat" }
candy_bar:      { name:"Candy bar", category:"Food", unitWeight:0.05, restores:{hunger:5}, verb:"Eat" }
rice_bag:       { name:"Bag of rice", category:"Food", unitWeight:1.0 }
coffee_grounds: { name:"Coffee grounds", category:"Food", unitWeight:0.3 }
spoiled_milk:   { name:"Spoiled milk", category:"Food", unitWeight:1.0 }
moldy_bread:    { name:"Moldy bread", category:"Food", unitWeight:0.4 }
rotten_produce: { name:"Rotten produce", category:"Food", unitWeight:0.5 }
```

**Hygiene / Medical**
```
bar_soap:          { name:"Bar of soap", category:"Materials", unitWeight:0.1 }
toothpaste:        { name:"Toothpaste", category:"Materials", unitWeight:0.1 }
shampoo:           { name:"Shampoo", category:"Materials", unitWeight:0.3 }
hand_sanitizer:    { name:"Hand sanitizer", category:"Materials", unitWeight:0.15 }
cold_medicine:     { name:"Cold medicine", category:"Medical", unitWeight:0.1 }
antiseptic_wipes:  { name:"Antiseptic wipes", category:"Medical", unitWeight:0.05 }
antibiotics:       { name:"Antibiotics", category:"Medical", unitWeight:0.05 }
cough_syrup:       { name:"Cough syrup", category:"Medical", unitWeight:0.3 }
```

**Clothing / Personal**
```
t_shirt:        { name:"T-shirt", category:"Clothing", unitWeight:0.2 }
jeans:          { name:"Jeans", category:"Clothing", unitWeight:0.6 }
police_uniform: { name:"Police uniform", category:"Clothing", unitWeight:1.0 }
jewelry_piece:  { name:"Piece of jewelry", category:"Misc", unitWeight:0.02 }
cash_bundle:    { name:"Bundle of cash", category:"Misc", unitWeight:0.05 }
```

**Recreation**
```
playing_cards: { name:"Deck of playing cards", category:"Misc", unitWeight:0.1 }
comic_book:    { name:"Comic book", category:"Literature", unitWeight:0.1 }
```

**Tools / Workshop / Warehouse / Hardware**
```
spare_parts_box:      { name:"Box of spare parts", category:"Materials", unitWeight:1.5 }
motor_oil:            { name:"Motor oil", category:"Materials", unitWeight:0.9 }
spare_machine_parts:  { name:"Spare machine parts", category:"Materials", unitWeight:1.5 }
paint_can:            { name:"Can of paint", category:"Materials", unitWeight:1.5 }
```

**Retail / Fuel**
```
chewing_gum: { name:"Pack of chewing gum", category:"Misc", unitWeight:0.02 }
lighter:     { name:"Lighter", category:"Materials", unitWeight:0.05, tags:["fire-starter"], durability:{ current:80, max:80, mode:"uses" } }
```

**Outdoor**
```
compass:                     { name:"Compass", category:"Tool", unitWeight:0.1 }
water_purification_tablets:  { name:"Water purification tablets", category:"Materials", unitWeight:0.05 }
```

**Police**
```
evidence_bag:         { name:"Evidence bag", category:"Misc", unitWeight:0.05 }
sealed_evidence_box:  { name:"Sealed evidence box", category:"Misc", unitWeight:1.5 }
handcuffs:            { name:"Handcuffs", category:"Tool", unitWeight:0.3 }
police_badge:         { name:"Police badge", category:"Misc", unitWeight:0.05 }
```

---

# Appendix C — Full Container → `spawnPools` Assignment (74 containers)

### Acorn Apartments

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| living | tvstand | TV Stand | recreation, residential_personal |
| living | bookshelf | Bookshelf | recreation, documents_lore |
| kitchen | stove | Stove | kitchen_perishable, kitchen_tools |
| kitchen | cabinets | Cabinets | kitchen_nonperishable, kitchen_tools |
| kitchen | drawers | Kitchen drawers | kitchen_tools |
| kitchen | fridge | Fridge | kitchen_perishable |
| kitchen | pantry | Pantry | kitchen_nonperishable |
| bathroom | medcab | Medicine cabinet | medical_otc, hygiene |
| bathroom | undersink | Under-sink cabinet | hygiene |
| bedroom | closet | Closet | clothing |
| bedroom | nightstand | Nightstand | residential_personal, documents_lore |
| bedroom | dresser | Dresser | clothing, residential_personal |
| balcony | storagebin | Storage bin | fuel_fire, tools_general |
| twobee | packedbag | Half-packed Bag | clothing, residential_personal |
| twobee | shelf | Shelf | recreation, residential_personal |
| twobee_kitchen | stove | Stove | kitchen_perishable, kitchen_tools |
| twobee_kitchen | cabinets | Cabinets | kitchen_nonperishable, kitchen_tools |
| twobee_kitchen | drawers | Kitchen drawers | kitchen_tools |
| **twobee_kitchen** | **fridge (NEW)** | **Fridge** | **kitchen_perishable** |
| **twobee_kitchen** | **pantry (NEW)** | **Pantry** | **kitchen_nonperishable** |
| twobee_bathroom | medcab | Medicine cabinet | medical_otc, hygiene |
| **twobee_bathroom** | **undersink (NEW)** | **Under-sink cabinet** | **hygiene** |
| twobee_bedroom | closet | Closet | clothing |
| twobee_bedroom | nightstand | Nightstand | residential_personal, documents_lore |
| **twobee_bedroom** | **dresser (NEW)** | **Dresser** | **clothing, residential_personal** |
| twobee_balcony | storagebin | Storage bin | fuel_fire, tools_general |
| onea | shelf1a | Shelf | recreation, residential_personal |
| onea | tvstand1a | TV Stand | recreation, residential_personal |
| onea_kitchen | stove1a | Stove | kitchen_perishable, kitchen_tools |
| onea_kitchen | kitchen1a | Kitchen Shelf | kitchen_nonperishable, kitchen_tools |
| onea_kitchen | fridge1a | Fridge | kitchen_perishable |
| onea_bathroom | medcab1a | Medicine cabinet | medical_otc, hygiene |
| onea_bedroom | suitcase | Open Suitcase | clothing, residential_personal |
| onea_bedroom | dresser1a | Dresser | clothing, residential_personal |
| onea_patio | storagebin1a | Storage bin | fuel_fire, tools_general |
| onebee | stove | Stove | kitchen_perishable, kitchen_tools |
| onebee | toolcabinet | Tool Cabinet | tools_general, tools_workshop |
| onebee | desk | Desk | office_supplies, documents_lore |
| **onebee** | **closet (NEW)** | **Closet** | **clothing** |

### Auto Workshop

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| auto_shop | workbench | Workbench | tools_workshop |
| auto_shop | partsshelf | Parts Shelf | tools_workshop, warehouse_goods |
| auto_shop_back | desk | Desk | office_supplies, documents_lore |
| auto_shop_back | filingcabinet | Filing Cabinet | office_supplies, documents_lore |

### Main St

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| cornerstore | shelves | Shelves | retail_stock_food, retail_stock_general |
| cornerstore | register | Register Counter | valuables, retail_stock_general |
| cornerstore | storage | Storage Room | retail_stock_food, retail_stock_general |
| cornerstore_apt | dresser | Dresser | clothing, residential_personal |
| pharmacy | counter | Pharmacy Counter | medical_pharmacy |
| pharmacy | shelves | Shelves | medical_otc |
| pharmacy | backroom | Back Room | medical_pharmacy, medical_otc |
| pharmacy_apt | cabinet | Cabinet | kitchen_nonperishable |
| hardware | toolwall | Tool Wall | hardware_store, tools_general |
| hardware | bins | Hardware Bins | hardware_store, tools_general |
| hardware | paintaisle | Paint Aisle | hardware_store, tools_workshop |
| hardware_apt | shelf | Shelf | recreation, residential_personal |

### Oak Apartments

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| oak_1a | dresser | Dresser | clothing, residential_personal |
| oak_1a | kitchenette | Kitchenette Shelf | kitchen_nonperishable, kitchen_tools |
| oak_1b | dresser | Dresser | clothing, residential_personal |
| oak_1b | kitchenette | Kitchenette Cabinet | kitchen_nonperishable, kitchen_tools |
| oak_2a | dresser | Dresser | clothing, residential_personal |
| oak_2a | kitchenette | Kitchenette Shelf | kitchen_nonperishable, kitchen_tools |
| oak_2b | dresser | Dresser | clothing, residential_personal |
| oak_2b | kitchenette | Kitchenette Cabinet | kitchen_nonperishable, kitchen_tools |

### Police Station

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| police_lobby | frontdesk | Front Desk | office_supplies, police_gear |
| police_lobby | lockerroom | Locker Room | police_gear, clothing |
| police_evidence | evidencelocker | Evidence Locker | police_evidence |

### Poplar St

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| alley | dumpster | Dumpster | trash, fuel_fire |

### Riverside Freight

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| industrial_floor | palletrack1 | Pallet Rack 1 | warehouse_goods |
| industrial_floor | palletrack2 | Pallet Rack 2 | warehouse_goods |
| industrial_office | desk | Desk | office_supplies, documents_lore |
| industrial_office | safe | Safe | valuables, documents_lore |

### Water St

| Room | Container id | Name | spawnPools |
|---|---|---|---|
| storage | unit1 | Storage Unit 1 | outdoor_camping |
| storage | unit2 | Storage Unit 2 | recreation, residential_personal |
| storage | unit3 | Storage Unit 3 | outdoor_camping |

**24 containers ship empty** (`spawnRolled` absent, so each rolls on
first open): the original 19 previously-empty containers (Oak Apartments
×8, Auto Workshop ×4, Police Station ×3, Riverside Freight ×4) plus the 5
new ones this handoff adds (marked **NEW** above — 2B's Fridge/Pantry/
Under-sink cabinet/Dresser, and onebee's Closet).

**The remaining 50 containers** — all pre-existing, hand-placed content —
ship with `spawnRolled:true` set at authoring time, so `doOpenContainer()`
never overwrites their authored contents. Their `spawnPools` tags exist
only so a future respawn cycle (roadmap item 15) has something to draw
from later.
