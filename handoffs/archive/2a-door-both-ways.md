# Ashfall Handoff — 2A's front door, gated both ways

Current shipped version: v0.6.0
Implied version-change type: PATCH
Issue: #145 — 2A's front door gates only one way — the four outbound exits carry no `doorId`

## What this is

Every exit *into* apartment 2A passes through door `"2a"`, but none of the four
exits *out* of it do. Lock the door and the player can still walk out of 2A from
any room; they just can't walk back in. 2B and 1A are gated in both directions
from every room. Tom's decision on #145 is **option 2**:

> **Gate it — add `doorId:"2a"` to the four exits above.** Makes all three
> apartments behave alike. Four WORLD DATA lines.

This is a content-only pass. No mechanic, no rendering change, and no schema or
state field.

## Relevant existing state

Verified against `ashfall.html` at v0.6.0. Line numbers are that file's.

**Door `"2a"`**, in `makeDefaultDoors()` (1260):

```js
"2a": { locked:false, sides:["hallway2","living"], building:"acorn" },
```

It is the only door that ships unlocked.

**The one exit that already carries `doorId:"2a"`**, in `hallway2` (1376):

```js
{ to:"living", label:"Enter apartment 2A", distanceM:6, doorId:"2a" },
```

**The four exits this pass gates.** Each is the last entry in its room's `exits`
inside `buildAcornApartments()`:

| room | line | exit as shipped |
|---|---|---|
| `living` | 1295 | `{ to:"hallway2", label:"Leave the apartment", distanceM:6 }` |
| `kitchen` | 1319 | `{ to:"hallway2", label:"Leave the apartment", distanceM:8 }` |
| `bathroom` | 1335 | `{ to:"hallway2", label:"Leave the apartment", distanceM:7 }` |
| `bedroom` | 1358 | `{ to:"hallway2", label:"Leave the apartment", distanceM:7 }` |

These are the only exits in the file from a 2A room to `hallway2`. `balcony` has
no exit to `hallway2`.

**How a gated exit already behaves.** Since v0.5.6 every door UI reads the exits
directly, so no code needs to change for the four rooms to pick up the door:

- `getExitsForRoom()` drops an exit whose `doorId` names a locked door.
- `gatedExitsForRoom(roomId)` returns one `{ doorId, to }` per door a room's
  exits pass through. `renderHereActionsPanel()` uses it to print
  `Unlock the <label> door` when a key is carried, or
  `The <label> door is locked.` when none is.
- `doorsTouchingRoom(roomId)` is the union of `doorsForRoom()` (from `sides`) and
  the gated exits. `getItemActions()` uses it for both the master key's and the
  single key's Lock/Unlock actions.
- `doorLabel("2a", room)` names the door **"2nd Floor"** from all four rooms:
  - from `living`, a `sides` member, via the far side `hallway2`;
  - from the other three, via their gated exit's `to`, which is also `hallway2`.
  In every case `hallway2`'s area `"2nd Floor"` differs from 2A's area `"2A"`, so
  the area is what names it.

**Why the player can't get stuck.**

- The `acorn_apt_2a_key` (`doorId:"2a"`) starts on the keychain
  (`makeDefaultState()`), and the `master_key` (building `"acorn"`) also opens it.
  Locking the door needs one of those keys in hand, and the same key unlocks it.
- 2A also has two ways out that don't pass through the door:
  - `balcony` → `alley` ("Climb down the fire escape", 1370);
  - the `2a-transom` window between `living` and `hallway2` (1270), which can be
    opened from either side and broken with a `blunt` tool.

## Rules / mechanics

- Add `doorId:"2a"` to each of the four exits in the table above. Change nothing
  else on those lines: `to`, `label` and `distanceM` stay exactly as they are.
- Change nothing else. `makeDefaultDoors()` is untouched, so `"2a"` still ships
  `locked:false`. The inbound exit at 1376 is untouched.

## Data / schema changes

None. `doorId` is an existing optional field in the EXIT SCHEMA.

## In scope

- The four `doorId:"2a"` additions.

## Explicitly out of scope

- Whether `"2a"` should ship locked. It stays `locked:false`.
- The transom window and the fire escape. They stay as they are and are the
  reason gating is safe.
- **#89** (`room.building` duplicating `BUILDINGS[].name`), and any other door,
  key or window.
- Any code change. If implementing this seems to need one, stop: the premise
  above (that v0.5.6's exit-driven door UI covers these rooms) has failed, and
  that needs raising, not working around.

## Sections touched

**WORLD DATA only**: four exits in `buildAcornApartments()`. Content-only pass.
No ACTIONS, SIMULATION or RENDERING code is touched.

## UI changes

No new string or control. With `"2a"` **locked**, the following holds:

| room | before | after |
|---|---|---|
| `living`, `kitchen`, `bathroom`, `bedroom` | `Leave the apartment` still offered; no door line | `Leave the apartment` gone. `Unlock the 2nd Floor door` if a key is carried, otherwise `The 2nd Floor door is locked.` |
| `kitchen`, `bathroom`, `bedroom` | the 2A key's and master key's detail views offer no Lock/Unlock | both offer `Unlock the 2nd Floor door` |
| `living` | the keys already offer Lock/Unlock (via `sides`) | unchanged |

With `"2a"` **unlocked** (the default at game start), the panels are unchanged,
except that the two keys' detail views now offer `Lock the 2nd Floor door` in
`kitchen`, `bathroom` and `bedroom` too. This matches 2B and 1A.

## Save compatibility

`applyLoadedData()` restores `world` wholesale from the save, and no backfill adds
or removes an exit field. **An existing save keeps 2A ungated.** Only a new game
or a Restart sees the change. The changelog must say this plainly, since the fix
is invisible to anyone mid-run.

## Validation to perform

- `git diff origin/main...HEAD -- ashfall.html` shows exactly four changed WORLD
  DATA lines plus `GAME_CONFIG.VERSION`.
- `ashfallDev.validateRoomSchema()`, `validateLocations()`,
  `validateItemRegistry()` and `validateReachability()` give output identical to
  v0.6.0.
- Walk each of the four rooms with `"2a"` locked, first with the 2A key on the
  keychain and then with it removed. Confirm the table above. Then unlock from
  inside and confirm `Leave the apartment` returns.
- Confirm the fire escape and the transom window still get the player out with
  the door locked and no key carried.

## Dependencies / issue linkage

Fulfils **#145**. Unblocks nothing. Nothing is expected to be deferred.

Sibling handoffs written in the same planning session:
- `handoffs/stowed-bag-contents.md` (#153 + #156)
- `handoffs/seed-report.md` (#150)

All three were checked against v0.6.0 and **touch no common line**. This one
touches only `buildAcornApartments()`, which neither of the others reads or edits.
They can ship in any order.

## Open questions for Tom

None. Option 2 was Tom's decision.

## After implementation

Open a pull request carrying the version bump and a new `CHANGELOG.md` entry per
`CHANGELOG_GUIDE.md` that names this handoff by path. `git mv` this file to
`handoffs/archive/` in the same pull request, and put `Closes #145` in the
description.
