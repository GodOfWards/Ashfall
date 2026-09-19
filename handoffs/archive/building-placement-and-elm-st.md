> **SUPERSEDED — the room schema it authors against no longer exists.**
>
> Written against v0.4.9. `handoffs/room-address-and-shelter.md` shipped in
> v0.4.12 and split the `building` field in two, so this file's room
> definitions would now author into the wrong one:
>
> - A house is `address:"214 Elm St"`, `building:null` (omitted) — not
>   `building:"214 Elm St"`. `building` now holds a building's *name* and
>   nothing else; a street address is `address`.
> - The unfinished-house set-piece in Part 1f is `address:"Elm St"`,
>   `building:"Unfinished House"`, `room:null` — the single-room convention
>   moved the name out of `room` and into `building`.
> - **Every room now needs `shelter`** (`"none"` or `"full"`), which this file
>   specs nowhere. The field order is `locationId, address, building, area,
>   room, shelter, desc, …`.
>
> **The label output this file describes is unaffected** — `roomLabel()`
> composes the same strings from the new fields. Only where the values are
> written changed. Everything else below — the placement grid, the street
> descriptions, the per-house contents — still stands.
>
> **#88 carries the live truth.** Read it before implementing any of this.

# Ashfall Handoff — Building placement, and the houses on Elm St

Current shipped version: v0.4.9
Implied version-change type: PATCH
Issue: #8 — Expand the map: building placement in the 8×8 grid

## What this is

The first half of #8, plus the rules the rest of it will follow.

#8's remaining scope opens with the real question: *"Which buildings go in the
44 new intersections and 81 new mid-blocks, and where."* Its own note says the
answer *"is a design question, not an implementation detail."* This handoff
settles that question as a **rule**, applies it to one street in full, and
leaves the other fifteen to short passes that copy the pattern.

The rule came out of reading the v0.4.1 street descriptions, and it is the
reason this pass is tractable: **the buildings are already written.** Mill St
has a feed mill with four bay doors, a weighbridge set into the pavement and a
conveyor bridge overhead. Cedar has a church with a cracked noticeboard and a
lot whose lines are freshly painted. Elm has a swing set with one chain snapped,
a basketball hoop over a garage door, a row of porches built by the same crew in
the same year. #8 is not mostly inventing buildings. It is making enterable what
the world already says is there.

**This handoff assumes `handoffs/map-building-identity-and-label-fit.md` has
shipped**, and relies on the `BUILDINGS` / `MAP_BUILDING_OFFSETS` seam it
establishes.

## Relevant existing state

Verified against `main` @ v0.4.9. Line numbers are v0.4.9's.

- **176 street nodes** — 64 intersections, 112 mid-blocks. **Nine carry a
  building today**, all of them in the original core: `main2nd`, `maple2nd`,
  `maple3rd`, `mid_main_1_3`, `mid_main_3_5`, `mid_poplar_1_2`,
  `mid_poplar_2_4`, `water1st`, `water2nd`. The four southern streets added in
  v0.4.1 — Dock, Mill, Cedar, Elm, 60 nodes — have **none**.
- **218 rooms in total, of which 42 are interiors.** The rest are street and
  mid-block nodes. This is the number to keep in view: the pass below adds 28
  interior rooms, a two-thirds increase in the interiors the game has.
- **Every building the game has is an apartment block, a shop, or a civic or
  industrial building.** A single-family house is a shape that does not exist
  yet. The closest precedent is an Acorn or Oak apartment: a few rooms wired to
  each other, entered from a hallway.
- **`LOCATIONS`** (`:848`) gives real (x,y,z) metres. Block size 100m, floor
  height 3m. A building floor gets one entry; `(x,y)` is the street node's, `z`
  is the floor's. Elm St is the row at `y:-100`. The five nodes this pass
  touches: `elm4th` (x:0), `mid_elm_2_4` (x:50), `elm1st` (x:200),
  `mid_elm_5_7` (x:450), `elm7th` (x:500).
