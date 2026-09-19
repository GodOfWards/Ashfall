# Ashfall Handoff — A room's address, its building, and whether it is under cover

Current shipped version: v0.4.11
Implied version-change type: PATCH
Issues: #42 — The `building` room field carries two different kinds of fact
        #82 — Rooms don't say whether they're outdoors, and #8 is about to make
              adding that much more expensive

## What this is

Two ROOM SCHEMA changes, settled together because both require editing all 218
room definitions and doing them separately means the second pass re-touches every
line the first one did.

**#42:** `building` holds a building's name on 33 rooms, a street or intersection
on 184, and `""` on one. It is split into `address` (where the room is) and
`building` (what building it is inside), and `roomLabel()` composes from both.

**#82:** nothing in the file knows whether the player is under cover. A `shelter`
field is laid down on every room now, with no consumer, because #8 is about to
add roughly three hundred rooms and the retrofit cost only goes one way. The
precedent is `LOCATIONS`' `z`, which the file already carries unused and says so:

> Z is laid down for every Location but not consumed by anything yet (the map is
> top-down) — future systems can rely on it without a retrofit.

Everything here is WORLD DATA plus one utility function and one backfill.

## Relevant existing state

Verified against `main` @ v0.4.11 by classifying all 218 rooms in the built
world. Line numbers are v0.4.11's.

- **218 rooms.** 176 are street or mid-block nodes, identified by
  `locationId === roomId`; 42 are not.
- **`roomLabel()`** (`:3544`) is four lines and is the **only reader of
  `room.building` anywhere in the file.** It is called from exactly one place,
  `renderLocationPanel()` (`:5296`), which writes `#locLabel`.
- **Nothing writes `room.building`, `room.area` or `room.room` at runtime.**
  All three are static content, set at world-build time and never mutated. This
  is what makes the backfill below safe.
- **`doors[id].building` and `master_key.building` are a different field.** They
  hold a building **id** (`"acorn"`), are read by `getItemActions()` (`:3856`)
  and `findKeyForDoor()` (`:3910`), and are consistent with themselves. **Do not
  touch them.** A blind rename of `building` across the file will break the
  master key.
- **Every room's label shape today**, measured across all 218:

  | rooms | `building` holds | area | room | renders as |
  |---|---|---|---|---|
  | 117 | a street | no | yes | `"Main St, Corner Store"` · `"Poplar St, between 1st & 2nd"` |
  | 64 | an intersection | no | no | `"Dock St & 6th St"` |
  | 21 | a building name | yes | yes | `"Acorn Apartments, 2A - Living Room"` |
  | 7 | a building name | no | yes | `"Oak Apartments, Stairwell"` |
  | 5 | a building name | yes | no | `"Acorn Apartments, 1B"` |
  | 3 | a street | yes | no | `"Main St, Apt above Corner Store"` |
  | 1 | `""` | no | yes | `", Riverbank"` |

  Rows 3–5 and rows 1/6 have **identical field shapes and opposite meanings**.
  `"Oak Apartments, Stairwell"` and `"Main St, Corner Store"` are both
  *slot-1, slot-3*: in one, slot 1 is a building and slot 3 a room; in the other,
  slot 1 is a street and slot 3 a building. That is why #42's body is wrong when
  it says option 2 "changes no output if the composition is written to match" —
  no single rule reproduces both without re-deriving the unwritten "does this
  building have more than one room" convention. **This pass changes 34 labels,
  deliberately.**
- **`riverbank` renders as `", Riverbank"`** — a leading comma-space visible in
  `#locBar` — because it takes `roomLabel()`'s third branch with `building: ""`.
- **40 of the 42 non-street rooms carry `cannotHaveFire`.** The two that do not
  are `riverbank` and `alley`, both genuinely outdoors. `cannotHaveFire` has
  exactly one consumer, the campfire gate in `renderHereActionsPanel()` (`:5412`).
- **`applyLoadedData()`** (`:4533`) takes the incoming world wholesale —
  `const nextWorld = data.world;` — with no merge against the defaults. A save
  made before this ships therefore carries rooms with the old `building` and no
  `address` at all.
- **`backfillLocationIds()`** (`:4453`) is the exact precedent for repairing
  that: it rebuilds a default world and copies a missing field by direct room-id
  lookup. `backfillItemIds()` and `backfillContainerFields()` are its siblings;
  all three run from `applyLoadedData()` after validation.
- **`validateLocations()`** (`:4592`) is the model for a dev-only console helper
  that walks every room and returns an array of problem strings.

## Rules / mechanics

### 1. The two new fields

