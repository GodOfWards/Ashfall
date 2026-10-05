# Ashfall Handoff — Battery cells, and the copper bodge

Current shipped version: v0.13.2
Implied version-change type: MINOR
Issue: #388 — Batteries as cells; #365 — Over-fusing a tapón

## What this is

Two `designed` mechanics bundled into one MINOR. #388: "AA and D cells that
keep their charge, devices that take them, and a voltmeter Test", which
fixes the free recharge from removing and replacing batteries. #365: "a
copper strand in place of fuse wire, and what it costs", which was parked
until some MINOR rotated the save key (Tom). This pass is that MINOR.

The two parts share no code. Build them as two phases: cells first, then
the bodge.

## Relevant existing state

Verified against `ashfall.html` at v0.13.2.

**Batteries today**:

- `flashlight` ("Flashlight", 0.2 kg, `drainRate:100/480`, 8 h) and
  `portable_radio` ("Portable radio", 0.4 kg, `drainRate:100/2880`, 48 h).
  Both carry `on`, `hasBatteries` and
  `durability:{ current, max:100, mode:"time" }`.
- `spare_batteries` ("Spare batteries", Materials, 0.05 kg, tag `battery`).
  It appears in three places: the player's home bedside (2, beside the
  flashlight and the wristwatch); `residential_personal` (chance 0.263672,
  qty 1–2); and `ACTION_GRANTED_ITEM_IDS`.
- The flashlight is in `car_glovebox` (0.2). The radio is in the
  electronics pool (0.069728).
- `batteryActions()` offers Turn on/off and "Remove batteries" (it gives
  one `spare_batteries`, whatever the charge) on a device with batteries.
  It offers "Replace batteries" whenever `countByTag("battery") >= 1`, even
  on a device that has batteries. Replace consumes one and sets
  `durability.current = max`. This is the bug: charge is lost on Remove and
  invented on Replace. Those are the only users of the `battery` tag.
- `batteryCharge()` gives the charge, worked out when read from
  `durability.asOf` while the device is on. `switchDevice()` is the one way
  a device is switched on or off. `scheduleBatteryDeath()` and
  `batteryDeaths` (runtime list, rebuilt by `rebuildSchedule()`) work with
  `settleBatteryDeaths()`, which switches off a device that has run out,
  with its line by where it is.
