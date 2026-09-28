# Ashfall Handoff — Wire the `row_house` type

Current shipped version: v0.10.4
Implied version-change type: PATCH
Issue: #305 — Wire the `row_house` type — the player's home first, and wiring carried by a building type

## What this is

The first of the type passes under #250. A building type learns to carry its
own wiring, and the builder expands it for every instance. The `row_house`
(the player's home and the neighbours' house on the same courtyard) is the
first type wired, with its real board as Tom describes it: the main at a
shared meter bank on the courtyard, and a modern board in the living room
headed by a diferencial. Wiring is a definition and isn't saved, so this is a
PATCH (#305: "PATCH (`tier-1`): wiring is a definition and isn't saved").

## Relevant existing state

Verified against `ashfall.html` at v0.10.4.

**Buildings (WORLD DATA, BUILDING TYPES).**
- `BUILDING_TYPES.row_house` has rooms by role: `living` (entry), `kitchen`,
  `laundry`, `hallway`, `bedroom`, `bedroom2`, `bathroom`, and `garden`
  (`shelter:"none"`). Its comment says "Nothing is wired".
- The comment above `KITCHEN_CONTAINERS` ends "Nothing a type builds is wired:
  every room falls back to the grid (containerPowered())".
- `KITCHEN_CONTAINERS` carries `stove`, `cupboards`, `drawers`, `fridge` and
  `freezer`.
- Two instances in `landmarkInstances()`, both on `HOME_STOP`
  (`m_c90b_c117_c119`): `home` (name "Home") and `row_neighbour` (name "Row
  house").
- `buildBuilding()` names rooms `<instance id>_<role>`; the role `"street"`
  maps to the instance's `site`, the courtyard stop.
- The home overrides the living room's `desc`: "Your living room, as you left
  it. The television is dark, and your mate is still on the table where you
  set it down."
- The type's hallway `desc` is "A short hallway. The breaker box is on the
  wall by the bathroom door."
- The type's living-room `desc` is "A living room with the dining table at
  one end. The bars on the window throw stripes across the floor, and a gas
  heater stands against the wall."
- The courtyard stop's text (`LIMA_STOP_TEXT`, key
  `m_c90b_c117_c119`) is "The courtyard in front of your row, in the Barrio
  Atucha. Four houses under red-tile roofs face the paths and the parking
  spaces. The neighbours' blinds are down."

**Power (WORLD DATA, POWER SCHEMA; SIMULATION, POWER).**
- `WIRING` is `{}`, keyed by building id. `POWER_NET = expandWiring(WIRING,
  WIRING_TEMPLATES)`. `WIRING_TEMPLATES.apartment` exists only for the dev
  seam (`simulatePower()`); leave it alone.
- `expandWiring()` builds, per building `b`: `b.board` with main
  `b.board.main` (layer `board`), and per panel `P`, a feeder `b.board.P`
  (layer `feeder`), the panel `b.P` with main `b.P.main` (layer `panel`),
  circuits `b.P.<key>` (layer `circuit`) and loads `b.P.<fixture key>`. A
  board with no feeder for a panel is reported as a problem.
- `powerSnapshot()`: a board is live when the grid is and its main is closed.
  A panel is `supplied` when its board is live and its feeder is closed
  (simplified rules skip the feeder), and live when its main is closed too.
- `resolvePowerStep()` runs the instant trip, then the heat trip, over every
  breaker in the layers the rules consult: `consultedLayers()` gives
  `["panel", "board"]` under simplified rules, all four otherwise.
- `state.power` is `{ switches, breakers, heat }`, keyed by node id, and a
  default is never written, so new ids need no new state field.
- Breakers default to curve C (`DEFAULT_BREAKER_CURVE`).
- A room nothing wires falls back to the grid (`containerPowered()`).
- `APPLIANCES` has `fridge_freezer`, `led_light`, `hall_light`, `range_hood`
  and `gas_range`. Each entry carries exactly one of `leftOnChance` and
  `switchless`, a `readout { on, off }` exactly when it has a switch, and a
  `nameplate` in one of three forms (`{ amps }`, `{ printsWatts:true }`,
  `{ watts }`). `validateWiring()` enforces all three.
- `LED_BULB_WATTS` is 10.
- A cycling load draws for `dutyCycle × cycleMinutes` of every
  `cycleMinutes`.
- `loadStatusText()` shows `readout.on` while the load is powered, else
  `readout.off + " · switched on|off"`.

**The electrical view (UI/RENDERING).**
- A device's pop-up lists its breakers as `${label} · ${rating} A · On|Off|Tripped`,
  with Switch on / Switch off / Reset.
- `deviceStripText()` reads "Main on" / "Main off" (plus "· N tripped")
  under detailed rules.
- `doSwitchBreaker()` logs "You switch the ${label} breaker on|off."
- `doorNamesFor()` already disambiguates two identical door names on one
  courtyard by appending the building's name: "Front door (Home)".

### Reference figures this pass depends on

From `docs/canon/reference/Electrical_AR.md` (quoted here, since a coding
session doesn't read it):

- **The row house's board, Tom first-hand (2026-09-28):** the meters in a
  shared bank by the parking spaces on the courtyard, each house's main
  beside its meter; a modern board in the living room; a diferencial over
  every circuit; three circuits (lights; sockets; the water heater with the
  pump); the water heater and pump in the laundry; no range hood.
- **Main at the meter:** a bipolar breaker, **at most 32 A** on a Tarifa 1
  supply (OCEBA). Confirmed.
- **Diferencial:** every terminal circuit behind a **≤ 30 mA** RCD; one may
  cover several circuits and may be the distribution board's head device.
  AEA's worked example uses **30 mA, 2 × 40 A** at the head. Confirmed.
- **Circuit maxima:** IUG (lighting) 16 A, TUG (general sockets) 20 A.
  AEA's example uses 10 A for lighting and 16 A for sockets. Confirmed.
- **Electric water heater:** Rheem's 85 L TEC085RH has a **2,000 W element**
  (primary). **Standing loss:** termotanques lose **1.5–9 kWh/day** keeping
  their water hot (Gil 2020, primary; not split by fuel).
- **House pump:** 0.5 hp peripheral pump, Rowa RW-PR60 **0.37 kW, 2.7 A**
  at 220 V (secondary).
- **Kettle,** 1.7 L: **2,200 W**, the most common figure (1,850–2,200 W;
  secondary).
- **Toaster,** two slots: **700 W** (Atma TO8020i and TO2180; the range is
  700–850 W; secondary).
- **Small microwave,** 20 L, "700 W" output: **1,150 W input** (BGH B120M16,
  dial, 10 A plug; the range is 1,050–1,150 W; secondary).
- **Rating plates:** IEC 60335-1 §7.1 allows "rated power input in watts or
  rated current in amperes". Which form an Argentine kettle's, toaster's or
  water heater's plate uses is **unconfirmed**; every listing quotes watts.

## Rules / mechanics

### 1. A building type carries its wiring

- A `BUILDING_TYPES` entry (and a one-off instance's `layout`) may carry
  wiring: a board, one panel, and the panel's layout (circuits and fixtures
  by room role, in `WIRING_TEMPLATES`' shape), with each device's room given
  **by role**.
- The builder produces a `WIRING`-shaped entry for every instance of a wired
  type, keyed by the instance id, mapping roles to that instance's room ids
  (`<id>_<role>`, and `"street"` to its site). The game's network is built
  from the authored `WIRING` merged with these expanded entries.
  `validateWiring()` covers the merged network, and it must report no
  problems at load.
- Expanded ids follow `expandWiring()`'s existing scheme, derived from the
  instance id: `home.board`, `home.board.main`, `home.<panel>`,
  `home.<panel>.main`, `home.<panel>.<circuit>`, `home.<panel>.<fixture>`.
  They are saved (switch and breaker state), so they must never change once
  shipped.
- A type without wiring stays unwired, and its rooms keep falling back to the
  grid (`casa`, `shop_home`, `galpon` and the police station, until their own
  passes).
- Per-instance overrides of the type's wiring are **not** needed in this
  pass: the home and the neighbours' house are wired identically.

### 2. The row house's network

| Device | Where (role) | Name | Head device |
|---|---|---|---|
| Board | `street` (the courtyard stop) | **Meter box** | main breaker, **32 A**, curve C |
| Panel | `living` | **Breaker panel** | the **diferencial**, **40 A**, label **RCD** |

**No feeder breaker** sits between the meter box's main and the breaker
panel: a real *tablero principal* holds only the main. With no feeder, the
panel is supplied whenever the meter box is live.

Circuits on the breaker panel, in this order (curve C, the default; 220 V):

| Key | Label | Rating | Roles |
|---|---|---|---|
| `lights` | LIGHTS | 10 A | `living`, `kitchen`, `laundry`, `hallway`, `bedroom`, `bedroom2`, `bathroom` |
| `sockets` | SOCKETS | 16 A | `kitchen` |
| `water` | WATER | 16 A | `laundry` |

Fixtures:

| Key | Appliance | Circuit | Role | Containers |
|---|---|---|---|---|
| `light_living` | `led_light` | lights | `living` | |
| `light_kitchen` | `led_light` | lights | `kitchen` | |
| `light_laundry` | `led_light` | lights | `laundry` | |
| `light_hallway` | `led_light` | lights | `hallway` | |
| `light_bedroom` | `led_light` | lights | `bedroom` | |
| `light_bedroom2` | `led_light` | lights | `bedroom2` | |
| `light_bath` | `led_light` | lights | `bathroom` | |
| `fridge` | `fridge_freezer` | sockets | `kitchen` | `fridge`, `freezer` |
| `stove` | `gas_range` | sockets | `kitchen` | `stove` |
| `kettle` | `kettle` | sockets | `kitchen` | |
| `toaster` | `toaster` | sockets | `kitchen` | |
| `microwave` | `microwave` | sockets | `kitchen` | |
| `water_heater` | `water_heater` | water | `laundry` | |
| `pump` | `house_pump` | water | `laundry` | |

No light in the garden (indoors only). No range hood. No TV and no washing
machine (#333).

### 3. The diferencial (RCD)

- It is the breaker panel's head device, in the place a panel main takes
  today: power passes it only while it is closed.
- **It never trips on overcurrent.** It takes part in neither the instant
  trip nor the heat trip, under either rules mode, and it never accumulates
  heat. Its leakage trip is #247's, not this pass's.
- It is switchable by hand: Switch off / Switch on, like a breaker. Its state
  lives in `state.power.breakers` like any breaker's (on/off; `tripped`
  never set).
- **Under simplified rules** the panel's one device is its RCD, so the only
  overcurrent protection left is the meter box's 32 A main. That is intended.
- Its row reads `RCD · 40 A · On|Off`. The 30 mA sensitivity isn't shown
  anywhere in this pass.

### 4. New appliances

Every figure below is retunable. Every readout is `{ on:"Running",
off:"Stopped" }` (Tom, 2026-09-28: clear and concise, the device's state
kept apart from its switch's). So a load reads **"Running"** while powered,
**"Stopped · switched on"** when its circuit is dead, and **"Stopped ·
switched off"** when its own switch is off.

| Id | Name | `watts` | `leftOnChance` | Other | `nameplate` |
|---|---|---|---|---|---|
| `kettle` | Electric kettle | 2200 | 0 | | `{ printsWatts:true }` (form unconfirmed) |
| `toaster` | Toaster | 700 | 0 | | `{ printsWatts:true }` (form unconfirmed) |
| `microwave` | Microwave | 1150 | 0 | | `{ printsWatts:true }` |
| `water_heater` | Water heater | 2000 | 0.95 | `dutyCycle`, `cycleMinutes` below | `{ printsWatts:true }` (form unconfirmed) |
| `house_pump` | Water pump | 370 | 0 | no `startWatts` (#317) | `{ amps:2.7 }` |

All `volts:220`.

- **`leftOnChance` 0** for the kettle, toaster, microwave and pump: each
  starts switched off in every run. Once the player switches one on, it
  **stays on and keeps drawing until switched off** (Tom, option (a):
  self-switch-off is #334, MINOR). The pump draws while switched on but does
  nothing yet; its use is #317.
- **The water heater is left on (0.95, a judgment call) and cycles on its
  thermostat.** Its standing loss is taken as 2.4 kWh/day, inside Gil's
  1.5–9 kWh/day (a judgment call, retunable). Write the derivation, not the
  result: `dutyCycle` = 2.4 kWh ÷ (2 kW × 24 h) = **0.05**, from a named
  constant for the daily loss, the heater's own watts and the hours in a day.
  `cycleMinutes` **120** (a judgment call), so it heats about 6 minutes in
  every 2 hours. No hot-water use is modelled.
- **The fridge and the gas range are the existing appliances**, unchanged.

### 5. What the numbers do (for checking, not for coding)

- LIGHTS: 7 × 10 W = 70 W, about 0.3 A.
- WATER: 2,000 + 370 W = 2,370 W, about 10.8 A of 16.
- SOCKETS, everything on: kettle + toaster + microwave = 4,050 W, 18.4 A,
  1.15 × 16 A; with the fridge's compressor on, 4,150 W, 18.9 A, 1.18 ×.
  Under the heat model that trips SOCKETS after **roughly 30 hours** left on
  (about 37 h at 1.15 ×, 21 h at 1.18 ×), and never within the minutes a
  real kettle would run. **This is expected**: a player who leaves all three
  on will eventually lose the fridge. The fridge's start (1,300 W) is far
  below C16's instant trip (160 A).
- Whole house at once: 70 + 4,150 + 2,370 = 6,590 W, about 30 A, under the
  32 A main.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **Where the type's wiring lives, and its shape:** a `wiring` field on the
   type, or a `WIRING_TEMPLATES` entry the type names. Either works; the
   expanded ids above are what must hold.
2. **The panel's id** (the `<panel>` in `home.<panel>.*`), for example
   `house`. It isn't shown to the player, but it's saved, so pick it once.
3. **How "no feeder" is expressed:** feeders made optional in
   `expandWiring()` and `powerSnapshot()` (an absent feeder counts as closed),
   or another shape with the same behaviour. `validateWiring()` must not
   report the missing feeder as a problem for a board that deliberately has
   none. The dev seam's apartment (which has feeders) must behave exactly as
   it does today.
4. **How the RCD is modelled:** a breaker kind flagged as never tripping on
   overcurrent (skipped by both trip passes), or a separate device kind. Its
   `rating` must still pass the IEC-preferred-rating check (40 A does).
5. **The named constant for the heater's daily standing loss** and where it
   sits (beside `LED_BULB_WATTS` is the obvious place).

## Data / schema changes

- **No new state fields.** New switch and breaker ids join
  `state.power.switches` and `state.power.breakers` under their existing
  shapes, and a default is never written. PATCH.
- **BUILDING TYPES schema:** a type (and `layout`) may carry wiring
  (decision 1). Update the schema comment and remove "Nothing is wired" /
  "Nothing a type builds is wired" where they no longer hold. Unwired types
  still fall back to the grid; say so.
- **POWER SCHEMA:** document the optional feeder and the RCD head device
  (decisions 3 and 4) in the `WIRING` and `WIRING_TEMPLATES` comments.
- **APPLIANCES:** five new entries (section 4).
- **World text:** the four text changes under UI changes.

## In scope

- [ ] A type carries wiring; the builder expands it per instance; the network
      and `validateWiring()` cover the result.
- [ ] `row_house` wired as in section 2, for both `home` and `row_neighbour`.
- [ ] The RCD: switchable, never trips on overcurrent (section 3).
- [ ] The meter box without a feeder breaker.
- [ ] Five appliances (section 4).
- [ ] Device names disambiguated at the courtyard (UI changes).
- [ ] The four text changes (UI changes).
- [ ] Comments updated where they say nothing is wired.

## Explicitly out of scope

- **The pump actually filling the tank** and its start surge: #317. Running
  water keeps its current rule.
- **Appliances switching themselves off, and being used** (the kettle
  boiling water, the microwave heating food): #334, MINOR.
- **The TV and the washing machine:** #333, waiting on #332's figures.
- **The RCD's leakage trip, and shock:** #247.
- **A range hood** in the row house (Tom: not for now). `range_hood` stays in
  `APPLIANCES` for the dev template.
- **A garden light.**
- **Other building types:** #306 `casa` (and its old fuse boards), #307,
  #308, #309, #299.
- **Removing the unwired-room fallback:** #258.
- **The dev seam's `apartment` template:** unchanged.
- **Any mention of the water heater in room text.**

## Sections touched

- **WORLD DATA:** BUILDING TYPES (the type's wiring, two `desc` changes, the
  home's living-room override), the courtyard stop's text, POWER SCHEMA
  (`APPLIANCES`, the schema comments, `WIRING` merge).
- **SIMULATION → POWER:** `expandWiring()` (optional feeder, RCD head
  device), `powerSnapshot()` (absent feeder), `resolvePowerStep()` (the RCD
  skipped by both trips), `validateWiring()`.
- **ACTIONS:** `doSwitchBreaker()`'s log line for the RCD.
- **UI/RENDERING:** device names at one stop, the RCD row and strip text.

This pass carries both mechanics (a type carrying wiring, the RCD, the
optional feeder) and the data that is those mechanics' own definition (the
row house's wiring, its appliances): `CLAUDE.md`, "Content vs. mechanics",
the one case that touches both. The four text changes describe where the
new devices hang.

## UI changes

**Room and stop text** (Tom approved, 2026-09-28):

- Type `row_house`, `hallway`: **"A short hallway. A calendar still hangs on
  the wall by the bathroom door."**
- Type `row_house`, `living`: **"A living room with the dining table at one
  end. The bars on the window throw stripes across the floor, and a gas
  heater stands against the wall. The breaker panel hangs on the wall by the
  front door."**
- The home's `living` override: **"Your living room, as you left it. The
  television is dark, and your mate is still on the table where you set it
  down. The breaker panel is on the wall by the door."**
- The courtyard stop (`m_c90b_c117_c119`): **"The courtyard in front of your
  row, in the Barrio Atucha. Four houses under red-tile roofs face the paths
  and the parking spaces. The neighbours' blinds are down. The row's
  electricity meters stand together in a box by the parking spaces."**

**Device names** (Tom approved "Meter box", "Breaker panel", "RCD"):

- Both houses' meter boxes hang at the courtyard. Where two devices in one
  room would read the same name, each is followed by its building's name, as
  `doorNamesFor()` does for doors: **"Meter box (Home)"**, **"Meter box (Row
  house)"**. Everywhere a device's name is shown (its Here tab, its pop-up
  heading). Functional UI text, retunable.

**The RCD** (functional UI text, retunable):

- Its pop-up row: `RCD · 40 A · On|Off`, with Switch off / Switch on and
  never Reset.
- The Here strip, detailed rules, for a panel headed by an RCD: **"RCD on" /
  "RCD off"** in place of "Main on" / "Main off", plus "· N tripped" as
  today.
- Its log lines: **"You switch the RCD on."** / **"You switch the RCD off."**
  (not "the RCD breaker").

**Appliance readouts:** "Running" / "Stopped" (section 4).

## Dependencies / issue linkage

- Fulfils **#305**.
- Unblocks **#317** (the pump), **#306–#309** (the other types build on a
  type carrying wiring), **#333** (the TV and washing machine, once #332's
  figures exist) and **#334**.
- The reference figures landed with this handoff (from #332). #332 stays
  open for what's still missing: the TV's figures, the washing machine's
  plate and start surge, the microwave's standby draw, and the plates' form.
- If implementation surfaces anything else deferred, file it at the wrap.

## Open questions for Tom

None.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new
`CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`, citing this handoff as
`Implements: handoffs/row-house-wiring.md`. Record the design decisions
above in its Notes/assumptions, and the judgment-call figures (the heater's
standing loss, `leftOnChance` 0.95, `cycleMinutes` 120, the circuit ratings,
the toaster's and microwave's picks, the plates' unconfirmed form) as
retunable. Move this handoff to `handoffs/archive/` with `git mv` in the
same pull request. `Closes #305`.
