# Ashfall Handoff — The house pump fills the roof tank

Current shipped version: v0.10.5
Implied version-change type: PATCH (no new state field; `state.tankDrawn`
  already exists)
Issue: #317 — The house pump fills the roof tank only while it has power — a
  load, not the grid

## What this is

A house's roof tank is refilled by its electric pump, and only while that pump
has power, not whenever the grid is up. The pump has an automatic float
switch: it starts when the tank drops below 80 % and fills it to full, drawing
power only while it fills. A tripped WATER circuit, a pump switched off or an
opened main now stops the refill, and the taps run only while the tank holds
water.

## Relevant existing state

Verified against `ashfall.html` at v0.10.5.

**Water (SURVIVAL / TIME SIMULATION, just below `gridUp()`):**
- `tankOf(roomId)` is the room's building's tank in litres, from
  `BUILDING_INFO[buildingId].tankL`, or 0 for none.
- `tankLeft(roomId, m)` returns the full `size` while `gridUp(m)`. Otherwise it
  returns `size - state.tankDrawn[buildingId]`, floored at 0.
- `waterRunningIn(roomId, m)` is `gridUp(m) || tankLeft(roomId, m) > 0`.
- No caller passes `m` to either.
- The comment above `tankOf()` says the tank's pump is unwired and stops with
  the grid.

**Tanks (BUILDING TYPES):**
- `HOUSE_TANK_L = 1000`, just above `BUILDING_TYPES`.
- `row_house`, `casa` and `shop_home` each carry `water:{ tankL:HOUSE_TANK_L }`.
- Every room with `sink:true` today is in one of those three types.
- The schema comment for `water` says the tank is "filled by a house pump,
  which keeps its sinks running after the grid fails until it is drawn dry".
  It also says "Absent: its sinks run on the grid alone."

**`state.tankDrawn` (PLAYER STATE):**
- `{}` by building id, litres drawn.
- Its comment says it is written only after the grid fails, because "while the
  grid is up its pump keeps every tank full".
- The loader (PERSISTENCE, about line 8575) resets a malformed value to `{}`.

**Sinks (ACTIONS):**
- `canFillAtSink(it)` needs `room.sink`, `waterRunningIn()` and
  `canTakeWater(it)`. It then returns
  `gridUp() || !vesselDefOf(it) || tankLeft(...) >= sinkLitresFor(it)`: a
  vessel off a tank needs its whole `waterKg`, and a bottle may part-fill.
- `doFillAtSink()` sets `fromTank = !gridUp() && tankOf(...) > 0`. Only when
  `fromTank` does it add the litres to `state.tankDrawn[b]`, rounded to the
  millilitre. It logs "The tap coughs, spits, and runs dry." when a tank fill
  empties the tank.
- `tapDryFor(it)` makes the item pop-up show "The tap is dry."

**The pump (POWER SCHEMA → `APPLIANCES`):**
```
house_pump: { name:"Water pump", watts:370, volts:220, leftOnChance:0, nameplate:{ amps:2.7 },
  readout:{ on:"Running", off:"Stopped" } }
```
- Its comment says it "draws while switched on and does nothing yet: filling
  the tank, and its start surge, are #317's, so no `startWatts`".
- The paragraph below that comment lists the pump among the loads found
  switched off.
- It is wired in `WIRING_TEMPLATES.row_house` as
  `{ key:"pump", appliance:"house_pump", circuit:"water", role:"laundry" }`, on
  WATER, 16 A, curve C, beside the `water_heater`.
- The load ids are `home.house.pump` and `row_neighbour.house.pump`.
- `casa` and `shop_home` carry no `wiring`, so they have no pump load.

**The resolver (POWER):**
- `powerSnapshot(net, appliances, power, rules, gridLive, minute, prevDrawing,
  seed)` is pure.
  - A load is `powered` when its circuit is live and `switchOnIn()` is true.
  - It is `drawing` when it is powered and, if it cycles (`dutyCycle`,
    `cycleMinutes`), is in the on part of its cycle.
  - It is `starting` when it carries `startWatts`, is drawing, and was not
    drawing in `prevDrawing`. With no `prevDrawing`, nothing starts.
  - `momentary` counts a starting load at its `startWatts`.
- `resolvePowerStep()` calls `powerSnapshot()` with the same arguments.
- `stepPower(dt)` passes `powerNow ? powerNow.drawing : null` as
  `prevDrawing`.