- `durabilityText()` already shows a battery device as only "On", "Off" or
  "No batteries installed" (#134 shipped in v0.12.0). There's no charge
  figure.
- `sameStackState()` refuses to merge any row that carries `durability`.
  #134's groups key rows with `groupKeyOf()` and draw levels with
  `levelMeter()` (`LEVEL_WARN_BELOW`).
- Items held inside an item already exist: a pot's `contents`. Don't reuse
  `contents` for cells, because the cooking code walks `contents`.
- `rolledLootFor()` → `rolledPoolFor()` is a pure, keyed roll of a seed and
  a container's identity. `stampAges()` stamps a rolled row after the roll.
- `validateReachability()` only reports, never fails. Unreachable items are
  expected until the spawn balance is done (#133).
- The Electrical view's Test is `doMeterTest()`, offered while a
  `voltage-test` tool is carried (`multimeter`, `clamp_meter`). It costs
  `METER_READING_MIN` (1).
- **The benchmark and the replay both build radios:** `benchScenario()`
  (`switchDevice()` on a `portable_radio` from the registry), and the
  replay's "Three radios run down" step. That step sets
  `r.durability.current = r.drainRate * minutes` and then clicks "Turn on".

**Old fuse boards today** (`docs/systems/power.md`):

- A casa off the barrio has an old board when `hasOldBoard()` rolls under
  `OLD_BOARD_PCT`. Its template is `casa_fuses`: a cut-off main and one
  circuit, `fuses` ("Fuses", `OLD_BOARD_FUSE_A` = 15 A, `fuse:true`),
  serving every room.
- Its loads are the casa's fixtures: LED lights, the fridge-freezer (100 W
  average), toaster 700 W (3.2 A), microwave 1150 W (5.2 A), TV 43 W
  (0.2 A), water heater 2000 W (9.1 A), and pump 370 W (1.7 A, starting
  3300 W). There are no fuse curves, so a fuse ignores starts. The electric
  kettle (2200 W, 10 A) runs through a socket's plug load. Everything at
  once is about 30 A.
- `canRewireFuse()` / `doRewireFuse()` work only on a blown fuse, with
  `screwdriving` and fuse wire of its rating (`fuseWireFor()`). They spend
  one length and take `REWIRE_FUSE_MIN` (5), then call
  `changePower(… rewireFuseIn())`. `rewireFuseIn()` is `resetBreakerIn()`,
  and `setBreakerIn()` **deletes the breaker's entry** when it is on and
  untripped.
- `resolvePower()` is pure and has no time in it. A fuse blows when
  `snap.running[id] > rating`. `untouchedTrippers()` predicts trips for
  untouched buildings from the definitions' ratings. A bodged building has a
  power-state entry, so it's busy and the prediction doesn't apply to it.
- `logTrips()` logs "Something pops in the fuse box." at the board, and
  `ROOM_GOES_QUIET` ("Everything in here goes quiet.") where something it
  fed was running. `breakerStateText()` shows a fuse as "Blown" or
  "Intact". The row reads `${label} · ${rating} A · ${state}`.
- The power invariant "only the grid changes power over a span" means the
  running current is constant between resolves. That's why an event planned
  at a resolve is enough.
- Electrical rules are fixed for a run (`state.electricalRules`; a change
  takes effect at restart). Simplified rules still consult a fuse
  (`consultsBreaker()`).
- `EDISON_FUSE_MAX_A` (30) validates the definitions only.
- The pools the offcut goes in:
  - `tools_general`: the shed box, the laundry shelf, and the
    building-materials yard's tool wall and bins.
  - `tools_workshop`: the repair shop's workbench and parts shelf, and the
    yard's paint aisle.

**Reference figures**, quoted here because the coding session reads no
reference:

- **Cell weights.** AA alkaline 23 g, D alkaline 139 g. Confirmed
  (`Batteries.md`).
- **Devices.**
  - Small flashlight: 2 × AA, 8 h, body 105 g (Derived, Unconfirmed).
  - Large flashlight: 2 × D, 40 h, body 225 g (Derived).
  - Portable radio: 2 × AA, 50 h (Confirmed, FM through the speaker; volume
    isn't modelled), body 140 g (Secondary).
- **An AA alkaline's resting voltage by charge left** (Texas Instruments
  SLVA194, Figure 3; Confirmed as a measurement, read off a graph to about
  ±0.02 V):

  | Charge | 100 % | 90 % | 80 % | 70 % | 60 % | 50 % | 40 % | 30 % | 20 % | 10 % | 0 % |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | At rest (V) | 1.59 | 1.44 | 1.38 | 1.34 | 1.32 | 1.30 | 1.28 | 1.26 | 1.23 | 1.20 | 1.10 |

  Applying it to D cells is **Unconfirmed**: no source gives a D-size
  table. Energizer says a reading at rest "at best will only yield a rough
  estimate". That is intended.
- **The bodge.** The whole core of 1.5 mm² cable melts at **≈ 130 A**
  (Preece, I = 80·d^1.5 with d in mm, d ≈ 1.38 mm equivalent; Derived, for
  a long wire in free air).
- **What 1.5 mm² PVC wiring in conduit carries.** Iz = **15 A** (Cobrhil,
  IRAM NM 247-3; primary for the maker). Whether old Lima houses are wired
  in 1.5 mm² is unconfirmed.
- **AEA's overload rule:** I2 ≤ 1.45 Iz (secondary).

## Rules / mechanics

### Phase 1: cells (#388)

**Items.**

- `aa_battery` "AA battery" and `d_battery` "D battery": Materials,
  0.023 kg and 0.139 kg.
  - Each carries a tag naming its size, `cell-aa` / `cell-d`. Mechanics
    check the tag.
  - Each carries its own charge, 0–100. A loose cell doesn't drain.
- `flashlight` keeps its id and is renamed **"Small flashlight"**: body
  0.105 kg, cells 2 × `cell-aa`, run time 8 h (`drainRate` 100/480).
- New `large_flashlight` "Large flashlight": body 0.225 kg, cells 2 ×
  `cell-d`, 40 h (100/2400). It gets no placement and no pool entry.
- `portable_radio`: body 0.14 kg, cells 2 × `cell-aa`, 50 h (100/3000).
- A device's weight is its body plus the cells inside it, as a pot's
  contents count toward its weight (2 AA = 46 g, 2 D = 278 g).
- `spare_batteries` is retired:
  - the bedside's 2 become **2 AA**;
  - `residential_personal`'s entry becomes **`aa_battery`, qty 2–4**, at the
    same chance;
  - it leaves `ACTION_GRANTED_ITEM_IDS`, and nothing replaces it there,
    because Remove only returns cells the world already placed;
  - the `battery` tag goes.

**Stacking.** Cells merge only at equal charge, so new ones stack and spent
ones form their own rows, inside one group (#134) with a smooth meter
showing the row's charge. A cell's charge is never shown as a figure. Its
pop-up has the meter and no number, and the only figure is the Test (below).

**In a device.**

- A device's cells sit inside it as real items. While it is on they drain
  together, each losing `drainRate` per minute, worked out when read as
  today.
- **The device dies when its weakest cell is flat.** Its death is scheduled
  at the weakest cell's charge ÷ `drainRate`.
- The device shows no charge. Its pop-up keeps On/Off only, and a lit one's
  row shows (On) as today.
- **Remove batteries** is offered on a device holding cells. It switches the
  device off first if it's on, and gives back each cell at its own charge.
  It is silent, as today.
- **Insert batteries** replaces "Replace batteries". It is offered only on a
  device holding **no** cells (Tom, 2026-10-05), and only while the player
  carries at least N cells of the device's size. It takes **the fullest N**
  carried. It is silent. To swap cells, Remove and then Insert.
- A device holding no cells reads "No batteries installed", as today, and
  can't be turned on.

**Found charge**, for items a **pool** rolls only (Tom, 2026-10-05):

- A device a pool rolls holds no cells at `FOUND_DEVICE_NO_CELLS_PCT` = 10.
  Otherwise it holds a full set, all at **one** rolled charge, since the
  cells wore together.
- That charge is `100 − (100 − FOUND_CHARGE_MIN) · u^FOUND_DEVICE_CHARGE_SKEW`,
  with u uniform in [0, 1), `FOUND_CHARGE_MIN` = 10 and
  `FOUND_DEVICE_CHARGE_SKEW` = 2 (median ≈ 78 %).
- A row of loose cells a pool rolls shares one charge, as one pack, using
  the same formula with `FOUND_CELL_CHARGE_SKEW` = 4 (median ≈ 94 %). That
  is further toward new than a device's.
- All four constants are judgment calls, retunable. The rolls are keyed and
  pure, like the loot roll: a function of the seed and the row's container,
  pool and entry, with their own key component, so they're independent of
  every other roll.
- **Hand-placed items are not rolled.** A hand-placed device comes with a
  full set and hand-placed cells are full, unless a placement's overrides
  say otherwise. A device from `itemFromRegistry()` has a full set.

**Test** (#388, Tom 2026-10-05 for the time):

- A **Test** action on a loose cell row, offered while a `voltage-test` tool
  is carried. Loose cells only, never cells inside a device.
- It takes `METER_READING_MIN`.
- It logs: `You put the probes across the cell. It reads ${v} V.`, with v
  to one decimal place. v is the table above interpolated linearly between
  its rows at the cell's charge, for D cells too.
- On a row of several cells, it reads the row's charge, since they're all
  equal.

**Old saves** (migration, run on load, idempotent, beside the existing
`migrate…Release()` functions):

- Every `spare_batteries` row, carried or in the world, becomes 2 full AA
  cells per unit.
- A battery device's current charge goes to each of its cells. One with
  `hasBatteries:false` holds none.
- `durability` and `hasBatteries` go from battery devices, whichever
  representation replaces them.

**The benchmark and the replay.**

- `benchScenario()` needs no change beyond what the registry gives: a fresh
  radio holds a full set.
- The replay's radio step must set its radios' cells to the same charge it
  sets today (`drainRate × minutes`), so each still runs out after its
  minutes.
- This pass's `replay_compare.py` run against its base will differ on that
  step's digest. That is expected, and the changelog says so.

### Phase 2: the copper bodge (#365)

**The item.** `cable_offcut` "Offcut of cable (1.5 mm²)", Materials,
**0.01 kg**. The weight is a judgment call, unconfirmed (Tom, 2026-10-05;
the reference has no figure). Its tag is `copper-bodge`.

- Pools: `tools_general` at 0.15, qty 1, and `tools_workshop` at 0.25,
  qty 1–2. Both chances are judgment calls, retunable.

**Rewiring.**

- A blown fuse offers **"Rewire with copper"** beside "Rewire". It needs a
  `screwdriving` tool and one `copper-bodge` item, spends one, and takes
  `REWIRE_FUSE_MIN`.
- It logs: "You strip the offcut, unscrew the blown plug, wind the copper
  core under its screws and screw it back in."
- The fuse then holds a **fitted rating** of `COPPER_BODGE_A` = 130, which
  the resolve uses in place of the definition's rating.
- **"Rewire"** with proper fuse wire is offered on a blown fuse, as today,
  **and on an intact bodged one** (Tom, 2026-10-05). It restores the
  definition's rating and clears the fitted one. Its log line is the
  existing one.
- The fitted rating must survive `setBreakerIn()`. Today that deletes an
  entry that is on and untripped, and the fitted rating has to outlive that.
- **The fuse's row doesn't change** (Tom, 2026-10-05): it still reads
  "Fuses · 15 A · Intact". The bodge is inside a screwed-in plug.

**Overheating** (detailed electrical rules only, Tom, 2026-10-05):

- The wiring's limit is `OLD_WIRING_IZ_A` = 15.
- `OVERHEAT_BURN_STEPS` gives the time to burn by the fuse's running
  current, in multiples of Iz. These are judgment calls, retunable; the
  amps in #365 are these multiples, rounded.

  | Running current | Burns after |
  |---|---|
  | under 1.45 × Iz (21.75 A) | never |
  | 1.45 × Iz and up | 240 min |
  | 1.73 × Iz and up (25.95 A) | 60 min |
  | 2 × Iz and up (30 A) | 15 min |
  | 2.5 × Iz and up (37.5 A) | 5 min |

- **Start.** The first resolve of the building that leaves a fuse's running
  current at or above the first step records the minute overheating began
  (saved).
- **Re-planning.** Every later resolve re-plans the burn at that start plus
  the current step's time. If that minute has already passed, the burn
  happens at once.
- **Cancelling.** A resolve that brings the current under the first step
  cancels it and clears the start. No damage carries over.
- The resolve stays pure. The start, the cancel and the planning happen
  where the resolve is committed (`commitResolve()`), which has the minute.
- **The warning** comes at half the current step's time after the start:
  "You catch a smell of hot plastic, from somewhere in the walls." It is
  logged only if the player is in the building at that minute.
  - A re-plan whose warning minute has already passed gives no warning. So
    a sudden jump in load can burn the wiring unwarned, and no saved flag is
    needed. This is a named implementation choice, retunable.
- **The burn** is a scheduled event (`docs/systems/time.md`), processed in
  the order at one minute right after the appliance stops.
  - The circuit is recorded **burnt** (saved, per circuit) and its building
    resolves.
  - A burnt circuit gives nothing downstream power, whatever its fuse says,
    under either rule set. Only the overheating clock is detailed-only.
  - The overheating start clears.
  - The burn logs what a trip does: `ROOM_GOES_QUIET` where something it fed
    was running, and nothing elsewhere. There's no line at the board.
- **Nothing extra shows a burnt circuit** (Tom, 2026-10-05). The fuse still
  reads Intact, everything on it is dead, and a Test on a load reads no
  voltage.
- Repairing a burnt circuit is out of scope (#179 hooks fire onto it).

**Never a per-minute check.** A burn and a warning are planned only at a
resolve of their building: an action, a float, a tank coming full, a stop,
a kettle, the grid. The schedule rebuild (`rebuildSchedule()`) re-plans them
from the saved start on new game, restart and load.

## Design decisions to make during implementation

Record each pick in the changelog.

- **A cell's charge field.** It must not be `durability`, because
  `sameStackState()` never merges a row with one. A plain `charge` (0–100),
  compared exactly in `sameStackState()` and drawn by `levelMeter()`, is
  recommended.
- **The device's cell definition and its held cells.** For example, a
  registry `cells:{ tag:"cell-aa", count:2 }`, and an instance `cells:[…]`
  holding real cell rows. Recommended: not `contents`.
- **Where the bodge state lives in `state.power`.** The fitted rating, the
  overheating start and `burnt`. Recommended: on the breaker's entry,
  `{ on, tripped, fitted?, hotSince?, burnt? }`, with `setBreakerIn()`
  keeping the entry while any of the three is set.
- **The pick of the fullest N** when cells tie: any stable order.

## Data / schema changes

- **Items:** `aa_battery`, `d_battery`, `large_flashlight`, `cable_offcut`
  added; `spare_batteries` retired (migrated); `flashlight` renamed, with a
  new weight and cells; `portable_radio` gets a new weight, run time and
  cells.
- **Tags:** `cell-aa`, `cell-d`, `copper-bodge` added; `battery` removed.
- **Instance state:** a cell's charge; a device's held cells; battery
  devices lose `durability` and `hasBatteries`.
- **PLAYER STATE:** in `state.power`, a fuse's fitted rating, its
  overheating start, and a circuit's `burnt`.
- **Save:** MINOR, and the save key rotates. Import migration as above.
  #365's state needs no migration (absent means none).

## Costs

- **Per game minute:** nothing.
- **Per resolve of a building with a bodged fuse:** one comparison of its
  running current against the steps, and at most one event planned.
- **Per scheduled event:** a warning or a burn, one building.
- **Batteries:** as today, one scheduled death per switched-on device, at
  its weakest cell.

## In scope

- Phase 1: the cells, the devices, Remove and Insert, stacking and meters,
  found charge, the Test, the migration, and the replay's radio step.
- Phase 2: the offcut, "Rewire with copper", Rewire on a bodged fuse,
  overheating, the warning, the burn, and burnt circuits.
- The systems docs below, and the `ARCHITECTURE` comment if a section's
  contents change.

## Explicitly out of scope

- The Large flashlight's placements, and any D-cell pool entry. File one
  content issue at the wrap.
- The car battery (#261).
- Fire from a burnt circuit (#179), and repairing one.
- Shock from rewiring live (#247).
- More loads that could reach the burn steps (#244's cords, heaters, #245's
  generator). The curve may want retuning then.

## Sections touched

- ITEM DATA SCHEMA and ITEM_REGISTRY (cells, devices, offcut).
- SPAWN POOLS and the home's placements.
- INVENTORY / ITEM SYSTEM (`batteryActions()`, `batteryCharge()`,
  `switchDevice()`, `sameStackState()`).
- SURVIVAL / TIME SIMULATION (battery deaths, the burn and warning events,
  POWER's resolve commit and fuse state).
- WORLD INTERACTION (rewiring, the cell Test).
- RENDERING (cell rows' meter, the device pop-up, the fuse pop-up's
  actions).
- PERSISTENCE (the migration, the replay step).
- The reachability lists (`ACTION_GRANTED_ITEM_IDS`).

## Systems docs

Read before starting: `docs/systems/time.md` and `docs/systems/power.md`.
Update both in this pull request:

- `time.md`: the battery model by cells; the burn and warning in the
  scheduled systems and the order at one minute.
- `power.md`: the bodge, the fitted rating, overheating and burnt circuits;
  the constants.

## UI changes

- Cell rows with meters.
- "Insert batteries" in place of "Replace batteries".
- "Test" on a loose cell.
- "Rewire with copper" on a blown fuse, and "Rewire" on a bodged intact one.
- Two new log lines (the Test, the bodge), plus the warning.

## Dependencies / issue linkage

- Fulfils #388 and #365: `Closes #388`, `Closes #365`.
- Builds on #134 (shipped).
- Unblocks #261 (charge on cells) and #179 (burnt state).
- At the wrap, file the Large flashlight and D-cell placement issue.

## Open questions for Tom

None.
