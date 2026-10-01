# Ashfall Handoff — Fluid transfer: item groups and meters, water in millilitres, drinking, pouring and auto-drink

Current shipped version: v0.11.1
Implied version-change type: MINOR — one bump for the whole release, one `SAVE_KEY` rotation
Issues (closed by this release's PR):
  #134 — Item groups and level meters (Phase 1)
  #47  — Fluid transfer: carrying, pouring and measuring liquids (Phases 2–6)

## What this is

Water stops being an all-or-nothing interim state and becomes a measured
fluid. Every holder (a bottle, a saucepan, the pot, the thermos) holds a
number of millilitres of one kind of water. The player drinks it in
measured amounts, pours it between any two holders, drinks at the tap, and
drinks on their own when thirsty.

Finer levels mean more rows that look alike, so the release starts with
#134: rows of the same thing gather under one ▸ header that opens to its
stacks, and what is left of a unit shows as a smooth meter along its row.

It is **one handoff, implemented in the order below, on one branch, shipped
as one version with one changelog entry and one pull request**, the way the
cooking release and the power foundation were. Both issues' bodies are the
record of the design; everything a coding session needs from them is
restated here.

## How to work through this

- **Order is fixed.** Each phase depends on the ones before it. Don't start a
  phase until the previous phase's checks pass. Each phase leaves the game
  playable.
- **One commit (or more) per phase**, each message starting `Phase N:`,
  pushed as it is made. A session resuming the work finds the last
  `Phase N:` commit, re-runs that phase's checks, and continues from `N + 1`.
- **Checks** run in headless Chromium (Playwright is pre-installed; drive
  `ashfall.html` from a `file://` URL) and through the dev seam
  (`window.ashfallDev`). **The dev seam stays read-only.** Don't add a debug
  hook that mutates game state.
- **The replay page** (`?replay`) and the **benchmark** (`?bench`) run at the
  end of every phase from Phase 2 on; both must still pass.
- **The version bump, changelog entry and archive move happen once, in
  Phase 6.**
- **Line numbers are approximate** (v0.11.1). Find code by identifier.

## Relevant existing state

Verified against `main` at v0.11.1 (`GAME_CONFIG.VERSION = "0.11.1"`,
`SAVE_KEY = "ashfall_save_v0.11"`).

### Items, rows and stacks (INVENTORY / ITEM SYSTEM, about 5430–5560)

- `itemFromRegistry()` (~1273) deep-copies a registry entry, deletes
  `REGISTRY_ONLY_FIELDS` (~1290: `carryFactor`, `foodPoisoningChance`,
  `disassembleLog`, `cooks`, `spoils`, `holdsWater`, `vessel`, `ingredient`,
  `dish`, `fuseRating`), and applies `overrides`. **`unitWeight` is copied
  onto the instance**, so a registry weight change does not reach an existing
  save by itself.
- `itemUnitWeight()` is `unitWeight × portionOf() + waterWeightOf()` plus
  any `contents`. `waterWeightOf()`: a bottle's `holdsWater.kg × water.fill`,
  a vessel's `vessel.waterKg` when it has `water`.
- **`sameStackState()`** (~5474) is the one merge predicate: same
  `itemId` and category, a `STACKABLE` category, **no `durability`** on
  either, the same `!!sealed`, cook state (and raw `cookMinutes`), the same
  `rowFreshness()` (never `"mixed"`), the same `portionOf()`, and the same
  water kind and `water.fill`. `addToList()`, `mergeRows()`,
  `remergeRow()`, `changeOneUnit()`, `unitsOf()`, `takeUnits()` and
  `dropUnits()` are the unit helpers built on it. A row with `durability`
  never merges, so every flashlight, lighter and box of matches is its own
  row.
- **Rendering** (~11690–11870): `itemStateLabels()` gives the labels after
  a name, in order: `Open` (only `sealed === false`), Raw/Cooked, freshness
  or Frozen, then water (`Water` / `Tainted`). `itemDisplay()` shows a vessel
  holding a dish as the dish. `renderItemList(el, list, buttons, side, ctx)`
  draws one `<li>` per row: a name button (sets `detailItem = { uid, side }`),
  the state span, `×qty — kg`, `(Category)`, then the panel's buttons (the
  Inventory side's **Store** / **Place**, the Here side's **Take**, disabled
  with the keychain tab open and the item not allowed there). Each row has a
  bottom divider (`ul.itemlist li { border-bottom }`). `durabilityText()` is
  "N/M uses" for `mode:"uses"` and "N% charge — On/Off" or "No batteries
  installed" for `mode:"time"`. `renderItemPop()` shows name and labels,
  category and weight ("each"), the durability line, Sealed/Opened, a
  vessel's "Holds: …" and its "Full of water" / "Full of tainted water", then
  `getItemActions()`.
- `getItemActions(list, index, side)` (~6302): Take/Store/Place All, Half
  (from qty 3), 1 (from qty 2) for a splittable row; Eat/Drink and its
  `EAT_PARTS` parts (½, ¼) while less than what's left (`eatTarget()` picks
  the least-left unit of the same food); `vesselActions()`; "Add to the …" and
  **"Pour into the …"** for every vessel in reach (`nearbyVessels()`,
  `vesselButtonNames()`); Open; **Fill at the sink** or the note "The tap is
  dry."; Equip; keys; `batteryActions()`; Disassemble.