- **`exitMinutes()`** (`:3503`) reads `exit.distanceM` only when both rooms
  share a `locationId`. A cross-Location exit computes from the two `LOCATIONS`
  entries instead, and **must not carry `distanceM`** — v0.4.7 deleted 26
  vestigial ones.
- **`applyComputedDirections()`** (`:1537`) rewrites compass words in
  cross-Location exit labels. Labels with no compass word — every building
  entrance and floor transition in the game — are left exactly as authored.
- **28 `SPAWN_POOLS`** (`:613`). Every pool this pass needs already exists;
  none is added.
- **`roomLabel()`** (`:3509`) composes `building`, `area` and `room`. Per #42,
  multi-room buildings put their name in `building`; single-room ones put the
  street there and the name in `room`. This pass follows that convention as it
  stands and does not touch #42.
- **`applyLoadedData()`** (`:4432`) sets `world = data.world` wholesale, so a
  save made before this ships keeps its old world and never sees the new rooms.
  That is true of every content pass since v0.4.0 and is not this one's problem
  — do not try to fix it here.
- **`validateLocations()`** (`:4478`) is a dev-only console helper that confirms
  every room's `locationId` resolves. It is the check for this pass.

## Rules / mechanics

Part 1 is the reusable framework. Part 2 applies it to Elm St. Everything here
is WORLD DATA.

### Part 1 — The placement rule

**A node gets at most one enterable building, and only where the node's existing
description already names a specific structure.**

Both halves matter.

*Already names a specific structure* means the description points at a building,
not at an object that implies one and not at buildings in general. On Elm, "a
corner lot with a swing set in the side yard" and "a basketball hoop bolted
above a garage door" qualify; "big yards out here, and the hedges have started
meeting across the driveways" does not, and neither does "a garden hose still
stretched across the sidewalk" — a hose belongs to a house the text never
places. The test is checkable against the file rather than a number someone
picked, and it guarantees the pass never puts a door where shipped text says
there is a field.

*At most one* is the crowd-control clause. `mid_elm_5_7` reads "Two houses, then
a lot that was never built on" — one of those two becomes enterable and the
other stays scenery, which is what most of the street is. A street is mostly
something you walk along.

**Do not edit a description to make a node qualify.** If a node should have a
building and its text does not support one, that is a finding for an issue, not
a licence to rewrite shipped content.

On Elm this yields 5 of 15 nodes. Expect a similar share elsewhere: roughly a
third of a street, concentrated where the text is most specific.

### Part 1b — The address convention

Houses are named by street address. The convention, which belongs as a comment
in WORLD DATA beside `LOCATIONS`' coordinate convention since it derives from
the same grid:

> **The hundreds digit is the block, counted along the street. The last two
> digits are per-instance content.**
>
> Blocks are numbered 1–7 between the eight cross-streets, running west→east on
> a named street and south→north on a numbered one. From a node's `LOCATIONS`
> entry: an east-west street's block index is `floor(x/100) + 2`, a north-south
> street's is `floor(y/100) + 5`.
>
> A mid-block node takes its own block. An **intersection** node takes the block
> *beyond* it — east, or north — because a corner lot fronts the block it
> begins. At the far edge, where there is no block beyond (9th St on a named
> street, Water St on a numbered one), it takes the block behind instead.

Worked, for the nodes below: `elm4th` at x:0 is block 2 → the 200s.
`mid_elm_2_4` at x:50 is block 2 → the 200s. `elm1st` at x:200 is block 4 → the
400s. `mid_elm_5_7` at x:450 is block 6 → the 600s.

**Write no numbering function.** The hundreds digit is derivable, but an address
is a string on a room, authored once — per-instance content, which the Project
Guide is explicit belongs as a literal at its instance. The convention is a
comment so later streets follow it; it is not code.

The last two digits are chosen to look like a town rather than a scheme — 214,
not 200. Anything in range is correct; they are content.

