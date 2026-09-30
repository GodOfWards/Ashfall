# Ashfall Handoff — Old fuse boards in Lima's casas

Current shipped version: v0.10.9
Implied version-change type: PATCH
Issue: #358 — Old fuse boards in Lima's casas — tapones that blow, spare fuses, and which homes

## What this is

The next type pass under #250, split from #306. v0.10.8 wired every `casa`
with a modern board. This pass gives **half of them an old fuse board**
instead: a bipolar cut-off switch and two porcelain plug fuses (*tapones*),
one on each pole, on a single circuit. A *tapón* doesn't trip; it **blows**,
and it's put right by **rewiring it with fuse wire** of its own rating, with
a screwdriver. The fuse wire is new, and so is where it's found.

It stays PATCH: a blown fuse reuses a breaker's saved `tripped` state and its
`heat`, the fuse's rating is fixed by the definition, and wiring isn't saved.

## Relevant existing state

Verified against `ashfall.html` at v0.10.9.

**The casa and its board.**
- `generatedHomes()` builds one `casa` on every mid stop except `HOME_STOP`:
  id `h_<stop id>`, `seed:stableHash(s.id)`, and
  `overrides:{ doors:{ front:{ locked: stableHash(id) % 100 < HOME_LOCKED_PCT } } }`
  (`HOME_LOCKED_PCT = 60`).
- **Every stop carries a `type`** (`LIMA_STOPS`: core, gravel, dirt,
  **barrio**, rural, rail, station), read into `LIMA.stops` as `s.type`. There
  are 22 barrio mid stops, one of them `HOME_STOP`, so 21 barrio casas.
- `BUILDING_TYPES.casa.wiring` is
  `{ board:{ name:"Meter box", role:"street", rating:32, direct:true },
  panels:[ { id:"house", name:"Breaker panel", role:"living", template:"casa" } ] }`.
- `WIRING_TEMPLATES.casa`: `main:{ rating:40, rcd:true }`; circuits LIGHTS
  10 A (living, kitchen, bedroom, bathroom), SOCKETS 16 A (kitchen) and WATER
  16 A (kitchen, patio); fixtures `light_living`, `light_kitchen`,
  `light_bedroom`, `light_bath` (led_light, 10 W), `fridge` (fridge_freezer,
  100 W, 1,300 W start), `stove` (gas_range, 0 W), `kettle` (2,200 W),
  `toaster` (700 W), `microwave` (1,150 W), `water_heater` (2,000 W),
  `pump` (house_pump, 370 W, 3,300 W start).
- The casa's living room text: "A front room that is living room and dining
  room both. Barred windows onto the street, the blinds half down. The
  breaker panel hangs on the wall by the front door." Its kitchen containers
  are `KITCHEN_CONTAINERS`, whose `drawers` roll `spawnPools:["kitchen_tools"]`.
- **An instance's `overrides`** take `rooms:{ role:{ …fields } }` (a field
  replaces the type's, so `desc` or `containers` can be swapped per
  instance), `addRooms`, `links` and `doors`. **Not `wiring`:**
  `buildBuilding()` passes `type.wiring` to `buildWiring()` as it is.

**The network (SIMULATION → POWER).**
- `expandWiring()` makes a panel's head device from the template's `main`:
  with `rcd:true` it is `{ layer:"panel", label:"RCD", curve:null, rcd:true }`,
  otherwise `{ label:"MAIN", curve:breakerCurve(main) }`. A circuit is
  `{ layer:"circuit", label, rating, curve, volts, roles }`. Ids:
  `h_x.house.main`, `h_x.house.<circuit key>`, `h_x.house.<fixture key>`.
- `state.power` is `{ switches, breakers:{ id:{ on, tripped } }, heat:{ id } }`.
  `setBreakerIn()` deletes a closed, untripped entry; `resetBreakerIn()`
  sets on and untripped; `setHeatIn()` deletes a zero.
- `resolvePowerStep()` checks, per consulted layer, lowest first:
  - **instant:** a momentary current above `BREAKER_CURVES[curve].instant` ×
    rating;
  - **heat:** at f = running current ÷ rating, heat rises by
    `dt / tripMinutes(rating, f)` while f > 1, and drains by
    `dt / HEAT_COOL_MIN` otherwise; it trips at 1.

  An `rcd` breaker is skipped by both checks. `tripMinutes()` runs through
  `(BREAKER_F_LOW 1.45, 60 min)` and `(BREAKER_F_HIGH 2.55, 1 min up to
  32 A)`.
