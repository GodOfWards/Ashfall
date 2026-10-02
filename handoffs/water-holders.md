# Ashfall Handoff — Water holders: a bucket, a canteen, a pantry water jug and a 20 L dispenser jug

Current shipped version: v0.12.0
Implied version-change type: PATCH
Issue: #394 — New water holders — a bucket, a canteen, a pantry water jug and a 20 L dispenser jug

## What this is

A content pass on #47's fluid model, as #394 describes it: "Data only:
definitions, spawn pool entries, placements." Four new holders, so the player
can carry more water than a few bottles and a pot, and so there is stored
water to find once the taps fail. No rule changes.

## Relevant existing state

Verified against `main` at v0.12.0 (`GAME_CONFIG.VERSION = "0.12.0"`). Line
numbers are approximate; find code by identifier.

- **Holders** (`docs/systems/fluids.md`): an `ITEM_REGISTRY` entry with
  `holdsFluid:{ capacityMl }` is a holder. Its instance's `fluid:{ kind, ml }`
  is absent when empty. Every fluid action (fill at a sink, drink, pour, pour
  out, auto-drink) already works on any holder, so nothing in ACTIONS needs
  touching. `validateItemRegistry()` checks that each `capacityMl` is a whole
  number above 0.
- **Existing holders** (~1084–1174): `plastic_bottle` (Food, 0.05 kg, 500 mL,
  `verb:"Drink"`), the saucepans and `cooking_pot` (Tool, with `vessel`), and
  `thermos` (Misc, 0.65 kg, 1,000 mL, with a one-line sourcing comment). The
  thermos is the model for a new holder's entry and comment.
- **`verb`** is read only by food's Eat path (`consumeActions()`,
  `consumeFromList()`). Drinking from a holder goes through `drinkable()` and
  needs no verb, so the new holders carry none.
- **`STACKABLE`** (~501) is `Food`, `Medical` and `Materials`. A Misc holder
  never stacks; a Food holder stacks with its own kind at the same kind and
  millilitres (`sameStackState()`).
- **`SPAWN_POOLS`** (~1439): a full bottle is written
  `{ itemId:"plastic_bottle", state:{ fluid:{ kind:"clean", ml:500 } }, … }`.
  The comment above the table lists every entry whose chance is chosen rather
  than derived, as retunable exceptions. **Pool rolls ignore a container's
  `capacityKg`** (`rolledPoolFor()`), and so do hand placements. Only storing
  checks capacity.
- **Who draws which pool** (~3970–3985, and the landmark instances):
  `cleaning_supplies` is drawn by the row house's laundry shelf, the
  under-basin cupboard (`BATHROOM_CONTAINERS`) and the corner store's Storage
  Room. `hardware_store` is drawn by the building-materials yard (`corralon`).
  `outdoor_camping` is drawn by the goods shed's crates.
  `kitchen_nonperishable` is drawn by every home's cupboards and the
  pharmacy's back-room cabinet. `retail_stock_food` is drawn by the corner
  store's Shelves and Storage Room.
- **Hand placements:** a room spec's `floor:[ { id, qty, overrides? } ]` and a
  container's `items`, built by `itemsFromRegistry()` in `buildBuilding()`.
  An instance's `overrides.rooms[role]` is laid over the type's room with
  `Object.assign`, so an override that sets `floor` replaces the type's floor,
  and one that sets `containers` replaces its containers.
- **Generated casas** (`generatedHomes()`, ~4323): one per mid stop but the
  home stop, `id = "h_" + stop id`. `hasOldBoard()` decides an old fuse board
  by `stableHash(id + KEY_SEP + "board") % 100 < OLD_BOARD_PCT`, and
  `oldBoardOverrides()` then sets `rooms.living` and `rooms.kitchen`
  (`containers`). The door uses `stableHash(id)` alone, against
  `HOME_LOCKED_PCT`.
- **Floors** (`floorCap`): casa kitchen 50, row-house kitchen 50, police
  station front desk 60 (the `comisaria` layout), `galpon` office 40,
  `shop_home` shop 60. Every placement below stays within its floor's cap.
- **The player's home** (`landmarkInstances()`, id `home`): its kitchen
  override sets `desc` and `items` (stove, cupboards, drawers, fridge), with
  no `floor`. The cupboards (15 kg) hold about 5.6 kg as placed.