### Part 1c — What goes in `BUILDINGS`, and what doesn't

**A house gets no `BUILDINGS` entry.** Per the previous handoff, `BUILDINGS`
holds buildings the map could name, and its `anchor` field exists for the map's
benefit. A house carries no marker, so an entry would add nothing and would put
its address in a second place alongside the `building` field its own rooms
already carry.

**Houses get no `MAP_BUILDING_OFFSETS` entry either, so no map marker.** This is
deliberate and is the reason the previous handoff's seam exists. Four markers on
Elm means roughly forty town-wide, and at half a block apart their labels
overlap outright — the collision that handoff explicitly leaves unsolved. The
map names landmarks; houses are found by walking.

The landmark buildings later streets add — Cedar's church, Mill's feed mill —
**do** get both, and the offsets need choosing so their labels clear their
neighbours. That is those passes' work, not this one's.

### Part 1d — The house room kit

A house draws from this menu. It is a menu, not a floorplan: which rooms a house
has, and how many floors, follow from what its street description says about it.

| Room | Flags | Containers / pools | `floorCap` |
|---|---|---|---|
| Entry Hall | `cannotHaveFire` | closet — `clothing`, `residential_personal` | 60 |
| Kitchen | `hasStove`, `cannotHaveFire` | stove (8kg) — `kitchen_perishable`, `kitchen_tools`; cabinet — `kitchen_nonperishable`, `kitchen_tools`; fridge — `kitchen_perishable` | 50 |
| Living Room | `cannotHaveFire` | shelf or media unit — `recreation`, `electronics`, `documents_lore` | 60 |
| Bedroom | `sleepSpot:"bed"`, `cannotHaveFire` | dresser — `clothing`, `residential_personal`; nightstand — `residential_personal`, `documents_lore` | 50 |
| Bathroom | `cannotHaveFire` | cabinet — `hygiene`, `medical_otc`; under-sink — `cleaning_supplies` | 30 |
| Stairs | `cannotHaveFire` | none | 40 |
| Landing | `cannotHaveFire` | none | 40 |
| Garage | `cannotHaveFire` | workbench — `tools_general`, `tools_workshop`; shelving — `fuel_fire`, `outdoor_camping` | 70 |

Every value matches something already in the file: the 8kg stove is
`HEAT_CONTAINER_CAPACITY_KG`, the empty stairwell matches `oak_stairs`, the 70kg
garage matches `auto_shop`, and `cannotHaveFire` on every interior matches Acorn
and Oak throughout.

**Spawn pools carry the household's character**, one or two per house on top of
the table: `baby_items` where a child lived, `pet_supplies`, `self_defense` at
the edge of town. These are the per-house variation; everything else is the kit.

**Containers ship empty** — `items:[]` with `spawnPools` set and no
`spawnRolled`, so `doOpenContainer()` rolls them on first open. Hand-place items
only where the street description already names a specific object, and set
`spawnRolled:true` on that container so the roll never overwrites it.

**Rooms are distinguished by `room`, not by `area`.** A house has no apartments,
so `area` stays `null` and two bedrooms become "Front Bedroom" and "Back
Bedroom" — otherwise both print as `"214 Elm St, Bedroom"`.

### Part 1e — Wiring a house

- **One `LOCATIONS` entry per floor.** `<id>_f0` at the street node's exact
  `(x,y)` with `z:0`; `<id>_f1` at the same `(x,y)` with `z:3`.
- **The street node gains one exit** into the entry hall. No compass word in the
  label, so `applyComputedDirections()` leaves it alone. This edits the existing
  room in `buildElmSt()`.
- **The entry hall gains the return exit**, labelled `"Step outside"` — the
  wording `oak_hallway1` already uses.
- **Same-floor exits carry `distanceM`.** Suggested: hall↔kitchen 5,
  hall↔living 5, hall↔bathroom 4, hall↔stairs 4, kitchen↔living 5,
  landing↔bedroom 4, landing↔bathroom 4, hall↔garage 6.
