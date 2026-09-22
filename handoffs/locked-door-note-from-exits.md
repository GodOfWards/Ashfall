# Ashfall Handoff — The locked-door note, driven by gated exits

Current shipped version: v0.5.4
Implied version-change type: PATCH
Issue: #142 — Six rooms lose an exit with no explanation

## What this is

In six rooms a locked door removes the only exit out of the apartment and the
Here panel prints nothing in its place. The master key's own panel is blank in
those same six rooms. Both come from one cause: the door UI is driven by
`doors[].sides`, which says which two rooms a door physically separates, while
movement is gated by `doorId` on an exit, which says which exits the door
actually blocks. The two disagree.

This pass moves the UI onto the exits. It is #142's **option 3**, the only one
of its three that touches no WORLD DATA:

> **Leave both and derive the note from the exits instead.** `renderHereActionsPanel()`
> already has `room.exits`; a locked-door note could be driven by
> `room.exits.filter(e => e.doorId && doors[e.doorId].locked)` rather than by
> `doorsForRoom()`. Touches no WORLD DATA, and makes half two's six rooms report
> correctly with no schema change.

## Relevant existing state

Verified against `ashfall.html` at v0.5.4. Line numbers are that file's.

**The five doors** (`makeDefaultDoors()`, 1239–1247) and their `sides`:

| doorId | `locked` at start | `sides` |
|---|---|---|
| `2a` | `false` | `hallway2`, `living` |
| `2b` | `true` | `hallway2`, `twobee` |
| `1a` | `true` | `hallway1`, `onea` |
| `1b` | `true` | `hallway1`, `onebee` |
| `1a-patio` | `true` | `onea_patio`, `onea` |

**Every exit carrying a `doorId`** — the complete list, extracted from the file:

| room | → | doorId | room in that door's `sides`? |
|---|---|---|---|
| `hallway2` | `living` | `2a` | yes |
| `hallway2` | `twobee` | `2b` | yes |
| `twobee` | `hallway2` | `2b` | yes |
| `twobee_kitchen` | `hallway2` | `2b` | **no** |
| `twobee_bathroom` | `hallway2` | `2b` | **no** |
| `twobee_bedroom` | `hallway2` | `2b` | **no** |
| `hallway1` | `onea` | `1a` | yes |
| `hallway1` | `onebee` | `1b` | yes |
| `onea` | `onea_patio` | `1a-patio` | yes |
| `onea` | `hallway1` | `1a` | yes |
| `onea_kitchen` | `hallway1` | `1a` | **no** |
| `onea_bathroom` | `hallway1` | `1a` | **no** |
| `onea_bedroom` | `hallway1` | `1a` | **no** |
| `onea_patio` | `onea` | `1a-patio` | yes |
| `onebee` | `hallway1` | `1b` | yes |

Two facts to rely on, both checked against the file rather than assumed:

- **No room carries two exits with the same `doorId`.** The dedup below is
  insurance against a future one, not a fix for a live case.
- **Apartment 2A's four outbound exits carry no `doorId` at all** (`living`
  1276, `kitchen` 1300, `bathroom` 1316, `bedroom` 1339). That asymmetry is
  **#145** and is deliberately *not* touched here. Its only consequence for this
  pass is the `living` row in the delta table below.

**The three call sites that name a door**, all reading `doorsForRoom()` (4194–4196):

- `renderHereActionsPanel()` 6057–6066 — the locked note and the unlock button.
- `getItemActions()` 4147–4150 — the master key's Lock/Unlock actions.
- `getItemActions()` 4151–4154 — the single key's, guarded instead by
  `doors[it.doorId].sides.includes(state.currentRoom)`.

**`doorLabel(doorId, fromRoomId)`** (4208–4218) resolves the far room strictly
from `sides`, and its first guard returns the bare `doorId` when the near room
is not one of them:

```js
if(!door || !near || !door.sides.includes(fromRoomId)) return doorId;
```

So it cannot be reused unchanged in the six rooms — it would render
`The 2b door is locked.`

## Rules / mechanics

### 1. A room's gated exits

A new query in **WORLD INTERACTION**, beside `doorsForRoom()`:

- Input: a room id.
- Output: one entry per exit of `world[roomId].exits` that carries a `doorId`
  resolving in `doors`, in the room's own exit order, carrying at least that
  exit's `doorId` and its `to`.
- Read **raw `room.exits`**, never `getExitsForRoom()` — the latter is precisely
  what drops locked-door exits, which is the defect.
- **Dedup by `doorId`, keeping the first.** No room needs this today; without
  it, a future room with two exits through one door prints the note twice.
- An exit whose `doorId` does not resolve in `doors` is skipped, matching how
  `doorLabel()` already fails safe.

### 2. The doors a room touches

A second query beside it: the **union** of

- `doorsForRoom(roomId)` — the doors this room is a `sides` member of, and
- the `doorId`s from the room's gated exits.

