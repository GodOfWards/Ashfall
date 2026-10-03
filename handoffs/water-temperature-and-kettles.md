# Ashfall Handoff — Water temperature, kettles, appliances that switch themselves off, timed transfers, and the canteen

Current shipped version: v0.12.3
Implied version-change type: MINOR
Issue: #431 — Water temperature; #334 — Appliances switch themselves off;
#385 — Kettles; #411 — Filling and pouring take time by volume; #415 — The
canteen can't be found

## What this is

One bundle, five issues, one save-key rotation. Water gets a temperature
(#431): it heats on a source, cools off it, is at the boil at 100 °C, and
tainted water is clean after 3 minutes at the boil. Small appliances switch
themselves off (#334). The electric kettle becomes an item that plugs itself
in where it's placed and cuts out at the boil, and a stovetop kettle joins it
(#385). Fills and pours over a litre take time (#411). The canteen gets a
placement (#415).

They're bundled because they share code: #431 and #411 both rewrite the fill
and the pour; #334's kettle rule lands on #385's kettle item, not on the
fixture #385 removes; and #385 can't work without #431. Each issue body is
the full design; this handoff is the spec, and quotes what the coding session
needs from the reference folder.

## Relevant existing state

Verified against `main` at v0.12.3 (`GAME_CONFIG.VERSION = "0.12.3"`). Line
numbers are approximate; find code by identifier.

**Fluids** (`docs/systems/fluids.md`; INVENTORY / ITEM SYSTEM, ~6170–6510)

- A holder is a registry entry with `holdsFluid:{ capacityMl }`. Its
  instance's `fluid:{ kind, ml }` is absent when empty. Every writer goes
  through `addFluid()` (which also deletes `boilMinutes`: "new water in a
  vessel starts its boil over") and `takeFluid()`.
- `sameStackState()` (~5602) merges holder rows only at the same kind and
  millilitre. `groupKeyOf()` (~5722) groups rows that differ by level.
  `STACKABLE` (~501) is Food, Medical and Materials, so only the bottle, water
  jug and dispenser jug (Food) stack; Misc and Tool holders never do.
- `doFillAtSink()` (~6265) fills one unit to full (or what the tank has
  left), instantly; `drawFromTank()` draws it and returns a building to
  resolve when a pumped tank's float moved. `waterRunningIn()` (~6996): a
  building's tank while it holds water, else `mainsWaterUp()`. **Every sink
  today is in a building with a tank** (row house, casa, shop_home), so the
  mains branch of a fill is never reached in play.
- `doPour()` (~6475) moves `ml` (null: as much as fits; Pour by the measure
  passes `MEASURE_ML`) through `pourFluid()`, instantly. `doPourOut()` empties
  one unit, instantly and silently. `pourTargets()` reaches everything
  `nearbyPlaces()` gives, **the room's heat container included**.
- Registry holders (~1083–1191): `plastic_bottle` 500 mL (Food),
  `burnt_saucepan` and `dented_saucepan` 1,000 mL (Tool, `vessel` kind
  saucepan), `cooking_pot` 2,000 mL (Tool, vessel kind pot), `thermos`
  1,000 mL (Misc; its comment says "keeping it hot is not modelled"),
  `bucket` 10,000 mL, `canteen` 1,000 mL (Misc), `water_jug` 6,250 mL and
  `dispenser_jug` 20,000 mL (Food). `frying_pan` and `roasting_pan` are
  vessels with no `holdsFluid`.

**Cooking** (FIRE / COOKING, ~9180–9470)

- `BOIL_MINUTES = 5` (~659): "Minutes tainted water must sit in a heated
  vessel to come out clean, whatever its volume."
- A lit room (`heatActive`) is in the runtime set `heatRooms`
  (`scheduleHeat()`). `settleHeat()` → `cookInHeat()` runs every item in
  every heat container (`heatContainersOf()`, tag `heat`: the stove's and the
  campfire's) for the span: a vessel through `settleVessel()`, anything else
  through `cookItem()`. **Every vessel in a heat container cooks at once.**
- `settleVessel()` (~9416): (1) forms a dish if `matchingTemplate()` is ready;
  (2) else tainted water adds the span to `boilMinutes` and turns clean at
  `BOIL_MINUTES`, forming the dish it now makes and ending the span there;
  (3) cooks the contents by the span (a dish's `cookMinutes` toward its
  `cooks.minutes`).
- `soonestIn()` (~9440) gives the soonest completion among a room's heat
  containers (a raw row, a dish, a dish that will form, tainted water
  boiling); `heatRoomDue()` feeds it to `planNextDue()`; the Wait button
  (`waitForCookingTarget()`) waits for it.
- `formDish()` builds the dish from the contents and **all the water**
  (`fluidWeightOf()` into `unitWeight`), then deletes the vessel's `fluid`
  and `boilMinutes`. `templateStatus()` needs at least `dishWaterMinMl()` of
  clean water for a `water:true` template. `DISH_TEMPLATES` (~741): pasta,
  rice, soup and stew are `water:true`; roast and stir-fry are not.
- `doLightStove()`, `doBuildFire()`, `doExtinguish()` and the fire's
  burn-down in `settleHeat()` are the writers of `heatActive`, each calling
  `scheduleHeat()`.

**The scheduler** (`docs/systems/time.md`; SURVIVAL / TIME SIMULATION,
~7950–8090)

- `settleWorld(m)` order: tanks (`settleTanks()`), grid changes
  (`resolveGrid()`), tanks come full resolve their buildings, battery deaths,
  stove timers, lit rooms' cooking and fires. `planNextDue()` takes the least
  of every system's next event. `rebuildSchedule()` rebuilds the runtime
  lists from one walk of the world on new game, restart and load. Between two
  advances `settledAt` is now.
- A device on batteries is the model for a switched item: `on` on the
  instance, `switchDevice()` the one writer, a runtime list of due minutes
  (`batteryDeaths`) rebuilt by `rebuildSchedule()`'s `forEachItemList()`
  walk. `itemStateLabels()` labels any item with `on` truthy "(On)", and a
  group header never shows it.
- `replayProblems()` (~10930) checks the runtime lists against a full scan
  after every replay step.

**Power** (`docs/systems/power.md`; POWER, ~8090–8800; POWER SCHEMA,
~4670–4840; WIRING_TEMPLATES, ~4955–5032)

- `expandWiring()` expands the wiring once, at startup, into `POWER_NET`
  (boards, panels, breakers, loads). A circuit breaker carries its template
  `roles`; a panel maps `roles:{ role: roomId }`. A load is
  `{ id, appliance, panel, circuit, room, containers }`, and each breaker's
  `loads` lists every load it feeds, upstream breakers included.
  `POWER_INDEX` (`powerIndex()`) splits it per building and indexes
  `roomLoads`.
- `powerSnapshot()` and `resolvePower()` are pure functions of the net, the
  appliances, a power state, the rules, the grid, the previous drawing, the
  seed and `floats` (each pump's tank float, `tankFloatsNow()`). A pump is
  the precedent for a load whose drawing depends on an input other than its
  switch.
- `state.power` is `{ switches, breakers }`, only what differs from default.
  `copyPower()` and `resolvePower()`'s own copy carry exactly those two keys;
  `busyBuildings()` makes busy any building with an entry in either, a float
  not full, or an untouched tripper; every other building is still
  (`stillLook()`). Load (~9845) rebuilds `state.power` as exactly
  `{ switches, breakers }`.
- Every resolve goes through `changePower()` (an action, a float, a tank come
  full) or `resolveGrid()` (a grid change, at every bound of `GRID_UP_SPANS`)
  or `refreshPower()` (boot, restart, load). `doSwitchLoad()` (~7421) is the
  one writer of a fixture's switch in play; it logs "You switch the <name>
  on/off." `logTrips()` and `logGridChange()` read `POWER_NET.loads[id].room`
  and `POWER_INDEX.roomLoads`.
- `APPLIANCES.kettle` 2,200 W, `toaster` 700 W, `microwave` 1,150 W, all
  `leftOnChance:0`, readout "Running"/"Stopped". Its figures comment calls
  the kettle "a 1.7 L kettle's most common figure", and a later comment says
  switching themselves off and being used "are #334's".
- Fixtures: `row_house` and `casa` (and so `casa_fuses`, built from the
  casa's) each have `kettle`, `toaster` and `microwave` on `sockets`, role
  kitchen. SOCKETS serves `roles:["kitchen", "living", "laundry"]` in the row
  house, `["kitchen", "living"]` in the casa, `["kitchen"]` in the
  `apartment` template; `casa_fuses`' single `fuses` circuit serves every
  casa room. The toaster and microwave have no container, so they are
  switched only from the Electrical view's load list (~13580).
- `containerPowered()`, `stoveLighting()`: a stove with power lights itself;
  a lit burner holds its flame without power.

**Placement and pools** (WORLD DATA)

- `KITCHEN_CONTAINERS` (~4008): `stove` (tags device, heat; pools
  kitchen_perishable, kitchen_tools), cupboards, drawers, fridge, freezer.
  **There is no counter.** Home kitchens are the `row_house`'s and the
  `casa`'s; `shop_home` has back rooms, no kitchen.
- `buildBuilding()` (~4410): **a container with any hand-placed items starts
  `spawnRolled:true` unless its spec says otherwise**, and so never rolls its
  pools. A room's `items:{ containerId:[refs] }` falls under the same rule.
- The player's home (`landmarkInstances()`, id `home`, ~4209) places a
  dispenser jug on the kitchen `floor` and a stew pot on the `stove`. The
  neighbours' row house (`row_neighbour`) has pools only.
- `generatedHomes()` (~4373): a casa per mid stop, `id = "h_" + stop id`.
  Independent rolls keyed `stableHash(id)` (door), `id + KEY_SEP + "board"`
  (old board: `oldBoardOverrides()` sets `rooms.kitchen.containers`, adding
  `old_board_spares` to the drawers) and `id + KEY_SEP + "jug"` (the
  dispenser jug on the kitchen `floor`, laid beside an old board's
  containers, never over them).
- `SPAWN_POOLS` (~1460): `office_supplies` is drawn by the police station's
  front desk and the offices' desks and filing cabinets. `hardware_store` is
  drawn only by the building-materials yard's three containers, all with
  hand-placed items, so it **never rolls** (#133). `electronics` is drawn by
  every bedside table and the office desks: not a shop. The comment above the
  table lists every chosen (not derived) chance as a retunable exception.
- The goods shed (`goods_shed`, ~4326): `unit1` "Padlocked crate 1"
  (`locked`, `breakTag:"cutting"`, pool `outdoor_camping`) holds a camping
  tent and a sleeping bag. `outdoor_camping`'s only canteen entry never rolls.

**Saving**: `serializeGame()` writes `state` whole and, per room, the
`ROOM_STATE_FIELDS` and `CONTAINER_STATE_FIELDS` that differ from a fresh
build. `SAVE_KEY` derives from MAJOR.MINOR. Items carry `_uid` in the save;
`addToList()` and `unitsOf()` strip it on a move.

### Figures (quoted; the coding session reads no reference file)

- **Boiling** (`Boiling_Water.md`): ANMAT: "Si no se dispone de agua potable:
  Hervila durante 3 minutos." Confirmed. Ministerio de Salud: 2–3 minutes,
  Confirmed. A kettle's cut-out trips "a few seconds" after the boil
  (Secondary).
- **The stove** (`Water_Temperature.md`, `Fuel_AR.md`): ENARGAS's medium
  burner, 1,400 kcal/h = 1.63 kW, Confirmed; a gas hob 49 % efficient with a
  lidded pot, Confirmed; "a lid saves about 30 %", so uncovered takes about
  1.4 × the energy, and 1.63 × 0.49 / 1.4 ≈ 0.57 kW reaches the water
  (derived).
- **The campfire**: 1 L from 20 °C to the boil on a going fire takes about
  6–19 min (derived); 0.45 kW is the middle, about 11 min. Unconfirmed.
- **The electric kettle** (`Electrical_AR.md`, `Water_Holders.md`): 1–1.2 L
  kettles draw 1,800–2,400 W, most commonly 2,200–2,400 W (Secondary);
  kettles are typically 80–90 % efficient, 88 % used (Secondary); empty with
  its base 0.8–1.0 kg (Secondary). 1.2 L from 20 °C ≈ 3.5 min at 88 %.
- **The stovetop kettle** (`Water_Holders.md`): aluminium N° 14, 1.2 L,
  about 0.2 kg empty (0.21 kg, Secondary).
- **Temperatures** (`Climate.md`, `Water_Temperature.md`): San Fernando
  Aero's February mean 23.5 °C (Confirmed as the station's figure; as
  Lima's indoor temperature, unconfirmed). Mains water about 17–20 °C from
  wells (derived, unconfirmed); roof-tank water about 5 °C above the month's
  mean air, ≈ 28–29 °C in February (derived from the Resistencia
  measurement, unconfirmed).
- **Cooling** (`Water_Temperature.md`): 1 L in an uncovered saucepan falls
  100 → 70 °C in very roughly 10–15 min, a Newton constant of about
  0.03–0.04 per minute (a physics estimate, unconfirmed). A lid stops most
  of the evaporation and "should roughly halve the rate". EN 12546-1's floor
  for an 801–1,200 mL vacuum flask gives at most ≈ 0.043 per hour
  (Secondary).
- **Flow** (`Lima.md`, `Water_Holders.md`): a kitchen tap fed from the roof
  tank about 6 L/min (derived, unconfirmed); a careful pour between holders
  about 7 L/min first-hand, taken as 10 L/min (Tom, unconfirmed).

## Rules / mechanics

All new values are named constants beside the system that owns them, and
every one without a confirmed source is commented as retunable (and
unconfirmed where the figure is).

### A. The canteen (#415)

Add `{ id:"canteen", qty:1 }` (empty) to `goods_shed`'s `unit1` items,
beside the tent and the sleeping bag. `outdoor_camping` is unchanged.

### B. Timed fills and pours (#411)

- `FLUID_INSTANT_MAX_ML = 1000`: a transfer of **1,000 mL or less is
  instant**, judged by the millilitres actually moved, not the holder's size.
- `TAP_FLOW_L_PER_MIN = 6` (Fill at the sink) and `POUR_L_PER_MIN = 10` (Pour
  and Pour by the measure). Two constants, retunable separately.
- A transfer over the threshold takes `max(1, litres moved / rate)` minutes,
  exact above the floor (fractions included, as moves are charged). The
  water moves first (and a tank draw resolves its building first, as now);
  then `advanceTime()` runs the minutes; the log line comes with the action
  as today.
- The button's cost shows the time rounded up to whole minutes, in the dim
  style every timed action uses, and only when the transfer would be timed.
  The pour submenu's entries show it per entry.
- **Pour out stays instant** for every holder. **Drinking stays instant.**
- Nothing interrupts a long transfer.

### C. Water temperature (#431)

**State.** A holder's `fluid` gains its temperature, **true at a minute**:
`fluid.temp = { c, at }`, `c` in °C and `at` in minutes since the collapse.
**Absent means the room's temperature**, at any minute: everything the world
spawns, and every save written before this, needs nothing written. (The
shape and names are an implementation call, named.)

**Constants.**

- `ROOM_TEMP_C = 23.5`. Every room's temperature, indoors and out, until
  weather (#58).
- `TANK_WATER_C = 28.5` (February's mean plus the ≈ 5 °C an exposed tank runs
  above the air; derived, unconfirmed). `MAINS_WATER_C = 18` (derived,
  unconfirmed). The mains constant **ships unused in play**: it is what a
  fill off the mains gets, a branch no sink reaches today.
- `WATER_BOIL_C = 100`. `WATER_HEAT_KJ_PER_L_K = 4.186`.

**Reading it.** One reader, e.g. `waterTempAt(unit, m)`: absent → room;
otherwise Newton's law in closed form,
`T(m) = ROOM_TEMP_C + (c − ROOM_TEMP_C) · e^(−k · (m − at))`, `k` the holder's
cooling constant per minute. Never ticked, never scheduled. Everything that
needs a temperature reads it here (the tint, mixing, stacking, heating's
start).

**Cooling constants**, definition data on each holder's `holdsFluid` (e.g.
`coolPerMin`), all retunable, all unconfirmed but the thermos's. Write each
as its derivation from the named constants:

| Holder | Rule | k per minute |
|---|---|---|
| Saucepans (burnt, dented), 1 L, open | `OPEN_PAN_COOL_PER_MIN = 0.035` | 0.035 |
| Cooking pot, 2 L, open | the saucepan's × (2)^(−⅓) | ≈ 0.0278 |
| Thermos | 0.043 per hour | ≈ 0.000717 |
| Closed holders: bottle 0.5 L, canteen 1 L, electric and stovetop kettles 1.2 L, water jug 6.25 L, bucket 10 L, dispenser jug 20 L | `CLOSED_HOLDER_COOL_FACTOR = 0.5` × 0.035 × (capacity in L)^(−⅓) | ≈ 0.0220, 0.0175, 0.0165, 0.0095, 0.0081, 0.0064 |

**New water.** A fill at a sink sets the poured-in water's temperature to
`TANK_WATER_C` off a tank, `MAINS_WATER_C` off the mains. Poured water
carries its source's temperature read now.

**Mixing.** Any `addFluid()` into a holder that already holds water sets the
result to the **volume-weighted mean** of the two, each read now, stamped
now. (Pour into an empty holder: the source's temperature, stamped now.)

**Stacking.** Two holder rows stack only when their temperatures, read now,
differ by less than `TEMP_MERGE_TOLERANCE_C` (an implementation call;
0.5 °C recommended), and a merge takes the mean. A fluid read within that
tolerance of `ROOM_TEMP_C` may drop its `temp` (it is at the room's
temperature). Both named in the changelog. Only Food holders stack, so this
matters for bottles and jugs.

**Which holders heat.** Only cookware: the saucepans, the pot and the
stovetop kettle. Mark it on the definition (e.g. `holdsFluid.heats: true`),
never by name or id. Any other holder in a lit heat container (a bottle, the
thermos, the electric kettle) **does not heat**, and cools as anywhere else.

**Heating on a lit source.** Every heating holder in a lit room's heat
containers gets that source's **full power**, each as if on its own burner
(Tom):

- `STOVE_HEAT_KW = 0.57` (derived above), `CAMPFIRE_HEAT_KW = 0.45`
  (unconfirmed). Which applies is the container's: the stove's (tag `device`
  with `heat`) or the campfire's. How the container states its power is an
  implementation call (a definition field on the container spec is
  recommended over reading its id).
- The water rises linearly: `°C per minute = kW × 60 / (litres ×
  WATER_HEAT_KJ_PER_L_K)`. It stops at `WATER_BOIL_C`: water at 100 °C on
  the heat is **at the boil**. Evaporation and the vessel's own heat aren't
  modelled.
- A heating holder in a lit room is **stamped at `settledAt` by every
  settle** (its `at` is always the settle's minute). So `settleVessel()`
  starts each span by reading the temperature at the span's start: if the
  holder has heated continuously, that is its stamp; if it was off the heat
  in between (put on the stove since, the stove relit), it is the
  closed-form value. **This is how the boil count knows whether it was
  broken** (below). Recommended; the exact mechanism is the coding
  session's, named.

**The boil.** `BOIL_MINUTES = 3` (ANMAT, Confirmed). Tainted water's
`boilMinutes` counts **only time at the boil, without a break**:

- It counts the part of a span the water spends at 100 °C.
- It is lost (deleted) whenever the water is below 100 °C: taken off the
  heat, the heat going out or being put out, or cooler water poured in
  (mixing to below 100). Pouring water at 100 °C into water at the boil
  doesn't break it. A new boil starts from zero.
- At `BOIL_MINUTES` the water turns clean, as now, and forms the dish it now
  makes, ending the span there, as now.

**Dishes.** For `water:true` templates (pasta, rice, soup, stew):

- Formation is unchanged: the moment the contents and enough clean water
  match, the dish forms (`formDish()`), taking all the water.
- **The dish keeps its water's temperature and volume** on the dish instance
  (e.g. `dish.water = { ml, temp:{ c, at } }`; an implementation call,
  named), carried over from the fluid at formation. It heats, holds at the
  boil and cools by the same rules, at its **vessel's** cooling constant and
  heating rate, with the dish's water as the volume. Ingredients add nothing
  to the volume or the heat.
- **A water dish's `cookMinutes` count only while its water is at the
  boil.** Unlike tainted water's count, **a dish's count pauses** below the
  boil and resumes once back at it: nothing is lost.
- Dishes without water (roast, stir-fry), and raw items lying directly in a
  heat container or in a vessel no template matches, are unchanged.
- The world's spawned stew pots (`dishFrom()`) are already cooked: their
  water starts at the room's temperature (absent stamp).

**Scheduling.** `soonestIn()` and the Wait button learn the time to the
boil: tainted water's remaining time is `to the boil + (BOIL_MINUTES −
boilMinutes)`; a water dish's is `to the boil + its cook remaining`; a dish
that will form adds the time to the boil before its cook time. Reaching the
boil is an event of its own only where something happens at it: the
stovetop kettle's whistle (F) and the electric kettle's cut-out (F). Plain
water reaching the boil needs no event: the tint is read at render.

**Drinking hot water does nothing**, for now. **The thermos's comment**
loses "keeping it hot is not modelled".

### D. The row tint (#431)

- An item row whose unit holds water with a temperature, or a vessel whose
  dish has water, is **tinted in its own background**: blue below the
  room's temperature, orange-red above, untinted at it, a smooth gradient
  with no threshold, stronger the further from `ROOM_TEMP_C`. **Boiling
  (100 °C) is the strongest hot tint**; frozen (0 °C, for #217) the strongest
  cold one.
- The colours, the curve, and where each end saturates are an
  implementation call against the theme's tokens, light and dark, named.
- **Only the row**: not the pop-up. **A group header is untinted**; its rows
  carry the tint, as they carry the meter (#134's rule for headers). #134's
  meter is unchanged.
- Colour only: no text label is added. A reduced-motion or high-contrast
  path isn't needed (static colour).

### E. Appliances switch themselves off (#334)

**The rule, on `APPLIANCES`.** An entry may carry a stop rule (shape an
implementation call, e.g. `stops:{ after, onPowerLoss }`):

| Appliance | Stops | On a power cut | Its line, heard in its room |
|---|---|---|---|
| `toaster` | after `TOASTER_RUN_MIN = 3` (a judgment call, no sourced cycle) | switches off, and pops | "The toaster pops up." |
| `microwave` | after the minutes the player chose, up to `MICROWAVE_DIAL_MAX_MIN = 35` | **pauses**: its time left is kept, and it resumes when power returns | "The microwave pings." |
| `kettle` (the item's load, F) | at the boil; **at once when empty** | switches off: it is off when power returns | "The kettle clicks off." |

- **The microwave's minutes** are chosen when switching it on from a small
  set, `MICROWAVE_MINUTE_CHOICES = [1, 2, 5, 10, 20, 35]` (a UI judgment
  call). Its Electrical-view "Switch on" opens the choice; the layout is the
  coding session's.
- **Switching on records when it stops.** New saved state:
  `state.power.stops`, `{ loadId: { at } }` while running (`at` in minutes
  since the collapse) and `{ left }` while paused. A load with no stop rule
  never has an entry. `copyPower()`, `resolvePower()`'s copy, load's
  rebuild of `state.power` and `busyBuildings()` all carry the new key (a
  load with an entry is busy). The name and shape are an implementation
  call, named.
- **The stop is a scheduled event** (`docs/systems/time.md`): the least `at`
  joins `planNextDue()`; at it, the world is settled to that minute, the
  load's switch goes off (`setSwitchIn()`), its entry goes, its building
  resolves (`changePower()`), and its line is logged if the player is in the
  load's room. Nothing checks every minute.
- **A power cut** is already a resolve. After every resolve of a building
  (`changePower()`, `resolveGrid()`, `refreshPower()`), apply the rule to
  each of its loads with a stop entry: unpowered and "switches off" → switch
  off, entry gone (and the toaster's line, heard in its room); unpowered and
  "pauses" → `{ left: at − now }`; powered and paused → `{ at: now + left }`.
  Switching a load off that isn't drawing doesn't change the resolve's look.
- **Switching on without power** leaves an appliance whose rule is "switches
  off" switched off (the toaster can't be pushed down; the kettle won't
  latch), with its own line: the toaster "You push the lever down. It won't
  stay." and the kettle "You press the switch. It clicks straight back up."
  The microwave switched on without power is on and paused, its full chosen
  time kept.
- `leftOnChance` stays 0 for all three; `validateWiring()` should require it
  for any appliance with a stop rule (nothing found running needs a stop
  rolled).
- The washing machine and the TV get no stop rule (#424 is the wash cycle).
- The `APPLIANCES` comment's "switching themselves off … are #334's" is
  rewritten to say what is true.

### F. Kettles (#385)

**Items.**

- `electric_kettle`: "Electric kettle", `unitWeight:0.9`,
  `holdsFluid:{ capacityMl:1200 }` (closed; **no `heats`**), `on:false`, and
  a definition field naming its load (e.g. `appliance:"kettle"`). Category
  an implementation call; it must not be `STACKABLE` (Electronics
  recommended, as the flashlight).
- `stovetop_kettle`: "Stovetop kettle", `unitWeight:0.2`,
  `holdsFluid:{ capacityMl:1200, heats:true }` (closed), and a definition
  flag or tag that it whistles. No `vessel`: water only, never food.
  Category an implementation call, not `STACKABLE` (Misc recommended, as the
  thermos).
- Each with a one-line sourcing comment in the thermos's style.

**Plugging in.** The electric kettle is **plugged in while it lies on the
floor (the Floor tab's Place) of a room a socket circuit serves**. In a
container, carried, or in a room no socket circuit serves, it isn't.

- **A socket circuit** is marked on the template circuit (e.g.
  `sockets:true`), never found by its key or label: SOCKETS in `row_house`,
  `casa` and `apartment`, and `casa_fuses`' `fuses` (it serves every casa
  room). A room is served when a socket circuit of its panel lists its role.
- **How a running kettle enters the resolve** is the design decision below;
  whatever the choice, its 2,200 W is drawn on that circuit and every breaker
  upstream, it can trip them, a trip or the grid going down is heard and
  noticed in its room as any load's is, and the resolve stays pure.

**Running it.**

- **Switch on / Switch off** are actions in the electric kettle's item
  pop-up, offered while it is plugged in. Its row shows "(On)" while running
  (`itemStateLabels()` already does for `on`). The Electrical view no longer
  lists a kettle fixture.
- Switching it on: "You switch the kettle on." Then:
  - **empty** → it cuts out at once: "The kettle clicks off." (dry-boil
    protection);
  - **no power** at its socket → it doesn't latch (E): "You press the
    switch. It clicks straight back up.", in place of the switch-on line;
  - otherwise it runs: its building resolves with it drawing, and its water
    heats.
- **It heats** at `APPLIANCES.kettle.watts × KETTLE_EFFICIENCY` (0.88,
  Secondary) by C's linear rule, and **cuts out when its water reaches
  100 °C**: a scheduled event at that minute. At it: the kettle is off, its
  water is stamped at 100 °C, its building resolves, and "The kettle clicks
  off." is logged if the player is in its room. The cut-out does **not**
  clean tainted water (no boil count runs in the kettle).
- **Running means powered**: any resolve that leaves its socket unpowered (a
  trip, a blown fuse, the grid failing, the circuit switched off) switches it
  off at that minute, its water stamped; it is off when power returns.
- **Lifted while running, it switches off**, silently: any move that takes it
  off that floor (Take, a group's take, Store, Take all), switched off first,
  water stamped, building resolved.
- Pouring from or into it, filling it at the sink, or drinking from it while
  it runs moves its next cut-out (the next advance replans); poured empty
  while running, it cuts out at once with its line.
- **Saved:** `on` on the item, as a device's. The running kettles are a
  runtime list rebuilt by `rebuildSchedule()`'s walk; `replayProblems()`
  checks it.
- **Order at one minute:** a running kettle's heating over a span is the
  power it had at the span's start, since power only changes at settle
  points: settle running kettles' heating before the grid change at that
  minute, then the cut-outs and appliance stops due there. The exact place in
  `settleWorld()`'s order is the coding session's, named, and
  `docs/systems/time.md`'s order is updated to match.

**The stovetop kettle** heats on a lit stove or campfire as a saucepan does
(C), cleans tainted water by the 3 minutes at the boil, and never cuts out.
**When its water reaches 100 °C from below, it whistles**: a scheduled event
at that minute, "The kettle starts to whistle." logged if the player is in
its room. Once per boil: it whistles again only after its water has been
below the boil.

**The fixtures go.** Remove `kettle` from `WIRING_TEMPLATES.row_house` and
`.casa` (and so `casa_fuses`). `APPLIANCES.kettle` stays, as what the load
is; its figures comment becomes the 1–1.2 L range (1,800–2,400 W, most
commonly 2,200–2,400 W; 2,200 W kept; secondary), and gains the 88 %.

**Where they're found.**

- **Every home kitchen except the player's rolls once**, keyed
  `stableHash(id + KEY_SEP + "kettle") % 100`, independent of the door, board
  and jug rolls: below `KETTLE_ELECTRIC_PCT = 49` an electric kettle **on
  the kitchen floor**; below `KETTLE_ELECTRIC_PCT + KETTLE_STOVETOP_PCT`
  (48) a stovetop kettle **on the stove, unlit**; otherwise none (Tom's
  first-hand estimate, retunable). Home kitchens are the generated casas'
  and `row_neighbour`'s.
  - The electric kettle's floor is laid **beside** a dispenser jug's, never
    over it.
  - **The stove must still roll its pools**: a hand-placed stovetop kettle
    would otherwise set the stove `spawnRolled:true` and suppress
    `kitchen_perishable` and `kitchen_tools` there. Give that stove
    `spawnRolled:false` explicitly, and keep an old board's drawers override.
- **The player's own kitchen**: an electric kettle, empty, hand-placed on
  its floor beside the dispenser jug.
- **Pools** (chosen, retunable; add them to the pool comment's exceptions):
  `office_supplies` electric kettle 0.20; `hardware_store` electric kettle
  0.20 and stovetop kettle 0.20. `hardware_store` never rolls until #133;
  the entries wait for it. **No `electronics` entry.**
- All found kettles are empty and off.

## Design decisions to make during implementation

Record each pick in the changelog.

1. **How a running electric kettle enters the resolve.**
   - (a) **A static plug load per socket-served room**, added by
     `expandWiring()` (appliance `kettle`, marked as a plug so the Electrical
     view lists no fixture and offers no switch for it), powered while its
     circuit is live and drawing `n × watts` for the `n` running kettles in
     that room, `n` passed to the pure resolve as `floats` is (e.g.
     `plugs:{ loadId: n }`); a building with `n > 0` is busy.
   - (b) Dynamic load nodes added to a building's sub-network for each
     running kettle at resolve time.
   - **Recommended: (a).** Every reader of `POWER_NET.loads` (`logTrips()`,
     `logGridChange()` through `roomLoads`, the meters' breaker currents)
     then works unchanged, and the still-building rule needs one more input,
     not a new node type. Check the memoised `untouchedTrippers()` and
     `stillLook()` treat a plug with no kettle as drawing nothing.
2. **The temperature's shape and helpers** (C): `fluid.temp = { c, at }`
   recommended; the dish's water likewise.
3. **`TEMP_MERGE_TOLERANCE_C`** and whether a fluid near room temperature
   drops its stamp (C).
4. **The tint's colours, curve and saturation points** (D).
5. **How a heat container states its power** (C).
6. **The microwave's minute picker** layout (E).
7. **`state.power.stops`'s name and shape** (E).
8. **The two kettles' categories** (F), neither `STACKABLE`.

None changes the version type.

## Data / schema changes

- **PLAYER STATE:** `state.power.stops` (E). New persistent state:
  **MINOR**, the save key rotates. No migration: an imported older save
  reads no `stops`, and every absent temperature is the room's.
- **Item instance:** `fluid.temp` (C); a water dish's water and its
  temperature (C); `on` on the electric kettle (F).
- **Item schema** (ITEM DATA SCHEMA comment updated): `holdsFluid.coolPerMin`
  (or the chosen name), `holdsFluid.heats`, the whistle flag, the kettle's
  appliance link. `boilMinutes`' description changes to time at the boil.
- **Containers / rooms:** the heat container's power (C); the stove's
  `spawnRolled:false` where a stovetop kettle is placed (F).
- **POWER SCHEMA:** `APPLIANCES` stop rules (E); the template circuit's
  socket flag (F); the plug loads if (a) (F); the kettle fixtures removed.
- **Items:** `electric_kettle`, `stovetop_kettle`. **Placements:** the
  canteen (A), the kettles (F). **Pools:** three entries (F).

## Costs

- **Per game minute:** nothing new. Temperatures are worked out when read;
  nothing ticks.
- **Per event:** a lit room's settle now also does the linear heating
  arithmetic per heating holder, as it already settles each vessel. A
  running kettle's settle is one holder. An appliance stop or kettle
  cut-out resolves one building, as a tank coming full does. After a
  resolve, the stop rule walks that building's loads with a `stops` entry
  (none in an untouched building).
- **Per advance:** `planNextDue()` adds the least `stops` minute and each
  running kettle's cut-out, and `heatRoomDue()` adds time to the boil to its
  arithmetic.
- **Per render:** each row reads one temperature (one `exp`) for its tint.
- **Per action:** a timed fill or pour runs `advanceTime()` for its minutes,
  as any timed action does.
- **Load:** `rebuildSchedule()`'s existing walk also finds running kettles.
- With (a), the expanded network gains one plug load per socket-served room
  (a few per home), built once.
- Expected to stay within the Performance check's tolerance. If a sleep or
  `render()` slows, say what was measured in the pull request.

## In scope

- [ ] A: the canteen in `unit1`.
- [ ] B: timed fill and pour over a litre, costs on the buttons.
- [ ] C: water temperature: state, reading, cooling constants, tap
  temperatures, mixing, stacking, heating on the stove and campfire, the
  3-minute unbroken boil, water dishes counting at the boil and keeping
  their water's temperature, scheduling and the Wait button.
- [ ] D: the row tint.
- [ ] E: the toaster's and microwave's stops, the microwave's minutes,
  power-cut rules, `state.power.stops`, the lines.
- [ ] F: both kettles, plugging in, running, cut-out, whistle, the fixtures
  removed, the kitchen roll, the player's kettle, the pools.
- [ ] `validateItemRegistry()`, `validateWiring()`, `validateReachability()`
  and `replayProblems()` extended to the new data and lists.
- [ ] The systems docs (below).

## Explicitly out of scope

- Hot water doing anything when drunk; the mate setting (unsourced).
- Food, dead fauna and plants having a temperature: #217.
- Weather replacing the room and tap temperatures: #58.
- Using the microwave, toaster or washing machine on food or clothes: #422,
  #423, #424.
- Cords and plugging in anything but the electric kettle: #243, #244.
- Cooking gas running out: #342. Burning and unattended cooking: #179.
- Over-fusing a tapón: #365 (stays parked for a later MINOR).
- `hardware_store` and `outdoor_camping` never rolling in general: #133.
- Interruptible waits: #212. Measured cooling curves and well-water
  temperature: still open in the reference folder.

## Sections touched

CONFIG / CONSTANTS; ITEM DATA SCHEMA and ITEM DATA; WORLD DATA (BUILDING
TYPES and instances, SPAWN POOLS, POWER SCHEMA: `APPLIANCES`,
`WIRING_TEMPLATES`); PLAYER STATE (`state.power`); SURVIVAL / TIME
SIMULATION (the scheduler, POWER); INVENTORY / ITEM SYSTEM (FLUIDS, the
fill, the pour, moves that lift a running kettle); FIRE / COOKING (VESSELS
AND DISHES, heating, the boil); WORLD INTERACTION (`doSwitchLoad()`, the
kettle's switch); PERSISTENCE (load's `state.power` rebuild); RENDERING (the
tint, the pop-up's kettle actions, the microwave's minutes, the Electrical
view, button costs).

## Systems docs

- **Read first:** `docs/systems/fluids.md`, `docs/systems/time.md`,
  `docs/systems/power.md`.
- **Update in the same pull request:**
  - `fluids.md`: temperature (state, reading, mixing, stacking, new water),
    which holders heat, the boil at the boil, dishes' water, timed
    transfers, the tint; Costs ("Nothing is scheduled" no longer holds);
    Constants.
  - `time.md`: the new scheduled systems and their events (appliance stops,
    running kettles' cut-outs, the whistle), heating in a lit room's settle,
    the order at one minute, the runtime list of running kettles, the saved
    fields; `BOIL_MINUTES`' meaning.
  - `power.md`: stop rules and `state.power.stops`, the post-resolve rule,
    the portable kettle and socket circuits (and plug loads if (a)), what
    makes a building busy; the invariant "Only the grid changes power over
    a span" still holds (every stop is a settle point).
- No number goes into a systems doc: name the constant.

## UI changes

- Fill and pour buttons show a time cost when the transfer is over a litre.
- Item rows holding water (and pots of water dishes) are tinted by
  temperature.
- The electric kettle's pop-up offers Switch on / Switch off while plugged
  in; its row shows "(On)" while running.
- The Electrical view no longer lists a kettle; the microwave's Switch on
  asks for minutes; the toaster and microwave readouts go back to "Stopped"
  when they stop.
- Log lines (Tom, 2026-10-03): "The kettle clicks off.", "The kettle
  starts to whistle.", "The toaster pops up.", "The microwave pings."; and
  switching on without power, "You push the lever down. It won't stay." and
  "You press the switch. It clicks straight back up." The kettle's switch-on
  line is functional: "You switch the kettle on." / "You switch the kettle
  off."

## Dependencies / issue linkage

- Fulfils, in one pull request: `Closes #431`, `Closes #334`,
  `Closes #385`, `Closes #411`, `Closes #415`.
- Unblocks #422 and #423 (their appliances now stop), #217 (the temperature
  model and tint to extend), #342 (fuel the kettle saves).
- To file at the wrap: anything cut, and an issue for hot water's effects
  when drunk if none exists by then.

## Open questions for Tom

None.