- `doTake(index, qty)` / `doStore(index, qty)` move units of one row of the
  current tab; capacity and load failures log "That won't fit — not enough
  room there." / "You can't carry any more." / "That won't fit there." and move
  nothing.
- `rebuildKeepingFocus()` (~10693) restores focus after a rebuild by the
  name button's `data-uid`.

### Water today (about 5950–6180, 8870–9060)

- `plastic_bottle`: `holdsWater:{ kg:0.5, restores:{thirst:30} }`,
  `verb:"Drink"`, category Food. Saucepans (`burnt_saucepan`,
  `dented_saucepan`): `vessel:{ kind:"saucepan", capacityKg:1.5, waterKg:1.0 }`;
  `cooking_pot`: `vessel:{ kind:"pot", capacityKg:3, waterKg:2.0 }`; the
  frying pan and roasting pan have `waterKg:0`. `thermos` is
  `{ name:"Thermos", category:"Misc", unitWeight:0.4 }` and does nothing.
- Instance `water: { kind, fill }` on a bottle, `water: { kind }` on a vessel
  (all or nothing). `waterKindOf()`, `holdsWaterAtAll()`, `canTakeWater()`,
  `addWater()` (taints if either is tainted, resets `boilMinutes`).
- `consumeProfile()` (~5918) is the interim Drink rule: a bottle's `left` is
  its `fill`, its restores `holdsWater.restores`, its poisoning
  `TAINTED_WATER_POISONING_CHANCE` when tainted. `eatFromRow()` takes an
  amount off; a bottle drunk dry keeps its row, empty. `consumeFromList()`
  logs "You drink the water." / "You drink some of the water." and rolls
  poisoning scaled by the amount.
- **The sink** (~5955): `canFillAtSink()`, `tapDryFor()`, `sinkLitresFor()`,
  `doFillAtSink()`: fills one unit to full while `waterRunningIn()` holds;
  off a tank (`tankOf()`, `tankLeft()`, `state.tankDrawn`) it draws the litres
  added, a bottle filling part-way on the last of it and a vessel needing its
  whole `waterKg`. A draw that moves a pumped tank's float resolves its
  building (`resolveBuilding()`). Lines: "You fill the … at the sink." / "The
  tap coughs, spits, and runs dry." Its comment says "whatever was left in the
  pipes is #47's".
- **Pouring**: `canPourInto()` / `doPourIntoVessel()` empty a whole bottle
  into a vessel ("You pour the water into the …"); `doPourOutWater()` empties
  a vessel, silently.
- **Dishes**: `templateStatus()` (~8904): `waterOk` is `t.water ? water ===
  "clean" : !water`, `waterBoils` is `t.water && water === "tainted"`.
  `buildDish(t, rows, waterKg)` adds the water's weight to the dish;
  `formDish()` passes the vessel's `waterKg`, `dishFrom()` (the world's
  spawned stews) the named vessel's registry `waterKg`, `soonestIn()` the
  vessel's `waterKg`. `dishNeedsText()` / `dishProgressText()` (~11958) say
  "with water" / "needs … water" / "the water poured out".
- `settleVessel()` boils tainted water clean after `BOIL_MINUTES`; nothing
  about volume.
- Spawn pools `kitchen_nonperishable` (~1407) and another (~1524) roll
  `plastic_bottle` with `state:{ water:{ kind:"clean", fill:1 } }`; the home
  placements (~4135, ~4213) use `overrides:{ water:{ kind:"clean", fill:1 } }`.
  `MIGRATED_ITEMS.bottled_water` (~9485) rebuilds a retired bottled water as
  a full bottle.
- The replay page puts `pot.water = { kind:"tainted" }` on a pot (~10390) and
  fills a bottle and a pot at the sink (~10437).

### Time, vitals and sleep (SURVIVAL / TIME SIMULATION)

- `clockStep(dt)` (~7689): `state.totalMinutes += dt`, `applyHungerThirst(dt)`
  (Thirst falls `DECAY.thirst` per minute, health drains at 0), then
  `processDueEvents()`. `advanceTime()`, `doRest()`, `doSleep()` are the only
  ways time passes; each ends with `settleToNow()`.
- `asleep` is true during `doSleep()`'s loop and during a blackout.
- `LOW_THIRST_THRESHOLD = 30` (~656); `hungerThirstRecoveryPenalty()` reads
  it. The vitals are clamped to 0–100 by `clamp()`.

### Persistence

- `applyLoadedData()` (~9512) runs, in order: `backfillItemIds()`,
  `backfillSlotItemIds()`, `backfillRegistryFields()` (resyncs `tags` and
  `name` from the registry), `backfillIllnessScale()`,
  `backfillInventoryCap()`, `migrateCookingRelease()` (idempotent), then
  `rebuildSchedule()`. `forEachItemList()` reaches every item list, including
  `contents`.

### The reference figures this release uses

The coding session reads neither the canon nor the reference folder; these
are quoted from `docs/canon/reference/Water_Holders.md` (checked
2026-10-01, status Secondary):

> | Mate thermos, stainless | 1000 mL | 0.6–0.7 kg | Secondary |
>
> **Thermos:** 500 mL, 750 mL, 1 L and 1.2 L are sold for mate; 1 L is the
> most common.