Order: the `doorsForRoom()` entries first, in their existing order, then any
exit-only doors in exit order. That ordering is not cosmetic — it is what keeps
every key-panel label sequence in the game byte-identical to v0.5.4.

The union is the point. A narrower rule would withdraw an action the player has
today: the master key offers **"Lock the 2nd Floor door"** from inside `living`,
which is a `sides`-only door (2A has no gated exit), and that must survive.

### 3. The label

Widen **`doorLabel(doorId, fromRoomId)`** in place — same name, same signature,
same fallback behaviour. Only the far-room resolution changes:

1. If `fromRoomId` is in `door.sides`, the far room is the other side. *(Today's
   behaviour, unchanged.)*
2. Otherwise, the far room is `world[exit.to]` for that room's gated exit
   carrying this `doorId`.
3. If neither resolves, return `doorId`, as now.

The naming rules below that are **unchanged** — far `area` when it differs from
the near room's, else far `room` lowercased, else far `area`, else the door id —
and the invariant comment above the function should be extended to say that the
far side now comes from the exit when the near room is not a `sides` member.

Widening in place is what makes this pass small: all three call sites keep
calling `doorLabel()` and all three become correct in the six rooms at once.

Labels this produces in the six rooms:

| room | near `area` | far | label |
|---|---|---|---|
| `twobee_kitchen` / `_bathroom` / `_bedroom` | `2B` | `hallway2` (`2nd Floor`) | `2nd Floor` |
| `onea_kitchen` / `_bathroom` / `_bedroom` | `1A` | `hallway1` (`1st Floor`) | `1st Floor` |

Both match what `twobee` and `onea` already print one room away, which is the
test: the same door reads the same from every room it shuts in.

### 4. The Here panel

`renderHereActionsPanel()`'s door block is driven by the room's **gated exits
whose door is locked**, in exit order, instead of by `doorsForRoom()`. Nothing
else about the block changes — same `actionButton` for a player holding a key
(`findKeyForDoor()` is untouched), same `hereNote()` otherwise, same two
strings:

- `Unlock the ${label} door`
- `The ${label} door is locked.`

### 5. Both key branches

`getItemActions()`'s master-key branch reads the **union** from rule 2 in place
of `doorsForRoom()`. Its `building` filter, its Lock/Unlock ternary and its
label are otherwise unchanged.

The single-key branch's guard becomes membership of that same union in place of
`doors[it.doorId].sides.includes(state.currentRoom)`. This changes nothing
today — the only single key is `acorn_apt_2a_key` (`doorId:"2a"`), and the one
room with a `2a`-gated exit is `hallway2`, already a `sides` member — and is
specified so a future single key behaves like the master one rather than
inheriting the bug this pass removes.

### 6. The complete behavioural delta

Every room that touches a door, before and after. **Seven rows change**; the
other six are identical.

| room | v0.5.4 Here panel | after | change |
|---|---|---|---|
| `hallway2` | `2a`, `2b` | `2a`, `2b` | — |
| `living` | `2a` | *(nothing)* | **note removed** |
| `twobee` | `2b` | `2b` | — |
| `twobee_kitchen` | *(nothing)* | `2b` | **note/button added** |
| `twobee_bathroom` | *(nothing)* | `2b` | **note/button added** |
| `twobee_bedroom` | *(nothing)* | `2b` | **note/button added** |
| `hallway1` | `1a`, `1b` | `1a`, `1b` | — |
| `onea` | `1a`, `1a-patio` | `1a-patio`, `1a` | **order swaps** |
| `onea_kitchen` | *(nothing)* | `1a` | **note/button added** |
| `onea_bathroom` | *(nothing)* | `1a` | **note/button added** |
| `onea_bedroom` | *(nothing)* | `1a` | **note/button added** |
| `onea_patio` | `1a-patio` | `1a-patio` | — |
| `onebee` | `1b` | `1b` | — |

Two of those rows are worth stating plainly, because a reviewer will otherwise
read them as regressions:

- **`living` loses a note, and the note it loses is false.** Standing in 2A with
  `"2a"` locked, v0.5.4 prints `The 2nd Floor door is locked.` while the exit
  carries no `doorId` and is perfectly walkable. Removing it is the fix, not a
  side effect. The master key still offers Lock/Unlock there, via rule 2.
- **`onea`'s two notes swap order**, because the block now follows exit order
  (`onea_patio` is authored before `hallway1`) rather than `Object.keys(doors)`
  order. Expected. Exit order is also the order the exits themselves appear in
  the panel immediately above.

## Design decisions to make during implementation

All three are narrow; record whichever is picked in the changelog's
Notes/assumptions.

- **Names and return shape of the two new queries.** Recommended default:
  `gatedExitsForRoom(roomId)` returning `[{ doorId, to }]`, and
  `doorsAtRoom(roomId)` returning a `doorId[]` — matching `doorsForRoom(roomId)`'s
  existing argument shape and return type so the two read as siblings. If
  `doorsAtRoom` reads too close to `doorsForRoom` to tell apart at a call site,
  rename the new one rather than the old one; `doorsForRoom()` is the one
  described in existing comments.