Every room gets both. Neither is optional and neither has a default — a room
missing one is a bug, not a shorthand.

**`address`** — the street or intersection the room is at, as a display string.
Always present, never empty.

**`building`** — the name of the building this room is inside. `null` when the
room is not inside a named building. Its meaning narrows: it now holds a
building's name and nothing else, ever.

**`shelter`** — `"none"` or `"full"`. `"partial"` is a **reserved third value**,
documented in the schema comment and used by no room in this pass; classifying
which rooms are genuinely partial (a covered porch, an open garage, a doorway)
is content for a later pass, once there is a consumer to make the distinction
mean something.

`area` and `room` keep their current meanings and values, except where the table
in §3 says otherwise.

**Field order in a room literal:** `locationId, address, building, area, room,
shelter, desc, …`. `shelter` sits with the identity block rather than with the
optional environmental flags below `desc`, because like `locationId` it is
mandatory on every room and those flags are not.

### 2. The address rule

> **A room's `address` is the street it is on. A building fronts a street, never
> a corner.**
>
> A street or mid-block node's address is its own location — including an
> intersection node, which genuinely is at a corner and keeps its
> `"<Street> St & <N>th St"` string. A room *inside* a building takes the named
> street that building fronts, even when the building sits on an intersection
> node: the Police Station is entered from `maple3rd` but its address is
> `"Maple St"`, not `"Maple St & 3rd St"`.

This rule is already the shipped convention for four of the six single-room
buildings — `cornerstore` and `storage` are authored `"Main St"` and `"Water St"`
today, against intersection nodes. The pass extends it to the rest rather than
inventing it.

Put the rule in the ROOM SCHEMA comment, beside the `address` field. It is the
rule #8's ~40 buildings will follow.

### 3. What every room gets

**The 176 street and mid-block nodes:** `address` takes the current `building`
value **verbatim** — `"Dock St & 6th St"`, `"Poplar St"`, and so on — and
`building` becomes `null`. `area` and `room` are untouched. `shelter: "none"`.

This half is a mechanical rename and changes no label.

**The 42 non-street rooms**, in full:

| rooms | count | `address` | `building` | other changes | `shelter` |
|---|---|---|---|---|---|
| Acorn Apartments — every room on `acorn_f0`/`acorn_f1` **except `alley`** | 20 | `"Poplar St"` | `"Acorn Apartments"` | — | `"full"` |
| `alley` | 1 | `"Poplar St"` | `null` | keeps `room: "Alley"` | **`"none"`** |
| Oak Apartments — `oak_f0`/`oak_f1` | 7 | `"Poplar St"` | `"Oak Apartments"` | — | `"full"` |
| Auto Workshop — `auto_shop`, `auto_shop_back` | 2 | `"Main St"` | `"Auto Workshop"` | — | `"full"` |
| Police Station — `police_lobby`, `police_evidence` | 2 | `"Maple St"` | `"Police Station"` | — | `"full"` |
| Riverside Freight — `industrial_floor`, `industrial_office` | 2 | `"Maple St"` | `"Riverside Freight"` | — | `"full"` |
| `cornerstore` | 1 | `"Main St"` | `"Corner Store"` | `room` → `null` | `"full"` |
| `pharmacy` | 1 | `"Main St"` | `"Pharmacy"` | `room` → `null` | `"full"` |
| `hardware` | 1 | `"Main St"` | `"Hardware Store"` | `room` → `null` | `"full"` |
| `storage` | 1 | `"Water St"` | `"Storage Facility"` | `room` → `null` | `"full"` |
| `riverbank` | 1 | `"Water St"` | `"Riverbank"` | `room` → `null` | **`"none"`** |
| `cornerstore_apt` | 1 | `"Main St"` | `null` | keeps its `area` | `"full"` |
| `pharmacy_apt` | 1 | `"Main St"` | `null` | keeps its `area` | `"full"` |
| `hardware_apt` | 1 | `"Main St"` | `null` | keeps its `area` | `"full"` |

42 rooms. The five single-room buildings plus `riverbank` move their name out of
`room` and into `building`, which is the duplication #42's comment identified.

**The three flats above shops get `building: null`** rather than the shop's name.
A flat over the Corner Store is not inside the Corner Store — the shop is
downstairs and the residence is a separate place reached by its own stair. This
also preserves their labels exactly. It is a judgment call with no prior
convention; flag it as retunable in the changelog.

### 4. `shelter` is not derived, and not `cannotHaveFire`

`shelter: "full"` and `cannotHaveFire` are coextensive across all 218 rooms
today. **That is a coincidence of the current content, not a rule, and the
implementation must not exploit it.**

