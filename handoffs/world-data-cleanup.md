# Ashfall Handoff — WORLD DATA cleanup: street/building split, vestigial exit fields, registry duplicate

Current shipped version: v0.4.6
Implied version-change type: PATCH
Issues: #3 — Split `buildStreetsAndOutdoor()` by town/location · #4 — Strip
vestigial `distanceM` from cross-Location exits · #5 — `bandage` /
`bandages` registry naming duplicate

## What this is

Three `tier-0` cleanups that all land in WORLD DATA, taken as one pass. Both
#3 and #4 say in their own text that they are "safe to do opportunistically
during an unrelated WORLD DATA pass"; this is that pass, and #5 joins because
it is the same section and the same tier.

No behavior changes. No new state. `SAVE_KEY` is untouched.

Ordering inside the pass matters: **do #4 and #5 first, then #3.** #3 moves
185 rooms between functions, which invalidates every line number in the other
two.

## Relevant existing state

Verified by reading `ashfall.html` at v0.4.6 and by executing
`makeDefaultWorld()` out of the file; counts below are measured, not
estimated.

**World shape.** 218 rooms total. 185 of them are street/outdoor, built by
two functions: `buildStreetsAndOutdoor()` (`:1383`, 60 rooms) and
`buildOuterStreets()` (`:2027`, 125 rooms). Five buildings have their own
functions already — `buildAcornApartments()` (`:1078`),
`buildOakApartments()` (`:3133`), `buildAutoWorkshop()` (`:3198`),
`buildPoliceStation()` (`:3223`), `buildRiversideFreight()` (`:3247`).
`makeDefaultWorld()` (`:3315`) `Object.assign`s all seven together and
returns `applyComputedDirections(world)`.

**Every street/outdoor room has its own `locationId`** — 185 rooms, 185
distinct location ids. So "split by location", as #3 words it, cannot mean
`locationId`; the only meaningful seam is the street. Room ids already encode
it: `maple3rd` is the Maple/3rd intersection, `mid_dock_2_4` is the Dock St
block between 2nd and 4th. Intersections are named for the horizontal
(named) street, so named streets own 15 rooms each (8 intersections + 7
mid-blocks) and numbered streets own 7 each (mid-blocks only).

**The current seam cuts through ten of the sixteen streets.** It was drawn
as "original core vs. v0.4.1 outer ring", not by street:

| Street | in `buildStreetsAndOutdoor()` | in `buildOuterStreets()` | split |
|---|---|---|---|
| Dock, Mill, Cedar, Elm | 0 each | 15 each | |
| Maple, Main, Water | 9 each | 6 each | ✅ |
| Poplar | 8 | 6 | ✅ |
| 6th, 7th, 9th | 0 each | 7 each | |
| 4th, 2nd, 1st, 3rd, 5th | 3 each | 4 each | ✅ |

**`buildStreetsAndOutdoor()` also contains four buildings and an outdoor
set-piece, not just streets.** The v0.2.8 modularity pass extracted one
function per building but left these behind — seven interior rooms plus the
riverbank:

| Rooms | Line | What |
|---|---|---|
| `cornerstore`, `cornerstore_apt` | `:1521` | Corner Store + apartment above |
| `pharmacy`, `pharmacy_apt` | `:1565` | Pharmacy + apartment above |
| `storage` | `:1623` | Storage Facility |
| `riverbank` | `:1651` | Riverbank set-piece |
| `hardware`, `hardware_apt` | `:1721` | Hardware Store + apartment above |

#3's text says the function "still mixes four streets with the riverbank and
the alley." That understates it: four whole buildings are in there too. The only
core rooms that are neither building nor street are `outside` and `alley`.

**Exit travel time.** `exitMinutes()` (`:3422`):

```js
const d = (fromLoc === toLoc) ? exit.distanceM : locationDistance(fromLoc, toLoc);
```