- **Cross-floor and street↔hall exits carry no `distanceM`.** Both are
  cross-Location, so `locationDistance()` computes them. A street↔hall exit
  spans 0 metres and costs `MIN_MOVE_MIN` — one minute — exactly as entering Oak
  does today. Stairs cost the same, from the 3m floor height.
- **Stair labels are `"Go upstairs"` / `"Go downstairs"`**, matching
  `oak_stairs`. No compass word, so they are left as authored — note that
  `computeDirection()` would otherwise return "up"/"down" here, since the two
  Locations differ only in `z`.

### Part 2 — Elm St

Five nodes qualify. Four become houses; one becomes a set-piece.

Descriptions are the coding session's to write, per the Project Guide's Part 1
checklist. What is specified here is **the detail each room must answer to** —
the thing the street already says, which the interior has to be consistent with.
Match the existing voice; do not invent a new one.

#### 214 Elm St — `elm4th`

> *"A corner lot with a swing set in the side yard, one chain snapped and the
> seat hanging vertical."*

A family with a young child, on the corner. The largest of the four: two
storeys, 9 rooms. `LOCATIONS`: `elm214_f0` `{x:0, y:-100, z:0}`, `elm214_f1`
`{x:0, y:-100, z:3}`.

- **f0** — Entry Hall, Kitchen, Living Room, Half Bath, Stairs
- **f1** — Landing, Front Bedroom, Back Bedroom, Bathroom

The child is the through-line: the back bedroom is theirs, and its dresser draws
`baby_items` alongside `clothing`. The swing set is outside and stays outside —
the interior should not mention it.

#### 246 Elm St — `mid_elm_2_4`

> *"A block of Elm where every house has the same porch, built by the same crew
> in the same year. A stuffed rabbit lies in the gutter, rained on until it lost
> its shape."*

One of the identical tract houses. Single storey, 5 rooms. `LOCATIONS`:
`elm246_f0` `{x:50, y:-100, z:0}`.

- Entry Hall, Kitchen, Living Room, Bedroom, Bathroom

The sameness is the point — this is the house the other porches belong to as
much as this one. The bedroom dresser draws `pet_supplies`. The node's floor
already carries `stuffed_toy ×1`; leave it where it is, in the gutter.

#### 402 Elm St — `elm1st`

> *"Elm crosses 1st here. A basketball hoop is bolted above a garage door, the
> net long gone."*

Single storey with the attached garage the hoop is bolted to, 6 rooms.
`LOCATIONS`: `elm402_f0` `{x:200, y:-100, z:0}`.

- Entry Hall, Kitchen, Living Room, Bedroom, Bathroom, Garage

The garage is what makes this house worth entering rather than a fourth
bedroom-and-kitchen — it is the only `tools_workshop` draw on the street.

#### 655 Elm St — `mid_elm_5_7`

> *"Elm thins out here. Two houses, then a lot that was never built on."*

The eastern of the two. Two storeys but smaller than 214, 7 rooms. `LOCATIONS`:
`elm655_f0` `{x:450, y:-100, z:0}`, `elm655_f1` `{x:450, y:-100, z:3}`.

- **f0** — Entry Hall, Kitchen, Living Room, Stairs
- **f1** — Landing, Bedroom, Bathroom

Last house before the street runs out. The bedroom dresser draws `self_defense`
alongside `clothing` — the edge of town, and whoever lived here knew it.

#### The unfinished house — `elm7th`

> *"Elm runs out of houses just short of 7th. The last two lots are foundations
> and framing that never got walls."*

**Not a house. A set-piece**, in the shape of the Riverbank: one room, no
containers, entered from the street and nothing else. `LOCATIONS`:
`elm_frame_f0` `{x:500, y:-100, z:0}`.

- One room. `building:"Elm St"`, `room:"Unfinished House"` — the single-room
  convention, the same shape `riverbank` and `cornerstore` use.