- They are different facts. `cannotHaveFire` is a fire rule with one consumer;
  `shelter` is about being under cover. Reading one as the other is exactly the
  two-facts-in-one-field problem #42 exists to fix, and is not worth creating a
  second time.
- The correlation is already known to break. `handoffs/building-placement-and-elm-st.md`
  specs an unfinished house that is *outdoors and fire-capable* — "No
  `cannotHaveFire`. It is open to the sky, so a campfire can be built here." A
  covered porch is the inverse.
- Deriving from `locationId === roomId` is likewise rejected: it gets 176 of the
  178 outdoor rooms free and is wrong for `alley` and `riverbank`, which is
  precisely the interesting content.

**Both fields stay, authored independently, on every room.**

### 5. `roomLabel()`

Replace the four-branch function with an outward-in composition:

```js
  // A room's label reads outward-in: the address, then the building it is in,
  // then the area within that building, then the room. `area` and `room` join
  // with " - " because they are two depths inside one building; everything else
  // joins with ", ". Every room has an address; the other three are optional.
  function roomLabel(room){
    const head = [room.address, room.building, room.area].filter(Boolean).join(", ");
    if(!room.room) return head;
    return head + (room.area ? " - " : ", ") + room.room;
  }
```

Worked against every shape in the table above:

| room | before | after |
|---|---|---|
| `dock6th` | `"Dock St & 6th St"` | unchanged |
| `mid_poplar_1_2` | `"Poplar St, between 1st & 2nd"` | unchanged |
| `cornerstore` | `"Main St, Corner Store"` | unchanged |
| `cornerstore_apt` | `"Main St, Apt above Corner Store"` | unchanged |
| `alley` | `"Poplar St, Alley"` | unchanged |
| `living` | `"Acorn Apartments, 2A - Living Room"` | `"Poplar St, Acorn Apartments, 2A - Living Room"` |
| `onebee` | `"Acorn Apartments, 1B"` | `"Poplar St, Acorn Apartments, 1B"` |
| `oak_stairs` | `"Oak Apartments, Stairwell"` | `"Poplar St, Oak Apartments, Stairwell"` |
| `auto_shop` | `"Auto Workshop, Main Bay"` | `"Main St, Auto Workshop, Main Bay"` |
| `police_lobby` | `"Police Station, Lobby"` | `"Maple St, Police Station, Lobby"` |
| `riverbank` | `", Riverbank"` | `"Water St, Riverbank"` |

**Exactly 34 of 218 labels change:** the 33 rooms whose `building` currently
holds a building name, each gaining its street as a prefix, plus `riverbank`,
whose leading comma is the defect being fixed. The other 184 are byte-identical.

The planning session executed this specification — §3's table plus the
composition above — against the real built world rather than reasoning about it:
34 changed labels, 178 `"none"` / 40 `"full"`, zero rooms without an address,
zero malformed labels. The numbers in this handoff are measured, not estimated,
and the acceptance tests below should reproduce them exactly. A different count
means the room table was applied differently, not that the count was wrong.

### 6. `backfillRoomAddresses()`

`roomLabel()` now reads a field that no existing save's rooms have. Without a
backfill, every one of the 218 labels renders `"undefined, …"` on any save made
before this ships. Add a fourth backfill in PERSISTENCE, beside the three that
are there, and call it from `applyLoadedData()` after the existing three:

```js
  function backfillRoomAddresses(){
    const defaults = makeDefaultWorld();
    Object.keys(world).forEach(roomId=>{
      const room = world[roomId];
      if(room && room.address === undefined && defaults[roomId]){
        room.address  = defaults[roomId].address;
        room.building = defaults[roomId].building;
        room.area     = defaults[roomId].area;
        room.room     = defaults[roomId].room;
      }
    });
  }
```

Two things about its shape, both of which need saying in its comment:

- **It keys off `address === undefined`, not falsiness.** An address is never
  empty, but `=== undefined` is what distinguishes "this save predates the
  field" from any other state, and it is the test the three siblings use in
  spirit.
- **It copies all four label fields, not just `address`.** The siblings each
  restore one missing field, because one field was added. Here the *meaning* of
  `building` changed and `room` moved for six rooms, so restoring `address`
  alone would leave `cornerstore` reading `"Main St, Corner Store, Corner Store"`.
  All four are static content that nothing mutates at runtime (verified: the only
  reader of any of them is `roomLabel()`), so taking them wholesale from the
  defaults is safe and is the only version that produces a correct label.

**`shelter` gets no backfill.** Nothing reads it, so an old save's rooms lacking
it changes nothing. The pass that adds the first consumer — #58 or #6 — inherits
that backfill. Say so in the schema comment so that pass is not surprised.

