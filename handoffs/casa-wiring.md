# Ashfall Handoff — Wire the `casa` type, and a power resolver that scales to it

Current shipped version: v0.10.7
Implied version-change type: PATCH
Issues: #359 — The power resolver doesn't scale to Lima; #306 — Wire the `casa` type — Lima's 427 generated homes

## What this is

The second type pass under #250, in two phases, one handoff (Tom,
2026-09-30).

- **Phase 1 (#359):** the power resolver is made to cost about the same per
  game minute whether 2 buildings are wired or all of Lima's are, with
  results identical to today's.
- **Phase 2 (#306):** every `casa` is wired with a modern board, as the row
  house is. Old fuse boards are not part of this pass (#358).

Both are PATCH: no new persistent state, since `state.power` keeps its shape
and wiring is a definition that isn't saved.

## Relevant existing state

Verified against `ashfall.html` at v0.10.7.

**Time and the power step (SIMULATION → POWER).**
- Time advances in steps of at most one minute (`runAwakeStep()`, `doRest()`,
  `doSleep()`). Every step calls `applyWorldTicking(dt)`, which calls
  `stepPower(dt)` first, then `refillTanks(dt)`, `ageFood(dt)` and the rest.
- `stepPower()` runs `resolvePowerStep()` over the **whole** game network
  (`POWER_NET`) and stores the result in `powerNow`. Its comment says "the
  networks are tens of rooms, so there is no cache to keep honest." That is
  true only because just the two row houses are wired.
- `resolvePowerStep()` calls `look()` (a full `powerSnapshot()`) once per
  consulted layer for the instant trip, once per layer for the heat trip, and
  once more at the end. Under detailed rules that is **9 full snapshots a
  step**, whether or not anything tripped. Only a trip changes the snapshot's
  inputs; `setHeatIn()` does not.
- `powerSnapshot()` walks every board, panel, load and breaker in the network.
  For each cycling load it calls `rollValueFor(seed, ["power", "cycle",
  id])`, and for each load with no stored switch it calls `switchOnIn()` →
  `chanceFor(…)`. Both are pure functions of the seed and the load id.
- The readers of `powerNow`: `isPowered()` (spoilage, through
  `containerPowered()`), `refillTanks()` (a pump's `drawing`), the meters
  (`loadSupplyVolts()` and the rest), `logGridChange()` (loads in the current
  room, only on a grid transition) and `logTrips()`.
- `loadPoweredNow()` takes a fresh full `powerSnapshot()` on every call, for
  a load's readout.
- `state.power` is `{ switches, breakers, heat }`, keyed by node id. A writer
  never stores a default: `setSwitchIn()` deletes an entry that matches the
  rolled starting state, `setBreakerIn()` deletes a closed, untripped one,
  and `setHeatIn()` deletes a zero heat. So a building nobody has touched has
  no entries.
- `expandWiring()` gives every node an id prefixed by its building id
  (`b.board`, `b.board.main`, `b.P`, `b.P.main`, `b.P.<circuit>`,
  `b.P.<fixture>`). Buildings share nothing but the grid.
- `refillTanks()` walks only `state.tankDrawn`, the tanks with litres drawn.
  A building with a tank and a pump load (`TANK_PUMPS`) refills only while
  that pump draws. A tank with no pump refills at `HOUSE_PUMP_FLOW_LPH`
  whenever the mains run.
- `ashfallDev.simulatePower(network, minutes, options)` runs the resolver on a
  supplied network, and returns one row per step with `running`,
  `momentary`, `heat`, `trips`, `powered`, `drawing`, `starting` and
  `tanks`.

**Measured cost (planning session, headless Chromium, 2026-09-30).**

| Case | Time |
|---|---|
| In-game Rest (60 one-minute steps), today, nothing but the row houses wired | ~150 ms |
| The same Rest, every casa wired as in Phase 2, today's resolver | **~4,400 ms** |
| The same, with `look()` reused until a trip and the cycle phase memoized | ~650 ms |

The last row came from a scratch copy that wasn't committed. It shows that two
exact changes buy about 7×. A CPU profile of that copy puts nearly all the
remaining power cost in the one full `powerSnapshot()` a step still takes,
about 6–8 ms. Memoizing the default switch roll as well made no measurable
difference. **Reaching the budget below needs the step to stop walking
buildings nobody has touched.**

**The `casa` type (WORLD DATA, BUILDING TYPES).**
- Rooms by role: `living` (entry, `sleepSpot:"couch"`, no containers),
  `kitchen` (`sink`, `KITCHEN_CONTAINERS`: `stove`, `cupboards`, `drawers`,
  `fridge`, `freezer`), `bedroom`, `bathroom` (`sink`), and `patio`
  (`shelter:"none"`, `SHED_BOX`). `water:{ tankL:HOUSE_TANK_L }`. No `wiring`.
- Its `living` text: "A front room that is living room and dining room both.
  Barred windows onto the street, the blinds half down."
- `generatedHomes()` builds one `casa` on every mid stop (`kind "m"`) except
  `HOME_STOP`: id `h_<stop id>`, name "House", `site` the stop. In the Barrio
  Atucha they stand in for the chalets until #299.
- Three landmarks share a mid stop with a generated casa: the pharmacy
  (`m_c7_c10_c8`), the comisaría (`m_c12_c13_c15`) and the building-materials
  yard (`m_cbar_dg2_c107`). None of them is wired, so no device name clashes
  in this pass. `deviceNamesFor()` already appends the building's name where
  two devices in one room would read the same.
- `buildBuilding()` maps the role `"street"` to the instance's site stop, and
  `buildWiring()` turns a type's `wiring` (a board and panels, each placed by
  `role`) into a `WIRING` entry per instance. `GAME_WIRING` merges them.

**The row house, the model to follow.**
- `BUILDING_TYPES.row_house.wiring`: `board:{ name:"Meter box",
  role:"street", rating:32, direct:true }`, `panels:[{ id:"house",
  name:"Breaker panel", role:"living", template:"row_house" }]`.
- `WIRING_TEMPLATES.row_house`: `main:{ rating:40, rcd:true }`. Circuits
  `lights` (LIGHTS, 10 A), `sockets` (SOCKETS, 16 A) and `water` (WATER,
  16 A), all 220 V. Fixtures: an `led_light` per room, and in the kitchen
  `fridge` (`fridge_freezer`, containers `fridge`, `freezer`), `stove`
  (`gas_range`, container `stove`), `kettle`, `toaster` and `microwave`.
  `water_heater` and `pump` (`house_pump`) are on the laundry's WATER
  circuit.
- `validateWiring()` reports a building with a tank and no pump load, or
  more than one.

### Reference facts this pass depends on

From `docs/canon/reference/Electrical_AR.md`, quoted here since a coding
session doesn't read it:

- **The meter is on the property line** (OCEBA, Reglamento de Acometidas
  T1): in a brick or precast pillar at the front when the house is set back,
  on the façade when the façade is on the line, and reachable from the street
  24 hours a day. **The main board is within 1 m of it**, with a bipolar
  breaker of **at most 32 A** on a Tarifa 1 supply. Confirmed.
- **The indoor distribution board** goes "en lugares de fácil localización
  dentro de la vivienda", never in a bathroom (AEA 90364-7-770
  §770.16.3.2). Confirmed.
- **A Lima home heats its water with an electric tank heater, and an electric
  pump lifts water to the roof tank. Both are common** (Tom, first-hand).
- Every other figure (the 40 A diferencial, the circuit ratings, the
  appliances' watts) is the row house's, already in the file.

## Rules / mechanics

### Phase 1 — The resolver scales (#359)

**1. Results are identical.** For every input, every value a reader gets is
the same as today's resolver gives: `powered`, `drawing`, `starting`,
`live`, `supplied`, `running`, `momentary`, the trips (their ids, causes,
`running` lists and order), and the new `state.power`. This holds under both
rules modes, with the grid up, down and changing, and with tanks, switches,
breakers and heat in any state. This is not an approximation pass: nothing
is simplified, averaged or skipped where it could change a result.

**2. The budget.** An in-game Rest (60 one-minute steps) on a fresh game,
**with every casa wired as in Phase 2**, takes **no more than twice** what
the same Rest takes on v0.10.7 in the same browser. That's about 300 ms
against today's ~150 ms on the planning session's machine. Sleep is held to
the same ratio. The ratio is a judgment call, retunable.

**3. Two exact changes are required**, since they're free and proven:
- Within one `resolvePowerStep()`, a snapshot is reused until a trip
  changes the power state. It is not re-taken for every layer.
- A load's cycle phase (`rollValueFor(seed, ["power", "cycle", id])`) is
  computed once per seed and load id, not once per snapshot.

**4. The step stops walking buildings nobody has touched.** Section 3 isn't
enough on its own (see the measured cost). How this is done is Design
decision 1. Whatever it is, rule 1 holds. These facts make it exact:
- Buildings share nothing but the grid, so each can be resolved on its own.
- A building with no entries in `state.power` has all its breakers closed,
  its switches at their rolled defaults, and no heat.
- Such a building can trip only if its default-on loads can overload one of
  its breakers. That means their running watts over the rating (heat trip),
  or their momentary watts over the curve's instant multiple (instant trip),
  with every motor load starting at once, as after the grid returns. This
  can be checked once per building, per seed.
- A building whose tank has nothing drawn (no `state.tankDrawn` entry) has a
  full tank, so its pump never draws.

**5. The comment above `stepPower()` is rewritten** to say what's true now:
how the step stays cheap, and what keeps it honest.

**6. `loadPoweredNow()`** looks at the load's own building, not the whole
network.

### Phase 2 — Wire the `casa` (#306)

**1. The type carries wiring**, shaped as the row house's:

| Device | Where (role) | Name | Head device |
|---|---|---|---|
| Board | `street` (the casa's site stop) | **Meter box** | main breaker, **32 A**, curve C, `direct:true` |
| Panel | `living` | **Breaker panel** | the **diferencial**, **40 A**, `rcd:true` |

The panel's id is **`house`**, as in the row house. The expanded ids are
therefore `h_<stop>.board`, `h_<stop>.board.main`, `h_<stop>.house`,
`h_<stop>.house.main`, `h_<stop>.house.<circuit>` and
`h_<stop>.house.<fixture>`. They're saved, so they never change once shipped.

**2. A new `WIRING_TEMPLATES.casa`**, since the casa's roles differ from the
row house's. Circuits, in this order, all 220 V and curve C:

| Key | Label | Rating | Roles |
|---|---|---|---|
| `lights` | LIGHTS | 10 A | `living`, `kitchen`, `bedroom`, `bathroom` |
| `sockets` | SOCKETS | 16 A | `kitchen` |
| `water` | WATER | 16 A | `kitchen`, `patio` |

Fixtures:

| Key | Appliance | Circuit | Role | Containers |
|---|---|---|---|---|
| `light_living` | `led_light` | lights | `living` | |
| `light_kitchen` | `led_light` | lights | `kitchen` | |
| `light_bedroom` | `led_light` | lights | `bedroom` | |
| `light_bath` | `led_light` | lights | `bathroom` | |
| `fridge` | `fridge_freezer` | sockets | `kitchen` | `fridge`, `freezer` |
| `stove` | `gas_range` | sockets | `kitchen` | `stove` |
| `kettle` | `kettle` | sockets | `kitchen` | |
| `toaster` | `toaster` | sockets | `kitchen` | |
| `microwave` | `microwave` | sockets | `kitchen` | |
| `water_heater` | `water_heater` | water | `kitchen` | |
| `pump` | `house_pump` | water | `patio` | |

- **The water heater is in the kitchen and the pump on the patio** (Tom,
  2026-09-30). No patio light. No TV or washing machine (#333).
- **The appliances are the existing ones**, unchanged, so they keep their
  `leftOnChance`, cycles and readouts.
- **Every casa is wired identically**, including those in the Barrio Atucha
  (Tom, 2026-09-30). They're rewired by the chalet's own pass when #299 moves
  them to a `chalet` type. That costs nothing, since wiring isn't saved.

**3. What changes for the player.**
- A casa's tank now refills only while its pump draws: its WATER circuit and
  diferencial are closed, the pump is switched on, and the grid is up. Today
  it refills without power. This is intended: it's how the row house's
  already works.
- A casa's fridge now spoils by its own power: grid, breakers, switch.
- Each casa's street stop shows its **Meter box** in the Here panel. The
  meter box is outside the house, so it's reachable even when the front door
  is locked. That's true of the real thing (OCEBA: reachable from the street).

**4. What the numbers do** (for checking, not for coding): LIGHTS 4 × 10 W =
40 W. WATER 2,000 + 370 W = 2,370 W, about 10.8 A of 16. SOCKETS is the row
house's: under the heat model, everything left on trips it after roughly
30 hours. The whole house is 6,560 W, about 29.8 A, under the 32 A main.
None of a casa's default-on loads can overload anything, so rule 4 of Phase
1 applies to every untouched casa.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **How Phase 1 keeps untouched buildings out of the step** (Phase 1, rule
   4). Recommended default: resolve per building. Each step fully resolves
   only the **active** buildings: any with an entry in `state.power` under
   its ids, a `state.tankDrawn` entry, the current room, or default-on loads
   that could overload a breaker (checked once per seed). An inactive
   building's values are computed on demand, from its own nodes, when
   something reads them (`isPowered()`, a meter, a readout). When a building
   becomes active mid-run, its `prevDrawing` is the pure snapshot of the
   minute before. Any other scheme is fine if rule 1 holds.
2. **Where the per-building index lives**: on the expanded network
   (`expandWiring()`'s output), or built beside it. Either way it's built
   once.
3. **The equivalence harness**, used in the session and not shipped. The
   recommended form: run today's file and the new one side by side in
   headless Chromium with the same seed, and deep-compare:
   - `ashfallDev.simulatePower()` rows over a 429-house network built from
     the Phase 2 template, under both rules, covering:
     - grid down and back up;
     - a SOCKETS overload left on until it heat-trips;
     - an instant trip;
     - a breaker switched off and back on, and a reset;
     - a drawn tank refilling;
   - in game: `state.power`, `state.tankDrawn` and every fridge's contents
     after a Rest and a Sleep, with a few switches and breakers touched
     beforehand.

   Name the scenarios run in the changelog's Validation performed.

## Data / schema changes

- **No new state fields.** New switch and breaker ids join
  `state.power.switches` and `state.power.breakers` under their existing
  shapes, and a default is never written. PATCH.
- **BUILDING TYPES:** `casa` gains `wiring` (Phase 2, rule 1), and its
  `living` text changes (UI changes).
- **POWER SCHEMA:** `WIRING_TEMPLATES` gains `casa`. The comment block above
  it gains a paragraph for it, in the style of the `row_house` one: the
  figures are the row house's; the heater is in the kitchen and the pump on
  the patio (Tom, first-hand); the meter's place is quoted from OCEBA.
- **SIMULATION → POWER:** the Phase 1 changes, and any runtime-only cache
  they need. Such a cache is never saved, and it's rebuilt on boot, restart
  and load, as `powerNow` is (`refreshPower()`).

## In scope

- [ ] Phase 1: identical results (rule 1), proven by the harness.
- [ ] Phase 1: `look()` reused until a trip; the cycle phase memoized.
- [ ] Phase 1: untouched buildings kept out of the step (Design decision 1).
- [ ] Phase 1: `loadPoweredNow()` scoped to the load's building.
- [ ] Phase 1: the `stepPower()` comment rewritten.
- [ ] Phase 1: the budget measured (rule 2). Phase 1 measures it with a
      local, uncommitted copy that wires the casa as Phase 2 does. Phase 2
      measures it again once it's committed.
- [ ] Phase 2: `WIRING_TEMPLATES.casa` and the `casa` type's `wiring`.
- [ ] Phase 2: the living-room text (UI changes).
- [ ] Phase 2: `validateWiring()` reports no problems. Its "unwired" warning
      no longer counts any casa room.

## Explicitly out of scope

- **Old fuse boards**, spare fuses, which homes have them, and earthing:
  #358.
- **Other building types:** `shop_home` (#307), `galpon` (#308), the
  comisaría (#309), `chalet` and `PH` (#299).
- **Removing the unwired-room fallback:** #258.
- **The TV and the washing machine:** #333. **Appliances in use:** #334.
- **The RCD's leakage trip, and shock:** #247.
- **Any mention of the water heater or the pump in room text**, and any
  change to the street stops' text. There are 427 of them, and the meter box
  shows in the Here panel.
- **Any change to `resolvePowerStep()`'s rules**: trips, heat, curves,
  cycles, floats. Phase 1 changes how it's computed, never what it computes.
- **The dev seam's `apartment` template**, unchanged.

## Sections touched

- **SIMULATION → POWER** (Phase 1): `resolvePowerStep()`, `powerSnapshot()`
  or what replaces its per-step use, `stepPower()`, `refreshPower()`,
  `isPowered()`, `loadPoweredNow()`, and the meters' reads of `powerNow`
  where they change. Rendering reads the same values as before.
- **WORLD DATA** (Phase 2): BUILDING TYPES (`casa`'s wiring and living-room
  text), POWER SCHEMA (`WIRING_TEMPLATES.casa` and its comment).

Phase 2 is content that uses mechanics already shipped: a type carrying
wiring, the RCD and the direct board all came with the row house. Phase 1
is engine work with no content in it.

## UI changes

**Room text** (Tom, 2026-09-30: the panel in the living room, with a
sentence naming it):

- Type `casa`, `living`: **"A front room that is living room and dining room
  both. Barred windows onto the street, the blinds half down. The breaker
  panel hangs on the wall by the front door."**

**Devices:** each casa's stop shows **"Meter box"**, and its living room shows
**"Breaker panel"**, with the RCD row, the strip text and the log lines the
row house already uses. Nothing new to render.

## Dependencies / issue linkage

- Fulfils **#359** (Phase 1) and **#306** (Phase 2).
- Unblocks **#307**, **#308** and **#309**, which rely on Phase 1's
  scaling, and **#358**, which builds on the casa's board.
- If Phase 1 can't meet the budget while keeping results identical, stop
  after Phase 1. Ship what it gained, file what's left, and don't commit
  Phase 2. A game where an hour's rest takes seconds is worse than casas that
  still read the grid directly.
- Anything else deferred is filed at the wrap.

## Open questions for Tom

None.

## After implementation

Commit per phase (`Phase 1: …`, `Phase 2: …`) and push the branch after each.
Open the pull request only at the wrap. It carries the version bump (PATCH)
and a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, citing this handoff
as `Implements: handoffs/casa-wiring.md`. Record the design decisions, the
harness's scenarios, and the measured Rest and Sleep times before and after.
Flag as retunable the budget ratio and every figure carried over from the row
house. Move this handoff to `handoffs/archive/` with `git mv` in the same
pull request. `Closes #359`, `Closes #306`.