- **No `cannotHaveFire`.** It is open to the sky, so a campfire can be built
  here. That is the point of including it: a roofed, defensible-looking space
  that is not one, and the only such spot on the street.
- **No containers.** Loose building materials on the floor instead — `plank`
  and `scrap_metal`, hand-placed. `floorCap:60`.
- Entry label: `"Step inside the framing"`.

This is the node that shows a building need not be an interior, and later
streets should have one of their own rather than four houses in a row.

#### Structure

All five go in **one new builder, `buildElmStHouses()`**, added to
`makeDefaultWorld()`'s list after `buildElmSt()`.

This departs from v0.4.7's one-builder-per-building rule deliberately: that rule
was written for eleven buildings, and #8 finishes with roughly forty. One
builder per street's houses keeps `makeDefaultWorld()` readable and matches the
street builders' own logic — a room belongs to the street its id names. Later
streets add `buildCedarStHouses()` and so on. Landmark buildings large enough to
deserve it — the feed mill, the church — should still get their own builder,
as the existing buildings do.

## Design decisions to make during implementation

Record the choice in the changelog's Notes/assumptions or Documentation section
rather than choosing silently.

1. **Whether 214's upstairs bathroom and its ground-floor half bath are both
   worth having.** Nine rooms is the largest interior in the game after Acorn.
   Dropping the half bath makes it 8 and loses little. Recommended: keep both —
   a two-storey family house with one bathroom reads wrong, and the half bath is
   the cheapest room in the kit.
2. **The last two digits of each address.** 214 / 246 / 402 / 655 are proposed
   above and are content; any numbers in the right hundreds are correct. If they
   change, change them in the handoff's spirit — irregular, not round.
3. **Whether the garage at 402 is reachable from the hall, the street, or both.**
   Recommended: from the hall only, at `distanceM:6`. A second street exit would
   make the node's exit list longer than any other on Elm for no gameplay gain.

None of these changes the versioning tier — all stay PATCH.

## Data / schema changes

- **New state fields:** none.
- **Item schema:** untouched. No new item, tag, category or registry entry —
  every item placed comes from `ITEM_REGISTRY` via `itemsFromRegistry()`.
- **Room / container / exit schema:** untouched. No new field on any of the
  three; the new rooms use the schema as documented.
- **`LOCATIONS`:** 7 new entries — `elm214_f0`, `elm214_f1`, `elm246_f0`,
  `elm402_f0`, `elm655_f0`, `elm655_f1`, `elm_frame_f0`.
- **`BUILDINGS` / `MAP_BUILDING_OFFSETS`:** no entries added. See Part 1c.
- **`SPAWN_POOLS`:** no new pool, no change to an existing one.
- **`SAVE_KEY` is unchanged.** PATCH, so `versionCompat()` still yields `0.4`
  and existing browser saves keep loading — carrying their own world, without
  these rooms, as every content pass since v0.4.0 has done.

## In scope

- The placement rule, the address convention and the house room kit, written
  into WORLD DATA as comments so later streets follow them.
- 28 new rooms in a new `buildElmStHouses()`: four houses (9, 5, 6 and 7 rooms)
  and one set-piece.
- 7 new `LOCATIONS` entries.
- One new exit on each of the five existing Elm street rooms.
- `buildElmStHouses()` added to `makeDefaultWorld()`.

## Explicitly out of scope

- **The other fifteen streets.** Cedar's church and Mill's feed mill are named
  here as evidence that the rule generalises, not as work to do. Each gets its
  own short pass.
- **Anything with a map marker.** No `BUILDINGS` or `MAP_BUILDING_OFFSETS`
  entry is added, so `renderMapClose()` is not touched and the map draws exactly
  the eleven markers it draws today.
- **#42** — the `building` field's two meanings. This pass follows the existing
  convention; it does not fix or extend it.
