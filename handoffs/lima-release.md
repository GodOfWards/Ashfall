# Ashfall Handoff — The Lima release

Current shipped version: v0.9.4
Implied version-change type: MINOR (the save format changes in phase 1, and
  phases 1, 7 and 8 add new saved state; the whole world is replaced, so
  saves break, which Tom accepted: "I don't care if it breaks saves")
Issues: #295, #291, #237, #284, #294, #292 (closed by this pass); #296 (in
  part: the confirmed items only, the issue stays open for the rest)

## What this is

The game moves from its invented American town to **Lima, Partido de Zárate,
Buenos Aires province, Argentina**, in one MINOR, so that saves break once.
The release is built in **eight phases**, one commit each (`Phase N: …`),
with the branch pushed after every phase:

| Phase | Issue | What |
|---|---|---|
| 1 | #295 | Rooms split into definition and saved state; the save carries only what play changed, and which buildings the player has entered |
| 2 | #291 | Building types: a type generates a building's rooms, exits, doors, windows and containers from one line of data; doors that lock by key from outside only, and forcing one with a crowbar |
| 3 | #237 | The map engine: metre coordinates, streets at any angle, a north arrow, the river and the railway, a new zoom ladder; the crossing-lights code removed |
| 4 | #237 | Lima's streets: 777 stops and 1,008 links from Appendix A, one exit per direction, text by street type |
| 5 | #237, #284 | Lima's landmarks and homes, the player's row house, the start; every invented building removed |
| 6 | #296 | Argentine items, no brands |
| 7 | #294 | Water per house: a tank that keeps a house's taps running after the grid fails |
| 8 | #292 | Walk to…: travel to a chosen place along the streets |

Tom's framing (#237): "rebuild to real geography"; "the whole built-up town
and the rail and the road towards Atucha"; "Go for mostly gravel roads,
except the ones where you clearly saw paved streets. The rest on the outside
would be just dirt roads." And for the buildings: "Go unwired. Then wiring
would be just a PATCH."

Tom answered the planning session's last three questions on 2026-09-27
(locked homes, fishing, the chalets); the answers are folded into the phases
below and recorded under Open questions for Tom.

## Relevant existing state

Verified against `ashfall.html` at v0.9.4 (10,829 lines).

**Saves.** `serializeGame()` (about l.7637) writes `{ version, state, world,
doors, windows }`; `world` is every room with every field. `applyLoadedData()`
(about l.7989) sets `world = data.world` after `validateLoadedWorld()`, then
runs the backfills: `backfillLocationIds()`, `backfillRenamedContainers()`,
`backfillContainerFields()`, `backfillRoomAddresses()`, `backfillRoomDescs()`,
`migrateCookingRelease()` (whose second half re-syncs `sink` and container
`tags` from the definitions), and the state ones (`backfillItemIds()`,
`backfillSlotItemIds()`, `backfillRegistryTags()`, `backfillIllnessScale()`,
`backfillInventoryCap()`, `backfillPowerState()`). Doors and windows already
split definition from saved state: `buildDoors(saved)`, `buildWindows(saved)`,
`savedDoorState()`, `savedWindowState()`. That split is the pattern phase 1
extends to rooms.

**What play writes on a room** (every write site, found by search):
`searched` (`doSearch()`), `carLocked` (`doBreakCar()`), `heatActive`,
`fireMinutesLeft`, `campfireBuilt` (FIRE / COOKING and the burn-down in
`applyWorldTicking()`), `hasTree` (chopping), `floor` (every take and drop),
`containers` (a campfire's container is pushed by `doBuildFire()` and removed
by dismantling). On a container: `items`, `spawnRolled` and
`lastRolledMinute` (`doOpenContainer()`), `locked` (`doUnlockContainer()`),
`timerMinutes` (the stove timer). The same holds for `carContainers`.