Tom's choice: **stainless, 1,000 mL, 0.65 kg.**

## Global rules and constants

New constants, each a balance value, retunable, defined once beside the
system that owns it:

| Constant | Value | Meaning |
|---|---|---|
| `LEVEL_WARN_BELOW` | `0.25` | A meter below this share of full draws in the warning colour. |
| `MEASURE_ML` | `250` | What **Drink** drinks and **Pour 250 mL** pours. The button's label reads its value. |
| `WATER_THIRST_PER_L` | `60` | Thirst restored per litre. Written with its derivation comment: a 500 mL bottle's 30, the rate before this release. |
| `TAINTED_WATER_DOSE_ML` | `500` | The amount `TAINTED_WATER_POISONING_CHANCE` is for; a drink's chance is that chance × ml ÷ this. |
| `VITAL_MAX` | `100` | The vitals' top, today a literal in `clamp()`; named so Drink all reads it too. |
| `DISH_WATER_MIN_SHARE` | `0.4` | A dish that needs water needs at least this share of its vessel's `capacityMl`, in clean water. |

`TAINTED_WATER_POISONING_CHANCE` (0.35) and `BOIL_MINUTES` (5) keep their
values. `EAT_PARTS` stays, for food only.

**Every fluid action takes `min(amount asked, what the source has, what the
target has room for)`**, so no button is ever greyed out for asking too
much. All amounts are whole millilitres.

---

## Phase 1 — Item groups and level meters (#134)

Rendering only: no saved field, no change to `sameStackState()` or to any
action's rules.

### The level of a unit

One helper, `unitLevel(it)`, is the single statement of what a row's meter
and its pop-up figure read. It returns `{ level, figure }` (`level` in
[0, 1]) or `null`:

- **A bottle holding water:** `level` = `water.fill`; `figure` =
  "`fill × 500` of 500 mL" (from `holdsWater.kg`, never a literal). An empty
  bottle: `null`.
- **A vessel holding water:** `level` = 1; `figure` = today's "Full of
  water" / "Full of tainted water" (that line moves here from
  `renderItemPop()`). No water, or holding a dish: `null`.
- **Food with `portion` below 1:** `level` = `portion`; `figure` = "¾ left",
  "½ left" or "¼ left". A whole unit: `null`.
- **`durability` with `mode:"uses"`** (matches, the lighter): `level` =
  `current / max`; `figure` = `durabilityText()`'s "N/M uses".
- **Anything else: `null`.** In particular `mode:"time"` devices (the
  flashlight, the radio) get no level. A device shows its level only where
  the device does so by design, and neither does.

Phase 2 rewrites the bottle and vessel cases; nothing else reads the level.

### The meter in a row

- A row whose `unitLevel()` is not null draws a **meter along its bottom
  edge, in place of its divider**: a thin bar the row's full width (inside a
  group, from the rows' indent to the right edge), filled to `level`. The
  track is the divider's colour; the fill a neutral ink colour; **below
  `LEVEL_WARN_BELOW` the fill is the warning colour** (`--warn`). A level of 0
  draws an empty track. Every meter is the same length, so levels compare
  down the list. Rows without one keep their divider.
- It is `role="meter"` with `aria-valuemin="0"`, `aria-valuemax="100"`,
  `aria-valuenow` (the level as a whole percent) and an `aria-label` of "Level".
- Thickness and colours are implementation choices, retunable; the mock in
  #134 used a 2 px line.

### `(On)`

`itemStateLabels()` adds **`On`** after the water label when `it.on` is
true. `durabilityText()` for `mode:"time"` becomes "On" / "Off", or "No
batteries installed": **the "N% charge" figure is removed.** A device dying
without warning is intended.

### Groups

- **Group key:** `itemId` (the name for an item without one), `!!sealed`,
  `cookStateOf()`, `waterKindOf()` (Phase 2: `fluidKindOf()`), and
  `rowFreshness()` (Frozen is per container, so every row in a list shares
  it). Rows sharing a key are one group. Two rows differ inside a group only
  by their level (`fill`, `portion`, `durability`), raw `cookMinutes`, or
  `on`.
- **A group of one row draws exactly as today.** Nothing else changes for it.
- **A group of two or more rows draws a header,** at the position of the
  group's first row in the list, then (when open) its rows:
  - the header: a **disclosure button** (▸ closed, ▾ open; `aria-expanded`;
    `aria-label` "Show the N stacks" / "Hide the N stacks"), the **name
    button**, the labels every row shares (the group key's: Open, cook
    state, freshness or Frozen, water kind; never `On`), `×total — total kg`,
    `(Category)`, and the panel's quick button (**Store** / **Place** /
    **Take**), which moves **the whole group**. **No meter on a header.**
  - the rows: indented under the header, each exactly as a plain row draws
    (its own labels including `On`, its own meter, its own quick button, its
    own pop-up). **Ordered least left first**: by `unitLevel().level`
    ascending, ties (and rows with no level) in list order.
- **Open or closed:** closed by default. A UI-only set, `openGroups`, beside
  `detailItem`, keyed by side, tab and group key. **Never saved**; cleared
  wherever `detailItem` is cleared on load, restart and new game.
- **Focus:** the header's name and disclosure buttons carry the group key
  (`data-group`), and `rebuildKeepingFocus()` returns focus to them the way
  it returns it to a row's `data-uid`.
