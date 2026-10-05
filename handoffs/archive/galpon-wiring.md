# Ashfall Handoff — Wire the `galpon` type, with instance wiring overrides

Current shipped version: v0.14.0
Implied version-change type: PATCH
Issue: #308 — Wire the `galpon` type — the yard, the repair shop, the goods
shed and the paper mill; and #483 — Instance wiring overrides — a board of the
building's own, or no supply at all

## What this is

The `galpon` type's pass under #250: its four instances get their wiring and
come off the unwired-room fallback (#258). Two of them need what an instance
can't yet express, so #483's engine change ships in the same pass and pull
request (Tom, 2026-10-05): the paper mill gets **a board of its own**, and the
goods shed gets **no supply at all**. A building's floor lamps are **one load
switched as a bank**, built as a fixture `count` (Tom, 2026-10-05). Wiring is
a definition and isn't saved, so this is a PATCH (#308: "world data only, no
new persistent state").

## Relevant existing state

Verified against `ashfall.html` at v0.14.0 (`GAME_CONFIG.VERSION` "0.14.0").

**Buildings (WORLD DATA, BUILDING TYPES).**
- `BUILDING_TYPES.galpon`: `label:"building"`, `entry:"floor"`. Rooms:
  `floor` (`room:null`, so it carries the building's name; `shelter:"full"`,
  `cannotHaveFire`, `floorCap:70`) and `office` (`room:"Office"`,
  `shelter:"full"`, `cannotHaveFire`, `floorCap:40`). One link floor↔office
  ("Go to the office" / "Leave the office", 5 m, door `office`). Doors
  `front` (street→floor, latch, unlocked) and `office` (unlockable). No
  windows, no `water`, no `wiring`.
- Its four instances, in `buildingInstances()`:
  - `corralon`, "Building-materials yard", site `m_cbar_dg2_c107`. Floor
    desc: "A yard of stacked bricks, bags of cement and lengths of pipe,
    under a corrugated roof at the back." `searchLabel:"Search the yard"`,
    `searchMinutes:20`. Containers `toolwall`, `bins`, `paintaisle`, with
    placed items. Office: "A cramped office with an order book open on the
    desk.", container `shelf`.
  - `mechanic`, "Repair shop", site `x_c16_c7`. Floor: "A workshop with a pit
    in the floor and an alignment rig. Oil stains, a car up on stands.",
    `workbench`, `partsshelf`. Office with a `dispenser_jug`, `desk`,
    `filingcabinet`.
  - `goods_shed`, "Goods shed", site `estacion_lima`. Floor: "The railway's
    goods shed. Brick walls, a high roof, a loading door onto the tracks."
    Crates `unit1`, `unit2` (padlocked, `breakTag:"cutting"`) and `unit3`,
    with placed items. Office: "A cubicle by the door where someone checked
    the freight in and out."
  - `paper_mill`, "Paper mill", site `r111_papermill`, `at:[-642, 5725]`.
    Floor: "A hall of rollers and vats, gone quiet. The smell of pulp hangs
    in the air.", `palletrack1`, `palletrack2`. Office: "The shift office. A
    clipboard still hangs by the door.", a `dispenser_jug`, `desk`, `safe`.
- The instance schema comment above `buildingInstances()` documents
  `overrides { rooms, addRooms, links, doors, wiring?:{ panels:{ id:{ …fields
  } } } }`. The one user of `overrides.wiring` today is
  `oldBoardOverrides()`: `wiring:{ panels:{ house:{ name:"Fuse box",
  template:"casa_fuses" } } }`.
- The type schema comment's `wiring` entry ends "Absent: nothing in the
  building is wired, and its rooms fall back to the grid
  (containerPowered())".
- `buildBuilding()`: rooms from `type.rooms` merged with `ov.rooms`, plus
  `ov.addRooms`; links from `type.links` plus `ov.links`. At the end:
  `mergeWiring(type.wiring, ov.wiring, inst.id, problems)`, then
  `withoutPumps()` for a network building, then `buildWiring()`.
- `mergeWiring(w, ov, instId, problems)`: `if(!ov) return w;` (so a `null`
  override keeps the type's wiring today), reports an override on a type
  with no wiring, reports a panel id the type lacks, and lays each panel's
  fields over the type's. **It never touches `board`.**
- `buildWiring()` turns the board's and each panel's `role` into a room id.
- `expandBuildings()` puts each instance's built wiring in `out.wiring` only
  when `b.wiring` is truthy. `GAME_WIRING = Object.assign({}, WIRING,
  expandBuildings().wiring)`; `WIRING` is `{}`.
- `BUILDING_INFO`: per building `{ name, site, entry, tankL, tankFill }`,
  derived from `buildingInstances()`, never saved.
- Every room a type builds carries `buildingId` (the instance id).

**Power (WORLD DATA, POWER SCHEMA; SIMULATION, POWER).**
- `STANDARD_BREAKER_RATINGS` is `[6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 63,
  80, 100, 125]`.
- WIRING's board schema: `{ name, room, rating, volts?, curve?, direct?,
  feeders:[{ panel, label, rating, curve? }] }`. A `direct` board holds only
  its main and carries no `feeders`.
- `expandWiring()`: per building `b`, the board `b.board` (main
  `b.board.main`); per panel `P`, a feeder `b.board.P` (layer `feeder`) only
  when the board isn't `direct`, the panel `b.P`, circuits `b.P.<key>`,
  loads `b.P.<fixture key>`, and a plug load `b.P.plug.<role>` per room a
  `sockets` circuit serves. It reports a direct board that lists feeders
  ("a direct board has no feeders, but it lists N") and a non-direct board
  with no feeder for a panel. A panel's layout is
  `pd.layout || templates[pd.template]`: an inline `layout` wins over
  `template`. `withoutPumps()` reads it the same way.
- **No building in play has a feeder today.** Every wired type uses a
  `direct` board. The paper mill is the first non-direct board a player
  can reach; the feeder code (supply, the board's pop-up listing feeders,
  simplified rules skipping them) has run only from the dev seam.
- The per-breaker sums in `powerSnapshot()`: for each drawing load, `n =
  l.plug ? plugs[id] : 1`; `run += loadDrawWatts(a) * n`; `mom +=
  (starting[id] ? a.startWatts : loadDrawWatts(a)) * n`.
- `untouchedTrippers()` sums each breaker's loads from their starting state:
  `run += loadDrawWatts(a)`; `mom += a.startWatts !== undefined ?
  Math.max(loadDrawWatts(a), a.startWatts) : loadDrawWatts(a)`, with no
  multiplier.
- `loadDrawWatts(a)` takes an appliance only.
- `switchOnIn()` rolls a load's starting switch on `leftOnChance`, keyed by
  load id; `setSwitchIn()` saves only what differs.
- Where a load is named by its appliance: `doSwitchLoad()`'s log line
  (`` `You switch the ${a.name.toLowerCase()} ${on ? "on" : "off"}.` ``),
  `renderCircuitTab()`'s row (`name.textContent = a.name`), and its
  "Elsewhere on this circuit" rows (`APPLIANCES[l.appliance].name`).
- `nameplateText(a)`: `printsWatts` → `` `Nameplate: ${a.watts} W` ``.
- `validateWiring()` checks every appliance (exactly one of `leftOnChance`
  and `switchless`, a worded readout, a nameplate no lower than its watts,
  one nameplate form), and returns `{ problems, unwired }`, where `unwired`
  is every `shelter:"full"` room no network names (a `console.warn` until
  #258).
- `APPLIANCES.led_light`: `{ name:"Light", watts:LED_BULB_WATTS, volts:220,
  leftOnChance:0.3, nameplate:{ printsWatts:true }, readout:{ on:"Lit",
  off:"Dark" } }`; `LED_BULB_WATTS` is 10.
- `WIRING_TEMPLATES.row_house.main` is `{ rating:40, rcd:true }`; its LIGHTS
  is 10 A and its SOCKETS 20 A, `sockets:true`. `casa_fuses` is built from
  another template below the table, which is the precedent for deriving
  templates from a shared base.

**The grid fallback, the three places a building with no wiring falls back
to the grid:**
- `containerPowered(roomId, container)`: `loadId ? isPowered(loadId) :
  gridUp()`.
- `effectiveAge(container, roomId, fromM, toM)`: `wasOn` is the load's
  starting switch, or `true` for a container no load claims, so an unwired
  container ages at its powered rate while the grid was up.
- `tankRefillLph(b, m)`: a well building with no pump load (`TANK_PUMPS`)
  refills at `HOUSE_PUMP_FLOW_LPH` while `gridUp(m)`. A network building
  fills from `mainsWaterUp(m)` at `NETWORK_FILL_LPH`, which needs no power.

Plug loads don't fall back (`plugFor()` finds no plug in a room no socket
circuit serves), and lights exist only as wired loads.

**Saves.** A room's saved state is only what differs from a freshly built
world (`savedRoomState()`), so a new room comes from its definition on load.

**Reference figures**, quoted for the why-comments (from
`docs/canon/reference/Electrical_AR.md`, "Lighting a galpón (#484)", and "A
shop and its home on one lot"; and `Lima.md`):
- LED high-bays (*campanas*): Lumenac Saturno, maker's sheet, August 2024
  (primary). The Saturno 100: 100 W, 12,000 lm; the Saturno 200: 200 W,
  24,000 lm. Power factor 0.9, 100–277 V, IP65. The sheet gives no inrush
  figure, and no surge worth modelling was found for LED.
- Fluorescent battens: a 36 W T8 on a 50 Hz magnetic ballast draws 43–45 W
  with the ballast, derived from EU Regulation 245/2009's ballast
  efficiencies, 83.4 % (B1) and 79.5 % (B2), as restated by Vossloh-Schwabe
  (secondary). So a 2 × 36 W batten is about 90 W. No surge worth modelling
  was found for fluorescent.
- Light levels (Decreto 351/79, Anexo IV, Tabla 2, primary): a paper mill's
  machine hall 100 lux; a materials store 100 lux.
- Fittings per area (the lumen method, utilisation × maintenance taken as
  0.5; derived, unconfirmed): a 200 W LED covers 120 m² at 100 lux, and a
  100 W LED 60 m².
- A non-residential supply under 10 kW is T1G (OCEBA Subanexo A §4.2), and
  Acometidas T1 caps its main at 32 A, with the meter on the property line.
  The panel's head device and circuits are borrowed from the house's (AEA
  770).
- The goods shed is the `building=warehouse` north-west of Lima station (OSM
  way 794595573), about 26 × 13 m. In March 2025 imagery it has a rust-red
  pitched roof with its ridge along the track, grass up to the walls, and no
  worn path or vehicles. No lessee, use or supply was found. Its wall
  material is unconfirmed.
- The paper mill: CEZ's 33 kV feeders include "332 Celulosa", from the ET
  Zárate (read from the name only).

## Rules / mechanics

### 1. A board override: `overrides.wiring.board` (#483)

- `mergeWiring()` lays `ov.board`'s fields over the type's `board`, field by
  field, as a panel's are. `feeders`, when given, replaces the type's list
  whole.
- A board that isn't direct says `direct:false`. If an override forgets it,
  `expandWiring()` already reports the direct board that lists feeders, so
  nothing new is needed for that.
- A board override on a type with no wiring is reported in `problems`, as a
  panel override is today (the existing "a wiring override, but its type has
  no wiring" covers it).

### 2. No supply: `overrides.wiring: null` (#483)

- `mergeWiring()` checks `ov === null` explicitly, **before** `if(!ov)
  return w`, and returns no wiring. The instance is built with no network.
  A `null` on a type with no wiring is valid and isn't reported.
- A derived, never-saved flag marks the building deliberately unsupplied,
  set at world build from the instance's `overrides.wiring === null`. The
  recommended home is `BUILDING_INFO[b].supplied === false` (true, or
  absent, for everything else); see the design decisions below.
- For a room whose building is unsupplied (found through the room's
  `buildingId`):
  - `containerPowered()` returns `false`; the grid fallback doesn't apply.
  - `effectiveAge()` counts its containers as unpowered throughout
    (`wasOn` is `false`).
  - `tankRefillLph()`: a **well** tank in an unsupplied building never
    refills (returns 0; the fallback doesn't apply). A **network** tank still
    fills through its float valve while the mains run, unchanged. `galpon`
    has no tank; this is for completeness.
  - `validateWiring()` leaves its rooms out of `unwired`.
- `buildBuilding()` reports an unsupplied instance whose type's panels carry
  template doors or windows (a layout's `doors` or `windows`, which
  `expandOpenings()` would place), since dropping the wiring would drop them
  silently. `galpon`'s carry none.
- When #258 deletes the fallback, the flag's only reader left is the check.
  Say so in its comment.

### 3. A fixture `count` (#308, Tom, 2026-10-05)

- A WIRING_TEMPLATES fixture (and an inline layout's) may carry `count`, a
  whole number ≥ 1, default 1. `expandWiring()` copies it onto the load
  (`net.loads[id].count`), absent when 1 or left as 1; the coding session
  picks, consistently.
- The load draws the appliance's watts × `count`, and, for an appliance with
  `startWatts`, its start × `count`, **everywhere the engine sums a load**:
  - `powerSnapshot()`'s per-breaker sums: `n` becomes `l.plug ? plugs[id] :
    (l.count || 1)`.
  - `untouchedTrippers()`'s sums: both `run` and `mom` multiplied by the
    load's count.
  - Any other reader of a load's watts the coding session finds.
- One load, one switch, one starting roll on `leftOnChance`, as any fixture.
- The nameplate stays the appliance's: one fitting's.
- A load whose `count` > 1 is named by its appliance's **`plural`**, a new
  optional `APPLIANCES` field, wherever a load is named: the `doSwitchLoad()`
  log line ("You switch the high-bay lamps on."), `renderCircuitTab()`'s row,
  and its "Elsewhere on this circuit" rows. One helper names a load
  (`loadName(l)` or similar), so the three read alike. Functional UI text,
  retunable.
- `validateWiring()` reports a fixture `count` that isn't a whole number
  ≥ 1, and a `count` > 1 whose appliance has no `plural`. It also reports a
  `plural` that isn't a non-empty string.

### 4. Three new appliances

Each uses fields the table already has, plus `plural`:

| id | `name` | `plural` | `watts` | `volts` | `leftOnChance` | `nameplate` | `readout` |
|---|---|---|---|---|---|---|---|
| `led_highbay_200` | "High-bay lamp" | "High-bay lamps" | 200 | 220 | 0.3 | `{ printsWatts:true }` | `{ on:"Lit", off:"Dark" }` |
| `led_highbay_100` | "High-bay lamp" | "High-bay lamps" | 100 | 220 | 0.3 | `{ printsWatts:true }` | `{ on:"Lit", off:"Dark" }` |
| `fluorescent_batten` | "Fluorescent light" | "Fluorescent lights" | 90 | 220 | 0.3 | `{ printsWatts:true }` | `{ on:"Lit", off:"Dark" }` |

- No `startWatts`, `dutyCycle` or `cycleMinutes`.
- Their why-comment, in the `APPLIANCES` block's style, gives the sources
  quoted under Reference figures. It says what isn't modelled: power factor
  (the engine's current is watts ÷ volts), and metal halide's warm-up, which
  is why the yard took LED. It says the 90 W is derived from a secondary
  source, and that `leftOnChance` is a judgment call, retunable.

### 5. The `galpon` wiring

`BUILDING_TYPES.galpon.wiring`, and its layouts in `WIRING_TEMPLATES`:

- **Board:** `{ name:"Meter box", role:"street", rating:32, direct:true }`,
  as the houses' (T1G, 32 A main, meter on the property line).
- **One panel:** id `shed`, name "Breaker panel", role `office` (designed,
  retunable). Its main is `{ rating:40, rcd:true }`, borrowed from the house
  templates.
- **Circuits**, in panel order:
  - `{ key:"lights", label:"LIGHTS", rating:10, volts:220, roles:["floor",
    "office"] }`
  - `{ key:"sockets", label:"SOCKETS", rating:20, volts:220, sockets:true,
    roles:["office"] }`
- **Fixtures:**
  - `{ key:"light_office", appliance:"led_light", circuit:"lights",
    role:"office" }`
  - The floor's bank: `{ key:"light_floor", appliance:<per instance>,
    circuit:"lights", role:"floor", count:<per instance> }`.
  - Nothing else: no fridge, no water heater, no pump.
- **The floor's bank differs by instance:**

  | Instance | `appliance` | `count` | LIGHTS load |
  |---|---|---|---|
  | `paper_mill` | `led_highbay_200` | 8 | 1,610 W, about 7.3 A |
  | `corralon` | `led_highbay_100` | 4 | 410 W |
  | `mechanic` | `fluorescent_batten` | 8 | 730 W |
  | `goods_shed` | none (no supply) | — | — |

  The counts: the mill's is about 960 m² at 100 lux, the yard's about
  240 m² at 100 lux; all three are judgment calls, retunable. Say so where
  they're set.
- The network ids are fixed once shipped: `<inst>.board`, `<inst>.shed`,
  `<inst>.shed.lights`, `<inst>.shed.sockets`, `<inst>.shed.light_office`,
  `<inst>.shed.light_floor`, `<inst>.shed.plug.office`, and for the mill
  `paper_mill.board.shed`.

### 6. Per instance

**`corralon`:**
- `floor`: `desc` becomes "A corrugated shed at the back of the yard: a wall
  of hanging tools, bins of nails and screws, shelves of paint tins.",
  `searchLabel:"Search the shed"`. Containers, items and `searchMinutes:20`
  unchanged.
- A new room by `overrides.addRooms`: `{ role:"yard", room:"Yard",
  shelter:"none", floorCap:80, desc:"Bricks stacked on pallets, bags of
  cement under a sheet of plastic, lengths of pipe in a rack. The gate onto
  the road is shut.", containers:[] }`. Room id `corralon_yard`. `floorCap`
  is a judgment call, retunable.
- A link by `overrides.links`: `{ between:["floor", "yard"], label:["Go out
  to the yard", "Go back into the shed"], distanceM:10 }`, no door. The
  distance is a judgment call, retunable. The yard is reached only from
  inside; the gate is text only (an implementation choice, revisable).
- Not wired: no role in the yard is on any circuit.
- Wiring: the type's board, and the bank of four `led_highbay_100`.

**`mechanic`:**
- Wiring: the type's board, and the bank of eight `fluorescent_batten`.
- Text unchanged: it keeps the pit, the alignment rig and the car on stands.

**`goods_shed`:**
- `overrides.wiring: null`.
- `floor`'s `desc` becomes "A long shed beside the siding, under a rust-red
  roof that runs along the track. Grass has grown up to the walls, and the
  loading door faces the rails." "Brick walls" goes: the wall material is
  unconfirmed. The text says nothing of lights or power.
- The office keeps its text (it's an addition; the interior is unknown).
- The crates and their items stay exactly as today.

**`paper_mill`:**
- `overrides.wiring.board`: `{ name:"Main board", role:"floor", rating:125,
  direct:false, feeders:[{ panel:"shed", label:"LIGHTING & OFFICES",
  rating:40 }] }`. The 125 A main is the largest rating
  `STANDARD_BREAKER_RATINGS` holds, standing in for a works' board; the
  feeder's 40 A and its label are judgment calls, retunable. Its comment
  says the board is fed from the works' own transformer (text only), and
  that the works gets no three-phase model: its current is computed as
  single-phase, which is wrong for a works, but these loads are far from any
  limit (Tom, 2026-10-05).
- The bank of eight `led_highbay_200`.
- `floor`'s `desc` becomes "A hall of rollers and vats, gone quiet. The smell
  of pulp hangs in the air, and the main board stands against the far wall."
- It keeps the type's two rooms, standing for one hall of the works.

**All four:** names and addresses stay. No real trading name appears, in game
text or appliance names. Whether a lamp is lit shows on its readout, never in
room text.

The room text above follows `docs/01-writing.md` (quoted for the coding
session): second person, present tense, plain; a concrete object over a mood
word; one to three sentences; never explains the collapse.

## Design decisions to make during implementation

Name each pick in the changelog entry.

1. **Where the "unsupplied" flag lives.** Recommended: `BUILDING_INFO[b]
   .supplied`, derived from the instance's `overrides`, since
   `tankRefillLph()` and `validateWiring()` already read `BUILDING_INFO`, and
   `containerPowered()`/`effectiveAge()` reach it through the room's
   `buildingId`. Alternative: a field on each built room. Either is derived
   and never saved.
2. **How each instance gets its floor bank.** Recommended: one base layout
   (the two circuits and `light_office`) and three `WIRING_TEMPLATES`
   entries built from it below the table, as `casa_fuses` is, each adding
   `light_floor`; the type's `shed` panel names one (say `galpon_workshop`)
   and the other two instances override `panels.shed.template`.
   Alternative: an inline `layout` per instance via the panel override. The
   templates keep instance data out of the mechanic and keep the layouts
   next to the other templates.
3. **How `count` sits on a load:** always set (1 by default) or only when
   greater than 1. Either, consistently.

None changes the version type.

## Data / schema changes

- **No new state.** Nothing in PLAYER STATE changes; no save-key rotation.
- **Instance schema** (the comment above `buildingInstances()`):
  `overrides.wiring` gains `board:{ …fields }` and may be `null` (no
  supply). Update the comment, including the type schema's "Absent: …
  fall back to the grid" line, which must now say an instance with
  `wiring: null` is deliberately unsupplied and does not fall back.
- **Fixture schema** (POWER SCHEMA / WIRING_TEMPLATES' comment): `count?`.
- **Appliance schema**: `plural?`.
- **World data:** room `corralon_yard`, new. Every existing room id kept.
- **Network ids:** as listed in §5.

## In scope

- [ ] `mergeWiring()`: board override; `null` for no supply.
- [ ] The unsupplied flag, and its four readers (`containerPowered()`,
      `effectiveAge()`, `tankRefillLph()`, `validateWiring()`'s `unwired`).
- [ ] `buildBuilding()` reports an unsupplied instance whose type's panels
      carry template doors or windows.
- [ ] Fixture `count` through `expandWiring()`, `powerSnapshot()` and
      `untouchedTrippers()`; `plural` and the one load-naming helper at its
      three readers; `validateWiring()` checks for both.
- [ ] Three appliances, with their why-comment.
- [ ] `galpon` wiring and its layouts.
- [ ] The four instances' overrides and text, and `corralon_yard`.
- [ ] Every new problem check has been made to fire once by hand (a bad
      `count`, a missing `plural`, a board override on an unwired type) and
      then reverted.
- [ ] `validateWiring()` returns no problems, and no galpón room is in
      `unwired`.
- [ ] Played in the browser: each galpón's floor and office lights in the
      Electrical view; the floor's bank as one row named in the plural, a
      200 W / 100 W / 90 W nameplate, one switch; the mill's board in its
      floor with one feeder, LIGHTING & OFFICES, under detailed and under
      simplified rules (simplified skips the feeder); a clamp on the mill's
      LIGHTS reads about 7.3 A with the bank and the office light on;
      tripping the feeder darkens the panel; the goods shed shows nothing
      electrical; the corralón's yard is reached from the shed and back.
- [ ] An existing v0.14.0 save loads and has the new yard.
- [ ] `docs/systems/power.md` updated (below).

## Explicitly out of scope

- Any three-phase model, and the mill's machinery as loads (Tom).
- A compressor or a lift in the repair shop (it would need a `research`
  issue first).
- Bank switching in the engine beyond `count` (separate switches per lamp
  group, contactors).
- Removing the unwired-room fallback: #258.
- Light levels as a mechanic (darkness, what a lit room does).
- A street gate into the corralón's yard.
- The other types under #250: `shop_home` (#307), the comisaría (#309).
- Overheating of old boards (#472) and well-pump replay coverage (#460):
  adjacent, untouched.

## Sections touched

- **WORLD DATA:** BUILDING TYPES (`galpon`, the instance and type schema
  comments, `buildingInstances()`, `buildBuilding()`, `mergeWiring()`),
  `BUILDING_INFO`, POWER SCHEMA (`APPLIANCES`, `WIRING_TEMPLATES`).
- **SURVIVAL / TIME SIMULATION:** its POWER sub-section (`expandWiring()`,
  `powerSnapshot()`, `untouchedTrippers()`), `containerPowered()`,
  `effectiveAge()`, `tankRefillLph()`.
- **WORLD INTERACTION:** `doSwitchLoad()`'s log line.
- **UI / RENDERING:** `renderCircuitTab()`'s load names.
- The dev checks: `validateWiring()`.

## Systems docs

Read before starting: `docs/systems/power.md` (and `docs/systems/spoilage.md`
for `effectiveAge()`, and `docs/systems/fluids.md` for tank refilling, as
needed).

Update in the same pull request:
- `docs/systems/power.md`: unsupplied buildings (an instance with
  `overrides.wiring: null` has no network and no grid fallback: what
  `containerPowered()`, `effectiveAge()` and `tankRefillLph()` then do); the
  board override; a fixture's `count` and an appliance's `plural`. Its tank
  refill line (today "the unwired fallback, none today") gains the
  unsupplied case.

## UI changes

- The Electrical view in each wired galpón: on LIGHTS, the floor's bank as
  one row, "High-bay lamps" or "Fluorescent lights", with "Lit"/"Dark", one
  Switch on/off, and a one-fitting nameplate; the office's "Light"; and
  SOCKETS in the office.
- The paper mill's floor holds a board, "Main board", with a 125 A main and
  one feeder, LIGHTING & OFFICES, 40 A.
- The goods shed shows "Nothing electrical to show here."
- The log line when switching a bank: "You switch the high-bay lamps on."
- The corralón: "Search the shed", and the new exits "Go out to the yard" /
  "Go back into the shed".

## Dependencies / issue linkage

- `Closes #308` and `Closes #483`.
- Part of #250. Takes four buildings off #258's list; #258's check must
  accept unsupplied rooms (this pass does it for the warning).
- Nothing is expected to be deferred. Anything that is gets an issue at the
  wrap.

## Open questions for Tom

None. Every design question was settled on #308 and #483 (Tom, 2026-10-05),
including the bank as one load with a fixture `count`. The room text in §6
was drafted in planning from #308's direction; it is game text, retunable.