`distanceM` is read **only** when both rooms share a `locationId`. Measured
across the built world: **706 cross-Location exits, of which 26 still carry a
`distanceM` that is never read**; **68 same-Location exits, of which 0 are
missing one**. The schema comment at `:342-349` already describes the
bimodal shape the pass will finish making true.

**One `distanceM` is synthesized at runtime and must survive.**
`getExitsForRoom()` (`:3809`) pushes a window-climb exit carrying
`distanceM:4`. Both windows connect rooms inside one Location —
`2a-transom` joins `hallway2`/`living` (both `acorn_f1`), `1b-alley` joins
`alley`/`onebee` (both `acorn_f0`) — so that value **is** read by
`exitMinutes()`. Stripping it would make window climbs cost `NaN` minutes.

**Registry duplicate.** `:405` `bandages: { name:"Bandages",
category:"Medical", unitWeight:0.05 }` and `:470` `bandage: { name:"Bandage",
category:"Medical", unitWeight:0.05 }` are identical but for the display
name. Neither carries `restores`, `verb`, `durability` or tags. Usage
diverges: `bandages` has one `SPAWN_POOLS` entry (`:661`) and six world
placements (`:1128`, `:1223`, `:1323`, `:1534`, `:1573`, `:1761`); `bandage`
is the output of the `RECIPES` entry at `:280-282`. No code anywhere compares
either display name — `grep '"Bandage'` matches only the two registry lines.

**Stacking.** `STACKABLE` (`:249`) includes `"Medical"`, and the detail view
renders quantity as `` ` ×${it.qty} — ${total} kg ` `` (`:4783`).

**Saves restore the world wholesale.** `applyLoadedData()` (`:4334`) does
`world = data.world` — it does not rebuild from `makeDefaultWorld()`. A room
id renamed in the builders therefore would not strand an existing save's
navigation, but it *would* silently miss `backfillLocationIds()` and
`backfillContainerFields()`, both of which look rooms up by id in a fresh
`makeDefaultWorld()`. **This pass renames no room ids and no container ids.**

## Rules / mechanics

### Part 1 — #4: strip the 26 vestigial `distanceM` fields

Remove the `distanceM` key from exactly these 26 exits, leaving `{ to, label }`
(plus `doorId` where present). Every one crosses a Location boundary, so the
field is dead.

| From → To | Locations | value |
|---|---|---|
| `balcony` → `alley` | `acorn_f1` → `acorn_f0` | 8 |
| `stairs2` → `stairs1` | `acorn_f1` → `acorn_f0` | 15 |
| `stairs1` → `stairs2` | `acorn_f0` → `acorn_f1` | 15 |
| `hallway1` → `mid_poplar_1_2` | `acorn_f0` → `mid_poplar_1_2` | 8 |
| `alley` → `mid_poplar_1_2` | `acorn_f0` → `mid_poplar_1_2` | 15 |
| `alley` → `balcony` | `acorn_f0` → `acorn_f1` | 8 |
| `main2nd` → `cornerstore` | `main2nd` → `cornerstore_f0` | 5 |
| `cornerstore` → `main2nd` | `cornerstore_f0` → `main2nd` | 5 |
| `cornerstore` → `cornerstore_apt` | `cornerstore_f0` → `cornerstore_f1` | 5 |
| `cornerstore_apt` → `cornerstore` | `cornerstore_f1` → `cornerstore_f0` | 5 |
| `pharmacy` → `mid_main_1_3` | `pharmacy_f0` → `mid_main_1_3` | 5 |
| `pharmacy` → `pharmacy_apt` | `pharmacy_f0` → `pharmacy_f1` | 5 |
| `pharmacy_apt` → `pharmacy` | `pharmacy_f1` → `pharmacy_f0` | 5 |
| `water2nd` → `storage` | `water2nd` → `storage_f0` | 5 |
| `storage` → `water2nd` | `storage_f0` → `water2nd` | 5 |
| `hardware` → `mid_main_1_3` | `hardware_f0` → `mid_main_1_3` | 5 |
| `hardware` → `hardware_apt` | `hardware_f0` → `hardware_f1` | 5 |
| `hardware_apt` → `hardware` | `hardware_f1` → `hardware_f0` | 5 |
| `maple2nd` → `industrial_floor` | `maple2nd` → `industrial_f0` | 5 |
| `maple3rd` → `police_lobby` | `maple3rd` → `police_f0` | 5 |
| `oak_hallway1` → `mid_poplar_2_4` | `oak_f0` → `mid_poplar_2_4` | 8 |
| `oak_stairs` → `oak_hallway2` | `oak_f0` → `oak_f1` | 10 |
| `oak_hallway2` → `oak_stairs` | `oak_f1` → `oak_f0` | 10 |
| `auto_shop` → `mid_main_3_5` | `auto_shop_f0` → `mid_main_3_5` | 5 |
| `police_lobby` → `maple3rd` | `police_f0` → `maple3rd` | 5 |
| `industrial_floor` → `maple2nd` | `industrial_f0` → `maple2nd` | 5 |

