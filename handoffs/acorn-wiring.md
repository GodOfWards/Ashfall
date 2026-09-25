# Ashfall Handoff — Acorn Apartments wiring, and the apartment unit template

Current shipped version: v0.9.0
Implied version-change type: PATCH (definitions only; no new persistent state)
Issue: #251 — Wire Acorn Apartments — and define the apartment unit template

## What this is

The first building pass after the power foundation. It gives Acorn Apartments
a real network: the complex's main board, a panel per unit, a house panel for
the halls and stairs, circuits and fixtures, all on v0.9.0's schema. It
defines the first `WIRING_TEMPLATES` entry, `apartment`, which Oak (#252) and
the flats above the shops will reuse. It also adds Acorn's windows and
interior doors, and gives unit 1B a fridge.

From #250: "Wiring and placements are definitions, never saved. A load,
window or door a save hasn't seen before gets its starting state on first
sight, so no pass here breaks saves."

## Relevant existing state

Verified against `ashfall.html` at v0.9.0.

**Power schema (WORLD DATA, the POWER SCHEMA comment above `APPLIANCES`).**
- `APPLIANCES` holds one entry, `fridge_freezer` (150 W, start 525 W, 120 V,
  duty 0.35 over 60 min).
- `WIRING_TEMPLATES = {}` and `WIRING = {}`. The comments above them say
  "None yet: Acorn's pass (#251) defines the first" and "Empty in this
  release: no building is wired yet (#250)".
- Template shape: `{ main:{ rating, volts? }, circuits:[{ key, label, rating,
  volts, roles }], fixtures:[{ key, appliance, circuit, role, containers? }] }`.
- `WIRING[building]`: `board { name, room, rating, volts?, feeders:[{ panel,
  label, rating }] }`, `panels [{ id, name, room, template?, layout?, rooms:{
  role: roomId } }]`, and an optional `common` panel entry that expands
  exactly like a unit panel and needs its own feeder.
- `expandWiring()` builds the ids `acorn.board`, `acorn.board.main`,
  `acorn.board.<panel>` (feeders), `acorn.<panel>`, `acorn.<panel>.main`,
  `acorn.<panel>.<circuit>` and `acorn.<panel>.<fixture>`. A panel's circuit
  and fixture keys share one namespace; a panel may not be called `board` or
  `main`. **Every role a fixture or circuit names must be in the panel's
  `rooms` map**, or expansion reports a problem. So a one-room unit maps every
  role onto that room.
- A fixture's `containers` are container **ids**. `containerLoad` keys on
  `roomId + KEY_SEP + containerId`, and that's how spoilage (`containerPowered()`,
  `effectiveAge()`) finds a container's load. A room nothing wires falls back
  to `gridUp()`.
- `validateWiring()` (`ashfallDev.validateWiring()` in the console) checks
  rooms, containers, appliances, 120/240 V, roles and that every breaker
  rating is in `STANDARD_BREAKER_RATINGS`. It lists fully sheltered rooms no
  panel includes as a warning.
- `PANEL_DEFAULT_VOLTS = 240`. `SWITCH_LEFT_ON_CHANCE = 0.9` rolls every
  load's starting switch (`switchOnIn()`).

**Acorn's rooms (`buildAcornApartments()`).**

| Unit | Living | Kitchen | Bathroom | Bedroom | Balcony / patio |
|---|---|---|---|---|---|
| 2A | `living` | `kitchen` | `bathroom` | `bedroom` | `balcony` |
| 2B | `twobee` | `twobee_kitchen` | `twobee_bathroom` | `twobee_bedroom` | `twobee_balcony` |
| 1A | `onea` | `onea_kitchen` | `onea_bathroom` | `onea_bedroom` | `onea_patio` |
| 1B | `onebee` (one room: the superintendent's unit) | | | | |

Common: `hallway1`, `hallway2`, `stairs1`, `stairs2`.

- Kitchen containers: 2A and 2B have `fridge` and `freezer`. **1A has
  `fridge1a` and `freezer1a`.** 1B has a `stove` and no fridge or freezer.
- In each of 2A, 2B and 1A, the living room connects to kitchen, bedroom,
  bathroom and balcony/patio, and the bedroom and bathroom also connect to
  each other. None of those exits carries a `doorId` except 1A's patio
  (`1a-patio`).
- Doors (`makeDefaultDoors()`): `2a`, `2b`, `1a`, `1b`, `1a-patio`, all
  `building:"acorn"`. The DOOR SCHEMA has `lockable:false` for an interior
  door with no lock.
- Windows (`makeDefaultWindows()`): `2a-transom` (hallway2↔living) and
  `1b-alley` (alley↔onebee), both climbable. The WINDOW SCHEMA's one-room
  window is a window to the outside. Every window offers Open, Close and
  Break (`breakTag`).

**Saves.**
- `serializeGame()` saves the whole `world`, containers and exits included.
  Doors and windows save only `{ locked, open }` / `{ state }` per id, and
  are rebuilt from the definitions on load (`buildDoors()`, `buildWindows()`).
- `migrateCookingRelease()` runs on **every** load (`applyLoadedData()`).
  Among other things, it adds any container the default world has and a
  saved room lacks, matched by id.
- Door actions come from `doorsForRoom()` (the definition's `sides`) as well
  as from exits' `doorId`s. So a save whose exits lack a new `doorId` still
  shows the door's actions from both rooms. Movement ignores `open`.
- Loot rolls key on the container id (`rolledPoolFor(seed, roomId,
  containerId, poolId)`).

## Rules / mechanics

No mechanic changes. Everything below is data, plus one save repair.

### 1. New `APPLIANCES` entries

Figures from the research on #251 (running watts). All 120 V, none cycling.

| id | name | watts | source range |
|---|---|---|---|
| `led_light` | Light | 10 | LED bulb 8–15 W (Champion) |
| `bath_fan` | Exhaust fan | 36 | 10–50 W, average about 36 W (Engineer Fix, HomeAlliance) |
| `range_hood` | Range hood | 200 | 150–300 W on high (Engineer Fix, Storables) |
| `smoke_alarm` | Smoke alarm | 1 | 1–2 W standby, hardwired (Kidde) |

Each figure is a pick inside its sourced range. Retunable. No `startWatts` on
the fan or hood: their start surge is left unmodelled (flag it in the
changelog).

Extend the fridge-freezer's source comment into one covering all five, with
the sources above.

### 2. `WIRING_TEMPLATES.apartment`

```
main: { rating:100 }                      // volts: PANEL_DEFAULT_VOLTS (240)
circuits, in panel order:
  kitchen1  "KITCHEN 1"  20 A  120 V  roles [kitchen]
  kitchen2  "KITCHEN 2"  20 A  120 V  roles [kitchen]
  bath      "BATH"       20 A  120 V  roles [bathroom]
  lights    "LIGHTS"     15 A  120 V  roles [living, kitchen, balcony]
  bedroom   "BEDROOM"    15 A  120 V  roles [bedroom]
fixtures:
  fridge         fridge_freezer  kitchen1  kitchen   containers [fridge, freezer]
  hood           range_hood      lights    kitchen
  light_kitchen  led_light       lights    kitchen
  light_living   led_light       lights    living
  light_balcony  led_light       lights    balcony
  light_bath     led_light       bath      bathroom
  bath_fan       bath_fan        bath      bathroom
  light_bedroom  led_light       bedroom   bedroom
  smoke_alarm    smoke_alarm     bedroom   bedroom
```

- Roles: `living`, `kitchen`, `bathroom`, `bedroom`, `balcony` (a balcony or a
  patio).
- Ratings: kitchen countertop 2 × 20 A (NEC 210.11(C)(1)), bathroom 20 A
  (210.11(C)(3)), lighting and room outlets 15 A, unit main 100 A (the modern
  minimum). A comment carries these citations.
- Panel-door labels (`KITCHEN 1`, …) are a naming choice. Retunable.
- `KITCHEN 2` has no fixture. It stands for the second countertop circuit,
  whose outlets arrive with cords (#244).
- No laundry circuit (Acorn has no laundry room). No water heater: Acorn's
  is taken to be gas, like its stove. That's unconfirmed, since Acorn isn't
  a real building; say so in the comment.

### 3. `WIRING.acorn`

```
board:  { name:"Main board", room:"hallway1", rating:200,
          feeders:[ { panel:"2A",    label:"2A",    rating:100 },
                    { panel:"2B",    label:"2B",    rating:100 },
                    { panel:"1A",    label:"1A",    rating:100 },
                    { panel:"1B",    label:"1B",    rating:100 },
                    { panel:"house", label:"HOUSE", rating:30 } ] }
panels:
  { id:"2A", name:"Unit 2A panel", room:"kitchen",        template:"apartment",
    rooms:{ living:"living", kitchen:"kitchen", bathroom:"bathroom", bedroom:"bedroom", balcony:"balcony" } }
  { id:"2B", name:"Unit 2B panel", room:"twobee_kitchen", template:"apartment",
    rooms:{ living:"twobee", kitchen:"twobee_kitchen", bathroom:"twobee_bathroom", bedroom:"twobee_bedroom", balcony:"twobee_balcony" } }
  { id:"1A", name:"Unit 1A panel", room:"onea_kitchen",   template:"apartment",
    rooms:{ living:"onea", kitchen:"onea_kitchen", bathroom:"onea_bathroom", bedroom:"onea_bedroom", balcony:"onea_patio" } }
  { id:"1B", name:"Unit 1B panel", room:"onebee",         template:"apartment",
    rooms:{ living:"onebee", kitchen:"onebee", bathroom:"onebee", bedroom:"onebee", balcony:"onebee" } }
common:
  { id:"house", name:"House panel", room:"hallway1",
    layout:{ main:{ rating:30 },
             circuits:[ { key:"house", label:"HOUSE", rating:15, volts:120,
                          roles:["hallway1","hallway2","stairs1","stairs2"] } ],
             fixtures:[ light_hallway1, light_hallway2, light_stairs1, light_stairs2:
                        each { appliance:"led_light", circuit:"house", role:<its room> } ] },
    rooms:{ hallway1:"hallway1", hallway2:"hallway2", stairs1:"stairs1", stairs2:"stairs2" } }
```

- **Where things hang:** the main board and the house panel in the
  ground-floor hallway. Each unit's panel is inside the unit, in its kitchen
  (1B's in its one room). NEC 240.24(B): each occupant has ready access to
  the breakers protecting their unit. Acorn has no basement or utility room,
  and a building doesn't need one for this.
- **Figures:** 240 V single-phase for a small four-unit building
  (`PANEL_DEFAULT_VOLTS`; bigger apartment buildings are often 120/208 V).
  The **200 A board main is unconfirmed:** no source was read for a
  four-unit service. The **30 A house feeder and house main** are a judgment
  call. Mark all three in the comment, retunable. Nothing in play draws
  enough to trip them.
- 1B plays every role in one room, so it carries every template fixture:
  five lights, the hood, the fan, the alarm and the fridge-freezer. That's
  accepted.
- Starting switch states come from the existing roll. Every load, lights and
  alarms included, is found on with `SWITCH_LEFT_ON_CHANCE`. That's #266's to
  refine, not this pass's.

### 4. 1B gets a fridge and freezer

In `onebee`'s containers, straight after `stove`, add the same shape 2B's
kitchen uses:

```
{ id:"fridge",  name:"Fridge",  capacityKg:30, tags:["fridge"],  spawnPools:["kitchen_perishable"], items:[] },
{ id:"freezer", name:"Freezer", capacityKg:10, tags:["freezer"], spawnPools:["kitchen_frozen"],     items:[] },
```

A normal fridge-freezer, not a small one. 1B's description is unchanged.

### 5. 1A's fridge and freezer are renamed

In `onea_kitchen`, `fridge1a` → `fridge` and `freezer1a` → `freezer`, so the
template's `containers:[fridge, freezer]` finds them. Nothing else in the
file names either id. The stove (`stove1a`) and the other `…1a` containers
keep their ids.

### 6. Save repair for the rename (PERSISTENCE)

Without it, a 0.9.0 save loads with `fridge1a`/`freezer1a` still in
`onea_kitchen`. `migrateCookingRelease()` then adds a second, empty `fridge`
and `freezer` beside them: two Fridge tabs, and the old one unwired.

- A repair step in `applyLoadedData()` that runs **before**
  `migrateCookingRelease()`. In the loaded `world.onea_kitchen`, if it has a
  container `fridge1a` and none called `fridge`, change that container's `id`
  to `fridge`; the same for `freezer1a` → `freezer`. The container object is
  kept, so its items and fields stay.
- Idempotent, and it does nothing on a save without those ids. The
  surrounding backfills and migrations follow the same pattern.
- It changes no saved field's shape and adds none. PATCH holds.

A 0.9.0 save also gets 1B's new containers from `migrateCookingRelease()`,
and the new windows and doors from their definitions. Its saved exits lack
the new `doorId`s. That's accepted: door actions still appear through
`sides`, and a closed interior door doesn't block movement.

### 7. Windows

Twelve new windows, one to the outside in each unit's living room, kitchen,
bedroom and bathroom (2A, 2B, 1A):

```
"<unit>-<room>-window": { state:"closed", rooms:[<room id>], breakTag:"blunt", label:"window" }
```

- Ids: `2a-living-window`, `2a-kitchen-window`, `2a-bedroom-window`,
  `2a-bathroom-window`, and the same for `2b-…` and `1a-…`.
- None is climbable. There are none on balconies, the patio, hallways or
  stairs. 1B keeps `1b-alley` and gets no other window. `2a-transom` is
  unchanged.
- Which way each faces isn't modelled (the WINDOW SCHEMA has no field for it).

### 8. Interior doors

Eleven new doors, all `{ locked:false, lockable:false, building:"acorn" }`:

| id | sides |
|---|---|
| `2a-bedroom` | `living`, `bedroom` |
| `2a-bathroom` | `living`, `bathroom` |
| `2a-bath-bedroom` | `bedroom`, `bathroom` |
| `2a-balcony` | `living`, `balcony` |
| `2b-bedroom` | `twobee`, `twobee_bedroom` |
| `2b-bathroom` | `twobee`, `twobee_bathroom` |
| `2b-bath-bedroom` | `twobee_bedroom`, `twobee_bathroom` |
| `2b-balcony` | `twobee`, `twobee_balcony` |
| `1a-bedroom` | `onea`, `onea_bedroom` |
| `1a-bathroom` | `onea`, `onea_bathroom` |
| `1a-bath-bedroom` | `onea_bedroom`, `onea_bathroom` |

- Add the matching `doorId` to **both** exits of each pair in
  `buildAcornApartments()`, e.g. `living`→`bedroom` and `bedroom`→`living`
  both get `doorId:"2a-bedroom"`.
- No door between a living room and its kitchen. The balcony doors are
  unlockable, as a sliding door is. That's a judgment call, retunable.
- The kitchens' and bedrooms' "Leave the apartment" exits keep only the unit
  door's `doorId`.

## Design decisions to make during implementation

Record each in the changelog's Notes/assumptions.

- **The save repair's name and placement** among the load-time backfills, as
  long as it runs before `migrateCookingRelease()`.
- **How the house panel's four light fixtures are written:** four literal
  entries or a mapped list. Both expand to the same ids.
- **Comment wording** for the schema comments this pass makes stale. Rewrite
  them to describe what's true now, with no issue numbers or versions (see
  "Comments carry intent, not history").

## Data / schema changes

- **State fields:** none.
- **Item schema:** none.
- **World data:** four `APPLIANCES` entries; `WIRING_TEMPLATES.apartment`;
  `WIRING.acorn`; two containers in `onebee`; two container ids renamed in
  `onea_kitchen`; twelve windows; eleven doors and their exits' `doorId`s. No
  schema field is added or changed.
- **Persistence:** one idempotent load-time repair (section 6).

## In scope

- [ ] `APPLIANCES`: `led_light`, `bath_fan`, `range_hood`, `smoke_alarm`, with
      sourced comments.
- [ ] `WIRING_TEMPLATES.apartment` as in section 2.
- [ ] `WIRING.acorn` as in section 3.
- [ ] 1B's Fridge and Freezer.
- [ ] 1A's `fridge1a`/`freezer1a` renamed, with the save repair.
- [ ] Twelve windows and eleven interior doors, with `doorId` on both exits of
      each pair.
- [ ] Stale comments updated: above `WIRING_TEMPLATES` ("None yet…"), above
      `WIRING` ("Empty in this release…"), and `POWER_NET`'s ("Empty until a
      building is wired").

## Explicitly out of scope

- **A control for a load's own switch** (#264, 0.9.2, bundled with #259).
  In this version a load found switched off can't be switched on, including
  the player's own fridge in 2A (a one-in-ten chance). Accepted for one
  version.
- **The stove as a load** (#259). 1A's `stove1a` isn't renamed here.
- **Room text following power** (#235). 2A's kitchen text still says the
  fridge hums and the stove needs no power.
- **Per-appliance left-on chances** (#266).
- **Templates carrying windows and doors** (#267). This pass hand-authors
  them.
- **Outlets, cords and plugging** (#244); GFCI/AFCI and shock (#247); a water
  heater; laundry.
- **The electrical view** (#242) and **meters and nameplates** (#249).
- **Other buildings** (#252–#257) and removing the fallback (#258).

## Sections touched

- **WORLD DATA:** `APPLIANCES`, `WIRING_TEMPLATES`, `WIRING`,
  `makeDefaultDoors()`, `makeDefaultWindows()`, `buildAcornApartments()`.
- **PERSISTENCE:** the save repair only.
- Not ACTIONS, SIMULATION or RENDERING. The existing POWER code and device
  tabs already handle everything this data produces.

## UI changes

These all follow from data, through existing rendering.

- Device tabs appear where panels hang: the Main board and the House panel
  in the ground-floor hallway, and each unit's panel in its kitchen (1B's in
  its room). Their Device Options offer the breakers' Switch on / off and
  Reset, as v0.9.0 ships them.
- A fridge in a wired kitchen now keeps food cold only while its circuit is
  live and its switch was found on. After `POWER_FAILS_DAY` everything in
  Acorn is unpowered, as before.
- Open / Close / Break on the new windows; Open / Close on the new interior
  doors (no key actions).
- 1B shows Fridge and Freezer tabs.

## Validation

- `ashfallDev.validateWiring()` reports no problems, and no Acorn room in
  its unwired list.
- Load a 0.9.0 save that has visited 1A's kitchen: one Fridge and one
  Freezer, items intact, and each tied to `acorn.1A.fridge`.
- A new game: 2A's fridge spoils at `FRIDGE_RATE_POWERED` while the grid is
  up (assuming its switch rolled on), and at 1 after `POWER_FAILS_DAY`.
- `git diff origin/main...HEAD -- ashfall.html` touches only the sections
  above.

## Dependencies / issue linkage

- Fulfils #251. Part of #250 and #220.
- Unblocks #259 + #264 (0.9.2), #235, #242 and #249, and makes the
  `apartment` template available to Oak (#252).
- Related: #266 (left-on chances), #267 (templates carry windows and doors).

## Open questions for Tom

None.

## After implementation

Open a pull request carrying the version bump (PATCH) and a new `CHANGELOG.md`
entry per `CHANGELOG_GUIDE.md`, naming this handoff by path and recording the
implementation decisions above. Move this file to `handoffs/archive/` in the
same pull request, and close the issue with `Closes #251`.