### 7. `validateRoomSchema()`

Add a dev-only console helper beside `validateLocations()`, same shape: walks
every room, returns an array of problem strings, `console.warn`s them when
non-empty, wired to nothing. It reports a room with no `address`, a room whose
`shelter` is missing, and a room whose `shelter` is not one of `"none"`,
`"partial"`, `"full"`.

A dev helper is the right tool here, unlike in
`handoffs/direction-zero-vector-guard.md` where the equivalent check earns a
build-time warning. The difference is how the two failures present: a missing
`address` renders `"undefined"` in the location bar of the room you are standing
in, on the first frame — it announces itself. A wrong compass word reads as
plausible English and never does. A helper is enough for a loud failure; it is
not enough for a quiet one.

## Design decisions to make during implementation

- **Whether `building: null` is written explicitly on the 176 street nodes or
  omitted.** Recommended: **omit it.** `address` is what those rooms have and a
  `null` on 176 definitions is noise; `filter(Boolean)` treats absent and `null`
  identically. The schema comment must then say `building` is absent when the
  room is not inside a named building. Record which was chosen.
- **Whether `shelter` is a bare string or a small named constant set.** A
  `SHELTER` frozen object would let `validateRoomSchema()` check against one
  list. Recommended: **bare strings**, with the three legal values named in the
  ROOM SCHEMA comment and in the validator — the file's other enumerated room
  fields (`sleepSpot`, `searchLabel`) are bare strings too, and a constant set
  read by one validator is not yet earning its name. Record it either way.
- **Where `backfillRoomAddresses()` sits in `applyLoadedData()`'s call order.**
  It is independent of the other three; after them is recommended, for no reason
  beyond reading order.

## Data / schema changes

- **Room schema (WORLD DATA):** `building` narrows to "the building's name, or
  absent"; `address` is new and mandatory; `shelter` is new and mandatory. The
  ROOM SCHEMA comment must document all three, the address rule from §2, the
  reserved `"partial"` value, and the fact that `shelter` has no consumer yet —
  with the `LOCATIONS` `z` precedent named, so a reader does not mistake an
  unused field for a dead one.
- **No PLAYER STATE field.** No ITEM DATA SCHEMA field, tag or category.
- **No container or exit schema change.**
- **`SAVE_KEY` does not rotate.** This stays a PATCH. Old browser saves keep
  loading and are repaired by `backfillRoomAddresses()`.

## In scope

- The ROOM SCHEMA comment block.
- All 218 room definitions, across every `build*()` function: the ten building
  builders and the sixteen street builders.
- `roomLabel()`.
- `backfillRoomAddresses()`, new, and its call from `applyLoadedData()`.
- `validateRoomSchema()`, new.
- **The supersession banner on `handoffs/building-placement-and-elm-st.md`** —
  see §"Dependencies" below. This is a deliverable of this pass, not a follow-up.

## Explicitly out of scope

- **Removing the `BUILDINGS.name` ↔ `room.building` duplication.** This pass
  removes the `room.room` half of it — all eleven `BUILDINGS` names are now
  carried in some room's `building` field, where before six lived in `room.room`
  — but it does **not** remove the remaining duplication, and it should not be
  described as doing so. Deriving `BUILDINGS[id].name` would need a stable
  `buildingId` on rooms to join on, since matching by name string is exactly what
  the project avoids. That is a further schema change and a separate pass; file
  it at wrap-time if it still looks worth doing.
- **`doors[id].building` and `master_key.building`.** A different field holding a
  building id. Untouched.
- **`cannotHaveFire`.** Not replaced, not derived, not removed. See §4.
- **Giving `shelter` a consumer.** #58 (weather) and #6 (rooftops) are the
  consumers; this pass deliberately ships the field unread.
- **#68** — specced separately in `handoffs/direction-zero-vector-guard.md`. It
  touches no room definition; the two passes can land in either order.
- **#87** (the `renderMapClose()` name split) and **#37** (Wide-view labels
  outside the box). Both RENDERING, both untouched.
- **#8 itself.** This is groundwork for it, not any part of it. Add no rooms.
- **The 64 intersection nodes' `"<Street> St & <N>th St"` strings.** They read
  correctly and stay as authored.

## Sections touched

- **WORLD DATA** — the ROOM SCHEMA comment and every room definition.
- **CORE UTILITIES** — `roomLabel()`.
- **PERSISTENCE** — `applyLoadedData()`, new `backfillRoomAddresses()`, new
  `validateRoomSchema()` in the dev-helper block.