- `consultedLayers("simplified")` is `["panel", "board"]`. Under simplified
  rules a load is powered when its **panel** is live: circuits are skipped
  both for trips and for liveness (`powerSnapshot()`).
- `validateWiring()` requires every breaker's rating to be in
  `STANDARD_BREAKER_RATINGS` (6, 8, 10, 13, 16, 20, 25, 32 …; **no 15**).
  For every breaker but an RCD it also requires a curve in `BREAKER_CURVES`,
  and `tripMinutes(rating, 1.13) ≥ 60`.
- `logTrips()` logs "The panel on the wall snaps. A breaker has tripped."
  when a tripped breaker's room is the current room, and else
  `ROOM_GOES_QUIET` where a load it fed was running.

**The device pop-up (RENDERING).**
- **Detailed rules** (`renderPowerDevicePop()`): the name, then
  `deviceFedText()`, then one row per breaker: `${label} · ${rating} A ·
  ${breakerStateText(id)}` ("Tripped" / "On" / "Off"), with Reset, Switch
  off or Switch on.
- **Simplified rules:** `Rating: <main> A`, On/Off, and one button.
- `deviceStripText()`: detailed, `"Main on"` or `"RCD on"`, plus
  `" · N tripped"`; simplified, "On" or "Off".
- `doResetBreaker()` and `doSwitchBreaker()` are the only breaker controls.

**Items.**
- The screwdriver's tags are `["can-opening"]`. `hasTool(tag)` checks what
  the player carries.
- `consumeByTag(tag, qty)` and `consumeFromPools(itemId, qty)` spend carried
  items.
- `SPAWN_POOLS` entries are `{ itemId, chance, qtyMin, qtyMax }` under an
  `emptyChance`. Each pool on a container rolls independently.
  `hardware_store` has `emptyChance:0.1`.

