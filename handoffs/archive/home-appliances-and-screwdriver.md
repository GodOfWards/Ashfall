# Ashfall Handoff — Home Appliances and the Household Screwdriver

Current shipped version: v0.12.2
Implied version-change type: PATCH
Issues: #333 — Wire the homes' TV; #384 — Wire the home's washing machine,
and 20 A SOCKETS in the row house and casa; #367 — Rewiring a blown fuse
needs a screwdriver, and the only live pool with one is the repair shop's

## What this is

Three small `tier-0` content passes, bundled because two of them edit the same
lines:

- **#333:** a 43 W TV in the living room of the row house and of every casa.
- **#384:** a 1,800 W washing machine in the row house's laundry. The row
  house's and the casa's SOCKETS circuits go from 16 A to 20 A.
- **#367:** a screwdriver in the household tool and kitchen-drawer pools, so
  a blown old fuse can usually be rewired without a trip to the repair shop.

## Relevant existing state

Verified against `ashfall.html` at v0.12.2.

- **`APPLIANCES`** (POWER SCHEMA). The kettle's entry is the form to copy:
  `kettle: { name:"Electric kettle", watts:2200, volts:220, leftOnChance:0,
  nameplate:{ printsWatts:true }, readout:{ on:"Running", off:"Stopped" } }`.
  The toaster and the microwave share it.
- **The nameplate comment** above `LED_BULB_WATTS` lists each appliance's
  nameplate form. Its line "kettle, toaster, microwave, water_heater  its own
  `watts`…" says the plate's form is unconfirmed (#332).
- **`WIRING_TEMPLATES.row_house`:**
  - SOCKETS is `{ key:"sockets", label:"SOCKETS", rating:16, volts:220,
    roles:["kitchen"] }`;
  - WATER (16 A) already serves `laundry` (the pump);
  - SOCKETS carries the fridge (100 W running), gas range (0 W), kettle
    (2,200 W), toaster (700 W) and microwave (1,150 W), all in the kitchen.
- **`WIRING_TEMPLATES.casa`:** the same SOCKETS line, rating 16,
  `roles:["kitchen"]`, with the same kitchen fixtures.
- **`WIRING_TEMPLATES.casa_fuses`:**
  - built below the table from the casa's fixtures:
    `fixtures: WIRING_TEMPLATES.casa.fixtures.map(fx=> Object.assign({}, fx,
    { circuit:"fuses" }))`;
  - its one circuit, rated `OLD_BOARD_FUSE_A`, serves every casa role;
  - so a fixture added to `casa` reaches it with no edit.
- **`WIRING_TEMPLATES.apartment`:** SOCKETS 16 A. It is not touched.
- **The comment block above `WIRING_TEMPLATES`** says:
  - for `row_house`: "The circuits' 10 A and 16 A are AEA's example's
    lighting and sockets figures (at most 16 A and 20 A); WATER's 16 A is a
    judgment call";
  - for `casa`: "Its figures are the row house's: the 40 A diferencial, the
    circuits' 10 A and 16 A, and the appliances";
  - and it ends the casa paragraph with "No patio light, no TV and no washing
    machine (#333). All retunable."
- **`BUILDING_TYPES.row_house` comment:** "The fixtures its text names but
  the wiring doesn't (the garrafa heater, the washing machine, the grill, the
  clothesline, the septic tank) are words only."
- **Room text, both unchanged:**
  - the row house's laundry: "A washing machine, a deep sink, and the pump
    that fills the house's water tank.";
  - its living room says "The television is dark".
- **Switch state is saved only as a difference from the rolled default**
  (`state.power.switches`, around `ashfall.html:8294-8303`). A load that a
  save has no entry for reads as its rolled default. With `leftOnChance:0`
  that is off, so new fixtures need no save change.