- `refreshPower()` builds a snapshot with `prevDrawing` null (on boot, restart
  and load).
- `loadPoweredNow()` builds a fresh snapshot with `prevDrawing` null.
- `simulatePower()` (dev helpers) drives `resolvePowerStep()` for a network
  minute by minute.
- `applyWorldTicking(min)` calls `stepPower(min)` first.
- `runAwakeStep()` steps time in slices of at most one minute.
- `switchOnIn()`: a load with no stored switch uses a keyed roll against
  `leftOnChance`. `state.power.switches` stores only a switch that differs
  from its roll.
- `loadStatusText()` shows `readout.on` whenever the load is powered, whether
  or not it is drawing. #337 tracks that; it is not this pass.

**The precedent for a surge:** `fridge_freezer` carries `startWatts:1300`,
and its cycle turning on counts as a start.

**Reference figures** (`docs/canon/reference/Electrical_AR.md`, quoted here
because the coding session doesn't read it):
- A 0.5 hp peripheral pump for a roof tank is 0.37 kW, 2.7 A (Rowa RW-PR60,
  secondary).
- Its flow is 1,800–2,400 L/h. Tom picked 2,400 (Czerweny QB60-L1, 40 L/min).
- Its start is about 5–6× its running current. For these pumps that is
  about 8.5–16.5 A, or **1,900–3,600 W**. The figure is derived, and
  secondary (from WEG's 60 Hz motors).
- A 1,000 L tank refills from empty in 25 minutes at 2,400 L/h (derived).

## Rules / mechanics

All decided by Tom on 2026-09-28 (#317's comments).

1. **The pump's figures** (`house_pump`, definition data for this mechanic):
   - `leftOnChance: 0.99`: found switched on, like the fridge. Retunable.
   - `startWatts: 3300`, the total draw at a start: 2.7 A × about 5.5 ×
     220 V, inside the 1,900–3,600 W found. Secondary, retunable.
   - `flowLph: 2400`, a new optional appliance field: the pump's flow in
     litres per hour. The mechanic finds a tank's pump by this field, never
     by the id `house_pump` ("Mechanics check tags, never names").
   - `watts` (370), `nameplate` and `readout` are unchanged.
2. **The float switch.** A new constant, `TANK_FLOAT_START = 0.8` (a fraction
   of the tank), beside `HOUSE_TANK_L`. It is Tom's figure, not researched,
   and retunable. For a building whose tank has a pump, in each step:
   - the float **calls** when the tank holds less than `TANK_FLOAT_START ×
     tankL` at the start of the step, **or** the pump was drawing in the
     previous step (`prevDrawing`) and the tank is not yet full;
   - the float **doesn't call** when the tank is full.
3. **The pump draws only while the float calls.** A pump load with `flowLph`
   is `drawing` when it is `powered` and its float calls. When the float
   doesn't call, it is powered but not drawing, and adds nothing to any
   breaker's current. A start from not-drawing counts as a start, at
   `startWatts`, through the existing `starting` rule.
4. **The latch comes from the last step and is not saved.** "The pump was
   drawing in the previous step" is `prevDrawing`, which already exists and
   is never saved. Where `prevDrawing` is null (on boot, load, restart,
   `loadPoweredNow()`), only the 80 % test applies. This is a **known,
   accepted gap**: after a load, or when power returns mid-fill, a tank
   between 80 % and full waits until it drops below 80 %. This is what keeps
   the pass PATCH (Tom, 2026-09-28); saving the latch would be new
   persistent state, so MINOR.
5. **Refilling.** After `stepPower(dt)`, each building's pump that is
   drawing in that step's result reduces `state.tankDrawn[b]` by
   `flowLph / 60 × dt` litres. The result is floored at 0 and rounded to the
   millilitre, as `doFillAtSink()` rounds. An entry that reaches 0 is
   deleted, so a full tank stores nothing.
6. **The water source.** A new named predicate, `mainsWaterUp(m)`, returns
   `gridUp(m)` today: the town's own pumps run on the grid. A pump that is
   drawing refills the tank **only while `mainsWaterUp()`**. If the mains are
   down, it draws power and adds no water. This can't happen yet, since the
   grid is the only power source. The predicate exists so that #300's
   decision (does the network outlive the grid?) has one place to change
   before generators (#245) land. Say so in its comment.
7. **An unwired tank (the fallback).** A building with a tank and no pump load
   in `GAME_WIRING` (today `casa` and `shop_home`) refills while
   `mainsWaterUp()`, at the same rate, `HOUSE_PUMP_FLOW_LPH`. It has no float
   and no latch: it refills whenever it is below full. This is the unwired
   fallback, which ends when #306 and #307 wire those types (#258).
   `HOUSE_PUMP_FLOW_LPH` is a named constant, so the fallback and
   `house_pump.flowLph` read one figure: define the constant beside
   `HOUSE_TANK_L`, and set `flowLph: HOUSE_PUMP_FLOW_LPH`.
8. **The tank is drawn at any time.**
   - `tankLeft(roomId)` is `max(0, tankOf(roomId) - (state.tankDrawn[b] || 0))`,
     whatever the grid.
   - `waterRunningIn(roomId)` is `tankLeft(roomId) > 0` for a room whose
     building has a tank, and `mainsWaterUp()` for one without. No room with a
     sink lacks a tank today.
   - `canFillAtSink()` drops its `gridUp() ||` shortcut: a tank fill always
     follows the tank rules (a bottle may part-fill, a vessel needs its whole
     `waterKg`).
   - `doFillAtSink()`'s `fromTank` is `tankOf(...) > 0`.
   - "The tap coughs, spits, and runs dry." can now happen before the grid
     fails, for example with the pump switched off.
9. **Starting state.** A run starts with every tank full (`tankDrawn` `{}`),
   as now. With the float at full, no pump is drawing at the start.
10. **Existing saves.** Nothing migrates.
    - A save made before the grid failed has `tankDrawn` `{}`, a full tank:
      correct.
    - A save made after it keeps its drawn litres: correct.
    - An untouched pump now rolls on (0.99) instead of off. A pump the player
      switched on stays on. Mention it in the changelog.

**Sanity figures, derived.** While filling, the pump draws 370 W, or 1.7 A.
The WATER circuit carries the heater (2,000 W) and the pump. Running, that is
about 10.8 A on a 16 A breaker; at the pump's start, about 24 A momentary,
against C16's instant trip at 160 A. So nothing trips, under either rules. A
simulated check is asked for under "After implementation".

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

- **How the float reaches the resolver.** `powerSnapshot()` is pure and knows
  nothing of tanks. Options:
  - (a) a new argument, a map or function giving each float-controlled load's
    "tank below the start level" and "tank full" facts, which the snapshot
    combines with `prevDrawing` as rule 2 says;
  - (b) the caller computes a set of loads whose float calls and passes it in.

  Either way, `resolvePowerStep()`, `refreshPower()`, `loadPoweredNow()`,
  `stepPower()` and `simulatePower()` pass it. `simulatePower()` may take it
  from `options`, defaulting to "no float calls".

  Recommended: (a), so the latch rule stays in one place, the resolver.
- **How a tank finds its pump.** A table built once at startup from
  `POWER_NET.loads`: a load whose appliance has `flowLph`, keyed by its room's
  building id. Recommended. Or a lookup per step.
- **What `validateWiring()` / `validateBuildings()` report.** A building with
  a `wiring` entry and a tank but no `flowLph` load; and a building with two.
  Recommended: report both.
- **Whether `tankLeft()` / `waterRunningIn()` keep their `m` parameter.** No
  caller passes one, and the tank is now stored state, not a function of
  time. Recommended: drop it.

## Data / schema changes

- **PLAYER STATE:** no new field. `state.tankDrawn` keeps its shape, but is
  now written whenever water is drawn and lowered by refilling. Update its
  comment.
- **POWER SCHEMA (`APPLIANCES`):**
  - `flowLph?` joins the schema comment: "a pump's flow in L/h; present on a
    load that fills its building's tank, drawing only while the tank's float
    calls".
  - `house_pump` gains `flowLph`, `startWatts:3300` and `leftOnChance:0.99`.
  - Its figure comment gives the surge's derivation and source, and the float
    switch (Tom, first-hand).
  - It moves out of the list of loads found switched off.
- **BUILDING TYPES:**
  - `HOUSE_PUMP_FLOW_LPH = 2400` and `TANK_FLOAT_START = 0.8` go beside
    `HOUSE_TANK_L`, with their sources and "retunable".
  - The `water` schema comment reads: a tank refilled by the building's pump
    while it has power, or, where the building is unwired, while the mains
    run.
- No item, room, container or exit schema change. No new content instance.

## In scope

- The pump's three figures and `flowLph` (rule 1).
- The float, the draw only while filling, and the latch from `prevDrawing`
  (rules 2–4).
- Refilling per step, from a powered pump and from the unwired fallback
  (rules 5 and 7).
- `mainsWaterUp()` (rule 6).
- The tank drawn at any time, across `tankLeft()`, `waterRunningIn()`,
  `canFillAtSink()` and `doFillAtSink()` (rule 8).
- The comments this makes wrong:
  - CONFIG / CONSTANTS, the collapse clock: "the pumps run on the grid…";
  - ROOM SCHEMA `sink`;
  - BUILDING TYPES `water`;
  - PLAYER STATE `tankDrawn`;
  - the sink block above `canFillAtSink()`;
  - the water block above `tankOf()`, and the `gridUp()` comment's line "The
    water follows the grid, not a building's power";
  - `APPLIANCES`' pump comments.
- `simulatePower()` accepts the float input.

## Explicitly out of scope

- **The readout** saying "Running" while the pump stands idle (#337).
- **Whether the town network outlives the grid** (#300). This pass only adds
  the predicate.
- **Generators** (#245) and **changeover switches** (#246).
- **Showers and toilets** drawing water, and **the town tank** (#300).
- **Wells** (a different water source, later).
- **Wiring `casa` and `shop_home`** (#306, #307), and **removing the
  fallback** (#258).
- **Any tank gauge or new UI**, and any new room text about the pump.
- **Saving the float's latch** (rule 4: deliberately not done).
- **The TV and the washing machine** (#333), and **appliances in use**
  (#334).

## Sections touched

- **WORLD DATA:** POWER SCHEMA (`APPLIANCES`: `flowLph` in the schema, and the
  `house_pump` entry and comments); BUILDING TYPES (the two new constants, and
  the `water` comment); the ROOM SCHEMA `sink` comment. This is definition data
  for the new rule, so it rides along. No instance data.
- **CONFIG / CONSTANTS:** the collapse-clock comment only.
- **PLAYER STATE:** the `tankDrawn` comment only.
- **SURVIVAL / TIME SIMULATION → POWER:** `powerSnapshot()`,
  `resolvePowerStep()`, `stepPower()`, `refreshPower()`, `loadPoweredNow()`,
  and the tank refill after `stepPower()` in `applyWorldTicking()` (or a
  helper it calls).
- **SURVIVAL / TIME SIMULATION, water:** `mainsWaterUp()`, `tankLeft()`,
  `waterRunningIn()`.
- **ACTIONS:** `canFillAtSink()`, `doFillAtSink()`.
- **Dev helpers:** `simulatePower()`, `validateWiring()` /
  `validateBuildings()`.
- **UI/RENDERING:** none.

## UI changes

None new. What the player notices:
- A sink can run dry before the grid fails, when the pump is switched off or
  its circuit is tripped. The existing line and "The tap is dry." cover it.
- The pump's meter reads current only while it fills.
- The pump is found switched on.

## Dependencies / issue linkage

- Fulfils #317.
- Unblocks the water half of bundle A (#239 + #245): the pump's surge is
  what a small generator has to start.
- **#300** must decide whether the network outlives the grid before bundle A
  is planned. `mainsWaterUp()` is where that lands.
- **#337** (the readout while idle) is separate, and is not blocked by this.
- Anything deferred beyond that list gets a new issue at the wrap. The gap in
  rule 4 is accepted, not deferred: it needs no issue.

## Open questions for Tom

None. All were answered on 2026-09-28 (#317's comments).

## After implementation

Open a pull request carrying:
- the version bump (PATCH);
- a new `CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, naming this handoff
  by path and recording the "Design decisions" choices;
- `Closes #317`.

Before opening it:
- With `simulatePower()` on the row house's wiring and a tank drawn below
  80 %, show the pump drawing, one start at 3,300 W, and the tank refilling at
  40 L/min to full and then stopping.
- Show the WATER breaker and the RCD not tripping with the heater and the
  pump both drawing.
- Show that a pump switched off, or a WATER breaker switched off, leaves the
  tank unfilled while the grid is up.
- Confirm `validateWiring()`, `validateBuildings()` and `validateRoomSchema()`
  report no problems.