**Do not touch `:3809`** — `exits.push({ to:target, label:"Climb through the "
+ w.label, distanceM:4 })`. That exit is same-Location and the value is live.
It is also not WORLD DATA; it is built in WORLD INTERACTION at render time.

**Do not** add `distanceM` anywhere, and do not touch any of the 68
same-Location exits, all of which already carry it.

### Part 2 — #5: consolidate on `bandage`

They are true duplicates. **Keep `bandage` (singular); delete the `bandages`
entry at `:405`.**

Why singular survives, given both forms exist across Medical:

1. It is the `RECIPES` output (`:280-282`). Keeping the plural would make
   "Craft a bandage" produce **Bandages ×1**.
2. Medical stacks, and the view appends `×N`. A bandage is a discrete
   countable thing, so **Bandage ×4** is right and **Bandages ×4** is
   ambiguous — four bandages, or four boxes?
3. The registry's other plurals (`Painkillers`, `Vitamins`, `Gauze rolls`,
   `Prescription bottles`) are mass or packaged nouns where `×N` means N
   containers. A bandage is not one of those.

Repoint all seven `bandages` references to `bandage`, preserving every
quantity exactly:

| Line | Context |
|---|---|
| `:661` | `SPAWN_POOLS` entry — `{ itemId:"bandages", weight:8, qtyMin:1, qtyMax:3 }` |
| `:1128` | placement, `qty:4` |
| `:1223` | placement, `qty:2` |
| `:1323` | placement, `qty:2` |
| `:1534` | placement, `qty:3` |
| `:1573` | placement, `qty:5` |
| `:1761` | placement, `qty:2` |

The `RECIPES` entry at `:280-282` already says `bandage` and needs no change.

This is the one part of the pass with a visible effect: six placements and
one loot pool now display "Bandage" instead of "Bandages". Weight, category,
stacking and spawn odds are identical. Note it in the changelog as a display
change, not a silent one.

### Part 3 — #3: one function per street, one per building

Pure code motion. Every room definition moves verbatim — same id, same
`locationId`, same `desc`, same `exits`, same containers, same floor items.
Nothing is renamed, reworded, added or removed.

**Assignment rule: a room belongs to the street its id names.** `maple3rd`
and `mid_maple_1_3` → Maple St. `mid_3rd_e_ma` → 3rd St. The rule is
mechanical for 175 of the 176 street nodes; `outside` and `alley` are handled
below.

**Five new building functions**, matching the existing `buildOakApartments()`
pattern and placed beside the other building builders:

| Function | Rooms |
|---|---|
| `buildCornerStore()` | `cornerstore`, `cornerstore_apt` |
| `buildPharmacy()` | `pharmacy`, `pharmacy_apt` |
| `buildHardwareStore()` | `hardware`, `hardware_apt` |
| `buildStorageFacility()` | `storage` |
| `buildRiverbank()` | `riverbank` |