- **Pools:**
  - `tools_general` (shed boxes, the laundry shelf) has no screwdriver;
  - `kitchen_tools` (kitchen drawers, cupboards, stove) has none;
  - the screwdriver is in `tools_workshop` (0.20) and `hardware_store`
    (0.23);
  - `hardware_store` is dead: every container that draws from it has
    hand-placed contents (#133);
  - the screwdriver is the only item tagged `screwdriving`, which
    `doRewireFuse()` needs.
- **The pool comment** above the spawn pools lists every chosen (not derived)
  chance as an exception, each block ending "Retunable."

### Figures (quoted, since the coding session reads no reference)

- **TV:** Noblex DM32X7000, **43 W on**, 0.3 W standby (secondary;
  `Electrical_AR.md`, "Small appliances"). Standby is left out (Tom).
- **Washing machine:** Longvie L8012 (Longvie's "Manual de Instrucciones
  Lavarropas y Lavasecarropas Cleanium", document 13280, November 2014,
  confirmed):
  - "Potencia máxima consumida" **1,800 W**;
  - "Tensión de alimentación" **220 V**;
  - motor 470 W and heater 1,600 W, not modelled separately.
- **AEA 770**, Table 770.6.I (confirmed): a general-socket (TUG) circuit is
  capped at **20 A**.

## Rules / mechanics

### `APPLIANCES`

Add two entries in the kettle's form:

```js
washing_machine: { name:"Washing machine", watts:1800, volts:220, leftOnChance:0, nameplate:{ printsWatts:true },
  readout:{ on:"Running", off:"Stopped" } },
tv:              { name:"TV", watts:43, volts:220, leftOnChance:0, nameplate:{ printsWatts:true },
  readout:{ on:"On", off:"Off" } },
```

- **No `startWatts`, no `dutyCycle`, no standby.** The washing machine draws
  its full 1,800 W the whole time it is switched on; no wash cycle (that is
  #385's).
- **The readout words**, retunable:
  - the washing machine takes the kettle's "Running" / "Stopped";
  - the TV takes "On" / "Off" (Tom).
- **The nameplate comment** adds `washing_machine` and `tv` to the "its own
  `watts`" line.
  - The TV's plate form is unconfirmed, as the kettle's is.
  - The washing machine's watts are the maker's own figure ("Potencia máxima
    consumida"), but how the plate itself prints them is unconfirmed.

### `WIRING_TEMPLATES`

**`row_house`:**
- SOCKETS becomes `rating:20`, `roles:["kitchen", "living", "laundry"]`.
- Fixtures gain:
  ```js
  { key:"tv",              appliance:"tv",              circuit:"sockets", role:"living" },
  { key:"washing_machine", appliance:"washing_machine", circuit:"sockets", role:"laundry" },
  ```

**`casa`:**
- SOCKETS becomes `rating:20`, `roles:["kitchen", "living"]`.
- Fixtures gain:
  ```js
  { key:"tv", appliance:"tv", circuit:"sockets", role:"living" },
  ```
- No washing machine.

**`casa_fuses`:** no edit. It inherits the TV on `fuses`.

**`apartment`:** no edit. It stays 16 A, with no TV.

Fixture order within each list: keep the existing grouping (lights, then
sockets loads, then water). Put the TV after the microwave, and in
`row_house` the washing machine after the TV. A stable order matters because
load ids come from the template and key, not the position. If the order
turns out to feed anything seeded, report it rather than reordering.

### Comments

- **The `row_house` paragraph above `WIRING_TEMPLATES`:**
  - state that SOCKETS is 20 A, AEA 770's cap for a general-socket circuit,
    and that it serves the kitchen, the living room's TV and the laundry's
    washing machine;
  - the 10 A lighting figure stays AEA's example's;
  - WATER's 16 A stays a judgment call;
  - still "All retunable."
- **The `casa` paragraph:**
  - "the circuits' 10 A and 16 A" becomes the lights' 10 A and the sockets'
    20 A;
  - the closing line becomes "No patio light and no washing machine. All
    retunable." (the TV is now wired).
- **`BUILDING_TYPES.row_house`'s comment:** drop "the washing machine" from
  the fixtures that are words only.

### Pools (#367)

- `tools_general` gains
  `{ itemId:"screwdriver", chance:0.20, qtyMin:1, qtyMax:1 }`.
- `kitchen_tools` gains
  `{ itemId:"screwdriver", chance:0.10, qtyMin:1, qtyMax:1 }`.
- **The pool comment** adds both to its list of chosen chances: a
  household screwdriver in the shed or laundry box (0.20) and in the kitchen
  drawer (0.10). Both are judgment calls, not sourced figures. End the
  block with "Retunable."
- No other item gains `screwdriving`.

Adding an entry to a pool changes what that pool rolls for every container
that hasn't rolled yet. That is intended: pools roll from the seed, and
nothing saved changes.

### Expected effects (check these)

**Row house, SOCKETS at 20 A (4,400 W at 220 V):**
- washing machine + kettle + fridge running = 4,100 W: holds;
- adding the toaster (+700 W) or the microwave (+1,150 W) trips it;
- the TV's 43 W changes neither outcome.

**Casa with a modern board:** the kitchen's sockets carry 4,400 W before
tripping, up from 3,520 W.

**Casa with an old board:** the TV is on its `fuses` circuit and draws 43 W
when switched on.

**`ashfallDev.validateReachability()`:** the line for tool tag
`"screwdriving"` lists `tools_general` and `kitchen_tools` among its live
pools, beside `tools_workshop`.

## Design decisions to make during implementation

None of substance. The fixture position within a list is given above. If
anything forces another order, name it in the changelog.

## Data / schema changes

- **PLAYER STATE:** none. No save field, no save key rotation.
- **POWER SCHEMA:**
  - two `APPLIANCES` entries;
  - three fixtures (two in `row_house`, one in `casa`);
  - two SOCKETS ratings and their `roles`.
- **SPAWN POOLS:** two entries.

## In scope

- [ ] `APPLIANCES.washing_machine` and `APPLIANCES.tv`, with the nameplate
      comment updated
- [ ] Row house SOCKETS: 20 A, roles `kitchen`, `living`, `laundry`; the
      `tv` and `washing_machine` fixtures
- [ ] Casa SOCKETS: 20 A, roles `kitchen`, `living`; the `tv` fixture
- [ ] `casa_fuses` confirmed to carry the TV, with no edit
- [ ] The three comments under "Comments" brought up to date
- [ ] `tools_general` and `kitchen_tools` screwdriver entries, and the pool
      comment
- [ ] The expected effects above checked in play or through the dev seam

## Explicitly out of scope

- **Using the appliances** (wash cycles, the kettle boiling water): #385.
- **Appliances switching themselves off:** #334.
- **TV standby draw:** left out by decision.
- **A washing machine in the casa:** decided against.
- **The apartment template:** stays as it is.
- **`hardware_store`'s dead pool, and the other unreachable items:** #133.
- **The water network and the row house's pump:** #300 (blocked by #343).
  Do not touch the WATER circuit or the laundry text.

## Sections touched

- **POWER SCHEMA:** `APPLIANCES`, the nameplate comment, `WIRING_TEMPLATES`
  and its comment.
- **SPAWN POOLS:** `tools_general`, `kitchen_tools`, the pool comment.
- **BUILDING TYPES:** one comment line in `row_house`. No room data or text
  changes.

This is content only. No mechanic, resolver or rendering code changes.

## Systems docs

Read `docs/systems/power.md`. At v0.12.2 it names neither appliances nor
circuit ratings, so it should need no update. If it does name something this
changes, update it in the same pull request.

## UI changes

The Electrical view lists:
- the TV on SOCKETS in the row house and casa;
- the washing machine on SOCKETS in the row house.

Both start switched off, and each reads its own on and off word when
switched.

## Dependencies / issue linkage

- **Closes** #333, #384 and #367.
- **Leaves deferred** nothing new.

## Open questions for Tom

None. This handoff is ready to build from.