- **Where the dedup lives.** Recommended default: inside
  `gatedExitsForRoom()`, so neither caller repeats it and the guarantee belongs
  to the query rather than to the two places that happen to use it.
- **Whether `doorLabel()` is widened in place or gains a sibling.**
  Recommended default: widened in place, per rule 3 — one function, three call
  sites, no caller edited for the label at all. A sibling would mean deciding at
  each call site which to use, which is the kind of choice that drifts.

## Data / schema changes

**None.** No state field, no item schema field, no room/container/exit schema
field, no `doors` schema change. `doors[].sides` keeps its current meaning —
"the two rooms this door physically separates" — and this pass is what stops the
UI treating it as something else.

## In scope

- The two new queries in WORLD INTERACTION.
- `doorLabel()`'s far-room resolution widened, and its comment extended.
- `renderHereActionsPanel()`'s door block driven by locked gated exits.
- `getItemActions()`'s master-key branch and single-key guard on the union.
- `GAME_CONFIG.VERSION` bumped (PATCH), changelog entry, handoff archived.

## Explicitly out of scope

- **#145** — 2A's four outbound exits carrying no `doorId`. Split out of #142
  during this planning session precisely so this pass stays rendering-side. Add
  no `doorId` anywhere, and change no exit.
- **#141** — the `shelter` corrections. Sibling handoff from the same planning
  session (`handoffs/shelter-partial-and-none.md`), WORLD DATA only. The two
  touch no common line and can ship in either order.
- `findKeyForDoor()`, `doorsForRoom()`, `doToggleLock()`, `getExitsForRoom()`
  and `makeDefaultDoors()` are **unchanged**. Which doors are lockable, by whom,
  and which exits a locked door removes is exactly as it was — only what the two
  panels say about it changes.
- **#89** (`room.building` duplicating `BUILDINGS[].name`) — the label reads
  `area` and `room`, never `building`.
- **#29** (log size and entry cap), **#78** (the accessibility pass) —
  `hereNote()` and `actionButton()` are used exactly as they are today.
- No new door, no new key, no new window, no world data of any kind.

## Sections touched

- **WORLD INTERACTION** — the two new queries; `doorLabel()`.
- **INVENTORY / ITEM SYSTEM** — `getItemActions()`, both key branches.
- **RENDERING** — `renderHereActionsPanel()`, the door block only.
- **CONFIG / CONSTANTS** — `GAME_CONFIG.VERSION`.

Untouched: WORLD DATA, PLAYER STATE, CORE UTILITIES, SURVIVAL / TIME SIMULATION,
STAMINA / FATIGUE, CRAFTING, FIRE / COOKING, PERSISTENCE, EVENTS,
RENDERING / MAP, and the document `<style>` and `<body>` blocks.

## UI changes

No new string and no new control — the same two sentences appear in six rooms
where nothing appeared, and stop appearing in one room where they were wrong.
The delta table in rule 6 is the complete list. The master key's panel gains
its Lock/Unlock action in the same six rooms.

## Dependencies / issue linkage

- Fulfils **#142** in full. `Closes #142` in the pull request.
- Leaves **#145** open and untouched by design.
- Nothing is expected to be deferred. If the pass surfaces something new, file
  it as an issue and reference it in the pull request; if nothing comes up, say
  so in the changelog's Documentation section.

## Verifying it

The claim "no world data changed" is checkable and should be checked, per the
Project Guide:

- `git diff origin/main...HEAD -- ashfall.html`, read hunk by hunk — it should
  touch only the four functions named above plus the version constant.
- `node --check` on the extracted script body.
- `ashfallDev.validateRoomSchema()`, `validateLocations()`,
  `validateItemRegistry()` and `validateReachability()` against a v0.5.4 build
  and this one, diffed: **identical output** is required, since no world data
  moved.
- Walk all thirteen rooms in the delta table, in both lock states, through the
  real render path, and confirm each row.
- The day-one route from #142, which needs no re-locking: master key from
  `onebee/desk` (in through the alley window), alley → `onea_patio`, unlock
  `1a-patio`, into `onea`, then `onea_kitchen`. Before: no exit and no note.
  After: `Unlock the 1st Floor door`.
- Confirm the master key in `living` still offers `Lock the 2nd Floor door` —
  this is the action rule 2's union exists to preserve.
- A save written by the v0.5.4 build loads under `ashfall_save_v0.5` with no
  version warning: no state field is added, read or changed, `versionCompat()`
  does not move.

## After implementation

Open a pull request carrying the version bump and a new `CHANGELOG.md` entry per
`docs/CHANGELOG_GUIDE.md`, naming this handoff by the path it was read at,
recording which of the three design decisions above were taken and why, and
closing #142 with `Closes #142`. Move this file to `handoffs/archive/` with
`git mv` in the same pull request.