- The Electrical view's filtered Inventory list groups the same way.

### The group pop-up

- Clicking a header's name opens the item pop-up on the group:
  `detailItem = { group: key, side }`, resolved fresh on every render
  against the current tab's list. When the group is down to one row, the
  pop-up shows that row's pop-up (as `{ uid, side }`); when it is gone, the
  pop-up closes.
- It shows the name and the shared labels, `Category · total kg`, and "N in M
  stacks". No meter.
- **Its actions are the stack's own, over the whole group:**
  - **Take / Store / Place All, Half, 1** over the group's total units, by
    the same rules as a row (Half from 3, rounding up; 1 from 2).
    **Units are taken least left first**, across rows in the order shown.
    **A move is all or nothing:** if the whole amount won't fit (capacity or
    load), nothing moves and the existing warning line speaks. The keychain
    rule disables them as it does a row's.
  - **Eat / Drink** and its parts, exactly as a row's: they already act on
    the least-left unit of the same food (`eatTarget()`).
  - Nothing else. Open, Fill at the sink, Add to …, Pour…, Equip,
    Disassemble and the battery controls stay on the rows.

### Checks — Phase 1

- Two bottles at different fills and one full: one header `Plastic bottle
  (Water) ×3`, closed. Opening shows the part-full rows first, each with a
  meter along its bottom edge, the full one last; a bottle at ¼ draws in the
  warning colour.
- An empty bottle shows no meter. A whole sealed can shows no meter; a
  half-eaten one does, and its pop-up says "½ left".
- Two lighters at different uses form a group; each row's meter and pop-up
  ("N/M uses") match. A lit flashlight's row reads `Flashlight (On)`; its
  pop-up says "On", with no percentage.
- Header **Take Half** on a group of 5 takes 3 units, least left first.
  Header **Take All** into a bag with no room moves nothing and logs the
  warning. Header **Drink** drinks from the least-left bottle.
- A group's open state survives a render and a tab switch, and is gone after
  a load.
- Keyboard: Tab reaches the disclosure button; Enter toggles it; focus stays
  on it after the rebuild. A screen reader announces the meter's value.
- `serializeGame()` output is byte-identical before and after opening groups.

---

## Phase 2 — Water in millilitres (#47)

### Definitions (ITEM DATA SCHEMA, WORLD DATA)