**Doors.** DOOR SCHEMA (about l.1767): `sides`, `building`, `locked`,
`lockable`; saved `{ locked, open }`. A locked door drops its exits
(`getExitsForRoom()`); unlocking needs a key the player carries
(`findKeyForDoor()`: a `masterKey` for the door's `building`, or a key whose
`doorId` is the door). There is **no way to force a door** today; forcing is
cars only (`doBreakCar()`). The tag `prying` gates nothing
(`validateReachability()`'s comment says so). Windows to the outside have one
room and are never a route, broken or not (WINDOW SCHEMA).

**Openings and wiring.** Every interior door and window of the Acorn flats
comes from `WIRING_TEMPLATES.apartment`'s `doors` and `windows`, expanded by
`expandOpenings(WIRING, WIRING_TEMPLATES)`. `WIRING` has one entry, `acorn`.
A room no panel wires falls back to the grid (`containerPowered()`,
`effectiveAge()`). `validateWiring()` warns about every fully sheltered room
with no wiring, "a warning until #258".

**The world.** `makeDefaultWorld()` (about l.4492) assembles 26 hand-written
builders (`buildAcornApartments()` … `buildNinthSt()`) and returns
`applyComputedDirections(stampTemplateDoorIds(world))`. `LOCATIONS` (about
l.1544) holds integer metres, +x east, +y north. `computeDirection()` picks the
dominant axis; `applyComputedDirections()` swaps the compass word in any
cross-Location exit label. Corners today carry **eight** exits: "Head west on
Poplar St" to the next corner and "Step into the block (west)" to the
mid-block. `BUILDINGS` (about l.1753) are the map-named buildings.
`makeDefaultState()` starts in `"living"` with the key `acorn_apt_2a_key`.

**Water.** `waterRunning(m){ return gridUp(m); }` (about l.5990); a `sink`
room fills a water-holding item while it runs (`doFillAtSink()`, the check at
about l.5398).

**The crossing code.** `CROSSING_STANDBY_MIN` (l.520), `crossingLit()`
(l.5993), the `crossing` DESC_READERS entry (l.10282), one room using it
(`mid_2nd_d_mi`, about l.4188), and the ROOM SCHEMA sentence about it.

**The map.** `MAP_SPACING = 130` SVG units per 100 m; `MAP_MIN_COL` …
`MAP_MAX_ROW` bound the old 8 × 8 grid; `mapToSvg(col, row)` takes grid
units; `MAP_STREETS` lists each street's chain of stop ids;
`mapBindStreetLabels()` assumes every street is horizontal or vertical
(`horizontal: a.y === b.y`), and `mapLabelBox()` builds axis-aligned boxes;
both renderers draw the river as one straight line along the top row;
`MAP_ZOOM_RANGE` is counted in blocks (close 1–3, wide 3–6);
`renderMap()` falls back to `"mid_poplar_1_2"`.

**Items.** `ITEM_REGISTRY` (about l.953) and `SPAWN_POOLS` (about l.1295).
"Replacing an item id keeps its entry's derived chance" (SPAWN_POOLS
comment). Acorn-only items: `acorn_apt_2a_key`, `master_key` (`building:
"acorn"`), `building_ledger`.

**Canon and reference facts this handoff depends on**, quoted because the
coding session reads neither:
- The collapse comes in **February 2025**. The town is Lima; the player is
  from Lima and lives in **a row house in the Barrio Complejo Nuclear Atucha**
  (canon).
- **The grid runs at 14° and 104°.** Local metres are centred on 34.0447 S,
  59.1961 W, with x = Δlon × 111,320 × cos 34.0447° and y = Δlat × 110,574;
  the grid frame is u = x cos 14° − y sin 14°, v = x sin 14° + y cos 14°
  (`reference/Lima.md`, "The street grid", secondary, from OSM). **Every
  coordinate in Appendix A is already (u, v), rounded to the metre.**
- **Street surfaces** (`reference/Lima.md`, "Streets and surfaces", from
  imagery, estimate; Tom first-hand): paved around the plaza, on the main
  axis, on the Camino Provincial and along the railway; **mostly gravel
  (*ripio*)** elsewhere; dirt at the edge where the town meets the fields.
- **The plaza** is a single block with diagonal paths and trees. Shops, the
  church and public buildings cluster around it. **Mixed use is the norm:**
  a shop on the ground floor with a home on top or behind (Tom).
- **Homes:** most have **bars on their windows**; **street doors open from
  outside only with a key**, freely from inside (Tom, Street View).
- **No gas network** (all bottled gas, *garrafas*), **no sewers** (septic
  tanks), and many homes have **their own water tank and pump** (Tom,
  first-hand).
- **Level crossings have a bell and nothing more**, day or night (Tom).
- **Tank size:** a guideline of at least 800 L per dwelling, and about
  1,000 L for a family of four at 250 L per person per day (Río Negro's
  water authority; secondary). **The Barrio Atucha's own tanks are
  unconfirmed.**
- **The Barrio Atucha:** about 40 chalets in treed gardens on winding lanes,
  a western strip of terraced row houses around U-shaped courtyards, the
  club (pool, tennis courts, hall) at the north-west corner (imagery).
- **Brands and names** (`CLAUDE.md`): no product brand appears; a private
  business is named by what it is ("the pharmacy"); state institutions keep
  their real names (Comisaría Zárate 2, Banco Nación, Correo Argentino, the
  municipal hospital, the Delegación Municipal). Real places keep their
  Spanish names, accents included, never translated.
- **Privacy:** a home is never given a house number or tied to a real
  family. Its rooms' `address` is the street name only.

## Rules / mechanics

### Phase 1 — Rooms: definition and saved state (#295)

**Save format** becomes `{ version, state, rooms, doors, windows }`. `world`
is no longer written.

- **Definitions** (never saved): everything `makeDefaultWorld()` returns,
  rebuilt fresh on every load.
- **Saved room state**, per room id, **only for rooms whose state differs
  from their fresh definition**:
  - room fields: `floor`, `searched`, `carLocked`, `heatActive`,
    `fireMinutesLeft`, `campfireBuilt`, `hasTree`;
  - per container, in `containers` and in `carContainers`, by container id:
    `items`, `spawnRolled`, `lastRolledMinute`, `locked`, `timerMinutes`;
  - **a container the definition lacks** (made in play, today only the
    campfire's) is saved **whole** and restored whole.
  - "Differs" is a comparison against a freshly built definition with every
    item's `_uid` ignored. Before writing this, the coding session repeats the
    write-site search in Relevant existing state; any field it finds that
    isn't listed is added to the saved set and named in the changelog.
- **New state, `state.enteredBuildings`:** an array of building ids, in the
  order first entered. `doMove()` appends the destination room's
  `buildingId` (phase 2 adds the field) when it has one and it isn't listed.
  Walk to… (phase 8) reads it.
- **Load:** `buildWorld(savedRooms)` builds the definitions, then applies
  each saved room's fields by id and each saved container's fields by
  container id. A saved room or container the definitions no longer have is
  dropped with a `console.warn`; a definition the save lacks keeps its
  default. Only well-typed fields are taken (the `buildDoors()` rule).
- **Old saves are refused**: a save with no `rooms` object (every save before
  this release) logs "This save is from an older version of Ashfall and
  can't be loaded." and loads nothing. Import takes the same path.
- **Retired:** `backfillLocationIds()`, `backfillRoomAddresses()`,
  `backfillRoomDescs()`, `backfillContainerFields()`,
  `backfillRenamedContainers()`, and the world half of
  `migrateCookingRelease()`. Each existed because definitions were saved.
  The state-side backfills stay; they are harmless on a new save, and
  retiring them is not this pass.
- `validateLoadedWorld()` validates the new shape: `rooms` is an object;
  each saved `floor` and container `items` is an array; `state.currentRoom`
  exists in the rebuilt world.

### Phase 2 — Building types (#291)

**`BUILDING_TYPES`** (WORLD DATA) is the mechanic's definition data; a
**building instance** is one line. The builder (WORLD DATA helpers, beside
`makeDefaultWorld()`) expands each instance into rooms, exits, doors and
windows. It replaces `expandOpenings()`'s role for everything this release
builds: `authoredDoors()`/`authoredWindows()` lose their Acorn entries (phase
5), the building types supply the rest, and `makeDefaultDoors()` /
`makeDefaultWindows()` merge in the types' openings.

A type:

```
{ label,            // "row house": what an exit calls it ("Enter the row house")
  rooms: [ { role, room, shelter, desc, floorCap, containers:[…], sink?, sleepSpot?,
             cannotHaveFire?, searchLabel?, searchMinutes? } ],
  entry,            // the role the street exit leads into
  links: [ { between:[role, role], label:[a→b, b→a], distanceM, door? } ],
  doors: [ { key, between:[role, role] | ["street", role], label, lock, locked, lockable? } ],
  windows: [ { role, label, breakTag } ],
  water?            // phase 7
}
```

An instance:

```
{ id, type, site, name?, address, seed?, overrides? }
```

- `site` is the stop id the building hangs off. `"street"` in a type's
  `links` and `doors` means that stop.
- Room ids are `<id>_<role>`. Door ids are `<id>-<key>`; window ids are
  `<id>-<role>-window`. These must never change: saves key on them.
- Every room gets `buildingId: id` (new, definition field), `building:
  name ?? type name` (ROOM SCHEMA's name field), `address` from the
  instance, `area: null`, and `locationId: <id>_f0`. `LOCATIONS[<id>_f0]` is
  the site's (u, v) unless the instance gives `at: [u, v]` (the paper mill).
  Links between a type's own rooms are same-Location exits with the type's
  `distanceM`; the street exit is cross-Location.
- `overrides`: `{ rooms:{ role: { …fields } }, addRooms:[…], links:[…],
  doors:{ key: {…} | null } }`, merged over the type's, for landmarks and the
  player's home.
- `seed` is only a stable variant picker for the type's text, where a type
  offers variants. Definitions never read `state.seed`: which home is where
  is the same in every run. Contents come from spawn pools, which roll from
  the run's seed when first opened, as today.

**Door locks, one new definition field, `lock`:**

| `lock` | From outside | From inside | Used for |
|---|---|---|---|
| `"key"` (default, today's) | key | key | unchanged |
| `"latch"` | key only | by hand, no key | every home's and shop's street door |
| `"bolt"` | cannot be opened | by hand, no key | the row house's back door |

- `lock` other than `"key"` needs `inside: roomId`, the room on the inside.
  The builder sets it from the type's `between`.
- From the inside room, a locked `latch` or `bolt` door offers **Unlock the
  front door** / **Draw the bolt on the back door** in the Here panel, no key
  needed; an unlocked one offers **Lock the front door** / **Bolt the back
  door**. From outside, a `latch` door behaves as a `"key"` door does today;
  a locked `bolt` door shows "The back door is bolted from the inside." and
  offers nothing.
- A new optional door field `label` ("front", "back", "bedroom") is what
  `doorLabel()` uses first when present.
- **Barred windows** carry the label "barred window". Nothing else changes:
  a window to the outside is already never a route. Cutting bars is out of
  scope.
- Every home type's street door is a `latch`.
- **Starting lock** (Tom, 2026-09-27): a **generated home's** street door
  starts locked when the stable hash of its building id, mod 100, is below
  `HOME_LOCKED_PCT = 60`: about 60% of homes, the same ones in every run.
  Retunable. The player's home starts locked (phase 5). **Landmarks' street
  doors start unlocked**, as the buildings they replace were enterable
  without a key; retunable. Back doors (`bolt`) start bolted.
- **Forcing a door** (Tom, 2026-09-27), a new action:
  - Offered from the **outside** room of a locked `latch` door while the
    player carries a `prying` tool (the crowbar today): **Force the front
    door**. Never offered for a `bolt` or a `"key"` door.
  - Takes `FORCE_DOOR_MIN = 5` minutes (`advanceTime()`) and costs
    `FORCE_DOOR_MIN * BASELINE_STAMINA_RATE` Exertion, the rate chopping
    uses. Both retunable.
  - The door becomes unlocked and **`broken: true`**, a new saved door field
    (default false). A broken door never locks again: no lock action is
    offered from either side, and the Here panel notes "The lock on the front
    door is broken." Open and Close still work.
  - Log: "You work the crowbar into the frame by the lock until it gives."
    (functional; retunable).
  - `validateReachability()`'s comment that `prying` gates nothing is
    rewritten: it now gates forcing a door.

**The types.** Room text is true of every building of that type, per
"Writing game text". Container names, capacities and pools reuse the Acorn
flats' (e.g. Fridge 30 kg `fridge` tag, Pantry 20 kg). Nothing is wired.

**`row_house`** (Tom-approved, #284): one storey, about 11 × 10.5 m inside,
entered from its courtyard stop; the front strip is part of the stop.

| Role | `room` | Shelter | Properties | Containers (pools) |
|---|---|---|---|---|
| living | Living room | full | sleepSpot couch, cannotHaveFire | Sideboard (recreation, residential_personal), Bookshelf (recreation, documents_lore) |
| kitchen | Kitchen | full | sink, cannotHaveFire | Stove 8 kg `device`,`heat` (kitchen_perishable, kitchen_tools), Cupboards (kitchen_nonperishable, kitchen_tools), Drawers (kitchen_tools), Fridge `fridge` (kitchen_perishable), Freezer `freezer` (kitchen_frozen) |
| laundry | Laundry | full | sink, cannotHaveFire | Shelf (cleaning_supplies, tools_general) |
| hallway | Hallway | full | cannotHaveFire | none |
| bedroom | Bedroom | full | sleepSpot bed, cannotHaveFire | Wardrobe (clothing), Bedside table (residential_personal, documents_lore, self_defense, electronics), Chest of drawers (clothing, residential_personal) |
| bedroom2 | Bedroom 2 | full | sleepSpot bed, cannotHaveFire | Wardrobe (clothing, baby_items), Chest of drawers (clothing, recreation) |
| bathroom | Bathroom | full | sink, cannotHaveFire | Bathroom cabinet (medical_otc, hygiene), Under-basin cupboard (hygiene, cleaning_supplies) |
| garden | Back garden | none | fire allowed | Shed box (fuel_fire, tools_general) |

- Links: street ↔ living (door `front`, latch); living ↔ kitchen (open, no
  door, 3 m); living ↔ hallway (4 m); hallway ↔ bedroom, hallway ↔ bedroom2,
  hallway ↔ bathroom (doors, `lockable:false`, 3 m); kitchen ↔ laundry (3 m);
  laundry ↔ garden (door `back`, bolt, 3 m).
- Windows: living, kitchen, bedroom, bedroom2 "barred window"; bathroom
  "small window", high up (label only). Every `breakTag: "blunt"`.
- Fixtures named in text only (nothing is wired): the garrafa cooker, the
  fridge, the washing machine, the house water pump, the *tablero* in the
  hallway, the garrafa heater in the living room (a design addition Tom
  approved), shower, toilet, bidet and basin, the brick *parrilla* (a design
  addition Tom approved), the clothesline and the septic tank.
- Text:
  - living: "A living room with the dining table at one end. The bars on the window throw stripes across the floor, and a gas heater stands against the wall."
  - kitchen: "A narrow kitchen, open to the living room. The cooker runs off a gas bottle in the cupboard beneath it."
  - laundry: "A washing machine, a deep sink, and the pump that fills the house's water tank. The back door opens onto the garden."
  - hallway: "A short hallway. The breaker box is on the wall by the bathroom door."
  - bedroom: "A double bed and a wardrobe. The window has bars, like every other in the house."
  - bedroom2: "The smaller bedroom. A single bed pushed against the wall."
  - bathroom: "Shower, toilet, bidet and basin, tiled to the ceiling. The window is small and high up."
  - garden: "A patch of grass behind the house. A brick parrilla against the back wall, a clothesline, and the concrete lid of the septic tank."

**`casa`** (**designed**: the plain Lima house, #291; its layout is not
sourced): living (street door `front`, latch; barred window; sleepSpot
couch), kitchen (sink; stove, cupboards, fridge, freezer as the row house),
bedroom (barred window; the row house's bedroom containers), bathroom (sink;
its containers), patio (shelter none; fire allowed; Shed box). Links: street ↔
living, living ↔ kitchen, living ↔ bedroom (door, lockless), kitchen ↔
bathroom (door, lockless), kitchen ↔ patio (door `back`, bolt). Text:
  - living: "A front room that is living room and dining room both. Barred windows onto the street, the blinds half down."
  - kitchen: "A kitchen with a gas cooker fed from a bottle, and a table with two chairs."
  - bedroom: "A bedroom. The bed is made, more or less."
  - bathroom: "A small bathroom with a bidet beside the toilet."
  - patio: "A paved patio at the back, walled in, with a few pots and a clothesline."

**`shop_home`**: shop (street door `front`, latch; one barred window;
cannotHaveFire) and home behind it (sink, sleepSpot couch, cannotHaveFire;
door between them, lockless). The old Corner Store and Pharmacy were exactly
this: a shop with a flat. Text comes from the instance's overrides.

**`galpon`**: floor (shelter full; cannotHaveFire) and office
(cannotHaveFire; door between, lockless). Street door `front`, latch. Text
from overrides.

**Named scenery** is not a type: a `BUILDINGS` entry with an `anchor` stop
and no rooms (phase 5).

### Phase 3 — The map engine (#237)

- **Coordinates:** `mapToSvg(x, y)` takes **metres** in the grid frame:
  `MAP_UNITS_PER_M = MAP_SPACING / 100` (1.3, today's scale). The margin and
  origin come from the extent of `LOCATIONS` at startup, not from
  `MAP_MIN_COL` … `MAP_MAX_ROW`, which go.
- **`GRID_BEARING_DEG = 14`** (WORLD DATA, beside `LOCATIONS`): the true
  bearing of the map's "up". `LOCATIONS` are stored already rotated
  (Appendix A), so movement and `computeDirection()` never read it; the north
  arrow does. Its comment says both.
- **North arrow:** a small arrow and "N" pinned to a corner of the map
  viewport (outside the panning SVG group, so it doesn't move), rotated
  **−14°** (anticlockwise: true north lies 14° left of the map's up).
- **Streets at any angle:** from phase 4, `MAP_STREETS` is **derived at
  startup** from the street links: for each street name, its links chained
  into maximal paths. (In phase 3 the engine still takes the old hand-written
  list.) For labels, each path is cut into **straight runs**
  (consecutive segments whose heading changes by less than 10°), and each run
  is labelled as a street is today, rotated onto the run's heading folded into
  (−90°, 90°]. `mapLabelBox()` and the hit tests become **oriented boxes**
  (project the point onto the run's axis and its normal). Unnamed streets and
  the rail get no label.
- **River:** the four polylines in Appendix A.4, drawn in both views with
  the existing `map-river` class. The old straight river line goes.
- **Railway:** the rail links (surface `r`) drawn as a new `map-rail` class,
  thin and dashed, under the streets.
- **Zoom ladder, in metres of span:** close `[100, 200, 300]`, opening at
  200; wide `[300, 600, 1200, 2400]`, opening at 1200. The two modes still
  share 300. Retunable; the old block counts go.
- **Fallback node** in `renderMap()`: the start stop (phase 4 onward), not
  `"mid_poplar_1_2"`.
- **The crossing code goes:** `CROSSING_STANDBY_MIN`, `crossingLit()`, the
  `crossing` DESC_READERS entry, the ROOM SCHEMA sentence, and
  `mid_2nd_d_mi`'s variants (it gets plain text for the one phase it
  survives). Tom (#237): it comes back only with a feature that rings the
  bell and something that cares.
- **Must hold at the end of phase 3:** the old town still draws and plays as
  it did, streets labelled, plus the north arrow. The river and rail drawing
  land with their data in phase 4; until then the old straight river line
  stays. (Phase 3 changes the engine, not the data.)

### Phase 4 — Lima's streets (#237)

**Data.** Appendix A is transcribed into the file as compact data (Design
decision 1): a street-code legend, 777 stops and 1,008 links. It replaces
every `build…St()` builder, the old `LOCATIONS` street entries and
`MAP_STREETS`. The old buildings stay attached to nothing until phase 5
removes them, so phase 4 moves the start to the home stop
`m_c90b_c117_c119` for one phase.

**A stop's room**, for every stop row:
- id and `locationId`: the stop id; `LOCATIONS[id] = { x:u, y:v, z:0 }`.
- `address`:
  - corner: its streets' names joined with " & ", unnamed ones left out;
    "Unnamed street" when all are unnamed;
  - mid: its street's name, or "Unnamed street";
  - rural: "Calle 111"; rail: "FC Mitre"; station: "Estación Lima".
- `room`: a mid with two named cross streets, "between <A> & <B>"; with
  one, "near <A>"; with none, null. Everything else null.
- `area` null, `shelter` "none", `floorCap` 100 at a corner and 20
  elsewhere (today's values).
- `hasTree: true` on plaza stops and on `barrio` mid stops. Retunable.
- **Parked cars:** a town stop whose stable hash (FNV-1a of the id) mod 10
  is 0 has a car (`carLocked` true when the hash's next digit is even), with
  a Boot (25 kg, pool `car_boot`) and a Glovebox (3 kg, pool `car_glovebox`).
  Both pools are new (phase 6 fills them; until then, `tools_general` and
  `documents_lore`). About one stop in ten; retunable.

**Exits: one per link, both ways; one exit per direction.** The compass
word comes from `computeDirection()`, as today.
- Along a named street: from a corner, "Head <dir> on <street>"; from a mid
  stop, "Head <dir> toward <the next corner's cross street>" when it has one,
  else "Head <dir> on <street>".
- Unnamed street: "Head <dir> along the unnamed street".
- Rail link: "Follow the tracks <dir>".
- The forecourt link (`fwd`): "Walk to the station" / "Walk out to <the
  corner's address>".
- **Two exits sharing a direction word** (18 stops): each gets
  " toward <the target's address, minus the link's own street>" appended; if
  that still leaves two identical, the second takes the target's `room`.
- "Step into the block" goes: the mid stop is simply the next stop.

**Text.** A stop flagged in Appendix A (`plaza`, `crossing`, `L:`, `S:`)
or rural, rail or station takes its hand-written text from Appendix B.
Every other stop takes a variant by type, chosen by stable hash of its id
(FNV-1a mod the count):

| Type | Mid stop | Corner |
|---|---|---|
| core | "A paved block of low houses built wall to wall. Every window has bars, and every door is shut." · "Low house fronts along the pavement, the paint faded. Nothing moves behind the bars." · "The street is paved here, with kerbs and a line of trees. It is very quiet." | "A paved corner. Nobody is waiting to cross." · "Two paved streets meet. No cars, no voices." |
| gravel | "A gravel street, the stones pushed into two ruts by tyres. The houses sit back behind low walls and wire fences." · "Loose gravel and dust. Each house along here is set back behind its own gate." · "A gravel street between low houses. Weeds grow along the edges, where the cars didn't reach." | "Two gravel streets meet. The crossing is just a wider patch of stones." · "A gravel corner, rutted where the cars used to turn." |
| dirt | "The street is packed earth here. Past the last houses, the fields begin." · "A dirt street at the edge of town, the ruts baked hard. Beyond the fences, open ground." | "Two dirt tracks cross at the edge of town." |
| barrio | "A lane in the Barrio Atucha. Chalets with red-tile roofs sit back in wide gardens under tall trees." · "Big gardens and tall trees along the lane. The lawns are already overdue for mowing." | "A junction of the barrio's lanes. Red-tile roofs show between the trees." |

**Must hold at the end of phase 4:** `validateLocations()` and
`validateRoomSchema()` pass; every stop is reachable from the home stop; the
map draws Lima at every zoom step.

### Phase 5 — Landmarks, homes and the start (#237, #284)

**Removed:** Acorn Apartments, Oak Apartments, the Alley, the Corner Store,
the Pharmacy, the Hardware Store, the Storage Facility, the Riverbank, the
Auto Workshop, the Police Station and Riverside Freight, with their
`BUILDINGS`, `LOCATIONS`, `MAP_BUILDING_OFFSETS`, `authoredDoors()` and
`authoredWindows()` entries, `WIRING.acorn` and `ACORN_HOUSE_ROOMS`.
`WIRING` becomes `{}`; `WIRING_TEMPLATES.apartment` keeps its `circuits`
and `fixtures` (the dev seam `simulatePower()` defaults to it, and #289
re-bases it) but loses `doors` and `windows`. Every Lima room is unwired
and falls back to the grid, as an unwired room does today.

**Landmarks** (the first-pass list Tom set on #237: real counterparts of the
game's current building roles). Each carries over the old building's
containers **and their hand-placed contents** by the room named, so the
start's balance doesn't shift. Contents are renamed by phase 6.

| Id | Stop | Type | `name` / map label | `address` | Old rooms carried over |
|---|---|---|---|---|---|
| `home` | `m_c90b_c117_c119` | row_house | "Home" | Calle 90 Bis | Acorn 2A's contents by role: living → living, kitchen → kitchen, bathroom → bathroom, bedroom → bedroom, balcony's storage bin → garden's Shed box |
| `row_neighbour` | `m_c90b_c117_c119` | row_house | "Row house" | Calle 90 Bis | none (pools only) |
| `pharmacy` | `m_c7_c10_c8` | shop_home | "Pharmacy" | Calle 7 | `pharmacy` → shop, `pharmacy_apt` → home |
| `comisaria` | `m_c12_c13_c15` | hand-authored (institution) | "Comisaría Zárate 2" | Calle 12 | `police_lobby` → Front desk, `police_evidence` → Cells & evidence |
| `corralon` | `m_cbar_dg2_c107` | galpon | "Building-materials yard" | Camino a Baradero | `hardware` → floor, `hardware_apt` → office |
| `almacen` | `x_c113_c50` | shop_home | "Almacén" | Calle 113 | `cornerstore` → shop, `cornerstore_apt` → home |
| `mechanic` | `x_c16_c7` | galpon | "Repair shop" | Calle 16 | `auto_shop` → floor, `auto_shop_back` → office |
| `goods_shed` | `estacion_lima` | galpon | "Goods shed" | Estación Lima | `storage`'s units → floor (renamed "Padlocked crate 1/2…", still `locked`, `breakTag:"cutting"`) |
| `paper_mill` | `r111_papermill`, `at:[-642, 5725]` | galpon | "Paper mill" | Calle 111 | `industrial_floor` → floor, `industrial_office` → office |

- The **almacén's site is designed**: no grocery in Lima was verified; this
  corner in the Nueve de Julio neighbourhood was chosen for play (#237).
  Every other site is real (Appendix B cites each).
- `oak_*` flats' contents are dropped: generated homes replace them.
- Landmark text (overrides):
  - pharmacy shop: "A small pharmacy. The glass counter is cracked, and most of the shelves behind it have been swept clean." · home: "The rooms behind the pharmacy. Someone lived here and left in a hurry."
  - comisaría front desk: "The front desk of the Comisaría Zárate 2. Papers on the floor, a chair on its side." · cells & evidence: "A corridor of cells, doors open, and a caged room of evidence shelves."
  - corralón floor: "A yard of stacked bricks, bags of cement and lengths of pipe, under a corrugated roof at the back." · office: "A cramped office with an order book open on the desk."
  - almacén shop: "A neighbourhood almacén: a counter, a fridge for drinks, shelves to the ceiling." · home: "The family's rooms behind the shop."
  - mechanic floor: "A workshop with a pit in the floor and an alignment rig. Oil stains, a car up on stands." · office: "A small office with a calendar and a stack of invoices."
  - goods shed floor: "The railway's goods shed. Brick walls, a high roof, a loading door onto the tracks." · office: "A cubicle by the door where someone checked the freight in and out."
  - paper mill floor: "A hall of rollers and vats, gone quiet. The smell of pulp hangs in the air." · office: "The shift office. A clipboard still hangs by the door."
- **Named scenery** (map markers, no rooms), anchored at: hospital
  `m_c6_c13_av11` ("Municipal hospital"); Banco Nación `m_av11_c8_c6`
  ("Banco Nación"); school `m_av11_c8_c6` ("Escuela Primaria Nº 9"); Correo
  Argentino `m_av11_c6_c4` ("Correo Argentino"); parish church
  `m_av11_c10_c8` ("San Isidro Labrador"); Delegación Municipal
  `m_c8_av11_c13` ("Delegación Municipal"); fire station `m_c7_acc_c20`
  ("Fire station"); the barrio's club `m_c117_c88_c84` ("Club"); petrol
  station `x_acc_av11_c20` ("Petrol station"); Estación Lima
  `estacion_lima` ("Estación Lima").
- **Generated homes: one enterable home on every `mid` stop but the home stop** (427), plus
  the neighbour row house at the home stop. Retunable. By stop type:
  every stop type → `casa`. In the barrio the `casa` is a **stand-in** for
  the chalets, whose interiors are unconfirmed, until a `chalet` type is
  researched (Tom, 2026-09-27). Instance id `h_<stop id>`, `name` "House",
  `address` the stop's street name, `seed` its hash. Their street doors
  start locked or not by `HOME_LOCKED_PCT` (phase 2).
- **Exits to buildings**, from the site stop: "Enter <the building's
  label>" ("Enter the pharmacy", "Enter the comisaría", "Enter a house");
  the player's home, "Go into your house"; the neighbour's, "Enter the
  neighbours' house". Back out: "Go out to the street" (the courtyard stop:
  "Go out to the courtyard").
- **The player's home** overrides:
  - living: "Your living room, as you left it. The television is dark, and your mate is still on the table where you set it down."
  - kitchen: "Your kitchen. The gas bottle under the cooker is the one you changed last week."
  - bedroom: "Your bedroom. The bed's unmade from whatever morning this all started."
  - garden: "Your back garden. The parrilla's grill is still greasy from the last asado."
- **The start:** `currentRoom: "home_living"`. The keychain holds
  `house_key` (phase 6), whose `doorId` is `"home-front"`. The front door
  starts **locked**, the back door **bolted**.
- `authoredDoors()` and `authoredWindows()` are left empty (the types supply
  every opening); keep the functions for later hand-authored buildings.

### Phase 6 — Items (#296, confirmed part)

Tags and behaviour never change with a name (`CLAUDE.md`). A renamed item
gets a new id where the old id names the old thing; every reference moves
with it, and its pool entries keep their derived chances.

| Old id → new id | New name | Notes |
|---|---|---|
| `registration_papers` → `cedula_verde` | Cédula verde | the car's registration card |
| `peanut_butter` → `dulce_de_leche` | Jar of dulce de leche | same food values |
| `crumpled_cash` (kept) | Crumpled pesos | |
| `cash_bundle` (kept) | Bundle of pesos | |
| `utility_bill` (kept) | Electricity bill | from the electricity co-operative, unnamed |
| `milk` (kept) | Sachet of milk | |
| `acorn_apt_2a_key` → `house_key` | House key | `doorId:"home-front"` |

**Removed:** `checkbook`, `gift_card`, `master_key`, `building_ledger`, with
their pool entries and placements (the Acorn ledger's placement goes with
Acorn).

**Added** (tags as the named model item; chances chosen, retunable):

| Id | Name | Category | Model | Pools (chance) |
|---|---|---|---|---|
| `yerba_mate` | Bag of yerba mate | Food | `coffee_grounds` | kitchen_nonperishable (0.35), retail_stock_food (0.30) |
| `mate_bombilla` | Mate and bombilla | Misc | `thermos`, no food values | kitchen_tools (0.30) |
| `alfajores` | Box of alfajores | Food | `candy_bar` | kitchen_nonperishable (0.15), retail_stock_food (0.25) |
| `galletitas` | Pack of galletitas | Food | `crackers` | kitchen_nonperishable (0.25), retail_stock_food (0.25) |
| `dni_card` | DNI card | Misc | 0.01 kg, no tags | documents_lore (0.25), residential_personal (0.15) |
| `us_dollars` | Envelope of US dollars | Misc | `cash_bundle` | valuables (0.15) |

**New pools:** `car_boot` { emptyChance 0.3: tow_chain 0.2, work_gloves 0.3,
tire_iron 0.3, motor_oil 0.2, spare_parts_box 0.1 } and `car_glovebox`
{ emptyChance 0.2: cedula_verde 0.8, flashlight 0.2, owners_manual 0.4,
loose_change 0.3, chewing_gum 0.2, dead_cellphone 0.05 }. Chosen,
retunable. The home's living room gets one `mate_bombilla` hand-placed on
the floor (its text names it).

**Left for #296's next pass** (the issue stays open): the police kit
(badge, uniform), pepper spray and the stun gun (civilian legality
unconfirmed), the baseball bat, shop pools for a *ferretería*, *gomería* or
*comisaría*, the *garrafa* as an item (#287).

### Phase 7 — Water per house (#294)

- **Definition:** a type's `water: { tankL }`. `row_house`, `casa` and
  `shop_home` carry `tankL: 1000` (**retunable**: the sourced figure is a
  guideline for a family of four; the barrio's own tanks are unconfirmed).
  `galpon` and the comisaría have none.
- **New state:** `state.tankDrawn: { buildingId: litres }`, written only
  when water is drawn from a tank while the grid is down.
- **Rule:** while `gridUp()`, the pump keeps every tank full, and drawing
  writes nothing. After the grid fails, a tank holds `tankL −
  tankDrawn[id]`: full at the moment of failure, since nobody else draws.
  The pump is unwired and so stops with the grid (#245 and #289 can change
  that later).
- **`waterRunning(m)` becomes `waterRunningIn(roomId, m)`:** a room in a
  building with `water` runs while `gridUp(m) || tankLeft(id) > 0`; any
  other sink room runs while `gridUp(m)`, as today.
- **Drawing:** `doFillAtSink()` fills the item as today; when the grid is
  down it takes the litres it added (1 kg of water = 1 L) from the tank, and
  fills only what the tank has left.
- **Text** (functional, retunable): filling while the tank still has water
  after the grid failed, unchanged; the fill that empties it, "The tap
  coughs, spits, and runs dry."; a sink with an empty tank shows the note
  "The tap is dry." where the fill action was.

### Phase 8 — Walk to… (#292)

- **Known places** (Tom, option C): every stop in Lima, every landmark and
  named scenery marker, and every building in `state.enteredBuildings`.
  No fog, no bookmarks.
- **Where it's offered:**
  - **Map:** tapping a stop dot or a building marker opens a small card:
    the place's name (building name, else the stop's address and `room`), the
    walking time, and **Walk here**. The card closes on a tap elsewhere.
  - **Here panel:** a **Walk to…** button opens a list: Home first, then
    landmarks, scenery and entered buildings, nearest first by walking time,
    each with its time.
  - Offered anywhere; from inside a building, the route starts by leaving it.
    Not offered for the place you're in.
- **Route:** the shortest path over rooms by `exitMinutes(exit)` at the
  current gait and load, through `getExitsForRoom()` (so a locked door is not
  a route). A place with no route is listed with "no way through" and no
  button.
- **The walk** runs the route's exits one by one through `doMove()`, so time,
  hunger, thirst, fatigue, spoilage and overload run as if clicked. Rendering
  happens once at the end (and at an early stop). It **stops early** when:
  the player collapses (`state.collapseCount` rises), the game ends, or the
  next exit is no longer offered. One log line: "You walk to <place>." or
  "You stop at <address>." with the time taken.
- A walk is never saved; it runs within one click.

## Design decisions to make during implementation

Record each choice in the changelog's Notes/assumptions.

1. **How Appendix A lives in the file.** Recommended: the appendix's line
   format verbatim in template strings (`LIMA_STREET_CODES`, `LIMA_STOPS`,
   `LIMA_LINKS`), parsed once at startup by a small reader in WORLD DATA
   helpers. Alternative: JS object literals. Either is data, not a mechanic.
2. **Where phase 1 compares room state.** At save time against a freshly
   built world (recommended: one build per save), or through a dirty set
   kept by the writers. The dirty set must then cover every writer listed.
3. **Oriented label boxes (phase 3):** any approach that keeps today's
   behaviour for horizontal and vertical runs.
4. **Map card and Walk to… list styling (phase 8):** reuse the existing
   pop-up layer (`openLayer()`), recommended.
5. **The FNV-1a helper** for stable per-stop picks: one shared function.

## Data / schema changes

- **Save:** `{ version, state, rooms, doors, windows }`; `world` no longer
  saved. Saved door state gains `broken` (phase 2).
- **PLAYER STATE:** `enteredBuildings` (phase 1), `tankDrawn` (phase 7).
  `currentRoom` default `"home_living"`; keychain `house_key`.
- **ROOM SCHEMA:** `buildingId` (definition). The address rule's examples
  move to Lima; mid-stop `room` is "between A & B".
- **DOOR SCHEMA:** `lock` ("key" | "latch" | "bolt"), `inside`, `label`
  (definition); `broken` (saved).
- **WORLD DATA:** `BUILDING_TYPES`, the building instances, the Lima street
  data, `GRID_BEARING_DEG`, `LIMA_RIVER` polylines.
- **ITEM_REGISTRY / SPAWN_POOLS:** phase 6's table; pools `car_boot`,
  `car_glovebox`.
- **Removed:** `CROSSING_STANDBY_MIN`, `crossingLit()`, the `crossing`
  reader, `MAP_MIN_COL` … `MAP_MAX_ROW`, `WIRING.acorn`,
  `ACORN_HOUSE_ROOMS`, the template `doors`/`windows`, the retired
  backfills.

## In scope

- [ ] Phase 1: save split, `enteredBuildings`, old saves refused, backfills retired.
- [ ] Phase 2: `BUILDING_TYPES`, the builder, `lock`/`inside`/`label` on doors, starting locks, Force the door (`broken`), the four types.
- [ ] Phase 3: metre map, north arrow, slanted labels, river, rail, zoom ladder, crossing code removed.
- [ ] Phase 4: Lima's 777 stops and 1,008 links, exits, stop text.
- [ ] Phase 5: landmarks, named scenery, 428 generated homes, the player's row house and the start; the old town removed.
- [ ] Phase 6: items and pools.
- [ ] Phase 7: tanks.
- [ ] Phase 8: Walk to….

## Explicitly out of scope

- **Wiring any Lima building** (#289, #250): a later PATCH, since power
  definitions aren't saved.
- **The chalet and *PH* types** (#291's list): new issue.
- **Fog of war and other towns** (#293, #8); **bookmarks** (#292's open
  item).
- **The water network and the town tank** (#294's remainder), showers and
  toilets drawing water, contamination.
- **Garrafas as fuel** (#287, #259); **fuel at the petrol station**.
- **Cutting window bars**; forcing a bolted door or a window.
- **The other real businesses and institutions** as enterable buildings
  (#250, #285, #252–#257): they are PATCH content once phase 1 lands.
- **Trains, the bell ringing, anything at the Atucha plant** beyond its shut
  gate (#290).
- **Fishing** (Tom, 2026-09-27): with the Riverbank gone, no Lima stop is
  `fishable` and Go Fishing is never offered in this release. The first
  PATCH after it adds a riverside stop at the Balcón al río (the costanera).
  The fishing items and the action stay as they are.
- **#296's remainder** (above).

## Sections touched

- **WORLD DATA:** almost all of it (phases 2, 4, 5, 6, 7's type field).
- **PLAYER STATE:** phases 1, 5, 7.
- **WORLD INTERACTION:** door actions and `doorLabel()` (phase 2),
  `doMove()` (phase 1), `doFillAtSink()` and `waterRunning` (phase 7), the
  walk (phase 8).
- **SURVIVAL / TIME SIMULATION:** only `gridUp()`'s callers for water.
- **PERSISTENCE:** phase 1.
- **RENDERING:** the map (phase 3), the Here panel's door and walk actions
  (phases 2, 8), the map card (phase 8).
- The ARCHITECTURE comment and the LOCATIONS comment are rewritten for Lima
  (origin, frame, bearing).

This touches content and mechanics together, deliberately, as one release:
Tom's decision on #237. Each phase keeps to one side where it can.

## UI changes

- Map: Lima, slanted street names, a north arrow, the river near the plant,
  the railway dashed, a new zoom ladder, building markers for landmarks and
  named scenery, a tap card with **Walk here**.
- Here panel: four compass exits at most corners instead of eight; latch and
  bolt actions on doors from inside; **Force the front door** with a crowbar; **Walk to…**; "The tap is dry."
- The locator bar reads Lima addresses ("Calle 7, between Calle 10 &
  Calle 8").

## Dependencies / issue linkage

- Closes #295, #291, #237, #284, #294, #292. Part of #296 (stays open).
- Updates #220's hub: the power bundle moves to the next MINOR after this.
- #235 (crossing lights): its code is removed; the coding session comments
  there that it's gone.
- **File at the wrap:** the riverside stop at the Balcón al río (fishable;
  Tom agreed, the first PATCH after this); the chalet and *PH* types; the
  water network and
  the town tank; Walk to… bookmarks; #296's remainder if not already listed;
  anything else cut.
- Research gaps to leave marked, not fill: 184 unnamed street links (#288);
  the plant's gate position (placed at the road's end); the town tank.

## Open questions for Tom

None. Resolved by Tom on 2026-09-27, as proposed:

1. **Locked homes:** about 60% of generated homes start with the street
   door locked, and a crowbar can force a latch (phase 2).
2. **Fishing:** none in this release; a riverside stop at the Balcón al río
   is the first PATCH after it (Out of scope; filed at the wrap).
3. **The chalets:** the `casa` stands in until a `chalet` type is
   researched (phase 5; filed at the wrap).

## After implementation

Open one pull request carrying the version bump to the next MINOR, a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md` with `Implements:
handoffs/lima-release.md`, every design decision and question resolution in
its Notes, and `Closes #295`, `Closes #291`, `Closes #237`, `Closes #284`,
`Closes #294`, `Closes #292`, plus "Part of #296". Move this file to
`handoffs/archive/` in the same PR.

Before the PR, in Chromium (Playwright): a new game starts in the home's
living room; the front door unlocks by hand from inside; save, reload and
export/import round-trip a moved item, an opened container, a burnt-down
campfire and a drawn tank; a v0.9.4 save is refused; every `ashfallDev`
validator runs clean or with its known, listed warnings (unwired rooms); a
walk from home to the pharmacy costs the same minutes as its steps clicked
one by one.

---

## Appendix A — Lima's street data

Generated from OpenStreetMap (© OpenStreetMap contributors, ODbL; read
2026-09-26/27 through the OSM API) and Esri World Imagery, in the planning
session. **Secondary.** Coordinates are grid-frame metres (u, v), rounded;
origin 34.0447 S, 59.1961 W; +v is the grid's "up", 14° east of true north.

Processing: ways split at every junction; a corner stop at every junction,
a mid stop on every stretch longer than 75 m; stops joined by less than
25 m merged; the road north (Calle 111) with stops only at real features
and roads that lead somewhere (Tom); the FC Mitre with stops at Estación
Lima, the level crossings and the Atucha halt. One connected network.

**Stop type** sets its text; **surface** is per link. Surface rules:
paved (`p`) if OSM tags it tertiary or above, or it's Avenida 11, the Camino
a Baradero, the Acceso a Lima or the Camino Provincial, or it lies within
230 m of the plaza or within 70 m of the railway; dirt (`d`) within 110 m of
the built-up edge; gravel (`g`) otherwise; `r` is the railway. The
`barrio` type marks the Barrio Atucha's lanes.

### A.1 Street codes

Code `sn` is an unnamed street: 184 links whose name OSM doesn't have
(#288). Code `rail` is the track itself; `fwd` is the station forecourt.

```
c1 = Calle 1
c2 = Calle 2
c3 = Calle 3
c4 = Calle 4
c5 = Calle 5
c6 = Calle 6
c7 = Calle 7
c8 = Calle 8
c9 = Calle 9
sn = unnamed
acc = Acceso a Lima
c10 = Calle 10
c12 = Calle 12
c13 = Calle 13
c14 = Calle 14
c15 = Calle 15
c16 = Calle 16
c17 = Calle 17
c18 = Calle 18
c19 = Calle 19
c20 = Calle 20
c21 = Calle 21
c23 = Calle 23
c24 = Calle 24
c25 = Calle 25
c27 = Calle 27
c28 = Calle 28
c29 = Calle 29
c2b = Calle 2 Bis
c31 = Calle 31
c33 = Calle 33
c35 = Calle 35
c44 = Calle 44
c46 = Calle 46
c48 = Calle 48
c50 = Calle 50
c52 = Calle 52
c54 = Calle 54
c84 = Calle 84
c88 = Calle 88
c90 = Calle 90
dg2 = Diagonal 2
dg4 = Diagonal 4
fwd = (station forecourt)
av11 = Avenida 11
c101 = Calle 101
c103 = Calle 103
c105 = Calle 105
c107 = Calle 107
c109 = Calle 109
c111 = Calle 111
c113 = Calle 113
c115 = Calle 115
c117 = Calle 117
c119 = Calle 119
c121 = Calle 121
c123 = Calle 123
c16b = Calle 16 Bis
c18b = Calle 18 Bis
c90b = Calle 90 Bis
cbar = Camino a Baradero
cp01 = Camino Provincial Secundario 038-01
rail = FC Mitre (along the tracks)
dgmorgan = Diagonal Morgan
```

### A.2 Stops

`id u v type kind streets [flags]`. Kind: `c` corner, `m` mid, `r` rural,
`t` rail, `s` station. Streets: a corner's codes joined by `+`; a mid's
`street:crossA,crossB`. Flags: `plaza`, `crossing`, `L:<landmark>`,
`S:<scenery>`.

```
x_acc 51 -1021 core c acc
x_acc_av11_c20 53 -625 core c acc+av11+c20 L:petrol
x_acc_c24 52 -829 core c acc+c24
x_acc_c7 51 -912 core c acc+c7
x_av11_c10 56 -67 core c av11+c10 plaza
x_av11_c12 55 -176 core c av11+c12
x_av11_c14 54 -287 core c av11+c14
x_av11_c16 54 -401 core c av11+c16
x_av11_c18 53 -513 core c av11+c18
x_av11_c2_c4 57 277 core c av11+c2+c4
x_av11_c6 57 160 core c av11+c6
x_av11_c8 56 50 core c av11+c8
x_c1 621 131 core c c1+sn
x_c101 612 383 gravel c c101+sn
x_c101_2 610 720 gravel c c101+sn
x_c101_c44 612 438 gravel c c101+c44+sn
x_c101_c46 612 516 gravel c c101+c46+sn
x_c101_c48 613 587 gravel c c101+c48
x_c101_c50 611 674 gravel c c101+c50+sn
x_c101_c52 608 770 gravel c c101+c52
x_c101_c54 608 866 gravel c c101+c54
x_c103 505 385 gravel c c103+sn
x_c103_2 509 955 gravel c c103+sn
x_c103_c44 505 438 gravel c c103+c44
x_c103_c46 505 515 gravel c c103+c46
x_c103_c48 506 588 gravel c c103+c48
x_c103_c50 506 674 gravel c c103+c50
x_c103_c52 506 768 gravel c c103+c52
x_c103_c54 508 865 gravel c c103+c54
x_c105 413 386 gravel c c105+sn
x_c105_2 406 955 gravel c c105+sn
x_c105_c44 402 438 gravel c c105+c44
x_c105_c46 402 514 gravel c c105+c46
x_c105_c48 401 588 gravel c c105+c48
x_c105_c50 401 675 gravel c c105+c50
x_c105_c52 402 768 gravel c c105+c52
x_c105_c54 404 865 gravel c c105+c54
x_c107 303 954 gravel c c107+sn
x_c107_c2_c7 284 302 core c c107+c2+c7+sn crossing
x_c107_c44 295 443 gravel c c107+c44
x_c107_c46 297 513 gravel c c107+c46
x_c107_c48_dgmorgan 297 589 gravel c c107+c48+dgmorgan
x_c107_c50 298 678 gravel c c107+c50
x_c107_c52 299 768 gravel c c107+c52
x_c107_c54 301 865 gravel c c107+c54
x_c107_cbar 290 371 core c c107+cbar
x_c107_cp01 296 334 core c c107+cp01
x_c109 194 953 barrio c c109+sn
x_c109_c48 191 590 gravel c c109+c48
x_c109_c50_dgmorgan 191 677 gravel c c109+c50+dgmorgan
x_c109_c52 193 768 barrio c c109+c52
x_c109_c54 193 865 barrio c c109+c54
x_c10_c13 -58 -67 core c c10+c13
x_c10_c15 -171 -66 core c c10+c15
x_c10_c17 -283 -66 gravel c c10+c17
x_c10_c19 -398 -65 gravel c c10+c19
x_c10_c21 -511 -65 gravel c c10+c21
x_c10_c23 -607 -64 gravel c c10+c23
x_c10_c25 -702 -64 gravel c c10+c25
x_c10_c27 -798 -63 gravel c c10+c27
x_c10_c29 -894 -63 dirt c c10+c29
x_c10_c3 506 -69 gravel c c10+c3
x_c10_c5 397 -69 gravel c c10+c5
x_c10_c7 279 -68 core c c10+c7
x_c10_c9 168 -68 core c c10+c9
x_c111 66 1199 core c c111+sn
x_c111_2 66 1278 core c c111
x_c111_c48 64 591 core c c111+c48
x_c111_c50 69 676 core c c111+c50
x_c111_c52 42 752 barrio c c111+c52
x_c111_c52_dgmorgan 71 751 core c c111+c52+dgmorgan
x_c111_c54 68 869 barrio c c111+c54
x_c111_c84 -2 1138 barrio c c111+c84
x_c111_c84_2 67 1140 barrio c c111+c84
x_c111_c88 24 941 barrio c c111+c88
x_c111_c88_2 68 964 barrio c c111+c88+sn
x_c111_cbar 57 473 core c c111+cbar
x_c113 -52 740 gravel c c113+sn
x_c113_c48 -53 592 gravel c c113+c48
x_c113_c50 -52 676 gravel c c113+c50 L:almacen
x_c113_c52 -24 750 barrio c c113+c52
x_c113_c84 -68 1135 barrio c c113+c84
x_c113_c88 -46 940 barrio c c113+c88
x_c113_cbar -56 524 core c c113+cbar
x_c115 -125 741 barrio c c115+sn
x_c115_c50 -126 676 gravel c c115+c50
x_c115_c52 -92 749 barrio c c115+c52
x_c115_c84 -132 1136 barrio c c115+c84
x_c115_c88 -111 939 barrio c c115+c88
x_c115_cbar -130 555 core c c115+cbar
x_c117 -199 740 barrio c c117+sn
x_c117_c15_cp01_cbar -184 552 core c c117+c15+cp01+cbar
x_c117_c50 -200 677 gravel c c117+c50
x_c117_c52 -168 749 barrio c c117+c52
x_c117_c84 -201 1132 barrio c c117+c84
x_c117_c88 -184 937 barrio c c117+c88
x_c117_c90 -180 880 barrio c c117+c90
x_c117_c90b -174 811 barrio c c117+c90b
x_c119 -279 979 barrio c c119
x_c119_2 -280 1043 barrio c c119
x_c119_3 -283 1082 barrio c c119
x_c119_c50 -277 679 gravel c c119+c50
x_c119_c52 -290 745 gravel c c119+c52+sn
x_c119_c88 -278 936 barrio c c119+c88
x_c119_c90 -279 877 barrio c c119+c90
x_c119_c90b -278 810 barrio c c119+c90b
x_c119_cp01 -278 583 core c c119+cp01
x_c12 1169 -178 dirt c c12
x_c121_c50 -350 680 gravel c c121+c50
x_c121_c52 -350 744 gravel c c121+c52
x_c121_cp01 -350 615 core c c121+cp01
x_c123_c50 -425 681 gravel c c123+c50
x_c123_c52 -426 745 gravel c c123+c52
x_c123_cp01 -425 648 core c c123+cp01
x_c12_2 830 -177 dirt c c12+sn
x_c12_c13 -59 -175 core c c12+c13
x_c12_c15 -172 -175 core c c12+c15
x_c12_c17 -285 -175 gravel c c12+c17
x_c12_c19 -399 -175 gravel c c12+c19
x_c12_c21 -511 -174 gravel c c12+c21
x_c12_c23 -607 -174 gravel c c12+c23
x_c12_c25 -703 -174 gravel c c12+c25
x_c12_c27 -799 -174 gravel c c12+c27
x_c12_c29 -894 -173 dirt c c12+c29
x_c12_c3 506 -177 gravel c c12+c3
x_c12_c5 393 -176 gravel c c12+c5
x_c12_c7 279 -176 core c c12+c7
x_c12_c9 167 -176 core c c12+c9
x_c13_c14 -59 -287 core c c13+c14
x_c13_c16 -60 -400 core c c13+c16
x_c13_c18 -61 -512 core c c13+c18
x_c13_c2 -55 332 core c c13+c2
x_c13_c20 -62 -624 core c c13+c20
x_c13_c4 -55 273 core c c13+c4
x_c13_c6 -56 161 core c c13+c6
x_c13_c8 -57 50 core c c13+c8
x_c14 -1146 -283 dirt c c14+sn
x_c14_c15 -173 -286 gravel c c14+c15
x_c14_c17 -286 -286 gravel c c14+c17
x_c14_c19 -400 -285 gravel c c14+c19
x_c14_c21 -511 -285 gravel c c14+c21
x_c14_c23 -607 -285 gravel c c14+c23
x_c14_c25 -703 -284 gravel c c14+c25
x_c14_c27 -800 -284 gravel c c14+c27
x_c14_c29 -895 -284 gravel c c14+c29
x_c14_c3 506 -290 gravel c c14+c3
x_c14_c5 393 -289 gravel c c14+c5
x_c14_c7 279 -288 gravel c c14+c7
x_c14_c9 166 -288 core c c14+c9
x_c15_c16 -173 -399 gravel c c15+c16
x_c15_c17_c2 -252 393 core c c15+c17+c2
x_c15_c18 -174 -511 gravel c c15+c18
x_c15_c2 -171 382 core c c15+c2
x_c15_c20 -174 -623 gravel c c15+c20
x_c15_c4 -170 274 gravel c c15+c4
x_c15_c6 -170 162 gravel c c15+c6
x_c15_c8 -171 51 core c c15+c8
x_c15_dg4 -209 494 core c c15+dg4 crossing
x_c16 -758 -401 gravel c c16+sn
x_c16_2 -678 -392 gravel c c16+sn
x_c16_3 -708 -391 gravel c c16+sn
x_c16_c17 -287 -398 gravel c c16+c17
x_c16_c21 -511 -394 gravel c c16+c21
x_c16_c23 -610 -393 gravel c c16+c23
x_c16_c3 505 -405 gravel c c16+c3
x_c16_c5 392 -402 gravel c c16+c5
x_c16_c7 279 -403 gravel c c16+c7 L:mechanic
x_c16_c9 165 -402 gravel c c16+c9
x_c16b -1146 -342 dirt c c16b+sn
x_c16b_c27 -801 -348 gravel c c16b+c27
x_c16b_c29 -896 -347 gravel c c16b+c29
x_c16b_c5 393 -460 gravel c c16b+c5
x_c16b_c7 279 -457 gravel c c16b+c7
x_c17 -287 -437 gravel c c17+sn
x_c17_c18 -288 -511 gravel c c17+c18
x_c17_c20 -289 -622 gravel c c17+c20
x_c17_c24 -291 -819 gravel c c17+c24
x_c17_c28 -292 -1020 dirt c c17+c28
x_c17_c4 -280 275 gravel c c17+c4
x_c17_c6 -281 162 gravel c c17+c6
x_c17_c8 -282 52 gravel c c17+c8
x_c18_c5 394 -516 gravel c c18+c5
x_c18_c7 278 -514 gravel c c18+c7
x_c18_c9 164 -514 gravel c c18+c9
x_c18b_c5 394 -571 dirt c c18b+c5
x_c18b_c7 277 -569 gravel c c18b+c7
x_c19 -393 454 gravel c c19+sn
x_c19_c2 -393 388 gravel c c19+c2
x_c19_c4 -394 276 gravel c c19+c4
x_c19_c44 -392 504 gravel c c19+c44
x_c19_c6 -395 163 gravel c c19+c6
x_c19_c8 -396 52 gravel c c19+c8
x_c19_dg4 -392 572 core c c19+dg4
x_c1_c10 624 -70 gravel c c1+c10
x_c1_c12 622 -177 gravel c c1+c12
x_c1_c14 621 -289 gravel c c1+c14
x_c1_c16 620 -406 dirt c c1+c16
x_c1_c8 622 47 gravel c c1+c8
x_c2 -1011 395 dirt c c2+sn
x_c20 -677 -619 gravel c c20+sn
x_c20_2 -709 -618 gravel c c20+sn
x_c20_3 -1146 -609 gravel c c20+sn
x_c20_c21 -511 -621 gravel c c20+c21
x_c20_c23 -613 -620 gravel c c20+c23
x_c20_c27 -806 -616 gravel c c20+c27
x_c20_c29 -901 -614 gravel c c20+c29
x_c20_c5 387 -626 dirt c c20+c5
x_c20_c7 277 -626 gravel c c20+c7
x_c20_c9 163 -626 gravel c c20+c9
x_c21 -511 -435 gravel c c21+sn
x_c21_c4 -510 277 gravel c c21+c4
x_c21_c44 -509 504 gravel c c21+c44
x_c21_c46 -509 543 gravel c c21+c46
x_c21_c6 -510 164 gravel c c21+c6
x_c21_c8 -510 53 gravel c c21+c8
x_c21_dg4 -509 622 core c c21+dg4
x_c23_c4 -606 277 gravel c c23+c4
x_c23_c6 -606 165 gravel c c23+c6
x_c23_c8 -607 53 gravel c c23+c8
x_c24 -710 -807 dirt c c24+sn
x_c25_c4 -701 278 gravel c c25+c4
x_c25_c46 -700 545 gravel c c25+c46
x_c25_c48 -700 597 gravel c c25+c48
x_c25_c6 -701 166 gravel c c25+c6
x_c25_c8 -702 54 gravel c c25+c8
x_c25_dg4 -699 704 core c c25+dg4
x_c27 -804 -539 gravel c c27+sn
x_c27_2 -803 -471 gravel c c27+sn
x_c27_3 -802 -407 gravel c c27+sn
x_c27_4 -796 513 gravel c c27
x_c27_c4 -797 281 gravel c c27+c4
x_c27_c48 -795 598 gravel c c27+c48
x_c27_c6 -797 166 gravel c c27+c6
x_c27_c8 -798 54 gravel c c27+c8
x_c28 -714 -1008 dirt c c28+sn
x_c29 -900 -536 gravel c c29+sn
x_c29_2 -899 -470 gravel c c29+sn
x_c29_3 -897 -406 gravel c c29+sn
x_c29_c4 -891 279 gravel c c29+c4
x_c29_c48 -888 599 gravel c c29+c48
x_c29_c6 -892 167 gravel c c29+c6
x_c29_c8 -893 55 dirt c c29+c8
x_c29_dg4 -886 787 core c c29+dg4
x_c2_2 -1114 399 dirt c c2
x_c2_c21 -508 391 gravel c c2+c21
x_c2_c23 -604 390 gravel c c2+c23
x_c2_c25 -699 391 gravel c c2+c25
x_c2_c27 -797 392 gravel c c2+c27
x_c2_c29 -891 392 gravel c c2+c29
x_c2_c4 21 292 core c c2+c4
x_c2_c9 173 234 core c c2+c9
x_c2b -1113 467 dirt c c2b
x_c2b_c29 -890 466 gravel c c2b+c29
x_c3 510 182 core c c3+sn
x_c31 -1001 707 dirt c c31+sn
x_c31_c48 -1002 601 gravel c c31+c48
x_c31_dg4 -1000 836 core c c31+dg4
x_c33 -1056 709 dirt c c33+sn
x_c33_c48 -1058 601 dirt c c33+c48
x_c33_dg4 -1053 859 core c c33+dg4
x_c35 -1113 669 dirt c c35
x_c35_2 -1113 709 dirt c c35+sn
x_c35_3 -1112 813 dirt c c35
x_c35_c48 -1113 602 dirt c c35+c48
x_c35_dg4 -1112 885 core c c35+dg4
x_c3_c6 508 156 gravel c c3+c6
x_c3_c8 507 47 gravel c c3+c8
x_c4 -1016 280 dirt c c4+sn
x_c48 797 590 gravel c c48+sn
x_c48_2 956 590 dirt c c48+sn
x_c48_3 -956 600 gravel c c48+sn
x_c48_dg2 148 590 gravel c c48+dg2
x_c5 393 235 core c c5+sn
x_c52 -554 744 dirt c c52+sn
x_c5_c6 395 160 gravel c c5+c6
x_c5_c8 397 48 gravel c c5+c8
x_c6_c7 280 160 gravel c c6+c7
x_c6_c9 169 161 core c c6+c9
x_c7_c8 278 49 core c c7+c8
x_c8 701 45 gravel c c8+sn
x_c8_2 746 46 gravel c c8+sn
x_c8_c9 168 49 core c c8+c9
x_cbar_dg2 90 460 core c cbar+dg2
x_cp01 799 116 core c cp01
x_cp01_2 598 204 core c cp01+sn
x_cp01_3 -557 704 core c cp01+sn
x_cp01_4 -748 789 core c cp01
x_cp01_5 -921 866 core c cp01
x_dg4 -275 523 core c dg4+sn
x_sn -1146 -529 dirt c sn
x_sn_10 753 74 core c sn
x_sn_11 596 253 gravel c sn
x_sn_12 787 272 dirt c sn
x_sn_13 763 314 dirt c sn
x_sn_14 820 344 dirt c sn
x_sn_15 533 370 gravel c sn
x_sn_16 596 373 gravel c sn
x_sn_17 818 381 dirt c sn
x_sn_18 725 382 dirt c sn
x_sn_19 798 453 gravel c sn
x_sn_2 -709 -499 gravel c sn
x_sn_20 973 454 dirt c sn
x_sn_21 798 524 gravel c sn
x_sn_22 964 524 dirt c sn
x_sn_23 -954 648 gravel c sn
x_sn_24 797 657 gravel c sn
x_sn_25 948 657 dirt c sn
x_sn_26 937 721 dirt c sn
x_sn_27 797 722 gravel c sn
x_sn_28 -554 834 dirt c sn
x_sn_29 -405 834 dirt c sn
x_sn_3 -779 -497 gravel c sn
x_sn_30 331 963 gravel c sn
x_sn_31 539 963 gravel c sn
x_sn_32 228 964 barrio c sn
x_sn_33 440 964 gravel c sn
x_sn_34 598 1036 dirt c sn
x_sn_35 145 1037 barrio c sn
x_sn_36 230 1037 barrio c sn
x_sn_37 538 1038 gravel c sn
x_sn_38 439 1040 gravel c sn
x_sn_39 332 1041 gravel c sn
x_sn_4 -1146 -467 dirt c sn
x_sn_40 141 1111 gravel c sn
x_sn_41 228 1112 gravel c sn
x_sn_42 538 1113 dirt c sn
x_sn_43 440 1114 gravel c sn
x_sn_44 598 1114 dirt c sn
x_sn_45 333 1117 gravel c sn
x_sn_46 538 1195 dirt c sn
x_sn_47 228 1196 barrio c sn
x_sn_48 336 1196 dirt c sn
x_sn_49 439 1196 dirt c sn
x_sn_5 838 -417 dirt c sn
x_sn_6 -1146 -404 dirt c sn
x_sn_7 1165 -106 core c sn
x_sn_8 747 -31 gravel c sn
x_sn_9 830 40 core c sn
atucha_gate -2957 7845 rural r c111
atucha_halt -10000 4821 rail t -
estacion_lima 39 405 station s - L:goods_shed
fcm_crossing_11km -9621 4651 rail t - crossing
fcm_crossing_6km -5446 2817 rail t - crossing
m_acc_av11_c24 52 -727 core m acc:av11,c24
m_acc_c24_c7 52 -871 core m acc:c24,c7
m_acc_c7_sn 51 -966 core m acc:c7,sn
m_av11_acc_c18 53 -569 core m av11:acc,c18
m_av11_c10_c8 56 -9 core m av11:c10,c8 plaza S:parroquia
m_av11_c12_c10 55 -121 core m av11:c12,c10 plaza
m_av11_c14_c12 55 -231 core m av11:c14,c12
m_av11_c16_c14 54 -344 core m av11:c16,c14
m_av11_c18_c16 54 -457 core m av11:c18,c16
m_av11_c6_c4 57 216 core m av11:c6,c4 S:correo
m_av11_c8_c6 56 105 core m av11:c8,c6 S:banco_nacion S:school_ep9
m_c101_c54_c101 608 818 gravel m c101:c54,c101
m_c101_sn_c54 604 944 dirt m c101:sn,c54
m_c103_c46_c44 505 477 gravel m c103:c46,c44
m_c103_c48_c50 506 631 gravel m c103:c48,c50
m_c103_c50_c52 506 721 gravel m c103:c50,c52
m_c103_c52_c54 507 817 gravel m c103:c52,c54
m_c103_c54_sn 509 910 gravel m c103:c54,sn
m_c105_c46_c44 402 476 gravel m c105:c46,c44
m_c105_c50_c48 401 631 gravel m c105:c50,c48
m_c105_c52_c50 402 721 gravel m c105:c52,c50
m_c105_c54_c52 404 816 gravel m c105:c54,c52
m_c105_sn_c54 405 910 gravel m c105:sn,c54
m_c107_c46_c48 297 551 gravel m c107:c46,c48
m_c107_c48_c50 297 633 gravel m c107:c48,c50
m_c107_c50_c52 298 723 gravel m c107:c50,c52
m_c107_c52_c54 300 817 gravel m c107:c52,c54
m_c107_c54_sn 302 909 gravel m c107:c54,sn
m_c109_c50_c48 191 633 gravel m c109:c50,c48
m_c109_c52_c50 192 723 gravel m c109:c52,c50
m_c109_c54_c52 193 816 barrio m c109:c54,c52
m_c109_sn_c54 193 909 barrio m c109:sn,c54
m_c10_av11_c9 112 -68 core m c10:av11,c9 plaza
m_c10_c13_av11 -1 -67 core m c10:c13,av11 plaza
m_c10_c15_c13 -115 -67 core m c10:c15,c13
m_c10_c17_c15 -227 -66 gravel m c10:c17,c15
m_c10_c19_c17 -341 -66 gravel m c10:c19,c17
m_c10_c21_c19 -454 -65 gravel m c10:c21,c19
m_c10_c23_c21 -559 -65 gravel m c10:c23,c21
m_c10_c25_c23 -655 -64 gravel m c10:c25,c23
m_c10_c27_c25 -750 -64 gravel m c10:c27,c25
m_c10_c29_c27 -846 -63 dirt m c10:c29,c27
m_c10_c3_c1 565 -70 gravel m c10:c3,c1
m_c10_c5_c3 452 -69 gravel m c10:c5,c3
m_c10_c7_c5 338 -69 gravel m c10:c7,c5
m_c10_c9_c7 223 -68 core m c10:c9,c7
m_c111_c48_cbar 61 532 core m c111:c48,cbar
m_c111_c50_c48 67 634 core m c111:c50,c48
m_c111_c52_c88 30 846 barrio m c111:c52,c88
m_c111_c54_dgmorgan 70 821 barrio m c111:c54,dgmorgan
m_c111_c84_sn 67 1052 barrio m c111:c84,sn
m_c111_c88_c84 21 1041 barrio m c111:c88,c84
m_c111_sn_sn 66 1239 core m c111:sn,sn
m_c113_c50_c48 -53 634 gravel m c113:c50,c48
m_c113_c52_c88 -41 844 barrio m c113:c52,c88
m_c113_c88_c84 -50 1038 barrio m c113:c88,c84
m_c115_c84_c88 -114 1038 barrio m c115:c84,c88
m_c115_c88_c52 -108 843 barrio m c115:c88,c52
m_c115_cbar_c50 -128 615 gravel m c115:cbar,c50
m_c117_c50_cp01 -202 615 gravel m c117:c50,cp01
m_c117_c88_c84 -188 1035 barrio m c117:c88,c84 S:club_barrio_atucha
m_c119_cp01_c50 -278 631 gravel m c119:cp01,c50
m_c12_av11_c13 -2 -175 core m c12:av11,c13
m_c12_c13_c15 -115 -175 core m c12:c13,c15 L:comisaria
m_c12_c15_c17 -228 -175 gravel m c12:c15,c17
m_c12_c17_c19 -342 -175 gravel m c12:c17,c19
m_c12_c19_c21 -455 -174 gravel m c12:c19,c21
m_c12_c1_c3 564 -177 gravel m c12:c1,c3
m_c12_c21_c23 -559 -174 gravel m c12:c21,c23
m_c12_c23_c25 -655 -174 gravel m c12:c23,c25
m_c12_c25_c27 -751 -174 gravel m c12:c25,c27
m_c12_c27_c29 -847 -174 dirt m c12:c27,c29
m_c12_c3_c5 450 -176 gravel m c12:c3,c5
m_c12_c5_c7 336 -176 gravel m c12:c5,c7
m_c12_c7_c9 223 -176 core m c12:c7,c9
m_c12_c9_av11 111 -176 core m c12:c9,av11
m_c12_sn_c1 726 -177 gravel m c12:sn,c1
m_c12_sn_sn 1000 -178 dirt m c12:sn,sn
m_c13_c10_c12 -58 -121 core m c13:c10,c12
m_c13_c12_c14 -59 -231 core m c13:c12,c14
m_c13_c14_c16 -60 -343 core m c13:c14,c16
m_c13_c16_c18 -61 -456 core m c13:c16,c18
m_c13_c18_c20 -62 -568 core m c13:c18,c20
m_c13_c4_c6 -56 217 core m c13:c4,c6
m_c13_c6_c8 -56 106 core m c13:c6,c8
m_c13_c8_c10 -57 -8 core m c13:c8,c10
m_c14_av11_c13 -2 -287 gravel m c14:av11,c13
m_c14_c13_c15 -116 -287 gravel m c14:c13,c15
m_c14_c15_c17 -229 -286 gravel m c14:c15,c17
m_c14_c17_c19 -343 -286 gravel m c14:c17,c19
m_c14_c19_c21 -455 -285 gravel m c14:c19,c21
m_c14_c1_c3 563 -290 gravel m c14:c1,c3
m_c14_c21_c23 -559 -285 gravel m c14:c21,c23
m_c14_c23_c25 -655 -284 gravel m c14:c23,c25
m_c14_c25_c27 -752 -284 gravel m c14:c25,c27
m_c14_c27_c29 -848 -284 gravel m c14:c27,c29
m_c14_c29_sn -1020 -283 dirt m c14:c29,sn
m_c14_c3_c5 449 -290 gravel m c14:c3,c5
m_c14_c5_c7 336 -289 gravel m c14:c5,c7
m_c14_c7_c9 223 -288 gravel m c14:c7,c9
m_c14_c9_av11 110 -287 gravel m c14:c9,av11
m_c15_c10_c12 -172 -121 core m c15:c10,c12
m_c15_c12_c14 -172 -231 gravel m c15:c12,c14
m_c15_c14_c16 -173 -342 gravel m c15:c14,c16
m_c15_c16_c18 -173 -455 gravel m c15:c16,c18
m_c15_c18_c20 -174 -567 gravel m c15:c18,c20
m_c15_c2_c4 -170 325 gravel m c15:c2,c4
m_c15_c4_c6 -170 218 gravel m c15:c4,c6
m_c15_c6_c8 -171 106 gravel m c15:c6,c8
m_c15_c8_c10 -171 -8 core m c15:c8,c10
m_c16_av11_c13 -3 -400 gravel m c16:av11,c13
m_c16_c13_c15 -117 -399 gravel m c16:c13,c15
m_c16_c15_c17 -230 -398 gravel m c16:c15,c17
m_c16_c17_c21 -399 -396 gravel m c16:c17,c21
m_c16_c1_c3 562 -405 dirt m c16:c1,c3
m_c16_c21_c23 -561 -394 gravel m c16:c21,c23
m_c16_c3_c5 448 -403 gravel m c16:c3,c5
m_c16_c5_c7 336 -402 gravel m c16:c5,c7
m_c16_c7_c9 222 -402 gravel m c16:c7,c9
m_c16_c9_av11 109 -401 gravel m c16:c9,av11
m_c16b_c29_c27 -848 -348 gravel m c16b:c29,c27
m_c16b_c5_c7 336 -459 gravel m c16b:c5,c7
m_c16b_sn_c29 -1021 -345 gravel m c16b:sn,c29
m_c17_c10_c8 -283 -7 gravel m c17:c10,c8
m_c17_c12_c10 -284 -120 gravel m c17:c12,c10
m_c17_c14_c12 -285 -230 gravel m c17:c14,c12
m_c17_c16_c14 -286 -342 gravel m c17:c16,c14
m_c17_c20_c18 -288 -566 gravel m c17:c20,c18
m_c17_c24_c20 -290 -721 gravel m c17:c24,c20
m_c17_c28_c24 -291 -920 dirt m c17:c28,c24
m_c17_c4_c2 -281 333 gravel m c17:c4,c2
m_c17_c6_c4 -281 219 gravel m c17:c6,c4
m_c17_c8_c6 -282 107 gravel m c17:c8,c6
m_c18_av11_c9 109 -513 gravel m c18:av11,c9
m_c18_c13_av11 -4 -513 gravel m c18:c13,av11
m_c18_c15_c13 -118 -512 gravel m c18:c15,c13
m_c18_c17_c15 -231 -511 gravel m c18:c17,c15
m_c18_c7_c5 336 -515 gravel m c18:c7,c5
m_c18_c9_c7 221 -514 gravel m c18:c9,c7
m_c18b_c5_c7 335 -570 dirt m c18b:c5,c7
m_c19_c10_c8 -397 -7 gravel m c19:c10,c8
m_c19_c12_c10 -398 -120 gravel m c19:c12,c10
m_c19_c14_c12 -399 -230 gravel m c19:c14,c12
m_c19_c4_c2 -394 332 gravel m c19:c4,c2
m_c19_c6_c4 -395 220 gravel m c19:c6,c4
m_c19_c8_c6 -396 108 gravel m c19:c8,c6
m_c1_c10_c12 623 -123 gravel m c1:c10,c12
m_c1_c12_c14 621 -233 gravel m c1:c12,c14
m_c1_c14_c16 620 -348 dirt m c1:c14,c16
m_c1_c8_c10 623 -12 gravel m c1:c8,c10
m_c1_sn_c8 622 89 gravel m c1:sn,c8
m_c20_acc_c13 -5 -624 core m c20:acc,c13
m_c20_c13_c15 -118 -624 gravel m c20:c13,c15
m_c20_c15_c17 -232 -623 gravel m c20:c15,c17
m_c20_c17_c21 -400 -622 gravel m c20:c17,c21
m_c20_c21_c23 -562 -620 gravel m c20:c21,c23
m_c20_c27_c29 -853 -615 gravel m c20:c27,c29
m_c20_c29_sn -1024 -611 gravel m c20:c29,sn
m_c20_c5_c7 332 -626 dirt m c20:c5,c7
m_c20_c7_c9 220 -626 gravel m c20:c7,c9
m_c20_c9_acc 108 -625 gravel m c20:c9,acc
m_c20_sn_c27 -757 -617 dirt m c20:sn,c27
m_c21_c10_c12 -511 -120 gravel m c21:c10,c12
m_c21_c12_c14 -511 -230 gravel m c21:c12,c14
m_c21_c14_c16 -511 -340 gravel m c21:c14,c16
m_c21_c2_c4 -509 334 gravel m c21:c2,c4
m_c21_c44_c2 -509 447 gravel m c21:c44,c2
m_c21_c4_c6 -510 220 gravel m c21:c4,c6
m_c21_c6_c8 -510 109 gravel m c21:c6,c8
m_c21_c8_c10 -510 -6 gravel m c21:c8,c10
m_c21_dg4_c46 -509 583 gravel m c21:dg4,c46
m_c21_sn_c20 -511 -528 gravel m c21:sn,c20
m_c23_c10_c8 -607 -6 gravel m c23:c10,c8
m_c23_c12_c10 -607 -119 gravel m c23:c12,c10
m_c23_c14_c12 -607 -229 gravel m c23:c14,c12
m_c23_c16_c14 -610 -339 gravel m c23:c16,c14
m_c23_c20_c16 -612 -506 gravel m c23:c20,c16
m_c23_c4_c2 -605 334 gravel m c23:c4,c2
m_c23_c6_c4 -606 221 gravel m c23:c6,c4
m_c23_c8_c6 -606 109 gravel m c23:c8,c6
m_c24_acc_c17 -119 -824 gravel m c24:acc,c17
m_c24_c17_sn -500 -813 gravel m c24:c17,sn
m_c25_c10_c12 -703 -119 gravel m c25:c10,c12
m_c25_c12_c14 -703 -229 gravel m c25:c12,c14
m_c25_c2_c4 -700 335 gravel m c25:c2,c4
m_c25_c46_c2 -699 468 gravel m c25:c46,c2
m_c25_c4_c6 -701 222 gravel m c25:c4,c6
m_c25_c6_c8 -702 110 gravel m c25:c6,c8
m_c25_c8_c10 -702 -5 gravel m c25:c8,c10
m_c25_dg4_c48 -699 650 gravel m c25:dg4,c48
m_c27_c10_c8 -798 -5 gravel m c27:c10,c8
m_c27_c12_c10 -799 -119 gravel m c27:c12,c10
m_c27_c14_c12 -800 -229 gravel m c27:c14,c12
m_c27_c20_sn -805 -577 gravel m c27:c20,sn
m_c27_c48_sn -796 556 gravel m c27:c48,sn
m_c27_c4_c2 -797 336 gravel m c27:c4,c2
m_c27_c6_c4 -797 224 gravel m c27:c6,c4
m_c27_c8_c6 -797 110 gravel m c27:c8,c6
m_c28_c17_sn -503 -1014 dirt m c28:c17,sn
m_c29_c10_c8 -893 -4 dirt m c29:c10,c8
m_c29_c12_c10 -894 -118 dirt m c29:c12,c10
m_c29_c14_c12 -895 -229 dirt m c29:c14,c12
m_c29_c20_sn -901 -575 gravel m c29:c20,sn
m_c29_c2b_c48 -889 533 gravel m c29:c2b,c48
m_c29_c48_dg4 -887 693 gravel m c29:c48,dg4
m_c29_c4_c2 -891 336 gravel m c29:c4,c2
m_c29_c6_c4 -891 223 gravel m c29:c6,c4
m_c29_c8_c6 -892 111 dirt m c29:c8,c6
m_c2_av11_c9 113 252 core m c2:av11,c9
m_c2_c13_c15 -113 357 core m c2:c13,c15
m_c2_c13_sn -17 307 core m c2:c13,sn
m_c2_c15_c13 -113 349 core m c2:c15,c13
m_c2_c15_c15 -210 391 core m c2:c15,c15
m_c2_c15_c15_2 -206 398 core m c2:c15,c15
m_c2_c17_c19 -337 390 gravel m c2:c17,c19
m_c2_c19_c21 -451 390 gravel m c2:c19,c21
m_c2_c21_c23 -556 390 gravel m c2:c21,c23
m_c2_c23_c25 -651 391 gravel m c2:c23,c25
m_c2_c25_c27 -748 392 gravel m c2:c25,c27
m_c2_c27_c29 -844 392 gravel m c2:c27,c29
m_c2_c29_sn -951 393 dirt m c2:c29,sn
m_c2_c7_c9 243 218 core m c2:c7,c9
m_c2_c9_av11 116 259 core m c2:c9,av11
m_c2_c9_c7 247 208 core m c2:c9,c7
m_c2_sn_c13 -16 316 core m c2:sn,c13
m_c2_sn_sn -1062 397 dirt m c2:sn,sn
m_c2b_c29_sn -1002 467 dirt m c2b:c29,sn
m_c31_c48_sn -1002 654 gravel m c31:c48,sn
m_c31_sn_dg4 -1001 772 dirt m c31:sn,dg4
m_c33_dg4_sn -1056 784 dirt m c33:dg4,sn
m_c33_sn_c48 -1057 655 dirt m c33:sn,c48
m_c35_sn_sn -1112 761 dirt m c35:sn,sn
m_c3_c10_c12 506 -123 gravel m c3:c10,c12
m_c3_c12_c14 506 -233 gravel m c3:c12,c14
m_c3_c14_c16 505 -348 gravel m c3:c14,c16
m_c3_c6_c8 507 102 gravel m c3:c6,c8
m_c3_c8_c10 507 -11 gravel m c3:c8,c10
m_c44_c105_c107 348 441 gravel m c44:c105,c107
m_c44_c19_c21 -451 504 gravel m c44:c19,c21
m_c44_sn_c105 453 438 gravel m c44:sn,c105
m_c44_sn_sn 558 438 gravel m c44:sn,sn
m_c46_c105_sn 453 515 gravel m c46:c105,sn
m_c46_c107_c105 349 514 gravel m c46:c107,c105
m_c46_c21_c25 -604 544 gravel m c46:c21,c25
m_c46_sn_sn 558 515 gravel m c46:sn,sn
m_c48_c101_c103 559 587 gravel m c48:c101,c103
m_c48_c103_c105 453 588 gravel m c48:c103,c105
m_c48_c105_c107 349 588 gravel m c48:c105,c107
m_c48_c107_c109 244 589 gravel m c48:c107,c109
m_c48_c111_c113 5 592 gravel m c48:c111,c113
m_c48_c25_c27 -748 597 gravel m c48:c25,c27
m_c48_c27_c29 -842 598 gravel m c48:c27,c29
m_c48_dg2_c111 106 590 gravel m c48:dg2,c111
m_c48_sn_c101 705 591 gravel m c48:sn,c101
m_c48_sn_sn 877 590 dirt m c48:sn,sn
m_c4_c13_c15 -112 274 gravel m c4:c13,c15
m_c4_c15_c17 -225 274 gravel m c4:c15,c17
m_c4_c17_c19 -337 275 gravel m c4:c17,c19
m_c4_c19_c21 -452 276 gravel m c4:c19,c21
m_c4_c21_c23 -558 277 gravel m c4:c21,c23
m_c4_c23_c25 -654 278 gravel m c4:c23,c25
m_c4_c25_c27 -749 279 gravel m c4:c25,c27
m_c4_c27_c29 -844 280 gravel m c4:c27,c29
m_c4_c29_sn -953 280 dirt m c4:c29,sn
m_c4_sn_c13 -17 273 gravel m c4:sn,c13
m_c50_c101_c103 559 674 gravel m c50:c101,c103
m_c50_c103_c105 453 675 gravel m c50:c103,c105
m_c50_c105_c107 349 677 gravel m c50:c105,c107
m_c50_c107_c109 245 678 gravel m c50:c107,c109
m_c50_c109_c111 130 679 gravel m c50:c109,c111
m_c50_c111_c113 8 676 gravel m c50:c111,c113
m_c50_c117_c119 -239 678 gravel m c50:c117,c119
m_c50_c121_c123 -388 680 gravel m c50:c121,c123
m_c52_c101_c103 557 769 gravel m c52:c101,c103
m_c52_c103_c105 454 768 gravel m c52:c103,c105
m_c52_c105_c107 351 768 gravel m c52:c105,c107
m_c52_c107_c109 246 768 gravel m c52:c107,c109
m_c52_c109_dgmorgan 137 768 gravel m c52:c109,dgmorgan
m_c52_c115_c117 -130 749 barrio m c52:c115,c117
m_c52_c117_c119 -223 748 barrio m c52:c117,c119
m_c52_c121_c123 -388 745 gravel m c52:c121,c123
m_c52_c123_sn -490 745 dirt m c52:c123,sn
m_c54_c103_sn 558 865 gravel m c54:c103,sn
m_c54_c105_c103 456 865 gravel m c54:c105,c103
m_c54_c107_c105 353 865 gravel m c54:c107,c105
m_c54_c109_c107 247 865 gravel m c54:c109,c107
m_c54_c111_c109 130 867 barrio m c54:c111,c109
m_c5_c10_c12 395 -123 gravel m c5:c10,c12
m_c5_c12_c14 393 -233 gravel m c5:c12,c14
m_c5_c14_c16 392 -346 gravel m c5:c14,c16
m_c5_c6_c8 396 104 gravel m c5:c6,c8
m_c5_c8_c10 397 -10 gravel m c5:c8,c10
m_c6_av11_c9 113 160 core m c6:av11,c9
m_c6_c13_av11 0 160 core m c6:c13,av11 S:hospital
m_c6_c15_c13 -113 161 gravel m c6:c15,c13
m_c6_c17_c15 -226 162 gravel m c6:c17,c15
m_c6_c19_c17 -338 163 gravel m c6:c19,c17
m_c6_c21_c19 -453 164 gravel m c6:c21,c19
m_c6_c23_c21 -558 165 gravel m c6:c23,c21
m_c6_c25_c23 -654 165 gravel m c6:c25,c23
m_c6_c27_c25 -749 166 gravel m c6:c27,c25
m_c6_c29_c27 -844 167 gravel m c6:c29,c27
m_c6_c5_c3 451 158 gravel m c6:c5,c3
m_c6_c7_c5 337 160 gravel m c6:c7,c5
m_c6_c9_c7 224 161 gravel m c6:c9,c7
m_c7_acc_c20 192 -783 dirt m c7:acc,c20 S:bomberos
m_c7_c10_c8 279 -10 gravel m c7:c10,c8 L:pharmacy
m_c7_c12_c10 279 -122 gravel m c7:c12,c10
m_c7_c14_c12 279 -232 gravel m c7:c14,c12
m_c7_c16_c14 279 -345 gravel m c7:c16,c14
m_c7_c6_c2 281 223 gravel m c7:c6,c2
m_c7_c8_c6 279 104 gravel m c7:c8,c6
m_c88_c117_c119 -231 937 barrio m c88:c117,c119
m_c8_av11_c13 0 50 core m c8:av11,c13 S:delegacion
m_c8_c13_c15 -114 51 core m c8:c13,c15
m_c8_c15_c17 -227 51 gravel m c8:c15,c17
m_c8_c17_c19 -339 52 gravel m c8:c17,c19
m_c8_c19_c21 -453 53 gravel m c8:c19,c21
m_c8_c1_c3 565 47 gravel m c8:c1,c3
m_c8_c21_c23 -558 53 gravel m c8:c21,c23
m_c8_c23_c25 -654 54 gravel m c8:c23,c25
m_c8_c25_c27 -750 54 gravel m c8:c25,c27
m_c8_c27_c29 -845 55 gravel m c8:c27,c29
m_c8_c3_c5 452 48 gravel m c8:c3,c5
m_c8_c5_c7 338 48 gravel m c8:c5,c7
m_c8_c7_c9 223 49 core m c8:c7,c9
m_c8_c9_av11 112 49 core m c8:c9,av11
m_c90_c119_c117 -229 879 barrio m c90:c119,c117
m_c90b_c117_c119 -226 810 barrio m c90b:c117,c119 L:home
m_c9_c10_c12 167 -122 core m c9:c10,c12
m_c9_c12_c14 166 -232 core m c9:c12,c14
m_c9_c14_c16 165 -345 gravel m c9:c14,c16
m_c9_c16_c18 165 -458 gravel m c9:c16,c18
m_c9_c18_c20 164 -570 gravel m c9:c18,c20
m_c9_c6_c8 169 105 core m c9:c6,c8
m_c9_c8_c10 168 -9 core m c9:c8,c10
m_cbar_c113_c111 1 499 core m cbar:c113,c111
m_cbar_c115_c113 -93 540 core m cbar:c115,c113
m_cbar_dg2_c107 191 416 core m cbar:dg2,c107 L:corralon
m_cp01_c107_sn 447 269 core m cp01:c107,sn
m_cp01_c117_c119 -241 568 core m cp01:c117,c119
m_cp01_c119_c121 -314 599 core m cp01:c119,c121
m_cp01_c121_c123 -388 631 core m cp01:c121,c123
m_cp01_c123_sn -491 676 core m cp01:c123,sn
m_cp01_sn_sn 699 160 core m cp01:sn,sn
m_cp01_sn_sn_2 -652 746 core m cp01:sn,sn
m_cp01_sn_sn_3 -834 827 core m cp01:sn,sn
m_dg2_cbar_c48 119 525 gravel m dg2:cbar,c48
m_dg4_c19_c21 -450 597 core m dg4:c19,c21
m_dg4_c21_c25 -604 663 core m dg4:c21,c25
m_dg4_c25_c29 -792 745 core m dg4:c25,c29
m_dg4_c29_c31 -943 812 core m dg4:c29,c31
m_dg4_sn_c19 -333 547 core m dg4:sn,c19
m_dgmorgan_c109_c107 244 633 gravel m dgmorgan:c109,c107
m_dgmorgan_c52_c109 136 723 gravel m dgmorgan:c52,c109
m_sn_c105_c103 458 955 gravel m sn:c105,c103
m_sn_c105_sn 459 385 gravel m sn:c105,sn
m_sn_c107_c105 355 954 gravel m sn:c107,c105
m_sn_c109_c107 248 953 gravel m sn:c109,c107
m_sn_c111_sn 147 1197 barrio m sn:c111,sn
m_sn_c119_c117 -239 740 barrio m sn:c119,c117
m_sn_c12_sn 834 -297 dirt m sn:c12,sn
m_sn_c16_c20 -677 -505 gravel m sn:c16,c20
m_sn_c16_sn -758 -449 gravel m sn:c16,sn
m_sn_c16_sn_2 -709 -445 gravel m sn:c16,sn
m_sn_c19_dg4 -302 453 gravel m sn:c19,dg4
m_sn_c1_sn 687 102 core m sn:c1,sn
m_sn_c20_c24 -710 -713 dirt m sn:c20,c24
m_sn_c21_c17 -399 -436 gravel m sn:c21,c17
m_sn_c24_c28 -712 -908 dirt m sn:c24,c28
m_sn_c29_c27 -852 -538 gravel m sn:c29,c27
m_sn_c29_c27_2 -851 -471 gravel m sn:c29,c27
m_sn_c29_c27_3 -850 -407 gravel m sn:c29,c27
m_sn_c2_c4 -1013 337 dirt m sn:c2,c4
m_sn_c2_c5 336 260 core m sn:c2,c5
m_sn_c3_c1 566 157 core m sn:c3,c1
m_sn_c52_sn -554 789 dirt m sn:c52,sn
m_sn_c5_c3 452 208 core m sn:c5,c3
m_sn_c8_c8 697 -31 gravel m sn:c8,c8
m_sn_c8_sn 747 7 gravel m sn:c8,sn
m_sn_sn_c101 704 658 gravel m sn:sn,c101
m_sn_sn_c101_2 703 721 gravel m sn:sn,c101
m_sn_sn_c105 369 963 gravel m sn:sn,c105
m_sn_sn_c107 266 964 gravel m sn:sn,c107
m_sn_sn_c109 135 952 barrio m sn:sn,c109
m_sn_sn_c109_2 136 964 barrio m sn:sn,c109
m_sn_sn_c12 830 -69 gravel m sn:sn,c12
m_sn_sn_c20 -1146 -569 dirt m sn:sn,c20
m_sn_sn_c20_2 -709 -558 gravel m sn:sn,c20
m_sn_sn_c29 -1023 -532 gravel m sn:sn,c29
m_sn_sn_c29_2 -1022 -468 gravel m sn:sn,c29
m_sn_sn_c29_3 -1022 -405 gravel m sn:sn,c29
m_sn_sn_sn 998 -33 core m sn:sn,sn
m_sn_sn_sn_10 885 454 dirt m sn:sn,sn
m_sn_sn_sn_11 705 524 gravel m sn:sn,sn
m_sn_sn_sn_12 881 524 gravel m sn:sn,sn
m_sn_sn_sn_13 872 657 dirt m sn:sn,sn
m_sn_sn_sn_14 867 722 dirt m sn:sn,sn
m_sn_sn_sn_15 -480 834 dirt m sn:sn,sn
m_sn_sn_sn_16 539 1001 gravel m sn:sn,sn
m_sn_sn_sn_17 332 1002 gravel m sn:sn,sn
m_sn_sn_sn_18 440 1002 gravel m sn:sn,sn
m_sn_sn_sn_19 187 1037 barrio m sn:sn,sn
m_sn_sn_sn_2 791 57 core m sn:sn,sn
m_sn_sn_sn_20 489 1039 gravel m sn:sn,sn
m_sn_sn_sn_21 281 1040 gravel m sn:sn,sn
m_sn_sn_sn_22 386 1041 gravel m sn:sn,sn
m_sn_sn_sn_23 598 1075 dirt m sn:sn,sn
m_sn_sn_sn_24 333 1079 gravel m sn:sn,sn
m_sn_sn_sn_25 185 1112 gravel m sn:sn,sn
m_sn_sn_sn_26 489 1113 gravel m sn:sn,sn
m_sn_sn_sn_27 387 1116 gravel m sn:sn,sn
m_sn_sn_sn_28 280 1119 gravel m sn:sn,sn
m_sn_sn_sn_29 228 1154 dirt m sn:sn,sn
m_sn_sn_sn_3 533 291 gravel m sn:sn,sn
m_sn_sn_sn_30 538 1154 dirt m sn:sn,sn
m_sn_sn_sn_31 439 1155 dirt m sn:sn,sn
m_sn_sn_sn_32 334 1157 dirt m sn:sn,sn
m_sn_sn_sn_33 597 1180 dirt m sn:sn,sn
m_sn_sn_sn_34 282 1196 dirt m sn:sn,sn
m_sn_sn_sn_35 387 1196 dirt m sn:sn,sn
m_sn_sn_sn_36 488 1196 dirt m sn:sn,sn
m_sn_sn_sn_4 647 301 dirt m sn:sn,sn
m_sn_sn_sn_5 596 313 gravel m sn:sn,sn
m_sn_sn_sn_6 935 381 dirt m sn:sn,sn
m_sn_sn_sn_7 668 382 gravel m sn:sn,sn
m_sn_sn_sn_8 558 384 gravel m sn:sn,sn
m_sn_sn_sn_9 705 453 gravel m sn:sn,sn
r111_2752m -169 3790 rural r c111
r111_7180m -2169 7269 rural r c111
r111_7334m -2307 7315 rural r c111
r111_767m -58 1810 rural r c111
r111_973m -77 2014 rural r c111
r111_papermill -284 5846 rural r c111
```

### A.3 Links

`a b street surface`. Every link is walkable both ways.

```
estacion_lima x_c107_c2_c7 rail r
estacion_lima x_c111_cbar fwd p
estacion_lima x_c15_dg4 rail r
fcm_crossing_11km atucha_halt rail r
fcm_crossing_6km fcm_crossing_11km rail r
m_acc_av11_c24 x_acc_c24 acc p
m_acc_c24_c7 x_acc_c7 acc p
m_acc_c7_sn x_acc acc p
m_av11_acc_c18 x_av11_c18 av11 p
m_av11_c10_c8 x_av11_c8 av11 p
m_av11_c12_c10 x_av11_c10 av11 p
m_av11_c14_c12 x_av11_c12 av11 p
m_av11_c16_c14 x_av11_c14 av11 p
m_av11_c18_c16 x_av11_c16 av11 p
m_av11_c6_c4 x_av11_c2_c4 av11 p
m_av11_c8_c6 x_av11_c6 av11 p
m_c101_c54_c101 x_c101_c52 c101 g
m_c101_sn_c54 x_c101_c54 c101 d
m_c103_c46_c44 x_c103_c44 c103 g
m_c103_c48_c50 x_c103_c50 c103 g
m_c103_c50_c52 x_c103_c52 c103 g
m_c103_c52_c54 x_c103_c54 c103 g
m_c103_c54_sn x_c103_2 c103 g
m_c105_c46_c44 x_c105_c44 c105 g
m_c105_c50_c48 x_c105_c48 c105 g
m_c105_c52_c50 x_c105_c50 c105 g
m_c105_c54_c52 x_c105_c52 c105 g
m_c105_sn_c54 x_c105_c54 c105 g
m_c107_c46_c48 x_c107_c48_dgmorgan c107 g
m_c107_c48_c50 x_c107_c50 c107 g
m_c107_c50_c52 x_c107_c52 c107 g
m_c107_c52_c54 x_c107_c54 c107 g
m_c107_c54_sn x_c107 c107 g
m_c109_c50_c48 x_c109_c48 c109 g
m_c109_c52_c50 x_c109_c50_dgmorgan c109 g
m_c109_c54_c52 x_c109_c52 c109 g
m_c109_sn_c54 x_c109_c54 c109 g
m_c10_av11_c9 x_c10_c9 c10 p
m_c10_c13_av11 x_av11_c10 c10 p
m_c10_c15_c13 x_c10_c13 c10 p
m_c10_c17_c15 x_c10_c15 c10 g
m_c10_c19_c17 x_c10_c17 c10 g
m_c10_c21_c19 x_c10_c19 c10 g
m_c10_c23_c21 x_c10_c21 c10 g
m_c10_c25_c23 x_c10_c23 c10 g
m_c10_c27_c25 x_c10_c25 c10 g
m_c10_c29_c27 x_c10_c27 c10 d
m_c10_c3_c1 x_c1_c10 c10 g
m_c10_c5_c3 x_c10_c3 c10 g
m_c10_c7_c5 x_c10_c5 c10 g
m_c10_c9_c7 x_c10_c7 c10 p
m_c111_c48_cbar x_c111_cbar c111 p
m_c111_c50_c48 x_c111_c48 c111 p
m_c111_c52_c88 x_c111_c88 c111 g
m_c111_c54_dgmorgan x_c111_c52_dgmorgan c111 p
m_c111_c84_sn x_c111_c88_2 c111 p
m_c111_c88_c84 x_c111_c84 c111 g
m_c111_sn_sn x_c111 c111 p
m_c113_c50_c48 x_c113_c48 c113 g
m_c113_c52_c88 x_c113_c88 c113 g
m_c113_c88_c84 x_c113_c84 c113 g
m_c115_c84_c88 x_c115_c88 c115 g
m_c115_c88_c52 x_c115_c52 c115 g
m_c115_cbar_c50 x_c115_c50 c115 g
m_c117_c50_cp01 x_c117_c15_cp01_cbar c117 g
m_c117_c88_c84 x_c117_c84 c117 g
m_c119_cp01_c50 x_c119_c50 c119 g
m_c12_av11_c13 x_c12_c13 c12 p
m_c12_c13_c15 x_c12_c15 c12 p
m_c12_c15_c17 x_c12_c17 c12 g
m_c12_c17_c19 x_c12_c19 c12 g
m_c12_c19_c21 x_c12_c21 c12 g
m_c12_c1_c3 x_c12_c3 c12 g
m_c12_c21_c23 x_c12_c23 c12 g
m_c12_c23_c25 x_c12_c25 c12 g
m_c12_c25_c27 x_c12_c27 c12 g
m_c12_c27_c29 x_c12_c29 c12 d
m_c12_c3_c5 x_c12_c5 c12 g
m_c12_c5_c7 x_c12_c7 c12 g
m_c12_c7_c9 x_c12_c9 c12 p
m_c12_c9_av11 x_av11_c12 c12 p
m_c12_sn_c1 x_c1_c12 c12 g
m_c12_sn_sn x_c12_2 c12 d
m_c13_c10_c12 x_c12_c13 c13 p
m_c13_c12_c14 x_c13_c14 c13 p
m_c13_c14_c16 x_c13_c16 c13 p
m_c13_c16_c18 x_c13_c18 c13 p
m_c13_c18_c20 x_c13_c20 c13 p
m_c13_c4_c6 x_c13_c6 c13 p
m_c13_c6_c8 x_c13_c8 c13 p
m_c13_c8_c10 x_c10_c13 c13 p
m_c14_av11_c13 x_c13_c14 c14 g
m_c14_c13_c15 x_c14_c15 c14 g
m_c14_c15_c17 x_c14_c17 c14 g
m_c14_c17_c19 x_c14_c19 c14 g
m_c14_c19_c21 x_c14_c21 c14 g
m_c14_c1_c3 x_c14_c3 c14 g
m_c14_c21_c23 x_c14_c23 c14 g
m_c14_c23_c25 x_c14_c25 c14 g
m_c14_c25_c27 x_c14_c27 c14 g
m_c14_c27_c29 x_c14_c29 c14 g
m_c14_c29_sn x_c14 c14 d
m_c14_c3_c5 x_c14_c5 c14 g
m_c14_c5_c7 x_c14_c7 c14 g
m_c14_c7_c9 x_c14_c9 c14 g
m_c14_c9_av11 x_av11_c14 c14 g
m_c15_c10_c12 x_c12_c15 c15 p
m_c15_c12_c14 x_c14_c15 c15 g
m_c15_c14_c16 x_c15_c16 c15 g
m_c15_c16_c18 x_c15_c18 c15 g
m_c15_c18_c20 x_c15_c20 c15 g
m_c15_c2_c4 x_c15_c4 c15 g
m_c15_c4_c6 x_c15_c6 c15 g
m_c15_c6_c8 x_c15_c8 c15 g
m_c15_c8_c10 x_c10_c15 c15 p
m_c16_av11_c13 x_c13_c16 c16 g
m_c16_c13_c15 x_c15_c16 c16 g
m_c16_c15_c17 x_c16_c17 c16 g
m_c16_c17_c21 x_c16_c21 c16 g
m_c16_c1_c3 x_c16_c3 c16 d
m_c16_c21_c23 x_c16_c23 c16 g
m_c16_c3_c5 x_c16_c5 c16 g
m_c16_c5_c7 x_c16_c7 c16 g
m_c16_c7_c9 x_c16_c9 c16 g
m_c16_c9_av11 x_av11_c16 c16 g
m_c16b_c29_c27 x_c16b_c27 c16b g
m_c16b_c5_c7 x_c16b_c7 c16b g
m_c16b_sn_c29 x_c16b_c29 c16b g
m_c17_c10_c8 x_c17_c8 c17 g
m_c17_c12_c10 x_c10_c17 c17 g
m_c17_c14_c12 x_c12_c17 c17 g
m_c17_c16_c14 x_c14_c17 c17 g
m_c17_c20_c18 x_c17_c18 c17 g
m_c17_c24_c20 x_c17_c20 c17 g
m_c17_c28_c24 x_c17_c24 c17 d
m_c17_c4_c2 x_c15_c17_c2 c17 g
m_c17_c6_c4 x_c17_c4 c17 g
m_c17_c8_c6 x_c17_c6 c17 g
m_c18_av11_c9 x_c18_c9 c18 g
m_c18_c13_av11 x_av11_c18 c18 g
m_c18_c15_c13 x_c13_c18 c18 g
m_c18_c17_c15 x_c15_c18 c18 g
m_c18_c7_c5 x_c18_c5 c18 g
m_c18_c9_c7 x_c18_c7 c18 g
m_c18b_c5_c7 x_c18b_c7 c18b d
m_c19_c10_c8 x_c19_c8 c19 g
m_c19_c12_c10 x_c10_c19 c19 g
m_c19_c14_c12 x_c12_c19 c19 g
m_c19_c4_c2 x_c19_c2 c19 g
m_c19_c6_c4 x_c19_c4 c19 g
m_c19_c8_c6 x_c19_c6 c19 g
m_c1_c10_c12 x_c1_c12 c1 g
m_c1_c12_c14 x_c1_c14 c1 g
m_c1_c14_c16 x_c1_c16 c1 d
m_c1_c8_c10 x_c1_c10 c1 g
m_c1_sn_c8 x_c1_c8 c1 g
m_c20_acc_c13 x_c13_c20 c20 p
m_c20_c13_c15 x_c15_c20 c20 g
m_c20_c15_c17 x_c17_c20 c20 g
m_c20_c17_c21 x_c20_c21 c20 g
m_c20_c21_c23 x_c20_c23 c20 g
m_c20_c27_c29 x_c20_c29 c20 g
m_c20_c29_sn x_c20_3 c20 g
m_c20_c5_c7 x_c20_c7 c20 d
m_c20_c7_c9 x_c20_c9 c20 g
m_c20_c9_acc x_acc_av11_c20 c20 g
m_c20_sn_c27 x_c20_c27 c20 d
m_c21_c10_c12 x_c12_c21 c21 g
m_c21_c12_c14 x_c14_c21 c21 g
m_c21_c14_c16 x_c16_c21 c21 g
m_c21_c2_c4 x_c21_c4 c21 g
m_c21_c44_c2 x_c2_c21 c21 g
m_c21_c4_c6 x_c21_c6 c21 g
m_c21_c6_c8 x_c21_c8 c21 g
m_c21_c8_c10 x_c10_c21 c21 g
m_c21_dg4_c46 x_c21_c46 c21 g
m_c21_sn_c20 x_c20_c21 c21 g
m_c23_c10_c8 x_c23_c8 c23 g
m_c23_c12_c10 x_c10_c23 c23 g
m_c23_c14_c12 x_c12_c23 c23 g
m_c23_c16_c14 x_c14_c23 c23 g
m_c23_c20_c16 x_c16_c23 c23 g
m_c23_c4_c2 x_c2_c23 c23 g
m_c23_c6_c4 x_c23_c4 c23 g
m_c23_c8_c6 x_c23_c6 c23 g
m_c24_acc_c17 x_c17_c24 c24 g
m_c24_c17_sn x_c24 c24 g
m_c25_c10_c12 x_c12_c25 c25 g
m_c25_c12_c14 x_c14_c25 c25 g
m_c25_c2_c4 x_c25_c4 c25 g
m_c25_c46_c2 x_c2_c25 c25 g
m_c25_c4_c6 x_c25_c6 c25 g
m_c25_c6_c8 x_c25_c8 c25 g
m_c25_c8_c10 x_c10_c25 c25 g
m_c25_dg4_c48 x_c25_c48 c25 g
m_c27_c10_c8 x_c27_c8 c27 g
m_c27_c12_c10 x_c10_c27 c27 g
m_c27_c14_c12 x_c12_c27 c27 g
m_c27_c20_sn x_c27 c27 g
m_c27_c48_sn x_c27_4 c27 g
m_c27_c4_c2 x_c2_c27 c27 g
m_c27_c6_c4 x_c27_c4 c27 g
m_c27_c8_c6 x_c27_c6 c27 g
m_c28_c17_sn x_c28 c28 d
m_c29_c10_c8 x_c29_c8 c29 d
m_c29_c12_c10 x_c10_c29 c29 d
m_c29_c14_c12 x_c12_c29 c29 d
m_c29_c20_sn x_c29 c29 g
m_c29_c2b_c48 x_c29_c48 c29 g
m_c29_c48_dg4 x_c29_dg4 c29 g
m_c29_c4_c2 x_c2_c29 c29 g
m_c29_c6_c4 x_c29_c4 c29 g
m_c29_c8_c6 x_c29_c6 c29 d
m_c2_av11_c9 x_c2_c9 c2 p
m_c2_c13_c15 x_c15_c2 c2 p
m_c2_c13_sn x_c2_c4 c2 p
m_c2_c15_c13 x_c13_c2 c2 p
m_c2_c15_c15 x_c15_c2 c2 p
m_c2_c15_c15_2 x_c15_c17_c2 c2 p
m_c2_c17_c19 x_c19_c2 c2 g
m_c2_c19_c21 x_c2_c21 c2 g
m_c2_c21_c23 x_c2_c23 c2 g
m_c2_c23_c25 x_c2_c25 c2 g
m_c2_c25_c27 x_c2_c27 c2 g
m_c2_c27_c29 x_c2_c29 c2 g
m_c2_c29_sn x_c2 c2 d
m_c2_c7_c9 x_c2_c9 c2 p
m_c2_c9_av11 x_av11_c2_c4 c2 p
m_c2_c9_c7 x_c107_c2_c7 c2 p
m_c2_sn_c13 x_c13_c2 c2 p
m_c2_sn_sn x_c2_2 c2 d
m_c2b_c29_sn x_c2b c2b d
m_c31_c48_sn x_c31 c31 g
m_c31_sn_dg4 x_c31_dg4 c31 d
m_c33_dg4_sn x_c33 c33 d
m_c33_sn_c48 x_c33_c48 c33 d
m_c35_sn_sn x_c35_3 c35 d
m_c3_c10_c12 x_c12_c3 c3 g
m_c3_c12_c14 x_c14_c3 c3 g
m_c3_c14_c16 x_c16_c3 c3 g
m_c3_c6_c8 x_c3_c8 c3 g
m_c3_c8_c10 x_c10_c3 c3 g
m_c44_c105_c107 x_c107_c44 c44 g
m_c44_c19_c21 x_c21_c44 c44 g
m_c44_sn_c105 x_c105_c44 c44 g
m_c44_sn_sn x_c103_c44 c44 g
m_c46_c105_sn x_c103_c46 c46 g
m_c46_c107_c105 x_c105_c46 c46 g
m_c46_c21_c25 x_c25_c46 c46 g
m_c46_sn_sn x_c101_c46 c46 g
m_c48_c101_c103 x_c103_c48 c48 g
m_c48_c103_c105 x_c105_c48 c48 g
m_c48_c105_c107 x_c107_c48_dgmorgan c48 g
m_c48_c107_c109 x_c109_c48 c48 g
m_c48_c111_c113 x_c113_c48 c48 g
m_c48_c25_c27 x_c27_c48 c48 g
m_c48_c27_c29 x_c29_c48 c48 g
m_c48_dg2_c111 x_c111_c48 c48 g
m_c48_sn_c101 x_c101_c48 c48 g
m_c48_sn_sn x_c48 c48 d
m_c4_c13_c15 x_c15_c4 c4 g
m_c4_c15_c17 x_c17_c4 c4 g
m_c4_c17_c19 x_c19_c4 c4 g
m_c4_c19_c21 x_c21_c4 c4 g
m_c4_c21_c23 x_c23_c4 c4 g
m_c4_c23_c25 x_c25_c4 c4 g
m_c4_c25_c27 x_c27_c4 c4 g
m_c4_c27_c29 x_c29_c4 c4 g
m_c4_c29_sn x_c4 c4 d
m_c4_sn_c13 x_c13_c4 c4 g
m_c50_c101_c103 x_c103_c50 c50 g
m_c50_c103_c105 x_c105_c50 c50 g
m_c50_c105_c107 x_c107_c50 c50 g
m_c50_c107_c109 x_c109_c50_dgmorgan c50 g
m_c50_c109_c111 x_c111_c50 c50 g
m_c50_c111_c113 x_c113_c50 c50 g
m_c50_c117_c119 x_c119_c50 c50 g
m_c50_c121_c123 x_c123_c50 c50 g
m_c52_c101_c103 x_c103_c52 c52 g
m_c52_c103_c105 x_c105_c52 c52 g
m_c52_c105_c107 x_c107_c52 c52 g
m_c52_c107_c109 x_c109_c52 c52 g
m_c52_c109_dgmorgan x_c111_c52_dgmorgan c52 g
m_c52_c115_c117 x_c117_c52 c52 g
m_c52_c117_c119 x_c119_c52 c52 g
m_c52_c121_c123 x_c123_c52 c52 g
m_c52_c123_sn x_c52 c52 d
m_c54_c103_sn x_c101_c54 c54 g
m_c54_c105_c103 x_c103_c54 c54 g
m_c54_c107_c105 x_c105_c54 c54 g
m_c54_c109_c107 x_c107_c54 c54 g
m_c54_c111_c109 x_c109_c54 c54 g
m_c5_c10_c12 x_c12_c5 c5 g
m_c5_c12_c14 x_c14_c5 c5 g
m_c5_c14_c16 x_c16_c5 c5 g
m_c5_c6_c8 x_c5_c8 c5 g
m_c5_c8_c10 x_c10_c5 c5 g
m_c6_av11_c9 x_c6_c9 c6 p
m_c6_c13_av11 x_av11_c6 c6 p
m_c6_c15_c13 x_c13_c6 c6 g
m_c6_c17_c15 x_c15_c6 c6 g
m_c6_c19_c17 x_c17_c6 c6 g
m_c6_c21_c19 x_c19_c6 c6 g
m_c6_c23_c21 x_c21_c6 c6 g
m_c6_c25_c23 x_c23_c6 c6 g
m_c6_c27_c25 x_c25_c6 c6 g
m_c6_c29_c27 x_c27_c6 c6 g
m_c6_c5_c3 x_c3_c6 c6 g
m_c6_c7_c5 x_c5_c6 c6 g
m_c6_c9_c7 x_c6_c7 c6 g
m_c7_acc_c20 x_c20_c7 c7 d
m_c7_c10_c8 x_c7_c8 c7 g
m_c7_c12_c10 x_c10_c7 c7 g
m_c7_c14_c12 x_c12_c7 c7 g
m_c7_c16_c14 x_c14_c7 c7 g
m_c7_c6_c2 x_c107_c2_c7 c7 g
m_c7_c8_c6 x_c6_c7 c7 g
m_c88_c117_c119 x_c119_c88 c88 g
m_c8_av11_c13 x_c13_c8 c8 p
m_c8_c13_c15 x_c15_c8 c8 p
m_c8_c15_c17 x_c17_c8 c8 g
m_c8_c17_c19 x_c19_c8 c8 g
m_c8_c19_c21 x_c21_c8 c8 g
m_c8_c1_c3 x_c3_c8 c8 g
m_c8_c21_c23 x_c23_c8 c8 g
m_c8_c23_c25 x_c25_c8 c8 g
m_c8_c25_c27 x_c27_c8 c8 g
m_c8_c27_c29 x_c29_c8 c8 g
m_c8_c3_c5 x_c5_c8 c8 g
m_c8_c5_c7 x_c7_c8 c8 g
m_c8_c7_c9 x_c8_c9 c8 p
m_c8_c9_av11 x_av11_c8 c8 p
m_c90_c119_c117 x_c117_c90 c90 g
m_c90b_c117_c119 x_c119_c90b c90b g
m_c9_c10_c12 x_c12_c9 c9 p
m_c9_c12_c14 x_c14_c9 c9 p
m_c9_c14_c16 x_c16_c9 c9 g
m_c9_c16_c18 x_c18_c9 c9 g
m_c9_c18_c20 x_c20_c9 c9 g
m_c9_c6_c8 x_c8_c9 c9 p
m_c9_c8_c10 x_c10_c9 c9 p
m_cbar_c113_c111 x_c111_cbar cbar p
m_cbar_c115_c113 x_c113_cbar cbar p
m_cbar_dg2_c107 x_c107_cbar cbar p
m_cp01_c107_sn x_cp01_2 cp01 p
m_cp01_c117_c119 x_c119_cp01 cp01 p
m_cp01_c119_c121 x_c121_cp01 cp01 p
m_cp01_c121_c123 x_c123_cp01 cp01 p
m_cp01_c123_sn x_cp01_3 cp01 p
m_cp01_sn_sn x_cp01 cp01 p
m_cp01_sn_sn_2 x_cp01_4 cp01 p
m_cp01_sn_sn_3 x_cp01_5 cp01 p
m_dg2_cbar_c48 x_c48_dg2 dg2 g
m_dg4_c19_c21 x_c21_dg4 dg4 p
m_dg4_c21_c25 x_c25_dg4 dg4 p
m_dg4_c25_c29 x_c29_dg4 dg4 p
m_dg4_c29_c31 x_c31_dg4 dg4 p
m_dg4_sn_c19 x_c19_dg4 dg4 p
m_dgmorgan_c109_c107 x_c107_c48_dgmorgan dgmorgan g
m_dgmorgan_c52_c109 x_c109_c50_dgmorgan dgmorgan g
m_sn_c105_c103 x_c103_2 sn g
m_sn_c105_sn x_c103 sn g
m_sn_c107_c105 x_c105_2 sn g
m_sn_c109_c107 x_c107 sn g
m_sn_c111_sn x_sn_47 sn d
m_sn_c119_c117 x_c117 sn g
m_sn_c12_sn x_sn_5 sn d
m_sn_c16_c20 x_c20 sn g
m_sn_c16_sn x_sn_3 sn g
m_sn_c16_sn_2 x_sn_2 sn g
m_sn_c19_dg4 x_dg4 sn g
m_sn_c1_sn x_sn_10 sn p
m_sn_c20_c24 x_c24 sn d
m_sn_c21_c17 x_c17 sn g
m_sn_c24_c28 x_c28 sn d
m_sn_c29_c27 x_c27 sn g
m_sn_c29_c27_2 x_c27_2 sn g
m_sn_c29_c27_3 x_c27_3 sn g
m_sn_c2_c4 x_c4 sn d
m_sn_c2_c5 x_c5 sn p
m_sn_c3_c1 x_c1 sn p
m_sn_c52_sn x_sn_28 sn d
m_sn_c5_c3 x_c3 sn p
m_sn_c8_sn x_sn_8 sn g
m_sn_sn_c101 x_c101_c50 sn g
m_sn_sn_c101_2 x_c101_2 sn g
m_sn_sn_c105 x_c105_2 sn g
m_sn_sn_c107 x_c107 sn g
m_sn_sn_c109 x_c109 sn g
m_sn_sn_c109_2 x_c109 sn g
m_sn_sn_c12 x_c12_2 sn g
m_sn_sn_c20 x_c20_3 sn d
m_sn_sn_c20_2 x_c20_2 sn g
m_sn_sn_c29 x_c29 sn g
m_sn_sn_c29_2 x_c29_2 sn g
m_sn_sn_c29_3 x_c29_3 sn g
m_sn_sn_sn x_sn_7 sn p
m_sn_sn_sn_10 x_sn_20 sn d
m_sn_sn_sn_11 x_sn_21 sn g
m_sn_sn_sn_12 x_sn_22 sn g
m_sn_sn_sn_13 x_sn_24 sn d
m_sn_sn_sn_14 x_sn_27 sn d
m_sn_sn_sn_15 x_sn_29 sn d
m_sn_sn_sn_16 x_sn_37 sn g
m_sn_sn_sn_17 x_sn_39 sn g
m_sn_sn_sn_18 x_sn_38 sn g
m_sn_sn_sn_19 x_sn_36 sn g
m_sn_sn_sn_2 x_sn_9 sn p
m_sn_sn_sn_20 x_sn_37 sn g
m_sn_sn_sn_21 x_sn_39 sn g
m_sn_sn_sn_22 x_sn_38 sn g
m_sn_sn_sn_23 x_sn_34 sn d
m_sn_sn_sn_24 x_sn_45 sn g
m_sn_sn_sn_25 x_sn_40 sn g
m_sn_sn_sn_26 x_sn_43 sn g
m_sn_sn_sn_27 x_sn_45 sn g
m_sn_sn_sn_28 x_sn_41 sn g
m_sn_sn_sn_29 x_sn_41 sn d
m_sn_sn_sn_3 x_sn_15 sn g
m_sn_sn_sn_30 x_sn_46 sn d
m_sn_sn_sn_31 x_sn_49 sn d
m_sn_sn_sn_32 x_sn_48 sn d
m_sn_sn_sn_33 x_sn_44 sn d
m_sn_sn_sn_34 x_sn_48 sn d
m_sn_sn_sn_35 x_sn_49 sn d
m_sn_sn_sn_36 x_sn_46 sn d
m_sn_sn_sn_4 x_sn_13 sn d
m_sn_sn_sn_5 x_sn_11 sn g
m_sn_sn_sn_6 x_sn_17 sn d
m_sn_sn_sn_7 x_sn_18 sn g
m_sn_sn_sn_8 x_c101 sn g
m_sn_sn_sn_9 x_sn_19 sn g
r111_2752m r111_papermill c111 p
r111_7180m r111_7334m c111 p
r111_7334m atucha_gate c111 p
r111_767m r111_973m c111 p
r111_973m r111_2752m c111 p
r111_papermill r111_7180m c111 p
x_acc_av11_c20 m_acc_av11_c24 acc p
x_acc_av11_c20 m_av11_acc_c18 av11 p
x_acc_av11_c20 m_c20_acc_c13 c20 p
x_acc_c24 m_acc_c24_c7 acc p
x_acc_c24 m_c24_acc_c17 c24 g
x_acc_c7 m_acc_c7_sn acc p
x_acc_c7 m_c7_acc_c20 c7 d
x_av11_c10 m_av11_c10_c8 av11 p
x_av11_c10 m_c10_av11_c9 c10 p
x_av11_c12 m_av11_c12_c10 av11 p
x_av11_c12 m_c12_av11_c13 c12 p
x_av11_c14 m_av11_c14_c12 av11 p
x_av11_c14 m_c14_av11_c13 c14 g
x_av11_c16 m_av11_c16_c14 av11 p
x_av11_c16 m_c16_av11_c13 c16 g
x_av11_c18 m_av11_c18_c16 av11 p
x_av11_c18 m_c18_av11_c9 c18 g
x_av11_c2_c4 m_c2_av11_c9 c2 p
x_av11_c2_c4 x_c2_c4 c4 g
x_av11_c6 m_av11_c6_c4 av11 p
x_av11_c6 m_c6_av11_c9 c6 p
x_av11_c8 m_av11_c8_c6 av11 p
x_av11_c8 m_c8_av11_c13 c8 p
x_c1 m_c1_sn_c8 c1 g
x_c1 m_sn_c1_sn sn p
x_c101 m_sn_sn_sn_7 sn g
x_c101_2 x_c101_c50 c101 g
x_c101_c44 m_c44_sn_sn c44 g
x_c101_c44 m_sn_sn_sn_9 sn g
x_c101_c44 x_c101 c101 g
x_c101_c46 m_sn_sn_sn_11 sn g
x_c101_c46 x_c101_c44 c101 g
x_c101_c48 m_c48_c101_c103 c48 g
x_c101_c48 x_c101_c46 c101 g
x_c101_c50 m_c50_c101_c103 c50 g
x_c101_c50 x_c101_c48 c101 g
x_c101_c52 m_c52_c101_c103 c52 g
x_c101_c52 x_c101_2 c101 g
x_c101_c54 m_c101_c54_c101 c101 g
x_c103 m_sn_sn_sn_8 sn g
x_c103_2 x_sn_31 sn g
x_c103_c44 m_c44_sn_c105 c44 g
x_c103_c44 x_c103 c103 g
x_c103_c46 m_c103_c46_c44 c103 g
x_c103_c46 m_c46_sn_sn c46 g
x_c103_c48 m_c103_c48_c50 c103 g
x_c103_c48 m_c48_c103_c105 c48 g
x_c103_c48 x_c103_c46 c103 g
x_c103_c50 m_c103_c50_c52 c103 g
x_c103_c50 m_c50_c103_c105 c50 g
x_c103_c52 m_c103_c52_c54 c103 g
x_c103_c52 m_c52_c103_c105 c52 g
x_c103_c54 m_c103_c54_sn c103 g
x_c103_c54 m_c54_c103_sn c54 g
x_c105 m_sn_c105_sn sn g
x_c105_2 m_c105_sn_c54 c105 g
x_c105_2 m_sn_c105_c103 sn g
x_c105_2 x_sn_33 sn g
x_c105_c44 m_c44_c105_c107 c44 g
x_c105_c44 x_c105 c105 g
x_c105_c46 m_c105_c46_c44 c105 g
x_c105_c46 m_c46_c105_sn c46 g
x_c105_c48 m_c48_c105_c107 c48 g
x_c105_c48 x_c105_c46 c105 g
x_c105_c50 m_c105_c50_c48 c105 g
x_c105_c50 m_c50_c105_c107 c50 g
x_c105_c52 m_c105_c52_c50 c105 g
x_c105_c52 m_c52_c105_c107 c52 g
x_c105_c54 m_c105_c54_c52 c105 g
x_c105_c54 m_c54_c105_c103 c54 g
x_c107 m_sn_c107_c105 sn g
x_c107 x_sn_30 sn g
x_c107_c2_c7 m_c2_c7_c9 c2 p
x_c107_c2_c7 m_sn_c2_c5 sn p
x_c107_c2_c7 x_c107_cp01 c107 p
x_c107_c44 x_c107_c46 c107 g
x_c107_c46 m_c107_c46_c48 c107 g
x_c107_c46 m_c46_c107_c105 c46 g
x_c107_c48_dgmorgan m_c107_c48_c50 c107 g
x_c107_c48_dgmorgan m_c48_c107_c109 c48 g
x_c107_c50 m_c107_c50_c52 c107 g
x_c107_c50 m_c50_c107_c109 c50 g
x_c107_c52 m_c107_c52_c54 c107 g
x_c107_c52 m_c52_c107_c109 c52 g
x_c107_c54 m_c107_c54_sn c107 g
x_c107_c54 m_c54_c107_c105 c54 g
x_c107_cbar x_c107_c44 c107 g
x_c107_cp01 m_cp01_c107_sn cp01 p
x_c107_cp01 x_c107_cbar c107 p
x_c109 m_c109_sn_c54 c109 g
x_c109 m_sn_c109_c107 sn g
x_c109 x_sn_32 sn g
x_c109_c48 x_c48_dg2 c48 g
x_c109_c50_dgmorgan m_c109_c50_c48 c109 g
x_c109_c50_dgmorgan m_c50_c109_c111 c50 g
x_c109_c50_dgmorgan m_dgmorgan_c109_c107 dgmorgan g
x_c109_c52 m_c109_c52_c50 c109 g
x_c109_c52 m_c52_c109_dgmorgan c52 g
x_c109_c54 m_c109_c54_c52 c109 g
x_c109_c54 m_c54_c109_c107 c54 g
x_c10_c13 m_c10_c13_av11 c10 p
x_c10_c13 m_c13_c10_c12 c13 p
x_c10_c15 m_c10_c15_c13 c10 p
x_c10_c15 m_c15_c10_c12 c15 p
x_c10_c17 m_c10_c17_c15 c10 g
x_c10_c17 m_c17_c10_c8 c17 g
x_c10_c19 m_c10_c19_c17 c10 g
x_c10_c19 m_c19_c10_c8 c19 g
x_c10_c21 m_c10_c21_c19 c10 g
x_c10_c21 m_c21_c10_c12 c21 g
x_c10_c23 m_c10_c23_c21 c10 g
x_c10_c23 m_c23_c10_c8 c23 g
x_c10_c25 m_c10_c25_c23 c10 g
x_c10_c25 m_c25_c10_c12 c25 g
x_c10_c27 m_c10_c27_c25 c10 g
x_c10_c27 m_c27_c10_c8 c27 g
x_c10_c29 m_c10_c29_c27 c10 d
x_c10_c29 m_c29_c10_c8 c29 d
x_c10_c3 m_c10_c3_c1 c10 g
x_c10_c3 m_c3_c10_c12 c3 g
x_c10_c5 m_c10_c5_c3 c10 g
x_c10_c5 m_c5_c10_c12 c5 g
x_c10_c7 m_c10_c7_c5 c10 g
x_c10_c7 m_c7_c10_c8 c7 g
x_c10_c9 m_c10_c9_c7 c10 p
x_c10_c9 m_c9_c10_c12 c9 p
x_c111 m_sn_c111_sn sn d
x_c111 x_c111_c84_2 c111 p
x_c111_2 m_c111_sn_sn c111 p
x_c111_2 r111_767m c111 p
x_c111_c48 m_c111_c48_cbar c111 p
x_c111_c48 m_c48_c111_c113 c48 g
x_c111_c50 m_c111_c50_c48 c111 p
x_c111_c50 m_c50_c111_c113 c50 g
x_c111_c52 m_c111_c52_c88 c111 g
x_c111_c52 x_c113_c52 c52 g
x_c111_c52_dgmorgan m_dgmorgan_c52_c109 dgmorgan g
x_c111_c52_dgmorgan x_c111_c50 c111 p
x_c111_c52_dgmorgan x_c111_c52 c52 g
x_c111_c54 m_c111_c54_dgmorgan c111 p
x_c111_c54 m_c54_c111_c109 c54 g
x_c111_c84 x_c113_c84 c84 d
x_c111_c84_2 m_c111_c84_sn c111 p
x_c111_c84_2 x_c111_c84 c84 d
x_c111_c88 m_c111_c88_c84 c111 g
x_c111_c88 x_c113_c88 c88 g
x_c111_c88_2 m_sn_sn_c109 sn g
x_c111_c88_2 m_sn_sn_c109_2 sn g
x_c111_c88_2 x_c111_c54 c111 p
x_c111_c88_2 x_c111_c88 c88 g
x_c111_cbar x_cbar_dg2 cbar p
x_c113 x_c113_c50 c113 g
x_c113_c48 x_c113_cbar c113 g
x_c113_c50 m_c113_c50_c48 c113 g
x_c113_c50 x_c115_c50 c50 g
x_c113_c52 m_c113_c52_c88 c113 g
x_c113_c52 x_c115_c52 c52 g
x_c113_c84 x_c115_c84 c84 d
x_c113_c88 m_c113_c88_c84 c113 g
x_c113_c88 x_c115_c88 c88 g
x_c113_cbar m_cbar_c113_c111 cbar p
x_c115 x_c113 sn g
x_c115_c50 x_c115 c115 g
x_c115_c50 x_c117_c50 c50 g
x_c115_c52 m_c52_c115_c117 c52 g
x_c115_c84 m_c115_c84_c88 c115 g
x_c115_c84 x_c117_c84 c84 d
x_c115_c88 m_c115_c88_c52 c115 g
x_c115_c88 x_c117_c88 c88 g
x_c115_cbar m_c115_cbar_c50 c115 g
x_c115_cbar m_cbar_c115_c113 cbar p
x_c117 x_c115 sn g
x_c117 x_c117_c50 c117 g
x_c117_c15_cp01_cbar m_cp01_c117_c119 cp01 p
x_c117_c15_cp01_cbar x_c115_cbar cbar p
x_c117_c50 m_c117_c50_cp01 c117 g
x_c117_c50 m_c50_c117_c119 c50 g
x_c117_c52 m_c52_c117_c119 c52 g
x_c117_c52 x_c117_c90b c117 g
x_c117_c88 m_c117_c88_c84 c117 g
x_c117_c88 m_c88_c117_c119 c88 g
x_c117_c90 x_c117_c88 c117 g
x_c117_c90b m_c90b_c117_c119 c90b g
x_c117_c90b x_c117_c90 c117 g
x_c119 x_c119_c88 c119 g
x_c119_2 x_c119 c119 g
x_c119_3 x_c119_2 c119 d
x_c119_c50 x_c119_c52 c119 g
x_c119_c50 x_c121_c50 c50 g
x_c119_c52 m_sn_c119_c117 sn g
x_c119_c52 x_c121_c52 c52 g
x_c119_c88 x_c119_c90 c119 g
x_c119_c90 m_c90_c119_c117 c90 g
x_c119_c90 x_c119_c90b c119 g
x_c119_c90b x_c119_c52 c119 g
x_c119_cp01 m_c119_cp01_c50 c119 g
x_c119_cp01 m_cp01_c119_c121 cp01 p
x_c12 m_c12_sn_sn c12 d
x_c121_c50 m_c50_c121_c123 c50 g
x_c121_c50 x_c121_cp01 c121 g
x_c121_c52 m_c52_c121_c123 c52 g
x_c121_c52 x_c121_c50 c121 g
x_c121_cp01 m_cp01_c121_c123 cp01 p
x_c123_c50 x_c123_c52 c123 g
x_c123_c52 m_c52_c123_sn c52 d
x_c123_cp01 m_cp01_c123_sn cp01 p
x_c123_cp01 x_c123_c50 c123 g
x_c12_2 m_c12_sn_c1 c12 g
x_c12_2 m_sn_c12_sn sn d
x_c12_c13 m_c12_c13_c15 c12 p
x_c12_c13 m_c13_c12_c14 c13 p
x_c12_c15 m_c12_c15_c17 c12 g
x_c12_c15 m_c15_c12_c14 c15 g
x_c12_c17 m_c12_c17_c19 c12 g
x_c12_c17 m_c17_c12_c10 c17 g
x_c12_c19 m_c12_c19_c21 c12 g
x_c12_c19 m_c19_c12_c10 c19 g
x_c12_c21 m_c12_c21_c23 c12 g
x_c12_c21 m_c21_c12_c14 c21 g
x_c12_c23 m_c12_c23_c25 c12 g
x_c12_c23 m_c23_c12_c10 c23 g
x_c12_c25 m_c12_c25_c27 c12 g
x_c12_c25 m_c25_c12_c14 c25 g
x_c12_c27 m_c12_c27_c29 c12 d
x_c12_c27 m_c27_c12_c10 c27 g
x_c12_c29 m_c29_c12_c10 c29 d
x_c12_c3 m_c12_c3_c5 c12 g
x_c12_c3 m_c3_c12_c14 c3 g
x_c12_c5 m_c12_c5_c7 c12 g
x_c12_c5 m_c5_c12_c14 c5 g
x_c12_c7 m_c12_c7_c9 c12 p
x_c12_c7 m_c7_c12_c10 c7 g
x_c12_c9 m_c12_c9_av11 c12 p
x_c12_c9 m_c9_c12_c14 c9 p
x_c13_c14 m_c13_c14_c16 c13 p
x_c13_c14 m_c14_c13_c15 c14 g
x_c13_c16 m_c13_c16_c18 c13 p
x_c13_c16 m_c16_c13_c15 c16 g
x_c13_c18 m_c13_c18_c20 c13 p
x_c13_c18 m_c18_c13_av11 c18 g
x_c13_c2 m_c2_c13_c15 c2 p
x_c13_c2 m_c2_c13_sn c2 p
x_c13_c2 x_c13_c4 c13 p
x_c13_c20 m_c20_c13_c15 c20 g
x_c13_c4 m_c13_c4_c6 c13 p
x_c13_c4 m_c4_c13_c15 c4 g
x_c13_c6 m_c13_c6_c8 c13 p
x_c13_c6 m_c6_c13_av11 c6 p
x_c13_c8 m_c13_c8_c10 c13 p
x_c13_c8 m_c8_c13_c15 c8 p
x_c14 x_c16b sn d
x_c14_c15 m_c14_c15_c17 c14 g
x_c14_c15 m_c15_c14_c16 c15 g
x_c14_c17 m_c14_c17_c19 c14 g
x_c14_c17 m_c17_c14_c12 c17 g
x_c14_c19 m_c14_c19_c21 c14 g
x_c14_c19 m_c19_c14_c12 c19 g
x_c14_c21 m_c14_c21_c23 c14 g
x_c14_c21 m_c21_c14_c16 c21 g
x_c14_c23 m_c14_c23_c25 c14 g
x_c14_c23 m_c23_c14_c12 c23 g
x_c14_c25 m_c14_c25_c27 c14 g
x_c14_c27 m_c14_c27_c29 c14 g
x_c14_c27 m_c27_c14_c12 c27 g
x_c14_c29 m_c14_c29_sn c14 d
x_c14_c29 m_c29_c14_c12 c29 d
x_c14_c3 m_c14_c3_c5 c14 g
x_c14_c3 m_c3_c14_c16 c3 g
x_c14_c5 m_c14_c5_c7 c14 g
x_c14_c5 m_c5_c14_c16 c5 g
x_c14_c7 m_c14_c7_c9 c14 g
x_c14_c7 m_c7_c14_c12 c7 g
x_c14_c9 m_c14_c9_av11 c14 g
x_c14_c9 m_c9_c14_c16 c9 g
x_c15_c16 m_c15_c16_c18 c15 g
x_c15_c16 m_c16_c15_c17 c16 g
x_c15_c17_c2 m_c2_c15_c15 c2 p
x_c15_c17_c2 m_c2_c17_c19 c2 g
x_c15_c17_c2 x_c15_dg4 c15 p
x_c15_c18 m_c15_c18_c20 c15 g
x_c15_c18 m_c18_c15_c13 c18 g
x_c15_c2 m_c15_c2_c4 c15 g
x_c15_c2 m_c2_c15_c13 c2 p
x_c15_c2 m_c2_c15_c15_2 c2 p
x_c15_c20 m_c20_c15_c17 c20 g
x_c15_c4 m_c15_c4_c6 c15 g
x_c15_c4 m_c4_c15_c17 c4 g
x_c15_c6 m_c15_c6_c8 c15 g
x_c15_c6 m_c6_c15_c13 c6 g
x_c15_c8 m_c15_c8_c10 c15 p
x_c15_c8 m_c8_c15_c17 c8 g
x_c15_dg4 fcm_crossing_6km rail r
x_c15_dg4 x_c117_c15_cp01_cbar c15 p
x_c15_dg4 x_dg4 dg4 p
x_c16 m_sn_c16_sn sn g
x_c16_2 m_sn_c16_c20 sn g
x_c16_2 x_c16_3 c16 g
x_c16_3 m_sn_c16_sn_2 sn g
x_c16_3 x_c16 c16 g
x_c16_c17 m_c16_c17_c21 c16 g
x_c16_c17 m_c17_c16_c14 c17 g
x_c16_c21 m_c16_c21_c23 c16 g
x_c16_c21 x_c21 c21 g
x_c16_c23 m_c23_c16_c14 c23 g
x_c16_c23 x_c16_2 c16 g
x_c16_c3 m_c16_c3_c5 c16 g
x_c16_c5 m_c16_c5_c7 c16 g
x_c16_c5 x_c16b_c5 c5 g
x_c16_c7 m_c16_c7_c9 c16 g
x_c16_c7 m_c7_c16_c14 c7 g
x_c16_c9 m_c16_c9_av11 c16 g
x_c16_c9 m_c9_c16_c18 c9 g
x_c16b m_c16b_sn_c29 c16b g
x_c16b x_sn_6 sn d
x_c16b_c27 x_c14_c27 c27 g
x_c16b_c29 m_c16b_c29_c27 c16b g
x_c16b_c29 x_c14_c29 c29 g
x_c16b_c5 m_c16b_c5_c7 c16b g
x_c16b_c5 x_c18_c5 c5 g
x_c16b_c7 x_c16_c7 c7 g
x_c17 x_c16_c17 c17 g
x_c17_c18 m_c18_c17_c15 c18 g
x_c17_c18 x_c17 c17 g
x_c17_c20 m_c17_c20_c18 c17 g
x_c17_c20 m_c20_c17_c21 c20 g
x_c17_c24 m_c17_c24_c20 c17 g
x_c17_c24 m_c24_c17_sn c24 g
x_c17_c28 m_c17_c28_c24 c17 d
x_c17_c28 m_c28_c17_sn c28 d
x_c17_c4 m_c17_c4_c2 c17 g
x_c17_c4 m_c4_c17_c19 c4 g
x_c17_c6 m_c17_c6_c4 c17 g
x_c17_c6 m_c6_c17_c15 c6 g
x_c17_c8 m_c17_c8_c6 c17 g
x_c17_c8 m_c8_c17_c19 c8 g
x_c18_c5 x_c18b_c5 c5 d
x_c18_c7 m_c18_c7_c5 c18 g
x_c18_c7 x_c16b_c7 c7 g
x_c18_c9 m_c18_c9_c7 c18 g
x_c18_c9 m_c9_c18_c20 c9 g
x_c18b_c5 m_c18b_c5_c7 c18b d
x_c18b_c5 x_c20_c5 c5 d
x_c18b_c7 x_c18_c7 c7 g
x_c19 m_sn_c19_dg4 sn g
x_c19 x_c19_c44 c19 g
x_c19_c2 m_c2_c19_c21 c2 g
x_c19_c2 x_c19 c19 g
x_c19_c4 m_c19_c4_c2 c19 g
x_c19_c4 m_c4_c19_c21 c4 g
x_c19_c44 m_c44_c19_c21 c44 g
x_c19_c44 x_c19_dg4 c19 g
x_c19_c6 m_c19_c6_c4 c19 g
x_c19_c6 m_c6_c19_c17 c6 g
x_c19_c8 m_c19_c8_c6 c19 g
x_c19_c8 m_c8_c19_c21 c8 g
x_c19_dg4 m_dg4_c19_c21 dg4 p
x_c1_c10 m_c1_c10_c12 c1 g
x_c1_c12 m_c12_c1_c3 c12 g
x_c1_c12 m_c1_c12_c14 c1 g
x_c1_c14 m_c14_c1_c3 c14 g
x_c1_c14 m_c1_c14_c16 c1 d
x_c1_c16 m_c16_c1_c3 c16 d
x_c1_c8 m_c1_c8_c10 c1 g
x_c1_c8 m_c8_c1_c3 c8 g
x_c2 m_c2_sn_sn c2 d
x_c2 m_sn_c2_c4 sn d
x_c20 x_c20_2 c20 g
x_c20_2 m_c20_sn_c27 c20 d
x_c20_2 m_sn_c20_c24 sn d
x_c20_c21 m_c20_c21_c23 c20 g
x_c20_c23 m_c23_c20_c16 c23 g
x_c20_c23 x_c20 c20 g
x_c20_c27 m_c20_c27_c29 c20 g
x_c20_c27 m_c27_c20_sn c27 g
x_c20_c29 m_c20_c29_sn c20 g
x_c20_c29 m_c29_c20_sn c29 g
x_c20_c5 m_c20_c5_c7 c20 d
x_c20_c7 m_c20_c7_c9 c20 g
x_c20_c7 x_c18b_c7 c7 g
x_c20_c9 m_c20_c9_acc c20 g
x_c21 m_c21_sn_c20 c21 g
x_c21 m_sn_c21_c17 sn g
x_c21_c4 m_c21_c4_c6 c21 g
x_c21_c4 m_c4_c21_c23 c4 g
x_c21_c44 m_c21_c44_c2 c21 g
x_c21_c46 m_c46_c21_c25 c46 g
x_c21_c46 x_c21_c44 c21 g
x_c21_c6 m_c21_c6_c8 c21 g
x_c21_c6 m_c6_c21_c19 c6 g
x_c21_c8 m_c21_c8_c10 c21 g
x_c21_c8 m_c8_c21_c23 c8 g
x_c21_dg4 m_c21_dg4_c46 c21 g
x_c21_dg4 m_dg4_c21_c25 dg4 p
x_c23_c4 m_c23_c4_c2 c23 g
x_c23_c4 m_c4_c23_c25 c4 g
x_c23_c6 m_c23_c6_c4 c23 g
x_c23_c6 m_c6_c23_c21 c6 g
x_c23_c8 m_c23_c8_c6 c23 g
x_c23_c8 m_c8_c23_c25 c8 g
x_c24 m_sn_c24_c28 sn d
x_c25_c4 m_c25_c4_c6 c25 g
x_c25_c4 m_c4_c25_c27 c4 g
x_c25_c46 m_c25_c46_c2 c25 g
x_c25_c48 m_c48_c25_c27 c48 g
x_c25_c48 x_c25_c46 c25 g
x_c25_c6 m_c25_c6_c8 c25 g
x_c25_c6 m_c6_c25_c23 c6 g
x_c25_c8 m_c25_c8_c10 c25 g
x_c25_c8 m_c8_c25_c27 c8 g
x_c25_dg4 m_c25_dg4_c48 c25 g
x_c25_dg4 m_dg4_c25_c29 dg4 p
x_c27 x_c27_2 c27 g
x_c27_2 x_c27_3 c27 g
x_c27_3 x_c16b_c27 c27 g
x_c27_c4 m_c27_c4_c2 c27 g
x_c27_c4 m_c4_c27_c29 c4 g
x_c27_c48 m_c27_c48_sn c27 g
x_c27_c48 m_c48_c27_c29 c48 g
x_c27_c6 m_c27_c6_c4 c27 g
x_c27_c6 m_c6_c27_c25 c6 g
x_c27_c8 m_c27_c8_c6 c27 g
x_c27_c8 m_c8_c27_c29 c8 g
x_c29 m_sn_c29_c27 sn g
x_c29 x_c29_2 c29 g
x_c29_2 m_sn_c29_c27_2 sn g
x_c29_2 x_c29_3 c29 g
x_c29_3 m_sn_c29_c27_3 sn g
x_c29_3 x_c16b_c29 c29 g
x_c29_c4 m_c29_c4_c2 c29 g
x_c29_c4 m_c4_c29_sn c4 d
x_c29_c48 m_c29_c48_dg4 c29 g
x_c29_c48 x_c48_3 c48 g
x_c29_c6 m_c29_c6_c4 c29 g
x_c29_c6 m_c6_c29_c27 c6 g
x_c29_c8 m_c29_c8_c6 c29 d
x_c29_dg4 m_dg4_c29_c31 dg4 p
x_c2_c21 m_c21_c2_c4 c21 g
x_c2_c21 m_c2_c21_c23 c2 g
x_c2_c23 m_c2_c23_c25 c2 g
x_c2_c25 m_c25_c2_c4 c25 g
x_c2_c25 m_c2_c25_c27 c2 g
x_c2_c27 m_c2_c27_c29 c2 g
x_c2_c29 m_c2_c29_sn c2 d
x_c2_c29 x_c2b_c29 c29 g
x_c2_c4 m_c2_sn_c13 c2 p
x_c2_c4 m_c4_sn_c13 c4 g
x_c2_c9 m_c2_c9_av11 c2 p
x_c2_c9 m_c2_c9_c7 c2 p
x_c2_c9 x_c6_c9 c9 g
x_c2b_c29 m_c29_c2b_c48 c29 g
x_c2b_c29 m_c2b_c29_sn c2b d
x_c3 m_sn_c3_c1 sn p
x_c3 x_c3_c6 c3 g
x_c31 m_c31_sn_dg4 c31 d
x_c31_c48 m_c31_c48_sn c31 g
x_c31_c48 x_c33_c48 c48 d
x_c31_dg4 x_c33_dg4 dg4 p
x_c33 m_c33_sn_c48 c33 d
x_c33 x_c31 sn d
x_c33_c48 x_c35_c48 c48 d
x_c33_dg4 m_c33_dg4_sn c33 d
x_c33_dg4 x_c35_dg4 dg4 p
x_c35 x_c35_2 c35 d
x_c35_2 m_c35_sn_sn c35 d
x_c35_2 x_c33 sn d
x_c35_3 x_c35_dg4 c35 d
x_c35_c48 x_c35 c35 d
x_c3_c6 m_c3_c6_c8 c3 g
x_c3_c8 m_c3_c8_c10 c3 g
x_c3_c8 m_c8_c3_c5 c8 g
x_c48 m_c48_sn_c101 c48 g
x_c48 x_sn_21 sn g
x_c48_2 m_c48_sn_sn c48 d
x_c48_2 x_sn_22 sn d
x_c48_3 x_c31_c48 c48 g
x_c48_3 x_sn_23 sn g
x_c48_dg2 m_c48_dg2_c111 c48 g
x_c5 m_sn_c5_c3 sn p
x_c5 x_c5_c6 c5 g
x_c52 m_sn_c52_sn sn d
x_c5_c6 m_c5_c6_c8 c5 g
x_c5_c6 m_c6_c5_c3 c6 g
x_c5_c8 m_c5_c8_c10 c5 g
x_c5_c8 m_c8_c5_c7 c8 g
x_c6_c7 m_c6_c7_c5 c6 g
x_c6_c7 m_c7_c6_c2 c7 g
x_c6_c9 m_c6_c9_c7 c6 g
x_c6_c9 m_c9_c6_c8 c9 p
x_c7_c8 m_c7_c8_c6 c7 g
x_c7_c8 m_c8_c7_c9 c8 p
x_c8 m_sn_c8_c8 sn g
x_c8 x_c1_c8 c8 g
x_c8_2 m_sn_c8_sn sn g
x_c8_2 x_c8 c8 g
x_c8_c9 m_c8_c9_av11 c8 p
x_c8_c9 m_c9_c8_c10 c9 p
x_cbar_dg2 m_cbar_dg2_c107 cbar p
x_cbar_dg2 m_dg2_cbar_c48 dg2 g
x_cp01_2 m_cp01_sn_sn cp01 p
x_cp01_3 m_cp01_sn_sn_2 cp01 p
x_cp01_3 x_c52 sn d
x_cp01_4 m_cp01_sn_sn_3 cp01 p
x_dg4 m_dg4_sn_c19 dg4 p
x_sn m_sn_sn_c20 sn d
x_sn m_sn_sn_c29 sn g
x_sn_10 m_sn_sn_sn_2 sn p
x_sn_10 x_c8_2 sn d
x_sn_11 m_sn_sn_sn_3 sn g
x_sn_11 x_cp01_2 sn d
x_sn_13 x_sn_12 sn d
x_sn_13 x_sn_14 sn d
x_sn_14 x_sn_17 sn d
x_sn_16 m_sn_sn_sn_5 sn g
x_sn_18 m_sn_sn_sn_4 sn d
x_sn_18 x_sn_13 sn d
x_sn_18 x_sn_17 sn d
x_sn_19 m_sn_sn_sn_10 sn d
x_sn_19 x_sn_17 sn d
x_sn_2 m_sn_sn_c20_2 sn g
x_sn_2 x_sn_3 sn g
x_sn_20 m_sn_sn_sn_6 sn d
x_sn_21 m_sn_sn_sn_12 sn g
x_sn_21 x_sn_19 sn g
x_sn_22 x_sn_20 sn d
x_sn_24 m_sn_sn_c101 sn g
x_sn_24 x_c48 sn g
x_sn_25 m_sn_sn_sn_13 sn d
x_sn_25 x_c48_2 sn d
x_sn_26 m_sn_sn_sn_14 sn d
x_sn_26 x_sn_25 sn d
x_sn_27 m_sn_sn_c101_2 sn g
x_sn_27 x_sn_24 sn g
x_sn_28 m_sn_sn_sn_15 sn d
x_sn_30 m_sn_sn_c105 sn g
x_sn_30 m_sn_sn_sn_17 sn g
x_sn_31 m_c101_sn_c54 sn d
x_sn_31 m_sn_sn_sn_16 sn g
x_sn_32 m_sn_sn_c107 sn g
x_sn_33 m_sn_sn_sn_18 sn g
x_sn_33 x_c103_2 sn g
x_sn_35 m_sn_sn_sn_19 sn g
x_sn_36 m_sn_sn_sn_21 sn g
x_sn_36 x_sn_32 sn g
x_sn_37 x_sn_34 sn d
x_sn_37 x_sn_42 sn d
x_sn_38 m_sn_sn_sn_20 sn g
x_sn_38 x_sn_43 sn g
x_sn_39 m_sn_sn_sn_22 sn g
x_sn_39 m_sn_sn_sn_24 sn g
x_sn_4 m_sn_sn_c29_2 sn g
x_sn_4 x_sn sn d
x_sn_41 m_sn_sn_sn_25 sn g
x_sn_41 x_sn_36 sn g
x_sn_42 m_sn_sn_sn_26 sn g
x_sn_42 m_sn_sn_sn_30 sn d
x_sn_43 m_sn_sn_sn_27 sn g
x_sn_43 m_sn_sn_sn_31 sn d
x_sn_44 m_sn_sn_sn_23 sn d
x_sn_44 x_sn_42 sn d
x_sn_45 m_sn_sn_sn_28 sn g
x_sn_45 m_sn_sn_sn_32 sn d
x_sn_46 m_sn_sn_sn_33 sn d
x_sn_47 m_sn_sn_sn_29 sn d
x_sn_47 m_sn_sn_sn_34 sn d
x_sn_48 m_sn_sn_sn_35 sn d
x_sn_49 m_sn_sn_sn_36 sn d
x_sn_6 m_sn_sn_c29_3 sn g
x_sn_6 x_sn_4 sn d
x_sn_9 m_sn_sn_c12 sn g
x_sn_9 m_sn_sn_sn sn p
```

### A.4 The river (Paraná de las Palmas), near the plant

Four polylines, `u,v` pairs, simplified to 25 m. Drawn only; no stop
touches them.

```
3004,6963 2626,7036 2161,7185 1408,7708 136,7902 -139,8014 -228,8079 -280,8242 -309,8217 -264,8126 -350,8195 -300,8284 -568,8691 -842,9225
-7402,9368 -7205,9286 -6358,9377 -5468,9399 -4371,9625 -4244,9713 -3978,9695 -3685,9570 -3564,9461 -3252,8949 -3029,8881 -2894,8883 -2480,9031 -1888,9443 -1426,9640 -1036,9668 -564,9514 -334,9240 -50,8583 192,8284 492,8161 1122,8265 1301,8225 1731,7979 2356,7452 2567,7374 3096,7269
-900,9273 -1004,9313 -1203,9313 -1368,9263 -1367,9232 -1648,9088 -1669,9114 -2316,8669 -2679,8572 -2724,8531 -2754,8347 -2760,8552 -2817,8534 -2847,8388 -2846,8548 -2920,8537 -2962,8388 -3005,8376 -2962,8531 -3139,8515 -3311,8550 -3473,8657 -3730,9033 -4004,9287 -4673,9202 -5371,8991 -6501,9038 -6830,9026 -7165,8945
-842,9225 -900,9273
```

## Appendix B — Hand-written stops

Each text is the stop's `desc`. Sources are for the record; the game names
none of them.

| Stop | Text | Basis |
|---|---|---|
| `x_av11_c10` | "The corner of the plaza, where Avenida 11 meets Calle 10. Paths cut diagonally across the square under the trees." | plaza: imagery |
| `m_av11_c12_c10` | "Avenida 11, along the side of the plaza. Benches under the trees, a shopping bag left on one of them." | plaza |
| `m_av11_c10_c8` | "Avenida 11 by the plaza. The parish church of San Isidro Labrador stands on this block, its doors shut." | OSM (Parroquia San Isidro Labrador) |
| `m_c10_av11_c9` | "Calle 10, along the plaza. On this side, shop fronts with their shutters down; across the street, the trees." | plaza; shops around it: imagery |
| `m_c10_c13_av11` | "Calle 10, on the plaza's far side. A bicycle leans against a tree, unlocked." | plaza |
| `m_av11_c8_c6` | "Avenida 11. The Banco Nación is on this block, its shutter down, and the Escuela Primaria Nº 9 a little further on." | OSM (Banco Nación, Av 11 245; EP 9, Av 11 256) |
| `m_av11_c6_c4` | "Avenida 11, outside the Correo Argentino office. A notice is taped to the inside of the glass, too faded to read from here." | OSM (Correo Argentino, Av 11 171) |
| `m_c6_c13_av11` | "Calle 6, outside the municipal hospital. The ambulance bay is empty, and a chain is looped through the doors' handles." | OSM (Hospital Intermedio Municipal "Aurelio Aleotti", Calle 6 560) |
| `m_c8_av11_c13` | "Calle 8, by the Delegación Municipal. Through the window, a row of plastic chairs where people used to wait." | OSM |
| `m_c7_acc_c20` | "The volunteer fire station is on this block. One bay door is open, and the bay is empty." | OSM (Bomberos Voluntarios de Lima) |
| `m_c117_c88_c84` | "The barrio's club runs along here behind a wire fence: tennis courts, a hall, a pool with leaves floating in it." | imagery (Club Barrio Atucha Lima) |
| `m_c90b_c117_c119` | "The courtyard in front of your row, in the Barrio Atucha. Four houses under red-tile roofs face the paths and the parking spaces. The neighbours' blinds are down." | imagery; canon (the home) |
| `m_c7_c10_c8` | "Calle 7. A pharmacy takes up the front of a house here, its window full of sun-faded posters." | Colegio de Farmacéuticos (Farmacia Fabio, Calle 7 Nº 324) |
| `m_c12_c13_c15` | "Calle 12, outside the Comisaría Zárate 2. A patrol car is parked across the entrance with its doors open." | OSM |
| `m_cbar_dg2_c107` | "The Camino a Baradero. A building-materials yard stands behind a wire fence: sand, bricks, stacked pipes." | directory listing (Casa Fierro Corralón, Camino a Baradero 337) |
| `x_c16_c7` | "The corner of Calle 16 and Calle 7. A repair shop's roller door is half up, tyres stacked beside it." | OSM (Alineación Esteban, Calle 16 Nº 470) |
| `x_acc_av11_c20` | "Where the Acceso a Lima meets Avenida 11. The petrol station's forecourt is empty, the nozzles hung up on the pumps." | APLA directory (D.A.P.S.A., Av 11 Nº 890) |
| `x_c113_c50` | "A corner in the Nueve de Julio neighbourhood. The almacén's door opens onto the corner itself, under a faded awning." | **designed** placement |
| `x_c15_dg4` | "Calle 15 crosses the railway here. A bell on a post beside the tracks, and nothing else." | OSM level crossing; Tom (bell only) |
| `x_c107_c2_c7` | "The level crossing on Calle 2. A bell on a post: no barrier, no lights." | OSM level crossing; Tom |
| `estacion_lima` | "Estación Lima. The station buildings, the platform, and the goods shed beside them. The platform is empty." | OSM |
| `fcm_crossing_6km` | "The tracks cross a country road here. A bell on a post, nothing else." | OSM; Tom |
| `fcm_crossing_11km` | "Another road crossing on the line, with its bell." | OSM; Tom |
| `atucha_halt` | "The Atucha halt: a platform beside the tracks, and not much else." | OSM (railway=halt) |
| `r111_767m` | "Calle 111, heading north out of town between fields. A side road branches west here." | OSM |
| `r111_973m` | "Calle 111, open country on both sides. Another side road branches off." | OSM |
| `r111_2752m` | "Calle 111. An unpaved road runs off to the west." | OSM |
| `r111_papermill` | "Calle 111. The paper mill stands off to the west, down a side road." | OSM (Celulosa Campana) |
| `r111_7180m` | "Calle 111, near the river. The Camino Provincial 038-03 branches off here." | OSM |
| `r111_7334m` | "Calle 111. The Camino Provincial 038-09 branches off here." | OSM |
| `atucha_gate` | "The road ends at the Atucha complex. The fence runs off both ways, and the gate is shut. Beyond it, the plant's domes." | OSM; canon (kept shut); La Nación (the domes). Gate position **unconfirmed** |