**Sixteen new street functions**, each merging that street's core and outer
nodes into one place:

| Function | Rooms | Function | Rooms |
|---|---|---|---|
| `buildDockSt()` | 15 | `buildSixthSt()` | 7 |
| `buildMillSt()` | 15 | `buildFourthSt()` | 7 |
| `buildCedarSt()` | 15 | `buildSecondSt()` | 7 |
| `buildElmSt()` | 15 | `buildFirstSt()` | 7 |
| `buildMapleSt()` | 15 | `buildThirdSt()` | 7 |
| `buildPoplarSt()` | 15 (incl. `outside`) + `alley` | `buildFifthSt()` | 7 |
| `buildMainSt()` | 15 | `buildSeventhSt()` | 7 |
| `buildWaterSt()` | 15 | `buildNinthSt()` | 7 |

`buildStreetsAndOutdoor()` and `buildOuterStreets()` are then deleted, and
`makeDefaultWorld()` (`:3315`) lists all 21 new builders alongside the five
existing building ones. Keep the `Object.assign` shape and the
`applyComputedDirections(world)` return exactly as they are.

`buildOuterStreets()`'s existing `// DOCK ST` … `// 9TH ST` group comments
(sixteen of them) are **deleted, not moved** — the function names now carry
what those comments were carrying. Do not re-add them as headers above the
new functions.

The room count must be 218 before and after, and `Object.keys()` of the
assembled world must be identical as a set.

## Design decisions to make during implementation

One genuine placement call, plus one that the room counts already decide.
Record the outcome of each in the changelog's Notes/assumptions.

1. **Where `outside` goes — settled, stated here so it isn't re-opened.**
   It is the Poplar St / 1st St intersection carrying a legacy id from before
   the grid existed, so the mechanical naming rule doesn't reach it. The
   counts settle it: every named street owns 15 rooms (8 intersections + 7
   mid-blocks) except Poplar, which owns 14 — because its 1st St crossing
   *is* `outside`. Put it in **`buildPoplarSt()`** and all eight named
   streets are 15, all eight numbered streets are 7, with `alley` the single
   exception. Add a one-line comment at the definition noting the id is
   historical. **Do not rename it to `poplar1st`** — see "Saves restore the
   world wholesale".

2. **Where `alley` goes — genuinely open.** `building:"Poplar St"`, `locationId:"acorn_f0"` —
   it is the outdoor alley behind Acorn Apartments, reachable from
   `mid_poplar_1_2` and from `balcony` by fire escape, and it is one end of
   the `1b-alley` window. So it reads as either Poplar St's or Acorn
   Apartments'. **Recommended: `buildPoplarSt()`**, keeping
   `buildAcornApartments()` strictly interior and matching the room's own
   `building` field.

Neither affects behavior; both only decide which function holds the literal.

## Data / schema changes

None. No state fields, no item schema fields, no room/container/exit schema
fields.

The EXIT SCHEMA comment at `:342-349` already documents the post-#4 shape
correctly ("Cross-Location: `{ to, label }` — no `distanceM`"), so it needs no
edit — Part 1 makes the code match a comment that was already right.

One item is removed from `ITEM_REGISTRY` (`bandages`), which is a registry
content change, not a schema change.

## In scope

- [ ] 26 cross-Location exits lose `distanceM`.
- [ ] `bandages` registry entry deleted; 7 references repointed to `bandage`.
- [ ] 5 building functions extracted from `buildStreetsAndOutdoor()`.
- [ ] 16 street functions replace `buildStreetsAndOutdoor()` and
      `buildOuterStreets()`, merging each street's core and outer nodes.
- [ ] `makeDefaultWorld()` updated to call all 26 builders.
- [ ] The 16 `// <STREET> ST` group comments deleted.
- [ ] `GAME_CONFIG.VERSION` bumped (PATCH).
- [ ] `CHANGELOG.md` entry naming this handoff by path.