Nothing in ACTIONS, SIMULATION or the STAMINA/FATIGUE sub-block. RENDERING is
reached only through `renderLocationPanel()`'s existing unchanged call to
`roomLabel()` — no rendering code is edited.

The ARCHITECTURE comment needs no change: no section gains or loses a
responsibility.

## UI changes

**34 location-bar labels change**, all of them by gaining the street they are on
as a prefix, plus `riverbank` losing its leading comma. No new UI element, no
new button, no new panel, no wording rewritten. `#locLabel` is the only thing on
screen that differs.

This is a deliberate, Tom-approved content change, not a side effect — the
alternative composition (drop the address when a building name is present) was
considered and rejected because it would have lost the address for the six
single-room buildings that carry one today.

## Validation

- **A full before/after label table for all 218 rooms.** Build the world on
  `origin/main` and on the branch, call `roomLabel()` on every room, and diff.
  **Exactly 34 rows differ**, and each differs exactly as §5's table specifies.
  This is the proof that 184 labels are untouched; do not assert it.
- **No label starts with `", "`, ends with `", "`, or is empty.** `riverbank` is
  the one that used to.
- **Every room has an `address` and a legal `shelter`.** `validateRoomSchema()`
  returns an empty array. Counts: 178 `"none"`, 40 `"full"`, 0 `"partial"`.
- **`shelter` is not a copy of `cannotHaveFire`.** Assert that `alley` and
  `riverbank` are `"none"` while having no `cannotHaveFire`, and that the 40
  `"full"` rooms are exactly the 40 that carry it — stated as a measured
  coincidence in the changelog, not as an invariant.
- **Old-save round trip.** Take a `serializeGame()` output produced on
  `origin/main` at v0.4.11, load it into the branch build, and confirm all 218
  labels render exactly as a fresh world does. This is the test that
  `backfillRoomAddresses()` works; without it the regression is invisible until
  a player with a save opens the game.
- **A well-formed new save still round-trips byte-identically** through
  `serializeGame()`.
- **`validateLocations()` still returns clean**, and `validateLoadedWorld()`'s
  existing shape checks still pass — neither is edited.
- **The master key still works.** Open a door with it from `hallway1`; this is
  the regression guard on `doors[].building` / `master_key.building` not having
  been caught by the sweep.
- **No page errors** on load or during any test run.
- **Diff discipline:** `git diff origin/main...HEAD -- ashfall.html`. Expect the
  version bump, the ROOM SCHEMA comment, 218 room definitions, `roomLabel()`,
  and two additions in PERSISTENCE. Nothing in ACTIONS, SIMULATION or RENDERING.

## Dependencies / issue linkage

- **Fulfils #42 and #82.** The PR says `Closes #42` and `Closes #82`.
- **Unblocks #8**, which is the reason both are worth doing now.
- **#88 is this pass's obligation.** `handoffs/building-placement-and-elm-st.md`
  is committed, unimplemented, and writes a house's street address into
  `building` (`"214 Elm St, Bedroom"`) — a third meaning the field no longer
  has. The moment this merges, that handoff fails the Handoff Guide's test:
  a coding session handed it and `ashfall.html` would author 28 rooms into the
  wrong field and omit `shelter` entirely.

  **Add the supersession banner in this PR**, per `docs/Ashfall_Handoff_Guide.md`
  Part 2: a blockquote on the very first line, above the title, body untouched,
  saying what changed (a house is now `address: "214 Elm St"`, `building: null`,
  and every room needs `shelter`), that its label output is unaffected by the
  change, and that #88 carries the live truth. `handoffs/map-view-ui-fixes.md` is
  the worked example. The guide is explicit that the gap between merging and
  bannering is when someone implements the stale file, so it rides in this PR
  rather than waiting.

  `Closes #88` belongs in the same PR once the banner is written.
- **#58 and #6** are `shelter`'s eventual consumers and inherit its backfill.
- **Expected to be deferred:** the `buildingId` question from "Out of scope".
  File it at wrap-time if it still looks worth doing, and reference it in the PR;
  if the pass surfaces nothing, say so in the changelog's Documentation section.

## After implementation

Open a pull request carrying the `GAME_CONFIG.VERSION` bump and a new
`CHANGELOG.md` entry per `docs/CHANGELOG_GUIDE.md`, naming this handoff by path
in the entry's `Implements:` field, recording the three design decisions above
and the flats-above-shops judgment call, and closing `#42`, `#82` and `#88`.
The entry must carry the full before/after label table — 34 changed labels is a
player-visible change and the changelog is where it is recorded. Tag the merge
commit per `CLAUDE.md`'s wrap-time checklist, naming the commit explicitly.