- **New registry field `holdsFluid: { capacityMl }`**, definition data
  (add it to `REGISTRY_ONLY_FIELDS` in `holdsWater`'s place):
  - `plastic_bottle`: `holdsFluid:{ capacityMl:500 }`; `holdsWater` goes.
  - `burnt_saucepan`, `dented_saucepan`: `holdsFluid:{ capacityMl:1000 }`.
  - `cooking_pot`: `holdsFluid:{ capacityMl:2000 }`.
  - Every `vessel` drops `waterKg`: `vessel:{ kind, capacityKg }`. The frying
    pan and roasting pan get no `holdsFluid`.
  - The thermos joins in Phase 6.
- **New instance field `fluid: { kind, ml }`**: `kind` a string (today
  `"clean"` or `"tainted"`, open-ended for later liquids), `ml` a positive
  integer. **Absent when empty**, never `ml: 0`. It replaces `water` on every
  holder.

### The helpers (INVENTORY / ITEM SYSTEM)

Replace the water helpers with fluid ones; every reader goes through them:

- `fluidKindOf(it)`: `it.fluid ? it.fluid.kind : null` (replaces
  `waterKindOf()`).
- `capacityMlOf(it)`: the registry's `holdsFluid.capacityMl`, or 0.
- `holdsFluidAtAll(it)`: a capacity above 0 and no dish in it (replaces
  `holdsWaterAtAll()`).
- `fluidSpaceMl(it)`: `capacityMlOf(it) − ml` while `holdsFluidAtAll()`, else
  0 (replaces `canTakeWater()` and `sinkLitresFor()`).
- **`mixKinds(a, b)`**, the one statement of what mixes: `null` with
  anything is the other; equal kinds are that kind; `"clean"` with
  `"tainted"` is `"tainted"`; **any other pair is `null`: they don't mix,
  and no action offers it.**
- `addFluid(unit, kind, ml)`: sets `unit.fluid` to the mixed kind and the
  summed ml, and deletes `boilMinutes` (new water starts a boil over, as
  today). Callers never pass more than `fluidSpaceMl()`.
- `takeFluid(unit, ml)`: subtracts; at 0 deletes `fluid` and `boilMinutes`.
- **Weight:** `fluidWeightOf(it)` = `fluid.ml / 1000` kg (1 L of water
  weighs 1 kg, as today), replacing `waterWeightOf()` in `itemUnitWeight()`.
- **Stacking:** `sameStackState()` compares `fluidKindOf()` and `fluid.ml`
  (absent on both counts as equal) in place of the water kind and `fill`.
  `leastLeftRow()` matches on `fluidKindOf()`.
- **The level** (`unitLevel()`, Phase 1): any holder with fluid, `level` =
  `ml / capacityMl`, `figure` = "`ml` of `capacityMl` mL", the numbers grouped
  with commas ("1,250 of 2,000 mL"). A holder without fluid: `null`. This
  replaces both Phase 1 water cases; the vessel's "Full of water" line goes.
  The pop-up's "Holds no food" / "Empty" line reads `fluid` in `water`'s
  place.

### The sink

- `canFillAtSink(it)`: the room has a sink, `waterRunningIn()`, and
  `fluidSpaceMl(it) > 0`. **Vessels fill part-way like bottles**: the
  all-or-nothing rule goes, and with it the vessel's special case in the
  tank check.
- `doFillAtSink()`: fills one unit (via `changeOneUnit()`, as today) by its
  `fluidSpaceMl()`, or off a tank by `min(space, tankLeft × 1000)` floored to
  the millilitre, adding clean water (`addFluid()`, so tainted water already
  there taints it). The tank draws the same amount in litres, as today. Log
  lines and the float resolve unchanged.
- `tapDryFor(it)`: a sink, a tank, `fluidSpaceMl(it) > 0`, and the tank dry.
- **Re-point the sink comment**: "whatever was left in the pipes" is #300's,
  not #47's.

### Pouring, until Phase 4

So the game keeps working between phases: `canPourInto()` /
`doPourIntoVessel()` pour **as much as fits**, `min(bottle ml, vessel
space)`, and are offered whenever the vessel has room and `mixKinds()` is
not null. Phase 4 replaces both.

### Drinking, until Phase 3

`consumeProfile()` for a holder with fluid: `left` = `ml / capacityMl`,
restores `{ thirst: WATER_THIRST_PER_L × capacityMl / 1000 }`, poisoning
`TAINTED_WATER_POISONING_CHANCE × capacityMl / TAINTED_WATER_DOSE_ML` when
tainted. For a 500 mL bottle that is exactly today's rule. `eatFromRow()`
takes `amount × capacityMl` ml (rounded) through `takeFluid()`. Phase 3
replaces this.

### Dishes (FIRE / COOKING)

- **A dish that needs water needs at least
  `ceil(DISH_WATER_MIN_SHARE × capacityMl)` ml of clean water** (400 mL in a
  saucepan, 800 mL in the pot). `templateStatus()` takes the vessel's
  `fluid` (kind and ml) in place of the water kind: `waterOk` is, for
  `t.water`, clean and at least the minimum; for a template without water,
  no fluid. `waterBoils`: `t.water`, tainted, and at least the minimum.
- **The dish takes up all the water in the vessel**, as it does today:
  `formDish()` passes the vessel's `ml / 1000` kg to `buildDish()` and deletes
  `fluid`. `soonestIn()` passes the same. `dishFrom()` (the world's spawned
  stews) passes the vessel's full `capacityMl / 1000`.
- `dishProgressText()`: with `t.water` and no fluid, or less than the
  minimum, the need reads **"at least N mL of water"** (N the minimum,
  comma-grouped). `dishNeedsText()` keeps "with water".
- Boiling unchanged: a flat `BOIL_MINUTES`, whatever the volume.

### Instances in the world

- The two spawn pool entries: `state:{ fluid:{ kind:"clean", ml:500 } }`.
- The two home placements: `overrides:{ fluid:{ kind:"clean", ml:500 } }`.
- `MIGRATED_ITEMS.bottled_water`: a bottle with `fluid:{ kind:"clean",
  ml:500 }`.
- The replay's pot: `fluid:{ kind:"tainted", ml:2000 }`.

### Checks — Phase 2

- A new game: the home's bottles read "500 of 500 mL" and weigh 0.55 kg
  each; the inventory total matches v0.11.1's.
- A saucepan filled at the sink holds 1,000 mL. With the home's tank drawn
  to 0.3 L left, an empty pot fills to 300 mL and the tap runs dry.
- A pot with 700 mL of clean water, meat and vegetables doesn't form stew;
  Crafting says "needs at least 800 mL of water"; fill to 800 mL and it forms
  on heat, its weight including the 0.8 kg of water.
- Tainted water in a pot boils clean after `BOIL_MINUTES`; adding water
  restarts the count.
- Two bottles at 250 mL stack; one at 250 and one at 300 don't, and form a
  group (Phase 1).
- Drinking a full bottle by today's buttons restores 30 Thirst, as before.

---

## Phase 3 — Drinking (#47)

### From a holder

- **Offered on any holder with fluid and no dish**, a vessel with
  ingredients included (it drinks the water, never the food), and on a group
  header over such holders (Phase 1).
- **Drink**: `MEASURE_ML`, or what is left when less. **Drink all**: the
  millilitres that bring Thirst to full,
  `ceil((VITAL_MAX − Thirst) / WATER_THIRST_PER_L × 1000)`, or what is left
  when less. `clamp()` (~710) hard-codes the vitals' top as `100`; name it
  `VITAL_MAX` and have both read it. **Drink all is not offered at full Thirst**; Drink always is.
- **Which unit:** the least-left unit holding the same kind of fluid among
  the rows of the same item (`eatTarget()`'s rule), as today.
- **What a drink does**, one function, `drinkFrom(list, unit, ml)`: Thirst
  += `ml / 1000 × WATER_THIRST_PER_L` (clamped); `takeFluid()` (a holder
  drunk dry stays, empty); tainted water rolls food poisoning (as today,
  `rollFoodPoisoning()`) at `TAINTED_WATER_POISONING_CHANCE × ml /
  TAINTED_WATER_DOSE_ML`.
- **`EAT_PARTS` no longer applies to fluid.** `consumeProfile()` goes back to
  being about food; the holder branch and Phase 2's interim rule go.
- **Log lines** (game text, wording retunable), the holder's name
  lowercased:
  - "You drink from the plastic bottle." (some left)
  - "You drink the last of the water in the plastic bottle." (emptied it)
  - "You drink your fill from the plastic bottle." (Drink all, Thirst full,
    some left)
  - The poisoning onset line, if any, follows, as today.

### From the tap (WORLD INTERACTION, RENDERING)

- In the Here actions, a room with a sink while `waterRunningIn()` offers
  **"Drink at the sink"** (`MEASURE_ML`) and, below full Thirst, **"Drink
  your fill at the sink"** (to full Thirst). These are the tap's Drink and
  Drink all; the labels are functional text, retunable. The water is clean.
  Instant, as filling is.
- **It draws from the tank as a fill does**: the litres drunk, the float
  resolve, and on the last of it only what is left ("The tap coughs, spits,
  and runs dry." when that empties it). A sink without a tank draws on the
  mains and draws nothing down.
- A sink whose tank is dry shows the note "The tap is dry." in their place.
- Lines: "You drink from the tap." / "You drink your fill at the tap."

### Checks — Phase 3

- At Thirst 50, Drink on a full bottle leaves 250 mL and Thirst 65; Drink all
  on it then empties it (Thirst 80) and says so.
- At Thirst 90, Drink all on a full pot drinks 167 mL (ceil) and leaves 1,833
  mL; Thirst is 100 and Drink all is gone, Drink still offered.
- A tainted 250 mL drink rolls at 0.175.
- At the sink, Drink at the sink draws 0.25 L from the tank; with 0.1 L left
  it drinks 100 mL and the tap runs dry.
- Eat ½ and ¼ still work on food; a bottle offers no ½ or ¼.

---

## Phase 4 — Pouring (#47)

### Targets

- **Any holder pours into any other**: bottle, vessel or thermos, either
  way. A holder with a dish neither gives nor takes.
- **Within reach**, as `nearbyVessels()` reaches today: the inventory pools,
  the floor, the listed containers (unrolled ones count as empty), and the
  room's heat container. Generalise it to every `holdsFluidAtAll()` item.
- **A target needs room** (`fluidSpaceMl() > 0`) **and a kind that mixes**
  (`mixKinds(source, target)` not null).
- The **source unit is split off first** (`changeOneUnit()`), so the other
  units of its own row are targets like any other.
- **Identical targets are one entry**: rows with the same group key (Phase 1)
  in the same place. Pouring into it pours into **the fullest unit that is
  not full**, so bottles are topped up rather than water spread thin.

### The submenu (RENDERING)

- A source with fluid and no dish shows one action, **"Pour…"**, in its
  pop-up (and none on a group header). It opens the transfer submenu **in
  the same pop-up**: a heading "Pour the water into…", a **Back** button to
  the item's actions, then one entry per target:
  - its name and labels, its place when two entries would otherwise read the
    same (`vesselButtonNames()`'s rule: "carried", "Floor" or the container's
    name), and its meter (Phase 1), so `(Tainted)` and how full it is show
    before the pour;
  - two buttons: **"Pour"** (as much as fits) and **"Pour 250 mL"** (the
    label from `MEASURE_ML`).
  - No target: the note "Nothing here has room for it." (functional text).
- After a pour the submenu stays open while the source still holds fluid;
  emptied, it returns to the item's actions.
- It replaces the flat "Pour into the …" buttons. `doPourIntoVessel()` and
  `canPourInto()` go; `vesselButtonNames()` stays for "Add to the …".

### The pour

- `pourFluid(sourceList, source, target, ml)`: moves `min(ml, source ml,
  target space)` with `takeFluid()` / `addFluid()`; the kind mixes
  (`mixKinds()`), a vessel target's boil starts over, a source vessel keeps
  its `boilMinutes`. Pouring tainted water into clean water is allowed, with
  no confirmation: the label shows it.
- Line: "You pour the water into the cooking pot." (as today; wording
  retunable).

### Pour out

**"Pour out the water"** is offered on every holder with fluid and no dish
(today only vessels): empties it; the water is gone. Silent, as today.

### Checks — Phase 4

- A full bottle and an empty pot carried: Pour… lists the pot; Pour 250 mL
  leaves 250 and 250; Pour moves the rest.
- Three empty bottles on the floor and one at 100 mL: one target entry;
  Pour from a full pot fills the 100 mL one first (400 mL), then a second
  pour fills an empty one.
- A clean pot and a tainted bottle: the pot is listed, labelled `(Water)`;
  after the pour the pot reads `(Tainted)`.
- A pot holding a dish is never a source or a target.
- A bottle in a stack of three at 250 mL pours into its own row's other
  units.
- Pour out the water on a bottle empties it and it shows no meter.

---

## Phase 5 — Auto-drink (#47)

### The rule

- **While awake, with Thirst below `LOW_THIRST_THRESHOLD`**, the player
  drinks on their own from **carried** holders (`invPools()`: the inventory
  and worn bags), **clean water only** (never tainted, never from a tap),
  **least left first** (by `unitLevel().level`, ties in list order), each
  holder **as Drink all** (Phase 3), moving to the next as one empties,
  **until Thirst is full or the carried clean water runs out.**
- **When it is checked:**
  1. **At the minute Thirst crosses the threshold**, in `clockStep()` right
     after `applyHungerThirst()`: one comparison of Thirst before and after
     the step, and a drink only on the step that crosses, only when not
     `asleep`.
  2. **At the end of every action**, while awake and below the threshold.
     This is what makes filling a bottle while thirsty drink from it at
     once, and waking thirsty drink on waking. (See the implementation
     decision below for where this hook lives.)
- **Not while asleep**: not during `doSleep()`, not during a blackout
  (`asleep` true).
- **Always on**; there is no switch.
- **Log**: one line per holder drunk from, Phase 3's lines.

### Checks — Phase 5

- Thirst 31 with a full bottle carried; Rest: at the crossing minute the
  bottle is emptied (500 mL brings Thirst to about 60) and the line logged;
  the rest of the hour runs at the higher Thirst.
- Thirst 31 with a full pot (2,000 mL) carried; at the crossing it drinks
  until Thirst is full and the rest stays in the pot.
- Thirst 25, no water carried; fill a bottle at the sink: it is drunk
  immediately after the fill.
- A tainted bottle only: nothing is drunk.
- Asleep through the crossing: nothing drunk until the sleep ends; then it
  drinks.
- Two bottles at 100 and 500 mL: the 100 mL one is emptied first.
- A bottle on the floor is never drunk.

---

## Phase 6 — The thermos, save migration, dev helpers, docs, wrap

### The thermos

`thermos`: `unitWeight:0.65`, `holdsFluid:{ capacityMl:1000 }` (stainless, the
most common mate size; source quoted above). Category, name and spawns
unchanged. Keeping water hot, and mate, are not designed. The
`mate_bombilla` comment stays.

### Loading older saves

`SAVE_KEY` rotates, but **an imported v0.11.1 file must load.** A new
`migrateFluidRelease()`, run after `migrateCookingRelease()`, idempotent,
over every item `forEachItemList()` reaches and every equipped slot:

- An item with `water`: when its registry entry `holdsFluid`, `fluid` =
  `{ kind: water.kind, ml }`, `ml` being `round(fill × capacityMl)` for one
  with a `fill`, and `capacityMl` for a vessel's (always full); then `water`
  is deleted. An item whose entry holds no fluid just loses `water`.
- The thermos's `unitWeight` is set from the registry.
- Loading twice changes nothing.

### Dev helpers (read-only)

`validateItemRegistry()` also flags: a `holdsFluid` whose `capacityMl` is not
a positive integer; any `holdsWater` or `vessel.waterKg` left on an entry; a
spawn pool `state` or placement `overrides` carrying `water`.

### Comments

- ITEM DATA SCHEMA: `holdsFluid` and `fluid` (with `mixKinds()` named as the
  rule), in place of `holdsWater` and `water`; `vessel` without `waterKg`;
  `portion` unchanged.
- VESSELS AND DISHES: vessels hold fluid part-way; the dish minimum.
- **Remove or rewrite every reference to #47 and #134 in the code**, since
  this release closes both ("the interim Drink rule, until fluid volumes
  (#47) replace it", the sink comment, `canTakeWater()`'s, `vesselButtonNames()`'s
  "since nothing yet tells them apart (#47)").

### Systems docs

- **New: `docs/systems/fluids.md`**, per `docs/systems/README.md`'s format,
  and listed in its Index: holders and kinds, mixing, the sink and the tap,
  drinking, auto-drink, pouring, dishes' water, weight. Names constants,
  never values.
- **Update `docs/systems/survival.md`**: auto-drink reads Thirst and
  `LOW_THIRST_THRESHOLD`, and is checked in the clock step; name it under
  Model and Entry points.
- **Update `docs/systems/time.md`**: the clock step's crossing check, and
  that nothing about fluid is scheduled.
- `docs/systems/power.md` names `doFillAtSink()`, which stays: check its
  sentence still holds.

### Wrap (per `CLAUDE.md` and `docs/03-workflow.md`)

1. `GAME_CONFIG.VERSION` bumped as **MINOR** (with nothing shipped in
   between, `0.12.0`; `SAVE_KEY` becomes `ashfall_save_v0.12`).
2. **One** `CHANGELOG.md` entry per `docs/05-changelog-guide.md`, with
   `Implements: handoffs/fluid-transfer.md`, and every implementation
   decision below resolved.
3. `git mv handoffs/fluid-transfer.md handoffs/archive/fluid-transfer.md`.
4. PR description: `Closes #134`, `Closes #47` (one per line).
5. New issues for anything cut or surfaced; if none, the changelog says so.
6. The tag block, as the last thing in the session's final message.

### Checks — Phase 6

- Import a v0.11.1 export holding a full bottle, a bottle at ½, a tainted
  bottle at ¼, a pot full of clean water, a pot holding a dish and a thermos.
  It loads: 500, 250 and 125 mL, a pot of 2,000 mL, the dish untouched, the
  thermos at 0.65 kg holding nothing. Import it twice: nothing changes.
- The thermos fills at the sink to 1,000 mL and pours like any holder.
- `validateItemRegistry()` reports nothing.
- The replay page passes; the benchmark passes within its budgets.
- A full play-through of every phase's checks on the final build.

---

## Design decisions to make during implementation

Record each in the changelog's Notes / assumptions:

- **Where the end-of-action auto-drink check lives.** Options: (a) a single
  `afterAction()` called by every place a player action is dispatched
  (`actionButton()`, the item pop-up's and the submenu's action buttons, the
  item lists' quick buttons, the device pop-up's buttons), which runs the
  check and renders again only if it drank; (b) calls at the end of
  `settleToNow()` plus every action that can put clean water into a carried
  holder or a holder into the inventory. **Recommended: (a)**, one hook with
  no list to keep in step.
- **Identifier names** for the new helpers and constants (the ones above are
  suggestions).
- **The meter's thickness and colours**, and the submenu's layout, within the
  rules above.
- **How `openGroups` is keyed**, within the rule that it is per side, tab and
  group.

None changes the version type.

## Data / schema changes

- **Item schema:** new `holdsFluid: { capacityMl }` (registry only); new
  instance `fluid: { kind, ml }`; removed `holdsWater` and instance `water`;
  `vessel` loses `waterKg`. `thermos` gains `holdsFluid` and weighs 0.65 kg.
- **Player state:** none new. `openGroups` is UI-only and never saved.
- **World data:** the spawn pool `state` and placement `overrides` above.

## Costs

- **Phase 1:** rendering only; grouping is one pass over a list per render,
  proportional to that list.
- **Fluid actions:** each touches one or two items. Building the Pour…
  submenu walks the lists in reach once, as "Pour into the …" did.
- **Auto-drink:** per clock step, one comparison of Thirst before and after.
  Per action, one comparison. Only while awake and below the threshold does
  it walk the carried lists (the inventory and worn bags), never the world.
  Nothing is scheduled and nothing new is saved.
- Expected effect on the benchmark: none measurable. If the Performance check
  trips, say in the PR what this section predicted and what was measured.

## In scope

- [ ] Item groups with a ▸/▾ header, group pop-up, group moves (Phase 1)
- [ ] Meters along the row, `LEVEL_WARN_BELOW`, exact figures in the pop-up (Phase 1)
- [ ] `(On)`; the "% charge" figure removed (Phase 1)
- [ ] `holdsFluid` / `fluid` in millilitres; weight; stacking; mixing (Phase 2)
- [ ] Vessels fill part-way; the sink in ml; the dish minimum (Phase 2)
- [ ] Drink / Drink all from any holder; drinking at the tap (Phase 3)
- [ ] The Pour… submenu; any holder to any holder; Pour out on every holder (Phase 4)
- [ ] Auto-drink (Phase 5)
- [ ] The thermos as a holder; save migration; validators; comments; `fluids.md`; wrap (Phase 6)

## Explicitly out of scope

- **#388** (batteries as cells): loose batteries' meters come with it.
  Phase 1's meter shows nothing for batteries today, which have no charge of
  their own.
- **#394** (a bucket, a canteen, dispenser jugs): new holders, data only, on
  this model, after it ships.
- **#385** (the kettle): an appliance as a pour target is that issue's,
  built on Phase 4's submenu.
- **#300**: water left in the pipes once the mains stop. The sink stops when
  `waterRunningIn()` says so, as today.
- **#52**: treatment, the well, the river, and boiling time by volume.
- **#239**: petrol as a fluid kind. `fluid.kind` is left open for it; no
  other kind is added.
- **Keeping water hot, mate, spilling, lids**, and any switch for auto-drink
  (#165).
- **The discrete liquids** (milk, bleach, motor oil, …) stay discrete.

## Sections touched

ITEM DATA SCHEMA; WORLD DATA (registry entries, spawn pools, placements);
INVENTORY / ITEM SYSTEM; SURVIVAL / TIME SIMULATION (`clockStep()`);
WORLD INTERACTION (the sink, the tap); FIRE / COOKING (vessels, dishes);
PERSISTENCE (migration); RENDERING (item lists, the item pop-up, the
submenu, the Here actions, Crafting's dish text); the dev seam
(`validateItemRegistry()`); the replay page's data.

## Systems docs

- **Read first:** `docs/systems/time.md`, `docs/systems/survival.md`,
  `docs/systems/power.md` (the sink's draw), `docs/systems/spoilage.md`
  (ages, which groups and moves must keep).
- **Create:** `docs/systems/fluids.md`, and list it in the Index.
- **Update:** `time.md`, `survival.md`; check `power.md`.

## UI changes

- Item lists: groups under a ▸/▾ header; meters along rows; `(On)`.
- The item pop-up: a larger meter and the exact figure; group pop-ups;
  Drink / Drink all in place of Drink, Drink ½, Drink ¼ for water; Pour… and
  its submenu in place of the "Pour into the …" buttons; Pour out the water
  on bottles and the thermos.
- The Here actions: Drink at the sink, Drink your fill at the sink.
- Crafting: "at least N mL of water".
- No device shows a battery percentage.

## Dependencies / issue linkage

- Fulfils **#134** and **#47**.
- Unblocks **#388** (batteries as cells, whose display is #134's), **#394**
  (new holders), **#385** (the kettle as a pour target) and **#52**'s
  implementation.
- Nothing is expected to be deferred. Anything cut is filed at the wrap.

## Open questions for Tom

None. Every design decision is settled in #134's and #47's bodies.