- **#7 (Lore development).** The `documents_lore` pool is drawn from, as every
  residential container already does, but no lore item is written, no resident is
  named, and no readable-text schema is added. Naming the families who lived on
  Elm is #7's call, and this pass deliberately leaves the addresses unattached to
  people so #7 still has it to make.
- **#6 (Rooftops).** Two of these houses have a second storey. Neither gets roof
  access; that issue decides where rooftops are plausible.
- **#15** — container property tags, respawn, fauna. New containers here use
  `spawnPools` exactly as v0.4.0 defined them and nothing more.
- **New items, new pools, new mechanics.** If a room seems to need one, it is the
  wrong room.
- **The v0.4.2 wish-list building types** — pet store, nursery, sporting-goods
  store. All commercial, none of them Elm.

## Sections touched

**WORLD DATA only.** This is a content pass: room definitions, containers, exits,
descriptions, and the static positional data in `LOCATIONS`. Nothing in ACTIONS,
SIMULATION, PLAYER STATE, PERSISTENCE or RENDERING — per the Project Guide, a
content pass modifies `makeDefaultWorld()` and the definitions it assembles, and
must not touch movement, inventory or simulation code.

If some part of this seems to need a mechanics change, stop: it is a sign the
content is wrong, not the mechanics. Every flag, pool, container shape and exit
form used here already exists and is already exercised by a shipped room.

## UI changes

None beyond the content itself. No new button, panel, status display or wording
outside the new rooms' own text. The player sees five new exits off Elm St, and
what is behind them.

The map is unchanged — no new marker, no moved marker.

## Dependencies / issue linkage

- **Fulfils part of #8.** The pull request should **not** close it: fifteen
  streets remain. Edit #8 down to what is actually left rather than leaving its
  "44 new intersections and 81 new mid-blocks" claim standing, and reference the
  framework this pass established so the later passes start from it.
- **Depends on `handoffs/map-building-identity-and-label-fit.md`** (#39, #16)
  having shipped — Part 1c relies on its `BUILDINGS` / `MAP_BUILDING_OFFSETS`
  split. Nothing else in this pass does.
- **Expect to defer, and file at wrap-time:** one issue per remaining street, or
  one covering the rest of #8 under the framework, whichever reads better once
  the first street is real. If the pass surfaces a description that wants a
  building but does not support one, that is a second issue.
- **#7** is unblocked in a small way — four addressed houses give a letter or a
  utility bill somewhere concrete to be found. Not a prerequisite either way.

## Open questions for Tom

None. The placement rule, the address convention, the house shape, the map-marker
decision and the five nodes were all settled during planning. The three items
under "Design decisions" are narrow implementation calls.

## After implementation

Open a pull request carrying the version bump and a new `CHANGELOG.md` entry per
`docs/CHANGELOG_GUIDE.md`, referencing this handoff by path and recording all
three "Design decisions" resolutions in it. **Do not write `Closes #8`** — edit
that issue down to the remaining streets instead, and file the deferred work as
new issues referenced from the pull request.

For **Validation performed**, the claims worth proving are:

- `git diff origin/main...HEAD -- ashfall.html` is the diff of record, and every
  hunk in it is inside WORLD DATA.
- `validateLocations()` reports every room resolving a `locationId`, with the 28
  new rooms in the world.
- **Every new room is reachable**, and every new exit has a return: walk the exit
  graph from `elm4th` and confirm all 28 rooms are reached and that no exit is
  one-way.
- **No cross-Location exit carries `distanceM`, and every same-Location exit
  has one** — the v0.4.7 invariant, now applied to 30-odd new exits.
- **Nothing outside Elm changed.** The diff should touch `buildElmSt()` (five
  exit additions), `LOCATIONS` (seven additions), `makeDefaultWorld()` (one
  line), the new builder, and the convention comments. Anything else is a
  mistake.
- Syntax check on the extracted `<script>` body, and a runtime check under a DOM
  stub completing module init and a first render.
