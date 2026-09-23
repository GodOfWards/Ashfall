# Ashfall Handoff — Carry load: a player limit, worn-bag discounts, and the cost of going over

Current shipped version: v0.7.2 (`handoffs/here-panel-tabs.md` must ship first; see "Precondition")
Implied version-change type: PATCH. The load is derived and never stored. Each
bag's factor is read from `ITEM_REGISTRY` through `itemId`, not copied onto
saved items or slots. The only save-facing change removes a field (the base
inventory's `capacityKg`) on load. No field is added, so `SAVE_KEY` doesn't
move.
Issues: #168, #170

## Precondition

Implement this only once `handoffs/here-panel-tabs.md` has shipped: it must be
in `handoffs/archive/`, not at the top level of `handoffs/`. If it is still at
the top level, stop and tell Tom. This handoff's Take and Equip checks reach
floor-bag tabs through the `worldSlot()` that one extends, and its "Relevant
existing state" assumes that pass has landed.

## What this is

Weight gets a consequence. #168 and #170 are one feature, and Tom decided both
in this planning session.

- The player has one **carry limit, 13 kg**. Load up to 13 kg is free.
- **Loose inventory has no weight cap of its own**. Only a hidden safety cap
  guards it. Bags keep their own capacities.
- **A worn bag counts for less.** Its whole weight (the bag plus its contents)
  counts against the player at the bag's factor. A backpack carries better
  than a purse.
- **Over 13 kg** is allowed, but movement gets slower and costs Exertion.
  From 26 kg, moving also costs Health.
- **The hard limit is 32.5 kg.** Nothing may push the load past it. Only
  Unequip can, and Unequip is always allowed.

In #170's words: "Allow over-encumbrance, but apply penalties until the player
gets to a hard upper limit."

## Relevant existing state

Verified against `ashfall.html` at v0.7.2. Line numbers are only a guide;
find each item by its function name. `here-panel-tabs.md` changes none of the
code below except `worldSlot()`, which gains floor-bag tabs.

- **`makeDefaultState()`** (PLAYER STATE, ~3775) gives the player:
  - `inventory:{ name:"Inventory", unitWeight:0, capacityKg:3, items:[] }`;
  - `keychain:{ name:"Keychain", unitWeight:0.05, capacityKg:null, items:[…] }`;
  - every other `CONTAINER_SLOTS` slot as `null`.
- **`applyLoadedData()`** builds `nextState` as
  `{ ...base, ...data.state, vitals:{…} }`. The saved `inventory` object
  replaces the default wholesale, so every existing save carries
  `inventory.capacityKg:3`. Its backfills run after `validateLoadedWorld()`.
- **Bags** in `ITEM_REGISTRY`:

  | Item | `slotType` | `unitWeight` | `capacityKg` |
  |---|---|---|---|
  | `worn_backpack` | `backpack` | 0.6 | 12 |
  | `duffel_bag` | `duffel` | 0.8 | 18 |
  | `purse` | `purse` | 0.4 | 5 |
  | `fanny_pack` | `fannypack` | 0.2 | 3 |
  | `tote_bag` | `tote` | 0.3 | 8 |

  None carries a carry factor.
- **`doEquip(sourceKind, index)`** resolves its source through `worldSlot()` or
  `invSlot()`. It builds the slot as
  `{ itemId, name, unitWeight, capacityKg, items: it.contents || [] }`. It has
  no capacity check.
- **`doUnequip(slotKey)`** rebuilds the bag from the registry, or through its
  fallback for the keychain or an `itemId`-less slot. It adds the bag to
  `state.inventory.items` with no capacity check, by Tom's earlier decision.
- **`invSlot(tab)`** returns `state.inventory` for `"inventory"`, and
  otherwise the `CONTAINER_SLOTS` slot or `null`. `invPools()` is the
  inventory plus each slot's `.items`.
- **`addToDestination(item)`**:
  - `dst = invSlot(invTab)`;
  - `{ok:false, reason:"keychain"}` when `keychainAllows` fails;
  - `{ok:false, reason:"capacity"}` when
    `dst.capacityKg && totalWeight(dst.items) + itemWeight(item) > dst.capacityKg`;
  - otherwise `addToList()` and `{ok:true}`.

  It has two callers:
  - **`doTake()`** logs "That won't fit — not enough room there." (`"warn"`)
    on `capacity`, and stays silent on every other reason.
  - **`giveItem()`** always ends on the floor when refused, logging one of
    three lines: the keychain line; "No room anywhere — the … ends up in a
    heap on the already-cluttered floor." when the floor is over `floorCap`;
    otherwise "No room for the … — it drops to the floor instead." Its
    callers are `doCraft()`, fishing, and removing batteries.
- **`doStore()`, `doConsume()` and `doOpen()`** only move weight out of the
  player or keep it level.
- **`itemUnitWeight(it)`, `itemWeight(it)` and `totalWeight(list)`** include
  `contents` at any depth.
- **Movement.** Every move goes through `doMove(exit)`, and nothing else
  calls `moveMinutes()`.
  - `moveMinutes(distanceM, gridTravel)` returns
    `Math.max(floor, distanceM / GAITS[effectiveGait()].speed / 60)`.
  - `GAITS` is `{ sneak:{speed:0.6}, walk:{speed:1.2}, fast:{speed:2.0} }`.
  - `exitMinutes(exit)` wraps `moveMinutes()`. Both move-button renderers
    print it as the button's cost.
  - `doMove()` samples `const gait = effectiveGait()` before
    `advanceTime(minutes)`. It then adds
    `applyExertion(JOG_EXERTION_PER_MIN * minutes)` when `gait === "fast"`.
  - `JOG_EXERTION_PER_MIN = 0.5`, declared beside `doMove()`.
- **`advanceTime(min)`** ends with `checkGameOver()`. **`applyExertion(x)`**
  returns early when `x <= 0`.
- **Health drains** are written as `health = clamp(health - min / X_MINUTES_PER_HEALTH)`:
  starvation 30, dehydration 15 and illness 20 game minutes per point.
- **`log(text, cls, key)`**: consecutive calls with the same `key` collapse
  into one line with a trailing "×N", unless `LOG_SUMMARIES` has the key.
- **`renderInventoryPanel()`** writes `#invWeight` as
  `totalWeight(currentInv.items).toFixed(2) + (currentInv.capacityKg ? " / " + currentInv.capacityKg + " kg" : " kg")`.
  CSS has `--warn` and `--danger` colour tokens.

## Rules / mechanics

### A. Load

- **`CARRY_LIMIT_KG = 13`**: the most the player carries with no penalty.
- **`carryFactor`**: a new `ITEM_REGISTRY` field on the five bags. It is
  definition data for this mechanic, so it rides along.

  | Item | `carryFactor` |
  |---|---|
  | `worn_backpack` | 0.72 |
  | `fanny_pack` | 0.76 |
  | `duffel_bag` | 0.81 |
  | `tote_bag` | 0.85 |
  | `purse` | 0.85 |

  Tom set these as the first proposal (0.8 / 0.85 / 0.9 / 0.95 / 0.95) × 0.9,
  floored to two decimals. Write the literals. They are per-bag data, and all
  are retunable.
- **A slot's factor** is `ITEM_REGISTRY[slot.itemId].carryFactor` when the
  slot has an `itemId` whose entry defines the field. Otherwise it is **1**:
  the keychain, or an unknown or unrepaired slot. It is always read from the
  registry and never copied onto the slot or the bag item.
- **`playerLoad()`** =
  `totalWeight(state.inventory.items)`
  \+ for each `CONTAINER_SLOTS` slot that is filled:
  `(slot.unitWeight + totalWeight(slot.items)) × slotFactor(slot)`.

  The keychain counts at factor 1, its own 0.05 kg included. A bag that isn't
  worn counts at full weight wherever it is on the player. This is the one
  definition every rule below reads.
- **Worked examples:**
  - A full worn backpack is (0.6 + 12) × 0.72 = 9.07 kg of load.
  - A full worn duffel is (0.8 + 18) × 0.81 = 15.23 kg, over the limit on its
    own.

### B. Loose inventory has no cap of its own

- Remove `capacityKg` from `makeDefaultState()`'s `inventory`.
- **On load, delete `state.inventory.capacityKg`** if present, so no old save
  keeps its 3 kg. After this pass, nothing reads a capacity off
  `state.inventory`.
- **Hidden safety caps**, a guard against a bug that adds items without end,
  never shown to the player:
  - `LOOSE_INVENTORY_MAX_KG = 100`
  - `LOOSE_INVENTORY_MAX_ENTRIES = 1000`, counting list entries, so a stack is
    one.

  `addToDestination()` checks them when the destination is `state.inventory`.
  Reject when `totalWeight + itemWeight(item) > 100`, or when
  `items.length >= 1000`. Both reject with the existing
  `reason:"capacity"`, so `doTake()` and `giveItem()` react as they already
  do. `doUnequip()` and `doOpen()` don't check them.

  100 kg sits far above anything play reaches: unequipping every full bag at
  the hard limit leaves about 45 kg loose. Tom offered "50 kg or 100 kg"; 100
  was chosen for that headroom.
- Bags keep their own `capacityKg`, checked exactly as today.

### C. The bands and what they cost

Constants (all retunable, each defined once; the derived ones as written):

```
CARRY_HARD_LIMIT_KG        = CARRY_LIMIT_KG * 2.5   // 32.5
OVERLOAD_HARM_START_KG     = CARRY_LIMIT_KG * 2     // 26
OVERLOAD_MIN_SPEED_FACTOR  = 0.25
OVERLOAD_MAX_EXERTION_PER_MIN = JOG_EXERTION_PER_MIN   // "+1 jogging's rate"
OVERLOAD_HARM_MINUTES_PER_HEALTH_START = 10   // at 26 kg
OVERLOAD_HARM_MINUTES_PER_HEALTH_END   = 5    // at 32.5 kg and beyond
```

Two fractions, each clamped to [0, 1]:

```
over = (load − CARRY_LIMIT_KG)         / (CARRY_HARD_LIMIT_KG − CARRY_LIMIT_KG)
harm = (load − OVERLOAD_HARM_START_KG) / (CARRY_HARD_LIMIT_KG − OVERLOAD_HARM_START_KG)
```

Everything is linear in these, as Tom specified. Past the hard limit, which
only Unequip reaches, both stay at 1.

- **Speed.** `speedFactor = 1 − over × (1 − OVERLOAD_MIN_SPEED_FACTOR)`, so 1
  at 13 kg and 0.25 at 32.5 kg. `moveMinutes()` divides by
  `GAITS[effectiveGait()].speed × speedFactor`. The `MIN_MOVE_MIN` floor
  term doesn't scale. Because `exitMinutes()` wraps `moveMinutes()`, the move
  buttons show the slower times with no RENDERING change.
- **Exertion.** Every move adds
  `over × OVERLOAD_MAX_EXERTION_PER_MIN × minutes` to the move's Exertion, at
  every gait. That is 0 at 13 kg and +0.5 per minute at 32.5 kg. It adds to
  Jog's surcharge rather than replacing it.
- **Health.** While `load ≥ OVERLOAD_HARM_START_KG`, a move costs
  `minutes × healthPerMin`, where
  `healthPerMin = 1/START + harm × (1/END − 1/START)`. That is 0.1 per minute
  (1 per 10) at 26 kg, rising linearly to 0.2 per minute (1 per 5) at 32.5 kg.
  Below 26 kg there is no Health cost. The rate is interpolated in Health per
  minute, not in minutes per point. Flag this as retunable.
  - The move logs **"Something in your back twinges under the weight."** as
    `"warn"`, with a log key so consecutive moves collapse to "×N".
  - Then `checkGameOver()`. Carrying too much can kill.
- **Timing.** `doMove()` samples the load once, before `advanceTime()`, beside
  its gait sample and for the same reason: the move is priced and charged
  from one reading.

  `minutes` is the move's actual duration, slowdown included. The per-minute
  Exertion and Health therefore grow with the slowdown as well: at 32.5 kg an
  exit takes four times as long, and every one of those minutes is charged.
  This is intended ("per minute moved").

### D. The hard limit refuses what would pass it

An action that would take `playerLoad()` above `CARRY_HARD_LIMIT_KG` is
refused.

- **`addToDestination(item)`**: the added load is `itemWeight(item) × f`,
  where `f` is the destination's factor. The loose inventory and the
  keychain are 1; a bag slot uses `slotFactor()`.
  - If `playerLoad() + added > CARRY_HARD_LIMIT_KG`, return
    `{ok:false, reason:"load"}`.
  - Check order: keychain, then capacity (the bag's own or the hidden caps),
    then load. When both room and weight fail, the room message wins.
- **`doTake()`** on `reason:"load"` logs **"You can't carry any more."** as
  `"warn"`.
- **`giveItem()`** on `reason:"load"` drops the item to the floor, as it does
  for every other refusal. It uses the existing floor lines: the
  `floorCap` heap line when the floor is over cap, otherwise "No room for the
  … — it drops to the floor instead." This covers crafting, fishing and
  removed batteries.
- **`doEquip()` from the world side** (floor, container or floor-bag tab):
  the added load is `itemUnitWeight(bag) × carryFactor(bag)`. The bag's
  factor comes from its registry entry by `itemId`, and 1 without one. If
  that would pass the hard limit, it is refused with "You can't carry any
  more." Equipping from the inventory side is never refused on load, since it
  can only lower the load.
- **`doUnequip()` is never refused.** It can push the load past the hard
  limit. The player is then at the maximum penalty and takes Health damage
  on every move until they shed weight.
- `doStore()`, `doConsume()`, `doOpen()` and crafting's input consumption
  lower the load or leave it level. None of them checks it.

### E. Comments

- Document `carryFactor` in the ITEM DATA SCHEMA comment beside `capacityKg`.
  It is an equippable bag's factor against the player's load, read from the
  registry and never from an instance.
- One short comment at `playerLoad()`: load is derived, never stored, and the
  factor is looked up by `itemId` so a retune reaches every save.
- Follow `here-panel-tabs.md`'s convention: no counts or ordinals in the
  comment of any load-time step this adds.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **Where the constants live.** Recommended: `CARRY_LIMIT_KG`,
   `CARRY_HARD_LIMIT_KG` and the two loose caps sit in INVENTORY / ITEM
   SYSTEM beside `playerLoad()`. The speed, Exertion and Health rates sit
   beside `doMove()`, on the precedent of `JOG_EXERTION_PER_MIN`: a task's
   rates live with the task.
2. **The load-time `capacityKg` removal.** Either a small named backfill
   beside the others, or one line in `applyLoadedData()` after validation.
   Recommended: a backfill, so it is listed with the other repairs.
3. **Helper shape.** `slotFactor(slot)`, `overloadFraction()` and so on, or
   inlined. Pick whatever keeps each formula written once.
4. **A registry check.** Optionally extend `validateItemRegistry()` (dev-only)
   to warn when a `slotType` entry lacks a `carryFactor` in (0, 1].
   Recommended.

## Data / schema changes

- **ITEM DATA SCHEMA:** `carryFactor` (number, 0–1) on equippable bags. It is
  set on the five entries above, and read only through the registry.
- **PLAYER STATE:** `inventory.capacityKg` is **removed** from the default and
  deleted on load. No field is added anywhere.
- **Constants:** listed in C, plus `CARRY_LIMIT_KG` and the two
  `LOOSE_INVENTORY_MAX_*`.

## In scope

- `playerLoad()`, the factor lookup and the `carryFactor` registry values.
- The loose inventory's cap removed, the saved cap deleted on load, and the
  hidden caps.
- Slowdown in `moveMinutes()`; overload Exertion and Health in `doMove()`,
  with the log line.
- Hard-limit refusals in `addToDestination()`, `doTake()` and `doEquip()`
  (world side), and the new `reason:"load"`.
- The Inventory-tab header readout and its colours.

## Explicitly out of scope

- **Capacity retunes.** Tom's "20 kg backpack" in #168 was an example. The
  shipped capacities stay, and any change is a WORLD DATA pass of its own.
- **Load affecting anything but movement.** Chopping, fishing, sleep and rest
  are unchanged.
- **Clothing (#56).** Worn clothing will add to the same load. Not now.
- **Health (#53) and weather (#58)** changing the limit or the penalties.
- **Run options (#149)**, such as a carry-limit knob.
- **#167** (Disassemble). Shelved.
- New log wording for `giveItem()`'s load refusal. It reuses the existing
  floor lines.

## Sections touched

- ITEM DATA SCHEMA / `ITEM_REGISTRY`: `carryFactor` on five bags. This is
  definition data only, and no instance data rides along.
- PLAYER STATE: `makeDefaultState()`'s inventory.
- INVENTORY / ITEM SYSTEM: `playerLoad()`, `addToDestination()`,
  `giveItem()`, `doTake()` and `doEquip()`.
- WORLD INTERACTION: `moveMinutes()` and `doMove()`.
- PERSISTENCE: removing the old cap on load.
- RENDERING: `renderInventoryPanel()`'s header.

STAMINA / FATIGUE itself is unchanged. Movement declares more Exertion and
the system handles it as it handles any other.

## UI changes

- **Inventory tab header** shows the player's load against the limit:
  `9.40 / 13 kg`, in the format the bag tabs already use.
  - At or under 13 kg it is the normal colour.
  - Over 13 kg it takes `var(--warn)`.
  - From 26 kg, where moving starts to cost Health, it takes
    `var(--danger)`.
- **Bag tab headers** are unchanged: the bag's own fill against its own
  capacity (`4.20 / 12 kg`), whatever its factor. **Keychain** is unchanged
  (`x kg`).
- **Move buttons** show longer times while over the limit, through
  `exitMinutes()`.
- **Log:** "You can't carry any more." when Take or Equip is refused at the
  hard limit. "Something in your back twinges under the weight." on a move
  at or above 26 kg.

## Dependencies / issue linkage

Closes #168 and #170. It depends on `handoffs/here-panel-tabs.md` (#169, #188,
#197) having shipped. See "Precondition".

File anything that surfaces during implementation. Nothing is expected to be
deferred.

## Validation the coding session should show

- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  listed above.
- **Load arithmetic:** a new game reads `0.05 / 13 kg`, the keychain alone.
  - Equip an empty backpack: 0.05 + 0.6 × 0.72 = 0.48.
  - Fill it to 12 kg: 9.12.
- **The bands, at a fixed 100 m walk:**
  - at 13 kg the time is unchanged;
  - at 22.75 kg it is 1.6×, since speed is 0.625×;
  - at 32.5 kg it is 4×.
  - Exertion and Health follow the formulas.
  - At 25.9 kg no Health is lost. At 26 kg it drops 0.1 per minute moved.
- **The hard limit:**
  - At 32 kg, taking a 1 kg item says "You can't carry any more." and moves
    nothing.
  - Crafting at the limit drops the result to the floor.
  - Equipping a loaded bag from the floor that would pass 32.5 kg is refused.
  - Unequipping a full duffel at 30 kg succeeds and takes the load past 32.5 kg.
- **Hidden caps:** set loose weight near 100 kg in the console; Take is
  refused with the room message. Both caps are absent from every header.
- **An old save:** a v0.7.2 save with `inventory.capacityKg:3` loads, has no
  `capacityKg` on the inventory afterwards, and can take past 3 kg loose.
- **Death:** moving at 32.5 kg with low Health can end the run, and the
  game-over screen follows.

## Open questions for Tom

None.

## After implementation

Open one pull request carrying:

- the PATCH bump;
- a `CHANGELOG.md` entry naming `handoffs/carry-load.md` and recording the
  implementation decisions and the retunable values;
- `Closes #168` and `Closes #170`;
- this file moved with `git mv` to `handoffs/archive/carry-load.md`.