## Explicitly out of scope

- **Renaming anything.** No room id, container id, or item id other than the
  `bandages` deletion. See "Saves restore the world wholesale" above.
- **`:3809`'s `distanceM:4`.** Live value; also not WORLD DATA.
- **The comment and magic-number pass (#33).** It touches
  ACTIONS/SIMULATION and UI/RENDERING, and `CLAUDE.md` forbids one change
  spanning WORLD DATA and mechanics. It also has to come after this pass:
  its entire audit is expressed in line numbers that Part 3 invalidates.
- **Giving `bandage` any mechanical behavior.** `restores`, a `verb`, tags,
  and the "Craft a bandage" dead end all belong to #23 (illness system).
  Consolidating the duplicate does not make the item useful and should not
  try to.
- **Placing buildings in the 44 new intersections and 81 new mid-blocks.**
  That is #8. The outer nodes keep their `containers:[]` exactly as they are.
- **Splitting by *town*.** #3's title offers "town or location" as
  alternatives; there is one town and no region concept in the data model
  (see #15), so street is the only available seam. Nothing here creates one.
- **Re-tuning any travel time.** The 26 stripped values were already unread;
  displayed minutes must not move.

## Sections touched

**WORLD DATA only**, and within it: the room builder functions,
`makeDefaultWorld()`, `ITEM_REGISTRY`, and `SPAWN_POOLS`.

Content-only in the Project Guide's sense — no ACTIONS, no SIMULATION, no
PERSISTENCE, no UI/RENDERING. The coding session can skip everything below
`makeDefaultWorld()` in the file apart from reading `exitMinutes()` once to
confirm Part 1's premise.

## UI changes

One, from Part 2: six world placements and one loot pool now read
**"Bandage ×N"** instead of **"Bandages ×N"**. Nothing else the player sees
changes — same rooms, same exits, same labels, same travel times, same map.

## Dependencies / issue linkage

Fulfils **#3**, **#4** and **#5**. The pull request carries
`Closes #3`, `Closes #4`, `Closes #5`.

Blocks **#33**, which must run after this pass for the two reasons in
"Explicitly out of scope".

Not a prerequisite for and not blocked by #8 (buildings in the new blocks),
though #8 becomes easier afterwards: a new building on Cedar St gets added to
`buildCedarSt()` rather than appended to a 125-room block.

Nothing is expected to be deferred. If the pass does surface something,
file it as a new issue at wrap-time and reference it in the PR; if it
doesn't, say so in the changelog's Documentation section per `CLAUDE.md`.

## Open questions for Tom

None. `outside`'s placement is settled by the room counts, and `alley`'s is
a narrow call with a recommended default — both under "Design decisions to
make during implementation" above.

## Validation

This pass claims no behavior change for Parts 1 and 3, so prove it rather
than asserting it. Per the Project Guide's Validation section, diff against
the base branch — **not** against a tag:

```
git diff origin/main...HEAD -- ashfall.html
```

Beyond the diff, check all four:

1. **Room set identical.** `Object.keys(makeDefaultWorld())` before and
   after, sorted, must match exactly — 218 ids.
2. **Exit shape.** Re-run the cross/same-Location census: cross-Location
   exits carrying `distanceM` must go 26 → **0**; same-Location exits missing
   one must stay **0**; the totals must stay 706 and 68.
3. **Travel times unchanged.** For every exit in the world, `exitMinutes()`
   must return the same value before and after, at all three gaits. This is
   the real proof for Part 1 — the field being unread is the premise, and
   this is what tests it.
4. **Window climbs still cost 4 m.** Open `2a-transom` and `1b-alley` and
   confirm each climb exit still shows a finite duration, not `NaN`.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` bump and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, referencing this handoff
by path (`handoffs/world-data-cleanup.md`), recording which option was taken
for each of the two design decisions, and closing #3, #4 and #5. Tag the
merge commit `vX.Y.Z`.