- **Carrying:** past `CARRY_LIMIT_KG` (13) moving slows and costs. Nothing may
  add load past `CARRY_HARD_LIMIT_KG` (2.5×). A full dispenser jug (about
  20.8 kg) is carried under the existing overload rules, with nothing new.
- **Saves** (`savedRoomState()`) record what differs from a freshly built
  world. A v0.12 save therefore finds the new placements in any room whose
  floor or containers it never changed, and the new pool entries in any
  container not yet opened. That is expected, and the save shape doesn't
  change.

**Reference figures** (`docs/canon/reference/Water_Holders.md`, #393; quoted
because the coding session doesn't read the reference folder):

| Holder | Capacity | Empty weight | Status |
|---|---|---|---|
| Bucket (*balde*) | 10 L, the standard household size | 0.4–0.5 kg, no lid, HDPE or PP | Secondary |
| Canteen (*cantimplora*), military-style plastic with a nesting aluminium cup and a cloth cover: the type Argentine shops list most | 1,000 mL | 0.35–0.4 kg (0.4 kg from an Argentine shop) | Secondary |
| Pantry jug (*bidón*), single-use PET, still water, the size a household keeps: 6.25 L | 6.25 L | 87–94 g body only (Confirmed); about 0.1 kg with handle and cap (Unconfirmed) | — |
| Dispenser jug (*bidón*), returnable 20 L, delivered full to homes and offices for a dispenser | 20 L | 0.75–0.82 kg | Secondary |

## Rules / mechanics

None. Everything below is WORLD DATA.

### The registry entries (ITEM_REGISTRY)

Four entries, each a plain holder: no `verb`, no tags, no rule. Each gets a
one-line comment giving its figure and status, as the thermos's does. Every
weight is a judgment call within the reference range, retunable.

| id | name | category | unitWeight | holdsFluid.capacityMl |
|---|---|---|---|---|
| `bucket` | `"Bucket"` | `"Misc"` | 0.45 | 10000 |
| `canteen` | `"Canteen"` | `"Misc"` | 0.4 | 1000 |
| `water_jug` | `"Water jug"` | `"Food"` | 0.1 | 6250 |
| `dispenser_jug` | `"Dispenser jug"` | `"Food"` | 0.8 | 20000 |

Both jugs are Food, as `plastic_bottle` is: bought as water, and stackable.
The bucket and canteen are Misc, as the thermos is.

### Pool entries (SPAWN_POOLS)

Every chance is chosen, not derived. Each is added to the exceptions list in
the comment above `SPAWN_POOLS`, as retunable.

| Pool | Entry | chance | qty |
|---|---|---|---|
| `cleaning_supplies` | `bucket`, empty | 0.25 | 1–1 |
| `hardware_store` | `bucket`, empty | 0.20 | 1–1 |
| `outdoor_camping` | `canteen`, empty | 0.25 | 1–1 |
| `kitchen_nonperishable` | `water_jug`, `state:{ fluid:{ kind:"clean", ml:6250 } }` | 0.25 | 1–2 |
| `retail_stock_food` | `water_jug`, `state:{ fluid:{ kind:"clean", ml:6250 } }` | 0.30 | 1–2 |

Each new entry goes at the end of its pool's list, so earlier entries keep
their order. The full jug's `ml` is the registry's capacity: write it so it
can't drift from `capacityMl` (read from `ITEM_REGISTRY.water_jug`, or one
named constant both use). Which way is the coding session's choice; record it
in the changelog.

**The dispenser jug is never a pool entry.** Full, it outweighs most
containers, and rolls ignore capacity.

### Hand placements (WORLD DATA)

All on floors, all `{ id:"dispenser_jug", qty, overrides:{ fluid:{ kind:"clean", ml } } }`
unless noted. Every fill is a judgment call, retunable (Tom, 2026-10-02: in
use at a home or an office, so part-drunk; full and sealed where a shop
stocks them).

| Where | Placement | ml |
|---|---|---|
| The player's home (`home`), kitchen | `floor`, 1 | 12000 |
| The player's home, kitchen `cupboards` | one `water_jug` added to the existing list, full (6,250 mL) | 6250 |
| The police station (`comisaria`), the `desk` room | `floor`, 1 | 8000 |
| The repair shop (`mechanic`), `office` | `floor`, 1 | 5000 |
| The paper mill (`paper_mill`), `office` | `floor`, 1 | 14000 |
| The corner store (`almacen`), `shop` | `floor`, qty 2 | 20000 (full) |
| Generated casas, by the roll below, kitchen | `floor`, 1 | 10000 |