**Reference figures this pass depends on** (from
`docs/canon/reference/Electrical_AR.md`, "Old installations"; quoted, since
a coding session doesn't read it):
- **An old board: two fuses, one on each pole, behind a manual bipolar
  switch.** Rosario, Ordenanza 3419/83 §2.8: circuits protected by
  "interruptor manual y fusibles (en ese orden), en todos los conductores".
  That is primary for Rosario; the single circuit in a Lima home is Tom's
  account.
- **15 A**: a dwelling's general-use circuit, lights and sockets together,
  is protected at "no greater than 15 A" (Rosario 3419/83 §2.8.1.a). Lima's
  own rating is unconfirmed.
- **Edison-thread fuses only up to 30 A** (Rosario 3419/83 §8.2.7).
- **How a gG fuse blows** (IEC 60269, via Mersen's EduPack TM-104; secondary
  for the standard): it must not blow at **1.25 × In**, and must blow at
  **1.6 × In** within a conventional time of 1–4 h. A **25 A** fuse blows in
  at most 5 s at **110 A** (**4.4 × In**). A fuse has no separate instant
  band. A rewired *tapón*'s fuse wire is not a gG cartridge, so these figures
  are a stand-in, marked unconfirmed.
- **A *tapón* is rewired with calibrated fuse wire**, sold by the metre at
  hardware shops. Secondary, from search summaries only.

## Rules / mechanics

### Which casas have an old board

- A generated casa has an old board when its **site stop's type isn't
  `barrio`** and a stable roll of its building id is under `OLD_BOARD_PCT`:
  `stableHash(<id-derived key>) % 100 < OLD_BOARD_PCT`.
- **The key must not be the bare building id.** `stableHash(id)` already
  decides the locked door, against `HOME_LOCKED_PCT = 60`. Reusing it would
  make every old-board house a locked one. Use a key derived from the id
  (e.g. the id joined with `"board"` by `KEY_SEP`) so the two rolls are
  independent.
- `OLD_BOARD_PCT = 50`. The same homes have old boards in every run, since
  the roll never reads `state.seed`. Retunable: Tom's "at least half".
- The player's home (a row house) and every other building type are
  untouched. So is every barrio casa.

### The old board

A new template, `WIRING_TEMPLATES.casa_fuses`, sits beside `casa`:

- **Head device: a bipolar cut-off switch.** A new template-main flag,
  `cutoff: true`:
  - it is labelled "Cut-off switch", with **no rating and no curve**;
  - it is switched by hand like a breaker;
  - it **never trips**: neither the instant nor the heat check touches it,
    under either rules, as the RCD is skipped today;
  - it is not an RCD, and `rcd` and `cutoff` never both appear on one main.
- **One circuit: the fuse pair.** Key `fuses`, label "Fuses", rating
  `OLD_BOARD_FUSE_A`, 220 V, `fuse: true`, serving every role the casa has
  (living, kitchen, bedroom, bathroom, patio).
  - The two *tapones* are **one device** in the model. When it blows, one
    *tapón*'s wire has burnt, and **one length of fuse wire** mends it.
    Nothing records which pole.
- **The fixtures are the casa's, with the same keys**, every one on
  `fuses`. The load ids (`h_x.house.fridge` and the rest) are then the same
  as a modern casa's, so a save's switch positions carry over.
  - Derive the list from `WIRING_TEMPLATES.casa`'s fixtures rather than
    repeating it (one source of truth).
- **The meter box at the street is unchanged:** 32 A, direct.
- **The panel's device name is "Fuse box"**, where a modern casa's is
  "Breaker panel".

### How a fuse blows

A breaker entry with `fuse: true` follows these rules, under **both** rules
modes:

- **No instant trip.** The instant check skips it.
- **Heat, the same meter as a breaker's, on the fuse's own curve:**
  - it rises by `dt / fuseBlowMinutes(f)` while f > 1, and drains by
    `dt / HEAT_COOL_MIN` otherwise;
  - at 1 it **blows**, which is the saved `tripped: true`;
  - `fuseBlowMinutes(f)` is `tripMinutes()`'s formula through the fuse's
    two anchors, `(FUSE_F_LOW, FUSE_T_LOW_MIN)` and
    `(FUSE_F_HIGH, FUSE_T_HIGH_MIN)`:

  | Constant | Value | Source |
  |---|---|---|
  | `FUSE_F_NO_BLOW` | 1.25 | gG: must not blow |
  | `FUSE_NO_BLOW_MIN` | 60 | the low end of gG's 1–4 h conventional time |
  | `FUSE_F_LOW` | 1.6 | gG: must blow |
  | `FUSE_T_LOW_MIN` | 60 | as above |
  | `FUSE_F_HIGH` | `110 / 25` (4.4) | 25 A gG: at most 5 s at 110 A; written as the derivation |
  | `FUSE_T_HIGH_MIN` | `5 / 60` | 5 s |

  These are the gG anchors, standing in for fuse wire: unconfirmed, and
  retunable.
- **Simplified rules consult fuses too.** A `fuse` breaker is checked for
  heat under simplified rules, and a load behind a blown fuse is **not
  powered** under simplified rules either. A panel whose circuits hold a
  fuse is live past it only while it's intact. Every other circuit breaker
  stays skipped under simplified rules, exactly as today.
- For reference, at 15 A with the casa's loads: everything on at once is
  about 29.6 A (1.98 ×) and blows in about 9 minutes. The heater, fridge and
  pump alone draw about 11 A and never blow. Kettle, heater, fridge and pump
  draw about 21 A (1.42 ×) and blow in about 4 hours. The pump's start
  surge is ignored, since a fuse has no instant trip.

### Rewiring a blown fuse

- **Offered only when all of these hold:**
  - the fuse has blown;
  - the player carries an item tagged `screwdriving`;
  - the player carries fuse wire whose `fuseRating` equals the fuse's rating.

  Otherwise the row shows "Blown" with no button. A fuse is never offered
  Reset, Switch on or Switch off, and `doResetBreaker()` and
  `doSwitchBreaker()` refuse a fuse id.
- **Doing it** (`doRewireFuse(id)`, ACTIONS):
  - spend **one** length of matching fuse wire;
  - advance time by `REWIRE_FUSE_MIN` (5, retunable);
  - set the fuse unblown (`resetBreakerIn()`) and **clear its heat to 0**,
    because new wire starts cold. A breaker's reset keeps its heat, so this
    difference is deliberate;
  - log the rewiring line, then render.
- An overload that's still there blows the new wire again on the fuse's own
  curve.
- **The cut-off switch doesn't matter to it.** Rewiring with it closed is
  live work, and its consequence is #247's. It is neither required nor
  checked here.

### Fuse wire

- New registry item `fuse_wire`:
  - name `"Fuse wire (" + OLD_BOARD_FUSE_A + " A)"`, so "Fuse wire (15 A)";
  - category `"Materials"`, tags `["fuse-wire"]`;
  - `fuseRating: OLD_BOARD_FUSE_A`;
  - one unit is one length, and units stack. `unitWeight` 0.01, a judgment
    call.

  Mechanics read the tag and `fuseRating`, never the name.
- The **screwdriver** gains the tag `screwdriving`, keeping `can-opening`.
- **Where it's found:**
  - A new pool, `old_board_spares: { emptyChance:0, entries:[ { itemId:"fuse_wire", chance:0.40, qtyMin:2, qtyMax:4 } ] }`.
    It is added to the **kitchen `drawers`' `spawnPools` of old-board casas
    only**, after `kitchen_tools`, through that instance's
    `rooms.kitchen.containers` override (`KITCHEN_CONTAINERS` with the
    drawers' pools extended; the other containers unchanged).
  - `hardware_store` gains `{ itemId:"fuse_wire", chance:0.25, qtyMin:1, qtyMax:3 }`.
  - All chances and quantities are retunable. The hardware store's quantity
    is a judgment call: the approved figure was its chance.

### Validation

`validateWiring()`:

- **a fuse:** requires `0 < rating ≤ EDISON_FUSE_MAX_A` (30), not
  `STANDARD_BREAKER_RATINGS` membership. Requires
  `fuseBlowMinutes(FUSE_F_NO_BLOW) ≥ FUSE_NO_BLOW_MIN`. Has no curve check.
- **a cut-off switch:** no rating or curve check.
- **Reported:** a main with both `rcd` and `cutoff`, and `fuse` anywhere but
  a template circuit.

The coding session also reports the number of old-board casas in its
changelog. Expect about half of Lima's non-barrio generated casas.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **How an old-board casa gets its wiring and text.** Options:
   - **(a)** a new instance `overrides.wiring`, e.g.
     `{ panels:{ house:{ name:"Fuse box", template:"casa_fuses" } } }`,
     merged by panel id in `buildBuilding()` before `buildWiring()`, and
     documented in BUILDING TYPES' instance schema;
   - **(b)** a second type, `casa_old`, built from `casa` by spreading its
     definition with the wiring swapped.

   **Recommended: (a).** A second type risks two copies of the casa's rooms.
   Either way:
   - the room, door and window ids stay `<id>_<role>` and the rest, which
     both options preserve, since they come from the instance id;
   - the living-room text and the drawers' pools are `overrides.rooms`.
2. **How fuses enter the resolver**: a `fuse` flag on the breaker entry read
   by the instant and heat checks and by `consultedLayers()` / liveness, or
   a separate layer. Either is fine if the rules above hold. Recommended: the
   flag, which leaves `BREAKER_LAYERS` alone.
3. **Where `fuseBlowMinutes()` lives**: `tripMinutes()` generalised to take
   its anchors, or a sibling. Recommended: generalise, so the formula exists
   once.
4. **Which spend helper**: today only one fuse wire exists, so
   `consumeFromPools("fuse_wire", 1)` works. Recommended: a rating-aware
   spend (tag `fuse-wire` and a matching `fuseRating`), so a second rating
   later needs no change.

## Data / schema changes

- **No new state fields.** `SAVE_KEY` doesn't change.
- **CONFIG / CONSTANTS** (beside the breaker constants):
  - `OLD_BOARD_PCT` (50);
  - `OLD_BOARD_FUSE_A` (15);
  - `EDISON_FUSE_MAX_A` (30);
  - `FUSE_F_NO_BLOW`, `FUSE_NO_BLOW_MIN`, `FUSE_F_LOW`, `FUSE_T_LOW_MIN`,
    `FUSE_F_HIGH`, `FUSE_T_HIGH_MIN` (the table above);
  - `REWIRE_FUSE_MIN` (5).

  Each gets its source in a comment, marked retunable, and unconfirmed where
  it is.
- **POWER SCHEMA / WIRING_TEMPLATES comment:** a main's `cutoff`; a
  circuit's `fuse`; the `casa_fuses` template's paragraph (the Rosario
  figures, and the single circuit as Tom's account).
- **expandWiring's breaker entry:** `cutoff?`, `fuse?`, documented beside
  `rcd?`.
- **ITEM_REGISTRY:** `fuse_wire`; the screwdriver's new tag. Item schema: the
  `fuseRating` field, documented where item fields are.
- **SPAWN_POOLS:** `old_board_spares`, and the `hardware_store` entry.
- **BUILDING TYPES:** the casa's comment names both boards. If option 1(a)
  is chosen, the instance schema gains `overrides.wiring`.
- **Old saves:** a casa that becomes old keeps its load and head ids, so its
  switch positions carry over, and a head switched off stays off.
  `h_x.house.lights`, `.sockets` and `.water` entries in its saved state
  become inert. The resolver never reads an id the network lacks, so they're
  harmless. No migration.

## In scope

- Which casas get old boards: `OLD_BOARD_PCT`, barrio exempt, an independent
  roll.
- `casa_fuses`: the cut-off switch, the fuse pair as one device, the casa's
  fixtures.
- Fuses in the resolver: no instant trip, the gG heat curve, consulted and
  counted under both rules.
- The Rewire action, its requirements, and clearing the fuse's heat.
- Fuse wire: the item, the screwdriver's tag, its two placements.
- The text below, the pop-up rows under both rules, and the strip.
- `validateWiring()` for fuses and cut-off switches.

## Explicitly out of scope

- **Earthing on old boards, and any shock from rewiring live:** #247. Record
  nothing about earthing here.
- **Over-fusing** (a copper strand, or a wrong-rated wire): #365.
- **Unscrewing a *tapón* to cut a circuit**, or taking one out. The fuse
  row's only action is Rewire.
- **The two *tapones* as separate devices**, and which pole blew.
- **Other building types' boards:** `shop_home` (#307), `galpon` (#308), the
  police station (#309), `chalet`/PH (#299). The fallback's removal (#258).
- **Appliances switching themselves off** (#334); the TV and washing
  machine (#333).
- **Old installations elsewhere:** meters on façades, round two-pin sockets.
- **Fuse wire in any other pool or container.**

## Sections touched

- **CONFIG / CONSTANTS:** the new constants.
- **WORLD DATA:**
  - ITEM_REGISTRY, SPAWN_POOLS;
  - BUILDING TYPES (`generatedHomes()`, the casa's comment; the instance
    schema if option 1(a));
  - WIRING_TEMPLATES (`casa_fuses`), POWER SCHEMA comments.

  This is the definition data the mechanic reads. The placements (which
  homes, the drawers' pool, the store entry) ride along by Tom's decision:
  #358 is a type pass, and without them a blown old house stays dark.
- **SIMULATION → POWER:** `expandWiring()`, `resolvePowerStep()`,
  `powerSnapshot()` liveness under simplified rules, `consultedLayers()` or
  its equivalent, `tripMinutes()` / `fuseBlowMinutes()`, `logTrips()`,
  `validateWiring()`.
- **ACTIONS (WORLD INTERACTION):** `doRewireFuse()`; the fuse guard in
  `doResetBreaker()` and `doSwitchBreaker()`.
- **UI / RENDERING:** `renderPowerDevicePop()`, `breakerStateText()`,
  `deviceStripText()`. BUILDING TYPES (`buildBuilding()`) too, if option 1(a).

## UI changes

The game text below is approved (Tom, 2026-09-30).

| Where | Text |
|---|---|
| Living room of an old-board casa (`desc` override) | "A front room that is living room and dining room both. Barred windows onto the street, the blinds half down. A small fuse box hangs by the front door, two porcelain plugs screwed into it." |
| The panel's device name | "Fuse box" |
| Cut-off switch row, both rules | "Cut-off switch · On" / "Off", with Switch off / Switch on. No rating shown. |
| Fuse row, both rules | "Fuses · 15 A · Intact" / "Blown" (the rating from `OLD_BOARD_FUSE_A`), with **Rewire** when blown and its requirements hold |
| Log, when a fuse blows, in the fuse box's room | "Something pops in the fuse box." (`warn`), in place of the panel line; elsewhere `ROOM_GOES_QUIET` where a load it fed was running, as today |
| Log, rewiring | "You unscrew the blown plug, wind a length of fuse wire under its screws and screw it back in." |
| Item | "Fuse wire (15 A)" |

- **Simplified rules, for an old board:** the pop-up shows the cut-off
  switch row and the fuse row as above, in place of the `Rating:` line, the
  On/Off line and the single button. A modern board's simplified pop-up is
  unchanged.
- **The Here strip** (functional UI, retunable):
  - detailed rules: "Switch on" / "Switch off", plus " · fuses blown" while
    blown;
  - simplified rules: "Off" when the switch is off, "Blown" when the fuses
    are blown, else "On".

  If the coding session words these differently for clarity, it names the
  change in the changelog.
- Meters in the electrical view work on the fuse and the switch as on any
  breaker (`meterButtons()`). Nothing new.

## Dependencies / issue linkage

- Fulfils **#358**. Part of **#250**; hub **#220**.
- Leaves for later: **#365** (over-fusing), **#247** (earthing and live
  rewiring; both noted there, 2026-09-30).
- If something else is deferred during implementation, the coding session
  files it at the wrap.

## Open questions for Tom

None. Every design question was settled in planning (2026-09-30, recorded
on #358).

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` PATCH bump and a new
`CHANGELOG.md` entry per `CHANGELOG_GUIDE.md`. It references this handoff
by path (`Implements: handoffs/old-fuse-boards.md`), records the design
decisions above and the old-board count, and closes the issue with
`Closes #358`. Move this file to `handoffs/archive/` in the same pull
request.
