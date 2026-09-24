# Ashfall Handoff — The cooking release

Current shipped version: v0.7.5
Implied version-change type: MINOR — one bump for the whole release, one `SAVE_KEY` rotation
Issues (closed by this release's PR):
  #206 — Pressing Enter on a Here or Inventory tab drops keyboard focus to the page
  #167 — Disassemble checks `it.itemId === "campfire_kit"` and restates the recipe
  #210 — Dismantling a campfire refunds a baseline of 1 firewood plus the whole firewood left in its fuel
  #218 — The default start moves to a few days after the collapse
  #178 — Passive cooking
  #213 — Stove timer
  #48  — Spoilage
  #121 — Rationing
  #119 — Reachable crafting
  #120 — Two-stage cooking
  #162 — Crafting panel: a search bar and filter options
  #215 — Dishes

## What this is

One MINOR release that turns food into something the player manages over time.
Tom's direction for it: "Whatever it costs, we can manage to organize it in a
way that this release doesn't get messy … I plan not to release another
version until we finish this MINOR rotation, so let's make it count."

It is **one handoff, implemented in the order below, on one branch, shipped as
one version with one changelog entry and one pull request.** Tom manages the
branch: work continues on it until every phase passes its checks, and only then
is it merged. The release may take more than one coding session. A session
picking it up mid-way finds where the last one stopped from the branch's commit
log (see "How to work through this").

What ships, in one line each:

- three small fixes (#206, #167, #210);
- a world clock that knows the run starts **2 days after the collapse** and that
  **power and running water fail on day 21**, plus the room text that has to
  agree with it (#218);
- the one illness becomes **food poisoning**, shaped so other illnesses can be
  added later;
- **cooking changes an item's state, not the item**: "Fish (Raw) (Fresh)"
  becomes "Fish (Cooked) (Fresh)" by sitting in a lit stove or campfire, with no
  Cook button (#178);
- the stove gets an **analog timer** that rings through the building (#213);
- food goes **Fresh → Stale → Rotten**, slowed by fridges and stopped by freezers
  while they work (#48);
- food can be **eaten by the half and the quarter** (#121);
- **plastic bottles** hold clean or tainted water, fill at **sinks**, and are
  drunk the same way food is eaten;
- crafting reaches **the room, not only your pockets**, lands its output on the
  floor, gains a **Preparation** group (filleting a fish) and a searchable,
  filterable panel (#119, #120, #162);
- **dishes**: pots, saucepans, frying pans and roasting pans hold ingredients and
  water, and the vessel plus its contents decide the dish (#215).

## How to work through this

- **Order is fixed.** Each phase depends on the ones before it. Do not start a
  phase until the previous phase's checks pass.
- **One commit (or more) per phase**, each commit message starting
  `Phase N:` (for example `Phase 3: passive cooking`). A session resuming the
  work runs `git log --oneline` on the branch, finds the last `Phase N:` commit
  whose checks it can re-run and pass, and continues from `N + 1`. Re-run that
  phase's checks before trusting it.
- **Checks** are run in headless Chromium (Playwright is pre-installed in the
  cloud environment; drive `ashfall.html` from a `file://` URL) and through the
  dev seam (`window.ashfallDev`). Each phase lists what to verify. A check that
  needs a game state the UI can't reach quickly may be set up by script inside
  the page, for example by running actions and advancing time through the
  game's own buttons. Do **not** add a debug hook to `ashfall.html` for it:
  the dev seam stays read-only.
- **Version bump, changelog entry and archive move happen once, in Phase 10.**
  Intermediate phases do not bump `GAME_CONFIG.VERSION`.
- **Prove "no behavior change" where a phase claims it** with
  `git diff origin/main...HEAD -- ashfall.html`, per `CLAUDE.md`.
- **Line numbers below are approximate** (v0.7.5). Find code by identifier.

## Relevant existing state

Verified against `main` at v0.7.5 (`GAME_CONFIG.VERSION = "0.7.5"`, `SAVE_KEY =
"ashfall_save_v0.7"`).

### Time, vitals, illness
- `state.totalMinutes` starts at 0; `DAY_START_MIN = 8*60`; `dayNumber()` counts
  days from the start of the run. Nothing knows how long ago the collapse was.
- Time passes only through `runAwakeStep()` (inside `advanceTime()`),
  `doRest()` and `doSleep()`. All three step in `dt ≤ 1` minute and call
  `applyHungerThirst(dt)` and `applyWorldTicking(dt)` every step (~4939, ~4954,
  ~5086, ~4771, ~4788).
- `applyWorldTicking(min)` drains powered items through `forEachItemList()` and
  burns campfire fuel (`room.fireMinutesLeft`) for every room. A stove has
  `heatActive` and no `fireMinutesLeft`: it never runs out.
- `forEachItemList(visit)` (~5329) calls `visit(list, roomId)` for the inventory
  pools, every room's floor, containers, car containers, and any item's
  `contents` to any depth. It does **not** tell the visitor which container a
  list belongs to.
- Illness: one timer, `state.illnessMinutesLeft`. `ILLNESS_DURATION_MIN = 180`,
  `ILLNESS_MINUTES_PER_HEALTH = 20` (~4931). Its only cause is `doConsume()`
  rolling the item's instance `illnessChance` with
  `chance(p, "illness", state.rollSeq)`, advancing `rollSeq` on every roll, and
  starting the timer only if none is running. Onset line: "It doesn't sit right.
  You can feel it already." (warn). `rollSeq`'s invariant (~3770): nothing
  reachable from `render()` may advance it.
- `backfillIllnessScale()` repairs pre-0.6 percent values of instance
  `illnessChance`.

### Items and stacks
- `ITEM_REGISTRY` (~673) is the only item definition. `itemFromRegistry()` deep-
  copies an entry onto an instance, so every instance carries copies of
  `restores`, `verb`, `illnessChance`, `tags` and so on. `tags` are resynced
  from the registry on load (`backfillRegistryTags()`); nothing else is.
- `STACKABLE = Food, Medical, Materials`. `addToList()` (~4073) merges a
  stackable, non-durability item into a row with the same `itemId`, `category`
  and `!!sealed`. It deep-clones and strips `_uid` on a new row.
- `doTake`, `doStore`, `doConsume`, `doOpen`, `doEquip` resolve their list from
  the **current tab** (`worldSlot(room, worldTab)` / `invSlot(invTab)`), never
  from the clicked item. `getItemActions(list, index, side)` (~4461) builds the
  pop-up's buttons; Take/Store All / Half / 1 exist for splittable stacks.
- `doConsume()` eats exactly one unit, adds `restores.hunger/thirst` through
  `clamp()`, logs `You ${verb} the ${name}.` with key `consume:<itemId>`.
- `doOpen()` splits one unit out of a sealed stack as `sealed:false`; rows show
  " (Open)" after the name (`renderItemList()`, ~6925). The pop-up shows
  "Sealed"/"Opened".
- `itemUnitWeight(it)` (~4064) is "the only place an item's weight is
  computed": `unitWeight` plus `contents`.
- Food today (Food category): canned soup, beans, corn, tuna, pet food, baby
  formula (sealed, `opensWith:"can-opening"`); cereal, peanut butter, dry pet
  food (sealed, open by hand); pasta (hunger 30, edible), rice (no `restores`),
  granola bars, crackers, chips, candy bar, bottled water (thirst 30, "Drink"),
  coffee grounds (inert), `cooked_fish` (hunger 35), `raw_fish` (hunger 10,
  `illnessChance:0.35`), and three inert spoiled foods: `spoiled_milk`,
  `moldy_bread`, `rotten_produce`. Two more inert spoiled items are Misc:
  `rotten_leftovers`, `pot_of_spoiled_stew`.
- Vessel-shaped items: `frying_pan` (Tool, `blunt`, 0.9), `dented_saucepan`
  (Tool, 0.7), `burnt_saucepan` (Misc, 0.6), `kids_plastic_bowl` (Misc).
- The `blade` tag exists (kitchen knife, box cutter, hand axe, combat knife) and
  nothing reads it. The ITEM DATA SCHEMA comment lists it as "declared, with no
  consumer yet".

### Spawning
- `SPAWN_POOLS` (~922) entries are `{ itemId, chance, qtyMin, qtyMax }`. Rolls
  are keyed on `["loot", roomId, containerId, poolId, itemId]` (and `"qty"`), so
  a pool must not list one `itemId` twice (`validateReachability()` reports it).
  Chances are derived six-decimal figures; only the screwdriver's two are chosen.
- Rolling is lazy: `doOpenContainer()` (~4914) appends `rolledLootFor()`'s
  yield the first time a container's tab is opened. `rolledLootFor()` is pure
  (seed as argument). Hand-placed containers carry `spawnRolled:true`.
- `kitchen_perishable` (~923): rotten_leftovers 0.129032, spoiled_milk
  0.096774, moldy_bread 0.096774, rotten_produce 0.080645, pot_of_spoiled_stew
  0.064516, raw_fish 0.016129, cooked_fish 0.016129; `emptyChance 0.3`. It is
  drawn by fridges **and by every stove**.
- `bottled_water` is in `kitchen_nonperishable` (0.193774, 1–3) and
  `retail_stock_food` (0.309252, 1–3), and hand-placed in the 2A pantry (4),
  the 1A kitchen shelf (3) and one more placement (~1907, qty 5).
- `kitchen_tools` (~945): can_opener, frying_pan, kitchen_knife,
  dented_saucepan, burnt_saucepan.

### The kitchens and bathrooms
Only three rooms have `room:"Kitchen"` and three `room:"Bathroom"`, all in Acorn
Apartments, none with a `searchLabel`:

| Room id | Containers today |
|---|---|
| `kitchen` (2A) | `stove` (device, heat; hand-placed `pot_of_spoiled_stew`), `cabinets`, `drawers`, `fridge` (hand-placed `rotten_leftovers`), `pantry` (bottled water ×4) |
| `twobee_kitchen` (2B) | `stove` (burnt saucepan), `cabinets`, `drawers`, `fridge` (unrolled), `pantry` (unrolled) |
| `onea_kitchen` (1A) | `stove1a` (kids' plastic bowl), `kitchen1a` (bottled water ×3), `fridge1a` (hand-placed `rotten_leftovers`) |
| `bathroom`, `twobee_bathroom`, `onea_bathroom` | medicine cabinet, under-sink cabinet (1A has no under-sink) |

The superintendent's unit `onebee` has a stove but is not a kitchen room.

### Fire and cooking
- `HEAT_RECIPES` (~475) holds `cook_fish` (raw_fish → cooked_fish, 15 min).
  `renderHereActionsPanel()` (~7332) offers "Cook the …" while `room.heatActive`
  and `getHeatContainer(room)` (first container tagged `heat`) holds the input;
  `doCookInContainer()` swaps one unit and calls `advanceTime(recipe.minutes)`.
- Stove: `roomStove(room)` = container tagged `device` + `heat`. Lit by
  `doLightStove()` (a fire-starter use, `LIGHT_STOVE_MIN`), turned off by
  `doExtinguish()`, both from `renderDevicePanel()` (~7142), whose status line
  reads "On"/"Off". The Here panel header shows **Device Options** beside the
  weight while the stove's tab is selected (`renderWorldItemsPanel()`, ~7449).
- Campfire: `doBuildFire()` sets `heatActive` **before** `advanceTime(BUILD_FIRE_MIN)`,
  so the fire burns during the build. `doDismantleCampfire()` (~5256) refunds a
  flat `Math.ceil(CAMPFIRE_KIT_COST/2)` firewood and requires the fire to be out.
- `doFish()` gives `raw_fish`.

### Crafting
- `RECIPES` (~467): bandage (cloth ×2, duct tape ×1, 5 min), campfire kit
  (firewood × `CAMPFIRE_KIT_COST`, 15 min). `canCraft()`/`doCraft()` (~5121)
  count and consume only `invPools()`; output goes through `giveItem()` →
  `addToDestination()`, which delivers to **whichever inventory tab is open**.
  `recipe.tool` and `recipe.needsHeat` are read but no recipe sets them.
- `renderCraftingPanel()` (~7068) lists every recipe, unavailable ones disabled
  with "(needs …)", by design a catalogue. The panel markup is `#craftingPanel`
  with `#craftingList` and `#craftResult`.
- Disassemble (~4524): `it.itemId === "campfire_kit"` → gives
  `CAMPFIRE_KIT_COST` firewood, logs "You untie the bundle — back to 3 loose
  firewood." The dev-helper comment `ACTION_GRANTED_ITEM_IDS` (~5676) names "the
  campfire kit's Disassemble".

### Focus
- `rebuildKeepingFocus(root, rebuild)` (~6079) restores focus by label, then by
  position, **but returns early unless `root` is an open layer**
  (`layerOpen(root)`). `renderInventoryPanel()` and `renderWorldItemsPanel()`
  rebuild `#invTabs` / `#worldTabs` with `innerHTML = ""`, and neither strip is
  a layer.

### Persistence
- Save = `{ version, state, world, doors, windows }`. `applyLoadedData()` (~5545)
  validates shape, then runs the backfills in order. A version mismatch only
  warns. `doRestart()` rebuilds the world and state; the initial boot uses the
  module-level `world = makeDefaultWorld()` / `state = makeDefaultState()`.
- `makeDefaultWorld()` is also called by backfills and dev helpers, so it must
  stay free of state-dependent work.

### Room text that contradicts the new start
`:1400` "dead television", `:1419` "The fridge hums no more…", `:1443` "The
water hasn't run in days…", `:1621` and `:1739` calendars "two months", `:3426`
"The crossing lights are dead".

---

## Global rules and constants

New named constants, in CONFIG / CONSTANTS unless a phase says otherwise. All
are **retunable** balance values unless marked as identities.

| Constant | Value | Meaning |
|---|---|---|
| `START_DAYS_AFTER_COLLAPSE` | `2` | A run starts this many days after the collapse. |
| `POWER_FAILS_DAY` | `21` | Grid power fails this many days after the collapse. |
| `WATER_FAILS_DAY` | `21` | Running water fails this many days after the collapse. Separate constant on purpose: the two will be set separately (#149). |
| `FRIDGE_RATE_POWERED` | `0.1` | Spoilage rate in a fridge while powered. |
| `FRIDGE_RATE_COASTING` | `0.25` | Rate in a fridge after the power fails, for `FRIDGE_COAST_MIN`. |
| `FRIDGE_COAST_MIN` | `2 * MINUTES_PER_DAY` | |
| `FREEZER_COAST_MIN` | `5 * MINUTES_PER_DAY` | A freezer stops spoilage while powered and for this long after. |
| `ROTTEN_RESTORES_FACTOR` | `0.35` | Rotten food restores this fraction. |
| `ROTTEN_POISONING_CHANCE` | `0.35` | Baseline food-poisoning chance of rotten food. |
| `POISONING_TRAIT_MULTIPLIER` | `1` | Placeholder until traits (#9) exist. Multiplies the rotten baseline only. |
| `TAINTED_WATER_POISONING_CHANCE` | `0.35` | For a full bottle's worth, scaled by the amount drunk. |
| `BOIL_MINUTES` | `5` | Tainted water in a heated vessel becomes clean after this. |
| `DISH_RESTORES_BONUS` | `0.25` | A dish restores its ingredients' sum × (1 + this). |
| `STOVE_TIMER_STEPS` | `[5, 10, 30]` | The stove timer's add buttons, in minutes. |
| `CAMPFIRE_DISMANTLE_BASE_WOOD` | `1` | (Phase 1.) |

Helpers every phase may use (names are the session's; shapes are not):

- **`minutesSinceCollapse()`** = `START_DAYS_AFTER_COLLAPSE * MINUTES_PER_DAY +
  state.totalMinutes`. Derived, never stored.
- **`powerOn(m)`** = `m < POWER_FAILS_DAY * MINUTES_PER_DAY`;
  **`waterRunning(m)`** = `m < WATER_FAILS_DAY * MINUTES_PER_DAY`; both default
  `m` to `minutesSinceCollapse()`.
- **`restoresValue(r)`** = `(r.hunger || 0) + (r.thirst || 0)`: the one scalar
  measure of "how much a food restores", used to rank and share (dishes).
- **`combinePoisoning(a, b)`** = `1 - (1 - a) * (1 - b)`.

The clock display (`Day N`, time of day) is **unchanged**: it still counts from
the start of the run.

---

## Phase 1 — Small fixes (#206, #167, #210)

Independent of everything after. No new state.

### #206: tab strips keep focus
- Rebuild `#invTabs` and `#worldTabs` so that focus stays on the rebuilt tab
  with the same label, or falls to the tab at the same position when that tab
  is gone (a floor bag taken with Take All). That is `rebuildKeepingFocus()`'s
  existing fallback.
- `rebuildKeepingFocus()` currently returns early for any root that is not an
  open layer. Either apply its layer guard only to roots that are layers, or add
  a sibling for non-layer roots sharing the label-then-position fallback. Which
  is an implementation choice (record it). It must still do nothing when focus
  was not inside the root before the rebuild.
- Labels are unique within each strip today (Here tabs number duplicate names:
  "Purse", "Purse 2").

### #167: Disassemble from a tag and the recipe
- New tag **`disassemble`** on `campfire_kit` only (definition data; saved kits
  get it through `backfillRegistryTags()`).
- Disassemble is offered for any item carrying the tag **and** for which a
  `RECIPES` entry has `output.id === it.itemId`. It removes one unit and gives
  back **every input of that recipe at its full quantity** through
  `giveItem(itemFromRegistry(...))`.
- The log line comes from a registry field on the item, **`disassembleLog`**,
  a string in which `{qty}` is replaced by the first input's quantity. The kit's:
  `"You untie the bundle — back to {qty} loose firewood."` (the current text,
  unchanged in play). An item without the field logs `"You take the {name}
  apart."` with the lowercased item name (retunable wording).
- Remove the `it.itemId === "campfire_kit"` branch.
- Add `disassemble` to the ITEM DATA SCHEMA's "read by a mechanic today" list,
  and reword `ACTION_GRANTED_ITEM_IDS`'s "the campfire kit's Disassemble" to
  "Disassemble, which returns a `disassemble`-tagged item's recipe inputs".

### #210: Dismantle refund
- `doDismantleCampfire()` refunds
  `CAMPFIRE_DISMANTLE_BASE_WOOD + Math.floor((room.fireMinutesLeft || 0) / FIRE_MINUTES_PER_WOOD)`.
  A burnt-out campfire gives 1; 1.5 firewood's worth of fuel gives 2.
- Comment beside `CAMPFIRE_DISMANTLE_BASE_WOOD`: with today's values the
  build → put out → dismantle cycle breaks exactly even (n firewood in, n out),
  **only because `doBuildFire()` burns the fire during `BUILD_FIRE_MIN` and the
  baseline is ≤ 1 unit of fuel**. Raising the baseline or making the build free
  turns the cycle into a firewood source.
- The log line is unchanged ("You break down the campfire, salvaging N firewood
  from it.").

### Checks — Phase 1
- Tab to a Here tab and press Enter: focus is on the same tab afterwards. Same
  for an Inventory tab. Take All on a floor bag while its tab is focused: focus
  lands on the tab now at that position.
- Disassemble a campfire kit: +3 firewood, same log line as v0.7.5. Temporarily
  change `CAMPFIRE_KIT_COST` in a scratch copy: Disassemble follows it.
- Dismantle: fire burnt out → 1 firewood. Build from a kit, put out at once,
  dismantle → 3 firewood (170 minutes of fuel: 1 + 2).
- `ashfallDev.validateItemRegistry()` and `validateReachability()` report
  nothing new.

---

## Phase 2 — Foundations

### 2a. The collapse clock, power and water
- Add the constants and helpers from "Global rules". Nothing else reads them
  until later phases.

### 2b. Room text (#218)
Exact replacements (`desc` strings):

| Room (line ~) | New text |
|---|---|
| `living` (1400) | "A worn couch faces a dark television. Sunlight through the blinds shows how much dust has settled since anyone last cleaned." |
| `kitchen` (1419) | "Grease and old coffee grounds. The fridge still hums, though something inside it has already given up. The gas stove works too — no power needed to light it." |
| `bathroom` (1443) | "A cracked mirror over the sink. The cabinet under it is still worth a look." |
| `onea_kitchen` (1621) | "A family kitchen, cluttered with kids' cups and a permission slip on the counter that nobody signed." |
| `oak_1b` (1739) | "The blinds are drawn in here, and a mug on the desk has grown a skin of cold coffee." |
| `mid_2nd_d_mi` (3426) | "2nd St crossing the rail spur at a shallow angle. The crossing lights blink for a train that isn't coming, but the bell housing's still up there." |

Left unchanged on purpose: the Elm hedge (~2526), the church noticeboard's
"last month's service" (~2412), the rained-on rabbit (~2519). They read as
neglect from before the collapse.

### 2c. Illness becomes food poisoning
- `state.illnessMinutesLeft` is replaced by **`state.illnesses`**, an object
  keyed by illness id: `{ food_poisoning: <minutes left> }`, empty `{}` in a new
  game. A missing or 0 entry means not ill.
- **`ILLNESSES`** (SURVIVAL / TIME SIMULATION) is the one definition table:
  `food_poisoning: { durationMin: 180, minutesPerHealth: 20, onsetLog:
  "It doesn't sit right. You can feel it already." }`. `ILLNESS_DURATION_MIN`
  and `ILLNESS_MINUTES_PER_HEALTH` are removed; their values live in the table.
- `applyHungerThirst()` drains Health for every running illness by its own rate
  and counts it down.
- **`startIllness(id)`**: starts the timer at `durationMin` and logs `onsetLog`
  (warn) only if that illness is not already running (today's rule).
- **Rolling:** one helper, **`rollFoodPoisoning(p)`**: if `p > 0`, roll
  `chance(p, "food_poisoning", state.rollSeq)`, advance `state.rollSeq`, and on
  a hit call `startIllness("food_poisoning")`. Keep today's order: the roll and
  the advance happen even if already ill. Every food-poisoning source in this
  release goes through it. `rollSeq`'s invariant stands.
- **The item field is renamed** `illnessChance` → **`foodPoisoningChance`** on
  `ITEM_REGISTRY` entries, and it is **read from the registry by `itemId`**,
  never from the instance (the `carryFactorOf()` pattern), so a retune reaches
  every save. Instances no longer carry it (Phase 10 strips old copies).
- `validateItemRegistry()` checks `foodPoisoningChance` (and, from Phase 3,
  `cooks.foodPoisoningChance`) are in [0, 1].

### 2d. The item-state core
Three shared pieces that Phases 3–9 all extend. Build them now, with only
today's states, so each later phase adds one clause rather than a new mechanism.

1. **`sameStackState(a, b)`**: the one merge predicate. `addToList()` uses it
   in place of its inline test. Today it compares `itemId`, `category`,
   `!durability` and `!!sealed`. Later phases add: cook state and progress
   (Phase 3), freshness state (5), portion (6), water (7), vessel and dish
   (9).
2. **Unit helpers.** From Phase 5 on, a perishable row carries one age per unit
   (`ages`, length = `qty`). From Phase 6, a row can hold a part-eaten unit. So
   every path that changes a row's `qty` must go through two helpers:
   - **`takeUnits(row, n)`**: removes `n` units from `row` and returns a new
     item object for them (a deep copy, `_uid` stripped), taking the **oldest**
     units when the row has `ages`. The row is left with the rest.
   - **`dropUnits(list, index, n)`**: `takeUnits` plus splicing the row out of
     `list` when it reaches 0.

   Callers today: `doTake`, `doStore`, `doConsume`, `doOpen`,
   `consumeFromPools`, `consumeByTag`, the Disassemble action,
   `doDismantleCampfire`'s container spill (it moves whole rows, which is fine),
   and every later phase's new actions. In this phase they behave exactly as
   before (no row has ages yet).
3. **`itemStateLabels(it, ctx)`**: the list of parenthesised state labels shown
   after an item's name, in this fixed order:
   1. `"Open"` when `sealed === false` (today's " (Open)");
   2. cook state (Phase 3);
   3. freshness or `"Frozen"` (Phase 5);
   4. water (Phase 7).

   `ctx` carries whatever the label needs from outside the item (Phase 5: the
   container, for Frozen). `renderItemList()` shows the labels after the name
   button, in the existing `.state` span, so the button's text stays exactly the
   item's name (focus-by-label depends on it). The item pop-up's name line shows
   them too. **Log lines keep using the plain lowercased name.**

### Checks — Phase 2
- New game: identical play to Phase 1 except the six room texts. Eat a raw fish
  until ill: same onset line, Health drains 1 per 20 min for 180 min.
  `state.illnesses.food_poisoning` counts down; `state.illnessMinutesLeft` no
  longer exists.
- Take/Store All / Half / 1, Open and Eat behave as before on stacks
  (regression pass over `doTake`, `doStore`, `doOpen`, `doConsume`).
- `git diff origin/main...HEAD -- ashfall.html`: Phase 2's changes are the
  helpers, the illness reshape and the six strings. Nothing else moves.

---

## Phase 3 — Passive cooking and cook states (#178, Layer 1)

### Cook states
- A registry entry that can be cooked carries **`cooks: { minutes, restores,
  foodPoisoningChance? }`**: how long it takes, and what the **Cooked** state
  restores and risks (`foodPoisoningChance` absent = 0). The entry's own
  `restores` / `foodPoisoningChance` are the **Raw** state's.
- An instance of such an item has **`cookState`**: `"raw"` or `"cooked"`
  (absent = raw), and while raw, **`cookMinutes`**: progress (absent = 0).
- **Labels:** an item whose registry entry has `cooks` always shows its cook
  state: "(Raw)" or "(Cooked)". Other items show none.
- **Restores and poisoning are read through one helper**, `foodEffects(it)` →
  `{ restores, poisoning }`: for a cookable item, the Raw or Cooked values from
  the registry; otherwise the registry's `restores` and `foodPoisoningChance`;
  for a dish (Phase 9), the instance's. Every reader (Eat, the Eat gate, dish
  maths) uses it, never the instance's copied `restores`.
- **Merging:** `sameStackState` adds cook state, and for raw rows `cookMinutes`
  (rows with different progress never merge).

### Fish
- `raw_fish` and `cooked_fish` become one entry, **`fish`**:
  `{ name:"Fish", category:"Food", unitWeight:0.3, restores:{hunger:10},
  verb:"Eat", foodPoisoningChance:0.35, cooks:{ minutes:15,
  restores:{hunger:35} } }`. (`cooked_fish` weighed 0.35; one weight is kept.)
- `doFish()` gives `fish`, raw.
- Spawn-pool entries gain two optional fields: **`key`** (default `itemId`),
  used in place of `itemId` in the roll keys and in the duplicate check, and
  **`state`**, an object of instance fields applied after `itemFromRegistry()`.
  `kitchen_perishable`'s `raw_fish` entry becomes `{ itemId:"fish", ... }` and
  its `cooked_fish` entry `{ itemId:"fish", key:"fish_cooked",
  state:{ cookState:"cooked" }, ... }`, both at their current chances.
  `validateReachability()` checks duplicates by key.
- Every other reference to `raw_fish` / `cooked_fish` (`ACTION_GRANTED_ITEM_IDS`,
  validators, comments) moves to `fish`.

### The cooking tick
In `applyWorldTicking(dt)`, for every room with `heatActive`, for every
container tagged `heat` in it, for every item directly in `c.items`:
- if its entry has `cooks` and it is raw: `cookMinutes += dt`. When
  `cookMinutes >= cooks.minutes`: `cookState = "cooked"`, delete
  `cookMinutes`, and (from Phase 5) reset every unit's age to 0: **cooked food
  starts Fresh**. Then re-merge the row into its list (so two cooked rows of
  fish become one), without disturbing `_uid` of rows the player may have open.
- **The counter stops at completion** in this release. Burning (#179) will
  extend it later.
- **When the heat stops**, progress holds. **An item taken out** keeps its
  progress, and put back in, continues from there.
- **No log line** when something finishes, anywhere. Knowing is the player's
  job (the timer, Phase 4, or the Wait button below).
- Vessels inside the heat container are Phase 9's.

### "Wait until the … is cooked"
Replaces the "Cook the …" buttons in `renderHereActionsPanel()`.
- Offered while `room.heatActive` and the room's heat container holds something
  still progressing: a raw cookable item, and from Phase 9 a vessel's forming
  or raw dish, or tainted water boiling.
- It targets **the soonest to finish**: the least remaining time among them.
  - Label: `Wait until the <name> is cooked`, where `<name>` is the item's (or
    dish's) lowercased name. For water: `Wait until the water boils`.
  - Cost shown the usual way (`fmtDuration(remaining)`).
- **Offered only if the heat will last:** always for a stove; for a campfire
  only when `room.fireMinutesLeft >= remaining`.
- Clicking it runs `advanceTime(remaining)`, which is not interruptible (#212),
  logs "You keep an eye on it." with key `"wait"` (plain; wording retunable),
  and renders.

### Removed
`HEAT_RECIPES`, `doCookInContainer()`, the Cook buttons, and every reader of
them (validators, reachability, comments).

### Checks — Phase 3
- Put a raw fish in a lit stove and walk to another room for 20 minutes: it is
  "Fish (Cooked)" when you return, and no log line said so.
- Stove off after 10 minutes, back on: it finishes after 5 more. Take it out at
  10, put it back: same.
- Two raw fish added 5 minutes apart stay two rows until both are cooked, then
  merge.
- The Wait button appears with the shortest remaining time and advances exactly
  that much. On a campfire with less fuel than needed, it is absent.
- Eat a cooked fish: +35 hunger and no poisoning roll (`state.rollSeq`
  unchanged). A raw fish: +10 and a roll.
- `validateItemRegistry()`, `validateReachability()`: clean except expected
  pre-existing lines; no `raw_fish` / `cooked_fish` anywhere.

---

## Phase 4 — Stove timer (#213)

- A stove container (tagged `device` + `heat`) carries **`timerMinutes`**
  (absent = 0).
- **Device Options** (`renderDevicePanel()`), for the stove:
  - **Status** lines "On"/"Off" (today) and **"Timer: N"**, where N is
    `Math.ceil(timerMinutes)`: "Timer: 0" when unset.
  - **Controls:** one button per `STOVE_TIMER_STEPS` entry, labelled "+5",
    "+10", "+30", each **adding** that many minutes. There is no Clear, no
    subtract and no cap: it is an analog timer. The buttons cost no game time
    and write no log line. Light / Turn off are unchanged.
- **Countdown:** in `applyWorldTicking(dt)`, every container with
  `timerMinutes > 0` counts down by `dt`, **whether or not the stove is on and
  whatever the power**. It needs neither. When it crosses 0 it is set to 0 and
  **rings**: if the player's current room has a `building` and it equals the
  stove's room's `building`, log **"You hear the ringing sound of the timer."**
  (plain class). Otherwise it rings unheard. The wording is Tom's.
- **Here panel:** while the selected Here tab is the stove, the header shows its
  state beside the weight and the Device Options button: `On · Timer: 30` /
  `Off · Timer: 0` (same N rule). Rendering only.
- The timer does not turn anything off.

### Checks — Phase 4
- +10 then +5: "Timer: 15", in Device Options and the Here header. Wait or rest
  15 minutes in the kitchen: the ring line appears once. From the 2A living
  room (same building): it appears. From the street: it doesn't, and the timer
  still reads 0 on return.
- The timer counts with the stove off.

---

## Phase 5 — Spoilage (#48)

### Perishables and states
- A registry entry that spoils carries **`spoils: { staleAfter, rottenAfter }`**
  in minutes of effective age. An item is **perishable** when its entry has
  `spoils` and it is not `sealed === true`. **A sealed item does not age.**
  Opening starts it at age 0.
- A perishable row carries **`ages`**: one number per unit, the unit's effective
  age in minutes, kept sorted oldest first, `ages.length === qty`.
- **Freshness state** of a unit: **Fresh** below `staleAfter`, **Stale** below
  `rottenAfter`, **Rotten** from there.
- **Labels:** a perishable always shows its freshness: "(Fresh)", "(Stale)",
  "(Rotten)". While the row is in a freezer whose rate is currently 0, it shows
  **"(Frozen)"** instead. Non-perishables show none.
- **Merging:** `sameStackState` adds freshness state: rows merge only when every
  unit of both is in the same state. Merging concatenates `ages` and re-sorts.
- **Effects:**
  - **Fresh:** as today.
  - **Stale:** none in this release (#216).
  - **Rotten:** restores × `ROTTEN_RESTORES_FACTOR`. Poisoning chance
    = `combinePoisoning(<the food's own chance for its cook state>,
    ROTTEN_POISONING_CHANCE * POISONING_TRAIT_MULTIPLIER)`. Rotten raw fish:
    ≈ 0.58.

### Rates and the tick
- `forEachItemList()`'s visitor gains a third argument: **the room container
  the list is in or nested under** (the authored or car container, or `null`
  for the floor, floor bags and anything carried). Existing callers ignore it.
- **`spoilageRate(container, m)`**:
  - tagged **`fridge`**: `FRIDGE_RATE_POWERED` while `powerOn(m)`, then
    `FRIDGE_RATE_COASTING` for `FRIDGE_COAST_MIN` after the power fails, then 1;
  - tagged **`freezer`**: 0 while powered and for `FREEZER_COAST_MIN` after,
    then 1;
  - anything else, including no container: 1.
- **Tick:** in `applyWorldTicking(dt)`, every perishable unit's age grows by
  `spoilageRate(container, minutesSinceCollapse()) * dt`. After ageing, a row
  whose units no longer share one freshness state is **split** into one row per
  state, oldest first, in place in its list. A split is how a unit visibly turns
  Stale on its own.
- **Cook completion** (Phase 3) resets ages to 0.

### Starting ages
- **`effectiveAge(container, fromM, toM)`** integrates `spoilageRate` over
  `[fromM, toM)` minutes since the collapse. It's piecewise: exact at the two
  power boundaries.
- **World items get the age they would have if they had sat there since the
  collapse:** `effectiveAge(container, 0, minutesSinceCollapse())` per unit.
  One pass, **`stampMissingAges()`**, walks every item list with its container
  and stamps any perishable **without `ages`**. It runs:
  1. on a new game: after the world is built, in `doRestart()` and at initial
     boot. Not inside `makeDefaultWorld()`, which must stay state-free;
  2. in `doOpenContainer()`, on the rolled items, before they're added;
  3. on load (Phase 10).
- **Items made by an action are new: age 0.** A caught fish, a fillet (which
  instead inherits the fish's age, Phase 8), an opened can, a dish.
- A placement may set `ages` through `overrides`. `stampMissingAges()` skips
  it. **The 2A fridge's leftovers are placed with `ages:[5 * MINUTES_PER_DAY]`**,
  already Rotten at the start, so the kitchen's "something inside it has
  already given up" stays true. That is the only such override.
- At the default start, 2 days in with the power on: fridge contents are ~4.8 h
  old (Fresh), freezer contents 0, and food left in a stove or cupboard is the
  full 2 days.
- **Perishables never respawn.** No respawn exists yet. Add to the CONTAINER
  SCHEMA's `lastRolledMinute` note that a future respawn (#15) must skip any
  item whose entry has `spoils`.

### Fridges, freezers, new food
- The three fridges (`kitchen.fridge`, `twobee_kitchen.fridge`,
  `onea_kitchen.fridge1a`) gain `tags:["fridge"]`.
- **Each gets a freezer beside it**, a new container:
  `{ id:"freezer", name:"Freezer", capacityKg:10, tags:["freezer"],
  spawnPools:["kitchen_frozen"], items:[] }`, with id `freezer1a` in
  `onea_kitchen`. Unrolled, so it rolls on first open. Place it straight after
  its fridge in `containers`.
- **New pool `kitchen_frozen`**, `emptyChance 0.2`:

  | Entry | chance | qty |
  |---|---|---|
  | `meat` | 0.5 | 1–2 |
  | `vegetables` | 0.5 | 1–2 |
  | `fish` | 0.3 | 1 |
  | `ice_cream` | 0.4 | 1 |

  These chances are **chosen, not derived**. Say so in the SPAWN_POOLS comment
  beside the screwdriver exception.
- **Registry changes** (weights kg; times: h = 60, d = `MINUTES_PER_DAY`):

  | Id | Entry | `spoils` stale / rotten |
  |---|---|---|
  | `fish` | (Phase 3) | 12 h / 1 d |
  | `meat` **new** | `name:"Meat"`, Food, 0.5, `restores:{hunger:10}`, "Eat", `foodPoisoningChance:0.5`, `cooks:{ minutes:20, restores:{hunger:40} }` | 12 h / 1 d |
  | `vegetables` **new**, replaces `rotten_produce` | `name:"Vegetables"`, Food, 0.5, `restores:{hunger:10, thirst:2}`, "Eat" | 2 d / 5 d |
  | `milk` **new**, replaces `spoiled_milk` | `name:"Milk"`, Food, 1.0, `restores:{thirst:20, hunger:5}`, "Drink" | 1 d / 3 d |
  | `bread` **new**, replaces `moldy_bread` | `name:"Bread"`, Food, 0.4, `restores:{hunger:20}`, "Eat" | 3 d / 7 d |
  | `leftovers` **new**, replaces `rotten_leftovers` | `name:"Leftovers"`, **Food** (was Misc), 0.8, `restores:{hunger:25}`, "Eat" | 1 d / 3 d |
  | `ice_cream` **new** | `name:"Ice cream"`, Food, 0.5, `restores:{hunger:15, thirst:5}`, "Eat" | 6 h / 1 d |
  | opened cans: `canned_soup`, `canned_beans`, `canned_corn`, `canned_tuna`, `canned_pet_food`, `baby_formula` | unchanged | 1 d / 3 d (after opening) |

  **Never spoil** (no `spoils`): water, pasta, rice, crackers, chips, granola
  bars, candy bar, cereal, peanut butter, dry pet food, coffee grounds.
- **Retired ids**: `spoiled_milk`, `moldy_bread`, `rotten_produce`,
  `rotten_leftovers`.
  - `kitchen_perishable` entries become `leftovers`, `milk`, `bread`,
    `vegetables`, at their current chances.
  - The two hand-placed `rotten_leftovers` become `leftovers`: the 2A one with
    the Rotten override above, the 1A one stamped normally.
  - **`pot_of_spoiled_stew` stays untouched until Phase 9.**

### Checks — Phase 5
- New game, open the 2A fridge: "Leftovers (Rotten)". Open the 2B fridge: rolled
  perishables read Fresh (≈4.8 h old). A stove's perishable spawn: 2 days old,
  so milk (Stale), fish (Rotten).
- Two Fresh fish, one caught 6 hours after the other, stored in the same list:
  one row while both are Fresh. When the older crosses 12 h, the row splits
  and the older one reads "(Stale)". Take 1 from a two-unit row takes the older
  unit.
- Freezer: shows "(Frozen)" while powered. Advance past day 21 + 5 (sleep/rest
  repeatedly): the label turns to a freshness state and ageing resumes.
- Rotten fish eaten: restores 3.5, poisoning chance ≈ 0.58 (check the value
  passed to `rollFoodPoisoning` by instrumenting a scratch copy, never the
  shipped file).
- Cooked fish from a Stale raw one: "(Cooked) (Fresh)".
- Validators clean; retired ids gone.

---

## Phase 6 — Rationing (#121)

- An edible unit carries **`portion`**: 1, 0.75, 0.5 or 0.25 (absent = 1).
  `sameStackState` adds portion: part-eaten units never merge with whole ones.
- **Buttons** in `getItemActions()` for edible items:
  - **`<Verb>`** eats whatever is left of one unit;
  - **`<Verb> 1/2`** only if 0.5 is **less than** what's left;
  - **`<Verb> 1/4`** only if 0.25 is **less than** what's left.

  So: whole → 3 buttons; ¾ → 3; ½ → Verb, Verb 1/4; ¼ → Verb. `<Verb>` is the
  item's `verb` ("Eat", "Drink"). **The portion itself is not shown** anywhere.
- **Which unit is eaten:** within the list the action runs on, among rows with
  the same `itemId`, cook state and freshness state, the unit with **the least
  left**; among equals, **the oldest**. Eating from a row with `qty > 1` splits
  that one unit out (`takeUnits`) and leaves it in the list with its reduced
  portion. A unit reaching 0 is removed.
- **Effects of eating amount `a`** (a fraction of one unit):
  - restores: `foodEffects(it).restores × a`, × `ROTTEN_RESTORES_FACTOR` if
    Rotten;
  - poisoning: `rollFoodPoisoning(p × a)`, where `p` is the full-unit chance
    (with the rotten combination). **Linear**: eating in bites is slightly
    safer than eating the whole, and that's accepted.
- **Log:** a whole unit: `You <verb> the <name>.` (today's). A part:
  `You <verb> some of the <name>.` (retunable). Both share today's key.

### Checks — Phase 6
- A can of soup (opened): Eat 1/4 ×4 → +25 hunger total, one row throughout,
  buttons shrink as specified.
- Two opened cans, one half-eaten: clicking either row's Eat finishes the half
  first.
- Raw fish Eat 1/2: one roll at 0.175, `rollSeq` +1.

---

## Phase 7 — Water: bottles and sinks

### Plastic bottles
- `bottled_water` is replaced by **`plastic_bottle`**: `{ name:"Plastic bottle",
  category:"Food", unitWeight:0.05, verb:"Drink", holdsWater:{ kg:0.5,
  restores:{thirst:30} } }`.
- Instance field **`water`**: `{ kind:"clean"|"tainted", fill: 1|0.75|0.5|0.25 }`,
  or absent when empty.
- **Labels:** "Plastic bottle (Water)", "Plastic bottle (Tainted)", and just
  "Plastic bottle" when empty. The fill level is not shown.
- **Weight:** `itemUnitWeight()` adds `holdsWater.kg × fill` when `water` is set.
  It stays the only place weight is computed.
- **Merging:** `sameStackState` adds water kind and fill.
- **Every placement and pool entry of `bottled_water`** becomes `plastic_bottle`
  with `state:{ water:{ kind:"clean", fill:1 } }` (pools) or the same
  `overrides` (hand-placed), same quantities and chances.
- **Drinking** uses Phase 6's buttons, with `fill` in the role of `portion`:
  - thirst restored: `holdsWater.restores × amount`;
  - tainted water: `rollFoodPoisoning(TAINTED_WATER_POISONING_CHANCE × amount)`;
  - the bottle stays: at 0 its `water` is removed and it reads
    "Plastic bottle". Drinking from a `qty > 1` row splits one bottle out.
- **The interim Drink rule** lasts until #47 replaces it. Vessels are never
  drunk from.

### Sinks
- ROOM SCHEMA gains optional **`sink: true`**. Set on `kitchen`,
  `twobee_kitchen`, `onea_kitchen`, `bathroom`, `twobee_bathroom`,
  `onea_bathroom`.
- **"Fill at the sink"** is offered in the pop-up of any water-holding item
  (plastic bottles here; vessels in Phase 9) when the room has a sink,
  `waterRunning()`, and the item is not already full of clean water.
  - Fills one unit to full. A row with `qty > 1` splits one out.
  - Kind: clean, **unless the unit already held tainted water: then the whole is
    tainted.** Any tainted water taints everything it mixes with, in either
    order.
  - Instant. Log: `You fill the <name> at the sink.` (retunable).
- **After day 21 the sink gives nothing**, and the action is not offered.
  Whatever water was left in the pipes is #47's.
- **No tainted source ships** in this release (#52). The tainted state and its
  rules ship ahead of it, like the freezer rule does.

### Checks — Phase 7
- Pantry bottles read "Plastic bottle (Water)". Drink 1/2 → +15 thirst, bottle
  kept. Drink the rest → "Plastic bottle", weight 0.05. Fill at the 2A sink →
  full again.
- Advance past day 21: no Fill action.
- A bottle hand-edited to tainted in a scratch copy: Drink → one roll at 0.35
  scaled by amount; filling it at a sink keeps it tainted.

---

## Phase 8 — Reachable crafting, preparation and the crafting panel (#119, #120, #162)

### Reach
- **Nearby** means: the player's inventory pools (`invPools()`), the current
  room's floor, its containers the Here panel lists (unlocked, and searched or
  `shownWithoutSearch()`: the same gate as `renderWorldItemsPanel()`), and its
  car containers when not `carLocked`. **Not** the contents of floor bags or of
  vessels. A container that has not rolled yet counts as empty. Crafting never
  triggers a roll.
- **Recipe inputs** may carry a state filter: `{ id, qty, cookState }`. A unit
  matches only in that state.
- `canCraft()` counts matching units across everything nearby. The `tool` gate
  stays **`hasTool()` (carried)**, as today.
- **Which units are used:**
  - non-perishables: **the player's inventory first** (in `invPools()` order),
    then the floor, then containers in authoring order, then car containers;
  - perishables: **the oldest units** across everything nearby, and on a tie,
    the inventory's.
- **The output lands on the room's floor**, always (`addToList(room.floor, …)`).
  Over `floorCap` it still lands there, with the existing "heap" warning line.
  This changes where a crafted bandage or campfire kit appears: on the floor,
  not in the open inventory tab. Say so in the changelog.

### Preparation (#120)
- `RECIPES` entries gain **`group`**: `"craft"` (bandage, campfire kit) or
  `"prep"`.
- New recipe: `{ id:"fillet_fish", label:"Fillet the fish", group:"prep",
  inputs:[{ id:"fish", qty:1, cookState:"raw" }], tool:"blade", minutes:10,
  output:{ id:"fish_fillets" } }`. This is `recipe.tool`'s and the `blade` tag's
  first consumer.
- New registry entry **`fish_fillets`**: `{ name:"Fish fillets", category:"Food",
  unitWeight:0.25, restores:{hunger:10}, verb:"Eat", foodPoisoningChance:0.35,
  cooks:{ minutes:10, restores:{hunger:35} }, spoils:{ staleAfter:8*60,
  rottenAfter:18*60 } }`.
- **A fillet inherits the consumed fish's age** (not age 0). It's the same
  flesh.
- Move `blade` from "declared, no consumer" to "read by a mechanic today" in the
  ITEM DATA SCHEMA comment, and add `"blade"` to `REPORTED_TOOL_TAGS`.

### The crafting panel (#162)
- **"(needs …)"** is rewritten for the new shapes: input names with their state
  when filtered ("Fish (Raw) ×1"), and a tool as "a blade" (the tag, in plain
  words). Exact wording is the session's (record it).
- A **search box** at the top of `#craftingPanel`: case-insensitive substring
  match against the recipe's label **and** its input names (and, from Phase 9,
  a dish template's label and roles).
- **Group filter** buttons: **All · Crafting · Preparation** (and **Dishes** from
  Phase 9). One is active at a time; All by default.
- A **"Can make now"** toggle, off by default.
- **The default view is the whole catalogue**, unavailable entries included
  (#162's constraint). Search and filters read `RECIPES` (and later
  `DISH_TEMPLATES`) directly, never a parallel list.
- Filter and search state is UI-only: not saved, and reset when the panel
  closes.

### Checks — Phase 8
- Cloth in a cabinet and duct tape in the backpack: "Craft a bandage" is
  enabled, uses both, and the bandage appears on the floor.
- Fillet with the fish in the fridge and a kitchen knife carried: fillets on the
  floor, with the fish's age. Without a blade: disabled, needs text names the
  blade.
- Two raw fish, one older, one carried and one in the fridge: filleting uses the
  older.
- Search "firewood" shows the campfire kit. Preparation shows only the fillet.
  "Can make now" hides what can't be made. Close and reopen: filters reset.

---

## Phase 9 — Vessels and dishes (#215)

### Vessels
Registry field **`vessel: { kind, capacityKg, waterKg }`** (`waterKg` 0 = can't
hold water):

| Id | Name | Category | Weight | kind | capacityKg | waterKg |
|---|---|---|---|---|---|---|
| `cooking_pot` **new** | "Cooking pot" | Tool | 1.2 | `pot` | 3 | 2.0 |
| `dented_saucepan` | (unchanged) | Tool | 0.7 | `saucepan` | 1.5 | 1.0 |
| `burnt_saucepan` | (unchanged) | **Tool** (was Misc) | 0.6 | `saucepan` | 1.5 | 1.0 |
| `frying_pan` | (unchanged, keeps `blunt`) | Tool | 0.9 | `frying_pan` | 1 | 0 |
| `roasting_pan` **new** | "Roasting pan" | Tool | 1.5 | `roasting_pan` | 3 | 0 |

- `kitchen_tools` gains `cooking_pot` (0.15, 1) and `roasting_pan` (0.10, 1):
  chosen chances, noted as such.
- A vessel instance holds **`contents`** (ingredients, or exactly one dish) and
  **`water: { kind }`** (full, or absent; vessels have no fill level). Reusing
  `contents` means weight (`itemUnitWeight()`, which also adds `waterKg` when
  `water` is set), saving and `forEachItemList()` already reach them.
- A vessel's contents are **not** item rows. The vessel's row and pop-up show
  them.
- **Row label:**
  - "Saucepan (Water)" or "Saucepan (Tainted)" with water;
  - once a dish exists, `Saucepan: <Dish name> (<Cook state>) (<Freshness>)`,
    for example "Saucepan: Fish stew (Cooked) (Fresh)";
  - otherwise the plain name.
- **Pop-up** lists the contents ("Holds: Fish ×1, Vegetables ×1") and its water.

### Ingredients
Registry field **`ingredient: { role, label, restores?, addPortion? }`**:

| Id | role | label | notes |
|---|---|---|---|
| `fish`, `fish_fillets` | `meat` | "Fish" | |
| `meat` | `meat` | "Meat" | |
| `canned_tuna` | `meat` | "Tuna" | opened only |
| `vegetables` | `vegetable` | "Vegetable" | |
| `canned_beans` | `vegetable` | "Bean" | opened only |
| `canned_corn` | `vegetable` | "Corn" | opened only |
| `pasta` | `grain` | "Pasta" | `restores:{hunger:120}`, `addPortion:0.25`; **no longer edible**: remove its `restores` and `verb` |
| `rice_bag` | `grain` | "Rice" | `restores:{hunger:120}`, `addPortion:0.25`; not edible (has no `restores` today) |

- **An ingredient unit's contribution** (restores) =
  - `ingredient.restores` when set, else its cooked restores for a cookable item,
    else its `restores`;
  - × `ROTTEN_RESTORES_FACTOR` if Rotten;
  - × its portion.
- **"Add to the <vessel name>"** is offered in the pop-up of any unsealed item
  with `ingredient`, once per vessel nearby (Phase 8's reach, plus vessels
  inside the room's heat container) that holds no dish yet and has room
  (`contents` weight + the added weight ≤ `capacityKg`).
  - It moves **one unit**, the oldest, into the vessel's `contents`.
  - For `addPortion` items it moves **a quarter**: the source unit's portion
    drops by 0.25, and the added unit has `portion:0.25`.
  - Log: `You add the <name> to the <vessel>.` (retunable).
- **"Take out the <name>"** per content row, while no dish has formed: returns
  it through `giveItem()`.
- Contents keep ageing (their container's rate) until a dish forms.

### Water in vessels
- **"Fill at the sink"** (Phase 7) works on vessels with `waterKg > 0` and no
  dish. It sets `water` to clean, or tainted if it was tainted.
- **"Pour into the <vessel name>"** in a water bottle's pop-up, once per nearby
  vessel with `waterKg > 0` and no dish. It empties the bottle, **whatever its
  fill**, and the vessel then holds water. The taint rule applies. Volumes are
  #47's. Log: `You pour the water into the <vessel>.` (retunable).
- **"Pour out the water"** on a vessel with water and no dish.
- **Boiling:** a vessel with **tainted** water in a lit heat container counts
  `boilMinutes`. At `BOIL_MINUTES` the water becomes clean and `boilMinutes` is
  deleted. It holds when the heat stops. No log line.

### Dish templates
**`DISH_TEMPLATES`** (CONFIG), checked **in this order**. The first match wins:

| id | Vessel kinds | Water | Contents rule | Name | Minutes |
|---|---|---|---|---|---|
| `boiled_pasta` | pot, saucepan | yes | only `pasta` | "Boiled pasta" | 10 |
| `boiled_rice` | pot, saucepan | yes | only `rice_bag` | "Boiled rice" | 20 |
| `soup` | pot, saucepan | yes | exactly 1 unit, role `vegetable` | "<A> soup" | 20 |
| `stew` | pot, saucepan | yes | ≥ 2 units of roles `meat`/`vegetable`; `grain` also allowed | "<A> stew" / "<A> and <b> stew" | 30 |
| `roast` | roasting pan | no | ≥ 1 unit, roles `meat`/`vegetable` only | "<A> roast" … | 45 |
| `stir_fry` | frying pan, saucepan | no | ≥ 1 unit, any role | "<A> stir fry" … | 10 |

- **A unit** is one add: a quarter of rice is one unit.
- **"Water: yes"** means the vessel holds **clean** water. Tainted water must
  boil first, and no dish forms until it has.
- **"no"** means the vessel holds no water.
- **Anything else** (for example water + one fish) matches no template: the
  contents cook one by one by their own `cooks` and the water boils.
- **Naming:** group the contents by `ingredient.label`, summing each label's
  contribution. The top one or two labels by contribution make the name: first
  capitalised, second lowercase, joined with " and ", then the dish word
  lowercase. For example "Fish stew", "Fish and vegetable stew", "Meat roast".
  A label that repeats counts once. Templates with a fixed name ignore this.
- **One registry entry per template** (`dish_boiled_pasta`, `dish_boiled_rice`,
  `dish_soup`, `dish_stew`, `dish_roast`, `dish_stir_fry`):
  - `name` is the dish word ("Stew", …), category Food, verb "Eat";
  - `cooks:{ minutes }` holds the template's minutes;
  - `spoils:{ staleAfter:1d, rottenAfter:3d }`;
  - `vessel` and `ingredient` are absent.

  The instance carries what the ingredients decided (below). This is genuine
  per-instance state, allowed by the ITEM DATA SCHEMA's `overrides` rule, and
  the schema comment must say so.

### Formation and cooking
- On the first tick a vessel is in a lit heat container and its contents match
  a template (with clean water where required), **the contents and the water
  become one dish item**, the vessel's only content:
  - `itemId` = the template's entry; `name` = the computed dish name;
    `qty:1`, `portion:1`, `ages:[0]`, `cookState:"raw"`, `cookMinutes:0`;
  - **`restores`** = sum of contributions × (1 + `DISH_RESTORES_BONUS`),
    per vital;
  - **`foodPoisoning: { raw, cooked }`**:
    - for each ingredient unit, its raw-state chance
      (`combinePoisoning(own raw, rotten term)`) and cooked-state chance
      (`combinePoisoning(own cooked, rotten term)`), where the rotten term is
      `ROTTEN_POISONING_CHANCE × POISONING_TRAIT_MULTIPLIER` if Rotten, else 0;
    - for each state, take the unit with the highest chance: the dish's chance
      = that chance × (that unit's contribution ÷ the dish's `restoresValue`
      total, after the bonus);
  - **`unitWeight`** = the contents' weight + the water's `waterKg` if water
    was used;
  - the vessel's `water` is removed.
- **From then on nothing can be taken out** of the vessel.
- The dish cooks like any cookable (Phase 3) with its entry's `cooks.minutes`.
  At completion it is Cooked with age 0, **always Fresh**. It spoils by its
  entry's `spoils` from there.
- `foodEffects()` returns the instance's `restores` and the `foodPoisoning`
  value for its cook state.
- **Eating:** the vessel's pop-up offers Phase 6's Eat buttons for its dish. The
  dish's own portion, restores and poisoning × amount, and the rotten rules,
  apply. When the dish is gone, the vessel is empty. **A dish never leaves its
  vessel:** carrying it is carrying the pot. Bowls are for later.
- **"Pour it out"** on a vessel holding a dish discards the dish, leaving the
  vessel empty. Log: `You pour out the <dish>.` (retunable).
- **"Wait until …"** (Phase 3) covers forming and raw dishes and boiling water.

### Create dish
- **"Create dish"** in the pop-up of any vessel holding no dish. It opens the
  crafting panel with the group filter on **Dishes** and **this vessel as
  context**:
  - only templates whose vessel kinds include this vessel's are listed;
  - each row shows what the vessel already holds towards it, what's missing,
    and whether it's ready to cook;
  - an **"Add ingredients"** button pulls the missing units from nearby (oldest
    perishables first, Phase 8's order otherwise), as "Add to" would. Water is
    never pulled: a missing water requirement says so.
  - **The panel never chooses the dish.** The contents do, when heated.
- **From the drawer**, the Dishes group lists every template as a catalogue row,
  with its needs in words ("A pot or saucepan with water, and two or more meat
  or vegetables"). Wording is the session's; record it.

### The spawned stew
- **`pot_of_spoiled_stew` is retired.**
  - The 2A stove's hand-placed one becomes a `cooking_pot` holding a Cooked stew
    dish made from one `meat` and one `vegetables`: "Meat and vegetable stew",
    restores hunger (40 + 10) × 1.25 = 62.5, thirst 2 × 1.25 = 2.5.
  - Its `kitchen_perishable` entry becomes
    `{ itemId:"cooking_pot", key:"stew_pot", state:{ dish: … } }` with the same
    chance.
  - Build both through one helper that makes a dish from ingredient ids and a
    cook state, the same code formation uses. The dish gets its age from
    `stampMissingAges()` like any world item. At the start the stove's one is 2
    days old (Stale); one rolled later is older.
- The stove's capacity (8 kg) holds it.

### Checks — Phase 9
- Fill a saucepan at the sink, add one fish and one vegetables, put it in the
  stove, light it: it becomes "Saucepan: Fish and vegetable stew (Raw) (Fresh)",
  nothing can be taken out, and after 30 minutes "(Cooked) (Fresh)". Restores =
  (35 + 10) × 1.25 hunger, 2 × 1.25 thirst.
- Water + pasta ×1 add: "Boiled pasta", 10 minutes, hunger 30 × 1.25.
- Frying pan + one raw fish: stir fry. Roasting pan + fish + vegetables: roast.
  Pot with water + one fish: no dish. The fish cooks alone in 15 minutes.
- A rotten raw fish (0.58 raw) in a stew with two vegetables: dish raw chance =
  0.58 × its share of the total. Check the arithmetic in a scratch copy.
- Tainted water + vegetables: no dish until the water has boiled 5 minutes,
  then soup forms.
- Create dish on an empty saucepan: Dishes filter, only saucepan templates;
  "Add ingredients" fills from the fridge oldest-first.
- Eat 1/4 of a stew from its pot. Pour out the rest: an empty pot.
- New game: the 2A stove holds "Cooking pot: Meat and vegetable stew (Cooked)
  (Stale)".

---

## Phase 10 — Save migration, dev helpers, comments, wrap

### Loading older saves
The release rotates `SAVE_KEY` (a browser save from 0.7 does not auto-load). An
imported 0.7 file must still load without throwing. Add
**`migrateCookingRelease()`**, run in `applyLoadedData()` after the existing
backfills. It is **idempotent**:
- **Items, by `itemId`, rebuilt from the registry**, keeping `qty` and `_uid`:
  - `raw_fish` → `fish` raw; `cooked_fish` → `fish` cooked;
  - `spoiled_milk` → `milk`, `moldy_bread` → `bread`, `rotten_produce` →
    `vegetables`, `rotten_leftovers` → `leftovers`, each with ages set to
    `rottenAfter` (Rotten);
  - `pot_of_spoiled_stew` → a cooking pot holding the stew dish, Rotten;
  - `bottled_water` → `plastic_bottle` full of clean water.
- **Instance `illnessChance`** is deleted (after `backfillIllnessScale()`).
  Poisoning is read from the registry now.
- **`state.illnessMinutesLeft` > 0** becomes `state.illnesses.food_poisoning`,
  and the old field is deleted. A missing `state.illnesses` becomes `{}`.
- **Authored containers:**
  - any container in the default world missing from a loaded room (by id) is
    added: the freezers;
  - a loaded container whose default carries `tags` takes a fresh copy of them:
    the fridges.
- **Rooms:** `sink` copied from the defaults.
- **`stampMissingAges()`** runs last.

### Dev helpers
- `validateItemRegistry()`:
  - checks `foodPoisoningChance` and `cooks.foodPoisoningChance` ∈ [0, 1];
  - `cooks.minutes > 0`;
  - `spoils.staleAfter < spoils.rottenAfter`;
  - `ingredient.role` ∈ {meat, vegetable, grain};
  - every `DISH_TEMPLATES` entry has its registry entry;
  - every recipe input and output resolves.
- `validateReachability()`:
  - counts pool entries by `key`;
  - adds dish entries and recipe outputs to the reachable set;
  - `ACTION_GRANTED_ITEM_IDS` = `fish` (doFish), `firewood`, `spare_batteries`,
    with the reworded Disassemble comment;
  - `REPORTED_TOOL_TAGS` gains `blade`, and its `heat` note stays accurate:
    `roomHasHeat()`'s only caller is still the unused `needsHeat` gate.
- `simulateSeed()` / `sampleSeeds()` keep working with `key`ed entries.

### Comments
Keep the schema blocks whole and current:
- **ITEM DATA SCHEMA:** `cooks`, `cookState`, `cookMinutes`, `spoils`, `ages`,
  `portion`, `water`, `holdsWater`, `vessel`, `contents` (now also a vessel's),
  `ingredient`, `foodPoisoningChance` (renamed, registry-read), `disassembleLog`,
  and the dish instance fields (`restores`, `foodPoisoning`, `unitWeight`, name).
- **CONTAINER SCHEMA:** `fridge`, `freezer` tags, `timerMinutes`, the
  respawn-skips-perishables note.
- **ROOM SCHEMA:** `sink`.
- **SPAWN_POOLS:** `key`, `state`, the chosen chances.
- **ARCHITECTURE:** FIRE/COOKING no longer has a Cook action. Adjust the word
  list only if it names one.

### Wrap (per `CLAUDE.md`)
1. `GAME_CONFIG.VERSION` bumped as **MINOR**. With nothing else shipped in
   between, that is `0.8.0`, and `SAVE_KEY` becomes `ashfall_save_v0.8`.
2. **One** `CHANGELOG.md` entry, per `docs/CHANGELOG_GUIDE.md`, with
   `Implements: handoffs/cooking-release.md`, New / New content / Changed /
   Removed kept separate, and every design decision the session resolved.
3. `git mv handoffs/cooking-release.md handoffs/archive/cooking-release.md`.
4. PR description: `Closes #206, #167, #210, #218, #178, #213, #48, #121, #119,
   #120, #162, #215` (one `Closes` per issue).
5. New issues for anything cut or surfaced.
6. The tag commands in the final message.

### Checks — Phase 10
- Import a v0.7.5 export that holds raw and cooked fish, spoiled milk, bottled
  water, a running illness: it loads, the items read "Fish (Raw) (…)", "Milk
  (Rotten)", "Plastic bottle (Water)", the illness keeps counting, the 2A
  kitchen has a freezer.
- Load it twice (export after the first load, import again): nothing changes the
  second time.
- All four validators and both seed reports run without errors.
- Full play-through smoke test of every phase's checks on the final build.

---

## Design decisions to make during implementation

Record each in the changelog's Notes / assumptions:
- How `rebuildKeepingFocus()` is made usable for the tab strips (flag vs.
  sibling helper).
- Helper names and exact signatures (`sameStackState`, `takeUnits`,
  `itemStateLabels`, `foodEffects`, `effectiveAge`, …). The shapes above are
  binding. The names are not.
- How `forEachItemList()` reports the owning container (third argument, or a
  second walker).
- The crafting panel's markup and styling for search, group buttons and the
  toggle. The panel must stay usable at phone width.
- Exact wording of the "(needs …)" text and of the Dishes catalogue's needs
  sentences.
- Where the Here panel header's `On · Timer: N` sits relative to the weight and
  the Device Options button.

## Data / schema changes

**PLAYER STATE:**
- `illnessMinutesLeft` removed, `illnesses: {}` added.
- **No other new state field.** The collapse clock is derived from
  `totalMinutes`.

**Item instances:**
- new: `cookState`, `cookMinutes`, `ages`, `portion`, `water`, `boilMinutes`,
  dish fields (`name`, `restores`, `foodPoisoning`, `unitWeight`);
- vessels' `contents`;
- `illnessChance` removed.

**ITEM_REGISTRY:**
- New fields: `cooks`, `spoils`, `holdsWater`, `vessel`, `ingredient`,
  `disassembleLog`.
- `illnessChance` → `foodPoisoningChance`.
- New ids: `fish`, `fish_fillets`, `meat`, `vegetables`, `milk`, `bread`,
  `leftovers`, `ice_cream`, `plastic_bottle`, `cooking_pot`, `roasting_pan`, and
  the six `dish_*`.
- Retired ids: `raw_fish`, `cooked_fish`, `spoiled_milk`, `moldy_bread`,
  `rotten_produce`, `rotten_leftovers`, `pot_of_spoiled_stew`, `bottled_water`.
- Changed: `pasta` (not edible, ingredient), `rice_bag` (ingredient),
  `burnt_saucepan` (Tool, vessel), `dented_saucepan` / `frying_pan` (vessel),
  cans (`spoils`, `ingredient`), `campfire_kit` (tag, `disassembleLog`).

**Containers:**
- `timerMinutes` (stoves);
- `fridge` / `freezer` tags;
- three new freezer containers.

**Rooms:** `sink`.

**Spawn pools:**
- entries gain `key`, `state`;
- new `kitchen_frozen`;
- `kitchen_perishable`, `kitchen_nonperishable`, `retail_stock_food` and
  `kitchen_tools` changed as above.

**New tables:** `ILLNESSES`, `DISH_TEMPLATES`.

**Removed:** `HEAT_RECIPES`.

**`SAVE_KEY` rotates** (MINOR).

## In scope

Everything in Phases 1–10.

## Explicitly out of scope

- **#179** burning and unattended fires. Cooked food never overcooks here.
- **#214** carried and digital timers.
- **#216** Stale food's effects (traits, morale).
- **#217** freezing and thawing times, and temperature.
- **#219** Food subcategories.
- **#220** power for other appliances, generators, and any sign that the power
  has failed.
- **#47** fluid volumes, partial pours, drinking from vessels or taps, sinks'
  leftover water.
- **#52** tainted water sources and purification tablets.
- **#211** disassembly yields by category.
- **#96** the propane torch (not for cooking).
- **#149** world-generation options (start day, power/water days).
- **#137** the hospital opening.
- **#15** respawn (only the comment).
- **#134 / #116** per-unit durability and tool wear.
- **#89** building ids. The timer compares building names.
- **#212** the sidebar Wait.
- **Bowls, and serving dishes out of vessels.**
- **#119's rule that a used tool moves to the inventory.** Tools stay
  carried-only (`hasTool()`).
- The `needsHeat` gate and `roomHasHeat()` stay untouched.
- The `Day N` clock.

## Sections touched

- CONFIG / CONSTANTS: constants, `RECIPES`, `DISH_TEMPLATES`, `HEAT_RECIPES`
  removed.
- WORLD DATA: registry, pools, kitchen and bathroom rooms, six room texts.
- PLAYER STATE: `illnesses`.
- CORE UTILITIES.
- INVENTORY / ITEM SYSTEM: merge, units, eat, open, actions.
- WORLD INTERACTION: `doOpenContainer`.
- SURVIVAL / TIME SIMULATION: illness, world ticking.
- CRAFTING.
- FIRE / COOKING: cooking tick, timer, dismantle, dish formation.
- PERSISTENCE: migration, new game stamping, dev helpers.
- RENDERING: labels, pop-up, Here actions, Here header, Device Options, crafting
  panel, tab-strip focus.

This is both a mechanics pass and a content pass. The changelog keeps **New**
and **New content** apart.

## UI changes (summary)

- **Item names** carry state labels: (Open), (Raw)/(Cooked),
  (Fresh)/(Stale)/(Rotten)/(Frozen), (Water)/(Tainted), and vessels'
  `: <dish>` form.
- **Eat / Drink** gain 1/2 and 1/4.
- **New pop-up actions:** Fill at the sink, Pour into …, Pour out the water, Add
  to …, Take out …, Create dish, Pour it out.
- **Here:** "Cook the …" is gone; "Wait until the … is cooked" / "…water boils"
  is new; the Here header shows the stove's On/Off and Timer.
- **Device Options (stove):** Timer line and +5 / +10 / +30.
- **Crafting panel:** search, All / Crafting / Preparation / Dishes, Can make
  now; "Fillet the fish"; the Dishes catalogue; vessel context from Create dish.
- **Crafted items** land on the floor.
- **New containers** (Freezer), sinks (as actions), new items, six room texts.

## Dependencies / issue linkage

Closes #206, #167, #210, #218, #178, #213, #48, #121, #119, #120, #162, #215.
Advances without closing: #52 (clean/tainted water, boiling), #23 (illness
reshaped for more illnesses), #47 (the interim Drink rule it will replace),
#179 (cook-state counter it will extend), #15 (the respawn note). Anything this
pass cuts or surfaces becomes a new issue at the wrap.

## Open questions for Tom

None. Every design question was settled in the planning session at v0.7.5 and
recorded on the issues above.

## After implementation

Open one pull request from the release branch carrying the version bump, the
single changelog entry (naming this handoff by path and recording every
"Design decisions" resolution), the `git mv` of this file into
`handoffs/archive/`, and one `Closes #NN` line per issue listed at the top.
End the session's final message with `CLAUDE.md`'s tag commands.