**The neighbours' row house (`row_neighbour`) gets none.**

**The casa roll.** A new constant beside `OLD_BOARD_PCT`:

```js
// The share of generated casas whose kitchen has a 20 L dispenser jug
// standing on the floor, in percent, by a stable roll of the building's id
// (generatedHomes()). Tom's figure, retunable.
const DISPENSER_JUG_PCT = 30;
```

Every generated casa, the barrio's included, has one when
`stableHash(id + KEY_SEP + "jug") % 100 < DISPENSER_JUG_PCT`. The key is the
id and `"jug"`, so the roll is independent of the door's (bare id) and the
board's (`"board"`). Give it a predicate like `hasOldBoard()`. The jug's
`ml` for a casa (10,000) and for each landmark above are per-instance
content, so literals are fine (`02-code-practices.md`, One source of truth).

An old-board casa's overrides already set `rooms.kitchen.containers`. The
jug's `rooms.kitchen.floor` must merge with them, never replace them: both
kitchen fields survive on a casa that has both an old board and a jug.

## Design decisions to make during implementation

- **How the full water jug's `ml` follows its capacity** (see Pool entries):
  read from the registry, or a shared constant. Either is fine. Record the
  pick.
- **Where `DISPENSER_JUG_PCT` sits:** beside `OLD_BOARD_PCT` (recommended) or
  beside `generatedHomes()`. Record the pick.

## Data / schema changes

- PLAYER STATE: none.
- Item schema: none. Four new registry entries using existing fields.
- Room and container schema: none. New placements and pool entries only.
- One new constant, `DISPENSER_JUG_PCT`.

## In scope

- [ ] The four `ITEM_REGISTRY` entries, each with its sourcing comment.
- [ ] The five pool entries, and the `SPAWN_POOLS` comment's exceptions list.
- [ ] The six landmark placements, and the home cupboards' water jug.
- [ ] `DISPENSER_JUG_PCT`, its predicate, and the casa kitchen jug, merged
      with the old-board overrides.
- [ ] `docs/systems/fluids.md`: the Purpose sentence's list of holders names
      the new ones (no numbers, as the doc's rules require).
- [ ] Checks, in headless Chromium (`file://`, `window.ashfallDev`, read-only):
  - `validateItemRegistry()` clean.
  - `validateReachability()` reports no dead pool and no unreachable item,
    with `dispenser_jug` hand-placed.
  - `validateBuildings()` clean.
  - `simulateSeed()` on a few seeds shows the placements above, and a
    dispenser jug in about 30% of casas. The same casas in every seed.
  - In play: the home's kitchen floor shows the dispenser jug with its meter;
    Drink, Pour… and Pour out the water work on it and on a water jug; a
    bucket fills at a sink.
  - The replay page (`?replay`) and the benchmark (`?bench`) pass.
- [ ] The wrap (`docs/03-workflow.md`): PATCH bump, changelog entry with
      a **New content** section, this handoff archived, `Closes #394`.

## Explicitly out of scope

- **Fill and pour time by volume**: #411. Filling a bucket is instant, as
  every fill is today.
- **The 12 L dispenser jug**: its empty weight is Unconfirmed.
- **A dispenser appliance**, a bucket's lid, spilling while walking, a jug too
  heavy to pour from: separate `mechanic` issues, if ever.
- **`galpon` pools and wiring** (#308), **the water network** (#300),
  **potability and the river** (#52).
- `plastic_bottle`'s `verb`, which no holder path reads: leave it.

## Sections touched

Content only: ITEM DATA (`ITEM_REGISTRY`, `SPAWN_POOLS`) and WORLD DATA
(`landmarkInstances()`, `generatedHomes()`). The coding session can skip
everything else.

## Systems docs

Read `docs/systems/fluids.md`. Update its Purpose sentence in the same pull
request.

## UI changes

None. The new holders show through the existing rows, groups, meters and
fluid actions.

## Dependencies / issue linkage

- Fulfils #394.
- Built on #47 (shipped in v0.12.0) and #393 (the figures).
- Deferred: #411 (fill time). Nothing else is expected to be deferred. If the
  pass surfaces anything, file it at the wrap.

## Open questions for Tom

None.
